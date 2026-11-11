"""Auth use cases: signup, login/logout, sessions, PATs, password reset, roles, audit.

Framework-free: the API layer maps :class:`AuthError` subclasses to HTTP statuses. Every
security-relevant event is written to the audit log. Policy values live in
:class:`AuthConfig` (see ``docs/architecture/auth.md`` §2, PRD C.3).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from robotics_curriculum.auth.crypto import (
    PasswordPolicyError,
    Passwords,
    check_policy,
    new_token,
    same,
    token_hash,
)
from robotics_curriculum.auth.mailer import Mail, Mailer
from robotics_curriculum.auth.models import (
    ApiToken,
    AuditEntry,
    AuthSession,
    Identity,
    Role,
    Scope,
    TokenKind,
    User,
    UserStatus,
)
from robotics_curriculum.auth.oidc import Claims
from robotics_curriculum.auth.store import AuthStore

PAT_PREFIX = "rcp_"
RESET_KEY_PREFIX = "reset:"


# -- errors ------------------------------------------------------------------------------


class AuthError(Exception):
    status = 400

    def __init__(self, detail: str, *, headers: dict[str, str] | None = None) -> None:
        super().__init__(detail)
        self.detail = detail
        self.headers = headers


class InvalidCredentials(AuthError):
    status = 401


class Forbidden(AuthError):
    status = 403


class NotFound(AuthError):
    status = 404


class Conflict(AuthError):
    status = 409


class Invalid(AuthError):
    status = 422


class Throttled(AuthError):
    status = 429


class Unavailable(AuthError):
    status = 503


# -- config / context ---------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AuthConfig:
    session_idle: timedelta = timedelta(days=14)
    session_absolute: timedelta = timedelta(days=30)
    login_window: timedelta = timedelta(minutes=15)
    max_failures_account: int = 5
    max_failures_ip: int = 20
    reset_ttl: timedelta = timedelta(minutes=30)
    verify_ttl: timedelta = timedelta(hours=24)
    audit_retention: timedelta = timedelta(days=90)
    allow_signup: bool = True
    bootstrap_admin_email: str | None = None
    reset_window: timedelta = timedelta(minutes=15)
    max_resets_per_window: int = 3
    max_resets_per_ip: int = 10
    public_url: str = "http://localhost:3000"
    api_base_url: str | None = None
    pepper: str = ""

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> AuthConfig:
        """``RC_AUTH_*`` variables; unset ones keep the defaults."""

        def days(name: str, default: timedelta) -> timedelta:
            value = env.get(name)
            return timedelta(days=int(value)) if value else default

        base = cls()
        return cls(
            session_idle=days("RC_AUTH_SESSION_DAYS", base.session_idle),
            audit_retention=days("RC_AUTH_AUDIT_RETENTION_DAYS", base.audit_retention),
            allow_signup=env.get("RC_AUTH_ALLOW_SIGNUP", "1") != "0",
            bootstrap_admin_email=(env.get("RC_AUTH_ADMIN_EMAIL") or "").lower() or None,
            public_url=env.get("RC_PUBLIC_URL") or base.public_url,
            api_base_url=env.get("RC_API_BASE_URL") or None,
            pepper=env.get("RC_AUTH_PEPPER", ""),
        )


@dataclass(frozen=True, slots=True)
class Context:
    """Who is calling from where, for the audit log."""

    ip: str | None = None
    user_agent: str | None = None
    request_id: str | None = None


@dataclass(frozen=True, slots=True)
class Principal:
    """An authenticated caller: a browser session or a personal access token."""

    user: User
    session: AuthSession | None = None
    token: ApiToken | None = None

    @property
    def via_token(self) -> bool:
        return self.token is not None

    def has_scope(self, scope: Scope) -> bool:
        """Sessions carry every scope their role allows; PATs only the granted ones."""
        if self.token is None:
            return scope is not Scope.ADMIN or self.user.role is Role.ADMIN
        return scope in self.token.scopes


@dataclass(frozen=True, slots=True)
class LoginResult:
    user: User
    session: AuthSession
    session_token: str = field(repr=False)
    csrf_token: str = field(repr=False)


def _utcnow() -> datetime:
    return datetime.now(UTC)


# -- service ------------------------------------------------------------------------------


class AuthService:
    def __init__(
        self,
        store: AuthStore,
        *,
        config: AuthConfig | None = None,
        mailer: Mailer | None = None,
        passwords: Passwords | None = None,
        clock: Callable[[], datetime] = _utcnow,
        erase_learning_data: Callable[[int], None] | None = None,
    ) -> None:
        self.store = store
        self.config = config or AuthConfig()
        self.mailer = mailer
        self.passwords = passwords or Passwords(self.config.pepper)
        self.clock = clock
        self.erase_learning_data = erase_learning_data

    def _audit(self, ctx: Context, action: str, actor: int | None, **kwargs: Any) -> None:
        self.store.audit(
            action,
            self.clock(),
            actor_user_id=actor,
            actor_ip=ctx.ip,
            request_id=ctx.request_id,
            **kwargs,
        )

    def record(self, ctx: Context, action: str, actor: int | None, **kwargs: Any) -> None:
        """Append an audit entry for events decided outside the service (denials, admin
        reads)."""
        self._audit(ctx, action, actor, **kwargs)

    # -- accounts ---------------------------------------------------------------------

    def signup(
        self, email: str, password: str, ctx: Context, *, display_name: str | None = None
    ) -> User:
        if not self.config.allow_signup:
            raise Forbidden("sign-up is disabled on this server")
        email = email.strip().lower()
        try:
            check_policy(password, email=email, display_name=display_name)
        except PasswordPolicyError as exc:
            raise Invalid(str(exc)) from None
        if self.store.get_user_by_email(email) is not None:
            raise Conflict("an account with this email already exists")
        # Everyone signs up as learner. The bootstrap admin is promoted only once the email is
        # proven (verify_email) and only while no admin exists (SRV-02).
        role = Role.LEARNER
        user = self.store.create_user(
            email, self.passwords.hash(password), role, self.clock(), display_name=display_name
        )
        self._audit(
            ctx,
            "user.created",
            user.id,
            target_type="user",
            target_id=str(user.id),
            detail={"role": role.value, "method": "password"},
        )
        self._send_token(user, TokenKind.VERIFY_EMAIL, self.config.verify_ttl)
        return user

    def _maybe_bootstrap_admin(self, user: User, ctx: Context) -> User:
        """Promote the ``RC_AUTH_ADMIN_EMAIL`` account after its email is verified, but only
        while the server has no active admin (so the setting cannot be used later)."""
        if (
            user.email != self.config.bootstrap_admin_email
            or user.email_verified_at is None
            or user.role is Role.ADMIN
            or self.store.count_users(role=Role.ADMIN, status=UserStatus.ACTIVE) > 0
        ):
            return user
        promoted = self.store.update_user(user.id, self.clock(), role=Role.ADMIN)
        self._audit(
            ctx,
            "user.role.changed",
            None,
            target_type="user",
            target_id=str(user.id),
            detail={"from": user.role.value, "to": "admin", "reason": "bootstrap"},
        )
        return promoted

    def promote_admin(self, email: str, ctx: Context) -> User:
        """Operator command (``rc api promote-admin``): make an existing account admin."""
        user = self.store.get_user_by_email(email.strip().lower())
        if user is None or not user.is_active:
            raise NotFound(f"no active account for {email}")
        if user.role is Role.ADMIN:
            return user
        promoted = self.store.update_user(user.id, self.clock(), role=Role.ADMIN)
        self._audit(
            ctx,
            "user.role.changed",
            None,
            target_type="user",
            target_id=str(user.id),
            detail={"from": user.role.value, "to": "admin", "reason": "operator"},
        )
        return promoted

    def _send_token(self, user: User, kind: TokenKind, ttl: timedelta) -> bool:
        if self.mailer is None:
            return False
        token = new_token()
        now = self.clock()
        self.store.create_one_time(user.id, kind, token_hash(token), now, now + ttl)
        path, subject = {
            TokenKind.VERIFY_EMAIL: ("verify-email", "이메일 주소를 확인해 주세요"),
            TokenKind.RESET_PASSWORD: ("reset-password", "비밀번호 재설정"),
            TokenKind.INVITE: ("accept-invite", "초대"),
        }[kind]
        minutes = int(ttl.total_seconds() // 60)
        body = (
            f"{self.config.public_url}/{path}?token={token}\n\n"
            f"이 링크는 {minutes}분 동안 한 번만 쓸 수 있습니다. 요청하지 않았다면 무시하세요.\n"
        )
        self.mailer.send(Mail(to=user.email, subject=subject, body=body))
        return True

    def verify_email(self, token: str, ctx: Context) -> User:
        user_id = self.store.consume_one_time(
            token_hash(token), TokenKind.VERIFY_EMAIL, self.clock()
        )
        if user_id is None:
            raise Invalid("invalid or expired token")
        user = self.store.update_user(user_id, self.clock(), email_verified_at=self.clock())
        self._audit(ctx, "user.email_verified", user_id, target_type="user", target_id=str(user_id))
        return self._maybe_bootstrap_admin(user, ctx)

    def update_profile(self, user: User, ctx: Context, **fields: str | None) -> User:
        allowed = {"display_name", "locale", "timezone"}
        changes = {k: v for k, v in fields.items() if k in allowed}
        if not changes:
            return user
        updated = self.store.update_user(user.id, self.clock(), **changes)
        self._audit(
            ctx,
            "user.profile_updated",
            user.id,
            target_type="user",
            target_id=str(user.id),
            detail={"fields": sorted(changes)},
        )
        return updated

    # -- login / sessions -------------------------------------------------------------

    def login(self, email: str, password: str, ctx: Context) -> LoginResult:
        email = email.strip().lower()
        now = self.clock()
        by_email, by_ip = self.store.failed_logins(email, ctx.ip, now - self.config.login_window)
        if by_email >= self.config.max_failures_account or by_ip >= self.config.max_failures_ip:
            self._audit(
                ctx,
                "auth.login.throttled",
                None,
                target_type="email",
                detail={"by_email": by_email, "by_ip": by_ip},
            )
            retry = str(int(self.config.login_window.total_seconds()))
            raise Throttled(
                "too many failed logins; try again later", headers={"Retry-After": retry}
            )
        user = self.store.get_user_by_email(email)
        stored = self.store.password_hash(user.id) if user else None
        ok = self.passwords.verify(stored, password)
        if not ok or user is None or not user.is_active:
            self.store.record_login(email, ctx.ip, False, now)
            reason = "password" if user and not ok else ("status" if user else "unknown")
            self._audit(
                ctx,
                "auth.login.failed",
                user.id if user else None,
                target_type="user" if user else None,
                target_id=str(user.id) if user else None,
                detail={"reason": reason},
            )
            raise InvalidCredentials("invalid email or password")
        self.store.record_login(email, ctx.ip, True, now)
        if stored is not None and self.passwords.needs_rehash(stored):
            self.store.update_user(user.id, now, password_hash=self.passwords.hash(password))
        result = self._new_session(user, ctx)
        self._audit(
            ctx,
            "auth.login.success",
            user.id,
            target_type="session",
            target_id=str(result.session.id),
            detail={"method": "password"},
        )
        return result

    def _new_session(self, user: User, ctx: Context) -> LoginResult:
        token, csrf = new_token(), new_token()
        now = self.clock()
        session = self.store.create_session(
            user.id,
            token_hash(token),
            token_hash(csrf),
            now,
            now + self.config.session_idle,
            ctx.ip,
            ctx.user_agent,
        )
        return LoginResult(user, session, token, csrf)

    def logout(self, principal: Principal, ctx: Context) -> None:
        if principal.session is not None:
            self.store.revoke_session(principal.session.id, self.clock())
            self._audit(
                ctx,
                "auth.logout",
                principal.user.id,
                target_type="session",
                target_id=str(principal.session.id),
            )

    def authenticate_session(self, token: str) -> Principal | None:
        """The live session for a cookie value, sliding its idle expiry; else ``None``."""
        session = self.store.session_by_token(token_hash(token))
        now = self.clock()
        if (
            session is None
            or session.revoked_at is not None
            or session.expires_at <= now
            or session.created_at + self.config.session_absolute <= now
        ):
            return None
        user = self.store.get_user(session.user_id)
        if user is None or not user.is_active:
            return None
        if now - session.last_seen_at >= timedelta(minutes=1):
            expires = min(
                now + self.config.session_idle, session.created_at + self.config.session_absolute
            )
            self.store.touch_session(session.id, now, expires)
        return Principal(user=user, session=session)

    @staticmethod
    def check_csrf(principal: Principal, header: str | None) -> bool:
        """Double submit bound to the session: the header must hash to the stored value."""
        if principal.session is None:
            return True  # bearer-token requests are not CSRF-able
        return bool(header) and same(token_hash(header or ""), principal.session.csrf_hash)

    def list_sessions(self, user: User) -> list[AuthSession]:
        return self.store.list_sessions(user.id, self.clock())

    def revoke_session(self, user: User, session_id: int, ctx: Context) -> None:
        if not self.store.revoke_session(session_id, self.clock(), user_id=user.id):
            raise NotFound(f"no active session {session_id}")
        self._audit(
            ctx, "auth.session.revoked", user.id, target_type="session", target_id=str(session_id)
        )

    # -- personal access tokens -------------------------------------------------------

    def create_token(
        self,
        user: User,
        name: str,
        scopes: list[Scope],
        ctx: Context,
        *,
        expires_in: timedelta | None = None,
    ) -> tuple[str, ApiToken]:
        """Returns the plaintext token (shown once) and its record."""
        if Scope.ADMIN in scopes and user.role is not Role.ADMIN:
            raise Forbidden("only admins can create tokens with the admin scope")
        if not scopes:
            raise Invalid("a token needs at least one scope")
        plaintext = new_token(PAT_PREFIX)
        now = self.clock()
        record = self.store.create_token(
            user.id,
            name,
            token_hash(plaintext),
            plaintext[: len(PAT_PREFIX) + 6],
            sorted(set(scopes)),
            now,
            now + expires_in if expires_in else None,
        )
        self._audit(
            ctx,
            "auth.token.created",
            user.id,
            target_type="api_token",
            target_id=str(record.id),
            detail={"scopes": [s.value for s in record.scopes]},
        )
        return plaintext, record

    def authenticate_token(self, token: str) -> Principal | None:
        if not token.startswith(PAT_PREFIX):
            return None
        record = self.store.token_by_hash(token_hash(token))
        now = self.clock()
        if (
            record is None
            or record.revoked_at is not None
            or (record.expires_at is not None and record.expires_at <= now)
        ):
            return None
        user = self.store.get_user(record.user_id)
        if user is None or not user.is_active:
            return None
        if record.last_used_at is None or now - record.last_used_at >= timedelta(minutes=1):
            self.store.touch_token(record.id, now)
        return Principal(user=user, token=record)

    def list_tokens(self, user: User) -> list[ApiToken]:
        return self.store.list_tokens(user.id)

    def revoke_token(self, user: User, token_id: int, ctx: Context) -> None:
        if not self.store.revoke_token(token_id, user.id, self.clock()):
            raise NotFound(f"no active token {token_id}")
        self._audit(
            ctx, "auth.token.revoked", user.id, target_type="api_token", target_id=str(token_id)
        )

    # -- passwords --------------------------------------------------------------------

    def change_password(self, principal: Principal, current: str, new: str, ctx: Context) -> None:
        user = principal.user
        if not self.passwords.verify(self.store.password_hash(user.id), current):
            self._audit(ctx, "auth.password.change_failed", user.id)
            raise InvalidCredentials("current password is wrong")
        self._set_password(user, new, ctx)
        keep = principal.session.id if principal.session else None
        self.store.revoke_user_sessions(user.id, self.clock(), keep=keep)
        self._audit(
            ctx, "auth.password.changed", user.id, target_type="user", target_id=str(user.id)
        )

    def _set_password(self, user: User, password: str, ctx: Context) -> None:
        try:
            check_policy(password, email=user.email, display_name=user.display_name)
        except PasswordPolicyError as exc:
            raise Invalid(str(exc)) from None
        self.store.update_user(user.id, self.clock(), password_hash=self.passwords.hash(password))

    @property
    def mail_enabled(self) -> bool:
        return self.mailer is not None

    def forgot_password(self, email: str, ctx: Context) -> None:
        """Mails a reset link if the account exists. Same answer either way (no enumeration)."""
        if self.mailer is None:
            raise Unavailable("password reset is disabled: mail is not configured on this server")
        email = email.strip().lower()
        now = self.clock()
        # Throttle per requested address and per IP whether or not the account exists, so a
        # 429 reveals nothing (SRV-03). Requests are kept in login_attempts under a "reset:"
        # key with success=True, which the login throttle (failures only) ignores.
        key = RESET_KEY_PREFIX + email
        by_email, by_ip = self.store.count_attempts(
            key, ctx.ip, now - self.config.reset_window, prefix=RESET_KEY_PREFIX
        )
        if by_email >= self.config.max_resets_per_window or by_ip >= self.config.max_resets_per_ip:
            self._audit(
                ctx,
                "auth.password.reset_throttled",
                None,
                target_type="email",
                detail={"by_email": by_email, "by_ip": by_ip},
            )
            retry = str(int(self.config.reset_window.total_seconds()))
            raise Throttled(
                "too many reset requests; try again later", headers={"Retry-After": retry}
            )
        self.store.record_login(key, ctx.ip, True, now)
        user = self.store.get_user_by_email(email)
        if user is None or not user.is_active:
            return
        # Only the newest reset link is valid (SRV-04).
        self.store.expire_one_time(user.id, TokenKind.RESET_PASSWORD, now)
        self._send_token(user, TokenKind.RESET_PASSWORD, self.config.reset_ttl)
        self._audit(
            ctx,
            "auth.password.reset_requested",
            None,
            target_type="user",
            target_id=str(user.id),
        )

    def reset_password(self, token: str, new: str, ctx: Context) -> None:
        user_id = self.store.consume_one_time(
            token_hash(token), TokenKind.RESET_PASSWORD, self.clock()
        )
        user = self.store.get_user(user_id) if user_id is not None else None
        if user is None or not user.is_active:
            self._audit(ctx, "auth.password.reset_invalid", None)  # SRV-07
            raise Invalid("invalid or expired token")
        self._set_password(user, new, ctx)
        self.store.expire_one_time(user.id, TokenKind.RESET_PASSWORD, self.clock())
        self.store.revoke_user_sessions(user.id, self.clock())
        self._audit(ctx, "auth.password.reset", user.id, target_type="user", target_id=str(user.id))

    # -- account deletion / export (FR-10.7) ------------------------------------------

    def delete_account(self, principal: Principal, password: str | None, ctx: Context) -> None:
        user = principal.user
        stored = self.store.password_hash(user.id)
        if stored is not None and not self.passwords.verify(stored, password or ""):
            raise InvalidCredentials("password is required to delete the account")
        if user.role is Role.ADMIN and self._is_last_admin(user.id):
            raise Conflict("the last admin cannot delete their account")
        if self.erase_learning_data is not None:
            self.erase_learning_data(user.id)
        self.store.erase_user(user.id, self.clock())
        # SRV-08: drop the user's id and IPs from earlier entries now; the deletion itself is
        # recorded without actor or IP, against the (already anonymized) user row.
        self.store.anonymize_actor(user.id)
        self.store.audit(
            "account.deleted",
            self.clock(),
            actor_user_id=None,
            actor_ip=None,
            target_type="user",
            target_id=str(user.id),
            request_id=ctx.request_id,
        )

    def record_export(self, user: User, ctx: Context) -> None:
        self._audit(ctx, "data.exported", user.id, target_type="user", target_id=str(user.id))

    # -- admin ------------------------------------------------------------------------

    def _is_last_admin(self, user_id: int) -> bool:
        return self.store.count_users(role=Role.ADMIN, status=UserStatus.ACTIVE) <= 1

    def list_users(self, limit: int, after_id: int = 0) -> list[User]:
        return self.store.list_users(limit, after_id)

    def get_user(self, user_id: int) -> User:
        user = self.store.get_user(user_id)
        if user is None:
            raise NotFound(f"unknown user {user_id}")
        return user

    def admin_update_user(
        self,
        actor: User,
        user_id: int,
        ctx: Context,
        *,
        role: Role | None = None,
        status: UserStatus | None = None,
    ) -> User:
        target = self.get_user(user_id)
        if status is not None and status not in (UserStatus.ACTIVE, UserStatus.DISABLED):
            raise Invalid("status can only be set to active or disabled")
        losing_admin = target.role is Role.ADMIN and (
            (role is not None and role is not Role.ADMIN) or (status is UserStatus.DISABLED)
        )
        if losing_admin and target.id == actor.id:
            raise Conflict("admins cannot remove their own admin access")
        if losing_admin and self._is_last_admin(target.id):
            raise Conflict("the last admin cannot be demoted or disabled")
        changes: dict[str, Any] = {}
        if role is not None and role is not target.role:
            changes["role"] = role
        if status is not None and status is not target.status:
            changes["status"] = status
        if not changes:
            return target
        updated = self.store.update_user(target.id, self.clock(), **changes)
        if "role" in changes:
            self._audit(
                ctx,
                "user.role.changed",
                actor.id,
                target_type="user",
                target_id=str(target.id),
                detail={"from": target.role.value, "to": updated.role.value},
            )
        if "status" in changes:
            if updated.status is UserStatus.DISABLED:
                self.store.revoke_user_sessions(target.id, self.clock())
                self.store.revoke_user_tokens(target.id, self.clock())
            self._audit(
                ctx,
                f"user.{updated.status.value}",
                actor.id,
                target_type="user",
                target_id=str(target.id),
            )
        return updated

    def admin_revoke_sessions(self, actor: User, user_id: int, ctx: Context) -> int:
        self.get_user(user_id)
        count = self.store.revoke_user_sessions(user_id, self.clock())
        self._audit(
            ctx,
            "auth.sessions.revoked_by_admin",
            actor.id,
            target_type="user",
            target_id=str(user_id),
            detail={"count": count},
        )
        return count

    def list_audit(
        self, limit: int, before_id: int | None = None, actor_user_id: int | None = None
    ) -> list[AuditEntry]:
        return self.store.list_audit(limit, before_id, actor_user_id)

    def purge_audit(self) -> int:
        """Anonymize audit entries older than the retention period (AC-AUTH.6)."""
        return self.store.anonymize_audit(self.clock() - self.config.audit_retention)

    # -- external identities (OIDC) ----------------------------------------------------

    def oidc_login(
        self, provider: str, claims: Claims, ctx: Context, *, current: Principal | None = None
    ) -> LoginResult:
        """Log in (or sign up / link) with verified OIDC claims.

        1. A known (provider, subject) logs in its user.
        2. A signed-in user starting the flow links the identity to their account.
        3. A verified email that matches an existing account is *not* linked automatically
           (account takeover risk): 409, log in with the password first, then link.
        4. Otherwise a new password-less account is created (needs a verified email).
        """
        now = self.clock()
        known = self.store.identity(provider, claims.subject)
        if known is not None:
            user = self.store.get_user(known.user_id)
            if user is None or not user.is_active:
                self._audit(
                    ctx,
                    "auth.login.failed",
                    known.user_id,
                    detail={"reason": "status", "method": f"oidc:{provider}"},
                )
                raise InvalidCredentials("this account is disabled")
        elif current is not None and current.session is not None:
            user = current.user
            self.store.link_identity(
                user.id, provider, claims.subject, claims.email, claims.raw, now
            )
            self._audit(
                ctx,
                "auth.identity.linked",
                user.id,
                target_type="identity",
                target_id=f"{provider}:{claims.subject}",
            )
        else:
            if not claims.email or not claims.email_verified:
                raise Forbidden("the provider did not return a verified email address")
            if self.store.get_user_by_email(claims.email) is not None:
                raise Conflict(
                    "an account with this email already exists: log in with your password, "
                    "then start this login again to link it"
                )
            if not self.config.allow_signup:
                raise Forbidden("sign-up is disabled on this server")
            role = Role.LEARNER
            user = self.store.create_user(
                claims.email, None, role, now, display_name=claims.name, email_verified_at=now
            )
            self.store.link_identity(
                user.id, provider, claims.subject, claims.email, claims.raw, now
            )
            self._audit(
                ctx,
                "user.created",
                user.id,
                target_type="user",
                target_id=str(user.id),
                detail={"role": role.value, "method": f"oidc:{provider}"},
            )
            user = self._maybe_bootstrap_admin(user, ctx)  # the IdP verified the email
        result = self._new_session(user, ctx)
        self._audit(
            ctx,
            "auth.login.success",
            user.id,
            target_type="session",
            target_id=str(result.session.id),
            detail={"method": f"oidc:{provider}"},
        )
        return result

    def list_identities(self, user: User) -> list[Identity]:
        return self.store.list_identities(user.id)

    def unlink_identity(self, user: User, identity_id: int, ctx: Context) -> None:
        owned = self.store.list_identities(user.id)
        if all(i.id != identity_id for i in owned):
            raise NotFound(f"no linked identity {identity_id}")
        if not user.has_password and len(owned) == 1:
            raise Conflict("this is the only way to sign in; set a password first")
        self.store.unlink_identity(identity_id, user.id)
        self._audit(
            ctx,
            "auth.identity.unlinked",
            user.id,
            target_type="identity",
            target_id=str(identity_id),
        )

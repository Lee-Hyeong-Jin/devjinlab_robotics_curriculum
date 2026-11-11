"""Auth persistence: the :class:`AuthStore` interface and its SQLAlchemy Core implementation.

One implementation serves SQLite (development, tests, single-node) and PostgreSQL (server
mode). On SQLite the tables are created on open; on PostgreSQL Alembic owns the schema
(revision 0003, P2-3). Every query that touches a user's data is bound to a ``user_id``.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any, Protocol

from sqlalchemy import (
    Connection,
    Engine,
    and_,
    create_engine,
    delete,
    event,
    func,
    insert,
    or_,
    select,
    update,
)
from sqlalchemy.engine import RowMapping

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
from robotics_curriculum.auth.schema import (
    api_tokens,
    audit_log,
    auth_metadata,
    identities,
    login_attempts,
    one_time_tokens,
    sessions_auth,
    users,
)


def _aware(value: datetime | None) -> datetime | None:
    """SQLite returns naive datetimes; everything here is UTC."""
    if value is None or value.tzinfo is not None:
        return value
    return value.replace(tzinfo=UTC)


def _req(value: datetime | None) -> datetime:
    aware = _aware(value)
    assert aware is not None
    return aware


class AuthStore(Protocol):
    """Everything the auth service needs from storage."""

    # users
    def create_user(
        self, email: str, password_hash: str | None, role: Role, now: datetime, **profile: Any
    ) -> User: ...
    def get_user(self, user_id: int) -> User | None: ...
    def get_user_by_email(self, email: str) -> User | None: ...
    def password_hash(self, user_id: int) -> str | None: ...
    def update_user(self, user_id: int, now: datetime, **fields: Any) -> User: ...
    def list_users(self, limit: int, after_id: int = 0) -> list[User]: ...
    def count_users(self, *, role: Role | None = None, status: UserStatus | None = None) -> int: ...
    def erase_user(self, user_id: int, now: datetime) -> None: ...

    # browser sessions
    def create_session(
        self,
        user_id: int,
        token_hash: str,
        csrf_hash: str,
        now: datetime,
        expires_at: datetime,
        ip: str | None,
        user_agent: str | None,
    ) -> AuthSession: ...
    def session_by_token(self, token_hash: str) -> AuthSession | None: ...
    def touch_session(self, session_id: int, now: datetime, expires_at: datetime) -> None: ...
    def revoke_session(
        self, session_id: int, now: datetime, *, user_id: int | None = None
    ) -> bool: ...
    def revoke_user_sessions(
        self, user_id: int, now: datetime, *, keep: int | None = None
    ) -> int: ...
    def list_sessions(self, user_id: int, now: datetime) -> list[AuthSession]: ...

    # personal access tokens
    def create_token(
        self,
        user_id: int,
        name: str,
        token_hash: str,
        prefix: str,
        scopes: list[Scope],
        now: datetime,
        expires_at: datetime | None,
    ) -> ApiToken: ...
    def token_by_hash(self, token_hash: str) -> ApiToken | None: ...
    def touch_token(self, token_id: int, now: datetime) -> None: ...
    def revoke_token(self, token_id: int, user_id: int, now: datetime) -> bool: ...
    def revoke_user_tokens(self, user_id: int, now: datetime) -> int: ...
    def list_tokens(self, user_id: int) -> list[ApiToken]: ...

    # one-time tokens
    def create_one_time(
        self, user_id: int, kind: TokenKind, token_hash: str, now: datetime, expires_at: datetime
    ) -> None: ...
    def consume_one_time(self, token_hash: str, kind: TokenKind, now: datetime) -> int | None: ...

    # login throttling
    def record_login(self, email: str, ip: str | None, success: bool, now: datetime) -> None: ...
    def failed_logins(self, email: str, ip: str | None, since: datetime) -> tuple[int, int]: ...

    # audit
    def audit(
        self,
        action: str,
        now: datetime,
        *,
        actor_user_id: int | None,
        actor_ip: str | None,
        target_type: str | None = None,
        target_id: str | None = None,
        detail: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> None: ...
    def list_audit(
        self, limit: int, before_id: int | None = None, actor_user_id: int | None = None
    ) -> list[AuditEntry]: ...
    def anonymize_audit(self, before: datetime) -> int: ...

    # external identities (OIDC)
    def identity(self, provider: str, subject: str) -> Identity | None: ...
    def link_identity(
        self,
        user_id: int,
        provider: str,
        subject: str,
        email: str | None,
        claims: dict[str, Any],
        now: datetime,
    ) -> Identity: ...
    def list_identities(self, user_id: int) -> list[Identity]: ...
    def unlink_identity(self, identity_id: int, user_id: int) -> bool: ...

    def schema_ready(self) -> bool: ...
    def close(self) -> None: ...


class SqlAuthStore:
    """:class:`AuthStore` over a SQLAlchemy engine (SQLite or PostgreSQL)."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    @classmethod
    def from_url(cls, url: str) -> SqlAuthStore:
        if url.startswith(("postgresql://", "postgres://")):
            url = "postgresql+psycopg://" + url.split("://", 1)[1]
        engine = create_engine(url, future=True)
        if engine.dialect.name == "sqlite":

            @event.listens_for(engine, "connect")
            def _fk_on(dbapi_conn: Any, _record: Any) -> None:
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

            auth_metadata.create_all(engine)
        return cls(engine)

    def close(self) -> None:
        self.engine.dispose()

    @contextmanager
    def _tx(self) -> Iterator[Connection]:
        with self.engine.begin() as conn:
            yield conn

    def schema_ready(self) -> bool:
        """``True`` when every auth table exists (PostgreSQL needs Alembic 0003)."""
        from sqlalchemy import inspect

        names = set(inspect(self.engine).get_table_names())
        return set(auth_metadata.tables) <= names

    # -- users -------------------------------------------------------------------------

    @staticmethod
    def _user(row: RowMapping) -> User:
        return User(
            id=row["id"],
            email=row["email"],
            email_verified_at=_aware(row["email_verified_at"]),
            display_name=row["display_name"],
            locale=row["locale"],
            timezone=row["timezone"],
            role=Role(row["role"]),
            status=UserStatus(row["status"]),
            has_password=row["password_hash"] is not None,
            created_at=_req(row["created_at"]),
            updated_at=_req(row["updated_at"]),
        )

    def create_user(
        self, email: str, password_hash: str | None, role: Role, now: datetime, **profile: Any
    ) -> User:
        with self._tx() as conn:
            row = (
                conn.execute(
                    insert(users)
                    .values(
                        email=email.lower(),
                        password_hash=password_hash,
                        role=role.value,
                        created_at=now,
                        updated_at=now,
                        **profile,
                    )
                    .returning(*users.c)
                )
                .mappings()
                .one()
            )
        return self._user(row)

    def get_user(self, user_id: int) -> User | None:
        with self._tx() as conn:
            row = conn.execute(select(users).where(users.c.id == user_id)).mappings().first()
        return self._user(row) if row else None

    def get_user_by_email(self, email: str) -> User | None:
        with self._tx() as conn:
            row = (
                conn.execute(select(users).where(func.lower(users.c.email) == email.lower()))
                .mappings()
                .first()
            )
        return self._user(row) if row else None

    def password_hash(self, user_id: int) -> str | None:
        with self._tx() as conn:
            value = conn.execute(
                select(users.c.password_hash).where(users.c.id == user_id)
            ).scalar_one_or_none()
        return value

    def update_user(self, user_id: int, now: datetime, **fields: Any) -> User:
        values = {
            k: (v.value if isinstance(v, Role | UserStatus) else v) for k, v in fields.items()
        }
        with self._tx() as conn:
            row = (
                conn.execute(
                    update(users)
                    .where(users.c.id == user_id)
                    .values(**values, updated_at=now)
                    .returning(*users.c)
                )
                .mappings()
                .one()
            )
        return self._user(row)

    def list_users(self, limit: int, after_id: int = 0) -> list[User]:
        with self._tx() as conn:
            rows = (
                conn.execute(
                    select(users).where(users.c.id > after_id).order_by(users.c.id).limit(limit)
                )
                .mappings()
                .all()
            )
        return [self._user(r) for r in rows]

    def count_users(self, *, role: Role | None = None, status: UserStatus | None = None) -> int:
        query = select(func.count()).select_from(users)
        if role is not None:
            query = query.where(users.c.role == role.value)
        if status is not None:
            query = query.where(users.c.status == status.value)
        with self._tx() as conn:
            return int(conn.execute(query).scalar_one())

    def erase_user(self, user_id: int, now: datetime) -> None:
        """Account deletion: drop credentials and identities, anonymize the user row."""
        with self._tx() as conn:
            for table in (sessions_auth, api_tokens, one_time_tokens, identities):
                conn.execute(delete(table).where(table.c.user_id == user_id))
            conn.execute(
                update(users)
                .where(users.c.id == user_id)
                .values(
                    email=f"deleted-{user_id}@invalid",
                    display_name=None,
                    locale=None,
                    timezone=None,
                    password_hash=None,
                    mfa_enabled=False,
                    mfa_secret_enc=None,
                    status=UserStatus.DELETED.value,
                    deleted_at=now,
                    updated_at=now,
                )
            )

    # -- browser sessions ----------------------------------------------------------------

    @staticmethod
    def _session(row: RowMapping) -> AuthSession:
        return AuthSession(
            id=row["id"],
            user_id=row["user_id"],
            created_at=_req(row["created_at"]),
            last_seen_at=_req(row["last_seen_at"]),
            expires_at=_req(row["expires_at"]),
            ip=row["ip"],
            user_agent=row["user_agent"],
            revoked_at=_aware(row["revoked_at"]),
            csrf_hash=row["csrf_hash"],
        )

    def create_session(
        self,
        user_id: int,
        token_hash: str,
        csrf_hash: str,
        now: datetime,
        expires_at: datetime,
        ip: str | None,
        user_agent: str | None,
    ) -> AuthSession:
        with self._tx() as conn:
            row = (
                conn.execute(
                    insert(sessions_auth)
                    .values(
                        user_id=user_id,
                        token_hash=token_hash,
                        csrf_hash=csrf_hash,
                        created_at=now,
                        last_seen_at=now,
                        expires_at=expires_at,
                        ip=ip,
                        user_agent=(user_agent or "")[:300] or None,
                    )
                    .returning(*sessions_auth.c)
                )
                .mappings()
                .one()
            )
        return self._session(row)

    def session_by_token(self, token_hash: str) -> AuthSession | None:
        with self._tx() as conn:
            row = (
                conn.execute(select(sessions_auth).where(sessions_auth.c.token_hash == token_hash))
                .mappings()
                .first()
            )
        return self._session(row) if row else None

    def touch_session(self, session_id: int, now: datetime, expires_at: datetime) -> None:
        with self._tx() as conn:
            conn.execute(
                update(sessions_auth)
                .where(sessions_auth.c.id == session_id)
                .values(last_seen_at=now, expires_at=expires_at)
            )

    def revoke_session(self, session_id: int, now: datetime, *, user_id: int | None = None) -> bool:
        cond = and_(sessions_auth.c.id == session_id, sessions_auth.c.revoked_at.is_(None))
        if user_id is not None:
            cond = and_(cond, sessions_auth.c.user_id == user_id)
        with self._tx() as conn:
            result = conn.execute(update(sessions_auth).where(cond).values(revoked_at=now))
        return result.rowcount > 0

    def revoke_user_sessions(self, user_id: int, now: datetime, *, keep: int | None = None) -> int:
        cond = and_(sessions_auth.c.user_id == user_id, sessions_auth.c.revoked_at.is_(None))
        if keep is not None:
            cond = and_(cond, sessions_auth.c.id != keep)
        with self._tx() as conn:
            return conn.execute(update(sessions_auth).where(cond).values(revoked_at=now)).rowcount

    def list_sessions(self, user_id: int, now: datetime) -> list[AuthSession]:
        with self._tx() as conn:
            rows = (
                conn.execute(
                    select(sessions_auth)
                    .where(
                        sessions_auth.c.user_id == user_id,
                        sessions_auth.c.revoked_at.is_(None),
                        sessions_auth.c.expires_at > now,
                    )
                    .order_by(sessions_auth.c.last_seen_at.desc())
                )
                .mappings()
                .all()
            )
        return [self._session(r) for r in rows]

    # -- personal access tokens ----------------------------------------------------------

    @staticmethod
    def _token(row: RowMapping) -> ApiToken:
        return ApiToken(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            prefix=row["prefix"],
            scopes=[Scope(s) for s in json.loads(row["scopes_json"])],
            created_at=_req(row["created_at"]),
            expires_at=_aware(row["expires_at"]),
            last_used_at=_aware(row["last_used_at"]),
            revoked_at=_aware(row["revoked_at"]),
        )

    def create_token(
        self,
        user_id: int,
        name: str,
        token_hash: str,
        prefix: str,
        scopes: list[Scope],
        now: datetime,
        expires_at: datetime | None,
    ) -> ApiToken:
        with self._tx() as conn:
            row = (
                conn.execute(
                    insert(api_tokens)
                    .values(
                        user_id=user_id,
                        name=name,
                        token_hash=token_hash,
                        prefix=prefix,
                        scopes_json=json.dumps([s.value for s in scopes]),
                        created_at=now,
                        expires_at=expires_at,
                    )
                    .returning(*api_tokens.c)
                )
                .mappings()
                .one()
            )
        return self._token(row)

    def token_by_hash(self, token_hash: str) -> ApiToken | None:
        with self._tx() as conn:
            row = (
                conn.execute(select(api_tokens).where(api_tokens.c.token_hash == token_hash))
                .mappings()
                .first()
            )
        return self._token(row) if row else None

    def touch_token(self, token_id: int, now: datetime) -> None:
        with self._tx() as conn:
            conn.execute(
                update(api_tokens).where(api_tokens.c.id == token_id).values(last_used_at=now)
            )

    def revoke_token(self, token_id: int, user_id: int, now: datetime) -> bool:
        with self._tx() as conn:
            result = conn.execute(
                update(api_tokens)
                .where(
                    api_tokens.c.id == token_id,
                    api_tokens.c.user_id == user_id,
                    api_tokens.c.revoked_at.is_(None),
                )
                .values(revoked_at=now)
            )
        return result.rowcount > 0

    def revoke_user_tokens(self, user_id: int, now: datetime) -> int:
        with self._tx() as conn:
            return conn.execute(
                update(api_tokens)
                .where(api_tokens.c.user_id == user_id, api_tokens.c.revoked_at.is_(None))
                .values(revoked_at=now)
            ).rowcount

    def list_tokens(self, user_id: int) -> list[ApiToken]:
        with self._tx() as conn:
            rows = (
                conn.execute(
                    select(api_tokens)
                    .where(api_tokens.c.user_id == user_id, api_tokens.c.revoked_at.is_(None))
                    .order_by(api_tokens.c.id)
                )
                .mappings()
                .all()
            )
        return [self._token(r) for r in rows]

    # -- one-time tokens ------------------------------------------------------------------

    def create_one_time(
        self, user_id: int, kind: TokenKind, token_hash: str, now: datetime, expires_at: datetime
    ) -> None:
        with self._tx() as conn:
            conn.execute(
                insert(one_time_tokens).values(
                    user_id=user_id,
                    kind=kind.value,
                    token_hash=token_hash,
                    created_at=now,
                    expires_at=expires_at,
                )
            )

    def consume_one_time(self, token_hash: str, kind: TokenKind, now: datetime) -> int | None:
        """Mark the token used and return its user id; ``None`` if unknown/used/expired."""
        with self._tx() as conn:
            row = (
                conn.execute(
                    update(one_time_tokens)
                    .where(
                        one_time_tokens.c.token_hash == token_hash,
                        one_time_tokens.c.kind == kind.value,
                        one_time_tokens.c.used_at.is_(None),
                        one_time_tokens.c.expires_at > now,
                    )
                    .values(used_at=now)
                    .returning(one_time_tokens.c.user_id)
                )
                .scalars()
                .first()
            )
        return row

    # -- login throttling -----------------------------------------------------------------

    def record_login(self, email: str, ip: str | None, success: bool, now: datetime) -> None:
        with self._tx() as conn:
            conn.execute(
                insert(login_attempts).values(at=now, email=email.lower(), ip=ip, success=success)
            )

    def failed_logins(self, email: str, ip: str | None, since: datetime) -> tuple[int, int]:
        """Failures since ``since`` for this account and for this IP."""
        base = select(func.count()).select_from(login_attempts)
        recent = and_(login_attempts.c.at >= since, login_attempts.c.success.is_(False))
        with self._tx() as conn:
            by_email = conn.execute(
                base.where(recent, login_attempts.c.email == email.lower())
            ).scalar_one()
            by_ip = (
                conn.execute(base.where(recent, login_attempts.c.ip == ip)).scalar_one()
                if ip
                else 0
            )
        return int(by_email), int(by_ip)

    # -- audit ----------------------------------------------------------------------------

    def audit(
        self,
        action: str,
        now: datetime,
        *,
        actor_user_id: int | None,
        actor_ip: str | None,
        target_type: str | None = None,
        target_id: str | None = None,
        detail: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> None:
        with self._tx() as conn:
            conn.execute(
                insert(audit_log).values(
                    at=now,
                    actor_user_id=actor_user_id,
                    actor_ip=actor_ip,
                    action=action,
                    target_type=target_type,
                    target_id=target_id,
                    detail_json=json.dumps(detail or {}, ensure_ascii=False, default=str),
                    request_id=request_id,
                )
            )

    def list_audit(
        self, limit: int, before_id: int | None = None, actor_user_id: int | None = None
    ) -> list[AuditEntry]:
        query = select(audit_log).order_by(audit_log.c.id.desc()).limit(limit)
        if before_id is not None:
            query = query.where(audit_log.c.id < before_id)
        if actor_user_id is not None:
            query = query.where(audit_log.c.actor_user_id == actor_user_id)
        with self._tx() as conn:
            rows = conn.execute(query).mappings().all()
        return [
            AuditEntry(
                id=r["id"],
                at=_req(r["at"]),
                actor_user_id=r["actor_user_id"],
                actor_ip=r["actor_ip"],
                action=r["action"],
                target_type=r["target_type"],
                target_id=r["target_id"],
                detail=json.loads(r["detail_json"] or "{}"),
                request_id=r["request_id"],
            )
            for r in rows
        ]

    def anonymize_audit(self, before: datetime) -> int:
        """Drop personal identifiers (actor id, IP) from entries older than ``before``."""
        with self._tx() as conn:
            return conn.execute(
                update(audit_log)
                .where(
                    audit_log.c.at < before,
                    or_(audit_log.c.actor_user_id.is_not(None), audit_log.c.actor_ip.is_not(None)),
                )
                .values(actor_user_id=None, actor_ip=None)
            ).rowcount

    # -- external identities ------------------------------------------------------------

    @staticmethod
    def _identity(row: RowMapping) -> Identity:
        return Identity(
            id=row["id"],
            user_id=row["user_id"],
            provider=row["provider"],
            subject=row["subject"],
            email=row["email"],
            linked_at=_req(row["linked_at"]),
        )

    def identity(self, provider: str, subject: str) -> Identity | None:
        with self._tx() as conn:
            row = (
                conn.execute(
                    select(identities).where(
                        identities.c.provider == provider, identities.c.subject == subject
                    )
                )
                .mappings()
                .first()
            )
        return self._identity(row) if row else None

    def link_identity(
        self,
        user_id: int,
        provider: str,
        subject: str,
        email: str | None,
        claims: dict[str, Any],
        now: datetime,
    ) -> Identity:
        with self._tx() as conn:
            row = (
                conn.execute(
                    insert(identities)
                    .values(
                        user_id=user_id,
                        provider=provider,
                        subject=subject,
                        email=email,
                        raw_claims_json=json.dumps(claims, ensure_ascii=False, default=str),
                        linked_at=now,
                    )
                    .returning(*identities.c)
                )
                .mappings()
                .one()
            )
        return self._identity(row)

    def list_identities(self, user_id: int) -> list[Identity]:
        with self._tx() as conn:
            rows = (
                conn.execute(
                    select(identities)
                    .where(identities.c.user_id == user_id)
                    .order_by(identities.c.id)
                )
                .mappings()
                .all()
            )
        return [self._identity(r) for r in rows]

    def unlink_identity(self, identity_id: int, user_id: int) -> bool:
        with self._tx() as conn:
            result = conn.execute(
                delete(identities).where(
                    identities.c.id == identity_id, identities.c.user_id == user_id
                )
            )
        return result.rowcount > 0

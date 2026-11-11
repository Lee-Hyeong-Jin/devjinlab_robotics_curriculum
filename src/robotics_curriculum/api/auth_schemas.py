"""Request/response bodies of the auth, ``/me`` and ``/admin`` endpoints
(names follow ``docs/api/openapi.yaml``). Secrets only ever leave the server once:
the PAT in :class:`ApiTokenCreated` and the CSRF token in :class:`LoginResult`."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from robotics_curriculum.auth import models
from robotics_curriculum.auth.models import Role, Scope, UserStatus


class Schema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SignupRequest(Schema):
    email: str = Field(min_length=3, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(max_length=1024)
    display_name: str | None = Field(default=None, max_length=100)


class LoginRequest(Schema):
    email: str = Field(max_length=254)
    password: str = Field(max_length=1024)
    remember: bool = Field(
        default=False,
        description="Accepted for the frontend contract; sessions always last 14 days.",
    )


class TokenRequest(Schema):
    token: str = Field(max_length=200)


class ForgotRequest(Schema):
    email: str = Field(max_length=254)


class ResetRequest(Schema):
    token: str = Field(max_length=200)
    password: str = Field(max_length=1024)


class PasswordChange(Schema):
    current_password: str = Field(max_length=1024)
    new_password: str = Field(max_length=1024)


class DeleteAccount(Schema):
    password: str | None = Field(default=None, max_length=1024)


class User(Schema):
    id: int
    email: str
    email_verified: bool
    display_name: str | None
    locale: str | None
    timezone: str | None
    role: Role
    status: UserStatus
    created_at: datetime

    @classmethod
    def of(cls, user: models.User) -> User:
        return cls(
            id=user.id,
            email=user.email,
            email_verified=user.email_verified_at is not None,
            display_name=user.display_name,
            locale=user.locale,
            timezone=user.timezone,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
        )


class AdminUser(User):
    has_password: bool
    updated_at: datetime

    @classmethod
    def of(cls, user: models.User) -> AdminUser:
        return cls(
            **User.of(user).model_dump(),
            has_password=user.has_password,
            updated_at=user.updated_at,
        )


class UserPage(Schema):
    items: list[AdminUser]
    next_cursor: str | None = Field(description="Pass as `cursor` for the next page.")


class UserUpdate(Schema):
    display_name: str | None = Field(default=None, max_length=100)
    locale: Literal["ko", "en"] | None = None
    timezone: str | None = Field(default=None, max_length=64)


class AdminUserUpdate(Schema):
    role: Role | None = None
    status: UserStatus | None = Field(default=None, description="active or disabled")


class LoginResult(Schema):
    user: User
    csrf_token: str = Field(
        description="Send as X-CSRF-Token on state-changing requests (also set as a cookie)."
    )


class AuthSession(Schema):
    id: int
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime
    ip: str | None
    user_agent: str | None
    current: bool

    @classmethod
    def of(cls, session: models.AuthSession, current_id: int | None) -> AuthSession:
        return cls(
            id=session.id,
            created_at=session.created_at,
            last_seen_at=session.last_seen_at,
            expires_at=session.expires_at,
            ip=session.ip,
            user_agent=session.user_agent,
            current=session.id == current_id,
        )


class ApiTokenCreate(Schema):
    name: str = Field(min_length=1, max_length=100)
    scopes: list[Scope] = Field(min_length=1)
    expires_in_days: int | None = Field(default=90, ge=1, le=365, description="null = no expiry")


class ApiToken(Schema):
    id: int
    name: str
    prefix: str = Field(description="First characters of the token, for recognition.")
    scopes: list[Scope]
    created_at: datetime
    expires_at: datetime | None
    last_used_at: datetime | None

    @classmethod
    def of(cls, token: models.ApiToken) -> ApiToken:
        return cls.model_validate(
            token.model_dump(
                include={
                    "id",
                    "name",
                    "prefix",
                    "scopes",
                    "created_at",
                    "expires_at",
                    "last_used_at",
                }
            )
        )


class ApiTokenCreated(ApiToken):
    token: str = Field(description="The secret. Shown only in this response.")


class AuditEntry(Schema):
    id: int
    at: datetime
    actor_user_id: int | None
    actor_ip: str | None
    action: str
    target_type: str | None
    target_id: str | None
    detail: dict[str, Any]
    request_id: str | None


class AuditPage(Schema):
    items: list[AuditEntry]
    next_cursor: str | None


class Identity(Schema):
    """A linked external login (OIDC provider)."""

    id: int
    provider: str
    email: str | None
    linked_at: datetime

    @classmethod
    def of(cls, identity: models.Identity) -> Identity:
        return cls(
            id=identity.id,
            provider=identity.provider,
            email=identity.email,
            linked_at=identity.linked_at,
        )

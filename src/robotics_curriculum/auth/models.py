"""Auth domain models (pydantic). Secrets never appear in these models."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Role(StrEnum):
    LEARNER = "learner"
    AUTHOR = "author"
    ADMIN = "admin"

    @property
    def rank(self) -> int:
        return _RANK[self]

    def includes(self, other: Role) -> bool:
        """Higher roles include every permission of the lower ones."""
        return self.rank >= other.rank


_RANK = {Role.LEARNER: 0, Role.AUTHOR: 1, Role.ADMIN: 2}


class UserStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    PENDING_DELETION = "pending_deletion"
    DELETED = "deleted"


class Scope(StrEnum):
    """PAT scopes (ADR 0009)."""

    READ_PROGRESS = "read:progress"
    WRITE_PROGRESS = "write:progress"
    ADMIN = "admin"


class TokenKind(StrEnum):
    VERIFY_EMAIL = "verify_email"
    RESET_PASSWORD = "reset_password"
    INVITE = "invite"


class AuthModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class User(AuthModel):
    id: int
    email: str
    email_verified_at: datetime | None = None
    display_name: str | None = None
    locale: str | None = None
    timezone: str | None = None
    role: Role = Role.LEARNER
    status: UserStatus = UserStatus.ACTIVE
    has_password: bool = True
    created_at: datetime
    updated_at: datetime

    @property
    def is_active(self) -> bool:
        return self.status is UserStatus.ACTIVE


class AuthSession(AuthModel):
    id: int
    user_id: int
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime
    ip: str | None = None
    user_agent: str | None = None
    revoked_at: datetime | None = None
    csrf_hash: str = Field(exclude=True, repr=False)


class ApiToken(AuthModel):
    id: int
    user_id: int
    name: str
    prefix: str
    scopes: list[Scope]
    created_at: datetime
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    revoked_at: datetime | None = None


class AuditEntry(AuthModel):
    id: int
    at: datetime
    actor_user_id: int | None
    actor_ip: str | None
    action: str
    target_type: str | None
    target_id: str | None
    detail: dict[str, Any] = Field(default_factory=dict)
    request_id: str | None


class OneTimeToken(AuthModel):
    id: int
    user_id: int
    kind: TokenKind
    expires_at: datetime
    used_at: datetime | None = None

"""Auth tables as SQLAlchemy Core (the source for Alembic revision 0003, written by P2-3).

Secrets are never stored: session ids, CSRF tokens, PATs and one-time tokens are kept as
SHA-256 hex digests, passwords as Argon2id hashes. Emails are stored lowercased.
"""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Table,
    Text,
    UniqueConstraint,
    false,
    func,
    text,
)

auth_metadata = MetaData()

# BigInteger primary keys become INTEGER on SQLite so they still autoincrement.
BigId = BigInteger().with_variant(Integer(), "sqlite")


def _ts(name: str, *, nullable: bool = True) -> Column[object]:
    return Column(name, DateTime(timezone=True), nullable=nullable)


users = Table(
    "users",
    auth_metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("email", Text, nullable=False),
    _ts("email_verified_at"),
    Column("display_name", Text),
    Column("locale", Text),
    Column("timezone", Text),
    Column("password_hash", Text, comment="Argon2id; NULL for OIDC-only accounts"),
    Column("role", Text, nullable=False, server_default=text("'learner'")),
    Column("status", Text, nullable=False, server_default=text("'active'")),
    Column("mfa_enabled", Boolean, nullable=False, server_default=false()),
    Column("mfa_secret_enc", Text),
    _ts("created_at", nullable=False),
    _ts("updated_at", nullable=False),
    _ts("deleted_at"),
    CheckConstraint("role IN ('learner', 'author', 'admin')", name="users_role"),
    CheckConstraint(
        "status IN ('active', 'disabled', 'pending_deletion', 'deleted')", name="users_status"
    ),
)
Index("users_email_lower", func.lower(users.c.email), unique=True)

identities = Table(
    "identities",
    auth_metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("provider", Text, nullable=False),
    Column("subject", Text, nullable=False),
    Column("email", Text),
    Column("raw_claims_json", Text),
    _ts("linked_at", nullable=False),
    UniqueConstraint("provider", "subject", name="identities_provider_subject"),
)

sessions_auth = Table(
    "sessions_auth",
    auth_metadata,
    Column("id", BigId, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("token_hash", Text, nullable=False, unique=True),
    Column("csrf_hash", Text, nullable=False),
    _ts("created_at", nullable=False),
    _ts("last_seen_at", nullable=False),
    _ts("expires_at", nullable=False),
    Column("ip", Text),
    Column("user_agent", Text),
    _ts("revoked_at"),
    Index("sessions_auth_user", "user_id"),
)

api_tokens = Table(
    "api_tokens",
    auth_metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("name", Text, nullable=False),
    Column("token_hash", Text, nullable=False, unique=True),
    Column("prefix", Text, nullable=False, comment="first characters, for display"),
    Column("scopes_json", Text, nullable=False),
    _ts("created_at", nullable=False),
    _ts("expires_at"),
    _ts("last_used_at"),
    _ts("revoked_at"),
    Index("api_tokens_user", "user_id"),
)

one_time_tokens = Table(
    "one_time_tokens",
    auth_metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("kind", Text, nullable=False),
    Column("token_hash", Text, nullable=False, unique=True),
    _ts("created_at", nullable=False),
    _ts("expires_at", nullable=False),
    _ts("used_at"),
    CheckConstraint(
        "kind IN ('verify_email', 'reset_password', 'invite')", name="one_time_tokens_kind"
    ),
)

login_attempts = Table(
    "login_attempts",
    auth_metadata,
    Column("id", BigId, primary_key=True, autoincrement=True),
    _ts("at", nullable=False),
    Column("email", Text, nullable=False),
    Column("ip", Text),
    Column("success", Boolean, nullable=False),
    Index("login_attempts_email_at", "email", "at"),
    Index("login_attempts_ip_at", "ip", "at"),
)

audit_log = Table(
    "audit_log",
    auth_metadata,
    Column("id", BigId, primary_key=True, autoincrement=True),
    _ts("at", nullable=False),
    Column("actor_user_id", Integer, comment="no FK: entries outlive deleted accounts"),
    Column("actor_ip", Text),
    Column("action", Text, nullable=False),
    Column("target_type", Text),
    Column("target_id", Text),
    Column("detail_json", Text),
    Column("request_id", Text),
    Index("audit_log_at", "at"),
    Index("audit_log_actor", "actor_user_id"),
)

"""Server-mode auth tables: users, identities, sessions_auth, api_tokens, one_time_tokens,
login_attempts, audit_log (P2-2).

Mirrors ``robotics_curriculum.auth.schema`` (api-developer owns that file; the drift test
compares the two once the module is on this branch). Server mode only: local mode has no
accounts, so the SQLite ``MIGRATIONS`` dict does not grow a step for this and
``meta.schema_version`` stays at 2 — it tracks the learning schema the two backends share.

Secrets are stored as digests by the application, never in clear text; this revision only
provides the columns.

Revision ID: 0003_auth
Revises: 0002_progress_v2
Create Date: 2026-11-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_auth"
down_revision: str | None = "0002_progress_v2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _ts(name: str, *, nullable: bool = True) -> sa.Column[object]:
    return sa.Column(name, sa.DateTime(timezone=True), nullable=nullable)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.Text(), nullable=False),
        _ts("email_verified_at"),
        sa.Column("display_name", sa.Text()),
        sa.Column("locale", sa.Text()),
        sa.Column("timezone", sa.Text()),
        sa.Column("password_hash", sa.Text(), comment="Argon2id; NULL for OIDC-only accounts"),
        sa.Column("role", sa.Text(), nullable=False, server_default=sa.text("'learner'")),
        sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'active'")),
        sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("mfa_secret_enc", sa.Text()),
        _ts("created_at", nullable=False),
        _ts("updated_at", nullable=False),
        _ts("deleted_at"),
        sa.CheckConstraint("role IN ('learner', 'author', 'admin')", name="users_role"),
        sa.CheckConstraint(
            "status IN ('active', 'disabled', 'pending_deletion', 'deleted')",
            name="users_status",
        ),
    )
    # Case-insensitive uniqueness: emails are stored lowercased, this enforces it.
    op.create_index("users_email_lower", "users", [sa.text("lower(email)")], unique=True)

    op.create_table(
        "identities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("subject", sa.Text(), nullable=False),
        sa.Column("email", sa.Text()),
        sa.Column("raw_claims_json", sa.Text()),
        _ts("linked_at", nullable=False),
        sa.UniqueConstraint("provider", "subject", name="identities_provider_subject"),
    )

    op.create_table(
        "sessions_auth",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.Text(), nullable=False, unique=True),
        sa.Column("csrf_hash", sa.Text(), nullable=False),
        _ts("created_at", nullable=False),
        _ts("last_seen_at", nullable=False),
        _ts("expires_at", nullable=False),
        sa.Column("ip", sa.Text()),
        sa.Column("user_agent", sa.Text()),
        _ts("revoked_at"),
    )
    op.create_index("sessions_auth_user", "sessions_auth", ["user_id"])

    op.create_table(
        "api_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False, unique=True),
        sa.Column("prefix", sa.Text(), nullable=False, comment="first characters, for display"),
        sa.Column("scopes_json", sa.Text(), nullable=False),
        _ts("created_at", nullable=False),
        _ts("expires_at"),
        _ts("last_used_at"),
        _ts("revoked_at"),
    )
    op.create_index("api_tokens_user", "api_tokens", ["user_id"])

    op.create_table(
        "one_time_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False, unique=True),
        _ts("created_at", nullable=False),
        _ts("expires_at", nullable=False),
        _ts("used_at"),
        sa.CheckConstraint(
            "kind IN ('verify_email', 'reset_password', 'invite')", name="one_time_tokens_kind"
        ),
    )

    op.create_table(
        "login_attempts",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        _ts("at", nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("ip", sa.Text()),
        sa.Column("success", sa.Boolean(), nullable=False),
    )
    op.create_index("login_attempts_email_at", "login_attempts", ["email", "at"])
    op.create_index("login_attempts_ip_at", "login_attempts", ["ip", "at"])

    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        _ts("at", nullable=False),
        sa.Column("actor_user_id", sa.Integer(), comment="no FK: entries outlive deleted accounts"),
        sa.Column("actor_ip", sa.Text()),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("target_type", sa.Text()),
        sa.Column("target_id", sa.Text()),
        sa.Column("detail_json", sa.Text()),
        sa.Column("request_id", sa.Text()),
    )
    op.create_index("audit_log_at", "audit_log", ["at"])
    op.create_index("audit_log_actor", "audit_log", ["actor_user_id"])


def downgrade() -> None:
    for index, table in (
        ("audit_log_actor", "audit_log"),
        ("audit_log_at", "audit_log"),
        ("login_attempts_ip_at", "login_attempts"),
        ("login_attempts_email_at", "login_attempts"),
        ("api_tokens_user", "api_tokens"),
        ("sessions_auth_user", "sessions_auth"),
    ):
        op.drop_index(index, table_name=table)
    op.drop_table("audit_log")
    op.drop_table("login_attempts")
    op.drop_table("one_time_tokens")
    op.drop_table("api_tokens")
    op.drop_table("sessions_auth")
    op.drop_table("identities")
    op.drop_index("users_email_lower", table_name="users")
    op.drop_table("users")

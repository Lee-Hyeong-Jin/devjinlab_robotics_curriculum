"""Initial schema, equivalent to SQLite schema v1: lesson_progress, sessions, meta.

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "meta",
        sa.Column("key", sa.Text(), primary_key=True),
        sa.Column("value", sa.Text(), nullable=False),
    )
    op.create_table(
        "lesson_progress",
        sa.Column("user_id", sa.Integer(), primary_key=True, server_default=sa.text("1")),
        sa.Column("lesson_id", sa.Text(), primary_key=True),
        sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'not_started'")),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("total_seconds", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("understanding", sa.Integer()),
        sa.Column("note", sa.Text()),
        sa.CheckConstraint(
            "status IN ('not_started', 'in_progress', 'done')", name="lesson_progress_status"
        ),
        sa.CheckConstraint("total_seconds >= 0", name="lesson_progress_total_seconds"),
        sa.CheckConstraint("understanding BETWEEN 1 AND 5", name="lesson_progress_understanding"),
    )
    op.create_table(
        "sessions",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("lesson_id", sa.Text(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("note", sa.Text()),
        sa.Column("source", sa.Text(), nullable=False, server_default=sa.text("'timer'")),
        sa.CheckConstraint("source IN ('timer', 'manual')", name="sessions_source"),
    )
    op.create_index("sessions_user_lesson", "sessions", ["user_id", "lesson_id"])
    op.create_index(
        "sessions_one_open",
        "sessions",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("ended_at IS NULL"),
    )
    op.execute("INSERT INTO meta (key, value) VALUES ('schema_version', '1')")


def downgrade() -> None:
    op.drop_index("sessions_one_open", table_name="sessions")
    op.drop_index("sessions_user_lesson", table_name="sessions")
    op.drop_table("sessions")
    op.drop_table("lesson_progress")
    op.drop_table("meta")

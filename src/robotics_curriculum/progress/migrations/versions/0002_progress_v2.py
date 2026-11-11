"""Progress schema v2: cards, SM-2 card_state, reviews, quiz_attempts, quiz_runs, activity_progress.

Equivalent to SQLite ``MIGRATIONS[2]`` in ``progress/store.py`` (P1-2). PostgreSQL uses
native types: TIMESTAMPTZ for timestamps, DATE for ``card_state.due``, BOOLEAN for the 0/1
integer flags, DOUBLE PRECISION for ``ease``, BIGINT IDENTITY for generated ids.

Revision ID: 0002_progress_v2
Revises: 0001_initial
Create Date: 2026-11-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_progress_v2"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cards",
        sa.Column("user_id", sa.Integer(), primary_key=True, server_default=sa.text("1")),
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("lesson_id", sa.Text(), nullable=False),
        sa.Column("question_id", sa.Text(), nullable=False),
        sa.Column("front", sa.Text(), nullable=False),
        sa.Column("back", sa.Text(), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("suspended", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.CheckConstraint("source IN ('quiz', 'concept')", name="cards_source"),
    )
    op.create_index("cards_user_lesson", "cards", ["user_id", "lesson_id"])

    op.create_table(
        "card_state",
        sa.Column("user_id", sa.Integer(), primary_key=True, server_default=sa.text("1")),
        sa.Column("card_id", sa.Text(), primary_key=True),
        sa.Column("repetitions", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("interval_days", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("ease", sa.Float(), nullable=False, server_default=sa.text("2.5")),
        sa.Column("due", sa.Date(), nullable=False),
        sa.CheckConstraint("repetitions >= 0", name="card_state_repetitions"),
        sa.CheckConstraint("interval_days >= 0", name="card_state_interval_days"),
    )
    op.create_index("card_state_user_due", "card_state", ["user_id", "due"])

    op.create_table(
        "reviews",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("card_id", sa.Text(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("rating", sa.Text(), nullable=False),
        sa.Column("interval_before", sa.Integer(), nullable=False),
        sa.Column("interval_after", sa.Integer(), nullable=False),
        sa.Column("ease_after", sa.Float(), nullable=False),
        sa.CheckConstraint("rating IN ('again', 'hard', 'good', 'easy')", name="reviews_rating"),
    )
    op.create_index("reviews_user_card", "reviews", ["user_id", "card_id"])

    op.create_table(
        "quiz_attempts",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("lesson_id", sa.Text(), nullable=False),
        sa.Column("question_id", sa.Text(), nullable=False),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("correct", sa.Boolean(), nullable=False),
    )
    op.create_index("quiz_attempts_user_lesson", "quiz_attempts", ["user_id", "lesson_id"])

    op.create_table(
        "quiz_runs",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("lesson_id", sa.Text(), nullable=False),
        sa.Column("activity_id", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("correct", sa.Integer(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
    )
    op.create_index("quiz_runs_user_lesson", "quiz_runs", ["user_id", "lesson_id"])

    op.create_table(
        "activity_progress",
        sa.Column("user_id", sa.Integer(), primary_key=True, server_default=sa.text("1")),
        sa.Column("activity_id", sa.Text(), primary_key=True),
        sa.Column("lesson_id", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'not_started'")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('not_started', 'in_progress', 'done')", name="activity_progress_status"
        ),
    )

    op.execute("UPDATE meta SET value = '2' WHERE key = 'schema_version'")


def downgrade() -> None:
    op.drop_table("activity_progress")
    op.drop_index("quiz_runs_user_lesson", table_name="quiz_runs")
    op.drop_table("quiz_runs")
    op.drop_index("quiz_attempts_user_lesson", table_name="quiz_attempts")
    op.drop_table("quiz_attempts")
    op.drop_index("reviews_user_card", table_name="reviews")
    op.drop_table("reviews")
    op.drop_index("card_state_user_due", table_name="card_state")
    op.drop_table("card_state")
    op.drop_index("cards_user_lesson", table_name="cards")
    op.drop_table("cards")
    op.execute("UPDATE meta SET value = '1' WHERE key = 'schema_version'")

"""SQLAlchemy Core table definitions for the PostgreSQL progress store.

Single source of the server-mode schema: :mod:`progress.postgres` queries these tables and
Alembic (``progress/migrations``) compares them against the database (autogenerate check in
the tests). Equivalent to SQLite schema v1 in ``progress/store.py``; PostgreSQL gets native
types (``TIMESTAMPTZ`` for timestamps, ``BIGINT IDENTITY`` for session ids).
"""

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    Identity,
    Index,
    Integer,
    MetaData,
    Table,
    Text,
    text,
)

metadata = MetaData()

meta_table = Table(
    "meta",
    metadata,
    Column("key", Text, primary_key=True),
    Column("value", Text, nullable=False),
)

lesson_progress = Table(
    "lesson_progress",
    metadata,
    Column("user_id", Integer, primary_key=True, server_default=text("1")),
    Column("lesson_id", Text, primary_key=True),
    Column("status", Text, nullable=False, server_default=text("'not_started'")),
    Column("started_at", DateTime(timezone=True)),
    Column("completed_at", DateTime(timezone=True)),
    Column("total_seconds", Integer, nullable=False, server_default=text("0")),
    Column("understanding", Integer),
    Column("note", Text),
    CheckConstraint(
        "status IN ('not_started', 'in_progress', 'done')", name="lesson_progress_status"
    ),
    CheckConstraint("total_seconds >= 0", name="lesson_progress_total_seconds"),
    CheckConstraint("understanding BETWEEN 1 AND 5", name="lesson_progress_understanding"),
)

sessions = Table(
    "sessions",
    metadata,
    Column("id", BigInteger, Identity(always=False), primary_key=True),
    Column("user_id", Integer, nullable=False, server_default=text("1")),
    Column("lesson_id", Text, nullable=False),
    Column("started_at", DateTime(timezone=True), nullable=False),
    Column("ended_at", DateTime(timezone=True)),
    Column("note", Text),
    Column("source", Text, nullable=False, server_default=text("'timer'")),
    CheckConstraint("source IN ('timer', 'manual')", name="sessions_source"),
    Index("sessions_user_lesson", "user_id", "lesson_id"),
    # at most one running timer per user
    Index(
        "sessions_one_open",
        "user_id",
        unique=True,
        postgresql_where=text("ended_at IS NULL"),
    ),
)


# -- schema v2: cards, SM-2 state, reviews, quiz records (P1-2) ---------------------------------

cards = Table(
    "cards",
    metadata,
    Column("user_id", Integer, primary_key=True, server_default=text("1")),
    Column("id", Text, primary_key=True),
    Column("lesson_id", Text, nullable=False),
    Column("question_id", Text, nullable=False),
    Column("front", Text, nullable=False),
    Column("back", Text, nullable=False),
    Column("source", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("suspended", Boolean, nullable=False, server_default=text("false")),
    CheckConstraint("source IN ('quiz', 'concept')", name="cards_source"),
    Index("cards_user_lesson", "user_id", "lesson_id"),
)

card_state = Table(
    "card_state",
    metadata,
    Column("user_id", Integer, primary_key=True, server_default=text("1")),
    Column("card_id", Text, primary_key=True),
    Column("repetitions", Integer, nullable=False, server_default=text("0")),
    Column("interval_days", Integer, nullable=False, server_default=text("0")),
    Column("ease", Float, nullable=False, server_default=text("2.5")),
    Column("due", Date, nullable=False),
    CheckConstraint("repetitions >= 0", name="card_state_repetitions"),
    CheckConstraint("interval_days >= 0", name="card_state_interval_days"),
    Index("card_state_user_due", "user_id", "due"),
)

reviews = Table(
    "reviews",
    metadata,
    Column("id", BigInteger, Identity(always=False), primary_key=True),
    Column("user_id", Integer, nullable=False, server_default=text("1")),
    Column("card_id", Text, nullable=False),
    Column("reviewed_at", DateTime(timezone=True), nullable=False),
    Column("rating", Text, nullable=False),
    Column("interval_before", Integer, nullable=False),
    Column("interval_after", Integer, nullable=False),
    Column("ease_after", Float, nullable=False),
    CheckConstraint("rating IN ('again', 'hard', 'good', 'easy')", name="reviews_rating"),
    Index("reviews_user_card", "user_id", "card_id"),
)

quiz_attempts = Table(
    "quiz_attempts",
    metadata,
    Column("id", BigInteger, Identity(always=False), primary_key=True),
    Column("user_id", Integer, nullable=False, server_default=text("1")),
    Column("lesson_id", Text, nullable=False),
    Column("question_id", Text, nullable=False),
    Column("answered_at", DateTime(timezone=True), nullable=False),
    Column("answer", Text, nullable=False),
    Column("correct", Boolean, nullable=False),
    Index("quiz_attempts_user_lesson", "user_id", "lesson_id"),
)

quiz_runs = Table(
    "quiz_runs",
    metadata,
    Column("id", BigInteger, Identity(always=False), primary_key=True),
    Column("user_id", Integer, nullable=False, server_default=text("1")),
    Column("lesson_id", Text, nullable=False),
    Column("activity_id", Text),
    Column("started_at", DateTime(timezone=True), nullable=False),
    Column("finished_at", DateTime(timezone=True), nullable=False),
    Column("correct", Integer, nullable=False),
    Column("total", Integer, nullable=False),
    Index("quiz_runs_user_lesson", "user_id", "lesson_id"),
)

activity_progress = Table(
    "activity_progress",
    metadata,
    Column("user_id", Integer, primary_key=True, server_default=text("1")),
    Column("activity_id", Text, primary_key=True),
    Column("lesson_id", Text, nullable=False),
    Column("status", Text, nullable=False, server_default=text("'not_started'")),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    CheckConstraint(
        "status IN ('not_started', 'in_progress', 'done')", name="activity_progress_status"
    ),
)

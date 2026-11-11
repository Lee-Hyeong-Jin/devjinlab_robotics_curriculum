"""SQLAlchemy Core table definitions for the PostgreSQL progress store.

Single source of the server-mode schema: :mod:`progress.postgres` queries these tables and
Alembic (``progress/migrations``) compares them against the database (autogenerate check in
the tests). Equivalent to SQLite schema v1 in ``progress/store.py``; PostgreSQL gets native
types (``TIMESTAMPTZ`` for timestamps, ``BIGINT IDENTITY`` for session ids).
"""

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
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

"""Monitoring tables as SQLAlchemy Core (the source for Alembic revision 0004).

Server mode only, in the same database as the auth tables. What each table may and may not
hold is decided in ADR 0017: no query strings, no request bodies, no IP addresses, no user
agents.
"""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Index,
    Integer,
    MetaData,
    SmallInteger,
    Table,
    Text,
)

from robotics_curriculum.ops.traffic import BUCKET_COUNT

ops_metadata = MetaData()

# BigInteger primary keys become INTEGER on SQLite so they still autoincrement.
BigId = BigInteger().with_variant(Integer(), "sqlite")

HISTOGRAM_COLUMNS = tuple(f"h{index}" for index in range(BUCKET_COUNT))
"""One counter per latency bucket (``traffic.LATENCY_BOUNDS_MS`` plus overflow). Columns, not
JSON, so a flush can add to them with a plain ``SET h0 = h0 + :n`` on both backends."""

request_stats = Table(
    "ops_request_stats",
    ops_metadata,
    Column("bucket", DateTime(timezone=True), primary_key=True, comment="start of the UTC hour"),
    Column("route", Text, primary_key=True, comment="route template, never the raw path"),
    Column("method", Text, primary_key=True),
    Column("status_class", SmallInteger, primary_key=True, comment="2, 3, 4 or 5"),
    Column("count", BigInteger, nullable=False),
    Column("duration_ms_sum", Float, nullable=False),
    Column("duration_ms_max", Float, nullable=False),
    *(Column(name, BigInteger, nullable=False) for name in HISTOGRAM_COLUMNS),
)

request_errors = Table(
    "ops_request_errors",
    ops_metadata,
    Column("id", BigId, primary_key=True, autoincrement=True),
    Column("at", DateTime(timezone=True), nullable=False),
    Column("method", Text, nullable=False),
    Column("route", Text, nullable=False),
    Column("path", Text, nullable=False, comment="without the query string"),
    Column("status", SmallInteger, nullable=False),
    Column("duration_ms", Float, nullable=False),
    Column("request_id", Text),
    Column("user_id", Integer, comment="no FK: erased with the account by the application"),
    Column("error_type", Text),
    Column("error_message", Text),
    Index("ops_request_errors_at", "at"),
)

page_views = Table(
    "ops_page_views",
    ops_metadata,
    Column("day", Date, primary_key=True, comment="day in the service time zone (RC_TIMEZONE)"),
    Column("path", Text, primary_key=True, comment="normalized; unknown paths are '(other)'"),
    Column("locale", Text, primary_key=True),
    Column("bot", Boolean, primary_key=True),
    Column("signed_in", Boolean, primary_key=True),
    Column("count", BigInteger, nullable=False),
)

visitors = Table(
    "ops_visitors",
    ops_metadata,
    Column("day", Date, primary_key=True, comment="day in the service time zone (RC_TIMEZONE)"),
    Column("visitor", Text, primary_key=True, comment="daily-salted hash, see ADR 0017"),
    Column("signed_in", Boolean, nullable=False),
)

referrers = Table(
    "ops_referrers",
    ops_metadata,
    Column("day", Date, primary_key=True, comment="day in the service time zone (RC_TIMEZONE)"),
    Column("host", Text, primary_key=True, comment="host only, never the full URL"),
    Column("count", BigInteger, nullable=False),
)

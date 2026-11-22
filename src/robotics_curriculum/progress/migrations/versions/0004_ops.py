"""Monitoring tables: ops_request_stats, ops_request_errors, ops_page_views, ops_visitors,
ops_referrers (P3-2, ADR 0017).

Mirrors ``robotics_curriculum.ops.schema`` (a drift test compares the two). Server mode only:
SQLite deployments create these tables from the metadata when the store opens.

None of these tables holds an IP address, a user agent, a query string or a request body.

Revision ID: 0004_ops
Revises: 0003_auth
Create Date: 2026-11-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_ops"
down_revision: str | None = "0003_auth"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

HISTOGRAM_BUCKETS = 12
"""Latency buckets at the time of this revision (11 edges plus overflow)."""


def upgrade() -> None:
    op.create_table(
        "ops_request_stats",
        sa.Column(
            "bucket",
            sa.DateTime(timezone=True),
            primary_key=True,
            comment="start of the UTC hour",
        ),
        sa.Column(
            "route", sa.Text(), primary_key=True, comment="route template, never the raw path"
        ),
        sa.Column("method", sa.Text(), primary_key=True),
        sa.Column("status_class", sa.SmallInteger(), primary_key=True, comment="2, 3, 4 or 5"),
        sa.Column("count", sa.BigInteger(), nullable=False),
        sa.Column("duration_ms_sum", sa.Float(), nullable=False),
        sa.Column("duration_ms_max", sa.Float(), nullable=False),
        *(
            sa.Column(f"h{index}", sa.BigInteger(), nullable=False)
            for index in range(HISTOGRAM_BUCKETS)
        ),
    )
    op.create_table(
        "ops_request_errors",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("method", sa.Text(), nullable=False),
        sa.Column("route", sa.Text(), nullable=False),
        sa.Column("path", sa.Text(), nullable=False, comment="without the query string"),
        sa.Column("status", sa.SmallInteger(), nullable=False),
        sa.Column("duration_ms", sa.Float(), nullable=False),
        sa.Column("request_id", sa.Text()),
        sa.Column(
            "user_id",
            sa.Integer(),
            comment="no FK: erased with the account by the application",
        ),
        sa.Column("error_type", sa.Text()),
        sa.Column("error_message", sa.Text()),
    )
    op.create_index("ops_request_errors_at", "ops_request_errors", ["at"])
    op.create_table(
        "ops_page_views",
        sa.Column("day", sa.Date(), primary_key=True, comment="UTC day"),
        sa.Column(
            "path",
            sa.Text(),
            primary_key=True,
            comment="normalized; unknown paths are '(other)'",
        ),
        sa.Column("locale", sa.Text(), primary_key=True),
        sa.Column("bot", sa.Boolean(), primary_key=True),
        sa.Column("signed_in", sa.Boolean(), primary_key=True),
        sa.Column("count", sa.BigInteger(), nullable=False),
    )
    op.create_table(
        "ops_visitors",
        sa.Column("day", sa.Date(), primary_key=True),
        sa.Column(
            "visitor", sa.Text(), primary_key=True, comment="daily-salted hash, see ADR 0017"
        ),
        sa.Column("signed_in", sa.Boolean(), nullable=False),
    )
    op.create_table(
        "ops_referrers",
        sa.Column("day", sa.Date(), primary_key=True),
        sa.Column("host", sa.Text(), primary_key=True, comment="host only, never the full URL"),
        sa.Column("count", sa.BigInteger(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("ops_referrers")
    op.drop_table("ops_visitors")
    op.drop_table("ops_page_views")
    op.drop_index("ops_request_errors_at", table_name="ops_request_errors")
    op.drop_table("ops_request_errors")
    op.drop_table("ops_request_stats")

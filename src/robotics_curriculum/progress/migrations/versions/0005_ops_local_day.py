"""Monitoring days are days in the service time zone, not UTC days (RC_TIMEZONE).

Only the column comments change: the ``day`` columns of ops_page_views, ops_visitors and
ops_referrers are now filled with the day in the service's zone (Korea Standard Time by
default). Rows written before this revision keep the UTC day they were counted under; they
are aggregates and cannot be re-cut, so the first day or two of data can be off by up to nine
hours at the day boundary.

Revision ID: 0005_ops_local_day
Revises: 0004_ops
Create Date: 2026-11-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_ops_local_day"
down_revision: str | None = "0004_ops"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

LOCAL_DAY = "day in the service time zone (RC_TIMEZONE)"
TABLES = {"ops_page_views": "UTC day", "ops_visitors": None, "ops_referrers": None}
"""Table -> the comment its ``day`` column had before this revision."""


def upgrade() -> None:
    for table, previous in TABLES.items():
        op.alter_column(
            table,
            "day",
            existing_type=sa.Date(),
            existing_nullable=False,
            comment=LOCAL_DAY,
            existing_comment=previous,
        )


def downgrade() -> None:
    for table, previous in TABLES.items():
        op.alter_column(
            table,
            "day",
            existing_type=sa.Date(),
            existing_nullable=False,
            comment=previous,
            existing_comment=LOCAL_DAY,
        )

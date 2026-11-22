"""Persistence of the monitoring data over a SQLAlchemy engine (SQLite or PostgreSQL)."""

from __future__ import annotations

import time
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from sqlalchemy import Connection, Engine, delete, func, or_, select, text
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.engine import RowMapping

from robotics_curriculum.ops.schema import (
    HISTOGRAM_COLUMNS,
    ops_metadata,
    page_views,
    referrers,
    request_errors,
    request_stats,
    visitors,
)

StatKey = tuple[datetime, str, str, int]
"""(hour bucket, route template, method, status class)."""


@dataclass(slots=True)
class StatDelta:
    """What one buffer flush adds to a row of ``ops_request_stats``."""

    count: int
    duration_ms_sum: float
    duration_ms_max: float
    histogram: list[int]


@dataclass(frozen=True, slots=True)
class RequestError:
    id: int
    at: datetime
    method: str
    route: str
    path: str
    status: int
    duration_ms: float
    request_id: str | None
    user_id: int | None
    error_type: str | None
    error_message: str | None


@dataclass(frozen=True, slots=True)
class StatRow:
    bucket: datetime
    route: str
    method: str
    status_class: int
    count: int
    duration_ms_sum: float
    duration_ms_max: float
    histogram: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class DayVisits:
    day: date
    views: int
    bot_views: int
    signed_in_views: int
    visitors: int
    signed_in_visitors: int


def _aware(value: datetime) -> datetime:
    from datetime import UTC

    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


class OpsStore:
    """Reads and writes the ``ops_*`` tables."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        if engine.dialect.name == "sqlite":
            # SQLite deployments have no migration step; PostgreSQL gets Alembic 0004.
            ops_metadata.create_all(engine)

    @contextmanager
    def _tx(self) -> Iterator[Connection]:
        with self.engine.begin() as conn:
            yield conn

    def _insert(self, table: Any) -> Any:
        """An ``INSERT`` that supports ``ON CONFLICT`` on the engine's backend."""
        if self.engine.dialect.name == "postgresql":
            return postgresql.insert(table)
        return sqlite.insert(table)

    # -- writes ----------------------------------------------------------------------------

    def add_request_stats(self, deltas: Mapping[StatKey, StatDelta]) -> None:
        """Add buffered counts to their hour rows, creating the rows that do not exist."""
        if not deltas:
            return
        with self._tx() as conn:
            for (bucket, route, method, klass), delta in deltas.items():
                values: dict[str, Any] = {
                    "bucket": bucket,
                    "route": route,
                    "method": method,
                    "status_class": klass,
                    "count": delta.count,
                    "duration_ms_sum": delta.duration_ms_sum,
                    "duration_ms_max": delta.duration_ms_max,
                }
                values.update(dict(zip(HISTOGRAM_COLUMNS, delta.histogram, strict=True)))
                stmt = self._insert(request_stats).values(**values)
                excluded = stmt.excluded
                update: dict[str, Any] = {
                    "count": request_stats.c.count + excluded.count,
                    "duration_ms_sum": request_stats.c.duration_ms_sum + excluded.duration_ms_sum,
                    "duration_ms_max": func.max(
                        request_stats.c.duration_ms_max, excluded.duration_ms_max
                    )
                    if self.engine.dialect.name == "sqlite"
                    else func.greatest(request_stats.c.duration_ms_max, excluded.duration_ms_max),
                }
                for name in HISTOGRAM_COLUMNS:
                    update[name] = request_stats.c[name] + excluded[name]
                conn.execute(
                    stmt.on_conflict_do_update(
                        index_elements=["bucket", "route", "method", "status_class"], set_=update
                    )
                )

    def add_request_error(
        self,
        *,
        at: datetime,
        method: str,
        route: str,
        path: str,
        status: int,
        duration_ms: float,
        request_id: str | None,
        user_id: int | None,
        error_type: str | None,
        error_message: str | None,
    ) -> None:
        with self._tx() as conn:
            conn.execute(
                request_errors.insert().values(
                    at=at,
                    method=method,
                    route=route,
                    path=path,
                    status=status,
                    duration_ms=duration_ms,
                    request_id=request_id,
                    user_id=user_id,
                    error_type=error_type,
                    error_message=error_message,
                )
            )

    def add_page_view(
        self,
        *,
        day: date,
        path: str,
        locale: str,
        bot: bool,
        signed_in: bool,
        visitor: str | None,
        referrer: str | None,
    ) -> None:
        """Count one visit. ``visitor`` is ``None`` for automated clients, which are not people."""
        with self._tx() as conn:
            view = self._insert(page_views).values(
                day=day, path=path, locale=locale, bot=bot, signed_in=signed_in, count=1
            )
            conn.execute(
                view.on_conflict_do_update(
                    index_elements=["day", "path", "locale", "bot", "signed_in"],
                    set_={"count": page_views.c.count + 1},
                )
            )
            if visitor is not None:
                seen = self._insert(visitors).values(day=day, visitor=visitor, signed_in=signed_in)
                # A visitor who signs in later in the day counts as signed in for that day.
                conn.execute(
                    seen.on_conflict_do_update(
                        index_elements=["day", "visitor"],
                        set_={"signed_in": or_(visitors.c.signed_in, seen.excluded.signed_in)},
                    )
                )
            if referrer is not None:
                ref = self._insert(referrers).values(day=day, host=referrer, count=1)
                conn.execute(
                    ref.on_conflict_do_update(
                        index_elements=["day", "host"], set_={"count": referrers.c.count + 1}
                    )
                )

    def purge(
        self,
        *,
        stats_before: datetime,
        errors_before: datetime,
        errors_keep: int,
        views_before: date,
        visitors_before: date,
    ) -> dict[str, int]:
        """Delete what is past its retention. Returns rows removed per table."""
        removed: dict[str, int] = {}
        with self._tx() as conn:
            removed["request_stats"] = conn.execute(
                delete(request_stats).where(request_stats.c.bucket < stats_before)
            ).rowcount
            removed["request_errors"] = conn.execute(
                delete(request_errors).where(request_errors.c.at < errors_before)
            ).rowcount
            # Also cap the count: a crash loop must not fill the disk it is reported on.
            cutoff = conn.execute(
                select(request_errors.c.id)
                .order_by(request_errors.c.id.desc())
                .offset(errors_keep)
                .limit(1)
            ).scalar_one_or_none()
            if cutoff is not None:
                removed["request_errors"] += conn.execute(
                    delete(request_errors).where(request_errors.c.id <= cutoff)
                ).rowcount
            removed["page_views"] = conn.execute(
                delete(page_views).where(page_views.c.day < views_before)
            ).rowcount
            removed["referrers"] = conn.execute(
                delete(referrers).where(referrers.c.day < views_before)
            ).rowcount
            removed["visitors"] = conn.execute(
                delete(visitors).where(visitors.c.day < visitors_before)
            ).rowcount
        return removed

    def erase_user(self, user_id: int) -> int:
        """Detach a deleted account from the failed-request log (the rows stay, anonymous)."""
        with self._tx() as conn:
            return conn.execute(
                request_errors.update()
                .where(request_errors.c.user_id == user_id)
                .values(user_id=None)
            ).rowcount

    # -- reads -----------------------------------------------------------------------------

    @staticmethod
    def _stat(row: RowMapping) -> StatRow:
        return StatRow(
            bucket=_aware(row["bucket"]),
            route=row["route"],
            method=row["method"],
            status_class=int(row["status_class"]),
            count=int(row["count"]),
            duration_ms_sum=float(row["duration_ms_sum"]),
            duration_ms_max=float(row["duration_ms_max"]),
            histogram=tuple(int(row[name]) for name in HISTOGRAM_COLUMNS),
        )

    def request_stats(self, since: datetime, until: datetime) -> list[StatRow]:
        """Hour rows with ``since <= bucket < until``, oldest first."""
        with self._tx() as conn:
            rows = (
                conn.execute(
                    select(request_stats)
                    .where(request_stats.c.bucket >= since, request_stats.c.bucket < until)
                    .order_by(request_stats.c.bucket)
                )
                .mappings()
                .all()
            )
        return [self._stat(row) for row in rows]

    def request_errors(
        self,
        limit: int,
        before_id: int | None = None,
        *,
        status: int | None = None,
        route: str | None = None,
        since: datetime | None = None,
    ) -> list[RequestError]:
        """Failed requests, newest first."""
        query = select(request_errors).order_by(request_errors.c.id.desc()).limit(limit)
        if before_id is not None:
            query = query.where(request_errors.c.id < before_id)
        if status is not None:
            query = query.where(request_errors.c.status == status)
        if route:
            query = query.where(request_errors.c.route == route)
        if since is not None:
            query = query.where(request_errors.c.at >= since)
        with self._tx() as conn:
            rows = conn.execute(query).mappings().all()
        return [
            RequestError(
                id=int(r["id"]),
                at=_aware(r["at"]),
                method=r["method"],
                route=r["route"],
                path=r["path"],
                status=int(r["status"]),
                duration_ms=float(r["duration_ms"]),
                request_id=r["request_id"],
                user_id=r["user_id"],
                error_type=r["error_type"],
                error_message=r["error_message"],
            )
            for r in rows
        ]

    def count_request_errors(self, since: datetime) -> int:
        with self._tx() as conn:
            return int(
                conn.execute(
                    select(func.count())
                    .select_from(request_errors)
                    .where(request_errors.c.at >= since)
                ).scalar_one()
            )

    def daily_visits(self, since: date, until: date) -> list[DayVisits]:
        """Views and visitors per day for ``since <= day <= until`` (days with data only)."""
        with self._tx() as conn:
            views = conn.execute(
                select(
                    page_views.c.day,
                    page_views.c.bot,
                    page_views.c.signed_in,
                    func.sum(page_views.c.count),
                )
                .where(page_views.c.day >= since, page_views.c.day <= until)
                .group_by(page_views.c.day, page_views.c.bot, page_views.c.signed_in)
            ).all()
            people = conn.execute(
                select(visitors.c.day, visitors.c.signed_in, func.count())
                .where(visitors.c.day >= since, visitors.c.day <= until)
                .group_by(visitors.c.day, visitors.c.signed_in)
            ).all()
        days: dict[date, dict[str, int]] = {}
        for day, bot, signed_in, count in views:
            entry = days.setdefault(day, {})
            key = "bot_views" if bot else "views"
            entry[key] = entry.get(key, 0) + int(count)
            if signed_in and not bot:
                entry["signed_in_views"] = entry.get("signed_in_views", 0) + int(count)
        for day, signed_in, count in people:
            entry = days.setdefault(day, {})
            entry["visitors"] = entry.get("visitors", 0) + int(count)
            if signed_in:
                entry["signed_in_visitors"] = entry.get("signed_in_visitors", 0) + int(count)
        return [
            DayVisits(
                day=day,
                views=entry.get("views", 0),
                bot_views=entry.get("bot_views", 0),
                signed_in_views=entry.get("signed_in_views", 0),
                visitors=entry.get("visitors", 0),
                signed_in_visitors=entry.get("signed_in_visitors", 0),
            )
            for day, entry in sorted(days.items())
        ]

    def top_pages(self, since: date, until: date, limit: int) -> list[tuple[str, int]]:
        """Most viewed pages by people (automated clients excluded)."""
        total = func.sum(page_views.c.count)
        with self._tx() as conn:
            rows = conn.execute(
                select(page_views.c.path, total)
                .where(
                    page_views.c.day >= since,
                    page_views.c.day <= until,
                    page_views.c.bot.is_(False),
                )
                .group_by(page_views.c.path)
                .order_by(total.desc(), page_views.c.path)
                .limit(limit)
            ).all()
        return [(str(path), int(count)) for path, count in rows]

    def views_by_locale(self, since: date, until: date) -> dict[str, int]:
        total = func.sum(page_views.c.count)
        with self._tx() as conn:
            rows = conn.execute(
                select(page_views.c.locale, total)
                .where(
                    page_views.c.day >= since,
                    page_views.c.day <= until,
                    page_views.c.bot.is_(False),
                )
                .group_by(page_views.c.locale)
            ).all()
        return {str(locale): int(count) for locale, count in rows}

    def top_referrers(self, since: date, until: date, limit: int) -> list[tuple[str, int]]:
        total = func.sum(referrers.c.count)
        with self._tx() as conn:
            rows = conn.execute(
                select(referrers.c.host, total)
                .where(referrers.c.day >= since, referrers.c.day <= until)
                .group_by(referrers.c.host)
                .order_by(total.desc(), referrers.c.host)
                .limit(limit)
            ).all()
        return [(str(host), int(count)) for host, count in rows]

    # -- database health -------------------------------------------------------------------

    def database_size_bytes(self) -> int | None:
        """Size of the database on disk, or ``None`` when the backend cannot say."""
        try:
            with self._tx() as conn:
                if self.engine.dialect.name == "postgresql":
                    value = conn.execute(
                        text("SELECT pg_database_size(current_database())")
                    ).scalar()
                else:
                    pages = conn.execute(text("PRAGMA page_count")).scalar()
                    size = conn.execute(text("PRAGMA page_size")).scalar()
                    value = int(pages or 0) * int(size or 0)
        except Exception:  # noqa: BLE001 - a monitoring read must never raise into the page
            return None
        return int(value) if value is not None else None

    def connections(self) -> tuple[int, int] | None:
        """(connections in use, maximum) on PostgreSQL; ``None`` elsewhere or when unreadable."""
        if self.engine.dialect.name != "postgresql":
            return None
        try:
            with self._tx() as conn:
                used = conn.execute(
                    text("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()")
                ).scalar()
                limit = conn.execute(text("SHOW max_connections")).scalar()
        except Exception:  # noqa: BLE001 - a monitoring read must never raise into the page
            return None
        try:
            return int(used or 0), int(limit or 0)
        except (TypeError, ValueError):
            return None

    def ping_ms(self) -> float | None:
        """Round-trip time of ``SELECT 1``, or ``None`` when the database does not answer."""
        begin = time.perf_counter()
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception:  # noqa: BLE001 - "the database is down" is the reading
            return None
        return (time.perf_counter() - begin) * 1000

    def table_rows(self) -> dict[str, int]:
        """Row counts of the monitoring tables (how much the monitoring itself stores)."""
        out: dict[str, int] = {}
        with self._tx() as conn:
            for table in (request_stats, request_errors, page_views, visitors, referrers):
                out[table.name] = int(
                    conn.execute(select(func.count()).select_from(table)).scalar_one()
                )
        return out


def top_routes(rows: Sequence[StatRow]) -> dict[tuple[str, str], list[StatRow]]:
    """Group hour rows by (method, route)."""
    grouped: dict[tuple[str, str], list[StatRow]] = {}
    for row in rows:
        grouped.setdefault((row.method, row.route), []).append(row)
    return grouped

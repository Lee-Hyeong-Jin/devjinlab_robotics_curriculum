"""``/api/v1/admin/monitoring``: service health and KPIs for operators (admin only, ADR 0017).

Four reads: the machine (``/system``), API traffic and latency (``/traffic``), the requests
that failed (``/errors``) and visits (``/visits``). Everything is aggregated before it is
stored, and nothing here returns an address, a user agent, a query string or a request body.
"""

from __future__ import annotations

from datetime import UTC, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from robotics_curriculum import __version__
from robotics_curriculum.api.deps import (
    AdminPrincipal,
    Auth,
    Ctx,
    State,
    open_progress_store,
    require_admin,
)
from robotics_curriculum.api.ops_schemas import (
    ActiveUsers,
    Alert,
    Cohorts,
    CpuReading,
    DatabaseReading,
    DiskReading,
    ErrorBudget,
    FailedRequest,
    FailedRequestPage,
    Growth,
    Kpis,
    LearningWindow,
    Level,
    MemoryReading,
    PageCount,
    ProcessReading,
    ReferrerCount,
    RouteStats,
    SystemStatus,
    TemperatureReading,
    Traffic,
    TrafficBucket,
    TrafficRange,
    TrafficTotals,
    VisitDay,
    VisitRange,
    Visits,
    VisitTotals,
)
from robotics_curriculum.api.problems import problem_responses
from robotics_curriculum.learn.platform import LearningKpis, activated, learning_kpis
from robotics_curriculum.ops import system
from robotics_curriculum.ops.recorder import Recorder
from robotics_curriculum.ops.store import StatRow
from robotics_curriculum.ops.traffic import (
    AVAILABILITY_TARGET,
    THRESHOLDS,
    RequestTotals,
    error_budget,
    hour_bucket,
    level,
)
from robotics_curriculum.timezone import day_start

router = APIRouter(
    prefix="/api/v1/admin/monitoring",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
    responses=problem_responses(401, 403, 404, 422),
)

TOP_ROUTES = 10
SLOWEST_MIN_REQUESTS = 5
"""A route needs this many requests in the range before its p95 is worth ranking."""


def get_recorder(state: State) -> Recorder:
    """The monitoring recorder; 404 where there is none (local mode, ``RC_OPS_METRICS=0``)."""
    if state.ops is None:
        raise HTTPException(404, "monitoring is not enabled on this server")
    return state.ops


Ops = Annotated[Recorder, Depends(get_recorder)]


def _typed(value: str) -> Level:
    assert value in ("ok", "warning", "critical")
    return value  # type: ignore[return-value]  # narrowed by the assert above


def _judge(key: str, value: float | None) -> Level:
    warning, critical = THRESHOLDS[key]
    return _typed(level(value, warning, critical))


def _alert(
    alerts: list[Alert],
    key: str,
    threshold_key: str,
    value: float | None,
    detail: str | None = None,
) -> Level:
    """Classify a reading and, when it is past a threshold, add it to ``alerts``."""
    verdict = _judge(threshold_key, value)
    if verdict != "ok" and value is not None:
        warning, critical = THRESHOLDS[threshold_key]
        alerts.append(
            Alert(
                key=key,
                level=verdict,
                value=value,
                threshold=critical if verdict == "critical" else warning,
                detail=detail,
            )
        )
    return verdict


# -- system --------------------------------------------------------------------------------


@router.get("/system", response_model=SystemStatus)
def system_status(
    request: Request, principal: AdminPrincipal, auth: Auth, ctx: Ctx, state: State, ops: Ops
) -> SystemStatus:
    """CPU, memory, disk, temperature, uptime and database readings, taken now.

    Read from the machine the API runs on. In a container the load, memory and temperature
    are the host's and the disk is the data volume. A reading the host does not expose is
    null or absent rather than a guess.
    """
    now = state.clock()
    alerts: list[Alert] = []

    load = system.read_loadavg()
    cpus = system.cpu_count()
    per_cpu = load[0] / cpus if load else None
    cpu = CpuReading(
        count=cpus,
        load_1m=load[0] if load else None,
        load_5m=load[1] if load else None,
        load_15m=load[2] if load else None,
        load_per_cpu=per_cpu,
        usage_ratio=state.cpu.usage(),
        level=_alert(alerts, "load", "load_per_cpu", per_cpu),
    )

    mem = system.read_memory()
    memory = (
        MemoryReading(
            total_bytes=mem.total_bytes,
            available_bytes=mem.available_bytes,
            used_ratio=mem.used_ratio,
            swap_total_bytes=mem.swap_total_bytes,
            swap_used_ratio=mem.swap_used_ratio,
            swap_level=_alert(alerts, "swap", "swap_used_ratio", mem.swap_used_ratio),
            process_rss_bytes=system.read_process_rss(),
            level=_alert(alerts, "memory", "memory_used_ratio", mem.used_ratio),
        )
        if mem
        else None
    )

    fds = system.read_file_descriptors()
    in_progress = None
    metrics = getattr(request.app.state, "metrics", None)
    gauge = getattr(metrics, "in_progress", None)
    if gauge is not None:
        # prometheus_client keeps the value on a private attribute; there is no public getter.
        in_progress = int(gauge._value.get())  # noqa: SLF001
    process = ProcessReading(
        open_files=fds.open if fds else None,
        open_files_limit=fds.limit if fds else None,
        open_files_ratio=fds.used_ratio if fds else None,
        open_files_level=_alert(
            alerts, "open_files", "fd_used_ratio", fds.used_ratio if fds else None
        ),
        requests_in_progress=in_progress,
    )

    disks: list[DiskReading] = []
    disk = system.read_disk(state.settings.data_dir)
    if disk is not None:
        disks.append(
            DiskReading(
                path=disk.path,
                total_bytes=disk.total_bytes,
                used_bytes=disk.used_bytes,
                free_bytes=disk.free_bytes,
                used_ratio=disk.used_ratio,
                level=_alert(alerts, "disk", "disk_used_ratio", disk.used_ratio, disk.path),
            )
        )

    temperatures = [
        TemperatureReading(
            sensor=reading.sensor,
            celsius=reading.celsius,
            level=_alert(alerts, "temperature", "temperature_c", reading.celsius, reading.sensor),
        )
        for reading in system.read_temperatures()
    ]

    ping = ops.store.ping_ms()
    pools: dict[str, dict[str, int]] = {}
    engine = ops.store.engine
    for name in ("checkedout", "size"):
        reader = getattr(engine.pool, name, None)
        if callable(reader):
            value = reader()
            if isinstance(value, int):
                pools.setdefault("main", {})["checked_out" if name == "checkedout" else name] = (
                    value
                )
    connections = ops.store.connections() if ping is not None else None
    connections_ratio = (
        connections[0] / connections[1] if connections and connections[1] > 0 else None
    )
    database = DatabaseReading(
        backend=engine.dialect.name,
        reachable=ping is not None,
        ping_ms=ping,
        size_bytes=ops.store.database_size_bytes(),
        connections=connections[0] if connections else None,
        connections_max=connections[1] if connections else None,
        connections_level=_alert(
            alerts, "db_connections", "db_connections_ratio", connections_ratio
        ),
        pool=pools,
        monitoring_rows=ops.store.table_rows() if ping is not None else {},
    )
    if ping is None:
        alerts.append(Alert(key="database", level="critical", value=0.0, threshold=0.0))

    auth.record(ctx, "admin.monitoring.viewed", principal.user.id, detail={"view": "system"})
    started = state.started_at or now
    return SystemStatus(
        generated_at=now,
        version=__version__,
        host_uptime_seconds=system.read_uptime(),
        process_uptime_seconds=max(0.0, (now - started).total_seconds()),
        cpu=cpu,
        memory=memory,
        process=process,
        disks=disks,
        temperatures=temperatures,
        database=database,
        alerts=alerts,
    )


# -- traffic -------------------------------------------------------------------------------

_RANGES: dict[str, tuple[timedelta, timedelta]] = {
    # range -> (how far back, bucket width of the series)
    "24h": (timedelta(hours=24), timedelta(hours=1)),
    "7d": (timedelta(days=7), timedelta(hours=6)),
    "30d": (timedelta(days=30), timedelta(days=1)),
}


def _totals(rows: list[StatRow]) -> RequestTotals:
    totals = RequestTotals()
    for row in rows:
        totals.add(
            row.status_class, row.count, row.duration_ms_sum, row.duration_ms_max, row.histogram
        )
    return totals


def _route_stats(method: str, route: str, rows: list[StatRow]) -> RouteStats:
    totals = _totals(rows)
    return RouteStats(
        method=method,
        route=route,
        requests=totals.count,
        client_errors=totals.client_errors,
        server_errors=totals.server_errors,
        mean_ms=totals.mean_ms,
        p95_ms=totals.quantile_ms(0.95),
        max_ms=totals.duration_ms_max if totals.count else None,
    )


@router.get("/traffic", response_model=Traffic)
def traffic(
    principal: AdminPrincipal,
    auth: Auth,
    ctx: Ctx,
    state: State,
    ops: Ops,
    range: TrafficRange = "24h",  # noqa: A002 - the query parameter is named `range`
) -> Traffic:
    """API requests over a period: volume, success rate, latency, and the routes behind them.

    The success rate is ``1 - 5xx / all``: a 4xx is the caller's mistake and is reported
    beside it, not counted against the service. Latency quantiles are estimated from a
    histogram, so they are accurate to its bucket edges.
    """
    ops.flush()
    now = state.clock()
    back, step = _RANGES[range]
    # Whole buckets, ending with the one in progress. Daily buckets are days in the service's
    # zone: "yesterday" on the chart is yesterday for the person reading it.
    end = hour_bucket(now) + timedelta(hours=1)
    if step >= timedelta(days=1):
        tomorrow = state.local_now().date() + timedelta(days=1)
        end = day_start(tomorrow, state.settings.timezone).astimezone(UTC)
    start = end - back
    rows = ops.store.request_stats(start, end)

    totals = _totals(rows)
    series: list[TrafficBucket] = []
    cursor = start
    index = 0
    while cursor < end:
        upper = cursor + step
        chunk: list[StatRow] = []
        while index < len(rows) and rows[index].bucket < upper:
            chunk.append(rows[index])
            index += 1
        part = _totals(chunk)
        series.append(
            TrafficBucket(
                start=cursor,
                requests=part.count,
                client_errors=part.client_errors,
                server_errors=part.server_errors,
                p50_ms=part.quantile_ms(0.5),
                p95_ms=part.quantile_ms(0.95),
            )
        )
        cursor = upper

    grouped: dict[tuple[str, str], list[StatRow]] = {}
    for row in rows:
        grouped.setdefault((row.method, row.route), []).append(row)
    routes = [_route_stats(method, route, group) for (method, route), group in grouped.items()]
    busiest = sorted(routes, key=lambda r: (-r.requests, r.route))[:TOP_ROUTES]
    slowest = sorted(
        (r for r in routes if r.requests >= SLOWEST_MIN_REQUESTS and r.p95_ms is not None),
        key=lambda r: (-(r.p95_ms or 0.0), r.route),
    )[:TOP_ROUTES]
    failing = sorted(
        (r for r in routes if r.server_errors > 0), key=lambda r: (-r.server_errors, r.route)
    )[:TOP_ROUTES]

    alerts: list[Alert] = []
    if totals.count:
        _alert(alerts, "errors", "server_error_ratio", totals.server_errors / totals.count)
        _alert(alerts, "latency", "p95_ms", totals.quantile_ms(0.95))
    budget = error_budget(totals.count, totals.server_errors, AVAILABILITY_TARGET)
    budget_level = _alert(alerts, "error_budget", "error_budget_consumed", budget.consumed_ratio)

    auth.record(
        ctx,
        "admin.monitoring.viewed",
        principal.user.id,
        detail={"view": "traffic", "range": range},
    )
    return Traffic(
        generated_at=now,
        range=range,
        since=start,
        bucket_seconds=int(step.total_seconds()),
        totals=TrafficTotals(
            requests=totals.count,
            succeeded=totals.count - totals.client_errors - totals.server_errors,
            client_errors=totals.client_errors,
            server_errors=totals.server_errors,
            success_rate=totals.success_rate,
            mean_ms=totals.mean_ms,
            p50_ms=totals.quantile_ms(0.5),
            p95_ms=totals.quantile_ms(0.95),
            p99_ms=totals.quantile_ms(0.99),
            max_ms=totals.duration_ms_max if totals.count else None,
            apdex=totals.apdex,
            requests_per_minute=totals.count / (back.total_seconds() / 60),
            peak_bucket_requests=max((bucket.requests for bucket in series), default=0),
        ),
        error_budget=ErrorBudget(
            target=budget.target,
            availability=budget.availability,
            allowed_failures=budget.allowed_failures,
            failures=budget.failures,
            consumed_ratio=budget.consumed_ratio,
            level=budget_level,
        ),
        series=series,
        busiest=busiest,
        slowest=slowest,
        failing=failing,
        alerts=alerts,
    )


# -- failed requests -----------------------------------------------------------------------


@router.get("/errors", response_model=FailedRequestPage)
def failed_requests(
    principal: AdminPrincipal,
    auth: Auth,
    ctx: Ctx,
    state: State,
    ops: Ops,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    cursor: str | None = None,
    status: Annotated[int | None, Query(ge=500, le=599)] = None,
    route: Annotated[str | None, Query(max_length=200)] = None,
) -> FailedRequestPage:
    """Requests that failed on the server's side (5xx), newest first.

    Each carries the request id: the full stack trace is in the server log under the same id.
    """
    if cursor is not None and not cursor.isdigit():
        raise HTTPException(422, "invalid cursor")
    rows = ops.store.request_errors(
        limit, int(cursor) if cursor else None, status=status, route=route
    )
    auth.record(ctx, "admin.monitoring.viewed", principal.user.id, detail={"view": "errors"})
    return FailedRequestPage(
        items=[
            FailedRequest(
                id=r.id,
                at=r.at,
                method=r.method,
                route=r.route,
                path=r.path,
                status=r.status,
                duration_ms=r.duration_ms,
                request_id=r.request_id,
                user_id=r.user_id,
                error_type=r.error_type,
                error_message=r.error_message,
            )
            for r in rows
        ],
        next_cursor=str(rows[-1].id) if len(rows) == limit else None,
        total_24h=ops.store.count_request_errors(state.clock() - timedelta(hours=24)),
    )


# -- visits --------------------------------------------------------------------------------

_VISIT_DAYS = {"7d": 7, "30d": 30, "90d": 90}


@router.get("/visits", response_model=Visits)
def visits(
    principal: AdminPrincipal,
    auth: Auth,
    ctx: Ctx,
    state: State,
    ops: Ops,
    range: VisitRange = "30d",  # noqa: A002 - the query parameter is named `range`
) -> Visits:
    """Page views and unique visitors per day, the most viewed pages and where visits came from.

    Days are in the service's time zone (``RC_TIMEZONE``, Korea Standard Time by default). A
    visitor is counted once per day by a pseudonym that changes daily, so the
    daily figures are exact and their sum is *visitor-days*, not unique people over the range.
    Signed-in accounts active in the last 7 and 30 days come from the audit log instead.
    """
    now = state.clock()
    today = state.local_now().date()
    days = _VISIT_DAYS[range]
    since = today - timedelta(days=days - 1)
    by_day = {entry.day: entry for entry in ops.store.daily_visits(since, today)}
    series = []
    for offset in range_days(days):
        day = since + timedelta(days=offset)
        entry = by_day.get(day)
        series.append(
            VisitDay(
                day=day,
                views=entry.views if entry else 0,
                visitors=entry.visitors if entry else 0,
                signed_in_visitors=entry.signed_in_visitors if entry else 0,
                bot_views=entry.bot_views if entry else 0,
            )
        )
    views = sum(day.views for day in series)
    signed_in_views = sum(entry.signed_in_views for entry in by_day.values())
    auth.record(
        ctx, "admin.monitoring.viewed", principal.user.id, detail={"view": "visits", "range": range}
    )
    return Visits(
        generated_at=now,
        range=range,
        since=since,
        totals=VisitTotals(
            views=views,
            visitor_days=sum(day.visitors for day in series),
            bot_views=sum(day.bot_views for day in series),
            signed_in_share=signed_in_views / views if views else None,
            views_today=series[-1].views,
            visitors_today=series[-1].visitors,
        ),
        series=series,
        top_pages=[
            PageCount(path=path, views=count)
            for path, count in ops.store.top_pages(since, today, 15)
        ],
        referrers=[
            ReferrerCount(host=host, visits=count)
            for host, count in ops.store.top_referrers(since, today, 15)
        ],
        by_locale=ops.store.views_by_locale(since, today),
        active_users_7d=auth.active_users(7),
        active_users_30d=auth.active_users(30),
    )


# -- product KPIs --------------------------------------------------------------------------


def _window(kpis: LearningKpis) -> LearningWindow:
    return LearningWindow(
        window_days=kpis.window_days,
        active_learners=kpis.active_learners,
        lessons_completed=kpis.lessons_completed,
        study_minutes=kpis.study_seconds // 60,
        quiz_runs=kpis.quiz_runs,
        quiz_mean_score=kpis.quiz_mean_score,
        reviews=kpis.reviews,
    )


@router.get("/kpi", response_model=Kpis)
def kpis(principal: AdminPrincipal, auth: Auth, ctx: Ctx, state: State, ops: Ops) -> Kpis:
    """Product KPIs: active users, growth, activation and retention, and learning volume.

    - **Active users** come from session activity: an account counts when one of its sessions
      was used in the period. Stickiness is DAU / MAU.
    - **Activation** is the share of accounts created in the last 30 days that completed at
      least one lesson. **Week-1 retention** is the share of accounts created 7 to 14 days ago
      that were active again in the last 7 days.
    - **Visit to sign-up** divides sign-ups by visitor-days; it shows the trend, not a funnel,
      because a visitor is only recognisable within one day (ADR 0017).
    """
    now = state.clock()
    today = state.local_now().date()
    daily, weekly, monthly = (auth.active_users(1), auth.active_users(7), auth.active_users(30))

    accounts = auth.accounts_overview()
    month = ops.store.daily_visits(today - timedelta(days=29), today)
    visitor_days = sum(day.visitors for day in month)

    store = open_progress_store(state.settings)
    try:
        lessons = store.list_lessons(user_id=None)
        sessions = store.list_sessions(user_id=None)
        quiz_runs = store.list_quiz_runs(user_id=None)
        reviews = store.list_reviews(user_id=None)
    finally:
        store.close()

    new_accounts = auth.cohort(30, 0)
    started = activated(new_accounts, lessons)
    week_old = auth.cohort(14, 7)
    came_back = week_old & auth.active_user_ids(7)

    auth.record(ctx, "admin.monitoring.viewed", principal.user.id, detail={"view": "kpi"})
    return Kpis(
        generated_at=now,
        active_users=ActiveUsers(
            daily=daily,
            weekly=weekly,
            monthly=monthly,
            stickiness=daily / monthly if monthly else None,
        ),
        growth=Growth(
            users_total=accounts.total,
            signups_7d=accounts.new_7d,
            signups_30d=accounts.new_30d,
            visitor_days_30d=visitor_days,
            # More sign-ups than counted visitors means the visits were not counted (page-view
            # intake off or refused, sign-ups through the API): a ratio above 100% is not a
            # conversion rate, so none is reported.
            visit_to_signup=(
                accounts.new_30d / visitor_days
                if visitor_days and accounts.new_30d <= visitor_days
                else None
            ),
        ),
        cohorts=Cohorts(
            activation_cohort=len(new_accounts),
            activated=len(started),
            activation_rate=len(started) / len(new_accounts) if new_accounts else None,
            retention_cohort=len(week_old),
            retained=len(came_back),
            week1_retention=len(came_back) / len(week_old) if week_old else None,
        ),
        learning_7d=_window(
            learning_kpis(lessons, sessions, quiz_runs, reviews, now, window_days=7)
        ),
        learning_30d=_window(
            learning_kpis(lessons, sessions, quiz_runs, reviews, now, window_days=30)
        ),
    )


def range_days(count: int) -> list[int]:
    """``0 … count-1``. Spelled out because ``range`` is shadowed by the query parameter."""
    return list(__builtins_range(count))


__builtins_range = range

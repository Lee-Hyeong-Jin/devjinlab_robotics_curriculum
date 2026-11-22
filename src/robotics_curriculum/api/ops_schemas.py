"""Response bodies of the monitoring endpoints (``/api/v1/admin/monitoring``, ADR 0017)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Level = Literal["ok", "warning", "critical"]
TrafficRange = Literal["24h", "7d", "30d"]
VisitRange = Literal["7d", "30d", "90d"]


class Schema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Alert(Schema):
    """One reading past its threshold."""

    key: str = Field(description="Which reading: disk, memory, load, temperature, errors, latency.")
    level: Level
    value: float
    threshold: float
    detail: str | None = Field(default=None, description="E.g. the sensor or the path.")


# -- system --------------------------------------------------------------------------------


class CpuReading(Schema):
    count: int
    load_1m: float | None
    load_5m: float | None
    load_15m: float | None
    load_per_cpu: float | None = Field(description="1-minute load divided by the CPU count.")
    usage_ratio: float | None = Field(
        description="Share of CPU time in use since the previous reading; null on the first."
    )
    level: Level


class MemoryReading(Schema):
    total_bytes: int
    available_bytes: int
    used_ratio: float
    swap_total_bytes: int
    swap_used_ratio: float | None = Field(description="null on a machine without swap.")
    swap_level: Level
    process_rss_bytes: int | None = Field(description="Resident memory of the API process.")
    level: Level


class ProcessReading(Schema):
    """Saturation of the API process itself."""

    open_files: int | None
    open_files_limit: int | None
    open_files_ratio: float | None
    open_files_level: Level
    requests_in_progress: int | None = Field(description="Requests being served right now.")


class DiskReading(Schema):
    path: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    used_ratio: float
    level: Level


class TemperatureReading(Schema):
    sensor: str
    celsius: float
    level: Level


class DatabaseReading(Schema):
    backend: str
    reachable: bool
    ping_ms: float | None
    size_bytes: int | None
    connections: int | None = Field(description="PostgreSQL connections in use; null on SQLite.")
    connections_max: int | None
    connections_level: Level
    pool: dict[str, dict[str, int]] = Field(description="Connections per pool: checked_out, size.")
    monitoring_rows: dict[str, int] = Field(description="Rows in each monitoring table.")


class SystemStatus(Schema):
    generated_at: datetime
    version: str
    host_uptime_seconds: float | None
    process_uptime_seconds: float
    cpu: CpuReading | None
    memory: MemoryReading | None
    process: ProcessReading
    disks: list[DiskReading]
    temperatures: list[TemperatureReading]
    database: DatabaseReading
    alerts: list[Alert]


# -- traffic -------------------------------------------------------------------------------


class TrafficTotals(Schema):
    requests: int
    succeeded: int = Field(description="2xx and 3xx.")
    client_errors: int = Field(description="4xx.")
    server_errors: int = Field(description="5xx.")
    success_rate: float | None = Field(description="1 - 5xx/all; null with no requests.")
    mean_ms: float | None
    p50_ms: float | None
    p95_ms: float | None
    p99_ms: float | None
    max_ms: float | None
    apdex: float | None = Field(
        description="Apdex score 0-1 (satisfied <= 500 ms, tolerating <= 2.5 s)."
    )
    requests_per_minute: float = Field(description="Average over the range.")
    peak_bucket_requests: int = Field(description="Requests in the busiest bucket of the series.")


class ErrorBudget(Schema):
    """An availability objective and how much of its allowed failure the range has used."""

    target: float = Field(description="E.g. 0.999.")
    availability: float | None
    allowed_failures: float
    failures: int
    consumed_ratio: float | None = Field(description="Above 1 the objective is missed.")
    level: Level


class TrafficBucket(Schema):
    start: datetime
    requests: int
    client_errors: int
    server_errors: int
    p50_ms: float | None
    p95_ms: float | None


class RouteStats(Schema):
    method: str
    route: str
    requests: int
    client_errors: int
    server_errors: int
    mean_ms: float | None
    p95_ms: float | None
    max_ms: float | None


class Traffic(Schema):
    generated_at: datetime
    range: TrafficRange
    since: datetime
    bucket_seconds: int
    totals: TrafficTotals
    error_budget: ErrorBudget
    series: list[TrafficBucket]
    busiest: list[RouteStats] = Field(description="Routes by request count.")
    slowest: list[RouteStats] = Field(
        description="Routes by p95, among those with enough requests."
    )
    failing: list[RouteStats] = Field(description="Routes with server errors, by error count.")
    alerts: list[Alert]


class FailedRequest(Schema):
    id: int
    at: datetime
    method: str
    route: str
    path: str
    status: int
    duration_ms: float
    request_id: str | None = Field(
        description="Find the full stack trace in the server log by this."
    )
    user_id: int | None
    error_type: str | None
    error_message: str | None


class FailedRequestPage(Schema):
    items: list[FailedRequest]
    next_cursor: str | None
    total_24h: int


# -- visits --------------------------------------------------------------------------------


class VisitDay(Schema):
    day: date
    views: int = Field(description="Page views by people.")
    visitors: int = Field(description="Unique visitors that day (daily-salted hash).")
    signed_in_visitors: int
    bot_views: int


class PageCount(Schema):
    path: str
    views: int


class ReferrerCount(Schema):
    host: str
    visits: int


class VisitTotals(Schema):
    views: int
    visitor_days: int = Field(
        description="Sum of daily unique visitors. Not unique people over the range: the "
        "identifier changes every day by design."
    )
    bot_views: int
    signed_in_share: float | None = Field(description="Share of views by signed-in readers.")
    views_today: int
    visitors_today: int


class Visits(Schema):
    generated_at: datetime
    range: VisitRange
    since: date
    totals: VisitTotals
    series: list[VisitDay] = Field(description="One entry per UTC day, zero days included.")
    top_pages: list[PageCount]
    referrers: list[ReferrerCount]
    by_locale: dict[str, int]
    active_users_7d: int = Field(description="Accounts that signed in during the last 7 days.")
    active_users_30d: int


# -- product KPIs --------------------------------------------------------------------------


class ActiveUsers(Schema):
    """Accounts that used the service, by how recently (from session activity)."""

    daily: int = Field(description="DAU: active in the last 24 hours.")
    weekly: int = Field(description="WAU: active in the last 7 days.")
    monthly: int = Field(description="MAU: active in the last 30 days.")
    stickiness: float | None = Field(description="DAU / MAU; null with no monthly actives.")


class Growth(Schema):
    users_total: int
    signups_7d: int
    signups_30d: int
    visitor_days_30d: int = Field(description="Sum of daily unique visitors over 30 days.")
    visit_to_signup: float | None = Field(
        description="Sign-ups per visitor-day over 30 days: a conversion proxy, not a funnel."
    )


class Cohorts(Schema):
    activation_cohort: int = Field(description="Accounts created in the last 30 days.")
    activated: int = Field(description="Of those, completed at least one lesson.")
    activation_rate: float | None
    retention_cohort: int = Field(description="Accounts created 7 to 14 days ago.")
    retained: int = Field(description="Of those, active again in the last 7 days.")
    week1_retention: float | None


class LearningWindow(Schema):
    window_days: int
    active_learners: int
    lessons_completed: int
    study_minutes: int
    quiz_runs: int
    quiz_mean_score: float | None = Field(description="Mean share correct, 0-1.")
    reviews: int


class Kpis(Schema):
    """Product KPIs: who uses the service, whether new accounts start learning, and how much
    learning happens."""

    generated_at: datetime
    active_users: ActiveUsers
    growth: Growth
    cohorts: Cohorts
    learning_7d: LearningWindow
    learning_30d: LearningWindow


class PageViewIn(Schema):
    """One page view, reported by the web tier."""

    path: str = Field(max_length=500)
    locale: str = Field(default="ko", max_length=8)
    referrer: str | None = Field(default=None, max_length=2000)
    signed_in: bool = False

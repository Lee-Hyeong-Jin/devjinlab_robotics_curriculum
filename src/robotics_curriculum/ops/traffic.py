"""Pure functions of the monitoring pipeline: buckets, latency quantiles, visit classification.

No I/O and no clock. The store persists what these compute and the API serves it.
"""

from __future__ import annotations

import hashlib
import hmac
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

LATENCY_BOUNDS_MS: tuple[float, ...] = (5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000)
"""Upper edges of the latency histogram, in milliseconds. One more bucket holds everything above."""

BUCKET_COUNT = len(LATENCY_BOUNDS_MS) + 1


def hour_bucket(moment: datetime) -> datetime:
    """The start of the UTC hour ``moment`` falls in."""
    return moment.astimezone(UTC).replace(minute=0, second=0, microsecond=0)


def status_class(status: int) -> int:
    """``2`` for 2xx … ``5`` for 5xx. 1xx counts as success; anything odd as a server error."""
    if 100 <= status < 300:
        return 2
    if 300 <= status < 400:
        return 3
    if 400 <= status < 500:
        return 4
    return 5


def latency_bucket(duration_ms: float) -> int:
    """Index of the histogram bucket a duration belongs to."""
    for index, bound in enumerate(LATENCY_BOUNDS_MS):
        if duration_ms <= bound:
            return index
    return len(LATENCY_BOUNDS_MS)


def quantile(histogram: Sequence[int], q: float) -> float | None:
    """Estimate the ``q`` quantile (0–1) in milliseconds from bucket counts.

    Linear interpolation inside the bucket the quantile falls in, the way Prometheus'
    ``histogram_quantile`` does it. A value in the overflow bucket is reported as the last
    finite bound: the histogram cannot say how far beyond it the request went.

    Args:
        histogram: Counts per bucket, ``BUCKET_COUNT`` long, not cumulative.
        q: The quantile, between 0 and 1.

    Returns:
        The estimate, or ``None`` when the histogram is empty.
    """
    total = sum(histogram)
    if total <= 0:
        return None
    rank = q * total
    seen = 0.0
    for index, count in enumerate(histogram):
        if count <= 0:
            continue
        if seen + count >= rank:
            if index >= len(LATENCY_BOUNDS_MS):
                return float(LATENCY_BOUNDS_MS[-1])
            lower = 0.0 if index == 0 else float(LATENCY_BOUNDS_MS[index - 1])
            upper = float(LATENCY_BOUNDS_MS[index])
            return lower + (upper - lower) * max(0.0, rank - seen) / count
        seen += count
    return float(LATENCY_BOUNDS_MS[-1])


APDEX_SATISFIED_MS = 500.0
APDEX_TOLERATING_MS = 2500.0
"""Apdex thresholds. The usual rule is "tolerating = 4 x satisfied" (2000 ms); the histogram has
no edge there, so the nearest one above is used and the score is, if anything, generous."""


def apdex(histogram: Sequence[int]) -> float | None:
    """Apdex score (0–1): satisfied requests plus half the tolerating ones, over all.

    A request is satisfied at or under ``APDEX_SATISFIED_MS``, tolerating up to
    ``APDEX_TOLERATING_MS`` and frustrated beyond. Both thresholds are histogram edges, so
    the score is exact for the data stored.
    """
    total = sum(histogram)
    if total <= 0:
        return None
    satisfied = tolerating = 0
    for index, count in enumerate(histogram):
        upper = LATENCY_BOUNDS_MS[index] if index < len(LATENCY_BOUNDS_MS) else float("inf")
        if upper <= APDEX_SATISFIED_MS:
            satisfied += count
        elif upper <= APDEX_TOLERATING_MS:
            tolerating += count
    return (satisfied + tolerating / 2) / total


@dataclass(frozen=True, slots=True)
class ErrorBudget:
    """How much of the allowed failure a period has used, for an availability target."""

    target: float
    availability: float | None
    allowed_failures: float
    failures: int

    @property
    def consumed_ratio(self) -> float | None:
        """Failures over the allowance; above 1 the objective is missed (``None``: no traffic)."""
        if self.availability is None:
            return None
        return self.failures / self.allowed_failures if self.allowed_failures > 0 else 0.0


def error_budget(requests: int, server_errors: int, target: float) -> ErrorBudget:
    """The error budget of an availability objective over ``requests`` requests.

    With a 99.9% target, one request in a thousand may fail; the budget is that allowance and
    the figure to watch is how much of it is gone.
    """
    return ErrorBudget(
        target=target,
        availability=None if requests <= 0 else 1.0 - server_errors / requests,
        allowed_failures=requests * (1.0 - target),
        failures=server_errors,
    )


@dataclass(slots=True)
class RequestTotals:
    """Requests added up over some set of buckets."""

    count: int = 0
    by_class: dict[int, int] | None = None
    duration_ms_sum: float = 0.0
    duration_ms_max: float = 0.0
    histogram: list[int] | None = None

    def __post_init__(self) -> None:
        if self.by_class is None:
            self.by_class = {2: 0, 3: 0, 4: 0, 5: 0}
        if self.histogram is None:
            self.histogram = [0] * BUCKET_COUNT

    def add(
        self,
        klass: int,
        count: int,
        duration_ms_sum: float,
        duration_ms_max: float,
        histogram: Sequence[int],
    ) -> None:
        assert self.by_class is not None and self.histogram is not None
        self.count += count
        self.by_class[klass] = self.by_class.get(klass, 0) + count
        self.duration_ms_sum += duration_ms_sum
        self.duration_ms_max = max(self.duration_ms_max, duration_ms_max)
        for index, value in enumerate(histogram[:BUCKET_COUNT]):
            self.histogram[index] += value

    @property
    def server_errors(self) -> int:
        assert self.by_class is not None
        return self.by_class.get(5, 0)

    @property
    def client_errors(self) -> int:
        assert self.by_class is not None
        return self.by_class.get(4, 0)

    @property
    def success_rate(self) -> float | None:
        """Share of requests that did not fail on the server's side.

        A 4xx is the client's mistake (a wrong password, a missing page) and says nothing
        about the service's health, so availability is ``1 - 5xx / all``.
        """
        return None if self.count == 0 else 1.0 - self.server_errors / self.count

    @property
    def mean_ms(self) -> float | None:
        return None if self.count == 0 else self.duration_ms_sum / self.count

    def quantile_ms(self, q: float) -> float | None:
        assert self.histogram is not None
        return quantile(self.histogram, q)

    @property
    def apdex(self) -> float | None:
        assert self.histogram is not None
        return apdex(self.histogram)


def series_buckets(start: datetime, end: datetime, step: timedelta) -> list[datetime]:
    """Bucket starts from ``start`` (inclusive) to ``end`` (exclusive), ``step`` apart."""
    out: list[datetime] = []
    cursor = start
    while cursor < end:
        out.append(cursor)
        cursor += step
    return out


# -- visits --------------------------------------------------------------------------------

_BOT = re.compile(
    r"bot|crawl|spider|scrap|preview|slurp|yeti|daum/|daumoa|facebookexternalhit|whatsapp|"
    r"embedly|lighthouse|google-|-google|mediapartners|bingpreview|headless|python-requests|"
    r"curl/|wget/|httpx|go-http-client|uptime|monitor",
    re.IGNORECASE,
)

_CONTENT_PATH = re.compile(r"^/modules/[A-Za-z0-9._-]{1,80}(?:/[A-Za-z0-9._-]{1,80})?(?:/quiz)?$")
_STATIC_PAGES = frozenset(
    {
        "/",
        "/roadmap",
        "/guide",
        "/resources",
        "/search",
        "/review",
        "/reports",
        "/profile",
        "/login",
        "/signup",
    }
)
OTHER_PATH = "(other)"


def is_bot(user_agent: str | None) -> bool:
    """Whether a user agent names itself as automated. An empty one counts as automated too."""
    return not user_agent or bool(_BOT.search(user_agent))


def normalize_path(path: str) -> str:
    """The page a visit is counted under.

    Known pages and content addresses keep their path; everything else becomes one
    ``(other)`` row. Without this, anybody requesting made-up addresses could fill the table
    with rows, and a path can carry things that should not be stored.
    """
    clean = path.split("?", 1)[0].split("#", 1)[0]
    if len(clean) > 1:
        clean = clean.rstrip("/")
    if clean in _STATIC_PAGES or _CONTENT_PATH.match(clean):
        return clean
    return OTHER_PATH


def referrer_host(referrer: str | None, own_hosts: Sequence[str] = ()) -> str | None:
    """The host a visit came from, or ``None`` for a direct visit or one from this site.

    Only the host is kept: a full referrer URL can carry a search query or a private address.
    """
    if not referrer:
        return None
    match = re.match(r"^https?://([^/:?#]+)", referrer.strip(), re.IGNORECASE)
    if not match:
        return None
    host = match.group(1).lower().removeprefix("www.")
    if len(host) > 100 or not re.fullmatch(r"[a-z0-9.-]+", host):
        return None
    own = {h.lower().removeprefix("www.") for h in own_hosts}
    return None if host in own else host


def daily_salt(secret: bytes, day: date) -> bytes:
    """The key visitor hashes are made with on ``day``; a different one every day."""
    return hmac.new(secret, f"visitor:{day.isoformat()}".encode(), hashlib.sha256).digest()


def visitor_hash(secret: bytes, day: date, ip: str | None, user_agent: str | None) -> str:
    """A pseudonym for one visitor on one day (ADR 0017).

    The same address and browser give the same value all day and an unrelated one the next,
    and the address cannot be recovered from it. Neither input is stored.
    """
    material = f"{ip or '-'}\n{user_agent or '-'}".encode()
    return hmac.new(daily_salt(secret, day), material, hashlib.sha256).hexdigest()[:16]


# -- thresholds ----------------------------------------------------------------------------

Level = str  # "ok" | "warning" | "critical"


def level(value: float | None, warning: float, critical: float) -> Level:
    """Classify a reading that is worse when higher. An unreadable value is ``ok``."""
    if value is None:
        return "ok"
    if value >= critical:
        return "critical"
    return "warning" if value >= warning else "ok"


THRESHOLDS: Mapping[str, tuple[float, float]] = {
    "disk_used_ratio": (0.80, 0.90),
    "memory_used_ratio": (0.85, 0.95),
    "load_per_cpu": (1.0, 2.0),
    "temperature_c": (80.0, 90.0),
    "server_error_ratio": (0.01, 0.05),
    "p95_ms": (1000.0, 3000.0),
    "swap_used_ratio": (0.50, 0.80),
    "fd_used_ratio": (0.70, 0.90),
    "db_connections_ratio": (0.70, 0.90),
    "error_budget_consumed": (0.75, 1.0),
}

AVAILABILITY_TARGET = 0.999
"""The availability objective the error budget is measured against (docs/specs/P3-2.md)."""
"""(warning, critical) per reading; documented in docs/specs/P3-2.md."""

"""Prometheus metrics (AC-OPS.1, docs/architecture/operations.md §4).

Each app gets its own :class:`CollectorRegistry`, so several apps in one process (tests)
never clash. Exposed at ``GET /metrics`` (``RC_API_METRICS=0`` disables it). The endpoint
is unauthenticated and meant for the internal network only: block ``/metrics`` at the
reverse proxy for public traffic.

Series:

- ``http_requests_total{method,route,status}``
- ``http_request_duration_seconds{method,route}`` (histogram; p50/p95/p99 via
  ``histogram_quantile``)
- ``http_requests_in_progress``
- ``rc_db_pool_connections{pool,state}`` (``checked_out`` / ``size``) for SQLAlchemy pools
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterator

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector
from starlette.types import ASGIApp, Message, Receive, Scope, Send

BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.3, 0.5, 1.0, 2.5, 5.0, 10.0)
UNMATCHED = "unmatched"


class PoolCollector(Collector):
    """Reads ``checked_out`` / ``size`` from named SQLAlchemy pools at scrape time."""

    def __init__(self, pools: Callable[[], dict[str, object]]) -> None:
        self._pools = pools

    def collect(self) -> Iterator[GaugeMetricFamily]:
        family = GaugeMetricFamily(
            "rc_db_pool_connections", "Database pool connections", labels=["pool", "state"]
        )
        for name, pool in self._pools().items():
            for state in ("checkedout", "size"):
                reader = getattr(pool, state, None)
                if callable(reader):
                    value = reader()
                    if isinstance(value, int):
                        label = "checked_out" if state == "checkedout" else state
                        family.add_metric([name, label], value)
        yield family


class Metrics:
    def __init__(self, pools: Callable[[], dict[str, object]] | None = None) -> None:
        self.registry = CollectorRegistry()
        self.requests = Counter(
            "http_requests_total",
            "HTTP requests",
            ["method", "route", "status"],
            registry=self.registry,
        )
        self.latency = Histogram(
            "http_request_duration_seconds",
            "HTTP request latency",
            ["method", "route"],
            buckets=BUCKETS,
            registry=self.registry,
        )
        self.in_progress = Gauge(
            "http_requests_in_progress", "HTTP requests being served", registry=self.registry
        )
        if pools is not None:
            self.registry.register(PoolCollector(pools))


def _route(scope: Scope) -> str:
    """The matched route template (``/api/v1/lessons/{lesson_id}``), never the raw path."""
    route = scope.get("route")
    path = getattr(route, "path", None)
    return path if isinstance(path, str) else UNMATCHED


class MetricsMiddleware:
    def __init__(self, app: ASGIApp, *, metrics: Metrics) -> None:
        self.app = app
        self.metrics = metrics

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        status = 500
        begin = time.perf_counter()

        async def send_status(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        self.metrics.in_progress.inc()
        try:
            await self.app(scope, receive, send_status)
        finally:
            self.metrics.in_progress.dec()
            route, method = _route(scope), scope["method"]
            self.metrics.requests.labels(method, route, str(status)).inc()
            self.metrics.latency.labels(method, route).observe(time.perf_counter() - begin)

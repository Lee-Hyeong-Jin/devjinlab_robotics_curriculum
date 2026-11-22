"""Buffers request measurements in the process and writes them to the store now and then.

Every request touches only a dictionary under a lock. A flush adds the buffered counts to
their hour rows in one transaction, at most every ``flush_interval`` seconds, and never on the
event loop. If the process dies, what was buffered since the last flush is lost: these are
operating figures, not a ledger (ADR 0017).
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from robotics_curriculum.ops.store import OpsStore, StatDelta, StatKey
from robotics_curriculum.ops.traffic import (
    BUCKET_COUNT,
    hour_bucket,
    latency_bucket,
    status_class,
)

logger = logging.getLogger("robotics_curriculum.api")

ERROR_MESSAGE_LIMIT = 500
PATH_LIMIT = 200


@dataclass(frozen=True, slots=True)
class Retention:
    """How long each kind of monitoring data is kept (ADR 0017)."""

    request_stats: timedelta = timedelta(days=90)
    request_errors: timedelta = timedelta(days=30)
    request_errors_max: int = 5000
    page_views: timedelta = timedelta(days=400)
    visitors: timedelta = timedelta(days=35)


class Recorder:
    """Collects request statistics and failed requests for one app."""

    def __init__(
        self,
        store: OpsStore,
        clock: Callable[[], datetime],
        *,
        flush_interval: float = 15.0,
        purge_interval: timedelta = timedelta(hours=6),
        retention: Retention | None = None,
    ) -> None:
        self.store = store
        self.clock = clock
        self.flush_interval = flush_interval
        self.purge_interval = purge_interval
        self.retention = retention or Retention()
        self._lock = threading.Lock()
        self._flush_lock = threading.Lock()
        self._buffer: dict[StatKey, StatDelta] = {}
        self._last_flush = clock()
        self._last_purge: datetime | None = None

    # -- recording -------------------------------------------------------------------------

    def record(self, *, method: str, route: str, status: int, duration_ms: float) -> None:
        """Count one finished request. Cheap: no I/O."""
        key: StatKey = (hour_bucket(self.clock()), route, method, status_class(status))
        with self._lock:
            delta = self._buffer.get(key)
            if delta is None:
                delta = self._buffer[key] = StatDelta(0, 0.0, 0.0, [0] * BUCKET_COUNT)
            delta.count += 1
            delta.duration_ms_sum += duration_ms
            delta.duration_ms_max = max(delta.duration_ms_max, duration_ms)
            delta.histogram[latency_bucket(duration_ms)] += 1

    def record_error(
        self,
        *,
        method: str,
        route: str,
        path: str,
        status: int,
        duration_ms: float,
        request_id: str | None,
        user_id: int | None,
        error: BaseException | None,
    ) -> None:
        """Keep one failed request. The path is stored without its query string."""
        message = None
        if error is not None:
            message = (str(error) or None) and str(error)[:ERROR_MESSAGE_LIMIT]
        try:
            self.store.add_request_error(
                at=self.clock(),
                method=method,
                route=route,
                path=path.split("?", 1)[0][:PATH_LIMIT],
                status=status,
                duration_ms=duration_ms,
                request_id=request_id,
                user_id=user_id,
                error_type=type(error).__name__ if error is not None else None,
                error_message=message,
            )
        except Exception:
            # The request already failed; failing to note it must not hide the first error.
            logger.exception("could not record a failed request")

    # -- flushing --------------------------------------------------------------------------

    def due(self) -> bool:
        """Whether enough time has passed since the last flush to do another."""
        with self._lock:
            if not self._buffer:
                return False
            return (self.clock() - self._last_flush).total_seconds() >= self.flush_interval

    def flush(self) -> int:
        """Write the buffer to the store. Returns the number of rows touched.

        Safe to call from any thread and at any time (an admin read calls it so the page
        shows the last seconds too). On a store error the counts go back into the buffer.
        """
        with self._flush_lock:
            with self._lock:
                pending, self._buffer = self._buffer, {}
                self._last_flush = self.clock()
            if not pending:
                return 0
            try:
                self.store.add_request_stats(pending)
            except Exception:
                logger.exception("could not flush request statistics")
                with self._lock:
                    for key, delta in pending.items():
                        current = self._buffer.get(key)
                        if current is None:
                            self._buffer[key] = delta
                            continue
                        current.count += delta.count
                        current.duration_ms_sum += delta.duration_ms_sum
                        current.duration_ms_max = max(
                            current.duration_ms_max, delta.duration_ms_max
                        )
                        for index, value in enumerate(delta.histogram):
                            current.histogram[index] += value
                return 0
            self._maybe_purge()
            return len(pending)

    def _maybe_purge(self) -> None:
        now = self.clock()
        if self._last_purge is not None and now - self._last_purge < self.purge_interval:
            return
        self._last_purge = now
        try:
            self.purge()
        except Exception:
            logger.exception("could not purge old monitoring data")

    def purge(self) -> dict[str, int]:
        """Delete everything past its retention period."""
        now = self.clock()
        keep = self.retention
        return self.store.purge(
            stats_before=now - keep.request_stats,
            errors_before=now - keep.request_errors,
            errors_keep=keep.request_errors_max,
            views_before=(now - keep.page_views).date(),
            visitors_before=(now - keep.visitors).date(),
        )

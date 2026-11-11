"""Structured JSON logging that carries the current request id.

:class:`~robotics_curriculum.api.middleware.RequestContextMiddleware` sets
:data:`request_id_var` for the duration of a request; every record logged meanwhile
(also from worker threads, which copy the context) carries it.
"""

from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime

LOGGER_NAME = "robotics_curriculum.api"

request_id_var: ContextVar[str | None] = ContextVar("rc_request_id", default=None)

# Attributes every LogRecord has; anything else came from ``extra=`` and becomes a field.
_STANDARD_ATTRS = frozenset(
    set(vars(logging.LogRecord("", 0, "", 0, "", None, None)))
    | {"message", "asctime", "color_message"}  # uvicorn's ANSI-colored copy of the message
)


class JsonFormatter(logging.Formatter):
    """One JSON object per line: ts, level, logger, message, request_id, extra fields."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(timespec="milliseconds"),
            "level": record.levelname.lower(),
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = request_id_var.get()
        if request_id is not None:
            payload["request_id"] = request_id
        for key, value in vars(record).items():
            if key not in _STANDARD_ATTRS and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(level: str = "info") -> None:
    """Send the root logger (and uvicorn's loggers) to one JSON handler on stderr."""
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level.upper())
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True

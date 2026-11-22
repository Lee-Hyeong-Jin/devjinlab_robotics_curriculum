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
from datetime import UTC, datetime, tzinfo

LOGGER_NAME = "robotics_curriculum.api"

request_id_var: ContextVar[str | None] = ContextVar("rc_request_id", default=None)
lang_var: ContextVar[str | None] = ContextVar("rc_lang", default=None)
"""Language chosen for the current request (``Accept-Language`` / ``RC_LANG``)."""

# Attributes every LogRecord has; anything else came from ``extra=`` and becomes a field.
_STANDARD_ATTRS = frozenset(
    set(vars(logging.LogRecord("", 0, "", 0, "", None, None)))
    | {"message", "asctime", "color_message"}  # uvicorn's ANSI-colored copy of the message
)


class JsonFormatter(logging.Formatter):
    """One JSON object per line: ts, level, logger, message, request_id, extra fields.

    ``ts`` is written in the service's time zone with its offset
    (``2026-11-22T19:11:34.120+09:00``): an operator reading the log reads local time, and the
    offset keeps every line an unambiguous instant for a tool that parses it.
    """

    def __init__(self, tz: tzinfo = UTC) -> None:
        super().__init__()
        self.tz = tz

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": datetime.fromtimestamp(record.created, self.tz).isoformat(
                timespec="milliseconds"
            ),
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


def configure_logging(level: str = "info", tz: tzinfo = UTC) -> None:
    """Send the root logger (and uvicorn's loggers) to one JSON handler on stderr.

    Args:
        level: Log level name.
        tz: Zone the ``ts`` field is written in (``Settings.timezone``).
    """
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter(tz))
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level.upper())
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True

"""Request id, access log, and last-resort 500 as one pure ASGI middleware."""

from __future__ import annotations

import logging
import re
import time
import uuid

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from robotics_curriculum.api.log import LOGGER_NAME, request_id_var
from robotics_curriculum.api.problems import problem_response

REQUEST_ID_HEADER = "X-Request-ID"
_VALID_ID = re.compile(r"^[A-Za-z0-9._-]{1,128}$")

logger = logging.getLogger(LOGGER_NAME)


def _request_id(scope: Scope) -> str:
    """The caller's ``X-Request-ID`` if it is a safe token, else a new UUID4 hex."""
    incoming = Headers(scope=scope).get(REQUEST_ID_HEADER)
    if incoming and _VALID_ID.match(incoming):
        return incoming
    return uuid.uuid4().hex


class RequestContextMiddleware:
    """Sets :data:`request_id_var`, echoes ``X-Request-ID``, logs one line per request.

    An exception that escapes the app is logged and answered with a 500 problem+json
    (when the response has not started yet), so even crashes carry the request id.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request_id = _request_id(scope)
        token = request_id_var.set(request_id)
        status = 500
        started = False
        begin = time.perf_counter()

        async def send_with_id(message: Message) -> None:
            nonlocal status, started
            if message["type"] == "http.response.start":
                started = True
                status = message["status"]
                MutableHeaders(scope=message)[REQUEST_ID_HEADER] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        except Exception:
            logger.exception("unhandled error")
            if started:
                raise
            response = problem_response(500, "internal server error", instance=scope["path"])
            await response(scope, receive, send_with_id)
        finally:
            logger.info(
                "request",
                extra={
                    "method": scope["method"],
                    "path": scope["path"],
                    "status": status,
                    "duration_ms": round((time.perf_counter() - begin) * 1000, 2),
                },
            )
            request_id_var.reset(token)

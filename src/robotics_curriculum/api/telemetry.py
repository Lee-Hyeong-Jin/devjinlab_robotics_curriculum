"""ASGI middleware that feeds the monitoring recorder (ADR 0017)."""

from __future__ import annotations

import time

import anyio
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from robotics_curriculum.api.log import request_id_var
from robotics_curriculum.api.metrics import UNMATCHED
from robotics_curriculum.ops.recorder import Recorder

EXCLUDED_PATHS = frozenset(
    {"/healthz", "/readyz", "/version", "/metrics", "/api/v1/telemetry/pageview"}
)
"""Probes, scrapes and the monitoring's own intake. Counted, they would be most of the traffic
and none of the service (one page view is one intake call, so it would always rank first)."""

USER_ID_STATE = "rc_user_id"
"""Key on ``scope["state"]`` where the auth dependency leaves the caller's user id."""


def _route(scope: Scope) -> str:
    route = scope.get("route")
    path = getattr(route, "path", None)
    return path if isinstance(path, str) else UNMATCHED


class OpsMiddleware:
    """Counts every request and keeps the ones that failed on the server's side.

    It sits inside the request-context middleware, so the request id is set and an exception
    passes through here on its way out: its type and message are recorded, then it is raised
    again for the handler that turns it into a 500.
    """

    def __init__(self, app: ASGIApp, *, recorder: Recorder) -> None:
        self.app = app
        self.recorder = recorder

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] in EXCLUDED_PATHS:
            await self.app(scope, receive, send)
            return
        status = 500
        error: BaseException | None = None
        begin = time.perf_counter()

        async def send_status(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_status)
        except Exception as exc:
            status, error = 500, exc
            raise
        finally:
            duration_ms = (time.perf_counter() - begin) * 1000
            route, method = _route(scope), scope["method"]
            self.recorder.record(method=method, route=route, status=status, duration_ms=duration_ms)
            if status >= 500:
                state = scope.get("state") or {}
                user_id = state.get(USER_ID_STATE)
                recorder = self.recorder
                request_id = request_id_var.get()
                path = scope["path"]

                def keep() -> None:
                    recorder.record_error(
                        method=method,
                        route=route,
                        path=path,
                        status=status,
                        duration_ms=duration_ms,
                        request_id=request_id,
                        user_id=user_id if isinstance(user_id, int) else None,
                        error=error,
                    )

                # Database work stays off the event loop.
                with anyio.CancelScope(shield=True):
                    await anyio.to_thread.run_sync(keep)
            if self.recorder.due():
                with anyio.CancelScope(shield=True):
                    await anyio.to_thread.run_sync(self.recorder.flush)

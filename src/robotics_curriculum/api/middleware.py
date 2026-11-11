"""Request id, access log, and last-resort 500 as one pure ASGI middleware."""

from __future__ import annotations

import logging
import re
import time
import uuid

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from robotics_curriculum.api.log import LOGGER_NAME, lang_var, request_id_var
from robotics_curriculum.api.problems import problem_response
from robotics_curriculum.i18n import resolve_lang

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
        accept_language = Headers(scope=scope).get("accept-language")
        lang_token = lang_var.set(resolve_lang(accept_language=accept_language))
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
            lang_var.reset(lang_token)


_DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")
# The API serves JSON only: nothing may be framed, scripted or embedded.
_API_CSP = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
_DOCS_CSP = (
    "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: "
    "https://fastapi.tiangolo.com; frame-ancestors 'none'"
)
_NO_STORE_PREFIXES = ("/api/v1/auth", "/api/v1/me", "/api/v1/admin")


class SecurityHeadersMiddleware:
    """CSP, nosniff, no framing, no referrer, locked-down features, HSTS in server mode,
    and ``Cache-Control: no-store`` on account endpoints (ASVS V14.4, AC-AUTH.8)."""

    def __init__(self, app: ASGIApp, *, hsts: bool = False) -> None:
        self.app = app
        self.hsts = hsts

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        path: str = scope["path"]

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                docs = path.startswith(_DOCS_PATHS)
                headers.setdefault("Content-Security-Policy", _DOCS_CSP if docs else _API_CSP)
                headers.setdefault("X-Content-Type-Options", "nosniff")
                headers.setdefault("X-Frame-Options", "DENY")
                headers.setdefault("Referrer-Policy", "no-referrer")
                headers.setdefault(
                    "Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()"
                )
                headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
                if self.hsts:
                    headers.setdefault(
                        "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
                    )
                if path.startswith(_NO_STORE_PREFIXES):
                    headers["Cache-Control"] = "no-store"
            await send(message)

        await self.app(scope, receive, send_with_headers)

"""FastAPI application factory.

Versioning: every resource lives under ``/api/v1``. A backwards-incompatible change ships as
``/api/v2`` next to v1 (see ``docs/adr/0006-api-fastapi.md``); ``/healthz`` and ``/readyz``
are unversioned.
"""

from __future__ import annotations

import logging
import os
import secrets
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

import httpx
from fastapi import FastAPI, Request

from robotics_curriculum import __version__
from robotics_curriculum.api.deps import AppState, ContentIndex, open_progress_store
from robotics_curriculum.api.log import LOGGER_NAME
from robotics_curriculum.api.metrics import Metrics, MetricsMiddleware
from robotics_curriculum.api.middleware import RequestContextMiddleware, SecurityHeadersMiddleware
from robotics_curriculum.api.problems import (
    PROBLEM_MEDIA_TYPE,
    Problem,
    ProblemResponse,
    install_problem_handlers,
    problem_response,
)
from robotics_curriculum.api.routers import admin, auth, content, health, me, progress, reports
from robotics_curriculum.api.settings import Settings
from robotics_curriculum.auth.mailer import Mailer, SmtpConfig, SmtpMailer
from robotics_curriculum.auth.oidc import OidcClient, OidcProvider, parse_providers
from robotics_curriculum.auth.service import AuthConfig, AuthError, AuthService
from robotics_curriculum.auth.store import SqlAuthStore
from robotics_curriculum.progress import ProgressError, ProgressService

logger = logging.getLogger(LOGGER_NAME)

API_TITLE = "Robotics Expert Course Platform API"
_PROBLEM_REF = {"$ref": "#/components/schemas/Problem"}


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def load_content(state: AppState) -> None:
    """(Re)build the content index; on failure keep the previous one and record the error."""
    try:
        index = ContentIndex(ProgressService.load_curriculum(state.settings.curriculum_dir))
    except ProgressError as exc:
        state.load_error = str(exc)
        logger.error("curriculum load failed", extra={"error": str(exc)})
        return
    state.index = index
    state.load_error = None
    logger.info("curriculum loaded", extra={"lessons": index.lesson_count})


_FROM_ENV: Any = object()


def build_auth(
    settings: Settings,
    clock: Callable[[], datetime],
    *,
    config: AuthConfig | None = None,
    mailer: Mailer | None = _FROM_ENV,
) -> AuthService:
    """Server mode: the auth service over ``RC_DATABASE_URL`` (or SQLite ``auth.db``)."""
    url = settings.database_url or f"sqlite:///{settings.data_dir / 'auth.db'}"
    if url.startswith("sqlite:///"):
        settings.data_dir.mkdir(parents=True, exist_ok=True)
    if mailer is _FROM_ENV:
        smtp = SmtpConfig.from_env(os.environ)
        mailer = SmtpMailer(smtp) if smtp else None

    def erase_learning_data(user_id: int) -> None:
        store = open_progress_store(settings)
        try:
            store.delete_user(user_id)
        finally:
            store.close()

    return AuthService(
        SqlAuthStore.from_url(url),
        config=config or AuthConfig.from_env(os.environ),
        mailer=mailer,
        clock=clock,
        erase_learning_data=erase_learning_data,
    )


async def _auth_error(request: Request, exc: Exception) -> ProblemResponse:
    assert isinstance(exc, AuthError)
    return problem_response(exc.status, exc.detail, instance=request.url.path, headers=exc.headers)


def _pools(state: AppState) -> dict[str, object]:
    """SQLAlchemy pools to report: the auth engine and shared PostgreSQL progress engines."""
    pools: dict[str, object] = {}
    if state.auth is not None:
        engine = getattr(state.auth.store, "engine", None)
        if engine is not None:
            pools["auth"] = engine.pool
    postgres = sys.modules.get("robotics_curriculum.progress.postgres")
    for i, engine in enumerate(getattr(postgres, "_shared_engines", {}).values()):
        pools[f"progress{i}"] = engine.pool
    return pools


def create_app(
    settings: Settings | None = None,
    *,
    clock: Callable[[], datetime] = _utcnow,
    auth_config: AuthConfig | None = None,
    mailer: Mailer | None = _FROM_ENV,
    oidc_providers: dict[str, OidcProvider] | None = None,
    oidc_http: httpx.Client | None = None,
) -> FastAPI:
    """Build the API app. ``settings`` defaults to :meth:`Settings.from_env`.

    Local mode (default): no accounts, every request acts as user 1. Server mode
    (``RC_AUTH_MODE=server``): every ``/api/v1`` call needs a session or a PAT.
    """
    settings = settings or Settings.from_env()
    state = AppState(settings=settings, clock=clock)
    load_content(state)
    if settings.server_mode:
        state.auth = build_auth(settings, clock, config=auth_config, mailer=mailer)
        providers = oidc_providers if oidc_providers is not None else parse_providers(os.environ)
        http = oidc_http or httpx.Client(follow_redirects=False)
        state.oidc = {pid: OidcClient(p, http, clock) for pid, p in providers.items()}
        secret = os.environ.get("RC_AUTH_SECRET", "")
        if not secret and state.oidc:
            logger.warning("RC_AUTH_SECRET is unset: OIDC logins only work on this one process")
        state.flow_key = secret.encode() if secret else secrets.token_bytes(32)

    app = FastAPI(
        title=API_TITLE,
        version=__version__,
        summary="Curriculum content, learner progress and reports over HTTP.",
        license_info={"name": "Apache-2.0", "identifier": "Apache-2.0"},
    )
    app.state.rc = state
    metrics = Metrics(pools=lambda: _pools(state))
    app.state.metrics = metrics
    app.add_middleware(MetricsMiddleware, metrics=metrics)
    app.add_middleware(
        SecurityHeadersMiddleware, hsts=settings.server_mode and settings.cookie_secure
    )
    app.add_middleware(RequestContextMiddleware)
    install_problem_handlers(app)
    app.add_exception_handler(AuthError, _auth_error)
    for module in (health, content, progress, reports, auth, me, admin):
        app.include_router(module.router)

    def openapi() -> dict[str, Any]:
        if app.openapi_schema is None:
            app.openapi_schema = _problem_openapi(FastAPI.openapi(app))
        return app.openapi_schema

    app.openapi = openapi  # type: ignore[method-assign]
    return app


def _problem_openapi(schema: dict[str, Any]) -> dict[str, Any]:
    """Document errors as problem+json: add ``Problem`` and replace FastAPI's 422 schema."""
    components = schema.setdefault("components", {}).setdefault("schemas", {})
    problem = Problem.model_json_schema(ref_template="#/components/schemas/{model}")
    components.update(problem.pop("$defs", {}))
    components["Problem"] = problem
    for name in ("HTTPValidationError", "ValidationError"):
        components.pop(name, None)
    for path_item in schema.get("paths", {}).values():
        for operation in path_item.values():
            responses = operation.get("responses", {})
            if "422" in responses:
                responses["422"] = {
                    "description": "Unprocessable Content",
                    "content": {PROBLEM_MEDIA_TYPE: {"schema": _PROBLEM_REF}},
                }
    return schema

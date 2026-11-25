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
from collections.abc import AsyncIterator, Callable, Mapping
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

import anyio
import httpx
from fastapi import FastAPI, Request

from robotics_curriculum import __version__
from robotics_curriculum.api.deps import AppState, ContentIndex, open_progress_store
from robotics_curriculum.api.log import LOGGER_NAME, lang_var
from robotics_curriculum.api.metrics import Metrics, MetricsMiddleware
from robotics_curriculum.api.middleware import RequestContextMiddleware, SecurityHeadersMiddleware
from robotics_curriculum.api.problems import (
    PROBLEM_MEDIA_TYPE,
    Problem,
    ProblemResponse,
    install_problem_handlers,
    problem_response,
)
from robotics_curriculum.api.routers import (
    admin,
    auth,
    content,
    health,
    me,
    monitoring,
    progress,
    quiz,
    reports,
    review,
)
from robotics_curriculum.api.routers import telemetry as telemetry_router
from robotics_curriculum.api.settings import ALLOW_REMOTE_LOCAL_ENV, Settings, is_loopback
from robotics_curriculum.api.telemetry import OpsMiddleware
from robotics_curriculum.auth.mailer import Mailer, SmtpConfig, SmtpMailer
from robotics_curriculum.auth.oidc import OidcClient, OidcProvider, parse_providers
from robotics_curriculum.auth.service import AuthConfig, AuthError, AuthService
from robotics_curriculum.auth.store import SqlAuthStore
from robotics_curriculum.i18n import get_translator
from robotics_curriculum.ops.recorder import Recorder
from robotics_curriculum.ops.store import OpsStore
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


class UnsafeConfiguration(RuntimeError):
    """The settings would serve an unauthenticated or unreliable API. Refuse to build."""


def check_exposure(settings: Settings, env: Mapping[str, str] | None = None) -> None:
    """Refuse local mode (no login, every request is admin) on a non-loopback bind.

    The same guard as ``rc api serve``, here as well so that building the app directly
    (``uvicorn robotics_curriculum.api.app:...``) cannot bypass it (SRV-11).
    ``RC_API_ALLOW_REMOTE_LOCAL=1`` opts out when the port is reachable only from the host.
    """
    env = os.environ if env is None else env
    if settings.server_mode or is_loopback(settings.host):
        return
    if env.get(ALLOW_REMOTE_LOCAL_ENV) == "1":
        logger.warning(
            "serving local mode (no authentication) on a non-loopback address",
            extra={"host": settings.host},
        )
        return
    raise UnsafeConfiguration(
        f"refusing to serve local mode (no login, admin access for everyone) on "
        f"{settings.host}: bind to 127.0.0.1, set RC_AUTH_MODE=server, or set "
        f"{ALLOW_REMOTE_LOCAL_ENV}=1 if the port is only reachable from this machine"
    )


def build_auth(
    settings: Settings,
    clock: Callable[[], datetime],
    *,
    config: AuthConfig | None = None,
    mailer: Mailer | None = _FROM_ENV,
    on_erase: Callable[[int], None] | None = None,
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
        if on_erase is not None:
            on_erase(user_id)

    return AuthService(
        SqlAuthStore.from_url(url),
        config=config or AuthConfig.from_env(os.environ),
        mailer=mailer,
        clock=clock,
        erase_learning_data=erase_learning_data,
        timezone=settings.timezone,
    )


async def _auth_error(request: Request, exc: Exception) -> ProblemResponse:
    assert isinstance(exc, AuthError)
    detail = exc.detail
    if exc.code is not None:
        # The sentence in the request's language; the English one stays in logs and the CLI.
        key = f"api.auth.{exc.code}"
        localized = get_translator(lang_var.get())(key, **exc.params)
        if localized != key:
            detail = localized
    return problem_response(
        exc.status, detail, instance=request.url.path, headers=exc.headers, code=exc.code
    )


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
    auth_secret: str | None = None,
) -> FastAPI:
    """Build the API app. ``settings`` defaults to :meth:`Settings.from_env`.

    Local mode (default): no accounts, every request acts as user 1. Server mode
    (``RC_AUTH_MODE=server``): every ``/api/v1`` call needs a session or a PAT.
    """
    settings = settings or Settings.from_env()
    check_exposure(settings)
    state = AppState(settings=settings, clock=clock)
    load_content(state)
    if settings.server_mode:

        def forget_in_monitoring(user_id: int) -> None:
            # Account deletion also detaches the user from the failed-request log.
            if state.ops is not None:
                state.ops.store.erase_user(user_id)

        state.auth = build_auth(
            settings, clock, config=auth_config, mailer=mailer, on_erase=forget_in_monitoring
        )
        providers = oidc_providers if oidc_providers is not None else parse_providers(os.environ)
        http = oidc_http or httpx.Client(follow_redirects=False)
        state.oidc = {pid: OidcClient(p, http, clock) for pid, p in providers.items()}
        if state.auth.config.require_verified_email and not state.auth.mail_enabled:
            # Nobody could ever get past the gate: every write would be 403 for every
            # account, with no way to request the link that would lift it.
            raise UnsafeConfiguration(
                "RC_AUTH_REQUIRE_VERIFIED_EMAIL=1 needs SMTP configured (RC_SMTP_HOST and "
                "friends): without mail the verification link can never be delivered, so no "
                "account could ever save anything. Configure mail, or unset the flag."
            )
        secret = auth_secret if auth_secret is not None else os.environ.get("RC_AUTH_SECRET", "")
        if not secret and state.oidc:
            # Without a shared key an OIDC callback that lands on another worker or replica
            # cannot be opened, so refuse rather than fail intermittently (SRV-15).
            raise UnsafeConfiguration(
                "RC_AUTH_SECRET must be set when OIDC providers are configured: it signs the "
                "in-flight login cookie and must be identical on every worker and replica"
            )
        state.flow_key = secret.encode() if secret else secrets.token_bytes(32)
        # Monitoring (ADR 0017) lives in the same database as the accounts. Without a
        # configured secret the visitor salt is per process: a restart starts the day's
        # unique-visitor count over, which is the safe failure.
        state.visit_key = secret.encode() if secret else secrets.token_bytes(32)
        engine = getattr(state.auth.store, "engine", None)
        if engine is not None and settings.ops_metrics:
            state.ops = Recorder(OpsStore(engine), clock, tz=settings.timezone)
    state.started_at = clock()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        yield
        # Write what is still buffered, so a deploy does not lose the last seconds of traffic.
        if state.ops is not None:
            await anyio.to_thread.run_sync(state.ops.flush)

    app = FastAPI(
        title=API_TITLE,
        version=__version__,
        summary="Curriculum content, learner progress and reports over HTTP.",
        license_info={"name": "Apache-2.0", "identifier": "Apache-2.0"},
        lifespan=lifespan,
    )
    app.state.rc = state
    metrics = Metrics(pools=lambda: _pools(state))
    app.state.metrics = metrics
    if state.ops is not None:
        # Added first, so it is the innermost: an exception passes through it on the way out.
        app.add_middleware(OpsMiddleware, recorder=state.ops)
    app.add_middleware(MetricsMiddleware, metrics=metrics)
    app.add_middleware(
        SecurityHeadersMiddleware, hsts=settings.server_mode and settings.cookie_secure
    )
    app.add_middleware(RequestContextMiddleware, default_lang=settings.default_lang)
    install_problem_handlers(app)
    app.add_exception_handler(AuthError, _auth_error)
    for module in (
        health,
        content,
        progress,
        quiz,
        review,
        reports,
        auth,
        me,
        admin,
        monitoring,
        telemetry_router,
    ):
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

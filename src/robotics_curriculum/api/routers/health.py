"""Unversioned system endpoints: ``/healthz``, ``/readyz``, ``/version``."""

from __future__ import annotations

import logging
from hmac import compare_digest

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from robotics_curriculum import __version__
from robotics_curriculum.api.deps import State, open_progress_store
from robotics_curriculum.api.log import LOGGER_NAME
from robotics_curriculum.api.schemas import Check, Health, Readiness, Version

router = APIRouter(tags=["system"])
logger = logging.getLogger(LOGGER_NAME)


@router.get("/healthz", response_model=Health)
def healthz() -> Health:
    """Liveness: the process answers."""
    return Health()


@router.get(
    "/readyz",
    response_model=Readiness,
    responses={503: {"model": Readiness, "description": "Not ready"}},
)
def readyz(state: State) -> Readiness | JSONResponse:
    """Readiness: the curriculum is indexed and the progress store opens."""
    # Details stay in the server log: paths and driver errors are not for clients (SRV-05).
    if state.index is None:
        content = Check(ok=False, detail="curriculum failed to load (see server log)")
    else:
        content = Check(ok=True, detail=f"{state.index.lesson_count} lessons")
    try:
        open_progress_store(state.settings).close()
        database = Check(ok=True)
    except Exception:  # any failure to open the store means "not ready"
        logger.exception("readiness: progress store unavailable")
        database = Check(ok=False, detail="progress store unavailable (see server log)")
    if database.ok and state.auth is not None and not state.auth.store.schema_ready():
        database = Check(ok=False, detail="auth tables missing (run alembic upgrade head)")
    ok = content.ok and database.ok
    body = Readiness(
        status="ready" if ok else "not_ready", checks={"content": content, "database": database}
    )
    if ok:
        return body
    return JSONResponse(body.model_dump(mode="json"), status_code=503)


@router.get("/version", response_model=Version)
def version() -> Version:
    """The installed package version."""
    return Version(version=__version__)


@router.get(
    "/metrics",
    response_class=Response,
    responses={200: {"content": {CONTENT_TYPE_LATEST: {"schema": {"type": "string"}}}}},
)
def metrics(request: Request, state: State) -> Response:
    """Prometheus text format: request counts, latency, in-flight requests, DB pools.

    Open by default and meant for the internal network: block ``/metrics`` at the reverse
    proxy, or set ``RC_API_METRICS_TOKEN`` to require ``Authorization: Bearer <token>``
    (SRV-16). ``RC_API_METRICS=0`` turns the endpoint off (404).
    """
    if not state.settings.metrics:
        raise HTTPException(404, "metrics are disabled (RC_API_METRICS=0)")
    expected = state.settings.metrics_token
    if expected:
        header = request.headers.get("authorization", "")
        scheme, _, given = header.partition(" ")
        if scheme.lower() != "bearer" or not compare_digest(given.strip(), expected):
            raise HTTPException(
                401, "metrics token required", headers={"WWW-Authenticate": 'Bearer realm="rc"'}
            )
    body = generate_latest(request.app.state.metrics.registry)
    return Response(body, media_type=CONTENT_TYPE_LATEST)

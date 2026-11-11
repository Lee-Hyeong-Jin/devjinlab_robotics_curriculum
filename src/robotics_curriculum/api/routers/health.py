"""Unversioned system endpoints: ``/healthz``, ``/readyz``, ``/version``."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from robotics_curriculum import __version__
from robotics_curriculum.api.deps import State, open_progress_store
from robotics_curriculum.api.schemas import Check, Health, Readiness, Version

router = APIRouter(tags=["system"])


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
    if state.index is None:
        content = Check(ok=False, detail=state.load_error)
    else:
        content = Check(ok=True, detail=f"{state.index.lesson_count} lessons")
    try:
        open_progress_store(state.settings).close()
        if state.auth is not None and not state.auth.store.schema_ready():
            raise RuntimeError("auth tables missing (run alembic upgrade head)")
        database = Check(ok=True)
    except Exception as exc:  # any failure to open the store means "not ready"
        database = Check(ok=False, detail=str(exc))
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
    """Prometheus text format. Unauthenticated: expose to the internal network only
    (block at the reverse proxy). ``RC_API_METRICS=0`` turns it off (404)."""
    if not state.settings.metrics:
        raise HTTPException(404, "metrics are disabled (RC_API_METRICS=0)")
    body = generate_latest(request.app.state.metrics.registry)
    return Response(body, media_type=CONTENT_TYPE_LATEST)

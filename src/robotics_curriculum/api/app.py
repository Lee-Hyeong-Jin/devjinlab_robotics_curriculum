"""FastAPI application factory.

Versioning: every resource lives under ``/api/v1``. A backwards-incompatible change ships as
``/api/v2`` next to v1 (see ``docs/adr/0006-api-fastapi.md``); ``/healthz`` and ``/readyz``
are unversioned.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI

from robotics_curriculum import __version__
from robotics_curriculum.api.deps import AppState, ContentIndex
from robotics_curriculum.api.log import LOGGER_NAME
from robotics_curriculum.api.middleware import RequestContextMiddleware
from robotics_curriculum.api.problems import PROBLEM_MEDIA_TYPE, Problem, install_problem_handlers
from robotics_curriculum.api.routers import content, health, progress, reports
from robotics_curriculum.api.settings import Settings
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


def create_app(
    settings: Settings | None = None,
    *,
    clock: Callable[[], datetime] = _utcnow,
) -> FastAPI:
    """Build the API app. ``settings`` defaults to :meth:`Settings.from_env`."""
    state = AppState(settings=settings or Settings.from_env(), clock=clock)
    load_content(state)

    app = FastAPI(
        title=API_TITLE,
        version=__version__,
        summary="Curriculum content, learner progress and reports over HTTP.",
        license_info={"name": "Apache-2.0", "identifier": "Apache-2.0"},
    )
    app.state.rc = state
    app.add_middleware(RequestContextMiddleware)
    install_problem_handlers(app)
    for module in (health, content, progress, reports):
        app.include_router(module.router)
    app.include_router(progress.me_router)

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

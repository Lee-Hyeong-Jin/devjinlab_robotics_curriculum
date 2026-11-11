"""RFC 9457 ``application/problem+json`` error responses and exception handlers."""

from __future__ import annotations

from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from robotics_curriculum.api.log import request_id_var

PROBLEM_MEDIA_TYPE = "application/problem+json"


class FieldError(BaseModel):
    loc: list[str | int] = Field(description="Where the bad value is, e.g. ['body', 'minutes'].")
    msg: str
    type: str


class Problem(BaseModel):
    """RFC 9457 problem details. ``type`` is ``about:blank`` and ``title`` the HTTP phrase."""

    model_config = ConfigDict(extra="allow")

    type: str = "about:blank"
    title: str
    status: int
    detail: str | None = None
    instance: str | None = Field(default=None, description="The request path.")
    request_id: str | None = Field(default=None, description="Same as the X-Request-ID header.")
    errors: list[FieldError] | None = Field(default=None, description="Only on 422.")


class ProblemResponse(JSONResponse):
    media_type = PROBLEM_MEDIA_TYPE


def problem_response(
    status: int,
    detail: str | None = None,
    *,
    instance: str | None = None,
    headers: dict[str, str] | None = None,
    **extensions: Any,
) -> ProblemResponse:
    problem = Problem(
        title=HTTPStatus(status).phrase,
        status=status,
        detail=detail,
        instance=instance,
        request_id=request_id_var.get(),
        **extensions,
    )
    body = jsonable_encoder(problem.model_dump(exclude_none=True))
    return ProblemResponse(body, status_code=status, headers=headers)


async def _http_exception(request: Request, exc: Exception) -> ProblemResponse:
    assert isinstance(exc, StarletteHTTPException)
    detail: str | None = exc.detail if isinstance(exc.detail, str) else None
    if detail == HTTPStatus(exc.status_code).phrase:
        detail = None  # Starlette's default detail only repeats the title
    headers = dict(exc.headers) if exc.headers else None
    return problem_response(exc.status_code, detail, instance=request.url.path, headers=headers)


async def _validation_error(request: Request, exc: Exception) -> ProblemResponse:
    assert isinstance(exc, RequestValidationError)
    errors = [
        FieldError(loc=list(err.get("loc", ())), msg=str(err.get("msg", "")), type=err["type"])
        for err in exc.errors()
    ]
    return problem_response(
        422,
        f"{len(errors)} invalid field(s)",
        instance=request.url.path,
        errors=[e.model_dump() for e in errors],
    )


def install_problem_handlers(app: FastAPI) -> None:
    """HTTP errors and request validation errors become problem+json.

    Unhandled exceptions become a 500 problem in the request middleware.
    """
    app.add_exception_handler(StarletteHTTPException, _http_exception)
    app.add_exception_handler(RequestValidationError, _validation_error)


def problem_responses(*statuses: int) -> dict[int | str, dict[str, Any]]:
    """OpenAPI ``responses=`` entries for the given error statuses."""
    return {
        status: {
            "description": HTTPStatus(status).phrase,
            "content": {PROBLEM_MEDIA_TYPE: {"schema": {"$ref": "#/components/schemas/Problem"}}},
        }
        for status in statuses
    }

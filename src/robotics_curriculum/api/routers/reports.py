"""Learning reports: JSON (structured summary + Markdown), or the Markdown alone when the
client sends ``Accept: text/markdown``.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import PlainTextResponse

from robotics_curriculum.api.deps import Index, Progress, State, get_principal
from robotics_curriculum.api.log import lang_var
from robotics_curriculum.api.problems import problem_responses
from robotics_curriculum.api.schemas import ModuleReportSummary, Report, WeeklySummary
from robotics_curriculum.report import (
    IsoWeek,
    build_module_report,
    build_weekly_report,
    render_module,
    render_weekly,
)

MARKDOWN = "text/markdown"
_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {"content": {MARKDOWN: {"schema": {"type": "string"}}}},
    **problem_responses(404, 422, 503),
}

router = APIRouter(
    dependencies=[Depends(get_principal)],
    prefix="/api/v1/reports",
    tags=["reports"],
    responses=_RESPONSES,
)

AcceptHeader = Annotated[str | None, Header(include_in_schema=False)]


class MarkdownResponse(PlainTextResponse):
    media_type = "text/markdown; charset=utf-8"


def _respond(report: Report, accept: str | None) -> Report | MarkdownResponse:
    if accept and MARKDOWN in accept and "application/json" not in accept:
        return MarkdownResponse(report.markdown)
    return report


@router.get("/weekly", response_model=Report)
def weekly(
    state: State,
    progress: Progress,
    week: Annotated[
        str | None,
        Query(
            pattern=r"^\d{4}-W\d{2}$",
            description="ISO week YYYY-Www [default: this week].",
            examples=["2026-W46"],
        ),
    ] = None,
    accept: AcceptHeader = None,
) -> Report | MarkdownResponse:
    """Weekly report (``rc report weekly``): time, completions, stuck points, next lessons.

    Weeks run Monday to Sunday in the server's local timezone.
    """
    now = state.clock()
    today = now.astimezone().date()
    try:
        iso = IsoWeek.parse(week) if week else IsoWeek.of(today)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    lang = lang_var.get()
    with progress.open() as service:
        data = build_weekly_report(service, iso, today=today, lang=lang)
    report = Report(
        kind="weekly",
        period=str(iso),
        generated_at=now,
        markdown=render_weekly(data),
        summary=WeeklySummary.of(data),
    )
    return _respond(report, accept)


@router.get("/modules/{module_id}", response_model=Report)
def module(
    module_id: str, state: State, index: Index, progress: Progress, accept: AcceptHeader = None
) -> Report | MarkdownResponse:
    """Per-module report (``rc report module``): lesson table, understanding distribution."""
    index.module(module_id)
    lang = lang_var.get()
    with progress.open() as service:
        data = build_module_report(service, module_id, lang)
    report = Report(
        kind="module",
        period=module_id,
        generated_at=state.clock(),
        markdown=render_module(data),
        summary=ModuleReportSummary.of(data),
    )
    return _respond(report, accept)

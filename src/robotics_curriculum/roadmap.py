"""`rc roadmap`: text view of a course grouped by level and module (FR-2, P1-3).

Statuses come from :meth:`ProgressService.status`; without a progress db the roadmap is
rendered from an empty in-memory store (nothing is created on disk). Kept out of
``cli.py`` so the CLI module only registers the command.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, get_args

import typer

from robotics_curriculum.content.models import Level
from robotics_curriculum.progress import (
    DB_FILENAME,
    LessonStatus,
    LessonSummary,
    ProgressError,
    ProgressService,
    SqliteProgressStore,
    default_curriculum_dir,
    default_data_dir,
)

LEVELS: tuple[str, ...] = get_args(Level)
NO_LEVEL = "(레벨 미지정)"
LEGEND = "[x] 완료  [>] 진행 중  [ ] 시작 전  [-] 잠김 (선수 레슨 미완료)"


def marker(summary: LessonSummary) -> str:
    if summary.status is LessonStatus.DONE:
        return "[x]"
    if summary.status is LessonStatus.IN_PROGRESS:
        return "[>]"
    return "[-]" if summary.locked else "[ ]"


def _fmt_minutes(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes}m"
    return f"{minutes // 60}h{minutes % 60:02d}m" if minutes % 60 else f"{minutes // 60}h"


def render_roadmap(summaries: list[LessonSummary], level: str | None = None) -> str:
    """Course -> level -> module -> lesson lines, with a done/total line per module."""
    out: list[str] = [LEGEND]
    course_ids = list(dict.fromkeys(s.course.id for s in summaries))
    for course_id in course_ids:
        rows = [s for s in summaries if s.course.id == course_id]
        course = rows[0].course
        n_done = sum(1 for s in rows if s.status is LessonStatus.DONE)
        out += ["", f"{course.title} ({course.id})  {n_done}/{len(rows)} lessons done"]
        groups = [lv for lv in (*LEVELS, None) if level is None or lv == level]
        for lv in groups:
            in_level = [s for s in rows if s.module.level == lv]
            if not in_level:
                continue
            out += ["", f"== {lv or NO_LEVEL} =="]
            module_ids = list(dict.fromkeys(s.module.id for s in in_level))
            for module_id in module_ids:
                lessons = [s for s in in_level if s.module.id == module_id]
                module = lessons[0].module
                done = sum(1 for s in lessons if s.status is LessonStatus.DONE)
                minutes = sum(s.lesson.estimated_minutes for s in lessons)
                out.append(
                    f"  {module.title} ({module.id})  {done}/{len(lessons)} done, "
                    f"est {_fmt_minutes(minutes)}"
                )
                for s in lessons:
                    prereqs = ", ".join(s.lesson.prerequisites) or "-"
                    out.append(
                        f"    {marker(s)} {s.lesson.id}  {s.lesson.title}  "
                        f"({_fmt_minutes(s.lesson.estimated_minutes)}; prereq: {prereqs})"
                    )
        if level is not None and not any(s.module.level == level for s in rows):
            out.append(f"  (no modules at level {level})")
    return "\n".join(out)


def _fail(message: str) -> typer.Exit:
    typer.echo(f"error: {message}", err=True)
    return typer.Exit(code=1)


def roadmap(
    ctx: typer.Context,
    course: Annotated[str | None, typer.Option("--course", help="Only this course id.")] = None,
    level: Annotated[
        str | None, typer.Option("--level", help="Only modules of this level: 기초|중급|고급.")
    ] = None,
) -> None:
    """Show the course roadmap by level and module with done/in-progress/locked markers."""
    if level is not None and level not in LEVELS:
        raise _fail(f"unknown level '{level}' (choose one of {'|'.join(LEVELS)})")
    root = getattr(ctx.obj, "curriculum", None) or default_curriculum_dir()
    data_dir = Path(getattr(ctx.obj, "data_dir", None) or default_data_dir())
    db = data_dir / DB_FILENAME
    try:
        courses = ProgressService.load_curriculum(Path(root))
        store = SqliteProgressStore(db if db.exists() else ":memory:")
        try:
            summaries = ProgressService(store, courses).status(course)
        finally:
            store.close()
    except ProgressError as exc:
        raise _fail(str(exc)) from None
    typer.echo(render_roadmap(summaries, level))

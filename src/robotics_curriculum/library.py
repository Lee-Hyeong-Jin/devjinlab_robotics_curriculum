"""`rc resources` / `rc show`: per-lesson study materials and study method (FR-6).

Kept out of ``cli.py`` so the CLI module only registers these commands.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from robotics_curriculum.content.models import Course, Lesson, Module, Resource, ResourceKind
from robotics_curriculum.content.sections import STUDY_GUIDE_HEADING, extract_section
from robotics_curriculum.i18n import Translator, get_translator
from robotics_curriculum.progress import (
    DB_FILENAME,
    LessonStatus,
    ProgressError,
    ProgressService,
    default_curriculum_dir,
    default_data_dir,
)
from robotics_curriculum.progress.factory import database_url, open_store
from robotics_curriculum.progress.store import StoreError

KIND_KEYS: dict[ResourceKind, str] = {
    ResourceKind.BOOK: "book",
    ResourceKind.COURSE: "course",
    ResourceKind.VIDEO: "video",
    ResourceKind.ARTICLE: "article",
    ResourceKind.OTHER: "other",
}


def _t(ctx: typer.Context | None = None) -> Translator:
    return get_translator(getattr(ctx.obj, "lang", None) if ctx is not None else None)


def _fail(message: str, ctx: typer.Context | None = None) -> typer.Exit:
    typer.echo(_t(ctx)("cli.error_prefix", message=message), err=True)
    return typer.Exit(code=1)


def _courses(ctx: typer.Context) -> list[Course]:
    root = getattr(ctx.obj, "curriculum", None) or default_curriculum_dir()
    try:
        return ProgressService.load_curriculum(Path(root))
    except ProgressError as exc:
        raise _fail(str(exc)) from None


def _modules(courses: list[Course]) -> list[Module]:
    return [module for course in courses for module in course.modules]


def _find_lesson(courses: list[Course], lesson_id: str) -> tuple[Module, Lesson]:
    for module in _modules(courses):
        for lesson in module.lessons:
            if lesson.id == lesson_id:
                return module, lesson
    raise _fail(f"unknown lesson '{lesson_id}'")


def _by_kind(entries: list[tuple[Resource, str]], t: Translator) -> list[str]:
    """Group ``(resource, suffix)`` pairs under the per-kind headers of the catalogue."""
    lines: list[str] = []
    for kind, key in KIND_KEYS.items():
        label = t(f"resource.kind.{key}")
        group = [(r, s) for r, s in entries if (r.kind or ResourceKind.OTHER) is kind]
        if group:
            lines.append(f"[{label}]")
        for resource, suffix in group:
            note = f" — {resource.note}" if resource.note else ""
            lines.append(f"  - {resource.title}{note}{suffix}")
            if resource.url:
                lines.append(f"    {resource.url}")
    return lines or [t("resource.none")]


def resources(
    ctx: typer.Context,
    lesson_id: Annotated[str | None, typer.Argument(help="Lesson id.")] = None,
    module: Annotated[
        str | None, typer.Option("--module", help="List every resource of a module.")
    ] = None,
    all_: Annotated[bool, typer.Option("--all", help="Library view of every resource.")] = False,
) -> None:
    """Show study materials by kind and the lesson's "이 단계 공부법" section."""
    t = _t(ctx)
    if sum([lesson_id is not None, module is not None, all_]) != 1:
        raise _fail("give exactly one of LESSON_ID, --module MODULE_ID or --all")
    courses = _courses(ctx)
    out: list[str] = []
    if lesson_id is not None:
        _, lesson = _find_lesson(courses, lesson_id)
        out += [f"{lesson.title} ({lesson.id})", ""]
        out += _by_kind([(r, "") for r in lesson.resources], t)
        guide = extract_section(lesson.body, STUDY_GUIDE_HEADING)
        if guide:
            out += ["", f"## {t('lesson.study_guide')}", "", guide]
    elif module is not None:
        found = [m for m in _modules(courses) if m.id == module]
        if not found:
            raise _fail(f"unknown module '{module}'")
        out.append(f"{found[0].title} ({found[0].id})")
        for lesson in found[0].lessons:
            out += ["", f"{lesson.title} ({lesson.id})"]
            out += _by_kind([(r, "") for r in lesson.resources], t)
    else:
        for course in courses:
            entries = [(r, f"  [{les.id}]") for les in course.iter_lessons() for r in les.resources]
            out += [t("resource.library_title", course=course.title, count=len(entries)), ""]
            out += _by_kind(entries, t)
    typer.echo("\n".join(out))


def _statuses(ctx: typer.Context, courses: list[Course]) -> dict[str, LessonStatus]:
    """Lesson statuses from the progress store, or ``{}`` if there is no store yet."""
    data_dir = Path(getattr(ctx.obj, "data_dir", None) or default_data_dir())
    if database_url() is None and not (data_dir / DB_FILENAME).exists():
        return {}
    store = open_store(data_dir)
    try:
        return {s.lesson.id: s.status for s in ProgressService(store, courses).status()}
    except (ProgressError, StoreError):
        return {}
    finally:
        store.close()


def show(
    ctx: typer.Context,
    lesson_id: Annotated[str, typer.Argument(help="Lesson id.")],
) -> None:
    """Print a lesson's summary (objectives, prerequisites, time) and its Markdown body."""
    t = _t(ctx)
    courses = _courses(ctx)
    module, lesson = _find_lesson(courses, lesson_id)
    statuses = _statuses(ctx, courses)
    level = t("lesson.level_suffix", level=module.level) if module.level else ""
    out = [
        f"# {lesson.title} ({lesson.id})",
        t("lesson.module_line", module=module.title) + level,
        t(
            "lesson.estimate_line",
            minutes=lesson.estimated_minutes,
            difficulty=lesson.difficulty,
        ),
        "",
        t("lesson.objectives"),
        *(f"  - {objective}" for objective in lesson.objectives),
        "",
        t("lesson.prerequisites")
        + ("" if lesson.prerequisites else t("lesson.prerequisites_none")),
    ]
    for prereq in lesson.prerequisites:
        if not statuses:
            mark = "-"
        else:
            mark = "[x]" if statuses.get(prereq) == LessonStatus.DONE else "[ ]"
        out.append(f"  {mark} {prereq}")
    out += ["", "---", "", lesson.body.strip()]
    typer.echo("\n".join(out))

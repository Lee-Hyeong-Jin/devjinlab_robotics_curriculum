"""Read-only curriculum content: courses, modules, lessons, resources, and the roadmap
(the content tree with the caller's lesson states)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from robotics_curriculum.api.deps import Index, Progress, get_principal
from robotics_curriculum.api.log import lang_var
from robotics_curriculum.api.problems import problem_responses
from robotics_curriculum.api.schemas import (
    Course,
    CourseSummary,
    Lesson,
    LessonProblem,
    LessonSummary,
    Module,
    ModuleSummary,
    Paper,
    Resource,
    ResourceRef,
    Roadmap,
    SearchHit,
    Stage,
)
from robotics_curriculum.content import Course as CourseModel
from robotics_curriculum.content import Lesson as LessonModel
from robotics_curriculum.content import ResourceKind, level_label
from robotics_curriculum.content.papers import paper_index, resolve_lesson_papers
from robotics_curriculum.content.problem_set import ProblemSetParseError, parse_problem_sets
from robotics_curriculum.content.problem_set import resolve_activity as resolve_problem_activity
from robotics_curriculum.content.search import search
from robotics_curriculum.content.sections import extract_study_guide

router = APIRouter(
    dependencies=[Depends(get_principal)],
    prefix="/api/v1",
    tags=["content"],
    responses=problem_responses(503),
)


def _summary(course: CourseModel) -> CourseSummary:
    return CourseSummary.of(course, lang_var.get())


@router.get("/courses", response_model=list[CourseSummary])
def list_courses(index: Index) -> list[CourseSummary]:
    """Every course in the curriculum, with its text in the requested language."""
    return [_summary(course) for course in index.courses]


@router.get("/courses/{course_id}", response_model=Course, responses=problem_responses(404))
def get_course(course_id: str, index: Index) -> Course:
    """One course with its modules grouped by level (consecutive modules of one level)."""
    course = index.course(course_id)
    lang = lang_var.get()
    stages: list[Stage] = []
    for module in course.modules:
        if not stages or stages[-1].level != module.level:
            label = level_label(module.level, lang) if module.level else None
            stages.append(Stage(level=module.level, level_label=label, modules=[]))
        stages[-1].modules.append(ModuleSummary.of(course, module, lang))
    return Course(**_summary(course).model_dump(), stages=stages)


@router.get("/modules/{module_id}", response_model=Module, responses=problem_responses(404))
def get_module(module_id: str, index: Index) -> Module:
    """One module with its lessons in teaching order."""
    entry = index.module(module_id)
    course, module = entry.course, entry.module
    lang = lang_var.get()
    return Module(
        **ModuleSummary.of(course, module, lang).model_dump(),
        lessons=[LessonSummary.of(course, module, les, lang) for les in module.lessons],
    )


@router.get("/lessons/{lesson_id}", response_model=Lesson, responses=problem_responses(404))
def get_lesson(lesson_id: str, index: Index) -> Lesson:
    """Lesson metadata, Markdown body, resources, and the study-method section.

    ``Accept-Language`` picks a translation (``<lesson>.<lang>.md``); a lesson without one
    answers in the language it was written in, which ``lang`` in the response states.
    """
    entry = index.lesson(lesson_id)
    lesson = entry.lesson
    text = lesson.localized(lang_var.get())
    order = [les.id for les in entry.course.iter_lessons()]
    pos = order.index(lesson.id)
    return Lesson(
        **LessonSummary.of(entry.course, entry.module, lesson, lang_var.get()).model_dump(),
        objectives=text.objectives,
        activities=text.activities,
        resources=[Resource.model_validate(r.model_dump()) for r in text.resources],
        papers=[
            Paper.of(row)
            for row in resolve_lesson_papers(lesson, paper_index(entry.course), lang_var.get())
        ],
        problems=_problems(lesson),
        body=text.body,
        study_method=extract_study_guide(text.body, text.lang),
        prev_lesson_id=order[pos - 1] if pos > 0 else None,
        next_lesson_id=order[pos + 1] if pos + 1 < len(order) else None,
    )


def _problems(lesson: LessonModel) -> list[LessonProblem]:
    """The lesson's problem set, or ``[]`` when a block does not parse.

    A broken block is a validation error (``rc validate`` rule 13); the API must still answer,
    and the body it returns still holds the block verbatim.
    """
    try:
        sets = parse_problem_sets(lesson)
    except ProblemSetParseError:
        return []
    return [
        LessonProblem(**problem.model_dump(), activity_id=resolve_problem_activity(block, lesson))
        for block in sets.blocks
        for problem in block.problems
    ]


@router.get("/resources", response_model=list[ResourceRef], responses=problem_responses(404))
def list_resources(
    index: Index,
    module_id: Annotated[str | None, Query(description="Only this module.")] = None,
    lesson_id: Annotated[str | None, Query(description="Only this lesson.")] = None,
    kind: Annotated[ResourceKind | None, Query(description="Only this kind.")] = None,
) -> list[ResourceRef]:
    """Resources of every lesson in teaching order, merged by (title, url)."""
    # Unknown ids are a 404 rather than an empty list.
    if module_id is not None:
        index.module(module_id)
    if lesson_id is not None:
        index.lesson(lesson_id)
    lang = lang_var.get()
    merged: dict[tuple[str, str | None], ResourceRef] = {}
    for course in index.courses:
        for module in course.modules:
            if module_id is not None and module.id != module_id:
                continue
            for lesson in module.lessons:
                if lesson_id is not None and lesson.id != lesson_id:
                    continue
                for res in lesson.localized_resources(lang):
                    if kind is not None and (res.kind or ResourceKind.OTHER) is not kind:
                        continue
                    key = (res.title, res.url)
                    if key not in merged:
                        merged[key] = ResourceRef(**res.model_dump(), lesson_ids=[])
                    if lesson.id not in merged[key].lesson_ids:
                        merged[key].lesson_ids.append(lesson.id)
    return list(merged.values())


@router.get("/search", response_model=list[SearchHit], responses=problem_responses(422))
def search_content(
    index: Index,
    q: Annotated[str, Query(min_length=2, max_length=200, description="Words to find.")],
    limit: Annotated[int, Query(ge=1, le=200)] = 20,
) -> list[SearchHit]:
    """Search lessons (title, summary, objectives, tags) and their resources (title, note).

    Every word must match; title matches rank first, then tags, then other text.
    """
    return [
        SearchHit(kind=h.kind, id=h.id, title=h.title, snippet=h.snippet, lesson_id=h.lesson_id)
        for h in search(index.courses, q, limit=limit, lang=lang_var.get())
    ]


@router.get("/roadmap", response_model=Roadmap, responses=problem_responses(404))
def get_roadmap(
    index: Index,
    progress: Progress,
    course_id: Annotated[str | None, Query(alias="course", description="Only this course.")] = None,
) -> Roadmap:
    """Level -> module -> lesson tree with the caller's states (``rc roadmap``).

    Lesson state: done, in_progress or available. Module state: done if every lesson is done,
    in_progress if any is started or done, else available. Progress values are fractions (0-1).
    Nothing is ever `locked` — lessons are not gated on finishing other lessons (ADR 0015);
    the value stays in the enum so an existing client keeps parsing.
    """
    if course_id is not None:
        index.course(course_id)
    with progress.open() as service:
        summaries = service.status(course_id)
    return Roadmap.of(summaries, lang_var.get())

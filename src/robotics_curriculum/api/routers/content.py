"""Read-only curriculum content: courses, modules, lessons, resources."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from robotics_curriculum.api.deps import Index, get_principal
from robotics_curriculum.api.problems import problem_responses
from robotics_curriculum.api.schemas import (
    Course,
    CourseSummary,
    Lesson,
    LessonSummary,
    Module,
    ModuleSummary,
    Resource,
    ResourceRef,
    Stage,
)
from robotics_curriculum.content import Course as CourseModel
from robotics_curriculum.content import ResourceKind
from robotics_curriculum.content.sections import STUDY_GUIDE_HEADING, extract_section

router = APIRouter(
    dependencies=[Depends(get_principal)],
    prefix="/api/v1",
    tags=["content"],
    responses=problem_responses(503),
)


def _summary(course: CourseModel) -> CourseSummary:
    return CourseSummary(
        id=course.id,
        title=course.title,
        summary=course.summary,
        tags=course.tags,
        module_count=len(course.modules),
        lesson_count=len(course.iter_lessons()),
    )


@router.get("/courses", response_model=list[CourseSummary])
def list_courses(index: Index) -> list[CourseSummary]:
    """Every course in the curriculum."""
    return [_summary(course) for course in index.courses]


@router.get("/courses/{course_id}", response_model=Course, responses=problem_responses(404))
def get_course(course_id: str, index: Index) -> Course:
    """One course with its modules grouped by level (consecutive modules of one level)."""
    course = index.course(course_id)
    stages: list[Stage] = []
    for module in course.modules:
        if not stages or stages[-1].level != module.level:
            stages.append(Stage(level=module.level, modules=[]))
        stages[-1].modules.append(ModuleSummary.of(course, module))
    return Course(**_summary(course).model_dump(), stages=stages)


@router.get("/modules/{module_id}", response_model=Module, responses=problem_responses(404))
def get_module(module_id: str, index: Index) -> Module:
    """One module with its lessons in teaching order."""
    entry = index.module(module_id)
    course, module = entry.course, entry.module
    return Module(
        **ModuleSummary.of(course, module).model_dump(),
        lessons=[LessonSummary.of(course, module, les) for les in module.lessons],
    )


@router.get("/lessons/{lesson_id}", response_model=Lesson, responses=problem_responses(404))
def get_lesson(lesson_id: str, index: Index) -> Lesson:
    """Lesson metadata, Markdown body, resources, and the study-method section."""
    entry = index.lesson(lesson_id)
    lesson = entry.lesson
    order = [les.id for les in entry.course.iter_lessons()]
    pos = order.index(lesson.id)
    return Lesson(
        **LessonSummary.of(entry.course, entry.module, lesson).model_dump(),
        objectives=lesson.objectives,
        activities=lesson.activities,
        resources=[Resource.model_validate(r.model_dump()) for r in lesson.resources],
        body=lesson.body,
        study_method=extract_section(lesson.body, STUDY_GUIDE_HEADING),
        prev_lesson_id=order[pos - 1] if pos > 0 else None,
        next_lesson_id=order[pos + 1] if pos + 1 < len(order) else None,
    )


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
    merged: dict[tuple[str, str | None], ResourceRef] = {}
    for course in index.courses:
        for module in course.modules:
            if module_id is not None and module.id != module_id:
                continue
            for lesson in module.lessons:
                if lesson_id is not None and lesson.id != lesson_id:
                    continue
                for res in lesson.resources:
                    if kind is not None and (res.kind or ResourceKind.OTHER) is not kind:
                        continue
                    key = (res.title, res.url)
                    if key not in merged:
                        merged[key] = ResourceRef(**res.model_dump(), lesson_ids=[])
                    if lesson.id not in merged[key].lesson_ids:
                        merged[key].lesson_ids.append(lesson.id)
    return list(merged.values())

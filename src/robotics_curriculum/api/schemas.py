"""Request and response bodies of the API. Names follow ``docs/api/openapi.yaml``.

These models are the public contract (the OpenAPI snapshot test guards them). They only
map core-library objects; no business logic lives here.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from robotics_curriculum import content
from robotics_curriculum.content import Activity, ResourceKind
from robotics_curriculum.progress import LessonProgress, LessonStatus, Session
from robotics_curriculum.progress import LessonSummary as Summary
from robotics_curriculum.report import ModuleReport, WeeklyReport


class Schema(BaseModel):
    model_config = ConfigDict(extra="forbid")


# -- system ----------------------------------------------------------------------------


class Health(Schema):
    status: Literal["ok"] = "ok"


class Check(Schema):
    ok: bool
    detail: str | None = None


class Readiness(Schema):
    status: Literal["ready", "not_ready"]
    checks: dict[str, Check] = Field(description="`content` and `database`.")


class Version(Schema):
    version: str


# -- content ---------------------------------------------------------------------------


class LessonSummary(Schema):
    id: str
    title: str
    summary: str
    course_id: str
    module_id: str
    difficulty: int = Field(ge=1, le=5)
    estimated_minutes: int
    prerequisites: list[str] = Field(description="Lesson ids.")
    tags: list[str]

    @classmethod
    def of(
        cls, course: content.Course, module: content.Module, lesson: content.Lesson
    ) -> LessonSummary:
        return cls(
            id=lesson.id,
            title=lesson.title,
            summary=lesson.summary,
            course_id=course.id,
            module_id=module.id,
            difficulty=lesson.difficulty,
            estimated_minutes=lesson.estimated_minutes,
            prerequisites=lesson.prerequisites,
            tags=lesson.tags,
        )


class Resource(content.Resource):
    """A study resource as written in lesson front matter."""


class Lesson(LessonSummary):
    objectives: list[str]
    activities: list[Activity]
    resources: list[Resource]
    body: str = Field(description="Markdown body without front matter.")
    study_method: str | None = Field(
        description='Markdown of the "## 이 단계 공부법" section, if the lesson has one.'
    )
    prev_lesson_id: str | None = Field(description="Previous lesson in course order.")
    next_lesson_id: str | None = Field(description="Next lesson in course order.")


class ModuleSummary(Schema):
    id: str
    title: str
    summary: str
    level: content.models.Level | None
    course_id: str
    lesson_count: int
    estimated_minutes: int = Field(description="Sum over the module's lessons.")

    @classmethod
    def of(cls, course: content.Course, module: content.Module) -> ModuleSummary:
        return cls(
            id=module.id,
            title=module.title,
            summary=module.summary,
            level=module.level,
            course_id=course.id,
            lesson_count=len(module.lessons),
            estimated_minutes=sum(lesson.estimated_minutes for lesson in module.lessons),
        )


class Module(ModuleSummary):
    lessons: list[LessonSummary]


class CourseSummary(Schema):
    id: str
    title: str
    summary: str
    tags: list[str]
    module_count: int
    lesson_count: int


class Stage(Schema):
    level: content.models.Level | None = Field(description="null for modules without a level.")
    modules: list[ModuleSummary]


class Course(CourseSummary):
    stages: list[Stage] = Field(description="Modules grouped by level, in course order.")


class ResourceRef(Resource):
    lesson_ids: list[str] = Field(description="Lessons that list this resource.")


# -- progress --------------------------------------------------------------------------


class StudySession(Schema):
    id: int | None
    lesson_id: str
    started_at: datetime
    ended_at: datetime | None
    note: str | None
    source: Literal["timer", "manual"]
    seconds: int = Field(description="Elapsed seconds (0 while running or when discarded).")

    @classmethod
    def of(cls, session: Session, seconds: int | None = None) -> StudySession:
        return cls(
            id=session.id,
            lesson_id=session.lesson_id,
            started_at=session.started_at,
            ended_at=session.ended_at,
            note=session.note,
            source=session.source,
            seconds=session.elapsed_seconds() if seconds is None else seconds,
        )


class LessonState(Schema):
    """One lesson in teaching order with its progress (a row of ``rc status``)."""

    lesson: LessonSummary
    status: LessonStatus
    locked: bool = Field(description="Some prerequisite is not done yet.")
    total_seconds: int
    started_at: datetime | None
    completed_at: datetime | None
    understanding: int | None
    note: str | None

    @classmethod
    def of(cls, s: Summary) -> LessonState:
        p = s.progress
        return cls(
            lesson=LessonSummary.of(s.course, s.module, s.lesson),
            status=p.status,
            locked=s.locked,
            total_seconds=p.total_seconds,
            started_at=p.started_at,
            completed_at=p.completed_at,
            understanding=p.understanding,
            note=p.note,
        )


class Status(Schema):
    open_session: StudySession | None = Field(description="The running timer, if any.")
    lessons: list[LessonState] = Field(description="Every lesson in teaching order.")


class NextLesson(Schema):
    lesson: LessonSummary
    status: LessonStatus
    reason: str = Field(description="Why it is recommended.")

    @classmethod
    def of(cls, s: Summary) -> NextLesson:
        reason = "in progress" if s.status is LessonStatus.IN_PROGRESS else "prerequisites done"
        return cls(
            lesson=LessonSummary.of(s.course, s.module, s.lesson),
            status=s.status,
            reason=reason,
        )


class StartRequest(Schema):
    lesson_id: str


class StopRequest(Schema):
    note: str | None = None
    discard: bool = Field(default=False, description="Delete the running session instead.")


class LogRequest(Schema):
    lesson_id: str
    minutes: int = Field(ge=1, le=24 * 60, description="Study time ending now.")
    note: str | None = None


class DoneRequest(Schema):
    lesson_id: str
    understanding: int | None = Field(default=None, ge=1, le=5, description="Self-rated, 1-5.")
    note: str | None = None


class DoneResult(Schema):
    progress: LessonProgress
    unlocked_lesson_ids: list[str] = Field(description="Lessons this completion unlocked.")


# -- reports ---------------------------------------------------------------------------


class ReportLesson(Schema):
    lesson_id: str
    title: str
    seconds_this_week: int
    understanding: int | None
    detail: str


class ReportModuleTime(Schema):
    module_id: str
    title: str
    seconds: int


class ReportNote(Schema):
    day: date
    lesson_id: str
    text: str


class WeeklySummary(Schema):
    start: date
    end: date
    as_of: date
    total_seconds: int
    session_count: int
    active_days: int
    completed: list[ReportLesson]
    in_progress: list[ReportLesson]
    module_time: list[ReportModuleTime]
    stuck: list[ReportLesson]
    next_lessons: list[ReportLesson]
    notes: list[ReportNote]

    @classmethod
    def of(cls, r: WeeklyReport) -> WeeklySummary:
        def lines(items: object) -> list[ReportLesson]:
            assert isinstance(items, list)
            return [ReportLesson.model_validate(x, from_attributes=True) for x in items]

        return cls(
            start=r.week.monday,
            end=r.week.sunday,
            as_of=r.as_of,
            total_seconds=r.total_seconds,
            session_count=r.session_count,
            active_days=r.active_days,
            completed=lines(r.completed),
            in_progress=lines(r.in_progress),
            module_time=[
                ReportModuleTime.model_validate(m, from_attributes=True) for m in r.module_time
            ],
            stuck=lines(r.stuck),
            next_lessons=lines(r.next_lessons),
            notes=[ReportNote.model_validate(n, from_attributes=True) for n in r.notes],
        )


class ModuleReportSummary(Schema):
    course_title: str
    module_id: str
    module_title: str
    done_count: int
    lesson_count: int
    total_seconds: int
    lessons: list[LessonState]

    @classmethod
    def of(cls, r: ModuleReport) -> ModuleReportSummary:
        return cls(
            course_title=r.course_title,
            module_id=r.module_id,
            module_title=r.module_title,
            done_count=r.done_count,
            lesson_count=len(r.lessons),
            total_seconds=r.total_seconds,
            lessons=[LessonState.of(s) for s in r.lessons],
        )


class Report(Schema):
    kind: Literal["weekly", "module"]
    period: str = Field(description="ISO week (weekly) or module id (module).")
    generated_at: datetime
    markdown: str = Field(description="The same Markdown as `rc report weekly|module`.")
    summary: WeeklySummary | ModuleReportSummary


__all__ = [
    "Course",
    "CourseSummary",
    "DoneRequest",
    "DoneResult",
    "Health",
    "Lesson",
    "LessonState",
    "LessonSummary",
    "LogRequest",
    "Module",
    "ModuleReportSummary",
    "ModuleSummary",
    "NextLesson",
    "Readiness",
    "Report",
    "Resource",
    "ResourceKind",
    "ResourceRef",
    "StartRequest",
    "Status",
    "StopRequest",
    "StudySession",
    "Version",
    "WeeklySummary",
]

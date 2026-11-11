"""Request and response bodies of the API. Names follow ``docs/api/openapi.yaml``.

These models are the public contract (the OpenAPI snapshot test guards them). They only
map core-library objects; no business logic lives here.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal, cast

from pydantic import BaseModel, ConfigDict, Field

from robotics_curriculum import content
from robotics_curriculum.content import Activity, ResourceKind
from robotics_curriculum.i18n import DEFAULT_LANG
from robotics_curriculum.learn import AnswerFeedback, CardView, QuestionView, SubmissionResult
from robotics_curriculum.learn.stats import StageProgress, WeekStats
from robotics_curriculum.progress import CardState, LessonProgress, LessonStatus, Session
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

    lang: str = Field(default=DEFAULT_LANG, description="Language of `title` and `summary`.")
    available_languages: list[str] = Field(
        default_factory=list, description="Languages this lesson has text in."
    )

    @classmethod
    def of(
        cls,
        course: content.Course,
        module: content.Module,
        lesson: content.Lesson,
        lang: str | None = None,
    ) -> LessonSummary:
        text = lesson.localized(lang)
        return cls(
            id=lesson.id,
            title=text.title,
            summary=text.summary,
            course_id=course.id,
            module_id=module.id,
            difficulty=lesson.difficulty,
            estimated_minutes=lesson.estimated_minutes,
            prerequisites=lesson.prerequisites,
            tags=text.tags,
            lang=text.lang,
            available_languages=lesson.languages(),
        )


class Resource(content.Resource):
    """A study resource as written in lesson front matter."""


class Lesson(LessonSummary):
    objectives: list[str]
    activities: list[Activity]
    resources: list[Resource]
    content_format: Literal["markdown"] = Field(
        default="markdown", description="Format of `body` and `study_method`."
    )
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


class StageStat(Schema):
    """One level (기초 / 중급 / 고급) with its lesson counts."""

    level: str
    progress: int = Field(ge=0, le=100, description="Percent of the level's lessons done.")
    lessons_done: int
    lessons_total: int
    module_ids: list[str]

    @classmethod
    def of(cls, stage: StageProgress) -> StageStat:
        return cls(
            level=stage.stage,
            progress=stage.progress.percent,
            lessons_done=stage.progress.done,
            lessons_total=stage.progress.total,
            module_ids=stage.module_ids,
        )


class WeekStat(Schema):
    """Study time of the current week (Monday onwards, caller's timezone)."""

    start: date
    minutes: int
    sessions: int

    @classmethod
    def of(cls, week: WeekStats) -> WeekStat:
        return cls(start=week.start, minutes=week.seconds // 60, sessions=week.sessions)


class Status(Schema):
    open_session: StudySession | None = Field(description="The running timer, if any.")
    lessons: list[LessonState] = Field(description="Every lesson in teaching order.")
    stages: list[StageStat] = Field(default_factory=list, description="Progress per level.")
    week: WeekStat | None = Field(default=None, description="This week's study time.")
    streak_days: int = Field(default=0, description="Consecutive days with study activity.")
    due_cards: int = Field(default=0, description="Flashcards due today.")


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


# -- quiz ------------------------------------------------------------------------------


QuestionKind = Literal["single", "multiple", "truefalse", "short"]
CardSourceName = Literal["quiz", "concept"]


class QuizQuestionPublic(Schema):
    """A question as a learner may see it before answering: no answer, no explanation."""

    id: str
    type: QuestionKind
    prompt: str
    choices: list[str] = Field(default_factory=list, description="Empty for short / true-false.")

    @classmethod
    def of(cls, view: QuestionView) -> QuizQuestionPublic:
        kind = cast(QuestionKind, view.type)  # validated by the quiz block parser
        return cls(id=view.id, type=kind, prompt=view.prompt, choices=view.choices)


class QuizPublic(Schema):
    """A lesson's quiz without answers (``GET /lessons/{id}/quiz``)."""

    lesson_id: str
    activity_id: str | None = Field(description="The `kind: quiz` activity it belongs to.")
    questions: list[QuizQuestionPublic]


class QuizSubmission(Schema):
    """One finished attempt at a lesson's quiz (``POST /quiz/runs``)."""

    lesson_id: str
    answers: dict[str, str] = Field(
        min_length=1,
        description="Question id -> answer, in the CLI notation: `2`, `1,3`, `o`/`x`, free text.",
    )
    partial: bool = Field(
        default=False, description="Allow leaving questions out instead of failing with 422."
    )


class QuizAnswerResult(Schema):
    """Per-question feedback, returned only once the answer was submitted."""

    question_id: str
    given: str
    correct: bool
    correct_answer: str
    explanation: str

    @classmethod
    def of(cls, feedback: AnswerFeedback) -> QuizAnswerResult:
        return cls(
            question_id=feedback.question_id,
            given=feedback.given,
            correct=feedback.correct,
            correct_answer=feedback.answer,
            explanation=feedback.explanation,
        )


class QuizRun(Schema):
    """The stored result of one quiz attempt."""

    lesson_id: str
    correct: int
    total: int
    percent: int = Field(ge=0, le=100)
    seconds: int
    answers: list[QuizAnswerResult]
    new_card_ids: list[str] = Field(description="Flashcards this attempt created.")

    @classmethod
    def of(cls, outcome: SubmissionResult) -> QuizRun:
        return cls(
            lesson_id=outcome.lesson_id,
            correct=outcome.correct,
            total=outcome.total,
            percent=outcome.percent,
            seconds=outcome.seconds,
            answers=[QuizAnswerResult.of(f) for f in outcome.feedback],
            new_card_ids=outcome.new_card_ids,
        )


# -- review ----------------------------------------------------------------------------


class ReviewCard(Schema):
    """A card that is due, with its current SM-2 schedule."""

    card_id: str
    lesson_id: str
    question_id: str
    front: str
    back: str
    source: CardSourceName
    due: date
    interval_days: int

    @classmethod
    def of(cls, view: CardView) -> ReviewCard:
        return cls(
            card_id=view.card_id,
            lesson_id=view.lesson_id,
            question_id=view.question_id,
            front=view.front,
            back=view.back,
            source=cast(CardSourceName, view.source),
            due=view.due,
            interval_days=view.interval_days,
        )


class RateRequest(Schema):
    """How well the learner recalled a card."""

    rating: Literal["again", "hard", "good", "easy"]


class ReviewResult(Schema):
    """The card's new schedule after a rating."""

    card_id: str
    repetitions: int
    interval_days: int
    ease: float
    due: date
    due_tomorrow: int = Field(description="Cards scheduled for the next day.")

    @classmethod
    def of(cls, state: CardState, due_tomorrow: int) -> ReviewResult:
        return cls(
            card_id=state.card_id,
            repetitions=state.repetitions,
            interval_days=state.interval_days,
            ease=state.ease,
            due=state.due,
            due_tomorrow=due_tomorrow,
        )


# -- roadmap -----------------------------------------------------------------------------

LockState = Literal["done", "in_progress", "available", "locked"]


def lock_state(s: Summary) -> LockState:
    """done / in_progress, else locked (a prerequisite is not done) or available."""
    if s.status is LessonStatus.DONE:
        return "done"
    if s.status is LessonStatus.IN_PROGRESS:
        return "in_progress"
    return "locked" if s.locked else "available"


class RoadmapLesson(Schema):
    id: str
    title: str
    state: LockState


class RoadmapModule(Schema):
    id: str
    title: str
    progress: float = Field(ge=0, le=1, description="Done lessons / all lessons.")
    state: LockState
    lessons: list[RoadmapLesson]

    @classmethod
    def of(cls, module: content.Module, rows: list[Summary]) -> RoadmapModule:
        states = [lock_state(s) for s in rows]
        if states and all(st == "done" for st in states):
            state: LockState = "done"
        elif any(st in ("done", "in_progress") for st in states):
            state = "in_progress"
        elif states and all(st == "locked" for st in states):
            state = "locked"
        else:
            state = "available"
        done = sum(1 for st in states if st == "done")
        return cls(
            id=module.id,
            title=module.title,
            progress=done / len(states) if states else 0.0,
            state=state,
            lessons=[
                RoadmapLesson(id=s.lesson.id, title=s.lesson.title, state=st)
                for s, st in zip(rows, states, strict=True)
            ],
        )


class RoadmapStage(Schema):
    course_id: str
    level: content.models.Level | None
    progress: float = Field(ge=0, le=1, description="Mean of the module progress values.")
    modules: list[RoadmapModule]


class Roadmap(Schema):
    stages: list[RoadmapStage] = Field(
        description="Consecutive modules of one level, in course order (like `rc roadmap`)."
    )

    @classmethod
    def of(cls, summaries: list[Summary]) -> Roadmap:
        stages: list[RoadmapStage] = []
        modules: dict[tuple[str, str], list[Summary]] = {}
        order: list[tuple[content.Course, content.Module]] = []
        for s in summaries:
            key = (s.course.id, s.module.id)
            if key not in modules:
                modules[key] = []
                order.append((s.course, s.module))
            modules[key].append(s)
        for course, module in order:
            item = RoadmapModule.of(module, modules[(course.id, module.id)])
            last = stages[-1] if stages else None
            if last is None or last.course_id != course.id or last.level != module.level:
                stages.append(
                    RoadmapStage(course_id=course.id, level=module.level, progress=0.0, modules=[])
                )
            stages[-1].modules.append(item)
        for stage in stages:
            stage.progress = sum(m.progress for m in stage.modules) / len(stage.modules)
        return cls(stages=stages)

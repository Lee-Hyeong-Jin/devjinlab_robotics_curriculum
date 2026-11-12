"""Learner progress: the ``rc status|next|start|stop|log|done`` and ``progress export``
use cases over :class:`~robotics_curriculum.progress.ProgressService`.

Unknown lesson / course ids are 404. A core :class:`ProgressError` (a timer is already
running, no timer is running, ...) is 409.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from robotics_curriculum.api.deps import (
    Index,
    Progress,
    State,
    get_principal,
    require_verified_email,
)
from robotics_curriculum.api.problems import problem_responses
from robotics_curriculum.api.schemas import (
    DoneRequest,
    DoneResult,
    LessonState,
    LogRequest,
    NextLesson,
    StageStat,
    StartRequest,
    Status,
    StopRequest,
    StudySession,
    WeekStat,
)
from robotics_curriculum.learn import dashboard_stats
from robotics_curriculum.progress import LessonProgress

router = APIRouter(
    dependencies=[Depends(get_principal), Depends(require_verified_email)],
    prefix="/api/v1/progress",
    tags=["progress"],
    responses=problem_responses(403, 404, 409, 422, 503),
)

CourseFilter = Annotated[str | None, Query(alias="course", description="Only this course id.")]


@router.get("/status", response_model=Status)
def get_status(
    index: Index, progress: Progress, state: State, course_id: CourseFilter = None
) -> Status:
    """Every lesson's progress in teaching order, the running timer, and the dashboard numbers.

    The dashboard part (``stages``, ``week``, ``streak_days``, ``due_cards``) is the same
    aggregate the static site and ``rc status`` show, and covers every course even when
    ``course`` narrows the lesson list.
    """
    if course_id is not None:
        index.course(course_id)
    with progress.open() as service:
        summaries = service.status(course_id)
        running = service.current_session()
        stats = dashboard_stats(service, now=state.clock())
    return Status(
        open_session=StudySession.of(running) if running else None,
        lessons=[LessonState.of(s) for s in summaries],
        stages=[StageStat.of(s) for s in stats.stages],
        week=WeekStat.of(stats.week),
        streak_days=stats.streak_days,
        due_cards=stats.due_today,
    )


@router.get("/next", response_model=list[NextLesson])
def get_next(
    index: Index,
    progress: Progress,
    course_id: CourseFilter = None,
    n: Annotated[int, Query(ge=1, le=10, description="How many to return.")] = 3,
) -> list[NextLesson]:
    """Lessons whose prerequisites are done: in-progress first, then teaching order."""
    if course_id is not None:
        index.course(course_id)
    with progress.open() as service:
        lessons = service.next_lessons(course_id, limit=n)
    return [NextLesson.of(s) for s in lessons]


@router.get("/lessons", response_model=list[LessonProgress])
def list_lesson_progress(progress: Progress) -> list[LessonProgress]:
    """Progress of every lesson in teaching order (``not_started`` when never touched)."""
    with progress.open() as service:
        return [s.progress for s in service.status()]


@router.get("/lessons/{lesson_id}", response_model=LessonProgress)
def get_lesson_progress(lesson_id: str, index: Index, progress: Progress) -> LessonProgress:
    """Progress of one lesson."""
    index.lesson(lesson_id)
    with progress.open() as service:
        return next(s.progress for s in service.status() if s.lesson.id == lesson_id)


@router.post("/start", response_model=StudySession, status_code=status.HTTP_201_CREATED)
def start(body: StartRequest, index: Index, progress: Progress) -> StudySession:
    """Start a study timer (one at a time; 409 if one is running)."""
    index.lesson(body.lesson_id)
    with progress.open() as service:
        return StudySession.of(service.start(body.lesson_id))


@router.post("/stop", response_model=StudySession)
def stop(progress: Progress, body: StopRequest | None = None) -> StudySession:
    """Stop the running timer and add its time; ``discard`` drops it (409 if none runs)."""
    body = body or StopRequest()
    with progress.open() as service:
        session, seconds = service.stop(body.note, discard=body.discard)
    return StudySession.of(session, seconds)


@router.post("/log", response_model=StudySession, status_code=status.HTTP_201_CREATED)
def log(body: LogRequest, index: Index, progress: Progress) -> StudySession:
    """Record study time manually: a session of ``minutes`` ending now."""
    index.lesson(body.lesson_id)
    with progress.open() as service:
        return StudySession.of(service.log(body.lesson_id, body.minutes, body.note))


@router.post("/done", response_model=DoneResult)
def done(body: DoneRequest, index: Index, progress: Progress) -> DoneResult:
    """Mark a lesson done (stops its running timer); lists the lessons it unlocked."""
    index.lesson(body.lesson_id)
    with progress.open() as service:
        saved, unlocked = service.done(
            body.lesson_id, understanding=body.understanding, note=body.note
        )
    return DoneResult(progress=saved, unlocked_lesson_ids=[les.id for les in unlocked])

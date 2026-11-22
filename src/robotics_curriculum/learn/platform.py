"""Platform-wide learning activity for the operator overview (P3-1).

Pure functions over rows already read from the progress store: no I/O, no clock. Everything
here counts across users, unlike :mod:`robotics_curriculum.learn.stats`, which describes one
learner.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta

from robotics_curriculum.progress import LessonProgress, LessonStatus, Session


@dataclass(frozen=True, slots=True)
class PlatformActivity:
    """What happened on the platform in the last ``window_days`` days, plus two totals."""

    window_days: int
    active_learners: int
    """Users with a study session or a lesson started or completed inside the window."""
    lessons_completed: int
    study_seconds: int
    lessons_completed_total: int
    learners_total: int
    """Users with any progress at all."""


@dataclass(frozen=True, slots=True)
class LearnerSummary:
    """One learner's progress, for the operator's user page."""

    lessons_done: int
    lessons_in_progress: int
    study_seconds: int
    last_activity_at: datetime | None


def platform_activity(
    lessons: Iterable[LessonProgress],
    sessions: Iterable[Session],
    now: datetime,
    *,
    window_days: int = 7,
) -> PlatformActivity:
    """Count activity across every user in the ``window_days`` before ``now``.

    A session that is still running counts up to ``now``. A session that began before the
    window counts in full if it ended inside it: the question is "how much studying happened
    lately", and splitting one sitting at the boundary would answer something finer than the
    data supports.

    Args:
        lessons: Lesson progress rows of all users.
        sessions: Study sessions of all users.
        now: The reference time (timezone-aware).
        window_days: Length of the window.

    Returns:
        The activity counts.
    """
    since = now - timedelta(days=window_days)
    active: set[int] = set()
    everyone: set[int] = set()
    completed = completed_total = 0
    for row in lessons:
        if row.status is not LessonStatus.NOT_STARTED:
            everyone.add(row.user_id)
        if row.status is LessonStatus.DONE:
            completed_total += 1
            if row.completed_at is not None and row.completed_at >= since:
                completed += 1
                active.add(row.user_id)
        if row.started_at is not None and row.started_at >= since:
            active.add(row.user_id)
    seconds = 0
    for session in sessions:
        everyone.add(session.user_id)
        last = session.ended_at or now
        if last < since:
            continue
        active.add(session.user_id)
        seconds += session.elapsed_seconds(now)
    return PlatformActivity(
        window_days=window_days,
        active_learners=len(active),
        lessons_completed=completed,
        study_seconds=seconds,
        lessons_completed_total=completed_total,
        learners_total=len(everyone),
    )


def learner_summary(
    lessons: Iterable[LessonProgress], sessions: Iterable[Session], now: datetime
) -> LearnerSummary:
    """Summarize one learner from their own rows.

    Args:
        lessons: That user's lesson progress rows.
        sessions: That user's study sessions.
        now: The reference time, for a session that is still running.

    Returns:
        Lesson counts, total study time and the latest moment anything was recorded.
    """
    done = in_progress = seconds = 0
    latest: datetime | None = None

    def seen(moment: datetime | None) -> None:
        nonlocal latest
        if moment is not None and (latest is None or moment > latest):
            latest = moment

    for row in lessons:
        if row.status is LessonStatus.DONE:
            done += 1
        elif row.status is LessonStatus.IN_PROGRESS:
            in_progress += 1
        seen(row.started_at)
        seen(row.completed_at)
    for session in sessions:
        seconds += session.elapsed_seconds(now)
        seen(session.ended_at or session.started_at)
    return LearnerSummary(
        lessons_done=done,
        lessons_in_progress=in_progress,
        study_seconds=seconds,
        last_activity_at=latest,
    )

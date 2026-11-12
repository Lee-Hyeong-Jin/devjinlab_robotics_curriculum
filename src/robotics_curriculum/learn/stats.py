"""Learning statistics: the numbers the dashboard, the CLI and the API all show.

The pure helpers (``ratio``, ``week_stats``, ``streak``, ...) used to live in
``site/stats.py``; they are here because statistics join content (stages, lessons) with
progress (sessions, cards), which is this package's job (platform-design §6). ``site/stats.py``
re-exports them so the page renderers keep working.

:func:`dashboard` is the one aggregate every surface should use, so the dashboard page, the
``rc`` output and the API cannot drift apart.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from robotics_curriculum.content import Module, level_label
from robotics_curriculum.i18n import DEFAULT_LANG, normalize_lang, translator
from robotics_curriculum.learn.review import due_count, recent_accuracy
from robotics_curriculum.progress import (
    LessonProgress,
    LessonStatus,
    LessonSummary,
    ProgressService,
    Session,
)

STAGES: tuple[str, ...] = ("기초", "중급", "고급")
NO_STAGE = "단계 미지정"
"""Bucket for modules that declare no level. Like the level values themselves this is a
stable id, not display text: :func:`stage_label` turns it into something to show."""
ACCURACY_DAYS = 7


def stage_of(module: Module) -> str:
    return module.level or NO_STAGE


def stage_label(stage: str, lang: str | None = None) -> str:
    """Display name of a stage bucket in ``lang`` (``NO_STAGE`` included)."""
    return level_label(None if stage == NO_STAGE else stage, lang)


def ordered_stages(stages: Iterable[str]) -> list[str]:
    """Known stages in teaching order (always all three), then the no-level bucket if used."""
    present = set(stages)
    return [*STAGES, *([NO_STAGE] if NO_STAGE in present else [])]


@dataclass(frozen=True, slots=True)
class Ratio:
    done: int
    total: int

    @property
    def percent(self) -> int:
        return round(100 * self.done / self.total) if self.total else 0


def ratio(summaries: Sequence[LessonSummary]) -> Ratio:
    return Ratio(sum(s.status is LessonStatus.DONE for s in summaries), len(summaries))


@dataclass(frozen=True, slots=True)
class WeekStats:
    start: date
    seconds: int
    sessions: int


def week_start(day: date) -> date:
    """Monday of the ISO week containing ``day``."""
    return day - timedelta(days=day.weekday())


def week_stats(sessions: Iterable[Session], now: datetime) -> WeekStats:
    """Study time and session count since Monday 00:00 in ``now``'s timezone.

    A still-running timer session counts up to ``now``.
    """
    start = week_start(now.date())
    seconds = count = 0
    for session in sessions:
        if session.started_at.astimezone(now.tzinfo).date() < start:
            continue
        count += 1
        seconds += session.elapsed_seconds(now)
    return WeekStats(start, seconds, count)


def activity_days(
    sessions: Iterable[Session], progress: Iterable[LessonProgress], now: datetime
) -> set[date]:
    """Local dates with a study session or a lesson completion."""
    tz = now.tzinfo
    days = {s.started_at.astimezone(tz).date() for s in sessions}
    days |= {p.completed_at.astimezone(tz).date() for p in progress if p.completed_at}
    return days


def streak(days: set[date], today: date) -> int:
    """Consecutive study days ending today (or yesterday, if nothing yet today)."""
    day = today if today in days else today - timedelta(days=1)
    count = 0
    while day in days:
        count += 1
        day -= timedelta(days=1)
    return count


def format_minutes(minutes: int, lang: str | None = None) -> str:
    """``135`` -> ``"2시간 15분"`` / ``"2h 15m"``."""
    t = translator(normalize_lang(lang) or DEFAULT_LANG)
    hours, rest = divmod(minutes, 60)
    if hours and rest:
        return t("duration.hours_minutes", hours=hours, minutes=rest)
    return t("duration.hours", hours=hours) if hours else t("duration.minutes", minutes=rest)


def format_seconds(seconds: int, lang: str | None = None) -> str:
    """Study time as a duration; anything under a minute is said in words."""
    t = translator(normalize_lang(lang) or DEFAULT_LANG)
    if seconds <= 0:
        return t("duration.zero")
    return format_minutes(seconds // 60, lang) if seconds >= 60 else t("duration.under_minute")


# -- dashboard aggregate -------------------------------------------------------


@dataclass(frozen=True, slots=True)
class StageProgress:
    """One level (foundation / intermediate / advanced) with its lesson counts and modules."""

    stage: str
    progress: Ratio
    module_ids: list[str]


@dataclass(frozen=True, slots=True)
class DashboardStats:
    """Everything the dashboard shows, computed once from content + progress."""

    now: datetime
    total: Ratio
    stages: list[StageProgress]
    week: WeekStats
    streak_days: int
    due_today: int
    current: LessonSummary | None
    accuracy: tuple[int, int] | None
    """Correct / answered quiz questions of the last :data:`ACCURACY_DAYS` days."""

    @property
    def accuracy_percent(self) -> int | None:
        if self.accuracy is None or not self.accuracy[1]:
            return None
        correct, total = self.accuracy
        return round(100 * correct / total)


def dashboard(service: ProgressService, *, now: datetime) -> DashboardStats:
    """Aggregate one learner's progress for the dashboard, ``rc status`` and the API."""
    summaries = service.status()
    sessions = service.store.list_sessions(service.user_id)
    progress_rows = [s.progress for s in summaries]
    today = now.astimezone(now.tzinfo).date()

    by_stage: dict[str, list[LessonSummary]] = {}
    modules: dict[str, list[str]] = {}
    for summary in summaries:
        stage = stage_of(summary.module)
        by_stage.setdefault(stage, []).append(summary)
        ids = modules.setdefault(stage, [])
        if summary.module.id not in ids:
            ids.append(summary.module.id)
    stages = [
        StageProgress(stage, ratio(by_stage[stage]), modules.get(stage, []))
        for stage in ordered_stages(by_stage)
        if stage in by_stage
    ]

    upcoming = service.next_lessons(limit=1)
    return DashboardStats(
        now=now,
        total=ratio(summaries),
        stages=stages,
        week=week_stats(sessions, now),
        streak_days=streak(activity_days(sessions, progress_rows, now), today),
        due_today=due_count(service.store, today=today, user_id=service.user_id),
        current=upcoming[0] if upcoming else None,
        accuracy=recent_accuracy(
            service.store.list_quiz_attempts(service.user_id),
            since=now - timedelta(days=ACCURACY_DAYS),
        ),
    )

"""Pure helpers that turn progress rows into dashboard numbers (platform-design 4.3)."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from robotics_curriculum.content import Module
from robotics_curriculum.progress import LessonProgress, LessonStatus, LessonSummary, Session

STAGES: tuple[str, ...] = ("기초", "중급", "고급")
NO_STAGE = "단계 미지정"


def stage_of(module: Module) -> str:
    return module.level or NO_STAGE


def ordered_stages(stages: Iterable[str]) -> list[str]:
    """Known stages in teaching order (always all three), then "단계 미지정" if used."""
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


def format_minutes(minutes: int) -> str:
    hours, rest = divmod(minutes, 60)
    if hours and rest:
        return f"{hours}시간 {rest}분"
    return f"{hours}시간" if hours else f"{rest}분"


def format_seconds(seconds: int) -> str:
    if seconds <= 0:
        return "0분"
    return format_minutes(seconds // 60) if seconds >= 60 else "1분 미만"

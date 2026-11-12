"""Weekly learning report (FR-7.1): ``rc report weekly``.

``build_weekly_report`` reads progress through a :class:`ProgressService` and returns a
plain :class:`WeeklyReport`; ``render_weekly`` turns it into Markdown with no I/O, so the
output is testable from fixed input. Weeks are ISO weeks (Monday-Sunday) in local time.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, tzinfo

from robotics_curriculum.i18n import DEFAULT_LANG, Translator, normalize_lang, translator
from robotics_curriculum.progress import LessonStatus, ProgressService

STUCK_DAYS = 7
STUCK_AGAIN = 2
LOW_UNDERSTANDING = 2
NEXT_COUNT = 3

_WEEK = re.compile(r"^(\d{4})-W(\d{2})$")


@dataclass(frozen=True, slots=True)
class IsoWeek:
    year: int
    week: int

    @classmethod
    def parse(cls, text: str) -> IsoWeek:
        """``"2026-W46"`` -> ``IsoWeek(2026, 46)``; raises ``ValueError`` if invalid."""
        match = _WEEK.match(text.strip())
        if not match:
            raise ValueError(f"invalid ISO week '{text}' (use YYYY-Www, e.g. 2026-W46)")
        try:
            date.fromisocalendar(int(match[1]), int(match[2]), 1)
        except ValueError:
            raise ValueError(f"week {text} does not exist") from None
        return cls(int(match[1]), int(match[2]))

    @classmethod
    def of(cls, day: date) -> IsoWeek:
        year, week, _ = day.isocalendar()
        return cls(year, week)

    @property
    def monday(self) -> date:
        return date.fromisocalendar(self.year, self.week, 1)

    @property
    def sunday(self) -> date:
        return self.monday + timedelta(days=6)

    def __str__(self) -> str:
        return f"{self.year}-W{self.week:02d}"


@dataclass(frozen=True, slots=True)
class LessonLine:
    lesson_id: str
    title: str
    seconds_this_week: int = 0
    understanding: int | None = None
    detail: str = ""


@dataclass(frozen=True, slots=True)
class ModuleTime:
    module_id: str
    title: str
    seconds: int


@dataclass(frozen=True, slots=True)
class NoteLine:
    day: date
    lesson_id: str
    text: str


@dataclass(frozen=True, slots=True)
class QuizStats:
    """Quiz attempts and card reviews that happened in the week (P1-2)."""

    attempts: int = 0
    correct: int = 0
    runs: int = 0
    reviews: int = 0
    rating_counts: tuple[int, int, int, int] = (0, 0, 0, 0)  # again, hard, good, easy

    @property
    def percent(self) -> int:
        return round(100 * self.correct / self.attempts) if self.attempts else 0


def _t(lang: str | None) -> Translator:
    return translator(normalize_lang(lang) or DEFAULT_LANG)


@dataclass(slots=True)
class WeeklyReport:
    week: IsoWeek
    as_of: date
    lang: str = DEFAULT_LANG
    """Language the titles and the ``detail`` strings were built in."""
    total_seconds: int = 0
    session_count: int = 0
    active_days: int = 0
    quiz: QuizStats = field(default_factory=QuizStats)
    completed: list[LessonLine] = field(default_factory=list)
    in_progress: list[LessonLine] = field(default_factory=list)
    module_time: list[ModuleTime] = field(default_factory=list)
    stuck: list[LessonLine] = field(default_factory=list)
    next_lessons: list[LessonLine] = field(default_factory=list)
    notes: list[NoteLine] = field(default_factory=list)


def _local_day(moment: datetime, tz: tzinfo | None) -> date:
    return moment.astimezone(tz).date()


def build_weekly_report(
    service: ProgressService,
    week: IsoWeek,
    *,
    today: date,
    tz: tzinfo | None = None,
    lang: str | None = None,
) -> WeeklyReport:
    """Collect one ISO week of progress. ``tz=None`` means the system local timezone.

    The stuck check is judged as of ``min(today, week's Sunday)``: a past week as of its
    Sunday, the current week as of today. "Next" lessons reflect the current state.

    ``lang`` picks the language of the lesson and module titles and of the short
    ``detail`` strings; the numbers are the same in every language.
    """
    as_of = min(today, week.sunday)
    chosen = normalize_lang(lang) or DEFAULT_LANG
    t = _t(chosen)
    report = WeeklyReport(week=week, as_of=as_of, lang=chosen)
    summaries = service.status()
    known = {s.lesson.id for s in summaries}

    def in_week(moment: datetime | None) -> bool:
        return moment is not None and week.monday <= _local_day(moment, tz) <= week.sunday

    # Closed sessions that started this week (a running timer is not counted yet).
    sessions = [
        s
        for s in service.store.list_sessions(service.user_id)
        if s.ended_at is not None and in_week(s.started_at) and s.lesson_id in known
    ]
    per_lesson: dict[str, int] = {}
    for s in sessions:
        per_lesson[s.lesson_id] = per_lesson.get(s.lesson_id, 0) + s.elapsed_seconds()
        if s.note:
            report.notes.append(NoteLine(_local_day(s.started_at, tz), s.lesson_id, s.note))
    report.session_count = len(sessions)
    report.total_seconds = sum(per_lesson.values())
    report.active_days = len({_local_day(s.started_at, tz) for s in sessions})

    per_module: dict[str, ModuleTime] = {}
    for summary in summaries:
        lesson, module, progress = summary.lesson, summary.module, summary.progress
        lesson_title = lesson.localized(chosen).title
        module_title = module.localized(chosen).title
        seconds = per_lesson.get(lesson.id, 0)
        if seconds:
            prev = per_module.get(module.id, ModuleTime(module.id, module_title, 0))
            per_module[module.id] = ModuleTime(module.id, module_title, prev.seconds + seconds)
        line = LessonLine(lesson.id, lesson_title, seconds, progress.understanding)

        if progress.status is LessonStatus.DONE and in_week(progress.completed_at):
            report.completed.append(line)
            if progress.note and progress.completed_at is not None:
                day = _local_day(progress.completed_at, tz)
                report.notes.append(NoteLine(day, lesson.id, progress.note))
        elif progress.status is LessonStatus.IN_PROGRESS:
            report.in_progress.append(line)

        reasons: list[str] = []
        if progress.status is LessonStatus.IN_PROGRESS and progress.started_at is not None:
            days = (as_of - _local_day(progress.started_at, tz)).days
            if days > STUCK_DAYS:
                reasons.append(t("report.stuck.days", days=days))
        if progress.understanding is not None and progress.understanding <= LOW_UNDERSTANDING:
            reasons.append(t("report.stuck.understanding", value=progress.understanding))
        if reasons:
            report.stuck.append(
                LessonLine(
                    lesson.id, lesson_title, seconds, progress.understanding, ", ".join(reasons)
                )
            )

    report.module_time = sorted(per_module.values(), key=lambda m: -m.seconds)
    report.quiz = _quiz_stats(service, in_week)
    for card_id, again in _again_counts(service, in_week).items():
        if again >= STUCK_AGAIN:
            card = service.store.get_card(card_id, service.user_id)
            title = card.front.splitlines()[0] if card else card_id
            lesson_id = card.lesson_id if card else "?"
            detail = t("report.stuck.again_cards", count=again)
            report.stuck.append(LessonLine(lesson_id, title, detail=detail))
    for nxt in service.next_lessons(limit=NEXT_COUNT):
        state = t(
            "report.state.in_progress"
            if nxt.status is LessonStatus.IN_PROGRESS
            else "report.state.not_started"
        )
        detail = t("report.next_detail", state=state, minutes=nxt.lesson.estimated_minutes)
        title = nxt.lesson.localized(chosen).title
        report.next_lessons.append(LessonLine(nxt.lesson.id, title, detail=detail))
    report.notes.sort(key=lambda n: n.day)
    return report


def _quiz_stats(service: ProgressService, in_week: Callable[[datetime | None], bool]) -> QuizStats:
    attempts = [
        a for a in service.store.list_quiz_attempts(service.user_id) if in_week(a.answered_at)
    ]
    runs = [r for r in service.store.list_quiz_runs(service.user_id) if in_week(r.finished_at)]
    reviews = [r for r in service.store.list_reviews(service.user_id) if in_week(r.reviewed_at)]
    order = ("again", "hard", "good", "easy")
    counts = tuple(sum(1 for r in reviews if r.rating == name) for name in order)
    return QuizStats(
        attempts=len(attempts),
        correct=sum(1 for a in attempts if a.correct),
        runs=len(runs),
        reviews=len(reviews),
        rating_counts=(counts[0], counts[1], counts[2], counts[3]),
    )


def _again_counts(
    service: ProgressService, in_week: Callable[[datetime | None], bool]
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for review in service.store.list_reviews(service.user_id):
        if review.rating == "again" and in_week(review.reviewed_at):
            counts[review.card_id] = counts.get(review.card_id, 0) + 1
    return counts


def format_duration(seconds: int) -> str:
    """``0`` -> ``"0m"``, ``2700`` -> ``"45m"``, ``12000`` -> ``"3h 20m"``."""
    minutes = round(seconds / 60)
    if minutes < 60:
        return f"{minutes}m"
    return f"{minutes // 60}h {minutes % 60:02d}m"


def md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    """Markdown table lines (pipes in cells are escaped)."""
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |" for row in rows]
    return out


def _score(value: int | None) -> str:
    return f"{value}/5" if value is not None else "-"


def _name(line: LessonLine) -> str:
    return f"{line.title} (`{line.lesson_id}`)"


def render_weekly(report: WeeklyReport, lang: str | None = None) -> str:
    """Markdown for a :class:`WeeklyReport` (pure function).

    ``lang`` defaults to the language the report was built in, so the headings cannot end
    up in a different language from the titles and details inside it.
    """
    t = _t(lang or report.lang)
    w = report.week
    lines = [
        f"# {t('report.weekly.title', week=w)}",
        "",
        t(
            "report.weekly.period",
            start=f"{w.monday:%Y-%m-%d}",
            end=f"{w.sunday:%Y-%m-%d}",
            as_of=f"{report.as_of:%Y-%m-%d}",
        ),
        "",
        f"## {t('report.weekly.summary')}",
        "",
        t("report.weekly.study_time", time=format_duration(report.total_seconds)),
        t("report.weekly.sessions", count=report.session_count, days=report.active_days),
        t("report.weekly.completed_count", count=len(report.completed)),
        t("report.weekly.in_progress_count", count=len(report.in_progress)),
        "",
        f"## {t('report.weekly.module_time')}",
        "",
    ]
    if report.module_time:
        rows = [
            [f"{m.title} (`{m.module_id}`)", format_duration(m.seconds)] for m in report.module_time
        ]
        lines += md_table([t("report.weekly.col_module"), t("report.weekly.col_time")], rows)
    else:
        lines.append(t("report.weekly.no_records"))

    lines += ["", f"## {t('report.weekly.completed')}", ""]
    if report.completed:
        rows = [
            [_name(c), format_duration(c.seconds_this_week), _score(c.understanding)]
            for c in report.completed
        ]
        headers = [
            t("report.weekly.col_lesson"),
            t("report.weekly.col_week_time"),
            t("report.weekly.col_understanding"),
        ]
        lines += md_table(headers, rows)
    else:
        lines.append(t("report.weekly.no_completed"))

    lines += ["", f"## {t('report.weekly.in_progress')}", ""]
    if report.in_progress:
        lines += [
            t(
                "report.weekly.in_progress_line",
                lesson=_name(p),
                time=format_duration(p.seconds_this_week),
            )
            for p in report.in_progress
        ]
    else:
        lines.append(t("report.weekly.none"))

    quiz = report.quiz
    if quiz.attempts:
        quiz_line = t(
            "report.weekly.quiz_rate",
            percent=quiz.percent,
            correct=quiz.correct,
            attempts=quiz.attempts,
            runs=quiz.runs,
        )
    else:
        quiz_line = t("report.weekly.quiz_rate_none")
    if quiz.reviews:
        again, hard, good, easy = quiz.rating_counts
        ratings = f"again {again} \u00b7 hard {hard} \u00b7 good {good} \u00b7 easy {easy}"
        review_line = t("report.weekly.cards", count=quiz.reviews, ratings=ratings)
    else:
        review_line = t("report.weekly.cards_none")
    lines += [
        "",
        f"## {t('report.weekly.quiz_review')}",
        "",
        quiz_line,
        review_line,
        "",
        f"## {t('report.weekly.notes')}",
        "",
    ]
    if report.notes:
        lines += [
            t("report.weekly.note_line", day=f"{n.day:%m-%d}", lesson_id=n.lesson_id, text=n.text)
            for n in report.notes
        ]
    else:
        lines.append(t("report.weekly.no_notes"))

    lines += ["", f"## {t('report.weekly.stuck')}", ""]
    if report.stuck:
        lines += [
            t("report.weekly.stuck_line", lesson=_name(s), detail=s.detail) for s in report.stuck
        ]
    else:
        lines.append(t("report.weekly.none"))

    lines += ["", f"## {t('report.weekly.next')}", ""]
    if report.next_lessons:
        lines += [
            t("report.weekly.next_line", number=i, lesson=_name(n), detail=n.detail)
            for i, n in enumerate(report.next_lessons, 1)
        ]
        lines += ["", t("report.weekly.start_hint", lesson_id=report.next_lessons[0].lesson_id)]
    else:
        lines.append(t("report.weekly.all_done"))
    return "\n".join(lines) + "\n"

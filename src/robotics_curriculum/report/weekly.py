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


@dataclass(slots=True)
class WeeklyReport:
    week: IsoWeek
    as_of: date
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
) -> WeeklyReport:
    """Collect one ISO week of progress. ``tz=None`` means the system local timezone.

    The stuck check is judged as of ``min(today, week's Sunday)``: a past week as of its
    Sunday, the current week as of today. "Next" lessons reflect the current state.
    """
    as_of = min(today, week.sunday)
    report = WeeklyReport(week=week, as_of=as_of)
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
        seconds = per_lesson.get(lesson.id, 0)
        if seconds:
            prev = per_module.get(module.id, ModuleTime(module.id, module.title, 0))
            per_module[module.id] = ModuleTime(module.id, module.title, prev.seconds + seconds)
        line = LessonLine(lesson.id, lesson.title, seconds, progress.understanding)

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
                reasons.append(f"{days}일째 진행 중")
        if progress.understanding is not None and progress.understanding <= LOW_UNDERSTANDING:
            reasons.append(f"이해도 {progress.understanding}/5")
        if reasons:
            report.stuck.append(
                LessonLine(
                    lesson.id, lesson.title, seconds, progress.understanding, ", ".join(reasons)
                )
            )

    report.module_time = sorted(per_module.values(), key=lambda m: -m.seconds)
    report.quiz = _quiz_stats(service, in_week)
    for card_id, again in _again_counts(service, in_week).items():
        if again >= STUCK_AGAIN:
            card = service.store.get_card(card_id, service.user_id)
            title = card.front.splitlines()[0] if card else card_id
            lesson_id = card.lesson_id if card else "?"
            report.stuck.append(LessonLine(lesson_id, title, detail=f"복습 카드 again {again}회"))
    for nxt in service.next_lessons(limit=NEXT_COUNT):
        state = "진행 중" if nxt.status is LessonStatus.IN_PROGRESS else "시작 전"
        detail = f"{state}, 예상 {nxt.lesson.estimated_minutes}분"
        report.next_lessons.append(LessonLine(nxt.lesson.id, nxt.lesson.title, detail=detail))
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


def render_weekly(report: WeeklyReport) -> str:
    """Markdown for a :class:`WeeklyReport` (pure function)."""
    w = report.week
    lines = [
        f"# 주간 리포트 {w}",
        "",
        f"기간: {w.monday:%Y-%m-%d} ~ {w.sunday:%Y-%m-%d} (기준일 {report.as_of:%Y-%m-%d})",
        "",
        "## 요약",
        "",
        f"- 학습 시간: {format_duration(report.total_seconds)}",
        f"- 세션: {report.session_count}회 (학습한 날 {report.active_days}일)",
        f"- 완료한 레슨: {len(report.completed)}개",
        f"- 진행 중인 레슨: {len(report.in_progress)}개",
        "",
        "## 모듈별 학습 시간",
        "",
    ]
    if report.module_time:
        rows = [
            [f"{m.title} (`{m.module_id}`)", format_duration(m.seconds)] for m in report.module_time
        ]
        lines += md_table(["모듈", "시간"], rows)
    else:
        lines.append("이번 주 학습 기록이 없습니다.")

    lines += ["", "## 완료한 레슨", ""]
    if report.completed:
        rows = [
            [_name(c), format_duration(c.seconds_this_week), _score(c.understanding)]
            for c in report.completed
        ]
        lines += md_table(["레슨", "이번 주 시간", "이해도"], rows)
    else:
        lines.append("이번 주 완료한 레슨이 없습니다.")

    lines += ["", "## 진행 중인 레슨", ""]
    if report.in_progress:
        lines += [
            f"- {_name(p)}: 이번 주 {format_duration(p.seconds_this_week)}"
            for p in report.in_progress
        ]
    else:
        lines.append("없음")

    quiz = report.quiz
    if quiz.attempts:
        detail = f"{quiz.correct}/{quiz.attempts} 문항, {quiz.runs}회 응시"
        quiz_line = f"- 퀴즈 정답률: {quiz.percent}% ({detail})"
    else:
        quiz_line = "- 퀴즈 정답률: 기록 없음"
    if quiz.reviews:
        again, hard, good, easy = quiz.rating_counts
        ratings = f"again {again} · hard {hard} · good {good} · easy {easy}"
        review_line = f"- 복습 카드: {quiz.reviews}장 ({ratings})"
    else:
        review_line = "- 복습 카드: 기록 없음"
    lines += ["", "## 퀴즈·복습", "", quiz_line, review_line, "", "## 메모 요약", ""]
    if report.notes:
        lines += [f"- {n.day:%m-%d} `{n.lesson_id}`: {n.text}" for n in report.notes]
    else:
        lines.append("이번 주 메모가 없습니다.")

    lines += ["", "## 막힌 지점", ""]
    if report.stuck:
        lines += [f"- {_name(s)}: {s.detail}" for s in report.stuck]
    else:
        lines.append("없음")

    lines += ["", "## 다음 주 제안", ""]
    if report.next_lessons:
        lines += [f"{i}. {_name(n)}: {n.detail}" for i, n in enumerate(report.next_lessons, 1)]
        lines += ["", f"시작: `rc start {report.next_lessons[0].lesson_id}`"]
    else:
        lines.append("모든 레슨을 완료했습니다.")
    return "\n".join(lines) + "\n"

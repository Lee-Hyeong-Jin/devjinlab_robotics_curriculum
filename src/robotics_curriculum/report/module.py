"""Per-module report (FR-7.2): ``rc report module <module_id>``.

Lesson table (status, time, understanding, completion date) plus the understanding
distribution. Lab results are not tracked in Phase 1, so they are not shown.
"""

from __future__ import annotations

from dataclasses import dataclass

from robotics_curriculum.progress import LessonSummary, ProgressError, ProgressService
from robotics_curriculum.report.weekly import format_duration, md_table

_STATUS = {"done": "완료", "in_progress": "진행 중", "not_started": "시작 전"}


@dataclass(frozen=True, slots=True)
class ModuleReport:
    course_title: str
    module_id: str
    module_title: str
    lessons: list[LessonSummary]

    @property
    def done_count(self) -> int:
        return sum(1 for s in self.lessons if s.status == "done")

    @property
    def total_seconds(self) -> int:
        return sum(s.progress.total_seconds for s in self.lessons)


def build_module_report(service: ProgressService, module_id: str) -> ModuleReport:
    lessons = [s for s in service.status() if s.module.id == module_id]
    if not lessons:
        raise ProgressError(f"unknown module '{module_id}'")
    first = lessons[0]
    return ModuleReport(first.course.title, module_id, first.module.title, lessons)


def render_module(report: ModuleReport) -> str:
    """Markdown for a :class:`ModuleReport` (pure function)."""
    n = len(report.lessons)
    pct = round(100 * report.done_count / n) if n else 0
    lines = [
        f"# 모듈 리포트: {report.module_title} (`{report.module_id}`)",
        "",
        f"- 코스: {report.course_title}",
        f"- 진도: {report.done_count}/{n} 레슨 ({pct}%)",
        f"- 누적 학습 시간: {format_duration(report.total_seconds)}",
        "",
        "## 레슨",
        "",
    ]
    rows = []
    for s in report.lessons:
        status = "잠김" if s.status == "not_started" and s.locked else _STATUS[s.status.value]
        p = s.progress
        rows.append(
            [
                f"{s.lesson.title} (`{s.lesson.id}`)",
                status,
                format_duration(p.total_seconds),
                f"{p.understanding}/5" if p.understanding else "-",
                f"{p.completed_at:%Y-%m-%d}" if p.completed_at else "-",
            ]
        )
    lines += md_table(["레슨", "상태", "시간", "이해도", "완료일"], rows)
    lines += ["", "## 이해도 분포", ""]
    scores = [s.progress.understanding for s in report.lessons if s.progress.understanding]
    if scores:
        lines += [f"- {k}점: {scores.count(k)}개" for k in range(5, 0, -1)]
    else:
        lines.append("아직 이해도 기록이 없습니다.")
    return "\n".join(lines) + "\n"

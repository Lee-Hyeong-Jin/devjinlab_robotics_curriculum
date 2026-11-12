"""Per-module report (FR-7.2): ``rc report module <module_id>``.

Lesson table (status, time, understanding, completion date) plus the understanding
distribution. Lab results are not tracked in Phase 1, so they are not shown.
"""

from __future__ import annotations

from dataclasses import dataclass

from robotics_curriculum.i18n import DEFAULT_LANG, normalize_lang, translator
from robotics_curriculum.progress import LessonSummary, ProgressError, ProgressService
from robotics_curriculum.report.weekly import format_duration, md_table


@dataclass(frozen=True, slots=True)
class ModuleReport:
    course_title: str
    module_id: str
    module_title: str
    lessons: list[LessonSummary]
    lang: str = DEFAULT_LANG
    """Language the course and module titles were built in."""

    @property
    def done_count(self) -> int:
        return sum(1 for s in self.lessons if s.status == "done")

    @property
    def total_seconds(self) -> int:
        return sum(s.progress.total_seconds for s in self.lessons)


def build_module_report(
    service: ProgressService, module_id: str, lang: str | None = None
) -> ModuleReport:
    """One module's lessons with their progress, with every title in ``lang``."""
    lessons = [s for s in service.status() if s.module.id == module_id]
    if not lessons:
        raise ProgressError(f"unknown module '{module_id}'")
    first = lessons[0]
    chosen = normalize_lang(lang) or DEFAULT_LANG
    return ModuleReport(
        first.course.localized(chosen).title,
        module_id,
        first.module.localized(chosen).title,
        lessons,
        chosen,
    )


def render_module(report: ModuleReport, lang: str | None = None) -> str:
    """Markdown for a :class:`ModuleReport` (pure function)."""
    t = translator(normalize_lang(lang or report.lang) or DEFAULT_LANG)
    n = len(report.lessons)
    pct = round(100 * report.done_count / n) if n else 0
    lines = [
        f"# {t('report.module.title', title=report.module_title, module_id=report.module_id)}",
        "",
        t("report.module.course", title=report.course_title),
        t("report.module.progress", done=report.done_count, total=n, percent=pct),
        t("report.module.total_time", time=format_duration(report.total_seconds)),
        "",
        f"## {t('report.module.lessons')}",
        "",
    ]
    rows = []
    for s in report.lessons:
        if s.status == "not_started" and s.locked:
            status = t("report.state.locked")
        else:
            status = t(f"report.state.{s.status.value}")
        p = s.progress
        rows.append(
            [
                f"{s.lesson.localized(report.lang).title} (`{s.lesson.id}`)",
                status,
                format_duration(p.total_seconds),
                f"{p.understanding}/5" if p.understanding else "-",
                f"{p.completed_at:%Y-%m-%d}" if p.completed_at else "-",
            ]
        )
    headers = [
        t("report.module.col_lesson"),
        t("report.module.col_state"),
        t("report.module.col_time"),
        t("report.module.col_understanding"),
        t("report.module.col_completed"),
    ]
    lines += md_table(headers, rows)
    lines += ["", f"## {t('report.module.understanding')}", ""]
    scores = [s.progress.understanding for s in report.lessons if s.progress.understanding]
    if scores:
        lines += [
            t("report.module.understanding_line", score=k, count=scores.count(k))
            for k in range(5, 0, -1)
        ]
    else:
        lines.append(t("report.module.no_understanding"))
    return "\n".join(lines) + "\n"

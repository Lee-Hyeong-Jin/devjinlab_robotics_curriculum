"""Markdown page renderers for the static site (platform-design 2.2-2.3).

Every function returns the Markdown text of one page. Links are relative ``.md`` paths
so that MkDocs resolves (and checks) them. Nothing here touches the filesystem.
"""

from __future__ import annotations

import html
import posixpath
import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import datetime

from robotics_curriculum.content import (
    Course,
    Lesson,
    LocalizedCourse,
    LocalizedLesson,
    LocalizedModule,
    Module,
    Resource,
    ResourceKind,
)
from robotics_curriculum.content.papers import citation, paper_index, resolve_lesson_papers
from robotics_curriculum.content.quiz_block import (
    QUIZ_FENCE,
    QuizParseError,
    QuizQuestion,
    localized_quiz,
)
from robotics_curriculum.content.sections import study_guide_headings
from robotics_curriculum.content.validate import is_http_url
from robotics_curriculum.i18n import DEFAULT_LANG, Translator, resolve_lang, translator
from robotics_curriculum.progress import LessonProgress, LessonStatus, LessonSummary, Session
from robotics_curriculum.site.stats import (
    Ratio,
    activity_days,
    format_minutes,
    format_seconds,
    ordered_stages,
    ratio,
    stage_label,
    stage_of,
    streak,
    week_stats,
)

INDEX_PAGE = "index.md"
ROADMAP_PAGE = "roadmap.md"
RESOURCES_PAGE = "resources.md"
STUDY_ANCHOR = "study-method"
RESOURCES_ANCHOR = "resources"
PAPERS_ANCHOR = "papers"

# state key -> symbol; the words come from the message catalogue
STATE_SYMBOLS: dict[str, str] = {
    "done": "■",
    "in_progress": "▣",
    "not_started": "□",
}

# resource kinds in display order; ``None`` shares the "other" label
KIND_KEYS: tuple[tuple[ResourceKind | None, str], ...] = (
    (ResourceKind.BOOK, "book"),
    (ResourceKind.COURSE, "course"),
    (ResourceKind.VIDEO, "video"),
    (ResourceKind.ARTICLE, "article"),
    (ResourceKind.PAPER, "paper"),
    (ResourceKind.DATASET, "dataset"),
    (ResourceKind.CODE, "code"),
    (ResourceKind.NOTES, "notes"),
    (ResourceKind.OTHER, "other"),
    (None, "other"),
)


def state_label(state: str, t: Translator) -> str:
    return t(f"site.state.{state}")


def kind_label(kind: ResourceKind | None, t: Translator) -> str:
    """Display name of a resource kind (``교재`` / ``Books``)."""
    key = next((name for k, name in KIND_KEYS if k == kind), "other")
    return t(f"resource.kind.{key}")


def activity_label(kind: str, t: Translator) -> str:
    label = t(f"site.activity.{kind}")
    return kind if label == f"site.activity.{kind}" else label


def stage_text(stage: str, t: Translator) -> str:
    """Display name of a stage. The stored value is an id; the label is translated."""
    return stage_label(stage, t.lang)


# -- small Markdown helpers ----------------------------------------------------


def esc_text(text: str) -> str:
    """Escape characters that would break link text or table cells."""
    return text.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]").replace("|", "\\|")


def md_text(text: str) -> str:
    """Escape content for a Markdown page: HTML first, then Markdown metacharacters.

    Front matter is untrusted (it arrives through pull requests) and Python-Markdown
    passes raw HTML through, so every content string embedded in a page goes through
    here (AC-SEC.1). :func:`robotics_curriculum.site.sanitize.clean` is the second line
    of defence, for raw HTML inside lesson bodies.
    """
    return esc_text(html.escape(text, quote=False))


def link(from_page: str, to_page: str, text: str, anchor: str = "") -> str:
    rel = posixpath.relpath(to_page, posixpath.dirname(from_page) or ".")
    return f"[{md_text(text)}]({rel}{'#' + anchor if anchor else ''})"


def state_of(summary: LessonSummary) -> str:
    if summary.status is LessonStatus.DONE:
        return "done"
    if summary.status is LessonStatus.IN_PROGRESS:
        return "in_progress"
    return "not_started"


def badge(state: str, t: Translator) -> str:
    label = html.escape(state_label(state, t))
    return f'<span class="rc-status rc-{state}">{STATE_SYMBOLS[state]} {label}</span>'


def bar(r: Ratio) -> str:
    """A progress bar. The width comes from a class, so no attribute carries CSS."""
    step = 5 * round(r.percent / 5)
    return (
        f'<span class="rc-bar" title="{r.percent}%"><span class="rc-fill rc-w-{step}">'
        f'</span></span> <span class="rc-pct">{r.percent}% ({r.done}/{r.total})</span>'
    )


def difficulty_dots(level: int) -> str:
    return "●" * level + "○" * (5 - level)


def legend(t: Translator) -> str:
    return " · ".join(
        f"{symbol} {md_text(state_label(state, t))}" for state, symbol in STATE_SYMBOLS.items()
    )


# -- body processing -----------------------------------------------------------

_FENCE = re.compile(r"^\s*(```|~~~)")
_H1_OR_H2 = re.compile(r"^#{1,2}\s")


def split_study_section(body: str, lang: str | None = None) -> tuple[str, str | None]:
    """Remove the study-guide section from ``body``; return (rest, section text).

    The heading is looked up in ``lang`` first (a translated body writes it in its own
    language) and then in the language lessons are written in.
    """
    headings = [h.strip().rstrip("#").strip() for h in study_guide_headings(lang)]
    lines = body.split("\n")
    in_fence = False
    start = end = None
    for index, line in enumerate(lines):
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if (
            start is None
            and line.startswith("## ")
            and line[3:].strip().rstrip("#").strip() in headings
        ):
            start = index
        elif start is not None and _H1_OR_H2.match(line):
            end = index
            break
    if start is None:
        return body, None
    end = len(lines) if end is None else end
    section = "\n".join(lines[start + 1 : end]).strip("\n")
    rest = "\n".join(lines[:start] + lines[end:])
    return rest, section


def strip_leading_h1(body: str) -> str:
    """Drop the body's first line if it is an H1 (the page header already shows the title)."""
    lines = body.lstrip("\n").split("\n")
    if lines and re.match(r"^#\s", lines[0]):
        return "\n".join(lines[1:]).lstrip("\n")
    return body


def indent(text: str, prefix: str = "    ") -> str:
    return "\n".join(prefix + line if line.strip() else "" for line in text.split("\n"))


# -- site model ----------------------------------------------------------------


@dataclass
class SiteModel:
    """Everything the pages need, computed once from content + progress."""

    courses: list[Course]
    summaries: list[LessonSummary]
    next_lessons: list[LessonSummary]
    sessions: list[Session]
    now: datetime
    due_today: int = 0
    lang: str = DEFAULT_LANG
    t: Translator = field(init=False)
    by_lesson: dict[str, LessonSummary] = field(init=False)
    module_keys: dict[int, str] = field(init=False)
    #: Lesson id -> its course, so a page can reach that course's paper registry.
    course_by_lesson: dict[str, Course] = field(init=False)

    def __post_init__(self) -> None:
        self.t = translator(resolve_lang(self.lang))
        self.by_lesson = {s.lesson.id: s for s in self.summaries}
        self.course_by_lesson = {
            lesson.id: course for course in self.courses for lesson in course.iter_lessons()
        }
        counts: dict[str, int] = {}
        for course in self.courses:
            for module in course.modules:
                counts[module.id] = counts.get(module.id, 0) + 1
        self.module_keys = {}
        for course in self.courses:
            for module in course.modules:
                key = module.id if counts[module.id] == 1 else f"{course.id}-{module.id}"
                self.module_keys[id(module)] = key

    @property
    def title(self) -> str:
        if len(self.courses) == 1:
            return self.courses[0].localized(self.lang).title
        return self.t("site.title_fallback")

    @property
    def description(self) -> str:
        """Site description: the single course's summary, else empty."""
        if len(self.courses) == 1:
            return self.courses[0].localized(self.lang).summary
        return ""

    def course_of(self, lesson: Lesson) -> Course:
        """The course a lesson belongs to; the first course as a fallback (single-course site)."""
        found = self.course_by_lesson.get(lesson.id)
        return found if found is not None else self.courses[0]

    def modules(self) -> list[Module]:
        return [m for c in self.courses for m in c.modules]

    def module_page(self, module: Module) -> str:
        return f"modules/{self.module_keys[id(module)]}/index.md"

    def lesson_page(self, lesson: Lesson) -> str:
        module = self.by_lesson[lesson.id].module
        return f"modules/{self.module_keys[id(module)]}/{lesson.id}.md"

    def module_summaries(self, module: Module) -> list[LessonSummary]:
        return [s for s in self.summaries if s.module is module]

    def stage_summaries(self, stage: str) -> list[LessonSummary]:
        return [s for s in self.summaries if stage_of(s.module) == stage]

    def stages(self) -> list[str]:
        return ordered_stages(stage_of(m) for m in self.modules())

    def text(self, lesson: Lesson) -> LocalizedLesson:
        """A lesson's title, summary, objectives, body, activities and resources."""
        return lesson.localized(self.lang)

    def module_text(self, module: Module) -> LocalizedModule:
        """A module's title and summary in the site's language."""
        return module.localized(self.lang)

    def course_text(self, course: Course) -> LocalizedCourse:
        """A course's title and summary in the site's language."""
        return course.localized(self.lang)

    def progress_rows(self) -> list[LessonProgress]:
        return [s.progress for s in self.summaries]


def lesson_link(model: SiteModel, page: str, lesson: Lesson, anchor: str = "") -> str:
    return link(page, model.lesson_page(lesson), model.text(lesson).title, anchor)


def module_link(model: SiteModel, page: str, module: Module) -> str:
    return link(page, model.module_page(module), model.module_text(module).title)


def _local(dt: datetime, now: datetime) -> datetime:
    return dt.astimezone(now.tzinfo)


# -- 대시보드 -------------------------------------------------------------------


def current_lesson(model: SiteModel) -> LessonSummary | None:
    """In-progress lesson if any, else the first recommended next lesson (design 4.3)."""
    for summary in model.summaries:
        if summary.status is LessonStatus.IN_PROGRESS:
            return summary
    return model.next_lessons[0] if model.next_lessons else None


def render_dashboard(model: SiteModel) -> str:
    page = INDEX_PAGE
    now = model.now
    t = model.t
    # `site.built` is the one catalogue entry rendered as HTML (it carries a <code> tag).
    out = [
        f"# {md_text(model.title)}",
        "",
        f'<p class="rc-built">{t("site.built", at=f"{now:%Y-%m-%d %H:%M}")}</p>',
        "",
        f"## {md_text(t('site.heading.position'))}",
        "",
    ]
    current = current_lesson(model)
    if current is None:
        out.append(md_text(t("site.dashboard.all_done")))
    else:
        module_ratio = ratio(model.module_summaries(current.module))
        progress = t(
            "site.dashboard.module_progress", done=module_ratio.done, total=module_ratio.total
        )
        stage = md_text(stage_text(stage_of(current.module), t))
        guide = link(
            page,
            model.lesson_page(current.lesson),
            t("site.dashboard.study_guide_link"),
            STUDY_ANCHOR,
        )
        out += [
            f"- **{md_text(t('site.label.stage'))}**: {stage}",
            f"- **{md_text(t('site.label.module'))}**: "
            f"{module_link(model, page, current.module)} {md_text(progress)}",
            f"- **{md_text(t('site.label.next_lesson'))}**: "
            f"{lesson_link(model, page, current.lesson)} "
            f"{badge(state_of(current), t)} · ⏱ "
            f"{format_minutes(current.lesson.estimated_minutes, model.lang)}",
            f"- {guide} · {t('site.dashboard.start_hint', lesson_id=current.lesson.id)}",
        ]
    out += [
        "",
        f"## {md_text(t('site.heading.overview'))}",
        "",
        _cards(model),
        "",
        f"## {md_text(t('site.heading.stage_progress'))}",
        "",
    ]
    out.append(_stage_table(model, page))
    out += ["", f"## {md_text(t('site.heading.next_lessons'))}", ""]
    if model.next_lessons:
        for summary in model.next_lessons[:5]:
            lesson = summary.lesson
            out.append(
                f"1. {lesson_link(model, page, lesson)} {badge(state_of(summary), t)} · "
                f"{md_text(model.module_text(summary.module).title)} · ⏱ "
                f"{format_minutes(lesson.estimated_minutes, model.lang)}"
            )
    else:
        out.append(md_text(t("site.dashboard.nothing_available")))
    out += ["", f"## {md_text(t('site.heading.recent'))}", ""]
    out += _recent_activity(model, page) or [t("site.dashboard.no_activity")]
    return "\n".join(out) + "\n"


def _cards(model: SiteModel) -> str:
    week = week_stats(model.sessions, model.now)
    days = activity_days(model.sessions, model.progress_rows(), model.now)
    total = ratio(model.summaries)
    t = model.t
    cards = [
        (
            t("site.card.week_time"),
            format_seconds(week.seconds, model.lang),
            t("site.card.week_time_sub", sessions=week.sessions, start=f"{week.start:%m/%d}"),
        ),
        (
            t("site.card.streak"),
            t("site.card.streak_value", days=streak(days, model.now.date())),
            t("site.card.streak_sub"),
        ),
        (
            t("site.card.lessons_done"),
            f"{total.done} / {total.total}",
            t("site.card.lessons_done_sub", percent=total.percent),
        ),
        (
            t("site.card.due"),
            t("site.card.due_value", count=model.due_today),
            t("site.card.due_sub"),
        ),
    ]
    parts = ['<div class="rc-cards">']
    for title, value, sub in cards:
        parts.append(
            f'<div class="rc-card"><div class="rc-card-title">{html.escape(title)}</div>'
            f'<div class="rc-card-value">{html.escape(value)}</div>'
            f'<div class="rc-card-sub">{html.escape(sub)}</div></div>'
        )
    parts.append("</div>")
    return "\n".join(parts)


def _stage_table(model: SiteModel, page: str) -> str:
    t = model.t
    header = (
        f"| {md_text(t('site.label.stage'))} | {md_text(t('site.label.progress'))} "
        f"| {md_text(t('site.label.modules'))} |"
    )
    rows = [header, "|---|---|---|"]
    for stage in model.stages():
        summaries = model.stage_summaries(stage)
        modules = [m for m in model.modules() if stage_of(m) == stage]
        if not modules:
            rows.append(
                f"| {md_text(stage_text(stage, t))} | — | "
                f"{md_text(t('site.dashboard.stage_empty'))} |"
            )
            continue
        module_cells = " · ".join(
            f"{module_link(model, page, m)} {ratio(model.module_summaries(m)).percent}%"
            for m in modules
        )
        label = md_text(stage_text(stage, t))
        rows.append(f"| **{label}** | {bar(ratio(summaries))} | {module_cells} |")
    return "\n".join(rows)


def _recent_activity(model: SiteModel, page: str, limit: int = 5) -> list[str]:
    events: list[tuple[datetime, str]] = []
    for session in model.sessions:
        summary = model.by_lesson.get(session.lesson_id)
        if summary is None:
            continue
        t = model.t
        kind = t(
            "site.recent.kind_timer" if session.source == "timer" else "site.recent.kind_manual"
        )
        length = (
            t("site.recent.session_open")
            if session.is_open
            else format_seconds(session.elapsed_seconds(model.now), model.lang)
        )
        events.append(
            (
                session.started_at,
                t(
                    "site.recent.session",
                    lesson=lesson_link(model, page, summary.lesson),
                    length=md_text(length),
                    kind=md_text(kind),
                ),
            )
        )
    for summary in model.summaries:
        done_at = summary.progress.completed_at
        if summary.status is LessonStatus.DONE and done_at is not None:
            extra = (
                model.t("site.recent.done_understanding", value=summary.progress.understanding)
                if summary.progress.understanding
                else ""
            )
            events.append(
                (
                    done_at,
                    model.t(
                        "site.recent.done",
                        lesson=lesson_link(model, page, summary.lesson),
                        extra=md_text(extra),
                    ),
                )
            )
    events.sort(key=lambda e: e[0], reverse=True)
    return [f"- {_local(when, model.now):%m/%d} · {text}" for when, text in events[:limit]]


# -- 로드맵 ---------------------------------------------------------------------


def render_roadmap(model: SiteModel) -> str:
    page = ROADMAP_PAGE
    t = model.t
    out = [
        f"# {md_text(t('site.heading.roadmap_page'))}",
        "",
        t("site.roadmap.intro", legend=legend(t)),
        "",
    ]
    for stage in model.stages():
        summaries = model.stage_summaries(stage)
        modules = [m for m in model.modules() if stage_of(m) == stage]
        out += [f"## {md_text(stage_text(stage, t))}", ""]
        if not modules:
            out += [md_text(t("site.roadmap.stage_empty")), ""]
            continue
        out += [bar(ratio(summaries)), ""]
        for module in modules:
            module_ratio = ratio(model.module_summaries(module))
            out += [
                f"### {module_link(model, page, module)}",
                "",
                f"{md_text(model.module_text(module).summary)}",
                "",
                bar(module_ratio),
                "",
            ]
            for summary in model.module_summaries(module):
                lesson = summary.lesson
                prereq = ""
                if lesson.prerequisites:
                    names = ", ".join(
                        md_text(model.text(model.by_lesson[p].lesson).title)
                        for p in lesson.prerequisites
                        if p in model.by_lesson
                    )
                    prereq = t("site.roadmap.prereq", names=names)
                out.append(
                    f"- {badge(state_of(summary), t)} {lesson_link(model, page, lesson)} · "
                    f"⏱ {format_minutes(lesson.estimated_minutes, model.lang)}{prereq}"
                )
            out.append("")
    return "\n".join(out) + "\n"


# -- 모듈 페이지 -----------------------------------------------------------------


def render_module(model: SiteModel, module: Module) -> str:
    page = model.module_page(module)
    summaries = model.module_summaries(module)
    total_minutes = sum(s.lesson.estimated_minutes for s in summaries)
    t = model.t
    meta = t(
        "site.module.meta",
        stage_label=md_text(t("site.label.stage")),
        stage=md_text(stage_text(stage_of(module), t)),
        lessons_label=md_text(t("site.label.lessons")),
        count=len(summaries),
        time_label=md_text(t("site.label.estimated_time")),
        time=format_minutes(total_minutes, model.lang),
        back=link(page, ROADMAP_PAGE, t("site.module.back_to_roadmap")),
    )
    headers = " | ".join(
        md_text(t(key))
        for key in (
            "site.label.index",
            "site.label.lessons",
            "site.label.state",
            "site.label.estimated_time",
            "site.label.difficulty",
            "site.label.prerequisites",
        )
    )
    module_text = model.module_text(module)
    out = [
        f"# {md_text(module_text.title)}",
        "",
        meta,
        "",
        md_text(module_text.summary),
        "",
        bar(ratio(summaries)),
        "",
        f"## {md_text(t('site.heading.lessons'))}",
        "",
        f"| {headers} |",
        "|---|---|---|---|---|---|",
    ]
    for number, summary in enumerate(summaries, 1):
        lesson = summary.lesson
        prereqs = ", ".join(
            f"{lesson_link(model, page, model.by_lesson[p].lesson)} "
            f"({md_text(state_label(state_of(model.by_lesson[p]), t))})"
            for p in lesson.prerequisites
            if p in model.by_lesson
        )
        out.append(
            f"| {number} | {lesson_link(model, page, lesson)} | {badge(state_of(summary), t)} | "
            f"{format_minutes(lesson.estimated_minutes, model.lang)} | "
            f"{difficulty_dots(lesson.difficulty)} | "
            f"{prereqs or md_text(t('site.label.none'))} |"
        )
    resources = _collect_resources(summaries, model.lang)
    if resources:
        out += ["", f"## {md_text(t('site.heading.module_resources'))}", ""]
        out += _resource_groups(model, page, resources, show_lessons=True)
    return "\n".join(out) + "\n"


# -- 레슨 페이지 -----------------------------------------------------------------


def render_lesson(model: SiteModel, summary: LessonSummary) -> str:
    lesson = summary.lesson
    page = model.lesson_page(lesson)
    progress = summary.progress
    t = model.t
    text = model.text(lesson)
    out = [
        f"# {md_text(text.title)}",
        "",
        f'<p class="rc-meta">{html.escape(stage_text(stage_of(summary.module), t))} · '
        f"{html.escape(model.module_text(summary.module).title)} · "
        f"⏱ {format_minutes(lesson.estimated_minutes, model.lang)} · "
        f"{html.escape(t('site.label.difficulty'))} {difficulty_dots(lesson.difficulty)} "
        f"({lesson.difficulty}/5) · "
        f"{badge(state_of(summary), t)}</p>",
        "",
        f"> {md_text(text.summary)}",
        "",
        f"[{md_text(t('site.heading.study_guide'))}](#{STUDY_ANCHOR}) · "
        f"[{md_text(t('site.heading.resources'))}](#{RESOURCES_ANCHOR}) · "
        f"{module_link(model, page, summary.module)}",
        "",
        f"**{md_text(t('site.label.objectives'))}**",
        "",
        *[f"- {md_text(objective)}" for objective in text.objectives],
        "",
    ]
    if lesson.prerequisites:
        items = []
        for prereq in lesson.prerequisites:
            other = model.by_lesson.get(prereq)
            if other is None:
                items.append(f"`{prereq}`")
            else:
                items.append(
                    f"{lesson_link(model, page, other.lesson)} {badge(state_of(other), t)}"
                )
        prereq_label = md_text(t("site.label.prerequisites"))
        out.append(f"**{prereq_label}**: " + " · ".join(items))
    else:
        out.append(f"**{md_text(t('site.label.prerequisites'))}**: {md_text(t('site.label.none'))}")
    if summary.missing_prerequisites and summary.status is not LessonStatus.DONE:
        # Informational: nothing stops a reader starting here (ADR 0015).
        ids = " · ".join(f"`{md_text(i)}`" for i in summary.missing_prerequisites)
        out += [
            "",
            f'!!! note "{md_text(t("site.lesson.prereq_pending_title"))}"',
            f"    {md_text(t('site.lesson.prereq_pending_body'))} {ids}",
        ]
    out.append("")
    if text.tags:
        tags = " ".join(f"`{md_text(tag)}`" for tag in text.tags)
        out += [f"**{md_text(t('site.label.tags'))}**: " + tags, ""]
    if text.activities:
        out += [f"**{md_text(t('site.label.activities'))}**", ""]
        for activity in text.activities:
            minutes = (
                f" · {format_minutes(activity.estimated_minutes, model.lang)}"
                if activity.estimated_minutes
                else ""
            )
            out.append(
                f"- {md_text(activity_label(activity.kind, t))}: {md_text(activity.title)}{minutes}"
            )
        out.append("")
    record = _progress_line(progress, model.now, t)
    if record:
        out += [f"**{md_text(t('site.label.my_record'))}**: {md_text(record)}", ""]
    out += ["---", ""]

    body, study = split_study_section(render_quiz_blocks(strip_leading_h1(text.body), lesson, t))
    out += [body.strip("\n"), ""]

    out += [f"## {md_text(t('site.heading.study_guide'))} {{#{STUDY_ANCHOR}}}", ""]
    if study:
        out += [f'!!! tip "{md_text(t("site.lesson.study_tip"))}"', "", indent(study), ""]
    else:
        out += [
            f'!!! note "{md_text(t("site.lesson.study_missing"))}"',
            "",
            f"    {md_text(t('site.lesson.study_missing_body'))}",
            "",
        ]
    out += _papers_section(model, lesson, t)
    out += [f"## {md_text(t('site.heading.resources'))} {{#{RESOURCES_ANCHOR}}}", ""]
    if text.resources:
        out += _resource_groups(model, page, [(r, [lesson]) for r in text.resources])
    else:
        out.append(md_text(t("site.lesson.no_resources")))
    return "\n".join(out) + "\n"


def _papers_section(model: SiteModel, lesson: Lesson, t: Translator) -> list[str]:
    """ "필독 논문": the papers this lesson assigns, required reading first (ADR 0014).

    Nothing is emitted when the course has no registry, so the courses that predate the
    research track look exactly as they did.
    """
    rows = resolve_lesson_papers(lesson, paper_index(model.course_of(lesson)))
    if not rows:
        return []
    out = [f"## {md_text(t('site.heading.papers'))} {{#{PAPERS_ANCHOR}}}", ""]
    for row in rows:
        marks = [t("paper.required") if row.required else t("paper.optional")]
        if row.role:
            marks.append(t(f"paper.role.{row.role}"))
        title = f"[{md_text(row.title)}]({row.url})" if row.url else f"**{md_text(row.title)}**"
        out.append(f"- ({md_text(' · '.join(marks))}) {title}")
        detail = [part for part in (citation(row), row.note) if part]
        if not row.verified and row.url:
            detail.append(t("paper.unverified"))
        if detail:
            out.append(f"  {md_text(' — '.join(detail))}")
    out.append("")
    return out


def render_quiz_blocks(body: str, lesson: Lesson, t: Translator | None = None) -> str:
    """Replace each ```` ```quiz ```` fence with a question list; answers fold into ``<details>``.

    Questions and choices stay visible; the correct answer and explanation go into a
    collapsible ``???`` admonition (pymdownx.details renders it as ``<details>``). A block
    that does not parse is shown as a plain YAML code block instead.
    """
    t = t or translator(DEFAULT_LANG)
    try:
        quiz = localized_quiz(lesson, t.lang)
    except QuizParseError:
        return _replace_fences(body, lambda _i, raw: _code_block(raw))
    blocks = quiz.blocks
    number = 0

    def render(index: int, raw: str) -> str:
        nonlocal number
        if index >= len(blocks):
            return _code_block(raw)
        heading = md_text(t("site.heading.quiz", count=len(blocks[index].questions)))
        out = [f'!!! question "{heading}"', ""]
        for question in blocks[index].questions:
            number += 1
            out += indent(_render_question(question, number, t)).splitlines() + [""]
        return "\n".join(out)

    return _replace_fences(body, render)


def _code_block(raw: str, language: str = "yaml") -> str:
    """Wrap ``raw`` in a fence long enough that its own backticks cannot close it."""
    longest = max((len(run) for run in re.findall(r"`+", raw)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}{language}\n{raw}\n{fence}"


def _render_question(question: QuizQuestion, number: int, t: Translator) -> str:
    # Quiz text comes from lesson front matter, so it is escaped like any other content.
    kind = md_text(t(f"quiz.kind.{question.type}"))
    lines = [f"**{number}.** ({kind}) {md_text(question.prompt)}", ""]
    if question.choices:
        lines += [f"{i + 1}. {md_text(choice)}" for i, choice in enumerate(question.choices)]
        lines.append("")
    answer = t("site.lesson.answer_label", answer=md_text(question.answer_text(t.lang)))
    lines += [
        f'??? note "{md_text(t("site.heading.answer"))}"',
        "",
        f"    {answer}",
        "",
        f"    {md_text(question.explanation)}",
    ]
    return "\n".join(lines)


def _replace_fences(body: str, render: Callable[[int, str], str]) -> str:
    out: list[str] = []
    current: list[str] | None = None
    closing: str | None = None
    index = 0
    for line in body.splitlines():
        if current is not None:
            if closing is not None and line.strip() == closing:
                out.append(render(index, "\n".join(current)))
                index += 1
                current, closing = None, None
            else:
                current.append(line)
            continue
        match = QUIZ_FENCE.match(line.strip())
        if match:
            current, closing = [], match["fence"]
        else:
            out.append(line)
    if current is not None:  # unterminated fence: keep it verbatim
        out += [f"{closing}quiz", *current]
    return "\n".join(out)


def _progress_line(progress: LessonProgress, now: datetime, t: Translator) -> str:
    parts = []
    if progress.total_seconds:
        parts.append(t("site.record.total", time=format_seconds(progress.total_seconds, t.lang)))
    if progress.started_at:
        parts.append(t("site.record.started", date=f"{_local(progress.started_at, now):%Y-%m-%d}"))
    if progress.completed_at and progress.status is LessonStatus.DONE:
        parts.append(
            t("site.record.completed", date=f"{_local(progress.completed_at, now):%Y-%m-%d}")
        )
    if progress.understanding:
        parts.append(t("site.record.understanding", value=progress.understanding))
    return " · ".join(parts)


# -- 자료 -----------------------------------------------------------------------


def _collect_resources(
    summaries: Iterable[LessonSummary], lang: str | None = None
) -> list[tuple[Resource, list[Lesson]]]:
    """Resources in first-use order, deduplicated by (title, url), with the lessons using them."""
    found: dict[tuple[str, str | None], tuple[Resource, list[Lesson]]] = {}
    for summary in summaries:
        for resource in summary.lesson.localized_resources(lang):
            key = (resource.title, resource.url)
            if key not in found:
                found[key] = (resource, [])
            found[key][1].append(summary.lesson)
    return list(found.values())


def _resource_groups(
    model: SiteModel,
    page: str,
    resources: list[tuple[Resource, list[Lesson]]],
    *,
    show_lessons: bool = False,
    heading: str = "###",
) -> list[str]:
    t = model.t
    labels = [kind_label(kind, t) for kind, _ in KIND_KEYS]
    order = list(dict.fromkeys(labels))  # unique, in display order
    groups: dict[str, list[tuple[Resource, list[Lesson]]]] = {label: [] for label in order}
    for item in resources:
        groups[kind_label(item[0].kind, t)].append(item)
    out: list[str] = []
    for label in order:
        if not groups[label]:
            continue
        out += [f"{heading} {md_text(label)}", ""]
        for resource, lessons in groups[label]:
            # Only http(s) survives: a `javascript:` url must never become a link.
            safe_url = resource.url if resource.url and is_http_url(resource.url) else None
            title = (
                f"[{md_text(resource.title)}]({safe_url})" if safe_url else md_text(resource.title)
            )
            line = f"- {title}"
            if resource.note:
                line += f" — {md_text(resource.note)}"
            if show_lessons:
                line += t(
                    "site.resources.lessons_suffix",
                    lessons=", ".join(lesson_link(model, page, x) for x in lessons),
                )
            out.append(line)
        out.append("")
    return out


def render_resources(model: SiteModel) -> str:
    page = RESOURCES_PAGE
    resources = _collect_resources(model.summaries, model.lang)
    t = model.t
    out = [
        f"# {md_text(t('site.heading.resources_page'))}",
        "",
        md_text(t("site.resources.intro", count=len(resources))),
        "",
    ]
    if not resources:
        out.append(md_text(t("site.resources.empty")))
    else:
        out += _resource_groups(model, page, resources, show_lessons=True, heading="##")
    return "\n".join(out) + "\n"

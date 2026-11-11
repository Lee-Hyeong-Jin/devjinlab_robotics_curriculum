"""Markdown page renderers for the static site (platform-design 2.2-2.3).

Every function returns the Markdown text of one page. Links are relative ``.md`` paths
so that MkDocs resolves (and checks) them. Nothing here touches the filesystem.
"""

from __future__ import annotations

import html
import posixpath
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime

from robotics_curriculum.content import Course, Lesson, Module, Resource, ResourceKind
from robotics_curriculum.content.validate import is_http_url
from robotics_curriculum.progress import LessonProgress, LessonStatus, LessonSummary, Session
from robotics_curriculum.site.stats import (
    Ratio,
    activity_days,
    format_minutes,
    format_seconds,
    ordered_stages,
    ratio,
    stage_of,
    streak,
    week_stats,
)

INDEX_PAGE = "index.md"
ROADMAP_PAGE = "roadmap.md"
RESOURCES_PAGE = "resources.md"
STUDY_HEADING = "이 단계 공부법"
STUDY_ANCHOR = "study-method"
RESOURCES_ANCHOR = "resources"

# state key -> (symbol, Korean label)
STATES: dict[str, tuple[str, str]] = {
    "done": ("■", "완료"),
    "in_progress": ("▣", "진행 중"),
    "not_started": ("□", "시작 전"),
    "locked": ("▨", "잠김"),
}

KIND_LABELS: dict[ResourceKind | None, str] = {
    ResourceKind.BOOK: "교재",
    ResourceKind.COURSE: "강의",
    ResourceKind.VIDEO: "영상",
    ResourceKind.ARTICLE: "글",
    ResourceKind.OTHER: "기타",
    None: "기타",
}
KIND_ORDER = ["교재", "강의", "영상", "글", "기타"]

ACTIVITY_LABELS = {"reading": "읽기", "quiz": "퀴즈", "exercise": "실습"}


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
    return "locked" if summary.locked else "not_started"


def badge(state: str) -> str:
    symbol, label = STATES[state]
    return f'<span class="rc-status rc-{state}">{symbol} {label}</span>'


def bar(r: Ratio) -> str:
    """A progress bar. The width comes from a class, so no attribute carries CSS."""
    step = 5 * round(r.percent / 5)
    return (
        f'<span class="rc-bar" title="{r.percent}%"><span class="rc-fill rc-w-{step}">'
        f'</span></span> <span class="rc-pct">{r.percent}% ({r.done}/{r.total})</span>'
    )


def difficulty_dots(level: int) -> str:
    return "●" * level + "○" * (5 - level)


def legend() -> str:
    return " · ".join(f"{sym} {label}" for sym, label in STATES.values())


# -- body processing -----------------------------------------------------------

_FENCE = re.compile(r"^\s*(```|~~~)")
_STUDY = re.compile(rf"^##\s+{STUDY_HEADING}\s*#*\s*$")
_H1_OR_H2 = re.compile(r"^#{1,2}\s")


def split_study_section(body: str) -> tuple[str, str | None]:
    """Remove the ``## 이 단계 공부법`` section from ``body``; return (rest, section text)."""
    lines = body.split("\n")
    in_fence = False
    start = end = None
    for index, line in enumerate(lines):
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if start is None and _STUDY.match(line):
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
    by_lesson: dict[str, LessonSummary] = field(init=False)
    module_keys: dict[int, str] = field(init=False)

    def __post_init__(self) -> None:
        self.by_lesson = {s.lesson.id: s for s in self.summaries}
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
        return self.courses[0].title if len(self.courses) == 1 else "로보틱스 커리큘럼"

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

    def progress_rows(self) -> list[LessonProgress]:
        return [s.progress for s in self.summaries]


def lesson_link(model: SiteModel, page: str, lesson: Lesson, anchor: str = "") -> str:
    return link(page, model.lesson_page(lesson), lesson.title, anchor)


def module_link(model: SiteModel, page: str, module: Module) -> str:
    return link(page, model.module_page(module), module.title)


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
    out = [
        f"# {md_text(model.title)}",
        "",
        f'<p class="rc-built">빌드: {now:%Y-%m-%d %H:%M} · 진도를 반영하려면 '
        "<code>rc site build</code> 를 다시 실행하세요.</p>",
        "",
        "## 현재 위치",
        "",
    ]
    current = current_lesson(model)
    if current is None:
        out.append("모든 레슨을 완료했습니다. 수고하셨습니다!")
    else:
        module_ratio = ratio(model.module_summaries(current.module))
        out += [
            f"- **단계**: {stage_of(current.module)}",
            f"- **모듈**: {module_link(model, page, current.module)} "
            f"({module_ratio.done}/{module_ratio.total} 레슨 완료)",
            f"- **다음 레슨**: {lesson_link(model, page, current.lesson)} "
            f"{badge(state_of(current))} · ⏱ {format_minutes(current.lesson.estimated_minutes)}",
            f"- {link(page, model.lesson_page(current.lesson), '공부법 보기', STUDY_ANCHOR)}"
            f" · 시작: `rc start {current.lesson.id}`",
        ]
    out += ["", "## 한눈에 보기", "", _cards(model), "", "## 단계별 진행률", ""]
    out.append(_stage_table(model, page))
    out += ["", "## 다음 레슨", ""]
    if model.next_lessons:
        for summary in model.next_lessons[:5]:
            lesson = summary.lesson
            out.append(
                f"1. {lesson_link(model, page, lesson)} {badge(state_of(summary))} · "
                f"{summary.module.title} · ⏱ {format_minutes(lesson.estimated_minutes)}"
            )
    else:
        out.append("지금 시작할 수 있는 레슨이 없습니다.")
    out += ["", "## 최근 활동", ""]
    out += _recent_activity(model, page) or [
        "아직 기록된 학습이 없습니다. `rc start <레슨>` 으로 시작하세요."
    ]
    return "\n".join(out) + "\n"


def _cards(model: SiteModel) -> str:
    week = week_stats(model.sessions, model.now)
    days = activity_days(model.sessions, model.progress_rows(), model.now)
    total = ratio(model.summaries)
    cards = [
        (
            "이번 주 학습 시간",
            format_seconds(week.seconds),
            f"{week.sessions}회 세션 · {week.start:%m/%d}~",
        ),
        ("연속 학습", f"{streak(days, model.now.date())}일", "하루 한 번 이상 학습한 날"),
        ("완료한 레슨", f"{total.done} / {total.total}", f"전체 {total.percent}%"),
        ("오늘 복습", "—", "복습 카드 기능 준비 중"),
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
    rows = ["| 단계 | 진행률 | 모듈 |", "|---|---|---|"]
    for stage in model.stages():
        summaries = model.stage_summaries(stage)
        modules = [m for m in model.modules() if stage_of(m) == stage]
        if not modules:
            rows.append(f"| {stage} | — | 아직 준비 중인 단계입니다 |")
            continue
        module_cells = " · ".join(
            f"{module_link(model, page, m)} {ratio(model.module_summaries(m)).percent}%"
            for m in modules
        )
        rows.append(f"| **{stage}** | {bar(ratio(summaries))} | {module_cells} |")
    return "\n".join(rows)


def _recent_activity(model: SiteModel, page: str, limit: int = 5) -> list[str]:
    events: list[tuple[datetime, str]] = []
    for session in model.sessions:
        summary = model.by_lesson.get(session.lesson_id)
        if summary is None:
            continue
        kind = "타이머" if session.source == "timer" else "기록"
        length = (
            "진행 중" if session.is_open else format_seconds(session.elapsed_seconds(model.now))
        )
        events.append(
            (
                session.started_at,
                f"{lesson_link(model, page, summary.lesson)} 학습 {length} ({kind})",
            )
        )
    for summary in model.summaries:
        done_at = summary.progress.completed_at
        if summary.status is LessonStatus.DONE and done_at is not None:
            extra = (
                f" (이해도 {summary.progress.understanding})"
                if summary.progress.understanding
                else ""
            )
            events.append((done_at, f"{lesson_link(model, page, summary.lesson)} 완료{extra}"))
    events.sort(key=lambda e: e[0], reverse=True)
    return [f"- {_local(when, model.now):%m/%d} · {text}" for when, text in events[:limit]]


# -- 로드맵 ---------------------------------------------------------------------


def render_roadmap(model: SiteModel) -> str:
    page = ROADMAP_PAGE
    out = ["# 로드맵", "", f"단계별 모듈과 레슨. 범례: {legend()}", ""]
    for stage in model.stages():
        summaries = model.stage_summaries(stage)
        modules = [m for m in model.modules() if stage_of(m) == stage]
        out += [f"## {stage}", ""]
        if not modules:
            out += ["아직 준비 중인 단계입니다.", ""]
            continue
        out += [bar(ratio(summaries)), ""]
        for module in modules:
            module_ratio = ratio(model.module_summaries(module))
            out += [
                f"### {module_link(model, page, module)}",
                "",
                f"{md_text(module.summary)}",
                "",
                bar(module_ratio),
                "",
            ]
            for summary in model.module_summaries(module):
                lesson = summary.lesson
                prereq = ""
                if lesson.prerequisites:
                    names = ", ".join(
                        md_text(model.by_lesson[p].lesson.title)
                        for p in lesson.prerequisites
                        if p in model.by_lesson
                    )
                    prereq = f" · 선수: {names}"
                out.append(
                    f"- {badge(state_of(summary))} {lesson_link(model, page, lesson)} · "
                    f"⏱ {format_minutes(lesson.estimated_minutes)}{prereq}"
                )
            out.append("")
    return "\n".join(out) + "\n"


# -- 모듈 페이지 -----------------------------------------------------------------


def render_module(model: SiteModel, module: Module) -> str:
    page = model.module_page(module)
    summaries = model.module_summaries(module)
    total_minutes = sum(s.lesson.estimated_minutes for s in summaries)
    out = [
        f"# {md_text(module.title)}",
        "",
        f"**단계**: {stage_of(module)} · **레슨** {len(summaries)}개 · "
        f"**예상 시간** {format_minutes(total_minutes)} · {link(page, ROADMAP_PAGE, '로드맵으로')}",
        "",
        md_text(module.summary),
        "",
        bar(ratio(summaries)),
        "",
        "## 레슨",
        "",
        "| # | 레슨 | 상태 | 예상 시간 | 난이도 | 선수 레슨 |",
        "|---|---|---|---|---|---|",
    ]
    for number, summary in enumerate(summaries, 1):
        lesson = summary.lesson
        prereqs = ", ".join(
            f"{lesson_link(model, page, model.by_lesson[p].lesson)} "
            f"({STATES[state_of(model.by_lesson[p])][1]})"
            for p in lesson.prerequisites
            if p in model.by_lesson
        )
        out.append(
            f"| {number} | {lesson_link(model, page, lesson)} | {badge(state_of(summary))} | "
            f"{format_minutes(lesson.estimated_minutes)} | {difficulty_dots(lesson.difficulty)} | "
            f"{prereqs or '없음'} |"
        )
    resources = _collect_resources(summaries)
    if resources:
        out += ["", "## 이 모듈의 학습 자료", ""]
        out += _resource_groups(model, page, resources, show_lessons=True)
    return "\n".join(out) + "\n"


# -- 레슨 페이지 -----------------------------------------------------------------


def render_lesson(model: SiteModel, summary: LessonSummary) -> str:
    lesson = summary.lesson
    page = model.lesson_page(lesson)
    progress = summary.progress
    out = [
        f"# {md_text(lesson.title)}",
        "",
        f'<p class="rc-meta">{stage_of(summary.module)} · '
        f"{html.escape(summary.module.title)} · ⏱ {format_minutes(lesson.estimated_minutes)} · "
        f"난이도 {difficulty_dots(lesson.difficulty)} ({lesson.difficulty}/5) · "
        f"{badge(state_of(summary))}</p>",
        "",
        f"> {md_text(lesson.summary)}",
        "",
        f"[{STUDY_HEADING}](#{STUDY_ANCHOR}) · [학습 자료](#{RESOURCES_ANCHOR}) · "
        f"{module_link(model, page, summary.module)}",
        "",
        "**학습 목표**",
        "",
        *[f"- {md_text(objective)}" for objective in lesson.objectives],
        "",
    ]
    if lesson.prerequisites:
        items = []
        for prereq in lesson.prerequisites:
            other = model.by_lesson.get(prereq)
            if other is None:
                items.append(f"`{prereq}`")
            else:
                items.append(f"{lesson_link(model, page, other.lesson)} {badge(state_of(other))}")
        out.append("**선수 레슨**: " + " · ".join(items))
    else:
        out.append("**선수 레슨**: 없음")
    if summary.locked and summary.status is not LessonStatus.DONE:
        out += ["", '!!! warning "잠김"', "    선수 레슨을 먼저 완료하면 이 레슨이 열립니다."]
    out.append("")
    if lesson.tags:
        out += ["**태그**: " + " ".join(f"`{md_text(tag)}`" for tag in lesson.tags), ""]
    if lesson.activities:
        out += ["**활동**", ""]
        for activity in lesson.activities:
            minutes = (
                f" · {format_minutes(activity.estimated_minutes)}"
                if activity.estimated_minutes
                else ""
            )
            out.append(
                f"- {ACTIVITY_LABELS.get(activity.kind, activity.kind)}: "
                f"{md_text(activity.title)}{minutes}"
            )
        out.append("")
    record = _progress_line(progress, model.now)
    if record:
        out += [f"**내 기록**: {record}", ""]
    out += ["---", ""]

    body, study = split_study_section(strip_leading_h1(lesson.body))
    out += [body.strip("\n"), ""]

    out += [f"## {STUDY_HEADING} {{#{STUDY_ANCHOR}}}", ""]
    if study:
        out += ['!!! tip "이렇게 공부하세요"', "", indent(study), ""]
    else:
        out += [
            '!!! note "공부법이 아직 작성되지 않았습니다"',
            "",
            "    학습 목표를 확인하고 본문을 읽은 뒤, 아래 학습 자료로 보충하세요.",
            "",
        ]
    out += [f"## 학습 자료 {{#{RESOURCES_ANCHOR}}}", ""]
    if lesson.resources:
        out += _resource_groups(model, page, [(r, [lesson]) for r in lesson.resources])
    else:
        out.append("등록된 자료가 없습니다.")
    return "\n".join(out) + "\n"


def _progress_line(progress: LessonProgress, now: datetime) -> str:
    parts = []
    if progress.total_seconds:
        parts.append(f"누적 학습 {format_seconds(progress.total_seconds)}")
    if progress.started_at:
        parts.append(f"시작 {_local(progress.started_at, now):%Y-%m-%d}")
    if progress.completed_at and progress.status is LessonStatus.DONE:
        parts.append(f"완료 {_local(progress.completed_at, now):%Y-%m-%d}")
    if progress.understanding:
        parts.append(f"이해도 {progress.understanding}/5")
    return " · ".join(parts)


# -- 자료 -----------------------------------------------------------------------


def _collect_resources(summaries: Iterable[LessonSummary]) -> list[tuple[Resource, list[Lesson]]]:
    """Resources in first-use order, deduplicated by (title, url), with the lessons using them."""
    found: dict[tuple[str, str | None], tuple[Resource, list[Lesson]]] = {}
    for summary in summaries:
        for resource in summary.lesson.resources:
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
    groups: dict[str, list[tuple[Resource, list[Lesson]]]] = {k: [] for k in KIND_ORDER}
    for item in resources:
        groups[KIND_LABELS[item[0].kind]].append(item)
    out: list[str] = []
    for label in KIND_ORDER:
        if not groups[label]:
            continue
        out += [f"{heading} {label}", ""]
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
                line += " · 레슨: " + ", ".join(lesson_link(model, page, x) for x in lessons)
            out.append(line)
        out.append("")
    return out


def render_resources(model: SiteModel) -> str:
    page = RESOURCES_PAGE
    resources = _collect_resources(model.summaries)
    out = [
        "# 자료실",
        "",
        f"코스 전체 학습 자료 {len(resources)}개를 유형별로 모았습니다. "
        "각 자료 옆의 레슨 링크에서 언제 어떻게 쓰는지 확인하세요.",
        "",
    ]
    if not resources:
        out.append("등록된 자료가 없습니다.")
    else:
        out += _resource_groups(model, page, resources, show_lessons=True, heading="##")
    return "\n".join(out) + "\n"

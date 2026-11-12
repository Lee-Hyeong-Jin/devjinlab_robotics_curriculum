"""Collect every place Korean text still shows up in the English build (FR-9).

Run it from the repository root::

    uv run python scripts/i18n/audit.py            # print the report
    uv run python scripts/i18n/audit.py --write    # also write docs/reviews/i18n-gap-audit.md

It drives the real surfaces: the API with ``Accept-Language: en``, the static site built
with ``--lang en``, the CLI with ``RC_LANG=en``, and the message catalogues / content files.
The web front-end is covered separately by ``web/e2e/i18n.spec.ts`` (same detector).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from robotics_curriculum.i18n.scan import Finding, find_hangul, html_text, scan_json  # noqa: E402

CURRICULUM = ROOT / "curriculum"
OUT = ROOT / "docs" / "reviews" / "i18n-gap-audit.md"


@dataclass(frozen=True, slots=True)
class Gap:
    surface: str
    where: str
    sample: str


def _gaps(surface: str, findings: list[Finding]) -> list[Gap]:
    return [Gap(surface, f.where, f.context[:160]) for f in findings]


# -- API -------------------------------------------------------------------------------


def audit_api(data_dir: Path) -> list[Gap]:
    from fastapi.testclient import TestClient

    from robotics_curriculum.api.app import create_app
    from robotics_curriculum.api.settings import Settings

    settings = Settings(curriculum_dir=CURRICULUM, data_dir=data_dir)
    client = TestClient(create_app(settings))
    headers = {"Accept-Language": "en"}
    paths = [
        "/api/v1/courses",
        "/api/v1/courses/robotics-expert",
        "/api/v1/roadmap",
        "/api/v1/resources",
        "/api/v1/search?q=robot",
        "/api/v1/progress/status",
        "/api/v1/progress/next",
        "/api/v1/reports/weekly",
        "/api/v1/review/queue",
    ]
    courses = client.get("/api/v1/courses/robotics-expert", headers=headers).json()
    module_ids = [m["id"] for stage in courses.get("stages", []) for m in stage["modules"]]
    paths += [f"/api/v1/modules/{mid}" for mid in module_ids]
    lesson_ids: list[str] = []
    for mid in module_ids:
        module = client.get(f"/api/v1/modules/{mid}", headers=headers).json()
        lesson_ids += [lesson["id"] for lesson in module.get("lessons", [])]
    paths += [f"/api/v1/lessons/{lid}" for lid in lesson_ids]
    paths += [f"/api/v1/lessons/{lid}/quiz" for lid in lesson_ids]
    paths += [f"/api/v1/reports/module/{mid}" for mid in module_ids]

    gaps: list[Gap] = []
    for path in paths:
        response = client.get(path, headers=headers)
        if response.status_code >= 400:
            continue
        try:
            body = response.json()
        except ValueError:
            continue
        gaps += _gaps("API", scan_json(body, f"GET {path} "))
    return gaps


# -- static site -----------------------------------------------------------------------


def audit_site(data_dir: Path, work: Path) -> list[Gap]:
    from robotics_curriculum.content import load_courses
    from robotics_curriculum.progress import ProgressService, SqliteProgressStore
    from robotics_curriculum.site import generate_project

    store = SqliteProgressStore.in_dir(data_dir)
    service = ProgressService(store, load_courses(CURRICULUM))
    project = work / "site-en"
    try:
        generate_project(service, project, lang="en")
    finally:
        store.close()
    gaps: list[Gap] = []
    for path in sorted(project.rglob("*.md")) + sorted(project.glob("mkdocs.yml")):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(project).as_posix()
        for run in dict.fromkeys(find_hangul(text)):
            gaps.append(Gap("static site", rel, run))
    return gaps


def audit_site_html(out_dir: Path) -> list[Gap]:
    """Scan already-built HTML (``rc site build --lang en --out <dir>``) when present."""
    gaps: list[Gap] = []
    for path in sorted(out_dir.rglob("*.html")):
        text = html_text(path.read_text(encoding="utf-8"))
        for run in dict.fromkeys(find_hangul(text)):
            gaps.append(Gap("static site (html)", path.relative_to(out_dir).as_posix(), run))
    return gaps


# -- CLI -------------------------------------------------------------------------------


CLI_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("status",),
    ("roadmap",),
    ("next",),
    ("resources", "m1-vectors-matrices"),
    ("show", "m1-vectors-matrices"),
    ("report", "weekly"),
    ("report", "module", "m1-math-physics"),
    ("--help",),
)


def audit_cli(data_dir: Path) -> list[Gap]:
    from typer.testing import CliRunner

    from robotics_curriculum.cli import app

    runner = CliRunner()
    gaps: list[Gap] = []
    for command in CLI_COMMANDS:
        result = runner.invoke(
            app,
            ["--data-dir", str(data_dir), "--curriculum", str(CURRICULUM), *command],
            env={"RC_LANG": "en"},
        )
        for run in dict.fromkeys(find_hangul(result.output)):
            gaps.append(Gap("CLI", "rc " + " ".join(command), run))
    return gaps


# -- content and catalogues ------------------------------------------------------------


def audit_content(lang: str = "en") -> list[Gap]:
    """Content fields that still read in the authoring language in the ``lang`` build."""
    from robotics_curriculum.content import load_courses, localized_quiz
    from robotics_curriculum.content.quiz_block import QuizParseError

    gaps: list[Gap] = []
    for course in load_courses(CURRICULUM):
        if not course.localized(lang).translated:
            gaps.append(Gap("content", f"course.yaml ({course.id})", "title / summary"))
        for module in course.modules:
            if not module.localized(lang).translated:
                gaps.append(Gap("content", f"{module.id}/module.yaml", "title / summary"))
            for lesson in module.lessons:
                where = f"{module.id}/{lesson.id}"
                text = lesson.localized(lang)
                if not text.translated:
                    gaps.append(Gap("content", where, f"no .{lang}.md translation"))
                for activity in text.activities:
                    if find_hangul(activity.title):
                        gaps.append(Gap("content", where, f"activity {activity.id}: title"))
                for index, resource in enumerate(text.resources):
                    if find_hangul(resource.title) or find_hangul(resource.note or ""):
                        gaps.append(Gap("content", where, f"resource {index}: title / note"))
                try:
                    questions = localized_quiz(lesson, lang).questions
                except QuizParseError:
                    continue
                for question in questions:
                    texts = [question.prompt, question.explanation, *question.choices]
                    if any(find_hangul(value) for value in texts):
                        gaps.append(Gap("content", where, f"quiz {question.id}"))
    return gaps


def audit_sources() -> list[Gap]:
    """Korean string literals in code that reaches the user."""
    gaps: list[Gap] = []
    for path in sorted((ROOT / "src").rglob("*.py")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            runs = find_hangul(line)
            if runs and not line.lstrip().startswith("#"):
                rel = path.relative_to(ROOT).as_posix()
                gaps.append(Gap("source", f"{rel}:{number}", " ".join(dict.fromkeys(runs))[:120]))
    return gaps


# -- report ----------------------------------------------------------------------------


_ID_SEGMENT = re.compile(r"/(m\d+[a-z0-9-]*|robotics-expert)(?=[/ ]|$)")
_INDEX_SEGMENT = re.compile(r"/\d+(?=/|$)")


def normalize(where: str) -> str:
    """``/lessons/m1-vectors /activities/0/title`` -> ``/lessons/{id} /activities/*/title``."""
    collapsed = _ID_SEGMENT.sub("/{id}", where)
    return _INDEX_SEGMENT.sub("/*", collapsed)


def render(groups: dict[str, list[Gap]]) -> str:
    total = sum(len(v) for v in groups.values())
    lines = [
        "# i18n gap audit - Korean left in the English build",
        "",
        f"- generated: {date.today():%Y-%m-%d} by `uv run python scripts/i18n/audit.py --write`",
        f"- Korean runs found: **{total}**",
        "- detector: `robotics_curriculum.i18n.scan` (Hangul syllables, Jamo, compatibility Jamo)",
        "- rows are grouped by field: list indexes and content ids collapse to `*` / `{id}`.",
        "",
        "## How to read this",
        "",
        "| class | meaning | owner |",
        "| --- | --- | --- |",
        "| **A. no container** | the field has nowhere to hold a translation "
        "(course/module title and summary, activity titles, resource title and note, quiz "
        "questions) | this audit's follow-up work |",
        "| **B. container unused** | a translation exists but the surface never asks for it "
        "(`/progress/status`, `/progress/next`, module listings) | same |",
        "| **C. Korean in code** | a literal in `src/` that reaches the user (report Markdown, "
        "quiz type labels, stage names, duration strings, account e-mails) | same |",
        "| **D. lesson body** | `<lesson>.en.md` does not exist yet for M5-M10 | the "
        "`translator-en` session |",
        "",
        "The web front-end is not listed separately: `web/messages/en.json` is at full key "
        "parity with `ko.json` and holds no Korean, so every Korean string the reader sees in "
        "the web app comes from the API rows below (lesson and module text, the stage chip, "
        "report Markdown). `web/e2e/i18n.spec.ts` guards it with the same detector.",
        "",
        "## Summary",
        "",
        "| surface | Korean runs | distinct fields |",
        "| --- | ---: | ---: |",
    ]
    rolled: dict[str, dict[str, tuple[int, str]]] = {}
    for surface, gaps in groups.items():
        fields: dict[str, tuple[int, str]] = {}
        for gap in gaps:
            key = normalize(gap.where)
            count, sample = fields.get(key, (0, gap.sample))
            fields[key] = (count + 1, sample)
        rolled[surface] = dict(sorted(fields.items(), key=lambda kv: (-kv[1][0], kv[0])))
        lines.append(f"| {surface} | {len(gaps)} | {len(fields)} |")
    for surface, fields in rolled.items():
        lines += ["", f"## {surface}", "", "| where | runs | sample |", "| --- | ---: | --- |"]
        for key, (count, sample) in fields.items():
            text = sample.replace("|", "\\|").replace("\n", " ")[:90]
            lines.append(f"| `{key}` | {count} | {text} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help=f"write {OUT.relative_to(ROOT)}")
    parser.add_argument("--json", action="store_true", help="print findings as JSON")
    parser.add_argument("--skip-cli", action="store_true", help="skip the slow CLI subprocesses")
    parser.add_argument("--html", type=Path, default=None, help="also scan a built site directory")
    args = parser.parse_args()

    groups: dict[str, list[Gap]] = defaultdict(list)
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for gap in audit_api(work / "api-data"):
            groups[gap.surface].append(gap)
        for gap in audit_site(work / "site-data", work):
            groups[gap.surface].append(gap)
        if not args.skip_cli:
            for gap in audit_cli(work / "cli-data"):
                groups[gap.surface].append(gap)
    if args.html is not None:
        for gap in audit_site_html(args.html):
            groups[gap.surface].append(gap)
    for gap in audit_content():
        groups[gap.surface].append(gap)
    for gap in audit_sources():
        groups[gap.surface].append(gap)

    if args.json:
        payload = {k: [asdict(g) for g in v] for k, v in groups.items()}
        print(json.dumps(payload, ensure_ascii=False))
        return 0
    report = render(dict(sorted(groups.items())))
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(report, encoding="utf-8")
        print(f"written: {OUT.relative_to(ROOT)}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

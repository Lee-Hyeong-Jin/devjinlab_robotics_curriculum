"""Reproductions for docs/reviews/2026-11-11-integration-review.md.

Every test asserts the *desired* behavior and is marked ``xfail(strict=True)`` while the
defect is open, so the gate stays green today. When a fix lands the test XPASSes, strict
mode turns that into a failure, and the fixer removes the marker: the test then becomes the
regression test the engineering rules require. IDs (QA-xx) match the review table.
"""

from __future__ import annotations

import os
import shutil
import sqlite3
from html.parser import HTMLParser
from pathlib import Path

import pytest
from typer.testing import CliRunner, Result

from robotics_curriculum.cli import app

FIXTURE = Path(__file__).parent / "fixtures" / "curriculum"
LESSON_ID = "m1-vectors-matrices"
runner = CliRunner()


def _open(reason: str) -> pytest.MarkDecorator:
    return pytest.mark.xfail(strict=True, reason=f"open defect {reason}")


def _rc(curriculum: Path, data: Path, *args: str) -> Result:
    return runner.invoke(app, ["--curriculum", str(curriculum), "--data-dir", str(data), *args])


def _clean_user_error(result: Result) -> bool:
    """Exit 1 through ``typer.Exit`` (an ``error: ...`` line), not an escaped exception."""
    return result.exit_code == 1 and isinstance(result.exception, SystemExit | None)


def _lesson(id_: str, prereqs: list[str], *, title: str | None = None, extra: str = "") -> str:
    return (
        f'---\nid: {id_}\ntitle: "{title or id_}"\nsummary: s\nobjectives: [o]\n'
        f"prerequisites: [{', '.join(prereqs)}]\ndifficulty: 1\nestimated_minutes: 5\n"
        f"{extra}---\nbody\n"
    )


def _course(root: Path, course_id: str, lessons: dict[str, str]) -> None:
    module = root / course_id / "m1"
    module.mkdir(parents=True)
    (root / course_id / "course.yaml").write_text(
        f"id: {course_id}\ntitle: t\nsummary: s\n", encoding="utf-8"
    )
    (module / "module.yaml").write_text("id: m1\ntitle: t\nsummary: s\n", encoding="utf-8")
    for stem, text in lessons.items():
        (module / f"{stem}.md").write_text(text, encoding="utf-8")


class _LivePayloads(HTMLParser):
    """Collect DOM-level script: ``<script>`` with alert, on* handlers, javascript: links."""

    def __init__(self) -> None:
        super().__init__()
        self.hits: list[str] = []
        self._script = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if value and name.startswith("on") and "alert" in value:
                self.hits.append(f"<{tag} {name}>")
            if value and name == "href" and value.lower().startswith("javascript:"):
                self.hits.append(f"<{tag} href=javascript:>")
        self._script = tag == "script"

    def handle_endtag(self, tag: str) -> None:
        self._script = False

    def handle_data(self, data: str) -> None:
        if self._script and "alert(" in data:
            self.hits.append("<script>alert")


def _live_payloads(site: Path) -> list[str]:
    hits: list[str] = []
    for page in sorted(site.rglob("*.html")):
        parser = _LivePayloads()
        parser.feed(page.read_text(encoding="utf-8"))
        hits += [f"{page.relative_to(site)}: {hit}" for hit in parser.hits]
    return hits


# -- site: XSS --------------------------------------------------------------------


@pytest.fixture
def hostile_curriculum(tmp_path: Path) -> Path:
    root = tmp_path / "curriculum"
    shutil.copytree(FIXTURE, root)
    lesson = root / "sample-course" / "m1-math-physics" / "vectors-matrices.md"
    text = lesson.read_text(encoding="utf-8")
    text = text.replace("title: 벡터와 행렬", "title: \"<img src=x onerror=alert('t')>\"")
    text = text.replace("# 벡터와 행렬", "# x\n\n<script>alert('body')</script>")
    lesson.write_text(text, encoding="utf-8")
    return root


@_open("QA-01: lesson title/body HTML reaches the built site unescaped")
def test_qa01_site_escapes_lesson_title_and_body(hostile_curriculum: Path, tmp_path: Path) -> None:
    result = _rc(hostile_curriculum, tmp_path / "d", "site", "build", "--out", str(tmp_path / "s"))
    assert result.exit_code == 0, result.output
    assert _live_payloads(tmp_path / "s") == []


@_open("QA-02: site build skips validation, javascript: resource URL becomes a link")
def test_qa02_site_build_rejects_javascript_resource_url(tmp_path: Path) -> None:
    root = tmp_path / "curriculum"
    shutil.copytree(FIXTURE, root)
    lesson = root / "sample-course" / "m1-math-physics" / "vectors-matrices.md"
    extra = (
        "estimated_minutes: 30\n"
        "resources:\n  - title: evil\n    url: \"javascript:alert('u')\"\n---\n"
    )
    text = lesson.read_text(encoding="utf-8").replace("estimated_minutes: 30\n---\n", extra, 1)
    lesson.write_text(text, encoding="utf-8")
    assert runner.invoke(app, ["validate", str(root)]).exit_code == 1  # validate does catch it
    result = _rc(root, tmp_path / "d", "site", "build", "--out", str(tmp_path / "s"))
    if result.exit_code == 0:
        assert _live_payloads(tmp_path / "s") == []
    else:
        assert _clean_user_error(result), repr(result.exception)


# -- site: destructive output paths ------------------------------------------------


@_open("QA-03: site build --out silently empties an existing directory")
def test_qa03_site_build_out_keeps_unrelated_files(tmp_path: Path) -> None:
    out = tmp_path / "out"
    out.mkdir()
    (out / "important.txt").write_text("keep me", encoding="utf-8")
    _rc(FIXTURE, tmp_path / "d", "site", "build", "--out", str(out))
    assert (out / "important.txt").exists()


@_open("QA-04: site build --src rmtree()s <src>/docs")
def test_qa04_site_build_src_keeps_existing_docs(tmp_path: Path) -> None:
    docs = tmp_path / "proj" / "docs"
    docs.mkdir(parents=True)
    (docs / "PRD.md").write_text("precious", encoding="utf-8")
    _rc(FIXTURE, tmp_path / "d", "site", "build", "--out", str(tmp_path / "s"), "--src",
        str(tmp_path / "proj"))  # fmt: skip
    assert (docs / "PRD.md").exists()


# -- content loading / validation ---------------------------------------------------


@_open("QA-05: recursive cycle check overflows the stack on a ~1000-lesson chain")
def test_qa05_validate_long_prerequisite_chain(tmp_path: Path) -> None:
    n = 1100  # l00000 needs l00001 needs ... so DFS starts at the deep end
    lessons = {
        f"l{i:05d}": _lesson(f"l{i:05d}", [f"l{i + 1:05d}"] if i < n - 1 else []) for i in range(n)
    }
    _course(tmp_path / "cur", "c1", lessons)
    result = runner.invoke(app, ["validate", str(tmp_path / "cur")])
    assert result.exit_code == 0, repr(result.exception)


@_open("QA-06: validate accepts a lesson id shared by two courses; progress then refuses")
def test_qa06_validate_rejects_lesson_id_shared_across_courses(tmp_path: Path) -> None:
    _course(tmp_path / "cur", "c1", {"x": _lesson("dup", [])})
    _course(tmp_path / "cur", "c2", {"x": _lesson("dup", [])})
    result = runner.invoke(app, ["validate", str(tmp_path / "cur")])
    assert result.exit_code == 1


@_open("QA-07: non-UTF-8 lesson file crashes validate with UnicodeDecodeError")
def test_qa07_validate_reports_non_utf8_file(tmp_path: Path) -> None:
    root = tmp_path / "curriculum"
    shutil.copytree(FIXTURE, root)
    (root / "sample-course" / "m1-math-physics" / "vectors-matrices.md").write_bytes(b"\xff\xfe")
    result = runner.invoke(app, ["validate", str(root)])
    assert _clean_user_error(result), repr(result.exception)


@pytest.mark.skipif(os.name != "posix", reason="symlinks")
@_open("QA-08: symlinked lesson outside the content root is loaded and published")
def test_qa08_symlink_outside_root_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "curriculum"
    shutil.copytree(FIXTURE, root)
    outside = tmp_path / "outside.md"
    outside.write_text(_lesson("leak", []), encoding="utf-8")
    module = root / "sample-course" / "m1-math-physics"
    (module / "leak.md").symlink_to(outside)
    meta = module / "module.yaml"
    meta.write_text(meta.read_text(encoding="utf-8") + "  - leak\n", encoding="utf-8")
    result = runner.invoke(app, ["validate", str(root)])
    assert result.exit_code == 1


# -- progress import / store ----------------------------------------------------------

_EXPORT = '{{"schema_version":1,"exported_at":"2026-11-11T00:00:00Z","lesson_progress":{lp},"sessions":{ss}}}'  # noqa: E501


@_open("QA-09: import with two open sessions escapes as sqlite3.IntegrityError")
def test_qa09_import_two_open_sessions_is_a_user_error(tmp_path: Path) -> None:
    sessions = (
        f'[{{"lesson_id":"{LESSON_ID}","started_at":"2026-11-11T00:00:00Z"}},'
        f'{{"lesson_id":"{LESSON_ID}","started_at":"2026-11-11T01:00:00Z"}}]'
    )
    file = tmp_path / "x.json"
    file.write_text(_EXPORT.format(lp="[]", ss=sessions), encoding="utf-8")
    result = _rc(FIXTURE, tmp_path / "d", "progress", "import", str(file))
    assert _clean_user_error(result), repr(result.exception)


@_open("QA-10: import accepts lesson ids that are not in the curriculum")
def test_qa10_import_rejects_unknown_lesson_ids(tmp_path: Path) -> None:
    sessions = '[{"lesson_id":"ghost","started_at":"2026-11-11T00:00:00Z"}]'
    file = tmp_path / "x.json"
    file.write_text(_EXPORT.format(lp="[]", ss=sessions), encoding="utf-8")
    result = _rc(FIXTURE, tmp_path / "d", "progress", "import", str(file))
    assert _clean_user_error(result)


@_open("QA-11: a locked database escapes as sqlite3.OperationalError after 5 s")
def test_qa11_locked_database_is_a_user_error(tmp_path: Path) -> None:
    data = tmp_path / "d"
    assert _rc(FIXTURE, data, "status").exit_code == 0
    holder = sqlite3.connect(data / "progress.db", isolation_level=None)
    holder.execute("BEGIN IMMEDIATE")
    try:
        result = _rc(FIXTURE, data, "start", LESSON_ID)
    finally:
        holder.execute("ROLLBACK")
        holder.close()
    assert _clean_user_error(result), repr(result.exception)


@_open("QA-12: an absurd duration escapes as OverflowError")
def test_qa12_log_huge_duration_is_a_user_error(tmp_path: Path) -> None:
    result = _rc(FIXTURE, tmp_path / "d", "log", LESSON_ID, "99999999999999")
    assert _clean_user_error(result), repr(result.exception)

"""No Korean in the English build (FR-9).

The reader who picks English must not be shown Korean. These tests drive the real
curriculum through the API, the static site and the CLI in English and fail on any Korean
character they find.

What they *do* allow is content that has not been translated yet: a lesson without
``<lesson>.en.md``, an activity title or resource note without ``<lesson>.en.yaml``, a quiz
question without a translation. Those fall back to the authoring language by design, and
listing them by hand would mean a list to maintain. Instead :func:`untranslatable` collects
the Korean the content itself still carries, and a finding is only accepted when its text
came from there. So the allowance shrinks on its own as translations land, and Korean from
anywhere else -- a message catalogue, a report renderer, page chrome, a label -- fails.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.settings import Settings
from robotics_curriculum.cli import app as cli_app
from robotics_curriculum.content import Course, load_courses, localized_quiz
from robotics_curriculum.content.quiz_block import QuizParseError
from robotics_curriculum.i18n.scan import Finding, find_hangul, scan_json, scan_text
from robotics_curriculum.progress import ProgressService, SqliteProgressStore
from robotics_curriculum.site import generate_project

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "curriculum"
EN = "en"

# Fields that carry a stable id rather than text. ``level`` is the value written in
# ``module.yaml``; it is the same in every language on purpose, and the reader is shown
# ``level_label`` instead (see docs/adr/0012). A JSON pointer ending in one of these is
# not a translation gap.
ID_FIELDS = ("/level", "/stage", "/id", "/lesson_id", "/module_id", "/course_id", "/card_id")


def _texts(values: Iterable[str | None]) -> Iterator[str]:
    for value in values:
        if value:
            yield value


def untranslatable(course: Course, lang: str = EN) -> set[str]:
    """Every Korean run the ``lang`` build may still legitimately show.

    One entry per run (not per field), because a finding is a run: the caller checks
    membership of what the detector matched.
    """
    runs: set[str] = set()

    def collect(*values: str | None) -> None:
        for value in _texts(values):
            runs.update(find_hangul(value))

    if not course.localized(lang).translated:
        collect(course.title, course.summary, *course.tags)
    for module in course.modules:
        if not module.localized(lang).translated:
            collect(module.title, module.summary)
        for lesson in module.lessons:
            text = lesson.localized(lang)
            if not text.translated:
                collect(lesson.title, lesson.summary, lesson.body, *lesson.objectives, *lesson.tags)
            # An activity, resource or question with no translation keeps its own text.
            collect(*(a.title for a in text.activities))
            collect(*(r.title for r in text.resources), *(r.note for r in text.resources))
            try:
                questions = localized_quiz(lesson, lang).questions
            except QuizParseError:  # pragma: no cover - rc validate rejects this
                continue
            for question in questions:
                collect(question.prompt, question.explanation, *question.choices)
                collect(*(str(a) for a in question.accepted_short))
                if question.concept is not None:
                    collect(question.concept.front, question.concept.back)
    return runs


def unexplained(findings: list[Finding], allowed: set[str]) -> list[Finding]:
    """Findings whose Korean did not come from untranslated content or an id field."""
    return [f for f in findings if f.text not in allowed and not f.where.endswith(ID_FIELDS)]


def describe(findings: list[Finding]) -> str:
    lines = [f"  {f.where}: {f.text}  ({f.context[:100]})" for f in findings[:25]]
    more = f"\n  ... and {len(findings) - 25} more" if len(findings) > 25 else ""
    return "\n".join(lines) + more


@pytest.fixture(scope="module")
def courses() -> list[Course]:
    return load_courses(CURRICULUM)


@pytest.fixture(scope="module")
def course(courses: list[Course]) -> Course:
    """The course the screens are walked on: the fully translated engineer track."""
    return next(c for c in courses if c.id == "robotics-expert")


@pytest.fixture(scope="module")
def allowed(courses: list[Course]) -> set[str]:
    """Korean that is expected in English mode: untranslated content of every course."""
    found: set[str] = set()
    for loaded in courses:
        found |= untranslatable(loaded)
    return found


# -- API -----------------------------------------------------------------------


@pytest.fixture(scope="module")
def client(tmp_path_factory: pytest.TempPathFactory) -> TestClient:
    data_dir = tmp_path_factory.mktemp("api-data")
    return TestClient(create_app(Settings(curriculum_dir=CURRICULUM, data_dir=data_dir)))


def _english(client: TestClient, path: str) -> object:
    response = client.get(path, headers={"Accept-Language": "en"})
    assert response.status_code == 200, f"{path} -> {response.status_code}"
    return response.json()


def test_the_english_api_shows_no_korean_of_its_own(
    client: TestClient, course: Course, allowed: set[str]
) -> None:
    paths = [
        "/api/v1/courses",
        f"/api/v1/courses/{course.id}",
        "/api/v1/roadmap",
        "/api/v1/resources",
        "/api/v1/search?q=robot",
        "/api/v1/progress/status",
        "/api/v1/progress/next",
        "/api/v1/reports/weekly",
    ]
    for module in course.modules:
        paths.append(f"/api/v1/modules/{module.id}")
        paths.append(f"/api/v1/reports/modules/{module.id}")
        # one lesson per module keeps the test quick while covering every module's content
        if module.lessons:
            paths.append(f"/api/v1/lessons/{module.lessons[0].id}")
            paths.append(f"/api/v1/lessons/{module.lessons[0].id}/quiz")

    findings: list[Finding] = []
    for path in paths:
        findings += scan_json(_english(client, path), f"GET {path} ")
    leaks = unexplained(findings, allowed)
    assert not leaks, f"Korean in the English API that no content explains:\n{describe(leaks)}"


def test_a_lang_query_parameter_beats_accept_language(client: TestClient) -> None:
    """The web front-end needs the language in the URL, because it caches by URL."""
    korean = client.get("/api/v1/courses", headers={"Accept-Language": "en"}, params={"lang": "ko"})
    assert find_hangul(korean.json()[0]["title"])
    assert korean.json()[0]["lang"] == "ko"

    english = client.get("/api/v1/courses", params={"lang": "en"})
    assert not find_hangul(english.json()[0]["title"])
    assert english.json()[0]["lang"] == "en"

    unknown = client.get("/api/v1/courses", params={"lang": "fr"})
    assert unknown.json()[0]["lang"] == "ko"


def test_the_level_is_an_id_and_the_label_is_translated(client: TestClient, course: Course) -> None:
    detail = _english(client, f"/api/v1/courses/{course.id}")
    stages = [s for s in detail["stages"] if s["level"]]
    assert stages, "the fixture course has no levelled module"
    for stage in stages:
        assert find_hangul(stage["level"]), "level is the stored id, not a label"
        assert not find_hangul(stage["level_label"] or "")
        for module in stage["modules"]:
            assert module["level"] == stage["level"]
            assert not find_hangul(module["level_label"] or "")


# -- static site ---------------------------------------------------------------


def test_the_english_site_shows_no_korean_of_its_own(
    tmp_path: Path, course: Course, allowed: set[str]
) -> None:
    store = SqliteProgressStore.in_dir(tmp_path / "data")
    service = ProgressService(store, [course])
    try:
        project = tmp_path / "site-en"
        generate_project(service, project, lang=EN)
    finally:
        store.close()

    findings: list[Finding] = []
    for path in sorted(project.rglob("*.md")) + sorted(project.glob("mkdocs.yml")):
        where = path.relative_to(project).as_posix()
        findings += scan_text(path.read_text(encoding="utf-8"), where)
    leaks = unexplained(findings, allowed)
    assert not leaks, f"Korean in the English site that no content explains:\n{describe(leaks)}"


# -- CLI -----------------------------------------------------------------------


CLI_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("status",),
    ("roadmap",),
    ("next",),
    ("report", "weekly", "--stdout"),
    ("report", "module", "m1-math-physics"),
)


def test_the_english_cli_shows_no_korean_of_its_own(tmp_path: Path, allowed: set[str]) -> None:
    runner = CliRunner()
    findings: list[Finding] = []
    for command in CLI_COMMANDS:
        result = runner.invoke(
            cli_app,
            ["--data-dir", str(tmp_path / "data"), "--curriculum", str(CURRICULUM), *command],
            env={"RC_LANG": "en"},
        )
        assert result.exit_code == 0, f"rc {' '.join(command)}: {result.output}"
        findings += scan_text(result.output, "rc " + " ".join(command))
    leaks = unexplained(findings, allowed)
    assert not leaks, f"Korean in the English CLI that no content explains:\n{describe(leaks)}"

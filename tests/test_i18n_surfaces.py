"""The CLI, the API and the static site in English (P2-6: --lang, RC_LANG, Accept-Language)."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner, Result

from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.settings import Settings
from robotics_curriculum.cli import app
from robotics_curriculum.content import load_courses
from robotics_curriculum.i18n import translator
from robotics_curriculum.progress import ProgressService, SqliteProgressStore
from robotics_curriculum.site import generate_project

runner = CliRunner()
ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "curriculum"
VECTORS = "m1-vectors-matrices"
ROTATION = "m1-rotation-representations"
NOW = datetime(2026, 11, 11, 12, 0, tzinfo=UTC)
EN = translator("en")
KO = translator("ko")


def rc(
    tmp_path: Path, *args: str, input: str | None = None, env: dict[str, str] | None = None
) -> Result:
    return runner.invoke(
        app,
        ["--data-dir", str(tmp_path / "data"), "--curriculum", str(FIXTURE), *args],
        input=input,
        env=env,
    )


# -- CLI -----------------------------------------------------------------------


def test_status_is_korean_by_default_and_english_with_lang(tmp_path: Path) -> None:
    korean = rc(tmp_path, "status")
    assert korean.exit_code == 0, korean.output
    assert KO("cli.timer.none") in korean.output
    assert "열린 타이머" in korean.output

    english = rc(tmp_path, "--lang", "en", "status")
    assert english.exit_code == 0, english.output
    assert EN("cli.timer.none") in english.output
    assert "Running timer: none" in english.output
    assert "열린 타이머" not in english.output
    assert "Due today: 0 cards" in english.output


def test_rc_lang_environment_variable_selects_english(tmp_path: Path) -> None:
    result = rc(tmp_path, "status", env={"RC_LANG": "en-US"})
    assert result.exit_code == 0, result.output
    assert "Running timer: none" in result.output


def test_explicit_lang_beats_the_environment(tmp_path: Path) -> None:
    result = rc(tmp_path, "--lang", "ko", "status", env={"RC_LANG": "en"})
    assert "열린 타이머" in result.output


def test_unknown_language_falls_back_to_korean(tmp_path: Path) -> None:
    result = rc(tmp_path, "--lang", "fr", "status")
    assert result.exit_code == 0, result.output
    assert "열린 타이머" in result.output


def test_errors_and_warnings_follow_the_language(tmp_path: Path) -> None:
    missing = rc(tmp_path, "--lang", "en", "start", "nope")
    assert missing.exit_code == 1
    assert "error: unknown lesson 'nope'" in missing.output

    noted = rc(tmp_path, "--lang", "en", "start", "m2-dh-parameters")
    assert noted.exit_code == 0, noted.output
    assert EN("cli.note_prereq", ids=VECTORS) in noted.output


def test_done_and_next_are_translated(tmp_path: Path) -> None:
    rc(tmp_path, "log", VECTORS, "30m")
    done = rc(tmp_path, "--lang", "en", "done", VECTORS, "-u", "4")
    assert done.exit_code == 0, done.output
    assert done.output.startswith("done ")
    assert ", understanding 4" in done.output
    assert "now next in the recommended order: " in done.output

    nxt = rc(tmp_path, "--lang", "en", "next")
    assert "difficulty" in nxt.output and "start: rc start" in nxt.output


def test_quiz_and_review_sessions_are_translated(tmp_path: Path) -> None:
    quiz = rc(tmp_path, "--lang", "en", "quiz", ROTATION, input="2\n1,2\no\n+1\n")
    assert quiz.exit_code == 0, quiz.output
    assert "(single choice)" in quiz.output
    assert "score 4/4 (100%)" in quiz.output
    assert "1 new card(s)" in quiz.output
    assert "why:" in quiz.output

    review = rc(tmp_path, "--lang", "en", "review", input="\n3\n")
    assert review.exit_code == 0, review.output
    assert "Reviewing 1 card(s)" in review.output
    assert "press Enter for the back" in review.output
    assert "1 again · 2 hard · 3 good · 4 easy" in review.output
    assert "next review:" in review.output
    assert "reviewed 1" in review.output

    empty = rc(tmp_path, "--lang", "en", "review")
    assert "no cards are due today" in empty.output


def test_resources_and_roadmap_labels_are_translated(tmp_path: Path) -> None:
    korean = rc(tmp_path, "resources", "m2-dh-parameters")
    assert "[교재]" in korean.output
    english = rc(tmp_path, "--lang", "en", "resources", "m2-dh-parameters")
    assert "[Books]" in english.output

    roadmap = rc(tmp_path, "--lang", "en", "roadmap")
    assert roadmap.exit_code == 0, roadmap.output
    assert roadmap.output.startswith("[x] done")

    show = rc(tmp_path, "--lang", "en", "show", VECTORS)
    assert "Module: " in show.output and "Objectives:" in show.output


# -- API -----------------------------------------------------------------------


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    settings = Settings(curriculum_dir=FIXTURE, data_dir=tmp_path / "data")
    return TestClient(create_app(settings, clock=lambda: NOW))


def test_problem_titles_follow_accept_language(client: TestClient) -> None:
    korean = client.get("/api/v1/lessons/nope")
    assert korean.status_code == 404
    assert korean.json()["title"] == KO("api.problem.404")

    english = client.get("/api/v1/lessons/nope", headers={"Accept-Language": "en-GB,en;q=0.9"})
    assert english.json()["title"] == "Not Found"

    weighted = client.get("/api/v1/lessons/nope", headers={"Accept-Language": "fr;q=0.9,en;q=0.5"})
    assert weighted.json()["title"] == "Not Found"

    unsupported = client.get("/api/v1/lessons/nope", headers={"Accept-Language": "fr"})
    assert unsupported.json()["title"] == KO("api.problem.404")


def test_validation_problem_detail_follows_accept_language(client: TestClient) -> None:
    body = {"lesson_id": VECTORS, "minutes": -1}
    korean = client.post("/api/v1/progress/log", json=body)
    assert korean.status_code == 422
    assert korean.json()["detail"] == KO("api.validation", count=1)

    english = client.post("/api/v1/progress/log", json=body, headers={"Accept-Language": "en"})
    assert english.json()["detail"] == "1 invalid field(s)"
    assert english.json()["title"] == "Unprocessable Content"


def test_conflict_title_is_translated(client: TestClient) -> None:
    assert client.post("/api/v1/progress/start", json={"lesson_id": VECTORS}).status_code == 201
    conflict = client.post(
        "/api/v1/progress/start", json={"lesson_id": VECTORS}, headers={"Accept-Language": "en"}
    )
    assert conflict.status_code == 409
    assert conflict.json()["title"] == "Conflict"
    assert conflict.json()["detail"]  # the core message stays as the service wrote it


# -- static site ---------------------------------------------------------------


@pytest.fixture
def service(tmp_path: Path) -> ProgressService:
    root = tmp_path / "curriculum"
    shutil.copytree(FIXTURE, root)
    store = SqliteProgressStore.in_dir(tmp_path / "rcdata")
    svc = ProgressService(store, load_courses(root), clock=lambda: NOW)
    svc.log(VECTORS, 40)
    svc.done(VECTORS, understanding=4)
    yield svc
    store.close()


def test_site_pages_can_be_built_in_english(service: ProgressService, tmp_path: Path) -> None:
    project = tmp_path / "en-site"
    generate_project(service, project, now=NOW, lang="en")
    index = (project / "docs" / "index.md").read_text(encoding="utf-8")
    assert "## Where you are" in index
    assert "## At a glance" in index
    assert "Study time this week" in index
    assert "Due today" in index
    assert "현재 위치" not in index and "오늘 복습" not in index

    roadmap = (project / "docs" / "roadmap.md").read_text(encoding="utf-8")
    assert roadmap.startswith("# Roadmap")
    assert "done</span>" in roadmap and "not started</span>" in roadmap
    assert "Legend: ■ done" in roadmap

    lesson = (
        project / "docs" / "modules/m1-math-physics/m1-rotation-representations.md"
    ).read_text(encoding="utf-8")
    assert "**Objectives**" in lesson
    assert "## How to study this stage" in lesson
    assert "## Study resources" in lesson
    assert "(single choice)" in lesson  # quiz question kind
    assert '??? note "Answer and explanation"' in lesson
    assert "**Answer:**" in lesson
    # lesson content itself stays in Korean: only the chrome is translated
    assert "회전 표현" in lesson

    config = (project / "mkdocs.yml").read_text(encoding="utf-8")
    assert "language: en" in config
    assert "Dashboard: index.md" in config and "Resources: resources.md" in config

    resources = (project / "docs" / "resources.md").read_text(encoding="utf-8")
    assert resources.startswith("# Resources")
    assert "## Books" in resources


def test_site_defaults_to_korean(service: ProgressService, tmp_path: Path) -> None:
    project = tmp_path / "ko-site"
    generate_project(service, project, now=NOW)
    index = (project / "docs" / "index.md").read_text(encoding="utf-8")
    assert "## 현재 위치" in index and "오늘 복습" in index
    config = (project / "mkdocs.yml").read_text(encoding="utf-8")
    assert "language: ko" in config and "대시보드: index.md" in config

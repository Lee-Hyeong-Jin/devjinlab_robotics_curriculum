"""Regression tests for fixes tracked as GitHub issues (the number is in each test's name)."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest

from robotics_curriculum.progress import ProgressService, SqliteProgressStore
from robotics_curriculum.report.weekly import IsoWeek, build_weekly_report

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "curriculum"
NOW = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)
EXPERT = "robotics-expert"
RESEARCH = "robotics-research"


@pytest.fixture
def service(tmp_path: Path) -> Iterator[ProgressService]:
    """A learner on the real curriculum, which has two courses."""
    store = SqliteProgressStore.in_dir(tmp_path)
    svc = ProgressService(store, ProgressService.load_curriculum(CURRICULUM), clock=lambda: NOW)
    yield svc
    store.close()


def _first_lesson(service: ProgressService, course_id: str) -> str:
    return next(s.lesson.id for s in service.status(course_id))


# -- #31: next week's suggestions mixed in another course's lessons ---------------------------


def test_issue_31_a_new_learner_is_offered_the_first_course_only(
    service: ProgressService,
) -> None:
    assert [c.id for c in service.courses][0] == EXPERT
    assert service.focus_course_ids() == [EXPERT]
    assert {s.course.id for s in service.next_lessons()} == {EXPERT}


def test_issue_31_suggestions_stay_in_the_course_being_studied(service: ProgressService) -> None:
    service.done(_first_lesson(service, EXPERT), understanding=4)
    assert service.focus_course_ids() == [EXPERT]
    # The research track's opening lessons have no prerequisites, so they used to outrank the
    # expert course's next lessons.
    assert {s.course.id for s in service.next_lessons(limit=10)} == {EXPERT}
    report = build_weekly_report(service, IsoWeek.of(NOW.date()), today=NOW.date(), tz=UTC)
    suggested = {line.lesson_id for line in report.next_lessons}
    expert_ids = {s.lesson.id for s in service.status(EXPERT)}
    assert suggested and suggested <= expert_ids


def test_issue_31_a_second_course_joins_once_it_is_started(service: ProgressService) -> None:
    service.done(_first_lesson(service, EXPERT), understanding=4)
    service.start(_first_lesson(service, RESEARCH))
    assert service.focus_course_ids() == [EXPERT, RESEARCH]
    assert {s.course.id for s in service.next_lessons()} == {EXPERT, RESEARCH}
    # Asking for one course by name is unchanged.
    assert {s.course.id for s in service.next_lessons(RESEARCH)} == {RESEARCH}
    assert {s.course.id for s in service.next_lessons(EXPERT)} == {EXPERT}


# -- #39: a completion could not be taken back --------------------------------------------------


def test_issue_39_undo_done_puts_the_lesson_back_in_progress(service: ProgressService) -> None:
    lesson = _first_lesson(service, EXPERT)
    service.log(lesson, 25, note="worked through the examples")
    service.done(lesson, understanding=2, note="marked by mistake")
    undone = service.undo_done(lesson)
    assert undone.status == "in_progress"
    assert undone.completed_at is None
    # The rating belonged to the completion; the work that happened is kept.
    assert undone.understanding is None
    assert undone.note == "marked by mistake"
    assert undone.total_seconds == 25 * 60
    assert service.status(EXPERT)[0].status == "in_progress"
    # Completing it again is an ordinary completion.
    again, _ = service.done(lesson, understanding=5)
    assert again.status == "done" and again.completed_at is not None


def test_issue_39_only_a_done_lesson_can_be_undone(service: ProgressService) -> None:
    from robotics_curriculum.progress import ProgressError

    lesson = _first_lesson(service, EXPERT)
    with pytest.raises(ProgressError, match="not marked done"):
        service.undo_done(lesson)
    service.start(lesson)
    with pytest.raises(ProgressError, match="not marked done"):
        service.undo_done(lesson)
    with pytest.raises(ProgressError):
        service.undo_done("no-such-lesson")


def test_issue_39_api_and_cli(tmp_path: Path) -> None:
    from fastapi.testclient import TestClient
    from typer.testing import CliRunner

    from robotics_curriculum.api.app import create_app
    from robotics_curriculum.api.settings import Settings
    from robotics_curriculum.cli import app as cli_app

    client = TestClient(
        create_app(Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path), clock=lambda: NOW)
    )
    lesson = "m1-vectors-matrices"
    refused = client.post("/api/v1/progress/undone", json={"lesson_id": lesson})
    assert refused.status_code == 409
    assert client.post("/api/v1/progress/undone", json={"lesson_id": "nope"}).status_code == 404
    client.post("/api/v1/progress/done", json={"lesson_id": lesson, "understanding": 4})
    undone = client.post("/api/v1/progress/undone", json={"lesson_id": lesson})
    assert undone.status_code == 200, undone.text
    assert undone.json()["status"] == "in_progress" and undone.json()["completed_at"] is None

    client.post("/api/v1/progress/done", json={"lesson_id": lesson})
    base = ["--data-dir", str(tmp_path), "--curriculum", str(CURRICULUM), "--lang", "en"]
    result = CliRunner().invoke(cli_app, [*base, "undone", lesson])
    assert result.exit_code == 0, result.output
    assert "back in progress" in result.output
    again = CliRunner().invoke(cli_app, [*base, "undone", lesson])
    assert again.exit_code != 0

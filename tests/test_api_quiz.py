"""Quiz, review and dashboard endpoints (P2-1 + P1-2) through TestClient."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.settings import Settings

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "tests" / "fixtures" / "curriculum"
ROTATION = "m1-rotation-representations"
VECTORS = "m1-vectors-matrices"
PROBLEM = "application/problem+json"
T0 = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)
TODAY = T0.astimezone().date().isoformat()
TOMORROW = (T0.astimezone().date() + timedelta(days=1)).isoformat()
RIGHT = {"q1": "2", "q2": "1,2", "q3": "o", "q4": "+1"}
WRONG_Q1 = {**RIGHT, "q1": "1"}


class Clock:
    def __init__(self) -> None:
        self.now = T0

    def __call__(self) -> datetime:
        return self.now


@pytest.fixture
def clock() -> Clock:
    return Clock()


@pytest.fixture
def client(tmp_path: Path, clock: Clock) -> TestClient:
    settings = Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path / "data")
    return TestClient(create_app(settings, clock=clock))


def assert_problem(response: Any, status: int) -> dict[str, Any]:
    assert response.status_code == status, response.text
    assert response.headers["content-type"].startswith(PROBLEM)
    body: dict[str, Any] = response.json()
    assert body["status"] == status
    return body


def submit(client: TestClient, answers: dict[str, str], **extra: Any) -> Any:
    return client.post(
        "/api/v1/quiz/runs", json={"lesson_id": ROTATION, "answers": answers, **extra}
    )


# -- reading a quiz ------------------------------------------------------------


def test_get_lesson_quiz_hides_answers(client: TestClient) -> None:
    response = client.get(f"/api/v1/lessons/{ROTATION}/quiz")
    assert response.status_code == 200
    body = response.json()
    assert body["lesson_id"] == ROTATION
    assert body["activity_id"] == "m1-rotation-representations-quiz"
    assert [q["id"] for q in body["questions"]] == ["q1", "q2", "q3", "q4"]
    assert body["questions"][0]["type"] == "single"
    assert body["questions"][0]["choices"][1] == "$R^T$"
    assert body["questions"][3]["choices"] == []  # short answer
    serialized = response.text
    for secret in ("answer", "explanation", "concept", "직교 행렬이므로"):
        assert secret not in serialized


def test_get_quiz_404_for_unknown_lesson_or_lesson_without_quiz(client: TestClient) -> None:
    assert_problem(client.get("/api/v1/lessons/nope/quiz"), 404)
    body = assert_problem(client.get(f"/api/v1/lessons/{VECTORS}/quiz"), 404)
    assert "no quiz block" in body["detail"]


# -- submitting ----------------------------------------------------------------


def test_submit_run_grades_stores_and_creates_cards(client: TestClient) -> None:
    response = submit(client, WRONG_Q1)
    assert response.status_code == 201, response.text
    body = response.json()
    assert (body["correct"], body["total"], body["percent"]) == (3, 4, 75)
    assert body["seconds"] == 0  # the fixed clock does not advance
    q1 = next(a for a in body["answers"] if a["question_id"] == "q1")
    assert (q1["correct"], q1["given"], q1["correct_answer"]) == (False, "1", "2. $R^T$")
    assert q1["explanation"].startswith("회전 행렬은 직교 행렬")
    assert sorted(body["new_card_ids"]) == [f"{ROTATION}-concept-q1", f"{ROTATION}-quiz-q1"]

    # the attempt is recorded: it shows up in the dashboard and in the review queue
    status = client.get("/api/v1/progress/status").json()
    assert status["due_cards"] == 2
    again = submit(client, WRONG_Q1).json()
    assert again["new_card_ids"] == []  # no duplicate cards


def test_submit_run_rejects_bad_submissions(client: TestClient) -> None:
    assert_problem(submit(client, {**RIGHT, "q9": "1"}), 422)
    missing = assert_problem(submit(client, {"q1": "2"}), 422)
    assert "missing answer(s) for: q2, q3, q4" in missing["detail"]
    ungradable = assert_problem(submit(client, {**RIGHT, "q1": "nope"}), 422)
    assert "question 'q1'" in ungradable["detail"]
    assert_problem(submit(client, {}), 422)  # empty answers fail schema validation
    assert_problem(
        client.post("/api/v1/quiz/runs", json={"lesson_id": "nope", "answers": {"q1": "2"}}), 404
    )
    assert_problem(
        client.post("/api/v1/quiz/runs", json={"lesson_id": VECTORS, "answers": {"q1": "2"}}), 404
    )


def test_partial_submission_is_allowed_explicitly(client: TestClient) -> None:
    body = submit(client, {"q3": "x"}, partial=True).json()
    assert (body["correct"], body["total"]) == (0, 1)
    assert body["new_card_ids"] == [f"{ROTATION}-quiz-q3"]


# -- review --------------------------------------------------------------------


def test_review_due_and_rating(client: TestClient, clock: Clock) -> None:
    assert client.get("/api/v1/review/due").json() == []
    submit(client, WRONG_Q1)

    due = client.get("/api/v1/review/due").json()
    assert [c["card_id"] for c in due] == [f"{ROTATION}-concept-q1", f"{ROTATION}-quiz-q1"]
    assert due[0]["due"] == TODAY and due[0]["source"] == "concept"
    assert due[0]["lesson_id"] == ROTATION and due[0]["interval_days"] == 0
    assert len(client.get("/api/v1/review/due", params={"limit": 1}).json()) == 1
    assert client.get("/api/v1/review/due", params={"lesson_id": VECTORS}).json() == []
    assert_problem(client.get("/api/v1/review/due", params={"lesson_id": "nope"}), 404)

    rated = client.post(f"/api/v1/review/{ROTATION}-quiz-q1", json={"rating": "good"})
    assert rated.status_code == 200, rated.text
    state = rated.json()
    assert (state["repetitions"], state["interval_days"]) == (1, 1)
    assert state["due"] == TOMORROW and state["due_tomorrow"] == 1
    assert state["ease"] == 2.5
    assert [c["card_id"] for c in client.get("/api/v1/review/due").json()] == [
        f"{ROTATION}-concept-q1"
    ]

    # again resets the interval; tomorrow it is due once more
    clock.now = T0 + timedelta(days=1)
    worse = client.post(f"/api/v1/review/{ROTATION}-quiz-q1", json={"rating": "again"}).json()
    assert worse["interval_days"] == 1 and worse["ease"] < 2.5


def test_review_rating_errors(client: TestClient) -> None:
    submit(client, WRONG_Q1)
    assert_problem(client.post("/api/v1/review/nope", json={"rating": "good"}), 404)
    assert_problem(
        client.post(f"/api/v1/review/{ROTATION}-quiz-q1", json={"rating": "perfect"}), 422
    )


# -- dashboard fields on /progress/status --------------------------------------


def test_status_carries_the_dashboard_aggregate(client: TestClient) -> None:
    client.post("/api/v1/progress/log", json={"lesson_id": VECTORS, "minutes": 40})
    client.post("/api/v1/progress/done", json={"lesson_id": VECTORS, "understanding": 4})
    submit(client, WRONG_Q1)

    body = client.get("/api/v1/progress/status").json()
    stages = {s["level"]: s for s in body["stages"]}
    assert (stages["기초"]["lessons_done"], stages["기초"]["lessons_total"]) == (1, 2)
    assert stages["기초"]["progress"] == 50
    assert stages["기초"]["module_ids"] == ["m1-math-physics"]
    assert "단계 미지정" in stages
    assert body["week"] == {"start": "2026-11-09", "minutes": 40, "sessions": 1}
    assert body["streak_days"] == 1
    assert body["due_cards"] == 2
    assert len(body["lessons"]) == 3  # unchanged P2-1 fields still there
    assert body["open_session"] is None


def test_status_dashboard_is_empty_without_progress(client: TestClient) -> None:
    body = client.get("/api/v1/progress/status").json()
    assert body["due_cards"] == 0 and body["streak_days"] == 0
    assert body["week"]["minutes"] == 0
    assert [s["level"] for s in body["stages"]] == ["기초", "단계 미지정"]
    assert all(s["lessons_done"] == 0 for s in body["stages"])


def test_status_course_filter_keeps_dashboard_fields(client: TestClient) -> None:
    body = client.get("/api/v1/progress/status", params={"course": "sample-course"}).json()
    assert body["due_cards"] == 0
    assert len(body["stages"]) == 2

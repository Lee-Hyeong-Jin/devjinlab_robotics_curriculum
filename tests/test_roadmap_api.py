"""GET /api/v1/roadmap: level -> module -> lesson states and progress (frontend P2-4)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.settings import Settings

CURRICULUM = Path(__file__).resolve().parent / "fixtures" / "curriculum"
COURSE = "sample-course"
VECTORS = "m1-vectors-matrices"
ROTATION = "m1-rotation-representations"


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    settings = Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path)
    return TestClient(create_app(settings, clock=lambda: datetime(2026, 11, 11, tzinfo=UTC)))


def _roadmap(client: TestClient) -> dict[str, Any]:
    r = client.get("/api/v1/roadmap")
    assert r.status_code == 200, r.text
    return dict(r.json())


def test_roadmap_states_and_progress(client: TestClient) -> None:
    stages = _roadmap(client)["stages"]
    assert [(s["course_id"], s["level"]) for s in stages] == [(COURSE, "기초"), (COURSE, None)]
    m1, m2 = stages[0]["modules"][0], stages[1]["modules"][0]
    # Nothing is locked any more (ADR 0015): an untouched lesson is simply available.
    assert [(les["id"], les["state"]) for les in m1["lessons"]] == [
        (VECTORS, "available"),
        (ROTATION, "available"),
    ]
    assert (m1["state"], m1["progress"]) == ("available", 0)
    assert (m2["state"], m2["lessons"][0]["state"]) == ("available", "available")

    client.post("/api/v1/progress/log", json={"lesson_id": VECTORS, "minutes": 10})
    m1 = _roadmap(client)["stages"][0]["modules"][0]
    assert (m1["state"], m1["lessons"][0]["state"]) == ("in_progress", "in_progress")

    client.post("/api/v1/progress/done", json={"lesson_id": VECTORS})
    stages = _roadmap(client)["stages"]
    m1 = stages[0]["modules"][0]
    assert m1["progress"] == 0.5 and m1["state"] == "in_progress"
    assert m1["lessons"][1]["state"] == "available"
    assert stages[0]["progress"] == 0.5
    assert stages[1]["modules"][0]["state"] == "available"

    client.post("/api/v1/progress/done", json={"lesson_id": ROTATION})
    m1 = _roadmap(client)["stages"][0]["modules"][0]
    assert (m1["state"], m1["progress"]) == ("done", 1)


def test_roadmap_course_filter(client: TestClient) -> None:
    assert client.get("/api/v1/roadmap", params={"course": COURSE}).status_code == 200
    r = client.get("/api/v1/roadmap", params={"course": "nope"})
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/problem+json")

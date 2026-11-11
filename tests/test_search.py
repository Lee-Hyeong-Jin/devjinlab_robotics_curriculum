"""Content search: core function and GET /api/v1/search."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.settings import Settings
from robotics_curriculum.content import load_courses
from robotics_curriculum.content.models import Course, Lesson, Module, Resource, ResourceKind
from robotics_curriculum.content.search import search

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "curriculum"


def _course() -> list[Course]:
    def lesson(lid: str, title: str, **kw: object) -> Lesson:
        base: dict[str, object] = {
            "id": lid,
            "title": title,
            "summary": "요약",
            "objectives": ["목표"],
            "difficulty": 1,
            "estimated_minutes": 10,
        }
        return Lesson.model_validate({**base, **kw})

    lessons = [
        lesson("a", "PID 제어", tags=["control"], summary="비례 적분 미분 제어기를 다룬다."),
        lesson("b", "경로 추종", tags=["pid"], objectives=["Pure pursuit 구현"]),
        lesson("c", "칼만 필터", summary="센서 융합에서 PID 와 비교한다."),
        lesson(
            "d",
            "기구학",
            resources=[
                Resource(title="Modern Robotics", kind=ResourceKind.BOOK, note="Ch. 4 PID tuning"),
            ],
        ),
    ]
    module = Module(id="m", title="M", summary="s", lessons=lessons)
    return [Course(id="c1", title="C", summary="s", modules=[module])]


def test_ranking_and_kinds() -> None:
    hits = search(_course(), "pid")
    assert [(h.kind, h.id) for h in hits] == [
        ("lesson", "a"),  # title
        ("lesson", "b"),  # tag
        ("lesson", "c"),  # summary
        ("resource", "d#0"),  # resource note
    ]
    assert hits[-1].lesson_id == "d" and hits[-1].title == "Modern Robotics"
    assert "PID" in hits[2].snippet


def test_all_words_must_match_and_case_folding() -> None:
    assert [h.id for h in search(_course(), "PURE pursuit")] == ["b"]
    assert search(_course(), "pid 칼만")[0].id == "c"
    assert search(_course(), "pid zebra") == []
    assert search(_course(), "   ") == []
    assert len(search(_course(), "pid", limit=2)) == 2


def test_snippet_is_trimmed() -> None:
    long = "x" * 200 + " needle " + "y" * 200
    lesson = Lesson(
        id="l", title="t", summary=long, objectives=["o"], difficulty=1, estimated_minutes=1
    )
    course = Course(
        id="c",
        title="C",
        summary="s",
        modules=[Module(id="m", title="M", summary="s", lessons=[lesson])],
    )
    snippet = search([course], "needle")[0].snippet
    assert snippet.startswith("…") and snippet.endswith("…") and "needle" in snippet


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    return TestClient(create_app(Settings(curriculum_dir=FIXTURE, data_dir=tmp_path)))


def test_search_endpoint(client: TestClient) -> None:
    hits = client.get("/api/v1/search", params={"q": "회전"}).json()
    assert hits[0] == {
        "kind": "lesson",
        "id": "m1-rotation-representations",
        "title": "회전 표현",
        "snippet": hits[0]["snippet"],
        "lesson_id": "m1-rotation-representations",
    }
    book = client.get("/api/v1/search", params={"q": "textbook"}).json()
    assert [h["kind"] for h in book] == ["resource"]
    assert client.get("/api/v1/search", params={"q": "없는단어"}).json() == []
    assert client.get("/api/v1/search", params={"q": "a"}).status_code == 422
    assert client.get("/api/v1/search").status_code == 422
    assert len(load_courses(FIXTURE)) == 1

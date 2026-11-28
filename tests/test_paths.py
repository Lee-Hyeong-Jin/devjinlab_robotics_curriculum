"""Goal-based learning paths (#52): the lessons a goal needs, in an order that can be followed."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.settings import Settings
from robotics_curriculum.cli import app as cli_app
from robotics_curriculum.content import check
from robotics_curriculum.content.models import Course, Goal, Lesson, Module
from robotics_curriculum.content.paths import (
    PathError,
    find_goal,
    goal_path,
    prerequisite_closure,
    resolve_path,
)
from robotics_curriculum.progress import ProgressService, SqliteProgressStore

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "curriculum"
NOW = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)


def _lesson(lesson_id: str, *prerequisites: str, minutes: int = 30) -> Lesson:
    return Lesson(
        id=lesson_id,
        title=lesson_id,
        summary="s",
        objectives=["o"],
        prerequisites=list(prerequisites),
        estimated_minutes=minutes,
        difficulty=1,
        body="",
    )


def _course(*lessons: Lesson, goals: list[Goal] | None = None) -> Course:
    module = Module(id="mod", title="m", summary="s", lessons=list(lessons))
    return Course(id="course", title="c", summary="s", modules=[module], goals=goals or [])


#   a ── b ── d ── f          e and c are side branches: f needs a, b, d only.
#    └── c    └── e
GRAPH = _course(
    _lesson("a", minutes=10),
    _lesson("b", "a", minutes=20),
    _lesson("c", "a", minutes=40),
    _lesson("d", "b", minutes=30),
    _lesson("e", "d", minutes=50),
    _lesson("f", "d", minutes=60),
)


def test_a_path_is_the_target_and_what_it_depends_on_in_teaching_order() -> None:
    path = prerequisite_closure(GRAPH, ["f"])
    assert path.lesson_ids == ("a", "b", "d", "f")
    assert path.total_minutes == 10 + 20 + 30 + 60
    assert path.remaining_minutes(["a", "b"]) == 90
    assert path.remaining_minutes([]) == path.total_minutes
    # A lesson with no prerequisite is its own path.
    assert prerequisite_closure(GRAPH, ["a"]).lesson_ids == ("a",)


def test_several_targets_share_their_prerequisites() -> None:
    path = prerequisite_closure(GRAPH, ["c", "e", "c"])
    assert path.targets == ("c", "e")
    assert path.lesson_ids == ("a", "b", "c", "d", "e")


def test_a_prerequisite_taught_later_is_still_placed_first() -> None:
    """Teaching order alone would put x before the lesson it depends on."""
    course = _course(_lesson("x", "y"), _lesson("y"), _lesson("z", "x"))
    assert prerequisite_closure(course, ["z"]).lesson_ids == ("y", "x", "z")


def test_a_cycle_does_not_hang_and_unknown_targets_are_refused() -> None:
    looped = _course(_lesson("p", "q"), _lesson("q", "p"))
    assert sorted(prerequisite_closure(looped, ["p"]).lesson_ids) == ["p", "q"]
    with pytest.raises(PathError, match="not a lesson"):
        prerequisite_closure(GRAPH, ["nope"])
    with pytest.raises(PathError, match="at least one"):
        prerequisite_closure(GRAPH, [])


def test_goals_resolve_before_lessons() -> None:
    goal = Goal(id="reach-f", title="Reach F", summary="s", targets=["f"])
    course = _course(*GRAPH.modules[0].lessons, goals=[goal])
    assert find_goal(course, "reach-f") is goal and find_goal(course, "x") is None
    assert goal_path(course, goal).goal is goal
    found_course, by_goal = resolve_path([course], "reach-f")
    assert found_course is course and by_goal.lesson_ids == ("a", "b", "d", "f")
    assert resolve_path([course], "e")[1].lesson_ids == ("a", "b", "d", "e")
    with pytest.raises(PathError, match="goals: reach-f"):
        resolve_path([course], "nothing")


def test_validation_refuses_goals_that_point_nowhere(tmp_path: Path) -> None:
    bad = _course(
        _lesson("a"),
        goals=[
            Goal(id="g", title="t", summary="s", targets=["a"]),
            Goal(id="g", title="t", summary="s", targets=["missing"]),
        ],
    )
    from robotics_curriculum.content.validate import validate_course

    messages = [error.message for error in validate_course(bad)]
    assert any("duplicate goal id 'g'" in m for m in messages)
    assert any("targets 'missing'" in m for m in messages)


def test_the_real_course_has_goals_shorter_than_the_course() -> None:
    courses, problems = check(CURRICULUM)
    assert not [p for p in problems if "goal" in p.message]
    expert = next(c for c in courses if c.id == "robotics-expert")
    whole = sum(lesson.estimated_minutes for lesson in expert.iter_lessons())
    assert {goal.id for goal in expert.goals} >= {"navigation", "manipulation", "robot-learning"}
    for goal in expert.goals:
        path = goal_path(expert, goal)
        assert set(goal.targets) <= set(path.lesson_ids)
        assert 0 < path.total_minutes < whole, goal.id
        # Every goal reads in both languages.
        assert expert.localized_goal(goal, "en") != (goal.title, goal.summary), goal.id
        # A lesson never comes before one of its prerequisites.
        seen: set[str] = set()
        for lesson in path.lessons:
            assert set(lesson.prerequisites) <= seen, (goal.id, lesson.id)
            seen.add(lesson.id)
    # Navigation does not need manipulation, and the other way round.
    navigation = goal_path(expert, find_goal(expert, "navigation"))  # type: ignore[arg-type]
    assert not any(lesson_id.startswith("m7-") for lesson_id in navigation.lesson_ids)


def test_next_lessons_stay_on_the_path(tmp_path: Path) -> None:
    store = SqliteProgressStore.in_dir(tmp_path)
    service = ProgressService(store, ProgressService.load_curriculum(CURRICULUM), clock=lambda: NOW)
    _course_, path = resolve_path(service.courses, "mobile-robot")
    suggested = [s.lesson.id for s in service.next_lessons(within=path.lesson_ids)]
    assert suggested and set(suggested) <= set(path.lesson_ids)
    for lesson_id in path.lesson_ids:
        service.done(lesson_id)
    assert service.next_lessons(within=path.lesson_ids) == []
    store.close()


def test_cli_and_api(tmp_path: Path) -> None:
    base = ["--data-dir", str(tmp_path), "--curriculum", str(CURRICULUM), "--lang", "en"]
    runner = CliRunner()
    listed = runner.invoke(cli_app, [*base, "path"])
    assert listed.exit_code == 0 and "navigation" in listed.output
    shown = runner.invoke(cli_app, [*base, "path", "mobile-robot"])
    assert shown.exit_code == 0, shown.output
    assert "0/6 lessons done" in shown.output and "m3-path-following" in shown.output
    assert "m7-" not in shown.output
    assert runner.invoke(cli_app, [*base, "path", "m2-dh-parameters"]).exit_code == 0
    assert runner.invoke(cli_app, [*base, "path", "no-such-thing"]).exit_code == 1
    onpath = runner.invoke(cli_app, [*base, "next", "--goal", "mobile-robot", "-n", "10"])
    assert onpath.exit_code == 0 and "m2-" not in onpath.output
    assert runner.invoke(cli_app, [*base, "next", "--goal", "nope"]).exit_code == 1

    client = TestClient(
        create_app(
            Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path / "api"), clock=lambda: NOW
        )
    )
    course = client.get("/api/v1/courses/robotics-expert").json()
    goals = {goal["id"]: goal for goal in course["goals"]}
    assert goals["mobile-robot"]["title"] == "Make a robot move"
    assert goals["mobile-robot"]["lesson_ids"][-1] == "m3-path-following"
    assert goals["mobile-robot"]["estimated_minutes"] == 500
    first = goals["mobile-robot"]["lessons"][0]
    assert first == {
        "id": "m1-vectors-matrices",
        "title": "Vectors and matrices",
        "module_id": "m1-math-physics",
        "estimated_minutes": 60,
    }
    korean = client.get("/api/v1/courses/robotics-expert?lang=ko").json()["goals"][0]
    assert korean["title"] == "움직이는 로봇 제어하기"
    # A course without goals answers with an empty list.
    assert client.get("/api/v1/courses/robotics-research").json()["goals"] == []

    nxt = client.get("/api/v1/progress/next", params={"goal": "mobile-robot", "n": 10}).json()
    assert {n["lesson"]["id"] for n in nxt} <= set(goals["mobile-robot"]["lesson_ids"])
    assert client.get("/api/v1/progress/next", params={"goal": "nope"}).status_code == 404

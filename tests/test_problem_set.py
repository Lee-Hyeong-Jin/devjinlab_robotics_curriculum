"""` ```problemset ` blocks: parsing, validation and how the site renders them.

A problem set is deliberately not a quiz: nothing is graded and nothing becomes a flashcard
(lesson-standard.md §10-11). These tests hold that line.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from robotics_curriculum.cli import app
from robotics_curriculum.content import (
    ProblemSetParseError,
    has_problem_set,
    load_course,
    parse_problem_sets,
    shape_advice,
    validate_course,
)

runner = CliRunner()

FOUR = """```problemset
activity: l1-exercise
problems:
  - id: p1
    type: derivation
    stars: 2
    prompt: "오일러-라그랑주 식을 유도하라."
    refers_to: ["R2"]
    solution_policy: sketch
    solution: "운동 에너지에서 시작한다."
  - id: p2
    type: proof
    stars: 3
    prompt: "질량 행렬이 양정부호임을 보이라."
    solution_policy: rubric
    solution: "양정부호 정의를 쓴다."
  - id: p3
    type: numerical
    stars: 1
    prompt: "tau 를 계산하라."
    solution_policy: answer
    solution: "4.2"
    tolerance: 1.0e-3
  - id: p4
    type: implementation
    stars: 2
    prompt: "역동역학을 구현하라."
    solution_policy: full
    solution: "코드는 ..."
```
"""


def write_course(root: Path, body: str, *, activities: str | None = None) -> Path:
    course = root / "course"
    module = course / "mod"
    module.mkdir(parents=True, exist_ok=True)
    (course / "course.yaml").write_text(
        "id: course\ntitle: Course\nsummary: S\nmodules: [mod]\n", encoding="utf-8"
    )
    (module / "module.yaml").write_text(
        "id: mod\ntitle: Module\nsummary: S\nlessons: [l1]\n", encoding="utf-8"
    )
    acts = (
        activities
        if activities is not None
        else "activities:\n  - id: l1-exercise\n    kind: exercise\n    title: 문제 풀이\n"
    )
    (module / "l1.md").write_text(
        "---\nid: l1\ntitle: Lesson\nsummary: S\nobjectives: [O]\n"
        "difficulty: 3\nestimated_minutes: 60\n" + acts + "---\n\n# L\n\n" + body,
        encoding="utf-8",
    )
    return course


_n = iter(range(1000))


def lesson_of(root: Path, body: str, **kw: str | None):
    course = load_course(write_course(root / f"c{next(_n)}", body, **kw))
    return course, course.iter_lessons()[0]


# -- parsing ---


def test_a_block_parses_into_problems_in_order(tmp_path: Path) -> None:
    _, lesson = lesson_of(tmp_path, FOUR)
    sets = parse_problem_sets(lesson)
    assert [p.id for p in sets.problems] == ["p1", "p2", "p3", "p4"]
    assert sets.types == {"derivation", "proof", "numerical", "implementation"}
    assert sets.activity_ids(lesson) == ["l1-exercise"]
    assert has_problem_set(lesson.body)


def test_a_problem_carries_no_answer_field(tmp_path: Path) -> None:
    """Nothing is graded, so an `answer` key is a sign the author wanted a quiz."""
    body = (
        "```problemset\nproblems:\n  - id: p1\n    type: proof\n    stars: 1\n"
        '    prompt: "P"\n    solution_policy: sketch\n    answer: 1\n```\n'
    )
    _, lesson = lesson_of(tmp_path, body)
    with pytest.raises(ProblemSetParseError) as exc:
        parse_problem_sets(lesson)
    assert any("answer" in m for m in exc.value.messages)


def test_an_unknown_type_or_policy_is_reported(tmp_path: Path) -> None:
    body = (
        "```problemset\nproblems:\n  - id: p1\n    type: essay\n    stars: 1\n"
        '    prompt: "P"\n    solution_policy: sketch\n```\n'
    )
    _, lesson = lesson_of(tmp_path, body)
    with pytest.raises(ProblemSetParseError) as exc:
        parse_problem_sets(lesson)
    assert any("type" in m for m in exc.value.messages)


def test_a_numerical_problem_needs_the_value_and_the_tolerance(tmp_path: Path) -> None:
    body = (
        "```problemset\nproblems:\n  - id: p1\n    type: numerical\n    stars: 1\n"
        '    prompt: "P"\n    solution_policy: answer\n    solution: "4.2"\n```\n'
    )
    _, lesson = lesson_of(tmp_path, body)
    with pytest.raises(ProblemSetParseError) as exc:
        parse_problem_sets(lesson)
    assert any("tolerance" in m for m in exc.value.messages)


def test_a_tolerance_on_a_proof_is_rejected(tmp_path: Path) -> None:
    body = (
        "```problemset\nproblems:\n  - id: p1\n    type: proof\n    stars: 1\n"
        '    prompt: "P"\n    solution_policy: sketch\n    tolerance: 0.1\n```\n'
    )
    _, lesson = lesson_of(tmp_path, body)
    with pytest.raises(ProblemSetParseError) as exc:
        parse_problem_sets(lesson)
    assert any("only applies to a 'numerical'" in m for m in exc.value.messages)


def test_duplicate_problem_ids_are_reported(tmp_path: Path) -> None:
    body = FOUR.replace("id: p4", "id: p1")
    _, lesson = lesson_of(tmp_path, body)
    with pytest.raises(ProblemSetParseError) as exc:
        parse_problem_sets(lesson)
    assert any("duplicate problem id 'p1'" in m for m in exc.value.messages)


def test_the_activity_must_be_an_exercise_of_this_lesson(tmp_path: Path) -> None:
    _, lesson = lesson_of(
        tmp_path,
        FOUR,
        activities="activities:\n  - id: l1-quiz\n    kind: quiz\n    title: 퀴즈\n",
    )
    with pytest.raises(ProblemSetParseError) as exc:
        parse_problem_sets(lesson)
    assert any("not a 'kind: exercise' activity" in m for m in exc.value.messages)


def test_the_activity_may_be_omitted_with_exactly_one_exercise(tmp_path: Path) -> None:
    _, lesson = lesson_of(tmp_path, FOUR.replace("activity: l1-exercise\n", ""))
    assert parse_problem_sets(lesson).activity_ids(lesson) == ["l1-exercise"]


def test_the_activity_is_required_with_several_exercises(tmp_path: Path) -> None:
    acts = (
        "activities:\n"
        "  - id: l1-exercise\n    kind: exercise\n    title: A\n"
        "  - id: l1-exercise-b\n    kind: exercise\n    title: B\n"
    )
    _, lesson = lesson_of(tmp_path, FOUR.replace("activity: l1-exercise\n", ""), activities=acts)
    with pytest.raises(ProblemSetParseError) as exc:
        parse_problem_sets(lesson)
    assert any("'activity' is required" in m for m in exc.value.messages)


def test_a_lesson_without_a_block_parses_to_nothing(tmp_path: Path) -> None:
    _, lesson = lesson_of(tmp_path, "본문만 있다.\n")
    assert parse_problem_sets(lesson).problems == []
    assert not has_problem_set(lesson.body)


# -- shape advice (warnings) ---


def test_a_well_shaped_set_draws_no_advice(tmp_path: Path) -> None:
    _, lesson = lesson_of(tmp_path, FOUR)
    assert shape_advice(parse_problem_sets(lesson)) == []


def test_a_short_set_is_advice_not_an_error(tmp_path: Path) -> None:
    body = (
        "```problemset\nproblems:\n  - id: p1\n    type: proof\n    stars: 1\n"
        '    prompt: "P"\n    solution_policy: sketch\n```\n'
    )
    course, lesson = lesson_of(tmp_path, body)
    notes = shape_advice(parse_problem_sets(lesson))
    assert any("4-8" in n for n in notes)
    assert any("problem type" in n for n in notes)
    problems = validate_course(course)
    assert problems and all(p.severity == "warning" for p in problems)
    assert [p for p in problems if p.blocking] == []


def test_validate_reports_the_parse_failure_as_an_error(tmp_path: Path) -> None:
    body = FOUR.replace("type: proof", "type: essay")
    course, _ = lesson_of(tmp_path, body)
    problems = validate_course(course)
    assert any(p.blocking and "problemset block 1" in p.message for p in problems)


# -- the static site ---


def test_the_site_shows_the_problems_and_folds_the_solutions(tmp_path: Path) -> None:
    course = write_course(tmp_path / "content", FOUR)
    out = tmp_path / "site"
    result = runner.invoke(
        app,
        [
            "--data-dir",
            str(tmp_path / "data"),
            "--curriculum",
            str(course.parent),
            "site",
            "build",
            "--strict",
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    page = (out / "modules" / "mod" / "l1.html").read_text("utf-8")
    assert "문제 세트 (4문항)" in page
    assert "오일러-라그랑주" in page
    assert "유도" in page and "증명" in page
    assert "★★☆" in page  # stars render as a rating, not a bare number
    # The solution is present but inside a <details>, so it is not read by accident.
    assert "<details" in page and "해답 스케치" in page
    assert "허용 오차" in page
    # Never a raw YAML dump of the block.
    assert "solution_policy" not in page


def test_a_broken_block_falls_back_to_a_code_block(tmp_path: Path) -> None:
    """A lesson that cannot be parsed still builds, so one bad block does not hide a page."""
    from robotics_curriculum.site.pages import render_problem_set_blocks

    _, lesson = lesson_of(tmp_path, "```problemset\nproblems:\n  - id: p1\n    type: essay\n```\n")
    rendered = render_problem_set_blocks(lesson.body, lesson)
    assert "```yaml" in rendered and "type: essay" in rendered

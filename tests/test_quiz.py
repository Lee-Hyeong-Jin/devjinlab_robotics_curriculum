"""P1-2 quizzes: block parsing/validation (AC-4.1), grading, `rc quiz` (AC-4.2, AC-4.3)."""

import json
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner, Result

from robotics_curriculum.cli import app
from robotics_curriculum.content import (
    QuizParseError,
    check,
    load_course,
    parse_quiz,
    validate_course,
)
from robotics_curriculum.content.loader import load_lesson
from robotics_curriculum.content.quiz_block import extract_quiz_blocks
from robotics_curriculum.learn.quiz import (
    InvalidAnswer,
    grade_answer,
    record_quiz_run,
    run_quiz,
    select_questions,
)
from robotics_curriculum.progress import (
    LessonStatus,
    ProgressService,
    SqliteProgressStore,
)

runner = CliRunner()
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "curriculum"
ROTATION = "m1-rotation-representations"
T0 = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)

FRONT = """---
id: a-intro
title: 소개
summary: S
objectives:
  - 목표.
difficulty: 1
estimated_minutes: 30
activities:
  - id: a-intro-quiz
    kind: quiz
    title: 퀴즈
{extra_activities}---

# 소개

```quiz
{block}
```
"""


def lesson_with(block: str, extra_activities: str = "") -> Path:
    """Write a one-lesson course and return the lesson path (via the fixture dir of the test)."""
    raise NotImplementedError  # replaced by the fixture below


@pytest.fixture
def make_lesson(tmp_path: Path):  # type: ignore[no-untyped-def]  # fixture factory
    course = tmp_path / "course"
    (course / "m1").mkdir(parents=True)
    (course / "course.yaml").write_text("id: c\ntitle: C\nsummary: S\n", encoding="utf-8")
    (course / "m1" / "module.yaml").write_text("id: m1\ntitle: M1\nsummary: S\n", encoding="utf-8")

    def _make(block: str, extra_activities: str = "") -> Path:
        path = course / "m1" / "a-intro.md"
        path.write_text(
            FRONT.format(block=block, extra_activities=extra_activities), encoding="utf-8"
        )
        return path

    return _make


def errors_of(path: Path) -> list[str]:
    course = load_course(path.parent.parent)
    return [e.message for e in validate_course(course)]


# -- parsing -------------------------------------------------------------------


def test_fixture_quiz_parses_all_four_types() -> None:
    course = load_course(FIXTURE / "sample-course")
    lesson = next(les for les in course.iter_lessons() if les.id == ROTATION)
    quiz = parse_quiz(lesson)
    assert [q.type for q in quiz.questions] == ["single", "multiple", "truefalse", "short"]
    assert quiz.activity_ids(lesson) == ["m1-rotation-representations-quiz"]
    q1 = quiz.question("q1")
    assert q1 is not None and q1.concept is not None
    assert q1.answer_text() == "2. $R^T$"
    assert quiz.questions[1].answer_text() == "1. 직교 행렬이다, 2. 행렬식이 1이다"
    assert quiz.questions[2].answer_text() == "O (참)"
    assert quiz.questions[3].answer_text() == "1 / +1"
    assert quiz.questions[3].tags == ["linear-algebra"]


def test_bare_list_and_multi_alias_are_accepted(make_lesson) -> None:  # type: ignore[no-untyped-def]
    path = make_lesson(
        "- id: q1\n  type: multi\n  prompt: P\n  choices: [a, b]\n  answer: [0]\n  explanation: E\n"
    )
    lesson = load_lesson(path)
    assert lesson is not None
    quiz = parse_quiz(lesson)
    assert quiz.questions[0].type == "multiple"
    assert quiz.blocks[0].activity is None
    assert quiz.activity_ids(lesson) == ["a-intro-quiz"]  # the lesson's only quiz activity


def test_extract_ignores_other_fences_and_handles_tildes() -> None:
    body = "```python\nx\n```\n~~~quiz\n- a\n~~~\n```quiz\n- b\n```\n"
    assert extract_quiz_blocks(body) == ["- a", "- b"]


@pytest.mark.parametrize(
    ("block", "fragment"),
    [
        ("- id: q1\n  type: single\n  prompt: [\n", "invalid YAML"),
        ("- id: q1\n  type: essay\n  prompt: P\n  answer: 1\n  explanation: E\n", "type"),
        (
            "- id: q1\n  type: single\n  prompt: P\n  choices: [a, b]\n  answer: 2\n"
            "  explanation: E\n",
            "out of range 0..1",
        ),
        (
            "- id: q1\n  type: single\n  prompt: P\n  choices: [a, b]\n  answer: 1\n",
            "explanation",
        ),
        (
            "- id: q1\n  type: single\n  prompt: P\n  choices: [a]\n  answer: 0\n"
            "  explanation: E\n",
            "at least 2 choices",
        ),
        (
            "- id: q1\n  type: multiple\n  prompt: P\n  choices: [a, b]\n  answer: [0, 0]\n"
            "  explanation: E\n",
            "must not repeat",
        ),
        (
            "- id: q1\n  type: truefalse\n  prompt: P\n  answer: yes please\n  explanation: E\n",
            "true or false",
        ),
        (
            "- id: q1\n  type: short\n  prompt: P\n  answer: []\n  explanation: E\n",
            "non-empty list",
        ),
        (
            "- id: q1\n  type: truefalse\n  prompt: P\n  answer: true\n  explanation: E\n"
            "- id: q1\n  type: truefalse\n  prompt: P\n  answer: false\n  explanation: E\n",
            "duplicate question id 'q1'",
        ),
        (
            "activity: a-intro-other\nquestions:\n- id: q1\n  type: truefalse\n  prompt: P\n"
            "  answer: true\n  explanation: E\n",
            "not a 'kind: quiz' activity",
        ),
        ("just text", "expected a mapping"),
    ],
)
def test_validate_reports_quiz_problems(make_lesson, block: str, fragment: str) -> None:  # type: ignore[no-untyped-def]
    path = make_lesson(block)
    messages = errors_of(path)
    assert messages, "expected a validation error"
    assert any(fragment in m for m in messages), messages
    assert all(m.startswith("lesson 'a-intro': ") for m in messages)


def test_activity_required_when_lesson_has_two_quiz_activities(make_lesson) -> None:  # type: ignore[no-untyped-def]
    extra = "  - id: a-intro-quiz2\n    kind: quiz\n    title: 퀴즈 2\n"
    path = make_lesson(
        "- id: q1\n  type: truefalse\n  prompt: P\n  answer: true\n  explanation: E\n", extra
    )
    assert any("'activity' is required" in m for m in errors_of(path))
    path = make_lesson(
        "activity: a-intro-quiz2\nquestions:\n- id: q1\n  type: truefalse\n  prompt: P\n"
        "  answer: true\n  explanation: E\n",
        extra,
    )
    assert errors_of(path) == []


def test_rc_validate_exits_1_with_path_and_message(make_lesson) -> None:  # type: ignore[no-untyped-def]
    path = make_lesson(
        "- id: q1\n  type: single\n  prompt: P\n  choices: [a, b]\n  answer: 5\n  explanation: E\n"
    )
    result = runner.invoke(app, ["validate", str(path.parent.parent)])
    assert result.exit_code == 1
    assert (
        f"{path}: lesson 'a-intro': quiz block 1: question 1: "
        "single answer 5 is out of range 0..1" in result.output
    )
    _, errors = check(path.parent.parent)
    assert len(errors) == 1


def test_parse_quiz_raises_with_all_messages(make_lesson) -> None:  # type: ignore[no-untyped-def]
    path = make_lesson("- id: q1\n  type: nope\n  prompt: P\n  answer: 1\n")
    lesson = load_lesson(path)
    assert lesson is not None
    with pytest.raises(QuizParseError) as info:
        parse_quiz(lesson)
    assert len(info.value.messages) >= 2  # type + explanation


# -- grading -------------------------------------------------------------------


def _fixture_quiz():  # type: ignore[no-untyped-def]
    course = load_course(FIXTURE / "sample-course")
    lesson = next(les for les in course.iter_lessons() if les.id == ROTATION)
    return lesson, parse_quiz(lesson)


@pytest.mark.parametrize(
    ("qid", "text", "correct", "given"),
    [
        ("q1", "2", True, "2"),
        ("q1", "1", False, "1"),
        ("q2", "1, 2", True, "1,2"),
        ("q2", "2 1", True, "1,2"),
        ("q2", "1", False, "1"),
        ("q3", "o", True, "O"),
        ("q3", "true", True, "O"),
        ("q3", "X", False, "X"),
        ("q3", "거짓", False, "X"),
        ("q4", "  +1 ", True, "+1"),
        ("q4", "1", True, "1"),
        ("q4", "-1", False, "-1"),
    ],
)
def test_grade_answer(qid: str, text: str, correct: bool, given: str) -> None:
    _, quiz = _fixture_quiz()
    question = quiz.question(qid)
    assert question is not None
    graded = grade_answer(question, text)
    assert (graded.correct, graded.given) == (correct, given)


@pytest.mark.parametrize(
    ("qid", "text"),
    [("q1", "7"), ("q1", "1,2"), ("q1", ""), ("q2", "x"), ("q3", "maybe"), ("q4", " ")],
)
def test_grade_answer_rejects_unparseable_input(qid: str, text: str) -> None:
    _, quiz = _fixture_quiz()
    question = quiz.question(qid)
    assert question is not None
    with pytest.raises(InvalidAnswer):
        grade_answer(question, text)


def test_short_answer_normalizes_case_and_spaces(make_lesson) -> None:  # type: ignore[no-untyped-def]
    path = make_lesson(
        '- id: q1\n  type: short\n  prompt: P\n  answer: ["Forward  Kinematics"]\n'
        "  explanation: E\n"
    )
    lesson = load_lesson(path)
    assert lesson is not None
    question = parse_quiz(lesson).questions[0]
    assert grade_answer(question, " forward kinematics ").correct
    assert not grade_answer(question, "forwardkinematics").correct


# -- session + recording -------------------------------------------------------


class FakeClock:
    def __init__(self) -> None:
        self.now = T0

    def __call__(self) -> datetime:
        self.now += timedelta(seconds=30)
        return self.now


@pytest.fixture
def service(tmp_path: Path) -> Iterator[ProgressService]:
    store = SqliteProgressStore.in_dir(tmp_path)
    svc = ProgressService(store, ProgressService.load_curriculum(FIXTURE), clock=FakeClock())
    yield svc
    store.close()


def _play(service: ProgressService, answers: list[str]) -> tuple[list[str], object]:
    lesson, quiz = _fixture_quiz()
    echoed: list[str] = []
    feed = iter(answers)
    result = run_quiz(
        lesson,
        quiz,
        quiz.questions,
        prompt=lambda _text: next(feed),
        echo=echoed.append,
        clock=service.clock,
    )
    return echoed, record_quiz_run(service.store, lesson, result)


def test_run_quiz_grades_each_answer_immediately_and_reports_score(
    service: ProgressService,
) -> None:
    echoed, recorded = _play(service, ["1", "1,2", "o", "2"])  # wrong, right, right, wrong
    assert "  ✘ 오답 (정답: 2. $R^T$)" in echoed[0]
    assert echoed[1].startswith("  해설: 회전 행렬은 직교 행렬")
    assert "  ✔ 정답" in echoed
    assert echoed[-1] == "결과 2/4 (50%)  오답 2"
    run = recorded.run  # type: ignore[attr-defined]
    assert (run.correct, run.total, run.seconds) == (2, 4, 30)
    assert run.activity_id == "m1-rotation-representations-quiz"


def test_invalid_input_is_asked_again_without_counting(service: ProgressService) -> None:
    echoed, recorded = _play(service, ["9", "2", "1 2", "O", "+1"])
    assert "  ! '9' 은(는) 1-4 사이의 번호가 아닙니다" in echoed
    assert echoed[-1] == "결과 4/4 (100%)  오답 0"
    assert len(service.store.list_quiz_attempts()) == 4


def test_wrong_and_concept_questions_become_cards_without_duplicates(
    service: ProgressService,
) -> None:
    _, recorded = _play(service, ["1", "1", "x", "2"])  # all wrong; q1 also has a concept
    ids = sorted(c.id for c in recorded.new_cards)  # type: ignore[attr-defined]
    assert ids == [
        f"{ROTATION}-concept-q1",
        f"{ROTATION}-quiz-q1",
        f"{ROTATION}-quiz-q2",
        f"{ROTATION}-quiz-q3",
        f"{ROTATION}-quiz-q4",
    ]
    quiz_card = service.store.get_card(f"{ROTATION}-quiz-q1")
    assert quiz_card is not None
    assert quiz_card.front.startswith("회전 행렬 $R$ 의 역행렬은?\n1. $R$\n2. $R^T$")
    assert quiz_card.back == "2. $R^T$\n회전 행렬은 직교 행렬이므로 $R^{-1} = R^T$ 다."
    assert (quiz_card.lesson_id, quiz_card.question_id, quiz_card.source) == (
        ROTATION,
        "q1",
        "quiz",
    )
    concept = service.store.get_card(f"{ROTATION}-concept-q1")
    assert concept is not None and concept.front == "회전 행렬의 역행렬"
    states = service.store.list_card_states()
    assert len(states) == 5 and all(s.due == T0.astimezone().date() for s in states)

    # second run: all correct -> only the concept card is wanted, and it already exists
    _, again = _play(service, ["2", "1,2", "o", "1"])
    assert again.new_cards == []  # type: ignore[attr-defined]
    assert len(service.store.list_cards()) == 5
    assert len(service.store.list_quiz_runs()) == 2
    activities = service.store.list_activities()
    assert [(a.activity_id, a.status) for a in activities] == [
        ("m1-rotation-representations-quiz", LessonStatus.DONE)
    ]


def test_correct_answer_without_concept_makes_no_card(service: ProgressService) -> None:
    _, recorded = _play(service, ["2", "1,2", "o", "1"])
    assert [c.source for c in recorded.new_cards] == ["concept"]  # type: ignore[attr-defined]


def test_select_questions_only_and_retry_wrong(service: ProgressService) -> None:
    _, quiz = _fixture_quiz()
    assert [q.id for q in select_questions(quiz, only=["q3", "q1"])] == ["q1", "q3"]
    with pytest.raises(ValueError, match="unknown question id"):
        select_questions(quiz, only=["q9"])
    assert select_questions(quiz, retry_wrong=True, store=service.store) == []  # no attempts yet
    _play(service, ["1", "1,2", "o", "2"])  # q1, q4 wrong
    retry = select_questions(quiz, retry_wrong=True, store=service.store)
    assert [q.id for q in retry] == ["q1", "q4"]
    _play(service, ["2", "1,2", "o", "2"])  # q1 fixed, q4 still wrong
    assert [q.id for q in select_questions(quiz, retry_wrong=True, store=service.store)] == ["q4"]


# -- CLI -----------------------------------------------------------------------


def rc(tmp_path: Path, *args: str, input: str | None = None) -> Result:
    data = tmp_path / "data"
    return runner.invoke(
        app, ["--data-dir", str(data), "--curriculum", str(FIXTURE), *args], input=input
    )


def test_rc_quiz_end_to_end(tmp_path: Path) -> None:
    result = rc(tmp_path, "quiz", ROTATION, input="1\n1,2\no\n+1\n")
    assert result.exit_code == 0, result.output
    out = result.output
    assert out.startswith("퀴즈: 회전 표현 (m1-rotation-representations) — 4문항")
    assert "[1/4] (객관식) 회전 행렬 $R$ 의 역행렬은?" in out
    assert "  2. $R^T$" in out
    assert "✘ 오답 (정답: 2. $R^T$)" in out
    assert out.count("해설:") == 4
    assert "결과 3/4 (75%)  오답 1" in out
    assert "새 카드 2장 (오답 1 + 개념 1) → `rc review` 로 복습" in out
    assert "저장됨" in out
    listing = rc(tmp_path, "review", "--dry-run")
    assert listing.exit_code == 0, listing.output
    assert f"{ROTATION}-quiz-q1" in listing.output and "2장 due" in listing.output
    status = rc(tmp_path, "status")
    assert "오늘 복습: 2장 · 최근 7일 퀴즈 정답률: 75% (3/4)" in status.output


def test_rc_quiz_options_and_errors(tmp_path: Path) -> None:
    only = rc(tmp_path, "quiz", ROTATION, "--only", "q3", input="x\n")
    assert only.exit_code == 0, only.output
    assert "1문항" in only.output and "결과 0/1 (0%)" in only.output
    retry = rc(tmp_path, "quiz", ROTATION, "--retry-wrong", input="o\n")
    assert retry.exit_code == 0 and "결과 1/1 (100%)" in retry.output
    nothing = rc(tmp_path, "quiz", ROTATION, "--retry-wrong")
    assert nothing.exit_code == 0 and "풀 문항이 없습니다" in nothing.output
    unknown = rc(tmp_path, "quiz", ROTATION, "--only", "zzz")
    assert unknown.exit_code == 1 and "unknown question id(s): zzz" in unknown.output
    no_quiz = rc(tmp_path, "quiz", "m1-vectors-matrices")
    assert no_quiz.exit_code == 1 and "has no quiz block" in no_quiz.output
    missing = rc(tmp_path, "quiz", "nope")
    assert missing.exit_code == 1 and "unknown lesson 'nope'" in missing.output


def test_rc_quiz_aborted_midway_saves_nothing(tmp_path: Path) -> None:
    result = rc(tmp_path, "quiz", ROTATION, input="1\n")  # EOF after the first answer
    assert result.exit_code == 1
    assert "중단: 결과를 저장하지 않았습니다" in result.output
    status = rc(tmp_path, "status")
    assert "오늘 복습: 0장 · 최근 7일 퀴즈 정답률: 기록 없음" in status.output


def test_progress_export_import_round_trip_keeps_quiz_data(tmp_path: Path) -> None:
    assert rc(tmp_path, "quiz", ROTATION, input="1\n1\nx\n2\n").exit_code == 0
    assert rc(tmp_path, "review", "-n", "1", input="\n3\n").exit_code == 0
    export = rc(tmp_path, "progress", "export")
    assert export.exit_code == 0, export.output
    text = export.output
    for key in (
        "cards",
        "card_states",
        "reviews",
        "quiz_attempts",
        "quiz_runs",
        "activity_progress",
    ):
        assert f'"{key}": [' in text
    file = tmp_path / "backup.json"
    file.write_text(text, encoding="utf-8")
    assert rc(tmp_path, "progress", "import", str(file), "--replace").exit_code == 0
    again = rc(tmp_path, "progress", "export")

    def payload(dump: str) -> dict[str, object]:
        """The export without ``exported_at``, which differs by design on every run."""
        data = dict(json.loads(dump))
        data.pop("exported_at")
        return data

    assert payload(again.output) == payload(text)

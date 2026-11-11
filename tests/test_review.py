"""P1-2 review sessions (AC-4.4): due selection, rating persistence, requeue, `rc review`."""

from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner

from robotics_curriculum.cli import app
from robotics_curriculum.learn import Rating
from robotics_curriculum.learn.review import (
    apply_rating,
    due_cards,
    due_count,
    recent_accuracy,
    run_review,
)
from robotics_curriculum.progress import (
    Card,
    CardState,
    QuizAttempt,
    SqliteProgressStore,
)

runner = CliRunner()
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "curriculum"
ROTATION = "m1-rotation-representations"
TODAY = date(2026, 11, 11)
NOW = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)


@pytest.fixture
def store(tmp_path: Path) -> Iterator[SqliteProgressStore]:
    with SqliteProgressStore.in_dir(tmp_path) as s:
        yield s


def seed(store: SqliteProgressStore, card_id: str, due: date, *, suspended: bool = False) -> None:
    store.save_card(
        Card(
            id=card_id,
            lesson_id=ROTATION,
            question_id=card_id.rsplit("-", 1)[-1],
            front=f"front {card_id}",
            back=f"back {card_id}",
            source="quiz",
            created_at=NOW,
            suspended=suspended,
        )
    )
    store.save_card_state(CardState(card_id=card_id, due=due))


def test_due_cards_filters_by_date_suspension_lesson_and_limit(store: SqliteProgressStore) -> None:
    seed(store, "c-quiz-b", TODAY)
    seed(store, "c-quiz-a", TODAY - timedelta(days=3))
    seed(store, "c-quiz-later", TODAY + timedelta(days=1))
    seed(store, "c-quiz-off", TODAY, suspended=True)
    store.save_card(
        Card(
            id="other-quiz-x",
            lesson_id="other",
            question_id="x",
            front="f",
            back="b",
            source="quiz",
            created_at=NOW,
        )
    )  # no state row -> never due
    due = due_cards(store, today=TODAY)
    assert [d.card.id for d in due] == ["c-quiz-a", "c-quiz-b"]  # earliest due first
    assert due_count(store, today=TODAY) == 2
    assert [d.card.id for d in due_cards(store, today=TODAY, limit=1)] == ["c-quiz-a"]
    assert due_cards(store, today=TODAY, lesson_id="other") == []
    assert due_count(store, today=TODAY + timedelta(days=1)) == 3


def test_apply_rating_updates_state_and_logs_review(store: SqliteProgressStore) -> None:
    seed(store, "c-quiz-a", TODAY)
    good = apply_rating(store, "c-quiz-a", Rating.GOOD, now=NOW, today=TODAY)
    assert (good.repetitions, good.interval_days, good.due) == (1, 1, TODAY + timedelta(days=1))
    again = apply_rating(store, "c-quiz-a", Rating.AGAIN, now=NOW, today=good.due)
    assert (again.repetitions, again.interval_days) == (0, 1)
    assert again.due == good.due + timedelta(days=1)
    assert again.ease == pytest.approx(1.96)
    reviews = store.list_reviews(card_id="c-quiz-a")
    assert [(r.rating, r.interval_before, r.interval_after) for r in reviews] == [
        ("good", 0, 1),
        ("again", 1, 1),
    ]
    assert reviews[1].ease_after == pytest.approx(1.96)
    assert store.get_card_state("c-quiz-a") == again


def test_run_review_requeues_again_cards_at_the_end_without_rescheduling(
    store: SqliteProgressStore,
) -> None:
    seed(store, "c-quiz-a", TODAY)
    seed(store, "c-quiz-b", TODAY)
    seen: list[str] = []
    answers = iter(["", "1", "", "3", "", "1", "", "2"])  # a: again, b: good, a again x2

    def prompt(text: str) -> str:
        seen.append(text.splitlines()[0])
        return next(answers)

    echoed: list[str] = []
    summary = run_review(
        store,
        due_cards(store, today=TODAY),
        prompt=prompt,
        echo=echoed.append,
        now=NOW,
        today=TODAY,
    )
    assert [s for s in seen if s.startswith("[")] == [
        "[1/2] front c-quiz-a",
        "[2/2] front c-quiz-b",
        "[다시 1/2] front c-quiz-a",
        "[다시 2/2] front c-quiz-a",
    ]
    assert summary.reviewed == 2 and summary.requeued == 1
    assert summary.counts[Rating.AGAIN] == 1 and summary.counts[Rating.GOOD] == 1
    assert summary.due_tomorrow == 2  # both land on tomorrow (again -> 1 day, first good -> 1 day)
    assert echoed[-1] == "완료 2장  again 1 · hard 0 · good 1 · easy 0   내일 예정 2장"
    # only the first answer per card is scheduled/logged
    assert len(store.list_reviews()) == 2
    assert "  ! 1-4 또는 again/hard/good/easy 로 답하세요" not in echoed


def test_run_review_reprompts_on_bad_rating(store: SqliteProgressStore) -> None:
    seed(store, "c-quiz-a", TODAY)
    answers = iter(["", "x", "4"])
    echoed: list[str] = []
    run_review(
        store,
        due_cards(store, today=TODAY),
        prompt=lambda _t: next(answers),
        echo=echoed.append,
        now=NOW,
        today=TODAY,
    )
    assert "  ! 1-4 또는 again/hard/good/easy 로 답하세요" in echoed
    assert store.list_reviews()[0].rating == "easy"


def test_recent_accuracy() -> None:
    def attempt(days_ago: int, correct: bool) -> QuizAttempt:
        return QuizAttempt(
            lesson_id=ROTATION,
            question_id="q",
            answered_at=NOW - timedelta(days=days_ago),
            answer="1",
            correct=correct,
        )

    attempts = [attempt(10, False), attempt(6, True), attempt(0, False)]
    assert recent_accuracy(attempts, since=NOW - timedelta(days=7)) == (1, 2)
    assert recent_accuracy([attempt(10, True)], since=NOW - timedelta(days=7)) is None


def test_rc_review_end_to_end(tmp_path: Path) -> None:
    data = tmp_path / "data"
    args = ["--data-dir", str(data), "--curriculum", str(FIXTURE)]
    empty = runner.invoke(app, [*args, "review"])
    assert empty.exit_code == 0 and "오늘 복습할 카드가 없습니다" in empty.output
    assert runner.invoke(app, [*args, "quiz", ROTATION], input="1\n1,2\no\n+1\n").exit_code == 0
    bad_lesson = runner.invoke(app, [*args, "review", "--lesson", "nope"])
    assert bad_lesson.exit_code == 1 and "unknown lesson 'nope'" in bad_lesson.output
    result = runner.invoke(app, [*args, "review", "--lesson", ROTATION], input="\n3\n\n1\n\n2\n")
    assert result.exit_code == 0, result.output
    out = result.output
    assert "복습 2장" in out
    assert "[1/2] 회전 행렬의 역행렬" in out  # concept card id sorts first
    assert "  답: 전치 행렬 $R^T$ (직교 행렬)" in out
    assert "다음 복습:" in out and "(1일 뒤)" in out
    assert "[다시 1/2]" in out
    assert "완료 2장  again 1 · hard 0 · good 1 · easy 0   내일 예정 2장" in out
    none_left = runner.invoke(app, [*args, "review"])
    assert "오늘 복습할 카드가 없습니다" in none_left.output
    aborted = runner.invoke(app, [*args, "review"], input="")
    assert aborted.exit_code == 0  # nothing due -> nothing to abort

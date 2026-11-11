"""Non-interactive quiz / review service layer used by the API (learn/service.py)."""

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from robotics_curriculum.learn import (
    QuizSubmissionError,
    Rating,
    dashboard_stats,
    grade_submission,
    lesson_quiz,
    question_views,
    rate_card,
    review_queue,
    scheduled_on,
    submit_quiz,
)
from robotics_curriculum.progress import (
    LessonStatus,
    ProgressError,
    ProgressService,
    SqliteProgressStore,
)

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "curriculum"
ROTATION = "m1-rotation-representations"
VECTORS = "m1-vectors-matrices"
START = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)
END = START + timedelta(minutes=4)
TODAY = START.astimezone().date()
RIGHT = {"q1": "2", "q2": "1,2", "q3": "o", "q4": "+1"}
WRONG_Q1 = {**RIGHT, "q1": "1"}


@pytest.fixture
def service(tmp_path: Path) -> Iterator[ProgressService]:
    store = SqliteProgressStore.in_dir(tmp_path)
    svc = ProgressService(store, ProgressService.load_curriculum(FIXTURE), clock=lambda: END)
    yield svc
    store.close()


def rotation(service: ProgressService):  # type: ignore[no-untyped-def]
    return service.lesson(ROTATION)


# -- reading the quiz ----------------------------------------------------------


def test_question_views_hide_answers_and_explanations(service: ProgressService) -> None:
    views = question_views(lesson_quiz(rotation(service)))
    assert [v.id for v in views] == ["q1", "q2", "q3", "q4"]
    assert views[0].type_label == "객관식"
    assert views[0].choices[1] == "$R^T$"
    assert views[3].choices == []  # short answer
    fields = set(type(views[0]).__slots__)
    assert "answer" not in fields and "explanation" not in fields and "concept" not in fields


def test_lesson_without_quiz_is_rejected(service: ProgressService) -> None:
    with pytest.raises(QuizSubmissionError, match="has no quiz block"):
        lesson_quiz(service.lesson(VECTORS))


# -- grading a submission ------------------------------------------------------


def test_grade_submission_scores_every_question(service: ProgressService) -> None:
    lesson = rotation(service)
    result = grade_submission(
        lesson_quiz(lesson), WRONG_Q1, started_at=START, finished_at=END, lesson=lesson
    )
    assert (result.correct_count, result.total, result.percent) == (3, 4, 75)
    assert [g.question.id for g in result.wrong] == ["q1"]


@pytest.mark.parametrize(
    ("answers", "fragment"),
    [
        ({**RIGHT, "q9": "1"}, r"unknown question id\(s\): q9"),
        ({"q1": "2"}, r"missing answer\(s\) for: q2, q3, q4"),
        ({**RIGHT, "q1": "nope"}, "question 'q1'"),
        ({}, r"missing answer\(s\)"),
    ],
)
def test_grade_submission_rejects_bad_input(
    service: ProgressService, answers: dict[str, str], fragment: str
) -> None:
    lesson = rotation(service)
    with pytest.raises(QuizSubmissionError, match=fragment):
        grade_submission(
            lesson_quiz(lesson), answers, started_at=START, finished_at=END, lesson=lesson
        )


def test_partial_submission_grades_only_what_was_sent(service: ProgressService) -> None:
    lesson = rotation(service)
    result = grade_submission(
        lesson_quiz(lesson),
        {"q3": "x"},
        started_at=START,
        finished_at=END,
        lesson=lesson,
        partial=True,
    )
    assert (result.total, result.correct_count) == (1, 0)
    with pytest.raises(QuizSubmissionError, match="no answers"):
        grade_submission(
            lesson_quiz(lesson), {}, started_at=START, finished_at=END, lesson=lesson, partial=True
        )


# -- submitting (grade + record) -----------------------------------------------


def test_submit_quiz_records_run_attempts_cards_and_activity(service: ProgressService) -> None:
    lesson = rotation(service)
    outcome = submit_quiz(
        service.store, lesson, WRONG_Q1, started_at=START, finished_at=END, user_id=1
    )
    assert (outcome.correct, outcome.total, outcome.percent, outcome.seconds) == (3, 4, 75, 240)
    assert sorted(outcome.new_card_ids) == [f"{ROTATION}-concept-q1", f"{ROTATION}-quiz-q1"]
    q1 = next(f for f in outcome.feedback if f.question_id == "q1")
    assert (q1.correct, q1.given, q1.answer) == (False, "1", "2. $R^T$")
    assert q1.explanation.startswith("회전 행렬은 직교 행렬")
    assert [f.correct for f in outcome.feedback] == [False, True, True, True]
    runs = service.store.list_quiz_runs()
    assert [(r.correct, r.total, r.activity_id) for r in runs] == [
        (3, 4, "m1-rotation-representations-quiz")
    ]
    assert len(service.store.list_quiz_attempts()) == 4
    assert [(a.activity_id, a.status) for a in service.store.list_activities()] == [
        ("m1-rotation-representations-quiz", LessonStatus.DONE)
    ]


def test_resubmitting_does_not_duplicate_cards(service: ProgressService) -> None:
    lesson = rotation(service)
    first = submit_quiz(service.store, lesson, WRONG_Q1, started_at=START, finished_at=END)
    second = submit_quiz(service.store, lesson, WRONG_Q1, started_at=START, finished_at=END)
    assert len(first.new_card_ids) == 2 and second.new_card_ids == []
    assert len(service.store.list_cards()) == 2


def test_all_correct_submission_only_makes_concept_cards(service: ProgressService) -> None:
    outcome = submit_quiz(
        service.store, rotation(service), RIGHT, started_at=START, finished_at=END
    )
    assert outcome.new_card_ids == [f"{ROTATION}-concept-q1"]
    assert outcome.percent == 100


# -- review --------------------------------------------------------------------


def test_review_queue_and_rate_card(service: ProgressService) -> None:
    submit_quiz(service.store, rotation(service), WRONG_Q1, started_at=START, finished_at=END)
    queue = review_queue(service.store, today=TODAY)
    assert [c.card_id for c in queue] == [f"{ROTATION}-concept-q1", f"{ROTATION}-quiz-q1"]
    assert queue[0].due == TODAY and queue[0].interval_days == 0
    assert queue[0].source == "concept" and queue[0].lesson_id == ROTATION
    assert [c.card_id for c in review_queue(service.store, today=TODAY, limit=1)] == [
        f"{ROTATION}-concept-q1"
    ]
    assert review_queue(service.store, today=TODAY, lesson_id="other") == []

    state = rate_card(service.store, f"{ROTATION}-quiz-q1", Rating.GOOD, now=END, today=TODAY)
    assert (state.repetitions, state.interval_days) == (1, 1)
    assert state.due == TODAY + timedelta(days=1)
    assert [r.rating for r in service.store.list_reviews()] == ["good"]
    assert [c.card_id for c in review_queue(service.store, today=TODAY)] == [
        f"{ROTATION}-concept-q1"
    ]
    assert scheduled_on(service.store, day=TODAY + timedelta(days=1)) == 1


def test_rate_card_rejects_unknown_card(service: ProgressService) -> None:
    with pytest.raises(ProgressError, match="unknown card 'nope'"):
        rate_card(service.store, "nope", Rating.GOOD, now=END, today=TODAY)


# -- dashboard -----------------------------------------------------------------


def test_dashboard_stats_aggregates_stages_week_streak_due_and_accuracy(
    service: ProgressService,
) -> None:
    service.log(VECTORS, 40)
    service.done(VECTORS, understanding=4)
    submit_quiz(service.store, rotation(service), WRONG_Q1, started_at=START, finished_at=END)

    stats = dashboard_stats(service, now=END)
    assert (stats.total.done, stats.total.total, stats.total.percent) == (1, 3, 33)
    stages = {s.stage: s for s in stats.stages}
    assert stages["기초"].progress == stats.stages[0].progress
    assert (stages["기초"].progress.done, stages["기초"].progress.total) == (1, 2)
    assert stages["기초"].module_ids == ["m1-math-physics"]
    assert "단계 미지정" in stages  # the fixture's m2 has no level
    assert stats.week.seconds == 40 * 60 and stats.week.sessions == 1
    assert stats.streak_days == 1
    assert stats.due_today == 2  # one quiz card + one concept card
    assert stats.current is not None and stats.current.lesson.id == ROTATION
    assert stats.accuracy == (3, 4) and stats.accuracy_percent == 75


def test_dashboard_stats_on_empty_progress(service: ProgressService) -> None:
    stats = dashboard_stats(service, now=END)
    assert (stats.total.done, stats.total.percent) == (0, 0)
    assert stats.week.seconds == 0 and stats.streak_days == 0 and stats.due_today == 0
    assert stats.accuracy is None and stats.accuracy_percent is None
    assert stats.current is not None and stats.current.lesson.id == VECTORS  # first unlocked


def test_site_stats_module_re_exports_the_same_objects() -> None:
    from robotics_curriculum.learn import stats as learn_stats
    from robotics_curriculum.site import stats as site_stats

    for name in ("ratio", "week_stats", "streak", "stage_of", "dashboard", "Ratio"):
        assert getattr(site_stats, name) is getattr(learn_stats, name)

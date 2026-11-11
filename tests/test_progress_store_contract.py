"""ProgressStore contract: the same tests run against SQLite and PostgreSQL (P2-3).

PostgreSQL runs in a real container (see ``conftest.py``); without Docker those cases skip.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from robotics_curriculum.progress import (
    SCHEMA_VERSION,
    ActivityProgress,
    Card,
    CardState,
    LessonProgress,
    LessonStatus,
    ProgressService,
    ProgressStore,
    QuizAttempt,
    QuizRun,
    Review,
    Session,
    SqliteProgressStore,
)
from robotics_curriculum.progress.postgres import PostgresProgressStore

CURRICULUM = Path(__file__).resolve().parent / "fixtures" / "curriculum"
VECTORS = "m1-vectors-matrices"
DH = "m2-dh-parameters"
T0 = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)


@pytest.fixture(params=["sqlite", "postgres"])
def store(request: pytest.FixtureRequest, tmp_path: Path) -> Iterator[ProgressStore]:
    backend: ProgressStore
    if request.param == "sqlite":
        backend = SqliteProgressStore.in_dir(tmp_path)
    else:
        backend = PostgresProgressStore(request.getfixturevalue("clean_postgres_url"))
    yield backend
    backend.close()


def test_new_store_is_empty_and_at_current_schema(store: ProgressStore) -> None:
    assert store.is_empty()
    assert store.list_lessons(None) == []
    assert store.list_sessions(None) == []
    assert getattr(store, "schema_version") == SCHEMA_VERSION  # noqa: B009


def test_lesson_round_trip_and_upsert(store: ProgressStore) -> None:
    assert store.get_lesson(VECTORS) is None
    first = LessonProgress(
        lesson_id=VECTORS,
        status=LessonStatus.IN_PROGRESS,
        started_at=T0,
        total_seconds=600,
    )
    store.save_lesson(first)
    assert store.get_lesson(VECTORS) == first
    done = first.model_copy(
        update={
            "status": LessonStatus.DONE,
            "completed_at": T0 + timedelta(hours=1),
            "understanding": 4,
            "note": "메모 ; with semicolon",
        }
    )
    store.save_lesson(done)
    assert store.get_lesson(VECTORS) == done
    assert store.list_lessons() == [done]
    assert not store.is_empty()


def test_timestamps_come_back_as_utc(store: ProgressStore) -> None:
    kst = timezone(timedelta(hours=9))
    naive = datetime(2026, 11, 11, 9, 0)
    store.save_lesson(
        LessonProgress(lesson_id=VECTORS, started_at=datetime(2026, 11, 11, 18, 0, tzinfo=kst))
    )
    store.save_lesson(LessonProgress(lesson_id=DH, started_at=naive))
    vectors, dh = store.get_lesson(VECTORS), store.get_lesson(DH)
    assert vectors is not None and dh is not None
    assert vectors.started_at == T0 and vectors.started_at.utcoffset() == timedelta(0)
    assert dh.started_at == T0  # naive input is taken as UTC


def test_lessons_are_scoped_by_user(store: ProgressStore) -> None:
    store.save_lesson(LessonProgress(user_id=1, lesson_id=VECTORS))
    store.save_lesson(LessonProgress(user_id=2, lesson_id=VECTORS, status=LessonStatus.DONE))
    store.save_lesson(LessonProgress(user_id=1, lesson_id=DH))
    assert [p.lesson_id for p in store.list_lessons(1)] == [VECTORS, DH]
    assert [p.user_id for p in store.list_lessons(2)] == [2]
    assert [(p.user_id, p.lesson_id) for p in store.list_lessons(None)] == [
        (1, VECTORS),
        (1, DH),
        (2, VECTORS),
    ]
    other = store.get_lesson(VECTORS, user_id=2)
    assert other is not None and other.status is LessonStatus.DONE


def test_session_lifecycle(store: ProgressStore) -> None:
    assert store.open_session() is None
    opened = store.add_session(Session(lesson_id=VECTORS, started_at=T0))
    assert opened.id is not None
    assert store.open_session() == opened
    store.close_session(opened.id, T0 + timedelta(minutes=30), "chapter 1")
    assert store.open_session() is None
    [closed] = store.list_sessions()
    assert closed.ended_at == T0 + timedelta(minutes=30)
    assert closed.note == "chapter 1"
    store.close_session(opened.id, T0 + timedelta(minutes=40), None)  # None keeps the note
    assert store.list_sessions()[0].note == "chapter 1"
    store.delete_session(opened.id)
    assert store.list_sessions() == []


def test_session_ids_increase_and_filters_apply(store: ProgressStore) -> None:
    a = store.add_session(Session(lesson_id=VECTORS, started_at=T0, ended_at=T0, source="manual"))
    b = store.add_session(Session(lesson_id=DH, started_at=T0, ended_at=T0, source="manual"))
    c = store.add_session(Session(user_id=2, lesson_id=DH, started_at=T0, ended_at=T0))
    assert a.id is not None and b.id is not None and c.id is not None
    assert a.id < b.id < c.id
    assert [s.id for s in store.list_sessions()] == [a.id, b.id]
    assert [s.id for s in store.list_sessions(lesson_id=DH)] == [b.id]
    assert [s.id for s in store.list_sessions(None, DH)] == [b.id, c.id]
    assert [s.id for s in store.list_sessions(None)] == [a.id, b.id, c.id]


def test_explicit_session_id_does_not_break_later_inserts(store: ProgressStore) -> None:
    imported = store.add_session(Session(id=50, lesson_id=VECTORS, started_at=T0, ended_at=T0))
    assert imported.id == 50
    later = store.add_session(Session(lesson_id=VECTORS, started_at=T0))
    assert later.id is not None and later.id > 50


def test_one_open_session_per_user(store: ProgressStore) -> None:
    store.add_session(Session(lesson_id=VECTORS, started_at=T0))
    store.add_session(Session(user_id=2, lesson_id=VECTORS, started_at=T0))  # other user: ok
    with pytest.raises(Exception, match=r"(?i)unique"):
        store.add_session(Session(lesson_id=DH, started_at=T0))


def test_check_constraints_reject_bad_rows(store: ProgressStore) -> None:
    bad = LessonProgress.model_construct(
        user_id=1,
        lesson_id=VECTORS,
        status=LessonStatus.DONE,
        started_at=None,
        completed_at=None,
        total_seconds=0,
        understanding=9,
        note=None,
    )
    with pytest.raises(Exception, match=r"(?i)check"):
        store.save_lesson(bad)


def test_transaction_commits_and_nests(store: ProgressStore) -> None:
    with store.transaction():
        store.save_lesson(LessonProgress(lesson_id=VECTORS))
        with store.transaction():
            store.add_session(Session(lesson_id=VECTORS, started_at=T0))
    assert store.get_lesson(VECTORS) is not None
    assert len(store.list_sessions()) == 1


def test_transaction_rolls_back_everything_on_error(store: ProgressStore) -> None:
    store.save_lesson(LessonProgress(lesson_id=DH))
    with pytest.raises(RuntimeError, match="boom"), store.transaction():
        store.save_lesson(LessonProgress(lesson_id=VECTORS))
        with store.transaction():
            store.add_session(Session(lesson_id=VECTORS, started_at=T0))
        raise RuntimeError("boom")
    assert store.get_lesson(VECTORS) is None
    assert store.list_sessions() == []
    assert store.get_lesson(DH) is not None  # earlier committed work survives
    with store.transaction():  # store is usable again
        store.save_lesson(LessonProgress(lesson_id=VECTORS))
    assert store.get_lesson(VECTORS) is not None


def test_clear_empties_everything(store: ProgressStore) -> None:
    store.save_lesson(LessonProgress(lesson_id=VECTORS))
    store.add_session(Session(lesson_id=VECTORS, started_at=T0))
    store.clear()
    assert store.is_empty()


def test_service_flow_runs_on_every_backend(store: ProgressStore) -> None:
    now = [T0]
    service = ProgressService(
        store, ProgressService.load_curriculum(CURRICULUM), clock=lambda: now[0]
    )
    service.start(VECTORS)
    now[0] = T0 + timedelta(minutes=25)
    _, seconds = service.stop(note="done reading")
    assert seconds == 25 * 60
    service.log(VECTORS, 15)
    service.done(VECTORS, understanding=4)
    progress = store.get_lesson(VECTORS)
    assert progress is not None
    assert progress.status is LessonStatus.DONE
    assert progress.total_seconds == 40 * 60
    exported = service.export()
    assert len(exported.sessions) == 2
    count = service.import_(exported, replace=True)
    assert count == (1, 2)


# -- schema v2: cards, SM-2 state, reviews, quiz records (P1-2) --------------------------------


def _card(card_id: str = "c1", user_id: int = 1) -> Card:
    return Card(
        id=card_id,
        user_id=user_id,
        lesson_id=VECTORS,
        question_id="q1",
        front="앞면",
        back="뒷면",
        source="quiz",
        created_at=T0,
    )


def test_card_round_trip_and_upsert(store: ProgressStore) -> None:
    assert store.get_card("c1") is None
    card = _card()
    store.save_card(card)
    assert store.get_card("c1") == card
    suspended = card.model_copy(update={"suspended": True, "back": "고친 뒷면"})
    store.save_card(suspended)
    assert store.get_card("c1") == suspended
    store.save_card(_card("c2"))
    store.save_card(_card("c3", user_id=2))
    assert [c.id for c in store.list_cards()] == ["c1", "c2"]
    assert [c.user_id for c in store.list_cards(None)] == [1, 1, 2]
    assert [c.id for c in store.list_cards(lesson_id=DH)] == []


def test_card_state_round_trip(store: ProgressStore) -> None:
    state = CardState(card_id="c1", due=date(2026, 11, 20))
    store.save_card_state(state)
    assert store.get_card_state("c1") == state
    graded = state.model_copy(
        update={"repetitions": 2, "interval_days": 6, "ease": 2.6, "due": date(2026, 11, 26)}
    )
    store.save_card_state(graded)
    found = store.get_card_state("c1")
    assert found is not None and found.due == date(2026, 11, 26) and found.ease == 2.6
    store.save_card_state(CardState(card_id="c9", user_id=2, due=date(2026, 12, 1)))
    assert [s.card_id for s in store.list_card_states()] == ["c1"]
    assert len(store.list_card_states(None)) == 2


def test_reviews_and_quiz_records_get_ids(store: ProgressStore) -> None:
    review = store.add_review(
        Review(
            card_id="c1",
            reviewed_at=T0,
            rating="good",
            interval_before=1,
            interval_after=6,
            ease_after=2.6,
        )
    )
    assert review.id is not None
    attempt = store.add_quiz_attempt(
        QuizAttempt(lesson_id=VECTORS, question_id="q1", answered_at=T0, answer="42", correct=True)
    )
    run = store.add_quiz_run(
        QuizRun(
            lesson_id=VECTORS,
            started_at=T0,
            finished_at=T0 + timedelta(minutes=5),
            correct=4,
            total=5,
        )
    )
    assert attempt.id is not None and run.id is not None
    assert store.list_reviews() == [review]
    assert store.list_reviews(card_id="other") == []
    assert store.list_quiz_attempts() == [attempt]
    assert store.list_quiz_runs(lesson_id=VECTORS) == [run]
    assert store.list_quiz_runs(lesson_id=DH) == []
    second = store.add_review(review.model_copy(update={"id": None}))
    assert second.id is not None and second.id > review.id


def test_activity_progress_round_trip(store: ProgressStore) -> None:
    activity = ActivityProgress(
        activity_id="a1", lesson_id=VECTORS, status=LessonStatus.IN_PROGRESS, updated_at=T0
    )
    store.save_activity(activity)
    assert store.list_activities() == [activity]
    store.save_activity(activity.model_copy(update={"status": LessonStatus.DONE}))
    [stored] = store.list_activities()
    assert stored.status is LessonStatus.DONE
    store.save_activity(activity.model_copy(update={"user_id": 2, "activity_id": "a2"}))
    assert len(store.list_activities(None)) == 2


def test_v2_rows_count_towards_is_empty_and_clear(store: ProgressStore) -> None:
    store.save_card(_card())
    assert not store.is_empty()
    store.clear()
    assert store.is_empty() and store.list_cards(None) == []


def test_delete_user_removes_only_that_user(store: ProgressStore) -> None:
    for user in (1, 2):
        store.save_lesson(LessonProgress(user_id=user, lesson_id=VECTORS))
        store.save_lesson(LessonProgress(user_id=user, lesson_id=DH))
        store.add_session(Session(user_id=user, lesson_id=VECTORS, started_at=T0))
        store.save_card(_card(f"c{user}", user_id=user))
        store.save_card_state(CardState(card_id=f"c{user}", user_id=user, due=date(2026, 11, 20)))
        store.save_activity(
            ActivityProgress(user_id=user, activity_id=f"a{user}", lesson_id=VECTORS, updated_at=T0)
        )
    assert store.delete_user(1) == (2, 1)
    assert store.list_lessons(1) == [] and store.list_sessions(1) == []
    assert store.list_cards(1) == [] and store.list_card_states(1) == []
    assert store.list_activities(1) == []
    assert [p.lesson_id for p in store.list_lessons(2)] == [VECTORS, DH]
    assert [c.id for c in store.list_cards(2)] == ["c2"]
    assert store.delete_user(99) == (0, 0)  # unknown user
    assert store.delete_user(2) == (2, 1)
    assert store.is_empty()

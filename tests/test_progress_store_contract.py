"""ProgressStore contract: the same tests run against SQLite and PostgreSQL (P2-3).

PostgreSQL runs in a real container (see ``conftest.py``); without Docker those cases skip.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from robotics_curriculum.progress import (
    SCHEMA_VERSION,
    LessonProgress,
    LessonStatus,
    ProgressService,
    ProgressStore,
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

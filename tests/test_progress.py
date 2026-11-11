"""Learner progress store, service, and CLI (P1-1)."""

import json
import sqlite3
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner, Result

from robotics_curriculum.cli import app
from robotics_curriculum.progress import (
    DB_FILENAME,
    SCHEMA_VERSION,
    LessonProgress,
    LessonStatus,
    ProgressError,
    ProgressService,
    SqliteProgressStore,
    parse_duration,
)

CURRICULUM = Path(__file__).resolve().parent / "fixtures" / "curriculum"
VECTORS = "m1-vectors-matrices"
ROTATION = "m1-rotation-representations"
DH = "m2-dh-parameters"
T0 = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)


class FakeClock:
    def __init__(self) -> None:
        self.now = T0

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **kwargs: float) -> None:
        self.now += timedelta(**kwargs)


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def service(tmp_path: Path, clock: FakeClock) -> Iterator[ProgressService]:
    store = SqliteProgressStore.in_dir(tmp_path)
    svc = ProgressService(store, ProgressService.load_curriculum(CURRICULUM), clock=clock)
    yield svc
    store.close()


# -- store ---------------------------------------------------------------------


def test_schema_applied_idempotently_and_status_persists(tmp_path: Path) -> None:
    db = tmp_path / DB_FILENAME
    with SqliteProgressStore(db) as store:
        assert store.schema_version == SCHEMA_VERSION
        store.save_lesson(LessonProgress(lesson_id=VECTORS, status=LessonStatus.IN_PROGRESS))
    with SqliteProgressStore(db) as store:  # reopen: no error, data survives
        assert store.schema_version == SCHEMA_VERSION
        found = store.get_lesson(VECTORS)
        assert found is not None
        assert found.status is LessonStatus.IN_PROGRESS
        assert found.user_id == 1
    tables = {
        row[0]
        for row in sqlite3.connect(db).execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    assert {"meta", "lesson_progress", "sessions"} <= tables


def test_status_change_round_trips_through_store(service: ProgressService) -> None:
    for status in LessonStatus:
        service.store.save_lesson(LessonProgress(lesson_id=DH, status=status))
        found = service.store.get_lesson(DH)
        assert found is not None and found.status is status


# -- service -------------------------------------------------------------------


def test_start_stop_accumulates_time(service: ProgressService, clock: FakeClock) -> None:
    service.start(VECTORS)
    assert service.status()[0].status is LessonStatus.IN_PROGRESS
    clock.advance(minutes=25)
    _, seconds = service.stop(note="first")
    assert seconds == 25 * 60
    service.start(VECTORS)
    clock.advance(minutes=10)
    service.stop()
    progress = service.store.get_lesson(VECTORS)
    assert progress is not None
    assert progress.total_seconds == 35 * 60
    assert progress.started_at == T0
    sessions = service.store.list_sessions(lesson_id=VECTORS)
    assert [s.note for s in sessions] == ["first", None]
    assert all(not s.is_open for s in sessions)


def test_double_start_errors(service: ProgressService) -> None:
    service.start(VECTORS)
    with pytest.raises(ProgressError, match="already running"):
        service.start(DH)


def test_stop_without_session_errors(service: ProgressService) -> None:
    with pytest.raises(ProgressError, match="no session"):
        service.stop()


def test_stop_discard_adds_no_time(service: ProgressService, clock: FakeClock) -> None:
    service.start(VECTORS)
    clock.advance(minutes=30)
    service.stop(discard=True)
    assert service.current_session() is None
    assert service.store.list_sessions() == []
    progress = service.store.get_lesson(VECTORS)
    assert progress is not None and progress.total_seconds == 0


def test_unknown_lesson_errors(service: ProgressService) -> None:
    for call in (
        lambda: service.start("nope"),
        lambda: service.log("nope", 5),
        lambda: service.done("nope"),
    ):
        with pytest.raises(ProgressError, match="unknown lesson 'nope'"):
            call()


def test_log_records_manual_session(service: ProgressService, clock: FakeClock) -> None:
    session = service.log(DH, 45, note="read ahead")
    assert session.source == "manual"
    assert session.ended_at == T0
    assert session.started_at == T0 - timedelta(minutes=45)
    progress = service.store.get_lesson(DH)
    assert progress is not None
    assert progress.total_seconds == 45 * 60
    assert progress.status is LessonStatus.IN_PROGRESS


def test_done_closes_open_session_and_records_understanding(
    service: ProgressService, clock: FakeClock
) -> None:
    service.start(VECTORS)
    clock.advance(minutes=20)
    progress, unlocked = service.done(VECTORS, understanding=4, note="ok")
    assert progress.status is LessonStatus.DONE
    assert progress.completed_at == clock.now
    assert progress.total_seconds == 20 * 60
    assert (progress.understanding, progress.note) == (4, "ok")
    assert service.current_session() is None
    assert {lesson.id for lesson in unlocked} == {ROTATION, DH}


def test_status_lists_all_lessons_in_teaching_order(service: ProgressService) -> None:
    service.log(VECTORS, 10)
    summaries = service.status()
    assert [s.lesson.id for s in summaries] == [VECTORS, ROTATION, DH]
    assert [s.status.value for s in summaries] == ["in_progress", "not_started", "not_started"]
    assert [s.locked for s in summaries] == [False, True, True]
    with pytest.raises(ProgressError, match="unknown course"):
        service.status("nope")


def test_next_respects_prerequisites(service: ProgressService) -> None:
    assert [s.lesson.id for s in service.next_lessons()] == [VECTORS]
    service.done(VECTORS)
    assert [s.lesson.id for s in service.next_lessons()] == [ROTATION, DH]
    service.log(DH, 5)  # in-progress lessons are recommended first
    assert [s.lesson.id for s in service.next_lessons("sample-course")] == [DH, ROTATION]
    assert [s.lesson.id for s in service.next_lessons(limit=1)] == [DH]
    service.done(DH)
    service.done(ROTATION)
    assert service.next_lessons() == []


def test_export_import_round_trip(service: ProgressService, tmp_path: Path) -> None:
    service.log(VECTORS, 30, note="노트")
    service.done(VECTORS, understanding=3)
    service.start(DH)  # an open session must survive too
    exported = service.export()

    other_store = SqliteProgressStore(tmp_path / "other" / DB_FILENAME)
    other = ProgressService(other_store, service.courses, clock=service.clock)
    assert other.import_(exported) == (2, 2)
    again = other.export()
    assert again.lesson_progress == exported.lesson_progress
    assert again.sessions == exported.sessions
    with pytest.raises(ProgressError, match="not empty"):
        other.import_(exported)
    assert other.import_(exported, replace=True) == (2, 2)
    other_store.close()


@pytest.mark.parametrize(
    ("text", "minutes"), [("45", 45), ("45m", 45), ("1h", 60), ("1h30m", 90), ("2H05", 125)]
)
def test_parse_duration(text: str, minutes: int) -> None:
    assert parse_duration(text) == minutes


@pytest.mark.parametrize("text", ["", "0", "abc", "1.5h", "-5"])
def test_parse_duration_rejects(text: str) -> None:
    with pytest.raises(ProgressError):
        parse_duration(text)


# -- CLI -----------------------------------------------------------------------

runner = CliRunner()


def rc(data_dir: Path, *args: str) -> Result:
    return runner.invoke(app, ["--data-dir", str(data_dir), "--curriculum", str(CURRICULUM), *args])


def test_cli_smoke(tmp_path: Path) -> None:
    result = rc(tmp_path, "next")
    assert result.exit_code == 0, result.output
    assert VECTORS in result.output and DH not in result.output

    assert rc(tmp_path, "start", VECTORS).exit_code == 0
    result = rc(tmp_path, "start", DH)
    assert result.exit_code == 1
    assert "already running" in result.stderr

    assert rc(tmp_path, "stop", "--note", "warm-up").exit_code == 0
    assert rc(tmp_path, "log", VECTORS, "1h30m", "--note", "problems").exit_code == 0
    result = rc(tmp_path, "done", VECTORS, "-u", "4")
    assert result.exit_code == 0, result.output
    assert f"unlocked: {DH}" in result.output

    result = rc(tmp_path, "status")
    assert result.exit_code == 0, result.output
    assert "33%" in result.output and "1h 30m" in result.output
    assert (tmp_path / DB_FILENAME).is_file()

    result = rc(tmp_path, "next", "-n", "1")
    assert result.exit_code == 0
    assert ROTATION in result.output and DH not in result.output


def test_cli_errors_go_to_stderr_with_nonzero_exit(tmp_path: Path) -> None:
    result = rc(tmp_path, "stop")
    assert result.exit_code == 1
    assert "no session is running" in result.stderr
    result = rc(tmp_path, "log", "nope", "10")
    assert result.exit_code == 1
    assert "unknown lesson 'nope'" in result.stderr
    result = rc(tmp_path, "log", VECTORS, "ten")
    assert result.exit_code == 1
    assert "invalid duration" in result.stderr
    result = runner.invoke(
        app, ["--data-dir", str(tmp_path), "--curriculum", str(tmp_path / "x"), "status"]
    )
    assert result.exit_code == 1
    assert "curriculum directory not found" in result.stderr


def test_cli_data_dir_from_env(tmp_path: Path) -> None:
    data_dir = tmp_path / "from-env"
    result = runner.invoke(
        app,
        ["--curriculum", str(CURRICULUM), "log", VECTORS, "20"],
        env={"RC_DATA_DIR": str(data_dir)},
    )
    assert result.exit_code == 0, result.output
    assert (data_dir / DB_FILENAME).is_file()


def test_cli_progress_export_import_round_trip(tmp_path: Path) -> None:
    src, dst = tmp_path / "src", tmp_path / "dst"
    assert rc(src, "log", VECTORS, "30").exit_code == 0
    assert rc(src, "done", VECTORS, "-m", "메모").exit_code == 0
    out = tmp_path / "export.json"
    assert rc(src, "progress", "export", str(out)).exit_code == 0

    result = rc(dst, "progress", "import", str(out))
    assert result.exit_code == 0, result.output
    out2 = tmp_path / "export2.json"
    assert rc(dst, "progress", "export", str(out2)).exit_code == 0
    first, second = json.loads(out.read_text()), json.loads(out2.read_text())
    for key in ("schema_version", "lesson_progress", "sessions"):
        assert first[key] == second[key]
    assert first["lesson_progress"][0]["note"] == "메모"

    result = rc(dst, "progress", "import", str(out))
    assert result.exit_code == 1
    assert "--replace" in result.stderr

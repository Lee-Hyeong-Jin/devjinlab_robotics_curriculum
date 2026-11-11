"""``rc progress transfer`` (US-DB.2 / AC-DB.3): local SQLite or JSON export -> another store."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner

from robotics_curriculum.cli import app
from robotics_curriculum.progress import (
    SCHEMA_VERSION,
    LessonProgress,
    LessonStatus,
    ProgressExport,
    Session,
    SqliteProgressStore,
)
from robotics_curriculum.progress.factory import DATABASE_URL_ENV
from robotics_curriculum.progress.postgres import PostgresProgressStore
from robotics_curriculum.progress.transfer_cli import _redact

VECTORS = "m1-vectors-matrices"
DH = "m2-dh-parameters"
T0 = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)

runner = CliRunner()


@pytest.fixture
def local_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.delenv(DATABASE_URL_ENV, raising=False)
    data_dir = tmp_path / "local"
    with SqliteProgressStore.in_dir(data_dir) as store:
        store.save_lesson(LessonProgress(lesson_id=VECTORS, status=LessonStatus.DONE))
        store.add_session(
            Session(lesson_id=VECTORS, started_at=T0, ended_at=T0 + timedelta(minutes=30))
        )
    return data_dir


def _rc(*args: str) -> tuple[int, str]:
    result = runner.invoke(app, list(args))
    return result.exit_code, result.output


def test_transfer_local_sqlite_to_postgres_is_idempotent(
    local_dir: Path, clean_postgres_url: str
) -> None:
    code, out = _rc(
        "--data-dir", str(local_dir), "progress", "transfer", "--to", clean_postgres_url
    )
    assert code == 0, out
    assert "transferred 1 lesson rows, 1 sessions" in out
    code, out = _rc(
        "--data-dir", str(local_dir), "progress", "transfer", "--to", clean_postgres_url
    )
    assert code == 0, out
    assert "1 lesson rows, 0 sessions, skipped 1 duplicate sessions" in out
    with PostgresProgressStore(clean_postgres_url) as server:
        assert [p.lesson_id for p in server.list_lessons()] == [VECTORS]
        assert len(server.list_sessions()) == 1


def test_transfer_reads_destination_from_env_and_rehomes_user(
    local_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    server_db = tmp_path / "server.db"
    monkeypatch.setenv(DATABASE_URL_ENV, f"sqlite:///{server_db}")
    code, out = _rc("--data-dir", str(local_dir), "progress", "transfer", "--user-id", "7")
    assert code == 0, out
    with SqliteProgressStore(server_db) as server:
        assert [p.user_id for p in server.list_lessons(None)] == [7]
        assert [s.user_id for s in server.list_sessions(None)] == [7]
    with SqliteProgressStore.in_dir(local_dir) as local:  # source is untouched
        assert [p.user_id for p in local.list_lessons(None)] == [1]


def test_transfer_from_json_export(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(DATABASE_URL_ENV, raising=False)
    export = ProgressExport(
        schema_version=SCHEMA_VERSION,
        exported_at=T0,
        lesson_progress=[LessonProgress(lesson_id=DH)],
        sessions=[],
    )
    file = tmp_path / "backup.json"
    file.write_text(export.model_dump_json(), encoding="utf-8")
    dest = tmp_path / "dest.db"
    code, out = _rc("progress", "transfer", "--from", str(file), "--to", f"sqlite:///{dest}")
    assert code == 0, out
    assert f"from {file}" in out


def test_transfer_empty_mode_refuses_non_empty_destination(local_dir: Path, tmp_path: Path) -> None:
    dest = f"sqlite:///{tmp_path / 'dest.db'}"
    assert _rc("--data-dir", str(local_dir), "progress", "transfer", "--to", dest)[0] == 0
    code, out = _rc(
        "--data-dir", str(local_dir), "progress", "transfer", "--to", dest, "--mode", "empty"
    )
    assert code == 1
    assert "not empty" in out and "--mode merge" in out


@pytest.mark.parametrize(
    ("args", "message"),
    [
        ((), "no destination"),
        (("--to", "mysql://u@h/db"), "unsupported RC_DATABASE_URL scheme"),
        (("--to", "sqlite:///x.db", "--from", "/nonexistent.json"), "cannot read"),
    ],
)
def test_transfer_errors(local_dir: Path, args: tuple[str, ...], message: str) -> None:
    code, out = _rc("--data-dir", str(local_dir), "progress", "transfer", *args)
    assert code == 1
    assert message in out


def test_transfer_rejects_invalid_export(local_dir: Path, tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{}", encoding="utf-8")
    code, out = _rc("progress", "transfer", "--from", str(bad), "--to", "sqlite:///x.db")
    assert code == 1 and "not a valid progress export" in out


def test_unreachable_server_error_hides_password(local_dir: Path) -> None:
    url = "postgresql://rc:s3cret@127.0.0.1:1/rc?connect_timeout=2"
    code, out = _rc("--data-dir", str(local_dir), "progress", "transfer", "--to", url)
    assert code == 1
    assert "cannot open postgresql://rc:***@127.0.0.1:1/rc" in out
    assert "s3cret" not in out


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("postgresql://rc:pw@db:5432/rc", "postgresql://rc:***@db:5432/rc"),
        ("postgresql://rc@db/rc", "postgresql://rc@db/rc"),
        ("sqlite:///tmp/p.db", "sqlite:///tmp/p.db"),
    ],
)
def test_redact(url: str, expected: str) -> None:
    assert _redact(url) == expected

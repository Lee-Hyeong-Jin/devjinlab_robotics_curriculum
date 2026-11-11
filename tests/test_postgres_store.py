"""PostgreSQL-specific behavior: Alembic up/down, autogenerate drift, factory, transfer (P2-3)."""

from __future__ import annotations

import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import Engine, create_engine, inspect, text

from robotics_curriculum.progress import (
    SCHEMA_VERSION,
    LessonProgress,
    LessonStatus,
    ProgressExport,
    Session,
    SqliteProgressStore,
)
from robotics_curriculum.progress import postgres as pg
from robotics_curriculum.progress.factory import (
    DATABASE_URL_ENV,
    TransferError,
    TransferMode,
    open_store,
    transfer,
)
from robotics_curriculum.progress.postgres import PostgresProgressStore, normalize_url

ROOT = Path(__file__).resolve().parents[1]
VECTORS = "m1-vectors-matrices"
DH = "m2-dh-parameters"
T0 = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)
PROGRESS_TABLES = {
    "meta",
    "alembic_version",
    "lesson_progress",
    "sessions",
    "cards",
    "card_state",
    "reviews",
    "quiz_attempts",
    "quiz_runs",
    "activity_progress",
}
AUTH_TABLES = {
    "users",
    "identities",
    "sessions_auth",
    "api_tokens",
    "one_time_tokens",
    "login_attempts",
    "audit_log",
}
TABLES = PROGRESS_TABLES | AUTH_TABLES


@pytest.fixture
def engine(clean_postgres_url: str) -> Engine:
    return create_engine(normalize_url(clean_postgres_url))


def _mentions(entry: object, tables: set[str]) -> bool:
    """Whether an autogenerate diff entry concerns one of ``tables``.

    Substring match on the entry's repr, so an index named after its table (for example the
    functional index ``users_email_lower``) is attributed to that table too.
    """
    return any(name in repr(entry) for name in tables)


def _tables(engine: Engine) -> set[str]:
    return set(inspect(engine).get_table_names())


# -- URL handling (no server needed) ---------------------------------------------------------


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("postgresql://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("postgres://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("postgresql+psycopg://u@h/db", "postgresql+psycopg://u@h/db"),
    ],
)
def test_normalize_url_uses_psycopg3(url: str, expected: str) -> None:
    assert normalize_url(url) == expected


def test_alembic_config_escapes_percent_in_password() -> None:
    cfg = pg.alembic_config(url="postgresql://rc:p%40ss@db/rc")
    assert cfg.get_main_option("sqlalchemy.url") == "postgresql+psycopg://rc:p%40ss@db/rc"


# -- factory -----------------------------------------------------------------------------------


def test_factory_defaults_to_sqlite_in_data_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(DATABASE_URL_ENV, raising=False)
    store = open_store(tmp_path)
    assert isinstance(store, SqliteProgressStore)
    assert store.path == tmp_path / "progress.db"
    store.close()


def test_factory_without_data_dir_uses_rc_data_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(DATABASE_URL_ENV, raising=False)
    monkeypatch.setenv("RC_DATA_DIR", str(tmp_path / "rcdata"))
    store = open_store()
    assert isinstance(store, SqliteProgressStore)
    assert store.path == tmp_path / "rcdata" / "progress.db"
    store.close()


def test_factory_imports_without_service_first() -> None:
    """service.open_service() will import factory; factory must not import service eagerly."""
    source = (ROOT / "src/robotics_curriculum/progress/factory.py").read_text()
    assert "\nfrom robotics_curriculum.progress.service" not in source


def test_factory_empty_env_means_sqlite(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(DATABASE_URL_ENV, "  ")
    store = open_store(tmp_path)
    assert isinstance(store, SqliteProgressStore)
    store.close()


def test_factory_sqlite_url(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = tmp_path / "elsewhere" / "p.db"
    monkeypatch.setenv(DATABASE_URL_ENV, f"sqlite:///{db}")
    store = open_store(tmp_path)
    assert isinstance(store, SqliteProgressStore) and store.path == db
    store.close()


def test_factory_rejects_unknown_scheme(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unsupported RC_DATABASE_URL scheme 'mysql'"):
        open_store(tmp_path, url="mysql://u@h/db")


def test_factory_env_selects_postgres(
    clean_postgres_url: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plain = clean_postgres_url.replace("postgresql+psycopg://", "postgresql://")
    monkeypatch.setenv(DATABASE_URL_ENV, plain)
    store = open_store(tmp_path)
    assert isinstance(store, PostgresProgressStore)
    assert store.schema_version == SCHEMA_VERSION
    store.close()
    assert not (tmp_path / "progress.db").exists()


# -- Alembic -------------------------------------------------------------------------------------


def test_upgrade_downgrade_round_trip_on_empty_db(engine: Engine) -> None:
    assert _tables(engine) == set()
    pg.upgrade(engine)
    assert _tables(engine) == TABLES
    indexes = {ix["name"] for ix in inspect(engine).get_indexes("sessions")}
    assert {"sessions_user_lesson", "sessions_one_open"} <= indexes
    pg.upgrade(engine)  # idempotent
    pg.downgrade(engine, "base")
    assert _tables(engine) == {"alembic_version"}
    pg.upgrade(engine)  # and back up again
    assert _tables(engine) == TABLES
    engine.dispose()


def test_one_step_down_and_up(engine: Engine) -> None:
    pg.upgrade(engine)
    pg.downgrade(engine, "-1")
    pg.upgrade(engine, "+1")
    with engine.connect() as conn:
        version = conn.execute(text("SELECT value FROM meta WHERE key = 'schema_version'"))
        assert version.scalar_one() == str(SCHEMA_VERSION)
    engine.dispose()


def test_models_match_migrations(engine: Engine) -> None:
    """A schema change without an Alembic revision fails here (autogenerate diff is empty)."""
    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext

    pg.upgrade(engine)
    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), pg.metadata)
    # auth tables belong to robotics_curriculum.auth.schema, not to this metadata
    assert [entry for entry in diff if not _mentions(entry, AUTH_TABLES)] == []
    engine.dispose()


def test_alembic_cli_uses_rc_database_url(clean_postgres_url: str) -> None:
    env = {"PATH": "/usr/bin:/bin", DATABASE_URL_ENV: clean_postgres_url}
    for args in (["upgrade", "head"], ["downgrade", "base"]):
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "-c", str(ROOT / "alembic.ini"), *args],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr


def test_store_refuses_newer_schema(clean_postgres_url: str) -> None:
    PostgresProgressStore(clean_postgres_url).close()
    engine = create_engine(normalize_url(clean_postgres_url))
    with engine.begin() as conn:
        conn.execute(text("UPDATE meta SET value = '999' WHERE key = 'schema_version'"))
    with pytest.raises(RuntimeError, match="schema version 999 is newer"):
        PostgresProgressStore(engine)
    engine.dispose()


def test_store_without_migrate_on_shared_engine(clean_postgres_url: str) -> None:
    engine = pg.make_engine(clean_postgres_url, pool_size=2)
    pg.upgrade(engine)
    with PostgresProgressStore(engine, migrate=False) as store:
        store.save_lesson(LessonProgress(lesson_id=VECTORS))
    # closing a store does not dispose an engine it was given
    with PostgresProgressStore(engine, migrate=False) as store:
        assert store.get_lesson(VECTORS) is not None
    engine.dispose()


# -- transfer (SQLite / JSON export -> PostgreSQL) -----------------------------------------------


def _seed(store: SqliteProgressStore) -> None:
    store.save_lesson(
        LessonProgress(lesson_id=VECTORS, status=LessonStatus.DONE, total_seconds=1800)
    )
    store.save_lesson(LessonProgress(lesson_id=DH, status=LessonStatus.IN_PROGRESS))
    store.add_session(
        Session(lesson_id=VECTORS, started_at=T0, ended_at=T0 + timedelta(minutes=30))
    )
    store.add_session(Session(lesson_id=DH, started_at=T0 + timedelta(hours=1)))


def test_transfer_sqlite_to_postgres_preserves_data(
    tmp_path: Path, clean_postgres_url: str
) -> None:
    with SqliteProgressStore.in_dir(tmp_path) as local:
        _seed(local)
        with PostgresProgressStore(clean_postgres_url) as server:
            result = transfer(local, server)
            assert (result.lessons, result.sessions) == (2, 2)
            assert server.list_lessons(None) == local.list_lessons(None)
            strip = [s.model_copy(update={"id": None}) for s in local.list_sessions(None)]
            assert [s.model_copy(update={"id": None}) for s in server.list_sessions(None)] == strip
            open_ = server.open_session()
            assert open_ is not None and open_.lesson_id == DH


def test_transfer_requires_empty_dest_unless_merge_or_replace(tmp_path: Path) -> None:
    with (
        SqliteProgressStore(tmp_path / "a.db") as src,
        SqliteProgressStore(tmp_path / "b.db") as dest,
    ):
        _seed(src)
        transfer(src, dest)
        with pytest.raises(TransferError, match="not empty"):
            transfer(src, dest)
        again = transfer(src, dest, mode=TransferMode.MERGE)
        assert (again.sessions, again.skipped_sessions) == (0, 2)  # no duplicates
        assert len(dest.list_sessions(None)) == 2
        dest.save_lesson(LessonProgress(lesson_id="extra"))
        transfer(src, dest, mode=TransferMode.REPLACE)
        assert [p.lesson_id for p in dest.list_lessons()] == [VECTORS, DH]


def test_transfer_json_export_into_server_account(tmp_path: Path) -> None:
    export = ProgressExport(
        schema_version=SCHEMA_VERSION,
        exported_at=T0,
        lesson_progress=[LessonProgress(lesson_id=VECTORS, status=LessonStatus.DONE)],
        sessions=[Session(id=7, lesson_id=VECTORS, started_at=T0, ended_at=T0)],
    )
    with SqliteProgressStore(tmp_path / "server.db") as dest:
        dest.save_lesson(LessonProgress(user_id=42, lesson_id=DH))
        result = transfer(export, dest, mode=TransferMode.MERGE, user_id=42)
        assert (result.lessons, result.sessions) == (1, 1)
        assert [p.lesson_id for p in dest.list_lessons(42)] == [VECTORS, DH]
        assert dest.list_lessons(1) == []
        [session] = dest.list_sessions(42)
        assert session.user_id == 42


def test_open_store_shares_one_pool_per_url(clean_postgres_url: str) -> None:
    first = open_store(url=clean_postgres_url)
    second = open_store(url=clean_postgres_url.replace("postgresql+psycopg://", "postgresql://"))
    assert isinstance(first, PostgresProgressStore) and isinstance(second, PostgresProgressStore)
    assert first.engine is second.engine is pg.shared_engine(clean_postgres_url)
    first.save_lesson(LessonProgress(lesson_id=VECTORS))
    first.close()  # does not dispose the shared pool
    assert second.get_lesson(VECTORS) is not None
    second.close()
    pg.dispose_shared_engines()


def test_auth_migration_matches_auth_schema(engine: Engine) -> None:
    """Alembic 0003 must stay in step with robotics_curriculum.auth.schema (P2-2 owns that file)."""
    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext

    from robotics_curriculum.auth.schema import auth_metadata

    pg.upgrade(engine)
    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), auth_metadata)
    # The progress tables show up as "extra" here: auth_metadata does not describe them.
    assert [entry for entry in diff if _mentions(entry, set(auth_metadata.tables))] == []
    engine.dispose()

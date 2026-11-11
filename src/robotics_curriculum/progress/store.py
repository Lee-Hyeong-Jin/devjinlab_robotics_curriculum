"""Progress storage: the :class:`ProgressStore` interface and its SQLite implementation.

The service layer only talks to :class:`ProgressStore`, so a different backend (for
example a server database in Phase 2) can be swapped in without touching it. See
``docs/adr/0003-progress-store-sqlite.md``.

Schema versioning: the ``meta`` table holds ``schema_version``.
:data:`MIGRATIONS` maps a target version to the SQL that upgrades from the
previous one; opening a database applies every missing step in order inside one
transaction, so opening is idempotent.
"""

from __future__ import annotations

import logging
import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import AbstractContextManager, contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol, Self

from robotics_curriculum.progress.models import (
    DEFAULT_USER,
    LessonProgress,
    LessonStatus,
    Session,
)

DB_FILENAME = "progress.db"

# Wait this long for another process to release the write lock before failing.
BUSY_TIMEOUT_SECONDS = 15.0
DB_FILE_MODE = 0o600  # study notes are personal data: owner-only
DATA_DIR_MODE = 0o700

logger = logging.getLogger(__name__)


class StoreError(Exception):
    """A storage failure: locked database, constraint violation, corrupt file.

    The service layer lets this reach the CLI boundary, which turns it into an
    ``error: ...`` message instead of a traceback.
    """


_META_DDL = "CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)"

MIGRATIONS: dict[int, str] = {
    1: """
    CREATE TABLE lesson_progress (
        user_id        INTEGER NOT NULL DEFAULT 1,
        lesson_id      TEXT    NOT NULL,
        status         TEXT    NOT NULL DEFAULT 'not_started'
                       CHECK (status IN ('not_started', 'in_progress', 'done')),
        started_at     TEXT,
        completed_at   TEXT,
        total_seconds  INTEGER NOT NULL DEFAULT 0 CHECK (total_seconds >= 0),
        understanding  INTEGER CHECK (understanding BETWEEN 1 AND 5),
        note           TEXT,
        PRIMARY KEY (user_id, lesson_id)
    );
    CREATE TABLE sessions (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL DEFAULT 1,
        lesson_id   TEXT    NOT NULL,
        started_at  TEXT    NOT NULL,
        ended_at    TEXT,
        note        TEXT,
        source      TEXT    NOT NULL DEFAULT 'timer' CHECK (source IN ('timer', 'manual'))
    );
    CREATE INDEX sessions_user_lesson ON sessions (user_id, lesson_id);
    -- at most one running timer per user
    CREATE UNIQUE INDEX sessions_one_open ON sessions (user_id) WHERE ended_at IS NULL;
    """,
}
SCHEMA_VERSION = max(MIGRATIONS)


def _message(exc: sqlite3.Error) -> str:
    """A user-facing sentence for a sqlite failure (no stack, no internal paths)."""
    text = str(exc)
    if isinstance(exc, sqlite3.OperationalError) and "locked" in text:
        return (
            "the progress database is busy (another `rc` command or editor is writing to it); "
            "try again in a moment"
        )
    if isinstance(exc, sqlite3.IntegrityError):
        return f"the progress data violates a database constraint: {text}"
    return f"progress database error: {text}"


def _ts(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat()


def _dt(value: str | None) -> datetime | None:
    return None if value is None else datetime.fromisoformat(value)


class ProgressStore(Protocol):
    """Persistence operations the progress service needs."""

    def transaction(self) -> AbstractContextManager[None]:
        """Group several writes atomically (nestable)."""
        ...

    def get_lesson(self, lesson_id: str, user_id: int = DEFAULT_USER) -> LessonProgress | None: ...

    def save_lesson(self, progress: LessonProgress) -> None: ...

    def list_lessons(self, user_id: int | None = DEFAULT_USER) -> list[LessonProgress]:
        """``user_id=None`` lists every user (used by export)."""
        ...

    def open_session(self, user_id: int = DEFAULT_USER) -> Session | None: ...

    def add_session(self, session: Session) -> Session: ...

    def close_session(self, session_id: int, ended_at: datetime, note: str | None) -> None: ...

    def delete_session(self, session_id: int) -> None: ...

    def list_sessions(
        self, user_id: int | None = DEFAULT_USER, lesson_id: str | None = None
    ) -> list[Session]: ...

    def is_empty(self) -> bool: ...

    def clear(self) -> None: ...

    def close(self) -> None: ...


class SqliteProgressStore:
    """:class:`ProgressStore` backed by a single SQLite file (stdlib ``sqlite3``)."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        on_disk = str(path) != ":memory:"
        if on_disk:
            self.path.parent.mkdir(parents=True, mode=DATA_DIR_MODE, exist_ok=True)
        try:
            # isolation_level=None: we issue BEGIN/COMMIT ourselves (see transaction()).
            self._conn = sqlite3.connect(
                str(path), isolation_level=None, timeout=BUSY_TIMEOUT_SECONDS
            )
        except sqlite3.Error as exc:
            raise StoreError(f"cannot open the progress database {self.path}: {exc}") from exc
        self._conn.row_factory = sqlite3.Row
        self._depth = 0
        if on_disk:
            # WAL lets a reader (e.g. `rc status`) run while another process writes.
            self._exec("PRAGMA journal_mode=WAL")
            self._restrict_permissions()
        self._migrate()

    def _restrict_permissions(self) -> None:
        for target, mode in ((self.path.parent, DATA_DIR_MODE), (self.path, DB_FILE_MODE)):
            try:
                target.chmod(mode)
            except OSError as exc:  # pragma: no cover - platform dependent
                logger.debug("cannot chmod %s: %s", target.name, exc)

    def _exec(self, sql: str, params: Sequence[object] = ()) -> sqlite3.Cursor:
        """Run one statement, turning sqlite failures into :class:`StoreError`."""
        try:
            return self._conn.execute(sql, params)
        except sqlite3.Error as exc:
            raise StoreError(_message(exc)) from exc
        except OverflowError as exc:
            raise StoreError("a value is out of range for the progress database") from exc

    @classmethod
    def in_dir(cls, data_dir: Path) -> Self:
        return cls(data_dir / DB_FILENAME)

    # -- lifecycle -------------------------------------------------------------

    def _migrate(self) -> None:
        with self.transaction():
            self._exec(_META_DDL)
            current = self.schema_version
            if current > SCHEMA_VERSION:
                raise RuntimeError(
                    f"{self.path}: schema version {current} is newer than "
                    f"supported {SCHEMA_VERSION}"
                )
            for version in range(current + 1, SCHEMA_VERSION + 1):
                for statement in _split_sql(MIGRATIONS[version]):
                    self._exec(statement)
                self._exec(
                    "INSERT INTO meta (key, value) VALUES ('schema_version', ?) "
                    "ON CONFLICT (key) DO UPDATE SET value = excluded.value",
                    (str(version),),
                )

    @property
    def schema_version(self) -> int:
        row = self._exec("SELECT value FROM meta WHERE key = 'schema_version'").fetchone()
        return 0 if row is None else int(row[0])

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Nestable: only the outermost block begins and commits / rolls back."""
        if self._depth == 0:
            self._exec("BEGIN IMMEDIATE")
        self._depth += 1
        try:
            yield
        except BaseException:
            self._depth -= 1
            if self._depth == 0:
                self._exec("ROLLBACK")
            raise
        self._depth -= 1
        if self._depth == 0:
            self._exec("COMMIT")

    # -- lesson_progress -------------------------------------------------------

    @staticmethod
    def _lesson(row: sqlite3.Row) -> LessonProgress:
        return LessonProgress(
            user_id=row["user_id"],
            lesson_id=row["lesson_id"],
            status=LessonStatus(row["status"]),
            started_at=_dt(row["started_at"]),
            completed_at=_dt(row["completed_at"]),
            total_seconds=row["total_seconds"],
            understanding=row["understanding"],
            note=row["note"],
        )

    def get_lesson(self, lesson_id: str, user_id: int = DEFAULT_USER) -> LessonProgress | None:
        row = self._exec(
            "SELECT * FROM lesson_progress WHERE user_id = ? AND lesson_id = ?",
            (user_id, lesson_id),
        ).fetchone()
        return None if row is None else self._lesson(row)

    def save_lesson(self, progress: LessonProgress) -> None:
        self._exec(
            """
            INSERT INTO lesson_progress (user_id, lesson_id, status, started_at, completed_at,
                                         total_seconds, understanding, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (user_id, lesson_id) DO UPDATE SET
                status = excluded.status,
                started_at = excluded.started_at,
                completed_at = excluded.completed_at,
                total_seconds = excluded.total_seconds,
                understanding = excluded.understanding,
                note = excluded.note
            """,
            (
                progress.user_id,
                progress.lesson_id,
                progress.status.value,
                _ts(progress.started_at),
                _ts(progress.completed_at),
                progress.total_seconds,
                progress.understanding,
                progress.note,
            ),
        )

    def list_lessons(self, user_id: int | None = DEFAULT_USER) -> list[LessonProgress]:
        if user_id is None:
            rows = self._exec(
                "SELECT * FROM lesson_progress ORDER BY user_id, lesson_id"
            ).fetchall()
        else:
            rows = self._exec(
                "SELECT * FROM lesson_progress WHERE user_id = ? ORDER BY lesson_id", (user_id,)
            ).fetchall()
        return [self._lesson(row) for row in rows]

    # -- sessions --------------------------------------------------------------

    @staticmethod
    def _session(row: sqlite3.Row) -> Session:
        started = _dt(row["started_at"])
        assert started is not None
        return Session(
            id=row["id"],
            user_id=row["user_id"],
            lesson_id=row["lesson_id"],
            started_at=started,
            ended_at=_dt(row["ended_at"]),
            note=row["note"],
            source=row["source"],
        )

    def open_session(self, user_id: int = DEFAULT_USER) -> Session | None:
        row = self._exec(
            "SELECT * FROM sessions WHERE user_id = ? AND ended_at IS NULL", (user_id,)
        ).fetchone()
        return None if row is None else self._session(row)

    def add_session(self, session: Session) -> Session:
        cursor = self._exec(
            """
            INSERT INTO sessions (id, user_id, lesson_id, started_at, ended_at, note, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session.id,
                session.user_id,
                session.lesson_id,
                _ts(session.started_at),
                _ts(session.ended_at),
                session.note,
                session.source,
            ),
        )
        return session.model_copy(update={"id": cursor.lastrowid})

    def close_session(self, session_id: int, ended_at: datetime, note: str | None) -> None:
        self._exec(
            "UPDATE sessions SET ended_at = ?, note = COALESCE(?, note) WHERE id = ?",
            (_ts(ended_at), note, session_id),
        )

    def delete_session(self, session_id: int) -> None:
        self._exec("DELETE FROM sessions WHERE id = ?", (session_id,))

    def list_sessions(
        self, user_id: int | None = DEFAULT_USER, lesson_id: str | None = None
    ) -> list[Session]:
        clauses: list[str] = []
        params: list[object] = []
        if user_id is not None:
            clauses.append("user_id = ?")
            params.append(user_id)
        if lesson_id is not None:
            clauses.append("lesson_id = ?")
            params.append(lesson_id)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self._exec(f"SELECT * FROM sessions{where} ORDER BY id", params).fetchall()
        return [self._session(row) for row in rows]

    # -- bulk ------------------------------------------------------------------

    def is_empty(self) -> bool:
        return not any(
            self._exec(f"SELECT 1 FROM {table} LIMIT 1").fetchone()
            for table in ("lesson_progress", "sessions")
        )

    def clear(self) -> None:
        with self.transaction():
            self._exec("DELETE FROM sessions")
            self._exec("DELETE FROM lesson_progress")


def _split_sql(script: str) -> list[str]:
    """Split a migration script on ``;`` (migrations contain no string literals with ``;``)."""
    lines = [line for line in script.splitlines() if not line.strip().startswith("--")]
    return [stmt.strip() for stmt in "\n".join(lines).split(";") if stmt.strip()]

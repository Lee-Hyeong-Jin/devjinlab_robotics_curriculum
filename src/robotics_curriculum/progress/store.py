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
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Protocol, Self

from robotics_curriculum.progress.models import (
    DEFAULT_USER,
    ActivityProgress,
    Card,
    CardState,
    LessonProgress,
    LessonStatus,
    QuizAttempt,
    QuizRun,
    Review,
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
    # v2 (P1-2): quizzes, flashcards, SM-2 state. Timestamps are UTC ISO 8601 text,
    # card_state.due is a calendar date (YYYY-MM-DD), bools are 0/1. No FK to content.
    2: """
    CREATE TABLE cards (
        id           TEXT    NOT NULL,
        user_id      INTEGER NOT NULL DEFAULT 1,
        lesson_id    TEXT    NOT NULL,
        question_id  TEXT    NOT NULL,
        front        TEXT    NOT NULL,
        back         TEXT    NOT NULL,
        source       TEXT    NOT NULL CHECK (source IN ('quiz', 'concept')),
        created_at   TEXT    NOT NULL,
        suspended    INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (user_id, id)
    );
    CREATE INDEX cards_user_lesson ON cards (user_id, lesson_id);
    CREATE TABLE card_state (
        user_id        INTEGER NOT NULL DEFAULT 1,
        card_id        TEXT    NOT NULL,
        repetitions    INTEGER NOT NULL DEFAULT 0 CHECK (repetitions >= 0),
        interval_days  INTEGER NOT NULL DEFAULT 0 CHECK (interval_days >= 0),
        ease           REAL    NOT NULL DEFAULT 2.5,
        due            TEXT    NOT NULL,
        PRIMARY KEY (user_id, card_id)
    );
    CREATE INDEX card_state_user_due ON card_state (user_id, due);
    CREATE TABLE reviews (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id          INTEGER NOT NULL DEFAULT 1,
        card_id          TEXT    NOT NULL,
        reviewed_at      TEXT    NOT NULL,
        rating           TEXT    NOT NULL CHECK (rating IN ('again', 'hard', 'good', 'easy')),
        interval_before  INTEGER NOT NULL,
        interval_after   INTEGER NOT NULL,
        ease_after       REAL    NOT NULL
    );
    CREATE INDEX reviews_user_card ON reviews (user_id, card_id);
    CREATE TABLE quiz_attempts (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id      INTEGER NOT NULL DEFAULT 1,
        lesson_id    TEXT    NOT NULL,
        question_id  TEXT    NOT NULL,
        answered_at  TEXT    NOT NULL,
        answer       TEXT    NOT NULL,
        correct      INTEGER NOT NULL
    );
    CREATE INDEX quiz_attempts_user_lesson ON quiz_attempts (user_id, lesson_id);
    CREATE TABLE quiz_runs (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id      INTEGER NOT NULL DEFAULT 1,
        lesson_id    TEXT    NOT NULL,
        activity_id  TEXT,
        started_at   TEXT    NOT NULL,
        finished_at  TEXT    NOT NULL,
        correct      INTEGER NOT NULL,
        total        INTEGER NOT NULL
    );
    CREATE INDEX quiz_runs_user_lesson ON quiz_runs (user_id, lesson_id);
    CREATE TABLE activity_progress (
        user_id      INTEGER NOT NULL DEFAULT 1,
        activity_id  TEXT    NOT NULL,
        lesson_id    TEXT    NOT NULL,
        status       TEXT    NOT NULL DEFAULT 'not_started'
                     CHECK (status IN ('not_started', 'in_progress', 'done')),
        updated_at   TEXT    NOT NULL,
        PRIMARY KEY (user_id, activity_id)
    );
    """,
}
SCHEMA_VERSION = max(MIGRATIONS)
TABLES = (
    "lesson_progress",
    "sessions",
    "cards",
    "card_state",
    "reviews",
    "quiz_attempts",
    "quiz_runs",
    "activity_progress",
)


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


def _req_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _where(user_id: int | None, **equals: object) -> tuple[str, list[object]]:
    """``WHERE`` clause for an optional user filter plus ``column = value`` filters."""
    clauses: list[str] = []
    params: list[object] = []
    if user_id is not None:
        clauses.append("user_id = ?")
        params.append(user_id)
    for column, value in equals.items():
        if value is not None:
            clauses.append(f"{column} = ?")
            params.append(value)
    return (f" WHERE {' AND '.join(clauses)}" if clauses else ""), params


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

    # -- schema v2: cards, SM-2 state, reviews, quiz records (P1-2) --------------

    def get_card(self, card_id: str, user_id: int = DEFAULT_USER) -> Card | None: ...

    def save_card(self, card: Card) -> None:
        """Insert or replace a card (keyed by ``(user_id, id)``)."""
        ...

    def list_cards(
        self, user_id: int | None = DEFAULT_USER, lesson_id: str | None = None
    ) -> list[Card]: ...

    def get_card_state(self, card_id: str, user_id: int = DEFAULT_USER) -> CardState | None: ...

    def save_card_state(self, state: CardState) -> None: ...

    def list_card_states(self, user_id: int | None = DEFAULT_USER) -> list[CardState]: ...

    def add_review(self, review: Review) -> Review: ...

    def list_reviews(
        self, user_id: int | None = DEFAULT_USER, card_id: str | None = None
    ) -> list[Review]: ...

    def add_quiz_attempt(self, attempt: QuizAttempt) -> QuizAttempt: ...

    def list_quiz_attempts(
        self, user_id: int | None = DEFAULT_USER, lesson_id: str | None = None
    ) -> list[QuizAttempt]: ...

    def add_quiz_run(self, run: QuizRun) -> QuizRun: ...

    def list_quiz_runs(
        self, user_id: int | None = DEFAULT_USER, lesson_id: str | None = None
    ) -> list[QuizRun]: ...

    def save_activity(self, progress: ActivityProgress) -> None: ...

    def list_activities(self, user_id: int | None = DEFAULT_USER) -> list[ActivityProgress]: ...

    def delete_user(self, user_id: int) -> tuple[int, int]:
        """Delete every row of one user; returns the (lesson rows, sessions) removed."""
        ...

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

    # -- cards (v2) ------------------------------------------------------------

    @staticmethod
    def _card(row: sqlite3.Row) -> Card:
        return Card(
            id=row["id"],
            user_id=row["user_id"],
            lesson_id=row["lesson_id"],
            question_id=row["question_id"],
            front=row["front"],
            back=row["back"],
            source=row["source"],
            created_at=_req_dt(row["created_at"]),
            suspended=bool(row["suspended"]),
        )

    def get_card(self, card_id: str, user_id: int = DEFAULT_USER) -> Card | None:
        row = self._exec(
            "SELECT * FROM cards WHERE user_id = ? AND id = ?", (user_id, card_id)
        ).fetchone()
        return None if row is None else self._card(row)

    def save_card(self, card: Card) -> None:
        self._exec(
            """
            INSERT INTO cards (id, user_id, lesson_id, question_id, front, back, source,
                               created_at, suspended)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (user_id, id) DO UPDATE SET
                lesson_id = excluded.lesson_id,
                question_id = excluded.question_id,
                front = excluded.front,
                back = excluded.back,
                source = excluded.source,
                created_at = excluded.created_at,
                suspended = excluded.suspended
            """,
            (
                card.id,
                card.user_id,
                card.lesson_id,
                card.question_id,
                card.front,
                card.back,
                card.source,
                _ts(card.created_at),
                int(card.suspended),
            ),
        )

    def list_cards(
        self, user_id: int | None = DEFAULT_USER, lesson_id: str | None = None
    ) -> list[Card]:
        where, params = _where(user_id, lesson_id=lesson_id)
        rows = self._exec(
            f"SELECT * FROM cards{where} ORDER BY user_id, created_at, id", params
        ).fetchall()
        return [self._card(row) for row in rows]

    @staticmethod
    def _card_state(row: sqlite3.Row) -> CardState:
        return CardState(
            card_id=row["card_id"],
            user_id=row["user_id"],
            repetitions=row["repetitions"],
            interval_days=row["interval_days"],
            ease=row["ease"],
            due=date.fromisoformat(row["due"]),
        )

    def get_card_state(self, card_id: str, user_id: int = DEFAULT_USER) -> CardState | None:
        row = self._exec(
            "SELECT * FROM card_state WHERE user_id = ? AND card_id = ?", (user_id, card_id)
        ).fetchone()
        return None if row is None else self._card_state(row)

    def save_card_state(self, state: CardState) -> None:
        self._exec(
            """
            INSERT INTO card_state (user_id, card_id, repetitions, interval_days, ease, due)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (user_id, card_id) DO UPDATE SET
                repetitions = excluded.repetitions,
                interval_days = excluded.interval_days,
                ease = excluded.ease,
                due = excluded.due
            """,
            (
                state.user_id,
                state.card_id,
                state.repetitions,
                state.interval_days,
                state.ease,
                state.due.isoformat(),
            ),
        )

    def list_card_states(self, user_id: int | None = DEFAULT_USER) -> list[CardState]:
        where, params = _where(user_id)
        rows = self._exec(
            f"SELECT * FROM card_state{where} ORDER BY user_id, due, card_id", params
        ).fetchall()
        return [self._card_state(row) for row in rows]

    @staticmethod
    def _review(row: sqlite3.Row) -> Review:
        return Review(
            id=row["id"],
            card_id=row["card_id"],
            user_id=row["user_id"],
            reviewed_at=_req_dt(row["reviewed_at"]),
            rating=row["rating"],
            interval_before=row["interval_before"],
            interval_after=row["interval_after"],
            ease_after=row["ease_after"],
        )

    def add_review(self, review: Review) -> Review:
        cursor = self._exec(
            """
            INSERT INTO reviews (id, user_id, card_id, reviewed_at, rating, interval_before,
                                 interval_after, ease_after)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                review.id,
                review.user_id,
                review.card_id,
                _ts(review.reviewed_at),
                review.rating,
                review.interval_before,
                review.interval_after,
                review.ease_after,
            ),
        )
        return review.model_copy(update={"id": cursor.lastrowid})

    def list_reviews(
        self, user_id: int | None = DEFAULT_USER, card_id: str | None = None
    ) -> list[Review]:
        where, params = _where(user_id, card_id=card_id)
        rows = self._exec(f"SELECT * FROM reviews{where} ORDER BY id", params).fetchall()
        return [self._review(row) for row in rows]

    @staticmethod
    def _attempt(row: sqlite3.Row) -> QuizAttempt:
        return QuizAttempt(
            id=row["id"],
            user_id=row["user_id"],
            lesson_id=row["lesson_id"],
            question_id=row["question_id"],
            answered_at=_req_dt(row["answered_at"]),
            answer=row["answer"],
            correct=bool(row["correct"]),
        )

    def add_quiz_attempt(self, attempt: QuizAttempt) -> QuizAttempt:
        cursor = self._exec(
            """
            INSERT INTO quiz_attempts (id, user_id, lesson_id, question_id, answered_at, answer,
                                       correct)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                attempt.id,
                attempt.user_id,
                attempt.lesson_id,
                attempt.question_id,
                _ts(attempt.answered_at),
                attempt.answer,
                int(attempt.correct),
            ),
        )
        return attempt.model_copy(update={"id": cursor.lastrowid})

    def list_quiz_attempts(
        self, user_id: int | None = DEFAULT_USER, lesson_id: str | None = None
    ) -> list[QuizAttempt]:
        where, params = _where(user_id, lesson_id=lesson_id)
        rows = self._exec(f"SELECT * FROM quiz_attempts{where} ORDER BY id", params).fetchall()
        return [self._attempt(row) for row in rows]

    @staticmethod
    def _run(row: sqlite3.Row) -> QuizRun:
        return QuizRun(
            id=row["id"],
            user_id=row["user_id"],
            lesson_id=row["lesson_id"],
            activity_id=row["activity_id"],
            started_at=_req_dt(row["started_at"]),
            finished_at=_req_dt(row["finished_at"]),
            correct=row["correct"],
            total=row["total"],
        )

    def add_quiz_run(self, run: QuizRun) -> QuizRun:
        cursor = self._exec(
            """
            INSERT INTO quiz_runs (id, user_id, lesson_id, activity_id, started_at, finished_at,
                                   correct, total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run.id,
                run.user_id,
                run.lesson_id,
                run.activity_id,
                _ts(run.started_at),
                _ts(run.finished_at),
                run.correct,
                run.total,
            ),
        )
        return run.model_copy(update={"id": cursor.lastrowid})

    def list_quiz_runs(
        self, user_id: int | None = DEFAULT_USER, lesson_id: str | None = None
    ) -> list[QuizRun]:
        where, params = _where(user_id, lesson_id=lesson_id)
        rows = self._exec(f"SELECT * FROM quiz_runs{where} ORDER BY id", params).fetchall()
        return [self._run(row) for row in rows]

    @staticmethod
    def _activity(row: sqlite3.Row) -> ActivityProgress:
        return ActivityProgress(
            user_id=row["user_id"],
            activity_id=row["activity_id"],
            lesson_id=row["lesson_id"],
            status=LessonStatus(row["status"]),
            updated_at=_req_dt(row["updated_at"]),
        )

    def save_activity(self, progress: ActivityProgress) -> None:
        self._exec(
            """
            INSERT INTO activity_progress (user_id, activity_id, lesson_id, status, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (user_id, activity_id) DO UPDATE SET
                lesson_id = excluded.lesson_id,
                status = excluded.status,
                updated_at = excluded.updated_at
            """,
            (
                progress.user_id,
                progress.activity_id,
                progress.lesson_id,
                progress.status.value,
                _ts(progress.updated_at),
            ),
        )

    def list_activities(self, user_id: int | None = DEFAULT_USER) -> list[ActivityProgress]:
        where, params = _where(user_id)
        rows = self._exec(
            f"SELECT * FROM activity_progress{where} ORDER BY user_id, activity_id", params
        ).fetchall()
        return [self._activity(row) for row in rows]

    # -- bulk ------------------------------------------------------------------

    def delete_user(self, user_id: int) -> tuple[int, int]:
        """Delete every row of ``user_id`` in one transaction (GDPR-style erasure).

        Returns the number of ``lesson_progress`` rows and ``sessions`` removed. Rows of other
        users are untouched; an unknown user yields ``(0, 0)``.
        """
        with self.transaction():
            counts = tuple(
                int(
                    self._exec(
                        f"SELECT count(*) FROM {table} WHERE user_id = ?", (user_id,)
                    ).fetchone()[0]
                )
                for table in ("lesson_progress", "sessions")
            )
            for table in TABLES:
                self._exec(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))
        return counts[0], counts[1]

    def is_empty(self) -> bool:
        return not any(self._exec(f"SELECT 1 FROM {table} LIMIT 1").fetchone() for table in TABLES)

    def clear(self) -> None:
        with self.transaction():
            for table in TABLES:
                self._exec(f"DELETE FROM {table}")


def _split_sql(script: str) -> list[str]:
    """Split a migration script on ``;`` (migrations contain no string literals with ``;``)."""
    lines = [line for line in script.splitlines() if not line.strip().startswith("--")]
    return [stmt.strip() for stmt in "\n".join(lines).split(";") if stmt.strip()]

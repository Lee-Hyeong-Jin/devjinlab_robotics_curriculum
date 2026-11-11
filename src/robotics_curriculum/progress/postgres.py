"""PostgreSQL implementation of :class:`~robotics_curriculum.progress.store.ProgressStore`.

Server mode (Phase 2) stores learner progress in PostgreSQL through SQLAlchemy 2.x Core and
psycopg 3. The schema is owned by Alembic (``progress/migrations/``); the initial revision is
equivalent to SQLite schema v1 (``lesson_progress``, ``sessions``, ``meta``). See
``docs/adr/0007-postgres-store.md``.

Requires the optional extra: ``pip install 'robotics-curriculum[postgres]'``.

Concurrency model: the :class:`~sqlalchemy.engine.Engine` (and its connection pool) is safe to
share between threads and store instances; a store instance is not. Outside
:meth:`PostgresProgressStore.transaction` every call checks a connection out of the pool and
runs in its own short transaction. Inside it, all calls share one connection and commit or
roll back together.
"""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from importlib import resources
from typing import Any, Self

from sqlalchemy import (
    Connection,
    Engine,
    Table,
    create_engine,
    delete,
    func,
    insert,
    select,
    text,
    update,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import RowMapping, make_url

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
from robotics_curriculum.progress.schema import (
    ALL_TABLES,
    activity_progress,
    card_state,
    cards,
    lesson_progress,
    meta_table,
    metadata,
    quiz_attempts,
    quiz_runs,
    reviews,
    sessions,
)
from robotics_curriculum.progress.store import SCHEMA_VERSION

__all__ = [
    "DATABASE_URL_ENV",
    "PostgresProgressStore",
    "dispose_shared_engines",
    "downgrade",
    "make_engine",
    "metadata",
    "normalize_url",
    "shared_engine",
    "upgrade",
]

DATABASE_URL_ENV = "RC_DATABASE_URL"


def normalize_url(url: str) -> str:
    """Map ``postgresql://`` / ``postgres://`` to the psycopg 3 driver; keep explicit drivers."""
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix) :]
    return url


def is_postgres_url(url: str) -> bool:
    return url.startswith(("postgresql://", "postgres://", "postgresql+"))


def make_engine(url: str, **pool_options: Any) -> Engine:
    """Create a pooled engine. ``pool_pre_ping`` drops connections the server closed."""
    options: dict[str, Any] = {"pool_pre_ping": True, "pool_size": 5, "max_overflow": 10}
    options.update(pool_options)
    return create_engine(normalize_url(url), **options)


def alembic_config(url: str | None = None, connection: Connection | None = None) -> Any:
    """Alembic :class:`~alembic.config.Config` pointing at the packaged migration scripts.

    Pass ``connection`` to run migrations on an existing connection (the store does this),
    or ``url`` to let Alembic connect itself.
    """
    from alembic.config import Config

    cfg = Config()
    cfg.set_main_option(
        "script_location", str(resources.files("robotics_curriculum.progress") / "migrations")
    )
    if url is not None:
        # ConfigParser interpolation: escape % in passwords.
        cfg.set_main_option("sqlalchemy.url", normalize_url(url).replace("%", "%%"))
    if connection is not None:
        cfg.attributes["connection"] = connection
    return cfg


def upgrade(engine: Engine, revision: str = "head") -> None:
    """Apply Alembic migrations up to ``revision`` (idempotent)."""
    from alembic import command

    with engine.begin() as conn:
        command.upgrade(alembic_config(connection=conn), revision)


def downgrade(engine: Engine, revision: str = "base") -> None:
    from alembic import command

    with engine.begin() as conn:
        command.downgrade(alembic_config(connection=conn), revision)


_shared_lock = threading.Lock()
_shared_engines: dict[str, Engine] = {}


def shared_engine(url: str) -> Engine:
    """One pooled engine per URL for the whole process, migrated to head on first use.

    ``open_store()`` uses this so that opening a store per CLI call or per API request reuses
    the connection pool instead of building a new one each time.
    """
    key = normalize_url(url)
    with _shared_lock:
        engine = _shared_engines.get(key)
        if engine is None:
            engine = make_engine(key)
            try:
                upgrade(engine)
            except BaseException:
                engine.dispose()
                raise
            _shared_engines[key] = engine
        return engine


def dispose_shared_engines() -> None:
    """Close every shared pool (process shutdown, or tests that recreate the schema)."""
    with _shared_lock:
        for engine in _shared_engines.values():
            engine.dispose()
        _shared_engines.clear()


def _utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _card_row(row: RowMapping) -> dict[str, Any]:
    return {**row, "created_at": _utc(row["created_at"])}


def _lesson(row: RowMapping) -> LessonProgress:
    return LessonProgress(
        user_id=row["user_id"],
        lesson_id=row["lesson_id"],
        status=LessonStatus(row["status"]),
        started_at=_utc(row["started_at"]),
        completed_at=_utc(row["completed_at"]),
        total_seconds=row["total_seconds"],
        understanding=row["understanding"],
        note=row["note"],
    )


def _session(row: RowMapping) -> Session:
    started = _utc(row["started_at"])
    assert started is not None
    return Session(
        id=row["id"],
        user_id=row["user_id"],
        lesson_id=row["lesson_id"],
        started_at=started,
        ended_at=_utc(row["ended_at"]),
        note=row["note"],
        source=row["source"],
    )


class PostgresProgressStore:
    """:class:`ProgressStore` backed by PostgreSQL (SQLAlchemy Core + psycopg 3)."""

    def __init__(
        self,
        url_or_engine: str | Engine,
        *,
        migrate: bool = True,
        **pool_options: Any,
    ) -> None:
        """Open a store.

        ``url_or_engine``: a ``postgresql://`` URL (an engine with a pool is created and
        disposed by :meth:`close`) or a shared :class:`Engine` (left open by :meth:`close`).
        ``migrate``: run ``alembic upgrade head`` first, like the SQLite store does on open.
        Server deployments that migrate as a separate step pass ``False``.
        """
        if isinstance(url_or_engine, Engine):
            self.engine = url_or_engine
            self._owns_engine = False
        else:
            self.engine = make_engine(url_or_engine, **pool_options)
            self._owns_engine = True
        self._conn: Connection | None = None
        self._depth = 0
        if migrate:
            upgrade(self.engine)
        current = self.schema_version
        if current > SCHEMA_VERSION:
            raise RuntimeError(
                f"{make_url(normalize_url(str(self.engine.url))).render_as_string()}: "
                f"schema version {current} is newer than supported {SCHEMA_VERSION}"
            )

    # -- lifecycle -------------------------------------------------------------

    @property
    def schema_version(self) -> int:
        with self._connection() as conn:
            value = conn.execute(
                select(meta_table.c.value).where(meta_table.c.key == "schema_version")
            ).scalar_one_or_none()
        return 0 if value is None else int(value)

    def close(self) -> None:
        if self._conn is not None:  # pragma: no cover - close() inside transaction()
            self._conn.close()
            self._conn = None
        if self._owns_engine:
            self.engine.dispose()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Nestable: only the outermost block begins and commits / rolls back."""
        if self._depth == 0:
            self._conn = self.engine.connect()
            self._conn.begin()
        self._depth += 1
        try:
            yield
        except BaseException:
            self._depth -= 1
            if self._depth == 0:
                self._finish(commit=False)
            raise
        self._depth -= 1
        if self._depth == 0:
            self._finish(commit=True)

    def _finish(self, *, commit: bool) -> None:
        conn = self._conn
        assert conn is not None
        self._conn = None
        try:
            if commit:
                conn.commit()
            else:
                conn.rollback()
        finally:
            conn.close()

    @contextmanager
    def _connection(self) -> Iterator[Connection]:
        """The open transaction's connection, or a fresh auto-committing one."""
        if self._conn is not None:
            yield self._conn
            return
        with self.engine.begin() as conn:
            yield conn

    # -- small SQL helpers -----------------------------------------------------

    def _upsert(self, table: Table, values: dict[str, Any], key: tuple[str, ...]) -> None:
        stmt = pg_insert(table).values(**values)
        updates = {k: stmt.excluded[k] for k in values if k not in key}
        stmt = stmt.on_conflict_do_update(
            index_elements=[table.c[name] for name in key], set_=updates
        )
        with self._connection() as conn:
            conn.execute(stmt)

    def _insert_returning_id(self, table: Table, values: dict[str, Any]) -> int:
        """Insert a row whose id the database generates; an explicit id resyncs the sequence."""
        explicit = values.get("id") is not None
        if not explicit:
            values = {k: v for k, v in values.items() if k != "id"}
        with self._connection() as conn:
            new_id = conn.execute(insert(table).values(**values).returning(table.c.id)).scalar_one()
            if explicit:
                conn.execute(
                    text(
                        f"SELECT setval(pg_get_serial_sequence('{table.name}', 'id'), "
                        f"(SELECT MAX(id) FROM {table.name}))"
                    )
                )
        return int(new_id)

    # -- lesson_progress -------------------------------------------------------

    def get_lesson(self, lesson_id: str, user_id: int = DEFAULT_USER) -> LessonProgress | None:
        with self._connection() as conn:
            row = (
                conn.execute(
                    select(lesson_progress).where(
                        lesson_progress.c.user_id == user_id,
                        lesson_progress.c.lesson_id == lesson_id,
                    )
                )
                .mappings()
                .one_or_none()
            )
        return None if row is None else _lesson(row)

    def save_lesson(self, progress: LessonProgress) -> None:
        values = {
            "user_id": progress.user_id,
            "lesson_id": progress.lesson_id,
            "status": progress.status.value,
            "started_at": _utc(progress.started_at),
            "completed_at": _utc(progress.completed_at),
            "total_seconds": progress.total_seconds,
            "understanding": progress.understanding,
            "note": progress.note,
        }
        stmt = pg_insert(lesson_progress).values(**values)
        stmt = stmt.on_conflict_do_update(
            index_elements=[lesson_progress.c.user_id, lesson_progress.c.lesson_id],
            set_={k: stmt.excluded[k] for k in values if k not in ("user_id", "lesson_id")},
        )
        with self._connection() as conn:
            conn.execute(stmt)

    def list_lessons(self, user_id: int | None = DEFAULT_USER) -> list[LessonProgress]:
        query = select(lesson_progress)
        if user_id is None:
            query = query.order_by(lesson_progress.c.user_id, lesson_progress.c.lesson_id)
        else:
            query = query.where(lesson_progress.c.user_id == user_id).order_by(
                lesson_progress.c.lesson_id
            )
        with self._connection() as conn:
            rows = conn.execute(query).mappings().all()
        return [_lesson(row) for row in rows]

    # -- sessions --------------------------------------------------------------

    def open_session(self, user_id: int = DEFAULT_USER) -> Session | None:
        with self._connection() as conn:
            row = (
                conn.execute(
                    select(sessions).where(
                        sessions.c.user_id == user_id, sessions.c.ended_at.is_(None)
                    )
                )
                .mappings()
                .one_or_none()
            )
        return None if row is None else _session(row)

    def add_session(self, session: Session) -> Session:
        values: dict[str, Any] = {
            "user_id": session.user_id,
            "lesson_id": session.lesson_id,
            "started_at": _utc(session.started_at),
            "ended_at": _utc(session.ended_at),
            "note": session.note,
            "source": session.source,
        }
        if session.id is not None:
            values["id"] = session.id
        with self._connection() as conn:
            new_id = conn.execute(
                insert(sessions).values(**values).returning(sessions.c.id)
            ).scalar_one()
            if session.id is not None:
                # An explicit id (import) does not advance the identity sequence; move it past
                # the largest id so later generated ids do not collide.
                conn.execute(
                    text(
                        "SELECT setval(pg_get_serial_sequence('sessions', 'id'), "
                        "(SELECT MAX(id) FROM sessions))"
                    )
                )
        return session.model_copy(update={"id": new_id})

    def close_session(self, session_id: int, ended_at: datetime, note: str | None) -> None:
        with self._connection() as conn:
            conn.execute(
                update(sessions)
                .where(sessions.c.id == session_id)
                .values(ended_at=_utc(ended_at), note=func.coalesce(note, sessions.c.note))
            )

    def delete_session(self, session_id: int) -> None:
        with self._connection() as conn:
            conn.execute(delete(sessions).where(sessions.c.id == session_id))

    def list_sessions(
        self, user_id: int | None = DEFAULT_USER, lesson_id: str | None = None
    ) -> list[Session]:
        query = select(sessions).order_by(sessions.c.id)
        if user_id is not None:
            query = query.where(sessions.c.user_id == user_id)
        if lesson_id is not None:
            query = query.where(sessions.c.lesson_id == lesson_id)
        with self._connection() as conn:
            rows = conn.execute(query).mappings().all()
        return [_session(row) for row in rows]

    # -- schema v2: cards, SM-2 state, reviews, quiz records (P1-2) ------------

    def get_card(self, card_id: str, user_id: int = DEFAULT_USER) -> Card | None:
        with self._connection() as conn:
            row = (
                conn.execute(select(cards).where(cards.c.user_id == user_id, cards.c.id == card_id))
                .mappings()
                .one_or_none()
            )
        return None if row is None else Card(**_card_row(row))

    def save_card(self, card: Card) -> None:
        values = {
            "user_id": card.user_id,
            "id": card.id,
            "lesson_id": card.lesson_id,
            "question_id": card.question_id,
            "front": card.front,
            "back": card.back,
            "source": card.source,
            "created_at": _utc(card.created_at),
            "suspended": card.suspended,
        }
        self._upsert(cards, values, ("user_id", "id"))

    def list_cards(
        self, user_id: int | None = DEFAULT_USER, lesson_id: str | None = None
    ) -> list[Card]:
        query = select(cards).order_by(cards.c.user_id, cards.c.id)
        if user_id is not None:
            query = query.where(cards.c.user_id == user_id)
        if lesson_id is not None:
            query = query.where(cards.c.lesson_id == lesson_id)
        with self._connection() as conn:
            rows = conn.execute(query).mappings().all()
        return [Card(**_card_row(row)) for row in rows]

    def get_card_state(self, card_id: str, user_id: int = DEFAULT_USER) -> CardState | None:
        with self._connection() as conn:
            row = (
                conn.execute(
                    select(card_state).where(
                        card_state.c.user_id == user_id, card_state.c.card_id == card_id
                    )
                )
                .mappings()
                .one_or_none()
            )
        return None if row is None else CardState(**row)

    def save_card_state(self, state: CardState) -> None:
        self._upsert(card_state, dict(state), ("user_id", "card_id"))

    def list_card_states(self, user_id: int | None = DEFAULT_USER) -> list[CardState]:
        query = select(card_state).order_by(card_state.c.user_id, card_state.c.card_id)
        if user_id is not None:
            query = query.where(card_state.c.user_id == user_id)
        with self._connection() as conn:
            return [CardState(**row) for row in conn.execute(query).mappings().all()]

    def add_review(self, review: Review) -> Review:
        values = dict(review)
        values["reviewed_at"] = _utc(review.reviewed_at)
        return review.model_copy(update={"id": self._insert_returning_id(reviews, values)})

    def list_reviews(
        self, user_id: int | None = DEFAULT_USER, card_id: str | None = None
    ) -> list[Review]:
        query = select(reviews).order_by(reviews.c.id)
        if user_id is not None:
            query = query.where(reviews.c.user_id == user_id)
        if card_id is not None:
            query = query.where(reviews.c.card_id == card_id)
        with self._connection() as conn:
            rows = conn.execute(query).mappings().all()
        return [Review(**{**row, "reviewed_at": _utc(row["reviewed_at"])}) for row in rows]

    def add_quiz_attempt(self, attempt: QuizAttempt) -> QuizAttempt:
        values = dict(attempt)
        values["answered_at"] = _utc(attempt.answered_at)
        return attempt.model_copy(update={"id": self._insert_returning_id(quiz_attempts, values)})

    def list_quiz_attempts(
        self, user_id: int | None = DEFAULT_USER, lesson_id: str | None = None
    ) -> list[QuizAttempt]:
        query = select(quiz_attempts).order_by(quiz_attempts.c.id)
        if user_id is not None:
            query = query.where(quiz_attempts.c.user_id == user_id)
        if lesson_id is not None:
            query = query.where(quiz_attempts.c.lesson_id == lesson_id)
        with self._connection() as conn:
            rows = conn.execute(query).mappings().all()
        return [QuizAttempt(**{**row, "answered_at": _utc(row["answered_at"])}) for row in rows]

    def add_quiz_run(self, run: QuizRun) -> QuizRun:
        values = dict(run)
        values["started_at"] = _utc(run.started_at)
        values["finished_at"] = _utc(run.finished_at)
        return run.model_copy(update={"id": self._insert_returning_id(quiz_runs, values)})

    def list_quiz_runs(
        self, user_id: int | None = DEFAULT_USER, lesson_id: str | None = None
    ) -> list[QuizRun]:
        query = select(quiz_runs).order_by(quiz_runs.c.id)
        if user_id is not None:
            query = query.where(quiz_runs.c.user_id == user_id)
        if lesson_id is not None:
            query = query.where(quiz_runs.c.lesson_id == lesson_id)
        with self._connection() as conn:
            rows = conn.execute(query).mappings().all()
        return [
            QuizRun(
                **{
                    **row,
                    "started_at": _utc(row["started_at"]),
                    "finished_at": _utc(row["finished_at"]),
                }
            )
            for row in rows
        ]

    def save_activity(self, progress: ActivityProgress) -> None:
        values = dict(progress)
        values["status"] = progress.status.value
        values["updated_at"] = _utc(progress.updated_at)
        self._upsert(activity_progress, values, ("user_id", "activity_id"))

    def list_activities(self, user_id: int | None = DEFAULT_USER) -> list[ActivityProgress]:
        query = select(activity_progress).order_by(
            activity_progress.c.user_id, activity_progress.c.activity_id
        )
        if user_id is not None:
            query = query.where(activity_progress.c.user_id == user_id)
        with self._connection() as conn:
            rows = conn.execute(query).mappings().all()
        return [
            ActivityProgress(
                **{
                    **row,
                    "status": LessonStatus(row["status"]),
                    "updated_at": _utc(row["updated_at"]),
                }
            )
            for row in rows
        ]

    # -- bulk ------------------------------------------------------------------

    def is_empty(self) -> bool:
        with self._connection() as conn:
            return not any(conn.execute(select(table).limit(1)).first() for table in ALL_TABLES)

    def clear(self) -> None:
        with self.transaction(), self._connection() as conn:
            for table in ALL_TABLES:
                conn.execute(delete(table))

    def delete_user(self, user_id: int) -> tuple[int, int]:
        """Delete every row for one user (account deletion, FR-10.7).

        Returns the number of lesson rows and sessions removed; ``(0, 0)`` for a user with no
        data. Other users' rows are left untouched.
        """
        with self.transaction(), self._connection() as conn:
            removed_sessions = conn.execute(
                delete(sessions).where(sessions.c.user_id == user_id)
            ).rowcount
            removed_lessons = conn.execute(
                delete(lesson_progress).where(lesson_progress.c.user_id == user_id)
            ).rowcount
            for table in ALL_TABLES:
                if table is not sessions and table is not lesson_progress:
                    conn.execute(delete(table).where(table.c.user_id == user_id))
        return removed_lessons, removed_sessions

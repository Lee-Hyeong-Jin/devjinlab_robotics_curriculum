"""Pick a :class:`ProgressStore` backend, and copy progress between backends.

``$RC_DATABASE_URL`` (or an explicit ``url``) selects the backend:

- ``postgresql://...`` / ``postgres://...`` / ``postgresql+psycopg://...`` -> PostgreSQL
  (needs the ``postgres`` extra)
- ``sqlite:///path/to/progress.db`` -> SQLite at that path
- unset or empty -> SQLite at ``<data_dir>/progress.db`` (Phase 1 local mode, unchanged)

See ``docs/adr/0007-postgres-store.md``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from robotics_curriculum.progress.models import ProgressExport
from robotics_curriculum.progress.store import ProgressStore, SqliteProgressStore

DATABASE_URL_ENV = "RC_DATABASE_URL"
_SQLITE_PREFIX = "sqlite:///"


def database_url() -> str | None:
    """``$RC_DATABASE_URL`` stripped, or ``None`` when unset/empty."""
    value = os.environ.get(DATABASE_URL_ENV, "").strip()
    return value or None


def open_store(data_dir: Path | None = None, url: str | None = None) -> ProgressStore:
    """Open the configured store. ``url`` overrides ``$RC_DATABASE_URL``."""
    url = url if url is not None else database_url()
    if not url:
        if data_dir is None:
            # Imported here: service.open_service() calls this module, so a top-level import
            # of service would be circular.
            from robotics_curriculum.progress.service import default_data_dir

            data_dir = default_data_dir()
        return SqliteProgressStore.in_dir(data_dir)
    if url.startswith(_SQLITE_PREFIX):
        return SqliteProgressStore(url[len(_SQLITE_PREFIX) :])
    if url.startswith(("postgresql://", "postgres://", "postgresql+")):
        try:
            from robotics_curriculum.progress.postgres import PostgresProgressStore
        except ImportError as exc:  # pragma: no cover - extra installed in dev
            raise RuntimeError(
                "PostgreSQL support needs the 'postgres' extra: "
                "pip install 'robotics-curriculum[postgres]'"
            ) from exc
        return PostgresProgressStore(url)
    scheme = url.split(":", 1)[0]
    raise ValueError(
        f"unsupported {DATABASE_URL_ENV} scheme {scheme!r}; use postgresql:// or sqlite:///"
    )


class TransferMode(StrEnum):
    """How :func:`transfer` treats data already in the destination."""

    EMPTY = "empty"  # destination must be empty (like `rc progress import`)
    REPLACE = "replace"  # wipe the destination first
    MERGE = "merge"  # upsert lessons by (user_id, lesson_id); skip duplicate sessions


@dataclass(frozen=True)
class TransferResult:
    lessons: int
    sessions: int
    skipped_sessions: int = 0


class TransferError(RuntimeError):
    pass


def _session_key(user_id: int, lesson_id: str, started_at: object) -> tuple[int, str, str]:
    return (user_id, lesson_id, str(started_at))


def transfer(
    source: ProgressStore | ProgressExport,
    dest: ProgressStore,
    *,
    mode: TransferMode = TransferMode.EMPTY,
    user_id: int | None = None,
) -> TransferResult:
    """Copy lesson progress and sessions from ``source`` into ``dest`` in one transaction.

    ``source`` is another store (e.g. the local SQLite file) or a JSON export.
    ``user_id`` re-homes every record to that user (e.g. a server account); ``None`` keeps
    the stored ids. Session ids are reassigned by ``dest`` so they cannot collide with rows
    already there; a session whose (user, lesson, start time) already exists is skipped in
    MERGE mode, so running the same transfer twice adds nothing.
    """
    if isinstance(source, ProgressExport):
        lessons, sessions = source.lesson_progress, source.sessions
    else:
        lessons, sessions = source.list_lessons(None), source.list_sessions(None)
    if user_id is not None:
        lessons = [p.model_copy(update={"user_id": user_id}) for p in lessons]
        sessions = [s.model_copy(update={"user_id": user_id}) for s in sessions]

    with dest.transaction():
        if mode is TransferMode.EMPTY and not dest.is_empty():
            raise TransferError("destination store is not empty; use mode=replace or merge")
        if mode is TransferMode.REPLACE:
            dest.clear()
        existing = {
            _session_key(s.user_id, s.lesson_id, s.started_at) for s in dest.list_sessions(None)
        }
        for progress in lessons:
            dest.save_lesson(progress)
        added = skipped = 0
        for session in sorted(sessions, key=lambda s: (s.started_at, s.id or 0)):
            key = _session_key(session.user_id, session.lesson_id, session.started_at)
            if key in existing:
                skipped += 1
                continue
            existing.add(key)
            dest.add_session(session.model_copy(update={"id": None}))
            added += 1
    return TransferResult(lessons=len(lessons), sessions=added, skipped_sessions=skipped)

"""Progress use cases (FR-3, FR-10.2) on top of a :class:`ProgressStore`.

Lesson ids are validated against the loaded curriculum. Progress rows are keyed by the
lesson ``id`` from front matter, so a lesson id must be unique across *all* courses
under the curriculum root (see docs/curriculum/CONTENT_MODEL.md).
"""

from __future__ import annotations

import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from robotics_curriculum.content import (
    Course,
    Lesson,
    LoadError,
    Module,
    load_courses,
    validate_courses,
)
from robotics_curriculum.progress.factory import open_store
from robotics_curriculum.progress.models import (
    DEFAULT_USER,
    LessonProgress,
    LessonStatus,
    ProgressExport,
    Session,
)
from robotics_curriculum.progress.store import SCHEMA_VERSION, ProgressStore

DATA_DIR_ENV = "RC_DATA_DIR"
DATA_DIR_NAME = ".rc"


class ProgressError(Exception):
    """A user-facing error (unknown lesson, no open session, ...)."""


def find_repo_root(start: Path | None = None) -> Path:
    """Nearest ancestor of ``start`` (default cwd) holding ``.git`` or ``pyproject.toml``."""
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").is_file():
            return candidate
    return here


def default_data_dir() -> Path:
    """``$RC_DATA_DIR`` if set, else ``<repo>/.rc``."""
    env = os.environ.get(DATA_DIR_ENV)
    return Path(env) if env else find_repo_root() / DATA_DIR_NAME


def default_curriculum_dir() -> Path:
    return find_repo_root() / "curriculum"


_DURATION = re.compile(r"^(?:(?P<h>\d+)h)?(?:(?P<m>\d+)m?)?$")
MAX_DURATION_MINUTES = 24 * 60


def parse_duration(text: str) -> int:
    """Minutes from ``"45"``, ``"45m"``, ``"1h"`` or ``"1h30m"``.

    Must be positive and at most one day; a longer value is bad input (and would overflow
    the database) rather than a session anyone studied.
    """
    match = _DURATION.match(text.strip().lower())
    if not match or not (match["h"] or match["m"]):
        raise ProgressError(f"invalid duration '{text}' (use e.g. 45, 45m, 1h30m)")
    minutes = int(match["h"] or 0) * 60 + int(match["m"] or 0)
    if minutes <= 0:
        raise ProgressError("duration must be positive")
    if minutes > MAX_DURATION_MINUTES:
        raise ProgressError(
            f"duration {text} is longer than a day; log one session per day "
            f"(at most {MAX_DURATION_MINUTES}m)"
        )
    return minutes


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


@dataclass(frozen=True, slots=True)
class LessonSummary:
    """One lesson in teaching order with its progress (or a default ``not_started``)."""

    course: Course
    module: Module
    lesson: Lesson
    progress: LessonProgress
    locked: bool

    @property
    def status(self) -> LessonStatus:
        return self.progress.status


@dataclass(frozen=True, slots=True)
class _Entry:
    course: Course
    module: Module
    lesson: Lesson


class ProgressService:
    def __init__(
        self,
        store: ProgressStore,
        courses: list[Course],
        *,
        user_id: int = DEFAULT_USER,
        clock: Callable[[], datetime] = _utcnow,
    ) -> None:
        self.store = store
        self.courses = courses
        self.user_id = user_id
        self.clock = clock
        self._index: dict[str, _Entry] = {}
        for course in courses:
            for module in course.modules:
                for lesson in module.lessons:
                    if lesson.id in self._index:
                        other = self._index[lesson.id].course.id
                        raise ProgressError(
                            f"lesson id '{lesson.id}' appears in courses '{other}' and "
                            f"'{course.id}'; progress needs globally unique lesson ids"
                        )
                    self._index[lesson.id] = _Entry(course, module, lesson)

    @staticmethod
    def load_curriculum(path: Path) -> list[Course]:
        """Load and fully validate the curriculum under ``path``.

        Every entry point runs the same checks as ``rc validate``: otherwise content that
        the validator rejects (``javascript:`` resource URLs, prerequisite cycles, ids
        shared by two courses) would still reach the site builder and the progress store.
        """
        if not path.is_dir():
            raise ProgressError(f"curriculum directory not found: {path}")
        try:
            courses = load_courses(path)
        except LoadError as exc:
            raise ProgressError(f"cannot load curriculum (run `rc validate`):\n{exc}") from exc
        problems = validate_courses(courses)
        if problems:
            listed = "\n".join(str(problem) for problem in problems[:10])
            more = "" if len(problems) <= 10 else f"\n... and {len(problems) - 10} more"
            raise ProgressError(f"curriculum is invalid (run `rc validate`):\n{listed}{more}")
        return courses

    # -- helpers ---------------------------------------------------------------

    def lesson(self, lesson_id: str) -> Lesson:
        return self._entry(lesson_id).lesson

    def _entry(self, lesson_id: str) -> _Entry:
        try:
            return self._index[lesson_id]
        except KeyError:
            raise ProgressError(f"unknown lesson '{lesson_id}'") from None

    def _progress(self, lesson_id: str) -> LessonProgress:
        found = self.store.get_lesson(lesson_id, self.user_id)
        return found or LessonProgress(user_id=self.user_id, lesson_id=lesson_id)

    def _add_time(self, lesson_id: str, seconds: int, started: datetime) -> LessonProgress:
        progress = self._progress(lesson_id)
        update: dict[str, object] = {"total_seconds": progress.total_seconds + seconds}
        if progress.status is LessonStatus.NOT_STARTED:
            update["status"] = LessonStatus.IN_PROGRESS
        if progress.started_at is None:
            update["started_at"] = started
        progress = progress.model_copy(update=update)
        self.store.save_lesson(progress)
        return progress

    def missing_prerequisites(self, lesson_id: str) -> list[str]:
        """Prerequisite lesson ids of ``lesson_id`` that are not done yet (empty = unlocked)."""
        lesson = self._entry(lesson_id).lesson
        done = {
            p.lesson_id
            for p in self.store.list_lessons(self.user_id)
            if p.status is LessonStatus.DONE
        }
        return [p for p in lesson.prerequisites if p not in done]

    def current_session(self) -> Session | None:
        return self.store.open_session(self.user_id)

    # -- commands --------------------------------------------------------------

    def start(self, lesson_id: str) -> Session:
        """Open a timer session; refuses if one is already open."""
        self._entry(lesson_id)
        with self.store.transaction():
            open_ = self.store.open_session(self.user_id)
            if open_ is not None:
                raise ProgressError(
                    f"a session for '{open_.lesson_id}' is already running "
                    f"(since {open_.started_at:%Y-%m-%d %H:%M} UTC); run `rc stop` first"
                )
            now = self.clock()
            session = self.store.add_session(
                Session(user_id=self.user_id, lesson_id=lesson_id, started_at=now)
            )
            self._add_time(lesson_id, 0, now)
        return session

    def stop(self, note: str | None = None, *, discard: bool = False) -> tuple[Session, int]:
        """Close the open session and add its elapsed seconds; ``discard`` deletes it."""
        with self.store.transaction():
            open_ = self.store.open_session(self.user_id)
            if open_ is None or open_.id is None:
                raise ProgressError("no session is running; start one with `rc start <lesson>`")
            if discard:
                self.store.delete_session(open_.id)
                return open_, 0
            now = self.clock()
            seconds = open_.elapsed_seconds(now)
            self.store.close_session(open_.id, now, note)
            self._add_time(open_.lesson_id, seconds, open_.started_at)
        closed = open_.model_copy(update={"ended_at": now, "note": note or open_.note})
        return closed, seconds

    def log(self, lesson_id: str, minutes: int, note: str | None = None) -> Session:
        """Record a manual session of ``minutes`` ending now."""
        self._entry(lesson_id)
        if minutes <= 0:
            raise ProgressError("minutes must be positive")
        now = self.clock()
        started = now - timedelta(minutes=minutes)
        with self.store.transaction():
            session = self.store.add_session(
                Session(
                    user_id=self.user_id,
                    lesson_id=lesson_id,
                    started_at=started,
                    ended_at=now,
                    note=note,
                    source="manual",
                )
            )
            self._add_time(lesson_id, minutes * 60, started)
        return session

    def done(
        self, lesson_id: str, *, understanding: int | None = None, note: str | None = None
    ) -> tuple[LessonProgress, list[Lesson]]:
        """Mark a lesson done (closing its running session, if any).

        Returns the saved progress and the lessons this completion newly unlocked.
        """
        self._entry(lesson_id)
        if understanding is not None and not 1 <= understanding <= 5:
            raise ProgressError("understanding must be between 1 and 5")
        locked_before = {s.lesson.id for s in self.status() if s.locked}
        with self.store.transaction():
            open_ = self.store.open_session(self.user_id)
            if open_ is not None and open_.lesson_id == lesson_id:
                self.stop()
            now = self.clock()
            progress = self._progress(lesson_id)
            update: dict[str, object] = {"status": LessonStatus.DONE}
            if progress.completed_at is None or progress.status is not LessonStatus.DONE:
                update["completed_at"] = now
            if progress.started_at is None:
                update["started_at"] = now
            if understanding is not None:
                update["understanding"] = understanding
            if note is not None:
                update["note"] = note
            progress = progress.model_copy(update=update)
            self.store.save_lesson(progress)
        unlocked = [
            s.lesson for s in self.status() if s.lesson.id in locked_before and not s.locked
        ]
        return progress, unlocked

    def status(self, course_id: str | None = None) -> list[LessonSummary]:
        """Every lesson (optionally of one course) in teaching order with its progress."""
        stored = {p.lesson_id: p for p in self.store.list_lessons(self.user_id)}
        done = {lid for lid, p in stored.items() if p.status is LessonStatus.DONE}
        result: list[LessonSummary] = []
        for course in self._courses(course_id):
            for module in course.modules:
                for lesson in module.lessons:
                    progress = stored.get(lesson.id) or LessonProgress(
                        user_id=self.user_id, lesson_id=lesson.id
                    )
                    locked = any(p not in done for p in lesson.prerequisites)
                    result.append(LessonSummary(course, module, lesson, progress, locked))
        return result

    def next_lessons(
        self, course_id: str | None = None, limit: int | None = None
    ) -> list[LessonSummary]:
        """Not-done lessons whose prerequisites are all done.

        In-progress lessons come first, then teaching order (course -> module -> lesson).
        """
        candidates = [s for s in self.status(course_id) if s.status != "done" and not s.locked]
        candidates.sort(key=lambda s: s.status != "in_progress")  # stable: keeps teaching order
        return candidates if limit is None else candidates[:limit]

    def _courses(self, course_id: str | None) -> list[Course]:
        if course_id is None:
            return self.courses
        matches = [c for c in self.courses if c.id == course_id]
        if not matches:
            raise ProgressError(f"unknown course '{course_id}'")
        return matches

    # -- export / import (FR-10.2) --------------------------------------------

    def export(self, *, user_id: int | None = None) -> ProgressExport:
        """Progress of every user (``user_id=None``, the CLI default) or of one user."""
        return ProgressExport(
            schema_version=SCHEMA_VERSION,
            exported_at=self.clock(),
            lesson_progress=self.store.list_lessons(user_id),
            sessions=self.store.list_sessions(user_id),
            cards=self.store.list_cards(user_id),
            card_states=self.store.list_card_states(user_id),
            reviews=self.store.list_reviews(user_id),
            quiz_attempts=self.store.list_quiz_attempts(user_id),
            quiz_runs=self.store.list_quiz_runs(user_id),
            activity_progress=self.store.list_activities(user_id),
        )

    def delete_user_data(self, user_id: int | None = None) -> tuple[int, int]:
        """Erase one user's progress (default: this service's user).

        Returns the (lesson rows, sessions) removed. Used by the account-deletion
        path of the server; the CLI has no command for it.
        """
        return self.store.delete_user(self.user_id if user_id is None else user_id)

    def import_(
        self, data: ProgressExport, *, replace: bool = False, allow_unknown: bool = False
    ) -> tuple[int, int]:
        """Load an export. Without ``replace`` the store must be empty. Returns row counts.

        Lesson ids must exist in the loaded curriculum unless ``allow_unknown`` is set:
        an unknown id is dead data no command can reach, and an unknown *open* session
        blocks ``rc start`` until it is stopped by hand.
        """
        if data.schema_version > SCHEMA_VERSION:
            raise ProgressError(
                f"export schema version {data.schema_version} is newer than "
                f"supported {SCHEMA_VERSION}"
            )
        if not replace and not self.store.is_empty():
            raise ProgressError("progress store is not empty; pass --replace to overwrite it")
        if not allow_unknown:
            unknown = sorted(
                {row.lesson_id for row in data.lesson_progress if row.lesson_id not in self._index}
                | {s.lesson_id for s in data.sessions if s.lesson_id not in self._index}
            )
            if unknown:
                listed = ", ".join(f"'{lesson_id}'" for lesson_id in unknown[:5])
                more = "" if len(unknown) <= 5 else f" and {len(unknown) - 5} more"
                raise ProgressError(
                    f"the export refers to {len(unknown)} lesson id(s) that are not in this "
                    f"curriculum: {listed}{more}; pass --allow-unknown to import anyway"
                )
        with self.store.transaction():
            self.store.clear()
            for progress in data.lesson_progress:
                self.store.save_lesson(progress)
            for session in data.sessions:
                self.store.add_session(session)
            for card in data.cards:
                self.store.save_card(card)
            for state in data.card_states:
                self.store.save_card_state(state)
            for review in data.reviews:
                self.store.add_review(review)
            for attempt in data.quiz_attempts:
                self.store.add_quiz_attempt(attempt)
            for run in data.quiz_runs:
                self.store.add_quiz_run(run)
            for activity in data.activity_progress:
                self.store.save_activity(activity)
        return len(data.lesson_progress), len(data.sessions)


def open_service(
    data_dir: Path | None = None,
    curriculum_dir: Path | None = None,
    *,
    clock: Callable[[], datetime] = _utcnow,
) -> ProgressService:
    """Build a service over the SQLite store in ``data_dir`` and the given curriculum."""
    courses = ProgressService.load_curriculum(curriculum_dir or default_curriculum_dir())
    store = open_store(data_dir or default_data_dir())  # $RC_DATABASE_URL may pick PostgreSQL
    return ProgressService(store, courses, clock=clock)

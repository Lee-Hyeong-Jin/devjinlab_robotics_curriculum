"""Pydantic models for learner progress (PRD FR-3, FR-10, section 8).

Every record carries an integer ``user_id`` (default ``1``) so that multi-user support
(FR-10.3) does not need a schema rewrite. Timestamps are timezone-aware UTC.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

DEFAULT_USER = 1


class LessonStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class ProgressModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


SQLITE_MAX_INT = 2**63 - 1
MAX_SECONDS = 100 * 366 * 24 * 3600  # a century of study time; anything more is bad data


class LessonProgress(ProgressModel):
    """Per-lesson state for one user."""

    user_id: int = Field(default=DEFAULT_USER, ge=1)
    lesson_id: str
    status: LessonStatus = LessonStatus.NOT_STARTED
    started_at: datetime | None = None
    completed_at: datetime | None = None
    total_seconds: int = Field(default=0, ge=0, le=MAX_SECONDS)
    understanding: int | None = Field(default=None, ge=1, le=5, description="FR-3.2, 1-5")
    note: str | None = None


class Session(ProgressModel):
    """One study session: a timer run (``rc start``/``rc stop``) or a manual log."""

    id: int | None = Field(default=None, ge=1)
    user_id: int = Field(default=DEFAULT_USER, ge=1)
    lesson_id: str
    started_at: datetime
    ended_at: datetime | None = None
    note: str | None = None
    source: Literal["timer", "manual"] = "timer"

    @model_validator(mode="after")
    def _check_order(self) -> Session:
        if self.ended_at is not None and self.ended_at < self.started_at:
            raise ValueError("ended_at is before started_at")
        return self

    @property
    def is_open(self) -> bool:
        return self.ended_at is None

    def elapsed_seconds(self, end: datetime | None = None) -> int:
        stop = self.ended_at or end
        if stop is None:
            return 0
        return max(0, int((stop - self.started_at).total_seconds()))


CardSource = Literal["quiz", "concept"]
RatingName = Literal["again", "hard", "good", "easy"]


class Card(ProgressModel):
    """A flashcard made from a quiz question (FR-4.2); id is ``<lesson>-<source>-<qid>``."""

    id: str
    user_id: int = DEFAULT_USER
    lesson_id: str
    question_id: str
    front: str
    back: str
    source: CardSource
    created_at: datetime
    suspended: bool = False


class CardState(ProgressModel):
    """SM-2 scheduling state of one card for one user (FR-4.3)."""

    card_id: str
    user_id: int = DEFAULT_USER
    repetitions: int = Field(default=0, ge=0)
    interval_days: int = Field(default=0, ge=0)
    ease: float = Field(default=2.5, ge=1.3)
    due: date


class Review(ProgressModel):
    """One answer given during ``rc review``."""

    id: int | None = None
    card_id: str
    user_id: int = DEFAULT_USER
    reviewed_at: datetime
    rating: RatingName
    interval_before: int = Field(ge=0)
    interval_after: int = Field(ge=0)
    ease_after: float


class QuizAttempt(ProgressModel):
    """One answered question of a quiz run."""

    id: int | None = None
    user_id: int = DEFAULT_USER
    lesson_id: str
    question_id: str
    answered_at: datetime
    answer: str
    correct: bool


class QuizRun(ProgressModel):
    """A completed ``rc quiz`` session: score and timing (AC-4.2)."""

    id: int | None = None
    user_id: int = DEFAULT_USER
    lesson_id: str
    activity_id: str | None = None
    started_at: datetime
    finished_at: datetime
    correct: int = Field(ge=0)
    total: int = Field(ge=0)

    @property
    def seconds(self) -> int:
        return max(0, int((self.finished_at - self.started_at).total_seconds()))


class ActivityProgress(ProgressModel):
    """Per-activity state (platform-design §4.1); Phase 1 only records quiz activities."""

    user_id: int = DEFAULT_USER
    activity_id: str
    lesson_id: str
    status: LessonStatus = LessonStatus.NOT_STARTED
    updated_at: datetime


class ProgressExport(ProgressModel):
    """JSON document produced by ``rc progress export`` (FR-10.2).

    Lists added in schema version 2 default to empty, so a version-1 export still imports.

    The validators enforce the invariants the database also enforces, so an edited or
    hand-written file fails with a readable message instead of a sqlite error mid-import.
    """

    schema_version: int = Field(ge=1)
    exported_at: datetime
    lesson_progress: list[LessonProgress] = Field(default_factory=list)
    sessions: list[Session] = Field(default_factory=list)
    cards: list[Card] = Field(default_factory=list)
    card_states: list[CardState] = Field(default_factory=list)
    reviews: list[Review] = Field(default_factory=list)
    quiz_attempts: list[QuizAttempt] = Field(default_factory=list)
    quiz_runs: list[QuizRun] = Field(default_factory=list)
    activity_progress: list[ActivityProgress] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_consistency(self) -> ProgressExport:
        rows = {(row.user_id, row.lesson_id) for row in self.lesson_progress}
        if len(rows) != len(self.lesson_progress):
            raise ValueError("lesson_progress has two rows for the same user and lesson")
        ids = [s.id for s in self.sessions if s.id is not None]
        if len(set(ids)) != len(ids):
            raise ValueError("two sessions share the same id")
        open_users = [s.user_id for s in self.sessions if s.ended_at is None]
        if len(set(open_users)) != len(open_users):
            raise ValueError("a user has more than one running session")
        for row in self.lesson_progress:
            # A done row without completed_at is accepted: the store allows it and the
            # renderers handle it. Only an impossible ordering is rejected.
            if row.completed_at is not None and row.started_at is not None:
                if row.completed_at < row.started_at:
                    raise ValueError(f"lesson '{row.lesson_id}' completed before it started")
        return self

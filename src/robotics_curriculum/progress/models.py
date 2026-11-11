"""Pydantic models for learner progress (PRD FR-3, FR-10, section 8).

Every record carries an integer ``user_id`` (default ``1``) so that multi-user support
(FR-10.3) does not need a schema rewrite. Timestamps are timezone-aware UTC.
"""

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_USER = 1


class LessonStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class ProgressModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LessonProgress(ProgressModel):
    """Per-lesson state for one user."""

    user_id: int = DEFAULT_USER
    lesson_id: str
    status: LessonStatus = LessonStatus.NOT_STARTED
    started_at: datetime | None = None
    completed_at: datetime | None = None
    total_seconds: int = Field(default=0, ge=0)
    understanding: int | None = Field(default=None, ge=1, le=5, description="FR-3.2, 1-5")
    note: str | None = None


class Session(ProgressModel):
    """One study session: a timer run (``rc start``/``rc stop``) or a manual log."""

    id: int | None = None
    user_id: int = DEFAULT_USER
    lesson_id: str
    started_at: datetime
    ended_at: datetime | None = None
    note: str | None = None
    source: Literal["timer", "manual"] = "timer"

    @property
    def is_open(self) -> bool:
        return self.ended_at is None

    def elapsed_seconds(self, end: datetime | None = None) -> int:
        stop = self.ended_at or end
        if stop is None:
            return 0
        return max(0, int((stop - self.started_at).total_seconds()))


class ProgressExport(ProgressModel):
    """JSON document produced by ``rc progress export`` (FR-10.2)."""

    schema_version: int
    exported_at: datetime
    lesson_progress: list[LessonProgress] = Field(default_factory=list)
    sessions: list[Session] = Field(default_factory=list)

"""Learner progress: models, storage interface + SQLite implementation, service layer."""

from robotics_curriculum.progress.models import (
    DEFAULT_USER,
    LessonProgress,
    LessonStatus,
    ProgressExport,
    Session,
)
from robotics_curriculum.progress.service import (
    LessonSummary,
    ProgressError,
    ProgressService,
    default_curriculum_dir,
    default_data_dir,
    open_service,
    parse_duration,
)
from robotics_curriculum.progress.store import (
    DB_FILENAME,
    SCHEMA_VERSION,
    ProgressStore,
    SqliteProgressStore,
)

__all__ = [
    "DB_FILENAME",
    "DEFAULT_USER",
    "SCHEMA_VERSION",
    "LessonProgress",
    "LessonStatus",
    "LessonSummary",
    "ProgressError",
    "ProgressExport",
    "ProgressService",
    "ProgressStore",
    "Session",
    "SqliteProgressStore",
    "default_curriculum_dir",
    "default_data_dir",
    "open_service",
    "parse_duration",
]

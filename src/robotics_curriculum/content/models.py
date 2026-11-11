"""Pydantic models for curriculum content.

Hierarchy: ``Course > Module > Lesson > Activity`` (PRD section 8; "Track" is the
course directory). Content files are the source of truth; these models describe
their front matter / YAML schema. See ``docs/curriculum/CONTENT_MODEL.md``.
"""

from enum import StrEnum
from pathlib import Path
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

ID_PATTERN = r"^[a-z0-9][a-z0-9-]*$"
Id = Annotated[str, Field(pattern=ID_PATTERN, description="lowercase slug, e.g. m1-vectors")]


class ContentModel(BaseModel):
    """Base: unknown keys in front matter are an error (catches typos)."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ActivityKind(StrEnum):
    READING = "reading"
    QUIZ = "quiz"
    LAB = "lab"
    EXERCISE = "exercise"


class Activity(ContentModel):
    """One unit of learner work inside a lesson."""

    id: Id
    kind: ActivityKind
    title: str = Field(min_length=1)
    estimated_minutes: int | None = Field(default=None, ge=1)
    lab_id: Id | None = Field(default=None, description="required when kind == lab")

    @model_validator(mode="after")
    def _lab_requires_lab_id(self) -> Self:
        if self.kind is ActivityKind.LAB and self.lab_id is None:
            raise ValueError("activity of kind 'lab' requires 'lab_id'")
        if self.kind is not ActivityKind.LAB and self.lab_id is not None:
            raise ValueError("'lab_id' is only allowed when kind == 'lab'")
        return self


class Lesson(ContentModel):
    """A lesson: one ``*.md`` file with YAML front matter."""

    id: Id
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    objectives: list[str] = Field(min_length=1)
    prerequisites: list[Id] = Field(default_factory=list, description="lesson ids")
    difficulty: int = Field(ge=1, le=5)
    estimated_minutes: int = Field(ge=1)
    tags: list[str] = Field(default_factory=list)
    activities: list[Activity] = Field(default_factory=list)

    # Filled by the loader, not by front matter.
    body: str = Field(default="", exclude=True)
    path: Path | None = Field(default=None, exclude=True)


class ModuleMeta(ContentModel):
    """Schema of ``module.yaml``."""

    id: Id
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    lessons: list[str] | None = Field(
        default=None,
        description="lesson file stems in teaching order; omit to use sorted file names",
    )


class Module(ContentModel):
    id: Id
    title: str
    summary: str
    lessons: list[Lesson] = Field(default_factory=list)
    path: Path | None = Field(default=None, exclude=True)


class CourseMeta(ContentModel):
    """Schema of ``course.yaml``."""

    id: Id
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    modules: list[str] | None = Field(
        default=None,
        description="module directory names in order; omit to use sorted directory names",
    )


class Course(ContentModel):
    id: Id
    title: str
    summary: str
    tags: list[str] = Field(default_factory=list)
    modules: list[Module] = Field(default_factory=list)
    path: Path | None = Field(default=None, exclude=True)

    def iter_lessons(self) -> list[Lesson]:
        return [lesson for module in self.modules for lesson in module.lessons]

    def lesson_ids(self) -> set[str]:
        return {lesson.id for lesson in self.iter_lessons()}

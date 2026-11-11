"""Curriculum content: pydantic models, Markdown/YAML loader, and validator."""

from robotics_curriculum.content.loader import ContentError, LoadError, load_course, load_courses
from robotics_curriculum.content.models import (
    Activity,
    ActivityKind,
    Course,
    Lesson,
    Module,
    Resource,
    ResourceKind,
)
from robotics_curriculum.content.validate import check, validate_course, validate_courses

__all__ = [
    "Activity",
    "ActivityKind",
    "ContentError",
    "Course",
    "Lesson",
    "LoadError",
    "Module",
    "Resource",
    "ResourceKind",
    "check",
    "load_course",
    "load_courses",
    "validate_course",
    "validate_courses",
]

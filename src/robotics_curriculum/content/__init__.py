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
from robotics_curriculum.content.quiz_block import (
    LessonQuiz,
    QuizBlock,
    QuizParseError,
    QuizQuestion,
    has_quiz,
    parse_quiz,
)
from robotics_curriculum.content.validate import check, validate_course, validate_courses

__all__ = [
    "Activity",
    "ActivityKind",
    "ContentError",
    "Course",
    "Lesson",
    "LessonQuiz",
    "LoadError",
    "Module",
    "QuizBlock",
    "QuizParseError",
    "QuizQuestion",
    "Resource",
    "ResourceKind",
    "check",
    "has_quiz",
    "load_course",
    "load_courses",
    "parse_quiz",
    "validate_course",
    "validate_courses",
]

"""Curriculum content: pydantic models, Markdown/YAML loader, and validator."""

from robotics_curriculum.content.loader import ContentError, LoadError, load_course, load_courses
from robotics_curriculum.content.models import (
    Activity,
    ActivityKind,
    Course,
    Lesson,
    LessonTranslation,
    LocalizedLesson,
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
from robotics_curriculum.content.sections import (
    STUDY_GUIDE_HEADING,
    extract_study_guide,
    study_guide_headings,
)
from robotics_curriculum.content.validate import check, validate_course, validate_courses

__all__ = [
    "Activity",
    "ActivityKind",
    "ContentError",
    "Course",
    "Lesson",
    "LessonTranslation",
    "LocalizedLesson",
    "LessonQuiz",
    "LoadError",
    "Module",
    "QuizBlock",
    "QuizParseError",
    "STUDY_GUIDE_HEADING",
    "QuizQuestion",
    "Resource",
    "ResourceKind",
    "check",
    "extract_study_guide",
    "has_quiz",
    "load_course",
    "load_courses",
    "parse_quiz",
    "study_guide_headings",
    "validate_course",
    "validate_courses",
]

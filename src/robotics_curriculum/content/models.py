"""Pydantic models for curriculum content.

Hierarchy: ``Course > Module > Lesson > Activity`` (PRD section 8; "Track" is the
course directory). Content files are the source of truth; these models describe
their front matter / YAML schema. See ``docs/curriculum/CONTENT_MODEL.md``.
"""

import dataclasses
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from robotics_curriculum.i18n import DEFAULT_LANG, normalize_lang, translator

ID_PATTERN = r"^[a-z0-9][a-z0-9-]*$"
Id = Annotated[str, Field(pattern=ID_PATTERN, description="lowercase slug, e.g. m1-vectors")]
Level = Literal["기초", "중급", "고급"]

LEVEL_KEYS: dict[str, str] = {"기초": "foundation", "중급": "intermediate", "고급": "advanced"}
"""Level value (the authoring language) -> message key suffix. The value is the stable id
that content, progress and the CLI ``--level`` filter use; only the display label is
translated (``level.foundation`` and friends in ``i18n/locales/``)."""

NO_LEVEL_KEY = "none"
"""Message key suffix for modules that declare no level."""


def level_label(level: str | None, lang: str | None = None) -> str:
    """Display name of a module level in ``lang`` (``"기초"`` -> ``"Foundation"``).

    An unknown value is returned unchanged, so content that invents a level still shows
    something rather than a message key.
    """
    key = LEVEL_KEYS.get(level) if level else NO_LEVEL_KEY
    if key is None:
        return level or ""
    return translator(normalize_lang(lang) or DEFAULT_LANG)(f"level.{key}")


class ContentModel(BaseModel):
    """Base: unknown keys in front matter are an error (catches typos)."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ActivityKind(StrEnum):
    READING = "reading"
    QUIZ = "quiz"
    EXERCISE = "exercise"


class Activity(ContentModel):
    """One unit of learner work inside a lesson."""

    id: Id
    kind: ActivityKind
    title: str = Field(min_length=1)
    estimated_minutes: int | None = Field(default=None, ge=1)


class ResourceKind(StrEnum):
    BOOK = "book"
    COURSE = "course"
    VIDEO = "video"
    ARTICLE = "article"
    OTHER = "other"


class Resource(ContentModel):
    """An external learning resource (book, course, video, ...) for a lesson."""

    title: str = Field(min_length=1)
    url: str | None = None
    kind: ResourceKind | None = None
    note: str | None = None


class ResourceText(ContentModel):
    """The translatable part of a :class:`Resource`: everything but the url and the kind."""

    title: str | None = Field(default=None, min_length=1)
    note: str | None = Field(default=None, min_length=1)


class ConceptText(ContentModel):
    """A translated key-concept flashcard (mirrors ``quiz_block.Concept``)."""

    front: str = Field(min_length=1)
    back: str = Field(min_length=1)


class QuestionText(ContentModel):
    """One quiz question in another language, matched to the original by ``id``.

    The question's ``type`` and ``answer`` live in the lesson body and are never repeated
    here, so a translation cannot change what counts as correct. ``choices``, when given,
    must have exactly as many entries as the original, in the same order.
    """

    id: Annotated[str, Field(pattern=ID_PATTERN)]
    prompt: str = Field(min_length=1)
    choices: list[str] | None = None
    explanation: str = Field(min_length=1)
    concept: ConceptText | None = None


class LessonMetaTranslation(ContentModel):
    """A lesson's *structured* text in another language: ``<lesson>.<lang>.yaml``.

    The prose of a lesson lives in ``<lesson>.<lang>.md`` (see :class:`LessonTranslation`).
    What is left over is held in YAML next to it, because it is data rather than prose:
    activity titles, resource titles and notes, and the quiz. Keeping it in its own file
    also lets the quiz keep its question ids, which a translated Markdown body could not.
    """

    id: Id | None = Field(default=None, description="Must match the base lesson when given.")
    lang: str | None = Field(default=None, description="Must match the file name suffix.")
    activities: dict[str, str] = Field(
        default_factory=dict, description="Activity id -> translated title."
    )
    resources: dict[str, ResourceText] = Field(
        default_factory=dict, description="Resource title in the base lesson -> translated text."
    )
    quiz: list[QuestionText] = Field(
        default_factory=list, description="Quiz questions, matched by question id."
    )

    # Filled by the loader, not by front matter.
    path: Path | None = Field(default=None, exclude=True)

    def question(self, question_id: str) -> QuestionText | None:
        return next((q for q in self.quiz if q.id == question_id), None)


class LessonTranslation(ContentModel):
    """A lesson's text in another language: ``<lesson>.<lang>.md`` next to the lesson.

    Only text is translated. Structure (prerequisites, difficulty, estimated_minutes,
    activities, resources) stays in the base file, so a translation can never change what the
    curriculum graph looks like. See ``docs/curriculum/CONTENT_MODEL.md``.
    """

    id: Id | None = Field(default=None, description="Must match the base lesson when given.")
    lang: str | None = Field(default=None, description="Must match the file name suffix.")
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    objectives: list[str] | None = Field(default=None, min_length=1)
    tags: list[str] | None = None

    # Filled by the loader, not by front matter.
    body: str = Field(default="", exclude=True)
    path: Path | None = Field(default=None, exclude=True)


@dataclass(frozen=True, slots=True)
class LocalizedLesson:
    """A lesson's text in one language, with the base (Korean) text as the fallback."""

    lesson_id: str
    lang: str
    title: str
    summary: str
    objectives: list[str]
    tags: list[str]
    body: str
    translated: bool
    """False when the requested language had no translation and the base text is used."""
    activities: list[Activity] = dataclasses.field(default_factory=list)
    """Activities with their titles in ``lang`` (ids and times are never translated)."""
    resources: list[Resource] = dataclasses.field(default_factory=list)
    """Resources with their title and note in ``lang`` (urls and kinds are not translated)."""


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
    resources: list[Resource] = Field(default_factory=list)

    # Filled by the loader, not by front matter.
    body: str = Field(default="", exclude=True)
    path: Path | None = Field(default=None, exclude=True)
    translations: dict[str, LessonTranslation] = Field(default_factory=dict, exclude=True)
    meta_translations: dict[str, LessonMetaTranslation] = Field(
        default_factory=dict, exclude=True, description="``<lesson>.<lang>.yaml`` by language."
    )

    def localized_activities(self, lang: str | None = None) -> list[Activity]:
        """Activities with their titles in ``lang``; untranslated ones keep the base title."""
        titles = self.meta_translations[lang].activities if lang in self.meta_translations else {}
        return [
            activity.model_copy(update={"title": titles[activity.id]})
            if activity.id in titles
            else activity
            for activity in self.activities
        ]

    def localized_resources(self, lang: str | None = None) -> list[Resource]:
        """Resources with title and note in ``lang``; untranslated ones keep the base text."""
        texts = self.meta_translations[lang].resources if lang in self.meta_translations else {}
        out: list[Resource] = []
        for resource in self.resources:
            text = texts.get(resource.title)
            if text is None:
                out.append(resource)
                continue
            update = {k: v for k, v in (("title", text.title), ("note", text.note)) if v}
            out.append(resource.model_copy(update=update))
        return out

    def localized(self, lang: str | None = None) -> LocalizedLesson:
        """This lesson's text in ``lang``, falling back to the language it was written in.

        Prose (title, summary, objectives, body) comes from ``<lesson>.<lang>.md`` and the
        structured text (activities, resources) from ``<lesson>.<lang>.yaml``; the two are
        independent, so a lesson may have either, both, or neither.
        """
        activities = self.localized_activities(lang)
        resources = self.localized_resources(lang)
        translation = self.translations.get(lang or "") if lang else None
        if translation is None:
            return LocalizedLesson(
                lesson_id=self.id,
                lang=DEFAULT_LANG,
                title=self.title,
                summary=self.summary,
                objectives=list(self.objectives),
                tags=list(self.tags),
                body=self.body,
                translated=False,
                activities=activities,
                resources=resources,
            )
        return LocalizedLesson(
            lesson_id=self.id,
            lang=lang or DEFAULT_LANG,
            title=translation.title,
            summary=translation.summary,
            objectives=list(translation.objectives or self.objectives),
            tags=list(translation.tags if translation.tags is not None else self.tags),
            body=translation.body,
            translated=True,
            activities=activities,
            resources=resources,
        )

    def languages(self) -> list[str]:
        """``[ko, en, ...]``: the base language first, then the translations, sorted."""
        return [DEFAULT_LANG, *sorted(self.translations)]


class ModuleMeta(ContentModel):
    """Schema of ``module.yaml``."""

    id: Id
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    level: Level | None = None
    lessons: list[str] | None = Field(
        default=None,
        description="lesson file stems in teaching order; omit to use sorted file names",
    )


class ModuleTranslation(ContentModel):
    """A module's text in another language: ``module.<lang>.yaml`` next to ``module.yaml``.

    Only text is translated. The lesson list, the level and the id stay in ``module.yaml``,
    so a translation can never change the shape of the course.
    """

    id: Id | None = Field(default=None, description="Must match the module when given.")
    lang: str | None = Field(default=None, description="Must match the file name suffix.")
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)

    path: Path | None = Field(default=None, exclude=True)


@dataclass(frozen=True, slots=True)
class LocalizedModule:
    """A module's text in one language, with the base text as the fallback."""

    module_id: str
    lang: str
    title: str
    summary: str
    level: str | None
    """The stored level value; stable across languages."""
    level_label: str
    """``level`` as it should be shown in ``lang``."""
    translated: bool


class Module(ContentModel):
    id: Id
    title: str
    summary: str
    level: Level | None = None
    lessons: list[Lesson] = Field(default_factory=list)
    path: Path | None = Field(default=None, exclude=True)
    translations: dict[str, ModuleTranslation] = Field(default_factory=dict, exclude=True)

    def localized(self, lang: str | None = None) -> LocalizedModule:
        """This module's text in ``lang``, falling back to the language it was written in."""
        translation = self.translations.get(lang or "") if lang else None
        return LocalizedModule(
            module_id=self.id,
            lang=(lang or DEFAULT_LANG) if translation is not None else DEFAULT_LANG,
            title=translation.title if translation is not None else self.title,
            summary=translation.summary if translation is not None else self.summary,
            level=self.level,
            level_label=level_label(self.level, lang) if self.level else "",
            translated=translation is not None,
        )


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


class CourseTranslation(ContentModel):
    """A course's text in another language: ``course.<lang>.yaml`` next to ``course.yaml``."""

    id: Id | None = Field(default=None, description="Must match the course when given.")
    lang: str | None = Field(default=None, description="Must match the file name suffix.")
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    tags: list[str] | None = None

    path: Path | None = Field(default=None, exclude=True)


@dataclass(frozen=True, slots=True)
class LocalizedCourse:
    """A course's text in one language, with the base text as the fallback."""

    course_id: str
    lang: str
    title: str
    summary: str
    tags: list[str]
    translated: bool


class Course(ContentModel):
    id: Id
    title: str
    summary: str
    tags: list[str] = Field(default_factory=list)
    modules: list[Module] = Field(default_factory=list)
    path: Path | None = Field(default=None, exclude=True)
    translations: dict[str, CourseTranslation] = Field(default_factory=dict, exclude=True)

    def localized(self, lang: str | None = None) -> LocalizedCourse:
        """This course's text in ``lang``, falling back to the language it was written in."""
        translation = self.translations.get(lang or "") if lang else None
        if translation is None:
            return LocalizedCourse(
                course_id=self.id,
                lang=DEFAULT_LANG,
                title=self.title,
                summary=self.summary,
                tags=list(self.tags),
                translated=False,
            )
        return LocalizedCourse(
            course_id=self.id,
            lang=lang or DEFAULT_LANG,
            title=translation.title,
            summary=translation.summary,
            tags=list(translation.tags if translation.tags is not None else self.tags),
            translated=True,
        )

    def iter_lessons(self) -> list[Lesson]:
        return [lesson for module in self.modules for lesson in module.lessons]

    def lesson_ids(self) -> set[str]:
        return {lesson.id for lesson in self.iter_lessons()}

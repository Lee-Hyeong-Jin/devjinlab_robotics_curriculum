"""Load a course from ``curriculum/<course>/`` on disk.

Layout::

    <course>/course.yaml
    <course>/<module>/module.yaml
    <course>/<module>/<lesson>.md     # YAML front matter + Markdown body

Loading collects every error it can (bad YAML, schema violations, missing files)
and raises a single :class:`LoadError` carrying :class:`ContentError` items.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ValidationError

from robotics_curriculum.content.models import (
    Course,
    CourseMeta,
    CourseTranslation,
    Lesson,
    LessonMetaTranslation,
    LessonTranslation,
    Module,
    ModuleMeta,
    ModuleTranslation,
)
from robotics_curriculum.i18n import DEFAULT_LANG, LANGS

COURSE_FILE = "course.yaml"
MODULE_FILE = "module.yaml"
FRONT_MATTER_DELIM = "---"


@dataclass(frozen=True, slots=True)
class ContentError:
    """A problem in one content file."""

    path: Path
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


class LoadError(Exception):
    """Raised when content could not be loaded; ``errors`` lists every problem found."""

    def __init__(self, errors: list[ContentError]) -> None:
        self.errors = errors
        super().__init__("\n".join(str(e) for e in errors))


class _Collector:
    def __init__(self) -> None:
        self.errors: list[ContentError] = []

    def add(self, path: Path, message: str) -> None:
        self.errors.append(ContentError(path, message))

    def add_validation(self, path: Path, exc: ValidationError) -> None:
        for err in exc.errors():
            loc = ".".join(str(part) for part in err["loc"])
            prefix = f"{loc}: " if loc else ""
            self.errors.append(ContentError(path, f"{prefix}{err['msg']}"))


def read_text(path: Path, errors: _Collector) -> str | None:
    """Read ``path`` as UTF-8, recording (instead of raising) decode and I/O errors."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        errors.add(path, "not valid UTF-8 text")
    except OSError as exc:
        errors.add(path, f"cannot read file: {exc.strerror or exc}")
    return None


def _escapes_root(path: Path, root: Path) -> bool:
    """True when ``path`` leaves ``root`` once symlinks are resolved (ASVS V12.3)."""
    try:
        resolved = path.resolve(strict=True)
    except OSError:
        return True
    try:
        return not resolved.is_relative_to(root.resolve())
    except OSError:  # pragma: no cover - root itself unreadable
        return True


def _check_inside(path: Path, root: Path, errors: _Collector) -> bool:
    if _escapes_root(path, root):
        errors.add(path, f"path leaves the content root {root} (symlink or broken link)")
        return False
    return True


def _read_yaml(path: Path, errors: _Collector) -> dict[str, Any] | None:
    text = read_text(path, errors)
    if text is None:
        return None
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        errors.add(path, f"invalid YAML: {exc}")
        return None
    if not isinstance(data, dict):
        errors.add(path, "expected a YAML mapping")
        return None
    return data


def split_front_matter(text: str) -> tuple[str | None, str]:
    """Return ``(front_matter_text, body)``; front matter is ``None`` when absent."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != FRONT_MATTER_DELIM:
        return None, text
    for index in range(1, len(lines)):
        if lines[index].strip() == FRONT_MATTER_DELIM:
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1 :])
    return None, text


def _parse_model[T: BaseModel](
    model: type[T], data: dict[str, Any], path: Path, errors: _Collector
) -> T | None:
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        errors.add_validation(path, exc)
        return None


def load_lesson(
    path: Path, errors: _Collector | None = None, root: Path | None = None
) -> Lesson | None:
    """Load one lesson file; on failure record errors and return ``None``.

    ``root`` (when given) is the content root the file must stay inside.
    """
    errors = errors if errors is not None else _Collector()
    if root is not None and not _check_inside(path, root, errors):
        return None
    text = read_text(path, errors)
    if text is None:
        return None
    front, body = split_front_matter(text)
    if front is None:
        errors.add(path, "missing YAML front matter (file must start with '---')")
        return None
    try:
        data = yaml.safe_load(front)
    except yaml.YAMLError as exc:
        errors.add(path, f"invalid YAML front matter: {exc}")
        return None
    if not isinstance(data, dict):
        errors.add(path, "front matter must be a YAML mapping")
        return None
    for reserved in ("body", "path"):
        if reserved in data:
            errors.add(path, f"'{reserved}' is a reserved key and may not appear in front matter")
            return None
    lesson = _parse_model(Lesson, data, path, errors)
    if lesson is None:
        return None
    lesson.body = body
    lesson.path = path
    return lesson


def _ordered_children(
    listed: list[str] | None,
    found: dict[str, Path],
    meta_path: Path,
    noun: str,
    errors: _Collector,
) -> list[Path]:
    if listed is None:
        return [found[name] for name in sorted(found)]
    result: list[Path] = []
    seen: set[str] = set()
    for name in listed:
        if name in seen:
            errors.add(meta_path, f"{noun} '{name}' listed more than once")
            continue
        seen.add(name)
        if name not in found:
            errors.add(meta_path, f"{noun} '{name}' is listed but does not exist")
            continue
        result.append(found[name])
    for name in sorted(set(found) - seen):
        errors.add(found[name], f"{noun} exists on disk but is not listed in {meta_path.name}")
    return result


_LANG_SUFFIX = re.compile(r"^(?P<stem>.+)\.(?P<lang>[a-z]{2}(?:-[a-z]{2})?)$")


def split_lang_suffix(stem: str) -> tuple[str, str] | None:
    """``"vectors.en"`` -> ``("vectors", "en")``; ``None`` when the stem carries no suffix."""
    match = _LANG_SUFFIX.match(stem)
    if match is None:
        return None
    return match["stem"], match["lang"]


def _collect_translation_files(
    directory: Path, pattern: str, errors: _Collector
) -> dict[str, list[tuple[str, Path]]]:
    """``{stem: [(lang, path), ...]}`` for ``<stem>.<lang>.<ext>`` files in ``directory``.

    Files without a language suffix are skipped (they are the base content). A suffix that
    names the authoring language or a language the build does not support is an error.
    """
    found: dict[str, list[tuple[str, Path]]] = {}
    for path in sorted(directory.glob(pattern)):
        if not path.is_file():
            continue
        suffixed = split_lang_suffix(path.stem)
        if suffixed is None:
            continue
        stem, lang = suffixed
        extension = path.suffix
        if lang == DEFAULT_LANG:
            errors.add(
                path,
                f"'{DEFAULT_LANG}' is the language content is written in; "
                f"drop the suffix and use {stem}{extension}",
            )
            continue
        if lang not in LANGS:
            errors.add(
                path, f"unsupported translation language '{lang}' (supported: {', '.join(LANGS)})"
            )
            continue
        found.setdefault(stem, []).append((lang, path))
    return found


def _load_yaml_translation[T: BaseModel](
    model: type[T], path: Path, lang: str, errors: _Collector, root: Path | None = None
) -> T | None:
    """Load a ``<name>.<lang>.yaml`` sibling file into ``model``."""
    if root is not None and not _check_inside(path, root, errors):
        return None
    data = _read_yaml(path, errors)
    if data is None:
        return None
    if "path" in data:
        errors.add(path, "'path' is a reserved key and may not appear in a translation file")
        return None
    parsed = _parse_model(model, data, path, errors)
    if parsed is None:
        return None
    declared = getattr(parsed, "lang", None)
    if declared is not None and declared != lang:
        errors.add(path, f"file says lang '{declared}' but the file name says '{lang}'")
        return None
    for field, value in (("lang", lang), ("path", path)):
        if hasattr(parsed, field):
            setattr(parsed, field, value)
    return parsed


def _attach_yaml_translations[T: BaseModel](
    model: type[T],
    files: list[tuple[str, Path]],
    owner_id: str,
    noun: str,
    errors: _Collector,
    root: Path | None = None,
) -> dict[str, T]:
    """Load each ``(lang, path)`` and key it by language, checking the declared id."""
    out: dict[str, T] = {}
    for lang, path in files:
        parsed = _load_yaml_translation(model, path, lang, errors, root)
        if parsed is None:
            continue
        declared = getattr(parsed, "id", None)
        if declared is not None and declared != owner_id:
            errors.add(path, f"translation id '{declared}' does not match {noun} id '{owner_id}'")
            continue
        out[lang] = parsed
    return out


def load_translation(
    path: Path, lang: str, errors: _Collector, root: Path | None = None
) -> LessonTranslation | None:
    """Load one ``<lesson>.<lang>.md`` file; on failure record errors and return ``None``."""
    if root is not None and not _check_inside(path, root, errors):
        return None
    text = read_text(path, errors)
    if text is None:
        return None
    front, body = split_front_matter(text)
    if front is None:
        errors.add(path, "missing YAML front matter (file must start with '---')")
        return None
    try:
        data = yaml.safe_load(front)
    except yaml.YAMLError as exc:
        errors.add(path, f"invalid YAML front matter: {exc}")
        return None
    if not isinstance(data, dict):
        errors.add(path, "front matter must be a YAML mapping")
        return None
    for reserved in ("body", "path"):
        if reserved in data:
            errors.add(path, f"'{reserved}' is a reserved key and may not appear in front matter")
            return None
    translation = _parse_model(LessonTranslation, data, path, errors)
    if translation is None:
        return None
    if translation.lang is not None and translation.lang != lang:
        errors.add(
            path, f"front matter says lang '{translation.lang}' but the file name says '{lang}'"
        )
        return None
    translation.lang = lang
    translation.body = body
    translation.path = path
    return translation


def load_module(module_dir: Path, errors: _Collector, root: Path | None = None) -> Module | None:
    root = root if root is not None else module_dir
    meta_path = module_dir / MODULE_FILE
    if not _check_inside(meta_path, root, errors):
        return None
    if not meta_path.is_file():
        errors.add(meta_path, "missing module.yaml")
        return None
    data = _read_yaml(meta_path, errors)
    if data is None:
        return None
    meta = _parse_model(ModuleMeta, data, meta_path, errors)
    if meta is None:
        return None

    found: dict[str, Path] = {
        path.stem: path
        for path in sorted(module_dir.glob("*.md"))
        if path.is_file() and split_lang_suffix(path.stem) is None
    }
    translation_files = _collect_translation_files(module_dir, "*.md", errors)
    meta_files = _collect_translation_files(module_dir, "*.yaml", errors)
    module_translations = _attach_yaml_translations(
        ModuleTranslation,
        meta_files.pop(Path(MODULE_FILE).stem, []),
        meta.id,
        "module",
        errors,
        root,
    )

    lessons: list[Lesson] = []
    for lesson_path in _ordered_children(meta.lessons, found, meta_path, "lesson", errors):
        lesson = load_lesson(lesson_path, errors, root)
        if lesson is None:
            continue
        for lang, path in translation_files.pop(lesson_path.stem, []):
            translation = load_translation(path, lang, errors, root)
            if translation is None:
                continue
            if translation.id is not None and translation.id != lesson.id:
                errors.add(
                    path,
                    f"translation id '{translation.id}' does not match lesson id '{lesson.id}'",
                )
                continue
            lesson.translations[lang] = translation
        lesson.meta_translations.update(
            _attach_yaml_translations(
                LessonMetaTranslation,
                meta_files.pop(lesson_path.stem, []),
                lesson.id,
                "lesson",
                errors,
                root,
            )
        )
        lessons.append(lesson)
    for stem, orphans in translation_files.items():
        for _lang, path in orphans:
            errors.add(path, f"translation has no lesson to translate ({stem}.md is missing)")
    for stem, orphans in meta_files.items():
        for _lang, path in orphans:
            errors.add(path, f"translation has no lesson to translate ({stem}.md is missing)")
    return Module(
        id=meta.id,
        title=meta.title,
        summary=meta.summary,
        level=meta.level,
        lessons=lessons,
        path=module_dir,
        translations=module_translations,
    )


def _is_content_dir(path: Path, marker: str) -> bool:
    return path.is_dir() and not path.name.startswith((".", "_")) and (path / marker).is_file()


def load_course(course_dir: Path) -> Course:
    """Load ``course_dir`` (which must contain ``course.yaml``) or raise :class:`LoadError`."""
    errors = _Collector()
    course = _load_course(course_dir, errors)
    if errors.errors or course is None:
        raise LoadError(errors.errors)
    return course


def _load_course(course_dir: Path, errors: _Collector) -> Course | None:
    meta_path = course_dir / COURSE_FILE
    if not _check_inside(meta_path, course_dir, errors):
        return None
    if not meta_path.is_file():
        errors.add(meta_path, "missing course.yaml")
        return None
    data = _read_yaml(meta_path, errors)
    if data is None:
        return None
    meta = _parse_model(CourseMeta, data, meta_path, errors)
    if meta is None:
        return None

    found = {p.name: p for p in course_dir.iterdir() if _is_content_dir(p, MODULE_FILE)}
    modules: list[Module] = []
    for module_dir in _ordered_children(meta.modules, found, meta_path, "module", errors):
        module = load_module(module_dir, errors, course_dir)
        if module is not None:
            modules.append(module)
    course_files = _collect_translation_files(course_dir, "*.yaml", errors)
    translations = _attach_yaml_translations(
        CourseTranslation,
        course_files.pop(Path(COURSE_FILE).stem, []),
        meta.id,
        "course",
        errors,
        course_dir,
    )
    for stem, orphans in course_files.items():
        for _lang, path in orphans:
            errors.add(path, f"'{stem}' is not translatable here (expected {COURSE_FILE})")
    return Course(
        id=meta.id,
        title=meta.title,
        summary=meta.summary,
        tags=meta.tags,
        modules=modules,
        path=course_dir,
        translations=translations,
    )


def find_course_dirs(root: Path) -> list[Path]:
    """``root`` is either a course directory itself or a parent holding course directories."""
    if (root / COURSE_FILE).is_file():
        return [root]
    return sorted(p for p in root.iterdir() if _is_content_dir(p, COURSE_FILE))


def load_courses(root: Path) -> list[Course]:
    """Load every course under ``root`` or raise :class:`LoadError` with all problems."""
    errors = _Collector()
    course_dirs = find_course_dirs(root)
    if not course_dirs:
        errors.add(root, f"no {COURSE_FILE} found here or in any direct subdirectory")
        raise LoadError(errors.errors)
    courses: list[Course] = []
    for course_dir in course_dirs:
        course = _load_course(course_dir, errors)
        if course is not None:
            courses.append(course)
    if errors.errors:
        raise LoadError(errors.errors)
    return courses

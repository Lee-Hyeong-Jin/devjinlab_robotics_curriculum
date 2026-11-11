"""Load a course from ``curriculum/<course>/`` on disk.

Layout::

    <course>/course.yaml
    <course>/<module>/module.yaml
    <course>/<module>/<lesson>.md     # YAML front matter + Markdown body

Loading collects every error it can (bad YAML, schema violations, missing files)
and raises a single :class:`LoadError` carrying :class:`ContentError` items.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ValidationError

from robotics_curriculum.content.models import (
    Course,
    CourseMeta,
    Lesson,
    Module,
    ModuleMeta,
)

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


def _read_yaml(path: Path, errors: _Collector) -> dict[str, Any] | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
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


def load_lesson(path: Path, errors: _Collector | None = None) -> Lesson | None:
    """Load one lesson file; on failure record errors and return ``None``."""
    errors = errors if errors is not None else _Collector()
    text = path.read_text(encoding="utf-8")
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


def load_module(module_dir: Path, errors: _Collector) -> Module | None:
    meta_path = module_dir / MODULE_FILE
    if not meta_path.is_file():
        errors.add(meta_path, "missing module.yaml")
        return None
    data = _read_yaml(meta_path, errors)
    if data is None:
        return None
    meta = _parse_model(ModuleMeta, data, meta_path, errors)
    if meta is None:
        return None

    found = {p.stem: p for p in module_dir.glob("*.md") if p.is_file()}
    lessons: list[Lesson] = []
    for lesson_path in _ordered_children(meta.lessons, found, meta_path, "lesson", errors):
        lesson = load_lesson(lesson_path, errors)
        if lesson is not None:
            lessons.append(lesson)
    return Module(
        id=meta.id, title=meta.title, summary=meta.summary, lessons=lessons, path=module_dir
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
        module = load_module(module_dir, errors)
        if module is not None:
            modules.append(module)
    return Course(
        id=meta.id,
        title=meta.title,
        summary=meta.summary,
        tags=meta.tags,
        modules=modules,
        path=course_dir,
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

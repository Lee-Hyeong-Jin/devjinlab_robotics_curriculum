"""Cross-file validation of loaded content (FR-1.4).

Rules:

1. every id (course, module, lesson, activity) is unique within a course
2. each lesson prerequisite refers to an existing lesson id (and not itself)
3. the prerequisite graph has no cycles
4. every course has at least one module, every module at least one lesson
5. a resource ``url``, when present, is a well-formed http(s) URL (no network access)
6. resource titles are unique within a lesson
7. quiz blocks in the lesson body parse and reference a quiz activity of the lesson
   (see :mod:`robotics_curriculum.content.quiz_block`)
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit

from robotics_curriculum.content.loader import ContentError, LoadError, load_courses
from robotics_curriculum.content.models import Course, Lesson
from robotics_curriculum.content.quiz_block import QuizParseError, parse_quiz


def validate_course(course: Course) -> list[ContentError]:
    errors: list[ContentError] = []
    course_dir = course.path if course.path is not None else Path(".")
    course_meta = course_dir / "course.yaml"

    if not course.modules:
        errors.append(ContentError(course_meta, "course has no modules"))

    seen: dict[str, Path] = {course.id: course_meta}
    lessons: dict[str, Lesson] = {}

    def claim(id_: str, path: Path) -> None:
        if id_ in seen:
            errors.append(ContentError(path, f"duplicate id '{id_}' (already used in {seen[id_]})"))
        else:
            seen[id_] = path

    for module in course.modules:
        module_dir = module.path if module.path is not None else course_dir / module.id
        module_meta = module_dir / "module.yaml"
        claim(module.id, module_meta)
        if not module.lessons:
            errors.append(ContentError(module_meta, f"module '{module.id}' has no lessons"))
        for lesson in module.lessons:
            lesson_path = lesson.path if lesson.path is not None else module_dir / f"{lesson.id}.md"
            claim(lesson.id, lesson_path)
            lessons.setdefault(lesson.id, lesson)
            for activity in lesson.activities:
                claim(activity.id, lesson_path)
            errors.extend(_check_resources(lesson, lesson_path))
            errors.extend(_check_quiz(lesson, lesson_path))

    # Rule 2: dangling / self prerequisites.
    for lesson in lessons.values():
        lesson_path = lesson.path if lesson.path is not None else course_dir
        for prereq in lesson.prerequisites:
            if prereq == lesson.id:
                msg = f"lesson '{lesson.id}' lists itself as a prerequisite"
                errors.append(ContentError(lesson_path, msg))
            elif prereq not in lessons:
                msg = f"prerequisite '{prereq}' does not match any lesson id"
                errors.append(ContentError(lesson_path, msg))

    # Rule 3: cycles (only over edges that resolve, so rule 2 errors are not duplicated).
    errors.extend(_find_cycles(lessons, course_dir))
    return errors


def _check_resources(lesson: Lesson, path: Path) -> list[ContentError]:
    """Rules 5 and 6: resource URLs are http(s) and titles are unique per lesson."""
    errors: list[ContentError] = []
    titles: set[str] = set()
    for resource in lesson.resources:
        if resource.title in titles:
            msg = f"lesson '{lesson.id}' has duplicate resource title '{resource.title}'"
            errors.append(ContentError(path, msg))
        titles.add(resource.title)
        if resource.url is not None and not is_http_url(resource.url):
            msg = f"resource '{resource.title}' has invalid url '{resource.url}' (need http(s))"
            errors.append(ContentError(path, msg))
    return errors


def _check_quiz(lesson: Lesson, path: Path) -> list[ContentError]:
    """Rule 7: every quiz block parses (one error per problem)."""
    try:
        parse_quiz(lesson)
    except QuizParseError as exc:
        return [ContentError(path, f"lesson '{lesson.id}': {m}") for m in exc.messages]
    return []


def is_http_url(url: str) -> bool:
    """True for a well-formed ``http``/``https`` URL with a host (no network access)."""
    if any(ch.isspace() for ch in url):
        return False
    try:
        parts = urlsplit(url)
        parts.port  # noqa: B018 - raises ValueError on a malformed port
    except ValueError:
        return False
    return parts.scheme in {"http", "https"} and bool(parts.hostname)


def _find_cycles(lessons: dict[str, Lesson], fallback: Path) -> list[ContentError]:
    """Report each prerequisite cycle once, as ``a -> b -> a``."""
    errors: list[ContentError] = []
    white, grey, black = 0, 1, 2
    state = dict.fromkeys(lessons, white)
    stack: list[str] = []
    reported: set[frozenset[str]] = set()

    def visit(node: str) -> None:
        state[node] = grey
        stack.append(node)
        for prereq in lessons[node].prerequisites:
            if prereq not in lessons or prereq == node:
                continue
            if state[prereq] == white:
                visit(prereq)
            elif state[prereq] == grey:
                cycle = stack[stack.index(prereq) :] + [prereq]
                key = frozenset(cycle)
                if key not in reported:
                    reported.add(key)
                    lesson_path = lessons[node].path
                    path = lesson_path if lesson_path is not None else fallback
                    errors.append(ContentError(path, f"prerequisite cycle: {' -> '.join(cycle)}"))
        stack.pop()
        state[node] = black

    for lesson_id in lessons:
        if state[lesson_id] == white:
            visit(lesson_id)
    return errors


def validate_courses(courses: list[Course]) -> list[ContentError]:
    errors: list[ContentError] = []
    for course in courses:
        errors.extend(validate_course(course))
    return errors


def check(root: Path) -> tuple[list[Course], list[ContentError]]:
    """Load and validate everything under ``root``; never raises for content problems."""
    try:
        courses = load_courses(root)
    except LoadError as exc:
        return [], list(exc.errors)
    return courses, validate_courses(courses)

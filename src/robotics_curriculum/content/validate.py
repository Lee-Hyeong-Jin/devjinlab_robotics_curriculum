"""Cross-file validation of loaded content (FR-1.4).

Rules:

1. every id (course, module, lesson, activity) is unique within a course
2. each lesson prerequisite refers to an existing lesson id (and not itself)
3. the prerequisite graph has no cycles
4. every course has at least one module, every module at least one lesson
5. a resource ``url``, when present, is a well-formed http(s) URL (no network access)
6. resource titles are unique within a lesson
7. ids are unique across every course under the content root (progress needs that)
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from urllib.parse import urlsplit

from robotics_curriculum.content.loader import ContentError, LoadError, load_courses
from robotics_curriculum.content.models import Course, Lesson


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
    """Report each prerequisite cycle once, as ``a -> b -> a``.

    Iterative depth-first search: a chain of thousands of lessons must not exhaust the
    interpreter's stack (a recursive version raised ``RecursionError`` past ~1000).
    """
    errors: list[ContentError] = []
    white, grey, black = 0, 1, 2
    state = dict.fromkeys(lessons, white)
    reported: set[frozenset[str]] = set()

    for root in lessons:
        if state[root] != white:
            continue
        stack: list[str] = []
        # (node, iterator over its prerequisites); the node is grey while on the stack.
        work: list[tuple[str, Iterator[str]]] = [(root, iter(lessons[root].prerequisites))]
        state[root] = grey
        stack.append(root)
        while work:
            node, prereqs = work[-1]
            advanced = False
            for prereq in prereqs:
                if prereq not in lessons or prereq == node:
                    continue
                if state[prereq] == white:
                    state[prereq] = grey
                    stack.append(prereq)
                    work.append((prereq, iter(lessons[prereq].prerequisites)))
                    advanced = True
                    break
                if state[prereq] == grey:
                    cycle = stack[stack.index(prereq) :] + [prereq]
                    key = frozenset(cycle)
                    if key not in reported:
                        reported.add(key)
                        lesson_path = lessons[node].path
                        path = lesson_path if lesson_path is not None else fallback
                        msg = f"prerequisite cycle: {' -> '.join(cycle)}"
                        errors.append(ContentError(path, msg))
            if not advanced:
                state[node] = black
                stack.pop()
                work.pop()
    return errors


def validate_courses(courses: list[Course]) -> list[ContentError]:
    """Validate each course, then rule 7: ids are unique across *all* courses.

    Progress rows are keyed by lesson id alone (``docs/curriculum/CONTENT_MODEL.md``), so a
    collision between two courses would make every progress command fail.
    """
    errors: list[ContentError] = []
    for course in courses:
        errors.extend(validate_course(course))
    errors.extend(_check_global_ids(courses))
    return errors


def _check_global_ids(courses: list[Course]) -> list[ContentError]:
    errors: list[ContentError] = []
    owner: dict[str, tuple[str, Path]] = {}
    for course in courses:
        course_dir = course.path if course.path is not None else Path(".")
        items: list[tuple[str, Path]] = [(course.id, course_dir / "course.yaml")]
        for module in course.modules:
            module_dir = module.path if module.path is not None else course_dir / module.id
            items.append((module.id, module_dir / "module.yaml"))
            for lesson in module.lessons:
                path = lesson.path if lesson.path is not None else module_dir / f"{lesson.id}.md"
                items.append((lesson.id, path))
                items += [(activity.id, path) for activity in lesson.activities]
        for id_, path in items:
            previous = owner.get(id_)
            if previous is None:
                owner[id_] = (course.id, path)
            elif previous[0] != course.id:
                msg = f"id '{id_}' is also used in course '{previous[0]}' ({previous[1]})"
                errors.append(ContentError(path, msg))
    return errors


def check(root: Path) -> tuple[list[Course], list[ContentError]]:
    """Load and validate everything under ``root``; never raises for content problems."""
    try:
        courses = load_courses(root)
    except LoadError as exc:
        return [], list(exc.errors)
    return courses, validate_courses(courses)

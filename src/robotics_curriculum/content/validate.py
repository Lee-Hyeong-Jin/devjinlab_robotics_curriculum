"""Cross-file validation of loaded content (FR-1.4).

Rules:

1. every id (course, module, lesson, activity) is unique within a course
2. each lesson prerequisite refers to an existing lesson id (and not itself)
3. the prerequisite graph has no cycles
4. every course has at least one module, every module at least one lesson
5. a resource ``url``, when present, is a well-formed http(s) URL (no network access)
6. resource titles are unique within a lesson
7. ids are unique across every course under the content root (progress needs that)
8. quiz blocks in the lesson body parse and reference a quiz activity of the lesson
   (see :mod:`robotics_curriculum.content.quiz_block`)
9. a ``<lesson>.<lang>.yaml`` translation only names activities, resources and quiz
   questions that the lesson actually has, with the same number of choices, and only
   gives ``answers`` for a ``short`` question
10. a lesson's ``papers[]`` ids exist in the course's ``papers.yaml``, registry ids are
    unique, registry urls are http(s), and a lesson that assigns papers marks at least one
    as required (ADR 0014). Two *warnings*: a registry paper no lesson references, and a
    registry ``lessons[]`` that disagrees with the lessons' own references.

12. links in a lesson body (and in its translations) are either http(s) URLs, anchors, or
    relative paths to a real asset — never a path to another lesson's file. ``mkdocs``
    resolves such a path against the *generated* project, where lessons live elsewhere, so
    it silently becomes a broken link on the site.

Some rules only warn (:attr:`ContentError.severity`). :func:`blocking` filters those out
for callers that must refuse invalid content.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import urlsplit

from robotics_curriculum.content.loader import ContentError, LoadError, load_courses
from robotics_curriculum.content.models import Course, Lesson, Paper
from robotics_curriculum.content.papers import paper_index
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
            errors.extend(_check_body_links(lesson, lesson_path))
            errors.extend(_check_quiz(lesson, lesson_path))
            errors.extend(_check_translations(lesson))
            errors.extend(_check_meta_translations(lesson, lesson_path))

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
    # Rule 10: the paper registry and the lessons that reference it.
    errors.extend(_check_papers(course, lessons, course_dir))
    return errors


def blocking(problems: list[ContentError]) -> list[ContentError]:
    """Only the problems that must stop the content being used (warnings dropped)."""
    return [problem for problem in problems if problem.blocking]


def _check_papers(
    course: Course, lessons: dict[str, Lesson], course_dir: Path
) -> list[ContentError]:
    """Rule 10. A course with no ``papers.yaml`` and no lesson references is silent."""
    errors: list[ContentError] = []
    papers_path = course_dir / "papers.yaml"

    seen: dict[str, Paper] = {}
    for paper in course.papers:
        if paper.id in seen:
            errors.append(ContentError(papers_path, f"duplicate paper id '{paper.id}'"))
            continue
        seen[paper.id] = paper
        if paper.url is not None and not is_http_url(paper.url):
            msg = f"paper '{paper.id}' has invalid url '{paper.url}' (need http(s))"
            errors.append(ContentError(papers_path, msg))

    index = paper_index(course)
    referenced: dict[str, set[str]] = {paper_id: set() for paper_id in index}
    for lesson in lessons.values():
        path = lesson.path if lesson.path is not None else course_dir
        ids: set[str] = set()
        for ref in lesson.papers:
            if ref.id in ids:
                errors.append(
                    ContentError(path, f"lesson '{lesson.id}' lists paper '{ref.id}' twice")
                )
            ids.add(ref.id)
            if ref.id not in index:
                msg = (
                    f"lesson '{lesson.id}' references paper '{ref.id}', which is not in "
                    f"{papers_path.name}"
                )
                errors.append(ContentError(path, msg))
            else:
                referenced[ref.id].add(lesson.id)
        if lesson.papers and not any(ref.required for ref in lesson.papers):
            msg = (
                f"lesson '{lesson.id}' assigns {len(lesson.papers)} paper(s) but marks none "
                f"'required: true'; a lesson with papers needs at least one required reading"
            )
            errors.append(ContentError(path, msg))

    for paper_id, lesson_ids in referenced.items():
        if not lesson_ids:
            errors.append(
                ContentError(
                    papers_path,
                    f"paper '{paper_id}' is in the registry but no lesson references it",
                    severity="warning",
                )
            )
            continue
        declared = seen[paper_id].lessons
        if declared is not None and set(declared) != lesson_ids:
            errors.append(
                ContentError(
                    papers_path,
                    f"paper '{paper_id}' lists lessons {sorted(declared)} but is referenced by "
                    f"{sorted(lesson_ids)}; the lessons' own `papers` win",
                    severity="warning",
                )
            )
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


#: A Markdown inline link or image: ``[text](target "title")``, ``![alt](target)``.
_LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s<>]+)>?(?:\s+[\"'][^\"']*[\"'])?\s*\)")
_FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
#: Schemes an external link may use. Anything else is almost always a typo.
_ALLOWED_SCHEMES = ("http", "https", "mailto")


def _link_targets(markdown: str) -> Iterator[str]:
    """Link targets outside fenced code blocks (a quiz block is one, and holds no links)."""
    fence: str | None = None
    for line in markdown.split("\n"):
        marker = _FENCE.match(line)
        if marker:
            char = (marker.group(1) or "")[0]
            if fence is None:
                fence = char
            elif char == fence:
                fence = None
            continue
        if fence is not None:
            continue
        for match in _LINK.finditer(line):
            yield match.group(1)


def _check_body_links(lesson: Lesson, path: Path) -> list[ContentError]:
    """Rule 12: body links are URLs, anchors or assets — never another lesson's file.

    Checks the translations too: a ``<lesson>.<lang>.md`` can introduce its own bad link.
    """
    errors: list[ContentError] = []
    bodies = [("", lesson.body)] + [
        (f" ({lang})", translation.body)
        for lang, translation in sorted(lesson.translations.items())
    ]
    for suffix, body in bodies:
        if not body:
            continue
        for target in _link_targets(body):
            where = f"lesson '{lesson.id}'{suffix}"
            scheme = urlsplit(target).scheme.lower()
            if target.startswith("#"):
                continue
            if scheme in ("http", "https"):
                if not is_http_url(target):
                    errors.append(ContentError(path, f"{where} has a malformed link '{target}'"))
                continue
            if scheme == "mailto":
                continue
            if scheme:
                msg = (
                    f"{where} links with the '{scheme}:' scheme ('{target}'); "
                    f"only {', '.join(_ALLOWED_SCHEMES)} are allowed"
                )
                errors.append(ContentError(path, msg))
                continue
            # A relative path. Pointing at a Markdown file is the mistake worth catching:
            # the site generates its own tree, so the path cannot resolve there.
            if target.split("#", 1)[0].endswith(".md"):
                msg = (
                    f"{where} links to a lesson file ('{target}'). Lesson files are not laid "
                    f"out the same way on the site, so this becomes a broken link; write the "
                    f"lesson id in backticks instead, e.g. `m1-vectors-matrices`"
                )
                errors.append(ContentError(path, msg))
    return errors


def _check_quiz(lesson: Lesson, path: Path) -> list[ContentError]:
    """Rule 7: every quiz block parses (one error per problem)."""
    try:
        parse_quiz(lesson)
    except QuizParseError as exc:
        return [ContentError(path, f"lesson '{lesson.id}': {m}") for m in exc.messages]
    return []


def _check_translations(lesson: Lesson) -> list[ContentError]:
    """Rule 8: a translation must actually carry text."""
    errors: list[ContentError] = []
    for lang, translation in sorted(lesson.translations.items()):
        path = translation.path if translation.path is not None else lesson.path
        if path is None:  # pragma: no cover - a translation always comes from a file
            continue
        if not translation.body.strip():
            errors.append(
                ContentError(path, f"'{lang}' translation of '{lesson.id}' has an empty body")
            )
    return errors


def _check_meta_translations(lesson: Lesson, lesson_path: Path) -> list[ContentError]:
    """Rule 9: ``<lesson>.<lang>.yaml`` may only translate text that exists in the lesson.

    A key that matches nothing is almost always a typo or a rename that was not followed
    through, and it would silently leave the reader with the original language.
    """
    errors: list[ContentError] = []
    activity_ids = {activity.id for activity in lesson.activities}
    resource_titles = {resource.title for resource in lesson.resources}
    try:
        questions = {q.id: q for q in parse_quiz(lesson).questions}
    except QuizParseError:
        questions = {}  # the quiz itself is already reported by _check_quiz
    for lang, meta in sorted(lesson.meta_translations.items()):
        path = meta.path if meta.path is not None else lesson_path
        where = f"'{lang}' translation of '{lesson.id}'"
        for activity_id in sorted(set(meta.activities) - activity_ids):
            errors.append(ContentError(path, f"{where}: no activity '{activity_id}'"))
        for title in sorted(set(meta.resources) - resource_titles):
            errors.append(ContentError(path, f"{where}: no resource titled '{title}'"))
        seen: set[str] = set()
        for question in meta.quiz:
            if question.id in seen:
                errors.append(ContentError(path, f"{where}: duplicate question '{question.id}'"))
            seen.add(question.id)
            original = questions.get(question.id)
            if original is None:
                errors.append(ContentError(path, f"{where}: no quiz question '{question.id}'"))
                continue
            if question.choices is not None and len(question.choices) != len(original.choices):
                errors.append(
                    ContentError(
                        path,
                        f"{where}: question '{question.id}' has {len(question.choices)} "
                        f"choices but the lesson has {len(original.choices)}",
                    )
                )
            if question.answers is not None and original.type != "short":
                errors.append(
                    ContentError(
                        path,
                        f"{where}: question '{question.id}' is a '{original.type}' question, "
                        f"so 'answers' does not apply (only 'short' questions have them)",
                    )
                )
            if question.answers is not None and any(not a.strip() for a in question.answers):
                errors.append(
                    ContentError(
                        path, f"{where}: question '{question.id}' has an empty accepted answer"
                    )
                )
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

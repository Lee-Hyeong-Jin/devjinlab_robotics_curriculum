"""Learning paths: the lessons a goal needs, and nothing else.

The course is one line from the first lesson to the last. A learner who wants a robot that
navigates does not need manipulator dynamics on the way, and one who wants to train policies
does not need Nav2. Given the lessons that reach a goal, the path is those lessons plus
everything they depend on, in the order the course teaches them.

Pure functions over the content model: no progress, no I/O.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from robotics_curriculum.content.models import Course, Goal, Lesson


class PathError(ValueError):
    """The path was asked for something the course does not have."""


@dataclass(frozen=True, slots=True)
class LearningPath:
    """The lessons that lead to some targets, in teaching order."""

    targets: tuple[str, ...]
    lessons: tuple[Lesson, ...]
    goal: Goal | None = None

    @property
    def lesson_ids(self) -> tuple[str, ...]:
        return tuple(lesson.id for lesson in self.lessons)

    @property
    def total_minutes(self) -> int:
        return sum(lesson.estimated_minutes for lesson in self.lessons)

    def remaining_minutes(self, done: Iterable[str]) -> int:
        """Estimated minutes of the path's lessons that are not in ``done``."""
        finished = set(done)
        return sum(lesson.estimated_minutes for lesson in self.lessons if lesson.id not in finished)


def prerequisite_closure(course: Course, targets: Iterable[str]) -> LearningPath:
    """The targets and every lesson they depend on, directly or not, in teaching order.

    Teaching order (course -> module -> lesson) is a valid order for the result as long as no
    lesson lists a later lesson as a prerequisite; where one does, prerequisites are moved
    ahead of the lessons that need them, so the result can always be followed top to bottom.

    Args:
        course: The course the targets belong to.
        targets: Lesson ids to reach.

    Raises:
        PathError: A target is not a lesson of the course, or no target was given.
    """
    by_id = {lesson.id: lesson for lesson in course.iter_lessons()}
    wanted = tuple(dict.fromkeys(targets))
    if not wanted:
        raise PathError("a path needs at least one target lesson")
    for target in wanted:
        if target not in by_id:
            raise PathError(f"'{target}' is not a lesson of course '{course.id}'")

    needed: set[str] = set()
    stack = list(wanted)
    while stack:
        lesson_id = stack.pop()
        if lesson_id in needed:
            continue
        needed.add(lesson_id)
        # A prerequisite outside the course (or a dangling one) is validation's business.
        stack.extend(p for p in by_id[lesson_id].prerequisites if p in by_id)

    ordered: list[Lesson] = []
    placed: set[str] = set()

    def place(lesson: Lesson, trail: tuple[str, ...] = ()) -> None:
        if lesson.id in placed or lesson.id in trail:  # the second guards against a cycle
            return
        for prerequisite in lesson.prerequisites:
            if prerequisite in needed:
                place(by_id[prerequisite], (*trail, lesson.id))
        placed.add(lesson.id)
        ordered.append(lesson)

    for lesson in course.iter_lessons():
        if lesson.id in needed:
            place(lesson)
    return LearningPath(targets=wanted, lessons=tuple(ordered))


def goal_path(course: Course, goal: Goal) -> LearningPath:
    """The path to one of the course's goals."""
    path = prerequisite_closure(course, goal.targets)
    return LearningPath(targets=path.targets, lessons=path.lessons, goal=goal)


def find_goal(course: Course, goal_id: str) -> Goal | None:
    return next((goal for goal in course.goals if goal.id == goal_id), None)


def resolve_path(courses: Iterable[Course], name: str) -> tuple[Course, LearningPath]:
    """The path to a goal or to a single lesson, whichever ``name`` is.

    A goal id is looked up first (in course order), then a lesson id.

    Raises:
        PathError: ``name`` is neither a goal nor a lesson of any course.
    """
    available = list(courses)
    for course in available:
        goal = find_goal(course, name)
        if goal is not None:
            return course, goal_path(course, goal)
    for course in available:
        if name in course.lesson_ids():
            return course, prerequisite_closure(course, [name])
    known = sorted(goal.id for course in available for goal in course.goals)
    hint = f" (goals: {', '.join(known)})" if known else ""
    raise PathError(f"'{name}' is neither a goal nor a lesson id{hint}")

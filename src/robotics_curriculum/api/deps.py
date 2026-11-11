"""Dependencies: content index, per-request progress service, current user.

The content is loaded once (at app creation) through the core loader. Each progress
request opens its own store connection, so the server holds no per-user state and an
SQLite connection never crosses threads.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Annotated

from fastapi import Depends, HTTPException, Request

from robotics_curriculum.api.settings import Settings
from robotics_curriculum.content import Course, Lesson, Module
from robotics_curriculum.progress import (
    DEFAULT_USER,
    ProgressError,
    ProgressService,
    SqliteProgressStore,
)


@dataclass(frozen=True, slots=True)
class LessonEntry:
    course: Course
    module: Module
    lesson: Lesson


@dataclass(frozen=True, slots=True)
class ModuleEntry:
    course: Course
    module: Module


@dataclass(slots=True)
class ContentIndex:
    """Id lookups over the loaded courses.

    Raises :class:`ProgressError` when a lesson id repeats across courses, the same rule
    :class:`ProgressService` enforces (progress rows are keyed by lesson id).
    """

    courses: list[Course]
    _courses: dict[str, Course] = field(init=False, default_factory=dict)
    _modules: dict[str, ModuleEntry] = field(init=False, default_factory=dict)
    _lessons: dict[str, LessonEntry] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        for course in self.courses:
            self._courses.setdefault(course.id, course)
            for module in course.modules:
                self._modules.setdefault(module.id, ModuleEntry(course, module))
                for lesson in module.lessons:
                    if lesson.id in self._lessons:
                        other = self._lessons[lesson.id].course.id
                        raise ProgressError(
                            f"lesson id '{lesson.id}' appears in courses '{other}' and "
                            f"'{course.id}'; progress needs globally unique lesson ids"
                        )
                    self._lessons[lesson.id] = LessonEntry(course, module, lesson)

    @property
    def lesson_count(self) -> int:
        return len(self._lessons)

    def course(self, course_id: str) -> Course:
        try:
            return self._courses[course_id]
        except KeyError:
            raise HTTPException(404, f"unknown course '{course_id}'") from None

    def module(self, module_id: str) -> ModuleEntry:
        try:
            return self._modules[module_id]
        except KeyError:
            raise HTTPException(404, f"unknown module '{module_id}'") from None

    def lesson(self, lesson_id: str) -> LessonEntry:
        try:
            return self._lessons[lesson_id]
        except KeyError:
            raise HTTPException(404, f"unknown lesson '{lesson_id}'") from None


@dataclass(slots=True)
class AppState:
    """What :func:`~robotics_curriculum.api.app.create_app` keeps on ``app.state.rc``."""

    settings: Settings
    clock: Callable[[], datetime]
    index: ContentIndex | None = None
    load_error: str | None = None


def get_state(request: Request) -> AppState:
    state = request.app.state.rc
    assert isinstance(state, AppState)
    return state


def get_index(state: Annotated[AppState, Depends(get_state)]) -> ContentIndex:
    """The content index, or 503 when the curriculum failed to load."""
    if state.index is None:
        raise HTTPException(503, f"curriculum not loaded: {state.load_error}")
    return state.index


def current_user_id() -> int:
    """The acting user. Fixed to the local user until authentication lands (P2-2)."""
    return DEFAULT_USER


@dataclass(frozen=True, slots=True)
class ProgressFactory:
    """Opens a :class:`ProgressService` for one request (use as a context manager)."""

    state: AppState
    index: ContentIndex
    user_id: int

    @contextmanager
    def open(self) -> Iterator[ProgressService]:
        """Yield a service; core :class:`ProgressError` becomes a 409 Conflict."""
        store = SqliteProgressStore.in_dir(self.state.settings.data_dir)
        try:
            yield ProgressService(
                store, self.index.courses, user_id=self.user_id, clock=self.state.clock
            )
        except ProgressError as exc:
            raise HTTPException(409, str(exc)) from None
        finally:
            store.close()


def get_progress(
    state: Annotated[AppState, Depends(get_state)],
    index: Annotated[ContentIndex, Depends(get_index)],
    user_id: Annotated[int, Depends(current_user_id)],
) -> ProgressFactory:
    return ProgressFactory(state, index, user_id)


Index = Annotated[ContentIndex, Depends(get_index)]
Progress = Annotated[ProgressFactory, Depends(get_progress)]
State = Annotated[AppState, Depends(get_state)]

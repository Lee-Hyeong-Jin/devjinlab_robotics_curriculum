"""Dependencies: content index, per-request progress service, current user.

The content is loaded once (at app creation) through the core loader. Each progress
request opens its own store connection, so the server holds no per-user state and an
SQLite connection never crosses threads.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException, Request

from robotics_curriculum.api.log import request_id_var
from robotics_curriculum.api.settings import Settings
from robotics_curriculum.auth.models import Role, Scope, User
from robotics_curriculum.auth.oidc import OidcClient
from robotics_curriculum.auth.service import AuthService, Context, Principal
from robotics_curriculum.content import Course, Lesson, Module
from robotics_curriculum.progress import (
    DEFAULT_USER,
    ProgressError,
    ProgressService,
    ProgressStore,
)
from robotics_curriculum.progress.factory import open_store


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
    auth: AuthService | None = None
    oidc: dict[str, OidcClient] = field(default_factory=dict)
    flow_key: bytes = b""


def get_state(request: Request) -> AppState:
    state = request.app.state.rc
    assert isinstance(state, AppState)
    return state


State = Annotated[AppState, Depends(get_state)]


def get_index(state: State) -> ContentIndex:
    """The content index, or 503 when the curriculum failed to load."""
    if state.index is None:
        raise HTTPException(503, f"curriculum not loaded: {state.load_error}")
    return state.index


# -- authentication ------------------------------------------------------------------------

SESSION_COOKIE = "sid"
CSRF_COOKIE = "csrf_token"
CSRF_HEADER = "X-CSRF-Token"
SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})

_LOCAL_USER = User(
    id=DEFAULT_USER,
    email="local@localhost",
    role=Role.ADMIN,
    created_at=datetime(2026, 1, 1, tzinfo=UTC),
    updated_at=datetime(2026, 1, 1, tzinfo=UTC),
)
LOCAL_PRINCIPAL = Principal(user=_LOCAL_USER)


def request_context(request: Request) -> Context:
    return Context(
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_id=request_id_var.get(),
    )


Ctx = Annotated[Context, Depends(request_context)]


def get_auth(state: State) -> AuthService:
    """The auth service; 404 in local mode, where accounts do not exist."""
    if state.auth is None:
        raise HTTPException(404, "accounts are only available in server mode (RC_AUTH_MODE=server)")
    return state.auth


Auth = Annotated[AuthService, Depends(get_auth)]


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(401, detail, headers={"WWW-Authenticate": 'Bearer realm="rc"'})


def optional_principal(request: Request, state: State) -> Principal | None:
    """The caller from ``Authorization: Bearer <PAT>`` or the session cookie, if valid."""
    if state.auth is None:
        return LOCAL_PRINCIPAL
    header = request.headers.get("authorization", "")
    if header:
        scheme, _, credentials = header.partition(" ")
        if scheme.lower() != "bearer" or not credentials.strip():
            raise _unauthorized("unsupported Authorization header (use Bearer <token>)")
        principal = state.auth.authenticate_token(credentials.strip())
        if principal is None:
            raise _unauthorized("invalid or expired token")
        return principal
    cookie = request.cookies.get(SESSION_COOKIE)
    return state.auth.authenticate_session(cookie) if cookie else None


def get_principal(
    request: Request, principal: Annotated[Principal | None, Depends(optional_principal)]
) -> Principal:
    """Authenticated caller (401 otherwise). Enforces CSRF on cookie-authenticated writes
    and the PAT scope for the method (reads need ``read:progress``, writes
    ``write:progress``)."""
    if principal is None:
        raise _unauthorized("authentication required")
    if principal is LOCAL_PRINCIPAL:
        return principal
    unsafe = request.method not in SAFE_METHODS
    if unsafe and not AuthService.check_csrf(principal, request.headers.get(CSRF_HEADER)):
        raise HTTPException(403, f"missing or invalid {CSRF_HEADER} header")
    scope = Scope.WRITE_PROGRESS if unsafe else Scope.READ_PROGRESS
    if not principal.has_scope(scope):
        raise HTTPException(403, f"token lacks the '{scope.value}' scope")
    return principal


CurrentPrincipal = Annotated[Principal, Depends(get_principal)]


def require_session(principal: CurrentPrincipal) -> Principal:
    """Account-management endpoints refuse personal access tokens."""
    if principal.via_token:
        raise HTTPException(403, "this endpoint needs a browser session, not a token")
    return principal


SessionPrincipal = Annotated[Principal, Depends(require_session)]


def require_admin(principal: CurrentPrincipal) -> Principal:
    if principal.user.role is not Role.ADMIN:
        raise HTTPException(403, "admin role required")
    if principal.via_token and not principal.has_scope(Scope.ADMIN):
        raise HTTPException(403, "token lacks the 'admin' scope")
    return principal


AdminPrincipal = Annotated[Principal, Depends(require_admin)]


def current_user_id(principal: CurrentPrincipal) -> int:
    """The acting user: user 1 in local mode, the authenticated user in server mode."""
    return principal.user.id


# -- progress ------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ProgressFactory:
    """Opens a :class:`ProgressService` for one request (use as a context manager)."""

    state: AppState
    index: ContentIndex
    user_id: int

    @contextmanager
    def open(self) -> Iterator[ProgressService]:
        """Yield a service bound to the caller; core :class:`ProgressError` becomes 409."""
        store = open_progress_store(self.state.settings)
        try:
            yield ProgressService(
                store, self.index.courses, user_id=self.user_id, clock=self.state.clock
            )
        except ProgressError as exc:
            raise HTTPException(409, str(exc)) from None
        finally:
            store.close()


def open_progress_store(settings: Settings) -> ProgressStore:
    """``RC_DATABASE_URL`` if set (PostgreSQL), else SQLite in the data dir."""
    return open_store(settings.data_dir, settings.database_url or "")


def get_progress(
    state: State,
    index: Annotated[ContentIndex, Depends(get_index)],
    user_id: Annotated[int, Depends(current_user_id)],
) -> ProgressFactory:
    return ProgressFactory(state, index, user_id)


Index = Annotated[ContentIndex, Depends(get_index)]
Progress = Annotated[ProgressFactory, Depends(get_progress)]

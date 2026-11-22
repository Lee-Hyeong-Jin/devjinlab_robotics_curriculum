"""``/api/v1/admin``: the operator console (admin role only).

An overview of the platform, user search and per-user detail with the actions an operator
takes on an account, and the audit log with filters and a CSV export. Reading is audited as
well as writing: who looked at whose account is part of the trail.
"""

from __future__ import annotations

import csv
import io
from collections.abc import Iterable
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from robotics_curriculum import __version__
from robotics_curriculum.api.auth_schemas import (
    AdminOverview,
    AdminUser,
    AdminUserOverview,
    AdminUserUpdate,
    ApiToken,
    AuditEntry,
    AuditPage,
    AuthSession,
    DayCount,
    Identity,
    LearnerSummary,
    LoginCounts,
    OverviewLearning,
    OverviewSecurity,
    OverviewSystem,
    OverviewUsers,
    RevokedCount,
    UserPage,
)
from robotics_curriculum.api.deps import (
    AdminPrincipal,
    Auth,
    Ctx,
    State,
    open_progress_store,
    require_admin,
)
from robotics_curriculum.api.problems import problem_responses
from robotics_curriculum.auth import models
from robotics_curriculum.auth.models import Role, UserStatus
from robotics_curriculum.auth.service import AuthService
from robotics_curriculum.learn.platform import learner_summary, platform_activity

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
    responses=problem_responses(401, 403, 404, 409, 422),
)

Limit = Annotated[int, Query(ge=1, le=200)]
SearchText = Annotated[
    str | None,
    Query(max_length=200, description="Matches part of the email address or the display name."),
]
ActionPrefix = Annotated[
    str | None,
    Query(
        alias="action",
        max_length=100,
        description="Start of the action name: `user.` finds every change to a user.",
    ),
]

AUDIT_EXPORT_LIMIT = 10_000
"""Rows in one CSV export. An export is a snapshot for a spreadsheet, not a backup."""


def _cursor(value: str | None) -> int | None:
    if value is None:
        return None
    if not value.isdigit():
        raise HTTPException(422, "invalid cursor")
    return int(value)


def _aware(name: str, value: datetime | None) -> datetime | None:
    """A filter time must carry its offset: a naive one would silently mean server time."""
    if value is not None and value.tzinfo is None:
        raise HTTPException(422, f"'{name}' must include a UTC offset, e.g. 2026-11-22T00:00:00Z")
    return value


def _audit_entries(auth: AuthService, entries: Iterable[models.AuditEntry]) -> list[AuditEntry]:
    """Audit rows as API objects, with the actor's address looked up in one query."""
    rows = list(entries)
    emails = auth.user_emails({e.actor_user_id for e in rows if e.actor_user_id is not None})
    return [
        AuditEntry(
            **e.model_dump(),
            actor_email=emails.get(e.actor_user_id) if e.actor_user_id is not None else None,
        )
        for e in rows
    ]


# -- overview ------------------------------------------------------------------------------


@router.get("/overview", response_model=AdminOverview)
def overview(principal: AdminPrincipal, auth: Auth, ctx: Ctx, state: State) -> AdminOverview:
    """Accounts, sign-ins, sessions, learning activity and system settings on one screen.

    A summary read from the database on each request; the time series an alert needs live in
    ``/metrics``.
    """
    accounts = auth.accounts_overview()
    now = state.clock()
    store = open_progress_store(state.settings)
    try:
        activity = platform_activity(
            store.list_lessons(user_id=None), store.list_sessions(user_id=None), now
        )
    finally:
        store.close()
    auth.record(ctx, "admin.overview.viewed", principal.user.id)
    return AdminOverview(
        generated_at=now,
        users=OverviewUsers(
            total=accounts.total,
            by_role=accounts.by_role,
            by_status=accounts.by_status,
            unverified=accounts.unverified,
            stale_unverified=accounts.stale_unverified,
            new_7d=accounts.new_7d,
            new_30d=accounts.new_30d,
            signups_daily=[DayCount(day=d, count=n) for d, n in accounts.signups_daily],
        ),
        security=OverviewSecurity(
            active_sessions=accounts.active_sessions,
            logins_24h=LoginCounts(succeeded=accounts.logins_24h[0], failed=accounts.logins_24h[1]),
            logins_7d=LoginCounts(succeeded=accounts.logins_7d[0], failed=accounts.logins_7d[1]),
        ),
        learning=OverviewLearning(
            window_days=activity.window_days,
            active_learners=activity.active_learners,
            lessons_completed=activity.lessons_completed,
            study_minutes=activity.study_seconds // 60,
            lessons_completed_total=activity.lessons_completed_total,
            learners_total=activity.learners_total,
        ),
        system=OverviewSystem(
            version=__version__,
            lesson_count=state.index.lesson_count if state.index else None,
            course_count=len(state.index.courses) if state.index else None,
            mail_enabled=accounts.mail_enabled,
            public_content=state.settings.public_content,
            signup_open=auth.config.allow_signup,
            auth_providers=sorted(state.oidc),
            audit_retention_days=accounts.audit_retention_days,
        ),
    )


# -- users ---------------------------------------------------------------------------------


@router.get("/users", response_model=UserPage)
def list_users(
    principal: AdminPrincipal,
    auth: Auth,
    ctx: Ctx,
    limit: Limit = 50,
    cursor: str | None = None,
    q: SearchText = None,
    role: Role | None = None,
    status: Annotated[UserStatus | None, Query(alias="status")] = None,
    verified: Annotated[
        bool | None, Query(description="Whether the email address is verified.")
    ] = None,
) -> UserPage:
    """Users by id, cursor-paginated, optionally narrowed by search text and filters."""
    users = auth.list_users(
        limit, _cursor(cursor) or 0, q=q, role=role, status=status, verified=verified
    )
    total = auth.count_users(q=q, role=role, status=status, verified=verified)
    auth.record(
        ctx,
        "admin.users.viewed",
        principal.user.id,
        # Whether a search was made, never the text: it is usually somebody's address.
        detail={"count": len(users), "searched": bool(q)},
    )
    nxt = str(users[-1].id) if len(users) == limit else None
    return UserPage(
        items=[AdminUser.of(u, auth.verification_state(u)) for u in users],
        next_cursor=nxt,
        total=total,
    )


@router.get("/users/{user_id}", response_model=AdminUser)
def get_user(user_id: int, principal: AdminPrincipal, auth: Auth, ctx: Ctx) -> AdminUser:
    user = auth.get_user(user_id)
    auth.record(
        ctx, "admin.user.viewed", principal.user.id, target_type="user", target_id=str(user_id)
    )
    return AdminUser.of(user, auth.verification_state(user))


@router.get("/users/{user_id}/overview", response_model=AdminUserOverview)
def user_overview(
    user_id: int, principal: AdminPrincipal, auth: Auth, ctx: Ctx, state: State
) -> AdminUserOverview:
    """One account with its sessions, tokens, external logins, learning and recent audit trail.

    Tokens are listed by name and prefix only; the secret and its hash never leave the server.
    """
    detail = auth.user_detail(user_id)
    now = state.clock()
    store = open_progress_store(state.settings)
    try:
        learning = learner_summary(
            store.list_lessons(user_id=user_id), store.list_sessions(user_id=user_id), now
        )
    finally:
        store.close()
    auth.record(
        ctx, "admin.user.viewed", principal.user.id, target_type="user", target_id=str(user_id)
    )
    return AdminUserOverview(
        user=AdminUser.of(detail.user, auth.verification_state(detail.user)),
        sessions=[AuthSession.of(s, None) for s in detail.sessions],
        tokens=[ApiToken.of(t) for t in detail.tokens if t.revoked_at is None],
        identities=[Identity.of(i) for i in detail.identities],
        failed_logins_24h=detail.failed_logins_24h,
        learning=LearnerSummary(
            lessons_done=learning.lessons_done,
            lessons_in_progress=learning.lessons_in_progress,
            study_minutes=learning.study_seconds // 60,
            last_activity_at=learning.last_activity_at,
        ),
        recent_audit=_audit_entries(auth, detail.recent_audit),
    )


@router.patch("/users/{user_id}", response_model=AdminUser)
def update_user(
    user_id: int, body: AdminUserUpdate, principal: AdminPrincipal, auth: Auth, ctx: Ctx
) -> AdminUser:
    """Change role or status. The last admin cannot be demoted or disabled, and admins
    cannot remove their own admin access. Disabling ends the user's sessions and tokens."""
    user = auth.admin_update_user(principal.user, user_id, ctx, role=body.role, status=body.status)
    return AdminUser.of(user, auth.verification_state(user))


@router.delete("/users/{user_id}/sessions", status_code=status.HTTP_204_NO_CONTENT)
def revoke_user_sessions(user_id: int, principal: AdminPrincipal, auth: Auth, ctx: Ctx) -> None:
    """Force-logout: end every browser session of the user."""
    auth.admin_revoke_sessions(principal.user, user_id, ctx)


@router.delete("/users/{user_id}/tokens", response_model=RevokedCount)
def revoke_user_tokens(
    user_id: int, principal: AdminPrincipal, auth: Auth, ctx: Ctx
) -> RevokedCount:
    """Revoke every personal access token of the user."""
    return RevokedCount(revoked=auth.admin_revoke_tokens(principal.user, user_id, ctx))


@router.post(
    "/users/{user_id}/password-reset",
    status_code=status.HTTP_202_ACCEPTED,
    responses=problem_responses(503),
)
def send_password_reset(user_id: int, principal: AdminPrincipal, auth: Auth, ctx: Ctx) -> Response:
    """Mail the user a password-reset link. The operator never sees the link.

    503 when the server has no mail configuration, 409 when the account is not active.
    """
    auth.admin_send_password_reset(principal.user, user_id, ctx)
    return Response(status_code=status.HTTP_202_ACCEPTED)


# -- audit ---------------------------------------------------------------------------------


@router.get("/audit", response_model=AuditPage)
def list_audit(
    principal: AdminPrincipal,
    auth: Auth,
    ctx: Ctx,
    limit: Limit = 50,
    cursor: str | None = None,
    actor_user_id: int | None = None,
    action: ActionPrefix = None,
    target_type: Annotated[str | None, Query(max_length=50)] = None,
    target_id: Annotated[str | None, Query(max_length=100)] = None,
    since: Annotated[datetime | None, Query(description="Inclusive, with a UTC offset.")] = None,
    until: Annotated[datetime | None, Query(description="Exclusive, with a UTC offset.")] = None,
) -> AuditPage:
    """Audit log, newest first (reading it is itself audited)."""
    entries = auth.list_audit(
        limit,
        _cursor(cursor),
        actor_user_id,
        action_prefix=action,
        target_type=target_type,
        target_id=target_id,
        since=_aware("since", since),
        until=_aware("until", until),
    )
    auth.record(ctx, "admin.audit.viewed", principal.user.id)
    nxt = str(entries[-1].id) if len(entries) == limit else None
    return AuditPage(items=_audit_entries(auth, entries), next_cursor=nxt)


def csv_cell(value: object) -> str:
    """A CSV cell that a spreadsheet will not run as a formula.

    Audit rows carry text an outsider chose (a user agent, an email address). A cell that
    starts with ``=``, ``+``, ``-``, ``@``, a tab or a carriage return is evaluated by Excel
    and its relatives, so such a cell gets a leading apostrophe (OWASP: CSV injection).
    """
    text = "" if value is None else str(value)
    return f"'{text}" if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


@router.get(
    "/audit/export",
    response_class=Response,
    responses={200: {"content": {"text/csv": {}}, "description": "The matching rows as CSV."}},
)
def export_audit(
    principal: AdminPrincipal,
    auth: Auth,
    ctx: Ctx,
    actor_user_id: int | None = None,
    action: ActionPrefix = None,
    target_type: Annotated[str | None, Query(max_length=50)] = None,
    target_id: Annotated[str | None, Query(max_length=100)] = None,
    since: Annotated[datetime | None, Query(description="Inclusive, with a UTC offset.")] = None,
    until: Annotated[datetime | None, Query(description="Exclusive, with a UTC offset.")] = None,
) -> Response:
    """The audit log as CSV with the same filters, newest first, at most 10,000 rows.

    The ``X-Truncated`` header is ``true`` when more rows matched than were exported.
    """
    entries = auth.list_audit(
        AUDIT_EXPORT_LIMIT + 1,
        None,
        actor_user_id,
        action_prefix=action,
        target_type=target_type,
        target_id=target_id,
        since=_aware("since", since),
        until=_aware("until", until),
    )
    truncated = len(entries) > AUDIT_EXPORT_LIMIT
    rows = _audit_entries(auth, entries[:AUDIT_EXPORT_LIMIT])
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\r\n")
    writer.writerow(
        [
            "id",
            "at",
            "action",
            "actor_user_id",
            "actor_email",
            "actor_ip",
            "target_type",
            "target_id",
            "request_id",
            "detail",
        ]
    )
    for row in rows:
        detail = "; ".join(f"{key}={value}" for key, value in sorted(row.detail.items()))
        writer.writerow(
            [
                row.id,
                row.at.isoformat(),
                csv_cell(row.action),
                row.actor_user_id if row.actor_user_id is not None else "",
                csv_cell(row.actor_email),
                csv_cell(row.actor_ip),
                csv_cell(row.target_type),
                csv_cell(row.target_id),
                csv_cell(row.request_id),
                csv_cell(detail),
            ]
        )
    auth.record(
        ctx,
        "admin.audit.exported",
        principal.user.id,
        detail={"rows": len(rows), "truncated": truncated},
    )
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="audit-log.csv"',
            "Cache-Control": "no-store",
            "X-Truncated": "true" if truncated else "false",
        },
    )

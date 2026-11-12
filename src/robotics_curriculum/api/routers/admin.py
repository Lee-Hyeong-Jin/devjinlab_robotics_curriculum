"""``/api/v1/admin``: user management and the audit log (admin role only)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from robotics_curriculum.api.auth_schemas import (
    AdminUser,
    AdminUserUpdate,
    AuditEntry,
    AuditPage,
    UserPage,
)
from robotics_curriculum.api.deps import AdminPrincipal, Auth, Ctx, require_admin
from robotics_curriculum.api.problems import problem_responses

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
    responses=problem_responses(401, 403, 404, 409, 422),
)

Limit = Annotated[int, Query(ge=1, le=200)]


def _cursor(value: str | None) -> int | None:
    if value is None:
        return None
    if not value.isdigit():
        raise HTTPException(422, "invalid cursor")
    return int(value)


@router.get("/users", response_model=UserPage)
def list_users(
    principal: AdminPrincipal, auth: Auth, ctx: Ctx, limit: Limit = 50, cursor: str | None = None
) -> UserPage:
    """Users by id, cursor-paginated."""
    users = auth.list_users(limit, _cursor(cursor) or 0)
    auth.record(ctx, "admin.users.viewed", principal.user.id, detail={"count": len(users)})
    nxt = str(users[-1].id) if len(users) == limit else None
    return UserPage(
        items=[AdminUser.of(u, auth.verification_state(u)) for u in users], next_cursor=nxt
    )


@router.get("/users/{user_id}", response_model=AdminUser)
def get_user(user_id: int, principal: AdminPrincipal, auth: Auth, ctx: Ctx) -> AdminUser:
    user = auth.get_user(user_id)
    auth.record(
        ctx, "admin.user.viewed", principal.user.id, target_type="user", target_id=str(user_id)
    )
    return AdminUser.of(user, auth.verification_state(user))


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


@router.get("/audit", response_model=AuditPage)
def list_audit(
    principal: AdminPrincipal,
    auth: Auth,
    ctx: Ctx,
    limit: Limit = 50,
    cursor: str | None = None,
    actor_user_id: int | None = None,
) -> AuditPage:
    """Audit log, newest first (reading it is itself audited)."""
    entries = auth.list_audit(limit, _cursor(cursor), actor_user_id)
    auth.record(ctx, "admin.audit.viewed", principal.user.id)
    nxt = str(entries[-1].id) if len(entries) == limit else None
    return AuditPage(
        items=[AuditEntry.model_validate(e.model_dump()) for e in entries], next_cursor=nxt
    )

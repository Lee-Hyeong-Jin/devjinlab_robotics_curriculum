"""``/api/v1/me``: the caller's profile, password, sessions, tokens, data export, deletion.

Every query is bound to the authenticated user's id; no path or body carries a user id.
"""

from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, Response, status

from robotics_curriculum.api.auth_schemas import (
    ApiToken,
    ApiTokenCreate,
    ApiTokenCreated,
    AuthSession,
    DeleteAccount,
    Identity,
    PasswordChange,
    User,
    UserUpdate,
)
from robotics_curriculum.api.deps import (
    CSRF_COOKIE,
    SESSION_COOKIE,
    Auth,
    Ctx,
    CurrentPrincipal,
    Progress,
    SessionPrincipal,
    State,
    get_principal,
)
from robotics_curriculum.api.problems import problem_responses
from robotics_curriculum.progress import ProgressExport

router = APIRouter(
    prefix="/api/v1/me",
    tags=["me"],
    dependencies=[Depends(get_principal)],
    responses=problem_responses(401, 403, 404, 422, 503),
)


@router.get("", response_model=User)
def get_me(principal: CurrentPrincipal) -> User:
    """The signed-in user."""
    return User.of(principal.user)


@router.patch("", response_model=User)
def update_me(body: UserUpdate, principal: SessionPrincipal, auth: Auth, ctx: Ctx) -> User:
    """Change display name, locale or timezone."""
    fields = body.model_dump(exclude_unset=True)
    return User.of(auth.update_profile(principal.user, ctx, **fields))


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    body: PasswordChange, principal: SessionPrincipal, auth: Auth, ctx: Ctx
) -> None:
    """Change the password; every other session of the account is ended."""
    auth.change_password(principal, body.current_password, body.new_password, ctx)


@router.get("/sessions", response_model=list[AuthSession])
def list_sessions(principal: SessionPrincipal, auth: Auth) -> list[AuthSession]:
    """Active browser sessions (devices) of the account."""
    current = principal.session.id if principal.session else None
    return [AuthSession.of(s, current) for s in auth.list_sessions(principal.user)]


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_session(session_id: int, principal: SessionPrincipal, auth: Auth, ctx: Ctx) -> None:
    """End one of the account's sessions (e.g. a lost device)."""
    auth.revoke_session(principal.user, session_id, ctx)


@router.get("/tokens", response_model=list[ApiToken])
def list_tokens(principal: SessionPrincipal, auth: Auth) -> list[ApiToken]:
    """Active personal access tokens (secrets are never shown again)."""
    return [ApiToken.of(t) for t in auth.list_tokens(principal.user)]


@router.post("/tokens", response_model=ApiTokenCreated, status_code=status.HTTP_201_CREATED)
def create_token(
    body: ApiTokenCreate, principal: SessionPrincipal, auth: Auth, ctx: Ctx
) -> ApiTokenCreated:
    """Issue a personal access token for programs (``Authorization: Bearer <token>``)."""
    expires = timedelta(days=body.expires_in_days) if body.expires_in_days else None
    secret, record = auth.create_token(
        principal.user, body.name, body.scopes, ctx, expires_in=expires
    )
    return ApiTokenCreated(**ApiToken.of(record).model_dump(), token=secret)


@router.delete("/tokens/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_token(token_id: int, principal: SessionPrincipal, auth: Auth, ctx: Ctx) -> None:
    """Revoke a personal access token."""
    auth.revoke_token(principal.user, token_id, ctx)


@router.get("/export", response_model=ProgressExport)
def export(
    principal: CurrentPrincipal, progress: Progress, state: State, ctx: Ctx
) -> ProgressExport:
    """The caller's progress and sessions: the JSON format of ``rc progress export``, so it
    loads into local mode with ``rc progress import``."""
    with progress.open() as service:
        data = service.export(user_id=principal.user.id)
    if state.auth is not None:
        state.auth.record_export(principal.user, ctx)
    return data


@router.delete("", status_code=status.HTTP_204_NO_CONTENT, responses=problem_responses(409))
def delete_me(
    principal: SessionPrincipal,
    auth: Auth,
    ctx: Ctx,
    response: Response,
    body: DeleteAccount | None = None,
) -> None:
    """Delete the account: learning data is removed now, the user row is anonymized."""
    auth.delete_account(principal, body.password if body else None, ctx)
    response.delete_cookie(SESSION_COOKIE, path="/")
    response.delete_cookie(CSRF_COOKIE, path="/")


@router.get("/identities", response_model=list[Identity])
def list_identities(principal: SessionPrincipal, auth: Auth) -> list[Identity]:
    """External logins (OIDC providers) linked to the account."""
    return [Identity.of(i) for i in auth.list_identities(principal.user)]


@router.delete(
    "/identities/{identity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=problem_responses(409),
)
def unlink_identity(identity_id: int, principal: SessionPrincipal, auth: Auth, ctx: Ctx) -> None:
    """Unlink an external login (refused when it is the account's only way to sign in)."""
    auth.unlink_identity(principal.user, identity_id, ctx)

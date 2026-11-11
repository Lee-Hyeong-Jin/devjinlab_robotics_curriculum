"""``/api/v1/auth``: sign-up, login/logout, email verification, password reset, OIDC slots.

Login sets two cookies: ``sid`` (HttpOnly, the session) and ``csrf_token`` (readable by the
page, echoed back as ``X-CSRF-Token``). A new session id is issued on every login, so a
session id planted before login is never promoted (no session fixation).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response, status

from robotics_curriculum.api.auth_schemas import (
    ForgotRequest,
    LoginRequest,
    LoginResult,
    ResetRequest,
    SignupRequest,
    TokenRequest,
    User,
)
from robotics_curriculum.api.deps import (
    CSRF_COOKIE,
    SESSION_COOKIE,
    Auth,
    Ctx,
    CurrentPrincipal,
    State,
)
from robotics_curriculum.api.problems import problem_responses

router = APIRouter(prefix="/api/v1/auth", tags=["auth"], responses=problem_responses(404, 422, 429))


@router.post(
    "/signup",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    responses=problem_responses(403, 409),
)
def signup(body: SignupRequest, auth: Auth, ctx: Ctx) -> User:
    """Create a local account (role learner) and mail an email-verification link."""
    user = auth.signup(body.email, body.password, ctx, display_name=body.display_name)
    return User.of(user)


@router.post("/login", response_model=LoginResult, responses=problem_responses(401))
def login(
    body: LoginRequest, response: Response, auth: Auth, ctx: Ctx, state: State
) -> LoginResult:
    """Start a browser session. Five failures in 15 minutes lock the account temporarily."""
    result = auth.login(body.email, body.password, ctx)
    secure = state.settings.cookie_secure
    max_age = int(auth.config.session_idle.total_seconds())
    response.set_cookie(
        SESSION_COOKIE,
        result.session_token,
        max_age=max_age,
        path="/",
        secure=secure,
        httponly=True,
        samesite="lax",
    )
    response.set_cookie(
        CSRF_COOKIE,
        result.csrf_token,
        max_age=max_age,
        path="/",
        secure=secure,
        httponly=False,
        samesite="lax",
    )
    return LoginResult(user=User.of(result.user), csrf_token=result.csrf_token)


@router.post(
    "/logout", status_code=status.HTTP_204_NO_CONTENT, responses=problem_responses(401, 403)
)
def logout(principal: CurrentPrincipal, auth: Auth, ctx: Ctx, response: Response) -> None:
    """End this browser session (needs the CSRF header)."""
    auth.logout(principal, ctx)
    response.delete_cookie(SESSION_COOKIE, path="/")
    response.delete_cookie(CSRF_COOKIE, path="/")


@router.post("/verify-email", status_code=status.HTTP_204_NO_CONTENT)
def verify_email(body: TokenRequest, auth: Auth, ctx: Ctx) -> None:
    """Confirm the email address with the mailed one-time token (valid 24 hours)."""
    auth.verify_email(body.token, ctx)


@router.post(
    "/password/forgot", status_code=status.HTTP_202_ACCEPTED, responses=problem_responses(503)
)
def forgot_password(body: ForgotRequest, auth: Auth, ctx: Ctx) -> None:
    """Mail a reset link (valid 30 minutes, single use) if the account exists.

    The answer is the same whether or not the email is registered.
    """
    auth.forgot_password(body.email, ctx)


@router.post("/password/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(body: ResetRequest, auth: Auth, ctx: Ctx) -> None:
    """Set a new password with a reset token; every session of the account is ended."""
    auth.reset_password(body.token, body.password, ctx)


@router.get(
    "/oidc/{provider}/start",
    response_model=None,
    responses=problem_responses(501),
)
def oidc_start(provider: str, auth: Auth) -> None:
    """OIDC login (Authorization Code + PKCE) — planned for the second P2-2 increment."""
    raise HTTPException(501, f"OIDC login ('{provider}') is not available yet")


@router.get(
    "/oidc/{provider}/callback",
    response_model=None,
    responses=problem_responses(501),
)
def oidc_callback(provider: str, auth: Auth) -> None:
    """OIDC callback — planned for the second P2-2 increment."""
    raise HTTPException(501, f"OIDC login ('{provider}') is not available yet")

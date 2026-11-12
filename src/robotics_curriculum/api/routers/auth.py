"""``/api/v1/auth``: sign-up, login/logout, email verification, password reset, OIDC login.

Login sets two cookies: ``sid`` (HttpOnly, the session) and ``csrf_token`` (readable by the
page, echoed back as ``X-CSRF-Token``). A new session id is issued on every login, so a
session id planted before login is never promoted (no session fixation).

OIDC: ``/oidc/{provider}/start`` redirects to the provider with ``state``, ``nonce`` and a
PKCE S256 challenge, keeping them in an HMAC-signed, HttpOnly ``oidc_flow`` cookie (10 min).
``/oidc/{provider}/callback`` checks the state, exchanges the code with the verifier,
verifies the id_token, signs in, and redirects to ``RC_PUBLIC_URL`` + ``return_to``.
"""

from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse

from robotics_curriculum.api.auth_schemas import (
    AuthProvider,
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
    AppState,
    Auth,
    Ctx,
    CurrentPrincipal,
    SessionPrincipal,
    State,
    optional_principal,
)
from robotics_curriculum.api.problems import problem_responses
from robotics_curriculum.auth.oidc import (
    FLOW_TTL_SECONDS,
    Flow,
    OidcClient,
    OidcError,
    open_flow,
    pkce_pair,
    seal_flow,
)
from robotics_curriculum.auth.service import AuthService, Principal
from robotics_curriculum.auth.service import LoginResult as SessionResult

router = APIRouter(prefix="/api/v1/auth", tags=["auth"], responses=problem_responses(404, 422, 429))

OIDC_COOKIE = "oidc_flow"
OIDC_COOKIE_PATH = "/api/v1/auth/oidc"


def _set_session_cookies(
    response: Response, result: SessionResult, state: AppState, auth: AuthService
) -> None:
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


@router.post(
    "/signup",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    responses=problem_responses(403, 409),
)
def signup(body: SignupRequest, auth: Auth, ctx: Ctx) -> User:
    """Create a local account (role learner) and mail an email-verification link."""
    user = auth.signup(body.email, body.password, ctx, display_name=body.display_name)
    return User.of(user, auth.verification_state(user))


@router.post("/login", response_model=LoginResult, responses=problem_responses(401))
def login(
    body: LoginRequest, response: Response, auth: Auth, ctx: Ctx, state: State
) -> LoginResult:
    """Start a browser session. Five failures in 15 minutes lock the account temporarily."""
    result = auth.login(body.email, body.password, ctx)
    _set_session_cookies(response, result, state, auth)
    return LoginResult(
        user=User.of(result.user, auth.verification_state(result.user)),
        csrf_token=result.csrf_token,
    )


@router.post(
    "/logout", status_code=status.HTTP_204_NO_CONTENT, responses=problem_responses(401, 403)
)
def logout(principal: CurrentPrincipal, auth: Auth, ctx: Ctx, response: Response) -> None:
    """End this browser session (needs the CSRF header)."""
    auth.logout(principal, ctx)
    response.delete_cookie(SESSION_COOKIE, path="/")
    response.delete_cookie(CSRF_COOKIE, path="/")


@router.post(
    "/resend-verification",
    status_code=status.HTTP_202_ACCEPTED,
    responses=problem_responses(401, 403, 503),
)
def resend_verification(principal: SessionPrincipal, auth: Auth, ctx: Ctx) -> None:
    """Send the verification link again to the signed-in account's own address.

    Needs a session, so there is nothing to enumerate and no address to type. 503 when the
    server has no SMTP configuration — the client reads `email_verification` first and does
    not offer this at all in that case. Already-verified accounts get 202 and no mail.
    """
    if not auth.mail_enabled:
        raise HTTPException(503, "mail is not configured on this server")
    auth.resend_verification(principal.user, ctx)


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


# -- OIDC ---------------------------------------------------------------------------------


def _safe_return_to(value: str | None) -> str:
    """Only same-site relative paths (no open redirect)."""
    if not value or not value.startswith("/") or value.startswith("//") or "\\" in value:
        return "/"
    return value


def _client(state: AppState, provider: str) -> OidcClient:
    client = state.oidc.get(provider)
    if client is None:
        raise HTTPException(404, f"unknown OIDC provider '{provider}'")
    return client


def _oidc_url(request: Request, auth: AuthService, provider: str, leg: str) -> str:
    """Absolute URL of an OIDC leg (``start`` or ``callback``).

    ``RC_API_BASE_URL`` wins when set: behind a proxy the request's own host is the internal
    one, and the provider has to be given — and later recognise — the public redirect URI.
    """
    base = auth.config.api_base_url
    if base:
        return f"{base.rstrip('/')}/api/v1/auth/oidc/{provider}/{leg}"
    return str(request.url_for(f"oidc_{leg}", provider=provider))


def _redirect_uri(request: Request, auth: AuthService, provider: str) -> str:
    return _oidc_url(request, auth, provider, "callback")


@router.get("/providers", response_model=list[AuthProvider])
def providers(request: Request, state: State, auth: Auth) -> list[AuthProvider]:
    """External logins configured through ``RC_OIDC_PROVIDERS``, for the sign-in buttons.

    Unauthenticated on purpose — the login screen is reached without a session. Secrets are
    never included. Empty in local mode, or when no provider is configured, which the
    frontend reads as "show no provider buttons".
    """
    return [
        AuthProvider(
            id=pid,
            name=client.provider.name or pid.replace("-", " ").replace("_", " ").title(),
            type=client.provider.type,
            start_url=_oidc_url(request, auth, pid, "start"),
        )
        for pid, client in sorted(state.oidc.items())
    ]


@router.get(
    "/oidc/{provider}/start",
    status_code=status.HTTP_302_FOUND,
    response_class=RedirectResponse,
    responses={
        302: {"description": "Redirect to the provider's login page"},
        **problem_responses(502),
    },
)
def oidc_start(
    provider: str,
    request: Request,
    state: State,
    auth: Auth,
    return_to: Annotated[str | None, Query(description="App path to land on afterwards.")] = None,
) -> RedirectResponse:
    """Start an OIDC login (Authorization Code + PKCE). With an active browser session the
    provider identity is linked to that account instead."""
    client = _client(state, provider)
    verifier, challenge = pkce_pair()
    flow = Flow(
        provider=provider,
        state=secrets.token_urlsafe(24),
        nonce=secrets.token_urlsafe(24),
        verifier=verifier,
        return_to=_safe_return_to(return_to),
        issued_at=int(state.clock().timestamp()),
    )
    try:
        url = client.authorization_url(
            state=flow.state,
            nonce=flow.nonce,
            challenge=challenge,
            redirect_uri=_redirect_uri(request, auth, provider),
        )
    except OidcError as exc:
        raise HTTPException(502, str(exc)) from None
    response = RedirectResponse(url, status_code=302)
    response.set_cookie(
        OIDC_COOKIE,
        seal_flow(flow, state.flow_key),
        max_age=FLOW_TTL_SECONDS,
        path=OIDC_COOKIE_PATH,
        secure=state.settings.cookie_secure,
        httponly=True,
        samesite="lax",
    )
    return response


@router.get(
    "/oidc/{provider}/callback",
    status_code=status.HTTP_302_FOUND,
    response_class=RedirectResponse,
    responses={
        302: {"description": "Signed in; redirect into the app"},
        **problem_responses(400, 401, 403, 409),
    },
)
def oidc_callback(
    provider: str,
    request: Request,
    state: State,
    auth: Auth,
    ctx: Ctx,
    current: Annotated[Principal | None, Depends(optional_principal)],
    code: str | None = None,
    state_param: Annotated[str | None, Query(alias="state")] = None,
    error: str | None = None,
) -> RedirectResponse:
    """Finish the OIDC login: check state, exchange the code with the PKCE verifier, verify
    the id_token (signature, issuer, audience, expiry, nonce), then sign in or link."""
    client = _client(state, provider)
    sealed = request.cookies.get(OIDC_COOKIE)
    flow = open_flow(sealed, state.flow_key, now=state.clock().timestamp()) if sealed else None
    if flow is None or flow.provider != provider:
        raise HTTPException(400, "login expired or was started elsewhere; try again")
    if not state_param or not secrets.compare_digest(state_param, flow.state):
        raise HTTPException(400, "state mismatch")
    if error or not code:
        raise HTTPException(400, f"the provider refused the login: {error or 'no code'}")
    try:
        claims = client.login(
            code,
            verifier=flow.verifier,
            redirect_uri=_redirect_uri(request, auth, provider),
            nonce=flow.nonce,
        )
    except OidcError as exc:
        raise HTTPException(400, f"login failed: {exc}") from None
    result = auth.oidc_login(
        provider, claims, ctx, current=current, mapped_role=client.mapped_role(claims)
    )
    response = RedirectResponse(
        auth.config.public_url.rstrip("/") + flow.return_to, status_code=302
    )
    _set_session_cookies(response, result, state, auth)
    response.delete_cookie(OIDC_COOKIE, path=OIDC_COOKIE_PATH)
    return response

"""GitHub OAuth2 adapter and IdP role mapping (follow-ups of AC-AUTH.3)."""

# Fixtures are imported from test_oidc and requested by name.
# ruff: noqa: F401, F811

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.settings import Settings
from robotics_curriculum.auth.oidc import (
    Claims,
    OidcClient,
    OidcError,
    OidcProvider,
    parse_providers,
)
from robotics_curriculum.auth.service import AuthConfig
from test_oidc import (
    CLIENT_ID,
    CURRICULUM,
    ISSUER,
    PUBLIC,
    Clock,
    FakeIdP,
    clock,
    fast_argon2,
    idp,
    oidc_login,
)

GITHUB = parse_providers(
    {"RC_OIDC_PROVIDERS": json.dumps([{"id": "github", "type": "github", "client_id": "gh"}])}
)["github"]


class FakeGitHub:
    def __init__(self, emails: list[dict[str, Any]], user: dict[str, Any] | None = None) -> None:
        self.emails = emails
        self.user = user or {"id": 4242, "login": "octo", "name": None}
        self.verifiers: list[str] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/login/oauth/access_token":
            form = {k: v[0] for k, v in parse_qs(request.content.decode()).items()}
            self.verifiers.append(form["code_verifier"])
            assert request.headers["accept"] == "application/json"
            if form["code"] != "good":
                return httpx.Response(200, json={"error": "bad_verification_code"})
            return httpx.Response(200, json={"access_token": "gho_x", "token_type": "bearer"})
        assert request.headers["authorization"] == "Bearer gho_x"
        if path == "/user":
            return httpx.Response(200, json=self.user)
        if path == "/user/emails":
            return httpx.Response(200, json=self.emails)
        return httpx.Response(404)


def _gh_app(tmp_path: Path, gh: FakeGitHub, clock: Clock) -> FastAPI:
    settings = Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path, auth_mode="server")
    return create_app(
        settings,
        clock=clock,
        mailer=None,
        auth_config=AuthConfig(public_url=PUBLIC),
        oidc_providers={"github": GITHUB},
        oidc_http=httpx.Client(transport=httpx.MockTransport(gh.handler)),
        auth_secret="test-flow-key",
    )


def test_github_defaults() -> None:
    assert GITHUB.type == "github"
    assert GITHUB.authorization_endpoint == "https://github.com/login/oauth/authorize"
    assert GITHUB.scopes == "read:user user:email"


def test_github_login_end_to_end(tmp_path: Path, clock: Clock) -> None:
    gh = FakeGitHub(
        [
            {"email": "Other@Example.org", "verified": True, "primary": False},
            {"email": "Octo@Example.org", "verified": True, "primary": True},
            {"email": "spam@example.org", "verified": False, "primary": False},
        ]
    )
    c = TestClient(
        _gh_app(tmp_path, gh, clock), base_url="https://testserver", follow_redirects=False
    )
    start = c.get("/api/v1/auth/oidc/github/start", params={"return_to": "/me"})
    assert start.status_code == 302
    query = {k: v[0] for k, v in parse_qs(urlparse(start.headers["location"]).query).items()}
    assert start.headers["location"].startswith("https://github.com/login/oauth/authorize?")
    r = c.get("/api/v1/auth/oidc/github/callback", params={"code": "good", "state": query["state"]})
    assert r.status_code == 302, r.text
    me = c.get("/api/v1/me").json()
    assert me["email"] == "octo@example.org" and me["display_name"] == "octo"
    assert gh.verifiers and gh.verifiers[0]


def test_github_bad_code_and_no_verified_email(tmp_path: Path, clock: Clock) -> None:
    gh = FakeGitHub([{"email": "x@example.org", "verified": False, "primary": True}])
    c = TestClient(
        _gh_app(tmp_path, gh, clock), base_url="https://testserver", follow_redirects=False
    )
    for code, expected in (("bad", 400), ("good", 403)):
        start = c.get("/api/v1/auth/oidc/github/start")
        state = parse_qs(urlparse(start.headers["location"]).query)["state"][0]
        r = c.get("/api/v1/auth/oidc/github/callback", params={"code": code, "state": state})
        assert r.status_code == expected, (code, r.text)


def test_github_claims_errors() -> None:
    def client(handler: Any) -> OidcClient:
        return OidcClient(GITHUB, httpx.Client(transport=httpx.MockTransport(handler)))

    with pytest.raises(OidcError, match="access_token"):
        client(lambda r: httpx.Response(200))._github_claims({})
    with pytest.raises(OidcError, match="no id"):
        client(
            lambda r: httpx.Response(200, json=[] if "emails" in r.url.path else {})
        )._github_claims({"access_token": "t"})
    with pytest.raises(OidcError, match="emails"):
        client(
            lambda r: (
                httpx.Response(500)
                if "emails" in r.url.path
                else httpx.Response(200, json={"id": 1})
            )
        )._github_claims({"access_token": "t"})


# -- role mapping ------------------------------------------------------------------------------

MAPPED = OidcProvider(
    id="univ",
    issuer=ISSUER,
    client_id=CLIENT_ID,
    client_secret="s",
    role_claim="groups",
    role_map={"rc-authors": "author", "rc-admins": "admin"},
)


def _mapped_app(tmp_path: Path, idp: FakeIdP, clock: Clock) -> FastAPI:
    settings = Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path, auth_mode="server")
    return create_app(
        settings,
        clock=clock,
        mailer=None,
        auth_config=AuthConfig(public_url=PUBLIC),
        oidc_providers={"univ": MAPPED},
        oidc_http=httpx.Client(transport=httpx.MockTransport(idp.handler)),
        auth_secret="test-flow-key",
    )


def test_role_mapping_raises_but_never_lowers(tmp_path: Path, idp: FakeIdP, clock: Clock) -> None:
    app = _mapped_app(tmp_path, idp, clock)
    c, r = oidc_login(app, idp, groups=["staff", "rc-authors"])
    assert r.status_code == 302
    assert c.get("/api/v1/me").json()["role"] == "author"
    c2, _ = oidc_login(app, idp, groups=["rc-admins", "rc-authors"])
    assert c2.get("/api/v1/me").json()["role"] == "admin"
    c3, _ = oidc_login(app, idp, groups=[])
    assert c3.get("/api/v1/me").json()["role"] == "admin"  # never lowered by the IdP
    entries = app.state.rc.auth.list_audit(50)
    reasons = [e.detail.get("reason") for e in entries if e.action == "user.role.changed"]
    assert reasons.count("idp:univ") == 2


def test_mapped_role_shapes() -> None:
    client = OidcClient(MAPPED, httpx.Client())
    claims = lambda v: Claims("s", None, False, None, {"groups": v})  # noqa: E731
    assert client.mapped_role(claims("rc-authors")) == "author"
    assert client.mapped_role(claims(["x", "rc-admins"])) == "admin"
    assert client.mapped_role(claims(42)) is None
    assert OidcClient(GITHUB, httpx.Client()).mapped_role(claims(["rc-admins"])) is None


def test_parse_providers_validation() -> None:
    for bad in (
        '[{"id": "x", "type": "saml", "client_id": "c"}]',
        '[{"id": "x", "issuer": "i", "client_id": "c", "role_map": {"g": "root"}}]',
        "[1]",
    ):
        with pytest.raises(ValueError):
            parse_providers({"RC_OIDC_PROVIDERS": bad})

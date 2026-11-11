"""OIDC login (AC-AUTH.3) end to end against an in-process fake IdP (httpx.MockTransport)."""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx
import jwt
import pytest
from argon2 import PasswordHasher
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI
from fastapi.testclient import TestClient

import robotics_curriculum.auth.crypto as crypto
from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.settings import Settings
from robotics_curriculum.auth.oidc import (
    Flow,
    OidcClient,
    OidcError,
    OidcProvider,
    open_flow,
    parse_providers,
    seal_flow,
)
from robotics_curriculum.auth.service import AuthConfig

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "tests" / "fixtures" / "curriculum"
ISSUER = "https://idp.test"
CLIENT_ID = "rc-web"
PUBLIC = "https://app.test"
PASSWORD = "correct horse battery staple"
T0 = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def fast_argon2(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        crypto, "_HASHER", PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)
    )


def _new_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _jwk(key: rsa.RSAPrivateKey, kid: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key()))
    return {**data, "kid": kid, "alg": "RS256", "use": "sig"}


@dataclass
class FakeIdP:
    """Discovery, JWKS and token endpoints; checks PKCE like a real provider."""

    key: rsa.RSAPrivateKey = field(default_factory=_new_key)
    kid: str = "k1"
    discovery_issuer: str = ISSUER
    codes: dict[str, dict[str, Any]] = field(default_factory=dict)
    token_requests: list[dict[str, str]] = field(default_factory=list)

    def handler(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/.well-known/openid-configuration":
            return httpx.Response(
                200,
                json={
                    "issuer": self.discovery_issuer,
                    "authorization_endpoint": f"{ISSUER}/authorize",
                    "token_endpoint": f"{ISSUER}/token",
                    "jwks_uri": f"{ISSUER}/jwks",
                },
            )
        if path == "/jwks":
            return httpx.Response(200, json={"keys": [_jwk(self.key, self.kid)]})
        if path == "/token":
            form = {k: v[0] for k, v in parse_qs(request.content.decode()).items()}
            self.token_requests.append(form)
            grant = self.codes.pop(form.get("code", ""), None)
            if grant is None:
                return httpx.Response(400, json={"error": "invalid_grant"})
            digest = hashlib.sha256(form["code_verifier"].encode()).digest()
            challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
            if challenge != grant["challenge"] or form["redirect_uri"] != grant["redirect_uri"]:
                return httpx.Response(400, json={"error": "invalid_grant"})
            return httpx.Response(200, json={"id_token": grant["id_token"], "token_type": "Bearer"})
        return httpx.Response(404)

    def id_token(
        self, *, nonce: str, key: rsa.RSAPrivateKey | None = None, alg: str = "RS256", **claims: Any
    ) -> str:
        now = int(T0.timestamp())
        payload = {
            "iss": ISSUER,
            "aud": CLIENT_ID,
            "iat": now,
            "exp": now + 300,
            "nonce": nonce,
            **claims,
        }
        if alg == "HS256":
            return jwt.encode(payload, "shared-secret-guess", algorithm="HS256")
        return jwt.encode(payload, key or self.key, algorithm=alg, headers={"kid": self.kid})

    def authorize(self, location: str, **claims: Any) -> tuple[str, str]:
        """Simulate the user approving; returns (code, state) for the callback."""
        query = {k: v[0] for k, v in parse_qs(urlparse(location).query).items()}
        assert query["code_challenge_method"] == "S256"
        assert query["client_id"] == CLIENT_ID and "openid" in query["scope"]
        overrides = claims.pop("token_overrides", {})
        nonce = overrides.pop("nonce", query["nonce"])
        code = secrets.token_urlsafe(8)
        self.codes[code] = {
            "challenge": query["code_challenge"],
            "redirect_uri": query["redirect_uri"],
            "id_token": self.id_token(nonce=nonce, **overrides, **claims),
        }
        return code, query["state"]


class Clock:
    def __init__(self) -> None:
        self.now = T0

    def __call__(self) -> datetime:
        return self.now


@pytest.fixture
def idp() -> FakeIdP:
    return FakeIdP()


@pytest.fixture
def clock() -> Clock:
    return Clock()


PROVIDER = OidcProvider(id="univ", issuer=ISSUER, client_id=CLIENT_ID, client_secret="s3cret")


@pytest.fixture
def app(tmp_path: Path, idp: FakeIdP, clock: Clock) -> FastAPI:
    settings = Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path, auth_mode="server")
    return create_app(
        settings,
        clock=clock,
        mailer=None,
        auth_config=AuthConfig(public_url=PUBLIC),
        oidc_providers={"univ": PROVIDER},
        oidc_http=httpx.Client(transport=httpx.MockTransport(idp.handler)),
        auth_secret="test-flow-key",
    )


def client_for(app: FastAPI) -> TestClient:
    return TestClient(app, base_url="https://testserver", follow_redirects=False)


def oidc_login(
    app: FastAPI,
    idp: FakeIdP,
    client: TestClient | None = None,
    *,
    return_to: str | None = None,
    sub: str = "u-1",
    email: str = "kim@univ.ac.kr",
    email_verified: bool = True,
    **extra: Any,
) -> tuple[TestClient, Any]:
    c = client or client_for(app)
    params = {"return_to": return_to} if return_to else {}
    start = c.get("/api/v1/auth/oidc/univ/start", params=params)
    assert start.status_code == 302, start.text
    code, state = idp.authorize(
        start.headers["location"],
        sub=sub,
        email=email,
        email_verified=email_verified,
        name="Kim",
        **extra,
    )
    callback = c.get("/api/v1/auth/oidc/univ/callback", params={"code": code, "state": state})
    return c, callback


def test_new_account_via_oidc(app: FastAPI, idp: FakeIdP) -> None:
    c, r = oidc_login(app, idp, return_to="/dashboard")
    assert r.status_code == 302, r.text
    assert r.headers["location"] == f"{PUBLIC}/dashboard"
    me = c.get("/api/v1/me").json()
    assert me["email"] == "kim@univ.ac.kr" and me["email_verified"] is True
    assert me["display_name"] == "Kim" and me["role"] == "learner"
    identities = c.get("/api/v1/me/identities").json()
    assert [i["provider"] for i in identities] == ["univ"]
    assert idp.token_requests[0]["code_verifier"]  # PKCE verifier sent
    # second login with the same subject lands in the same account
    c2, r2 = oidc_login(app, idp)
    assert r2.status_code == 302
    assert c2.get("/api/v1/me").json()["id"] == me["id"]
    # the only login method cannot be unlinked
    r = c.delete(
        f"/api/v1/me/identities/{identities[0]['id']}",
        headers={"X-CSRF-Token": c.cookies["csrf_token"]},
    )
    assert r.status_code == 409


def test_existing_email_is_not_linked_automatically(app: FastAPI, idp: FakeIdP) -> None:
    anon = client_for(app)
    assert (
        anon.post(
            "/api/v1/auth/signup", json={"email": "kim@univ.ac.kr", "password": PASSWORD}
        ).status_code
        == 201
    )
    _, r = oidc_login(app, idp)
    assert r.status_code == 409
    assert "log in with your password" in r.json()["detail"]

    session = client_for(app)
    login = session.post(
        "/api/v1/auth/login", json={"email": "kim@univ.ac.kr", "password": PASSWORD}
    )
    user_id = login.json()["user"]["id"]
    _, linked = oidc_login(app, idp, client=session)
    assert linked.status_code == 302
    fresh, again = oidc_login(app, idp)
    assert again.status_code == 302
    assert fresh.get("/api/v1/me").json()["id"] == user_id
    ident = fresh.get("/api/v1/me/identities").json()[0]
    r = fresh.delete(
        f"/api/v1/me/identities/{ident['id']}",
        headers={"X-CSRF-Token": fresh.cookies["csrf_token"]},
    )
    assert r.status_code == 204  # the password still works
    assert (
        fresh.delete(
            "/api/v1/me/identities/999", headers={"X-CSRF-Token": fresh.cookies["csrf_token"]}
        ).status_code
        == 404
    )


def test_unverified_email_cannot_sign_up(app: FastAPI, idp: FakeIdP) -> None:
    _, r = oidc_login(app, idp, email_verified=False)
    assert r.status_code == 403


@pytest.mark.parametrize(
    "tamper",
    [
        "nonce",
        "audience",
        "issuer",
        "foreign_key",
        "hs256",
        "expired",
        "multi_aud_no_azp",
        "multi_aud_other_azp",
    ],
)
def test_bad_id_tokens_are_rejected(app: FastAPI, idp: FakeIdP, tamper: str) -> None:
    overrides: dict[str, Any] = {
        "nonce": {"nonce": "attacker"},
        "audience": {"aud": "someone-else"},
        "issuer": {"iss": "https://evil.test"},
        "foreign_key": {"key": _new_key()},
        "hs256": {"alg": "HS256"},
        "expired": {"exp": int((T0 - timedelta(hours=1)).timestamp())},
        # OIDC Core 3.1.3.7 (3)-(5): several audiences need an azp naming us (SRV-14).
        "multi_aud_no_azp": {"aud": [CLIENT_ID, "other-client"]},
        "multi_aud_other_azp": {"aud": [CLIENT_ID, "other-client"], "azp": "other-client"},
    }[tamper]
    _, r = oidc_login(app, idp, token_overrides=overrides)
    assert r.status_code == 400, (tamper, r.text)
    assert r.headers["content-type"].startswith("application/problem+json")
    assert "sid=" not in r.headers.get("set-cookie", "")


def test_state_cookie_and_errors(app: FastAPI, idp: FakeIdP, clock: Clock) -> None:
    c = client_for(app)
    start = c.get("/api/v1/auth/oidc/univ/start")
    code, state = idp.authorize(
        start.headers["location"], sub="x", email="a@b.co", email_verified=True
    )
    cb = "/api/v1/auth/oidc/univ/callback"
    assert c.get(cb, params={"code": code, "state": "forged"}).status_code == 400
    assert c.get(cb, params={"error": "access_denied", "state": state}).status_code == 400
    assert client_for(app).get(cb, params={"code": code, "state": state}).status_code == 400
    clock.now += timedelta(minutes=11)  # flow cookie expired
    assert c.get(cb, params={"code": code, "state": state}).status_code == 400
    assert client_for(app).get("/api/v1/auth/oidc/nope/start").status_code == 404


def test_open_redirect_is_blocked(app: FastAPI, idp: FakeIdP) -> None:
    for i, target in enumerate(("//evil.test/x", "https://evil.test", "/\\evil.test")):
        _, r = oidc_login(app, idp, return_to=target, sub=f"s-{i}", email=f"o{i}@univ.ac.kr")
        assert r.headers["location"] == f"{PUBLIC}/", target


def test_disabled_account_cannot_use_oidc(app: FastAPI, idp: FakeIdP) -> None:
    c, _ = oidc_login(app, idp)
    user_id = c.get("/api/v1/me").json()["id"]
    service = app.state.rc.auth
    service.store.update_user(user_id, T0, status="disabled")
    _, r = oidc_login(app, idp)
    assert r.status_code == 401


def test_discovery_issuer_mismatch(app: FastAPI, idp: FakeIdP) -> None:
    idp.discovery_issuer = "https://other.test"
    r = client_for(app).get("/api/v1/auth/oidc/univ/start")
    assert r.status_code == 502


def test_key_rotation_refetches_jwks(idp: FakeIdP) -> None:
    client = OidcClient(
        PROVIDER, httpx.Client(transport=httpx.MockTransport(idp.handler)), clock=lambda: T0
    )
    client.verify(idp.id_token(nonce="n", sub="1"), nonce="n")
    idp.key, idp.kid = _new_key(), "k2"
    claims = client.verify(idp.id_token(nonce="n", sub="2"), nonce="n")
    assert claims.subject == "2" and claims.email is None and not claims.email_verified
    with pytest.raises(OidcError, match="cannot fetch"):
        OidcClient(
            PROVIDER, httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500)))
        ).config()


def test_explicit_endpoints_skip_discovery() -> None:
    provider = OidcProvider(
        id="x",
        issuer=ISSUER,
        client_id="c",
        authorization_endpoint="https://a",
        token_endpoint="https://t",
        jwks_uri="https://j",
    )
    client = OidcClient(
        provider, httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500)))
    )
    assert client.config()["token_endpoint"] == "https://t"
    url = client.authorization_url(state="s", nonce="n", challenge="c", redirect_uri="https://r")
    assert url.startswith("https://a?") and "code_challenge=c" in url
    with pytest.raises(OidcError, match="token request failed|token endpoint"):
        client.exchange("code", verifier="v", redirect_uri="https://r")


def test_flow_cookie_integrity() -> None:
    flow = Flow(provider="p", state="s", nonce="n", verifier="v", return_to="/", issued_at=1000)
    sealed = seal_flow(flow, b"key")
    assert open_flow(sealed, b"key", now=1001) == flow
    assert open_flow(sealed, b"other", now=1001) is None
    assert open_flow(sealed, b"key", now=1000 + 601) is None
    body, mac = sealed.split(".")
    assert open_flow(body[:-2] + "AA." + mac, b"key", now=1001) is None
    assert open_flow("garbage", b"key") is None


def test_parse_providers() -> None:
    assert parse_providers({}) == {}
    env = {
        "RC_OIDC_PROVIDERS": json.dumps(
            [
                {
                    "id": "google",
                    "issuer": "https://accounts.google.com",
                    "client_id": "g",
                    "client_secret_env": "G_SECRET",
                    "unknown": 1,
                },
                {"id": "univ", "issuer": ISSUER, "client_id": "u", "client_secret": "inline"},
            ]
        ),
        "G_SECRET": "from-env",
    }
    providers = parse_providers(env)
    assert providers["google"].client_secret == "from-env"
    assert providers["univ"].client_secret == "inline"
    assert "from-env" not in repr(providers["google"])
    for bad in ("{", "{}", '[{"id": "x"}]'):
        with pytest.raises(ValueError):
            parse_providers({"RC_OIDC_PROVIDERS": bad})


def test_multiple_audiences_with_our_azp_are_accepted(app: FastAPI, idp: FakeIdP) -> None:
    """The legitimate multi-audience case: azp names this client (SRV-14)."""
    _, r = oidc_login(
        app, idp, token_overrides={"aud": [CLIENT_ID, "other-client"], "azp": CLIENT_ID}
    )
    assert r.status_code == 302, r.text

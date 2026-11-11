"""OpenID Connect login: Authorization Code + PKCE (S256), ``state`` and ``nonce`` checks,
``id_token`` signature / issuer / audience / expiry verification against the provider's JWKS.

Providers come from ``RC_OIDC_PROVIDERS`` (JSON list)::

    [{"id": "google", "issuer": "https://accounts.google.com",
      "client_id": "...", "client_secret_env": "RC_OIDC_GOOGLE_SECRET"}]

Optional per provider: ``client_secret`` (inline), ``scopes`` (default
``openid email profile``), ``name``, and explicit ``authorization_endpoint`` /
``token_endpoint`` / ``jwks_uri`` (otherwise read from
``<issuer>/.well-known/openid-configuration``).

The in-flight login (state, nonce, PKCE verifier) is kept in a short-lived HMAC-signed cookie,
so the server stays stateless. See ``docs/architecture/auth.md`` §2.2.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlencode

import httpx
import jwt

ALLOWED_ALGS = ("RS256", "RS384", "RS512", "ES256", "ES384", "PS256")
FLOW_TTL_SECONDS = 600


class OidcError(Exception):
    """The provider answered unexpectedly or a token failed verification."""


@dataclass(frozen=True, slots=True)
class OidcProvider:
    id: str
    issuer: str
    client_id: str
    client_secret: str | None = field(default=None, repr=False)
    name: str | None = None
    scopes: str = "openid email profile"
    authorization_endpoint: str | None = None
    token_endpoint: str | None = None
    jwks_uri: str | None = None


def parse_providers(env: Mapping[str, str]) -> dict[str, OidcProvider]:
    """Providers from ``RC_OIDC_PROVIDERS``; ``{}`` when unset. Raises ``ValueError``."""
    raw = env.get("RC_OIDC_PROVIDERS", "").strip()
    if not raw:
        return {}
    try:
        items = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"RC_OIDC_PROVIDERS is not valid JSON: {exc}") from None
    if not isinstance(items, list):
        raise ValueError("RC_OIDC_PROVIDERS must be a JSON list")
    providers: dict[str, OidcProvider] = {}
    for item in items:
        if not isinstance(item, dict) or not {"id", "issuer", "client_id"} <= item.keys():
            raise ValueError("each OIDC provider needs id, issuer and client_id")
        secret = item.get("client_secret")
        if secret_env := item.get("client_secret_env"):
            secret = env.get(secret_env) or secret
        known = {f for f in OidcProvider.__dataclass_fields__ if f != "client_secret"}
        values = {k: v for k, v in item.items() if k in known}
        providers[item["id"]] = OidcProvider(**values, client_secret=secret)
    return providers


def pkce_pair() -> tuple[str, str]:
    """(verifier, S256 challenge)."""
    verifier = secrets.token_urlsafe(48)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return verifier, base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


# -- signed flow cookie --------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Flow:
    provider: str
    state: str
    nonce: str
    verifier: str = field(repr=False)
    return_to: str
    issued_at: int


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def seal_flow(flow: Flow, key: bytes) -> str:
    body = _b64(json.dumps(_flow_dict(flow)).encode())
    mac = _b64(hmac.new(key, body.encode("ascii"), hashlib.sha256).digest())
    return f"{body}.{mac}"


def _flow_dict(flow: Flow) -> dict[str, Any]:
    return {name: getattr(flow, name) for name in Flow.__dataclass_fields__}


def open_flow(sealed: str, key: bytes, *, now: float | None = None) -> Flow | None:
    """The flow if the MAC is valid and it is younger than :data:`FLOW_TTL_SECONDS`."""
    body, _, mac = sealed.partition(".")
    expected = _b64(hmac.new(key, body.encode("ascii"), hashlib.sha256).digest())
    if not mac or not hmac.compare_digest(mac, expected):
        return None
    try:
        flow = Flow(**json.loads(_unb64(body)))
    except (ValueError, TypeError):
        return None
    if (now if now is not None else time.time()) - flow.issued_at > FLOW_TTL_SECONDS:
        return None
    return flow


# -- client --------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Claims:
    subject: str
    email: str | None
    email_verified: bool
    name: str | None
    raw: dict[str, Any]


class OidcClient:
    def __init__(
        self,
        provider: OidcProvider,
        http: httpx.Client,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.provider = provider
        self.http = http
        self.clock = clock
        self._config: dict[str, Any] | None = None
        self._jwks: dict[str, Any] | None = None

    def _get_json(self, url: str) -> dict[str, Any]:
        try:
            response = self.http.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise OidcError(f"cannot fetch {url}: {exc}") from None
        if not isinstance(data, dict):
            raise OidcError(f"unexpected response from {url}")
        return data

    def config(self) -> dict[str, Any]:
        p = self.provider
        if p.authorization_endpoint and p.token_endpoint and p.jwks_uri:
            return {
                "issuer": p.issuer,
                "authorization_endpoint": p.authorization_endpoint,
                "token_endpoint": p.token_endpoint,
                "jwks_uri": p.jwks_uri,
            }
        if self._config is None:
            url = p.issuer.rstrip("/") + "/.well-known/openid-configuration"
            config = self._get_json(url)
            if config.get("issuer") != p.issuer:
                raise OidcError("discovery document issuer does not match the configured issuer")
            self._config = config
        return self._config

    def authorization_url(
        self, *, state: str, nonce: str, challenge: str, redirect_uri: str
    ) -> str:
        query = urlencode(
            {
                "response_type": "code",
                "client_id": self.provider.client_id,
                "redirect_uri": redirect_uri,
                "scope": self.provider.scopes,
                "state": state,
                "nonce": nonce,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
            }
        )
        return f"{self.config()['authorization_endpoint']}?{query}"

    def exchange(self, code: str, *, verifier: str, redirect_uri: str) -> str:
        """Trade the code for tokens; returns the raw ``id_token``."""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": verifier,
            "client_id": self.provider.client_id,
        }
        auth: tuple[str, str] | None = None
        if self.provider.client_secret:
            auth = (self.provider.client_id, self.provider.client_secret)
        try:
            response = (
                self.http.post(self.config()["token_endpoint"], data=data, auth=auth, timeout=10)
                if auth
                else self.http.post(self.config()["token_endpoint"], data=data, timeout=10)
            )
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise OidcError(f"token request failed: {exc}") from None
        if response.status_code != 200 or not isinstance(payload, dict):
            raise OidcError(f"token endpoint returned {response.status_code}")
        id_token = payload.get("id_token")
        if not isinstance(id_token, str):
            raise OidcError("token response has no id_token")
        return id_token

    def _key(self, kid: str | None) -> jwt.PyJWK:
        for refresh in (False, True):  # refetch once for key rotation
            if self._jwks is None or refresh:
                self._jwks = self._get_json(self.config()["jwks_uri"])
            for key in self._jwks.get("keys", []):
                if kid is None or key.get("kid") == kid:
                    return jwt.PyJWK(key)
        raise OidcError("no matching signing key in the provider's JWKS")

    def verify(self, id_token: str, *, nonce: str, leeway: int = 60) -> Claims:
        try:
            header = jwt.get_unverified_header(id_token)
            if header.get("alg") not in ALLOWED_ALGS:
                raise OidcError(f"id_token algorithm {header.get('alg')!r} is not allowed")
            claims = jwt.decode(
                id_token,
                key=self._key(header.get("kid")),
                algorithms=list(ALLOWED_ALGS),
                audience=self.provider.client_id,
                issuer=self.provider.issuer,
                options={
                    "require": ["exp", "iat", "iss", "aud", "sub"],
                    # checked below against the server clock
                    "verify_exp": False,
                    "verify_iat": False,
                    "verify_nbf": False,
                },
            )
        except jwt.PyJWTError as exc:
            raise OidcError(f"invalid id_token: {exc}") from None
        now = self.clock().timestamp()
        try:
            exp, iat = float(claims["exp"]), float(claims["iat"])
        except (TypeError, ValueError):
            raise OidcError("invalid id_token: exp/iat are not numbers") from None
        if exp < now - leeway:
            raise OidcError("invalid id_token: expired")
        if iat > now + leeway:
            raise OidcError("invalid id_token: issued in the future")
        if not hmac.compare_digest(str(claims.get("nonce", "")), nonce):
            raise OidcError("id_token nonce mismatch")
        email = claims.get("email")
        return Claims(
            subject=str(claims["sub"]),
            email=email.lower() if isinstance(email, str) else None,
            email_verified=claims.get("email_verified") is True,
            name=claims.get("name") if isinstance(claims.get("name"), str) else None,
            raw=claims,
        )

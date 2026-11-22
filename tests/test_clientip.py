# ruff: noqa: F811
# Fixtures are imported from test_auth and requested by name, which ruff sees as redefinitions.
"""The caller's address behind the web tier (``api/clientip.py``, ``RC_API_TRUSTED_PROXIES``)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.clientip import (
    Network,
    TrustedProxyError,
    client_address,
    parse_trusted_proxies,
)
from robotics_curriculum.api.settings import Settings, SettingsError
from robotics_curriculum.auth.mailer import FakeMailer
from robotics_curriculum.auth.service import AuthConfig
from test_auth import (  # noqa: F401  (fixtures are used by name)
    ADMIN,
    CURRICULUM,
    PASSWORD,
    Clock,
    clock,
    fast_argon2,
    mailer,
    signup,
)

LOOPBACK = parse_trusted_proxies(None)
COMPOSE = parse_trusted_proxies("127.0.0.1, 172.16.0.0/12")


@pytest.mark.parametrize(
    ("peer", "header", "trusted", "expected"),
    [
        # No proxy in front: the peer is the client, whatever the header claims.
        ("203.0.113.9", None, LOOPBACK, "203.0.113.9"),
        ("203.0.113.9", "198.51.100.1", LOOPBACK, "203.0.113.9"),
        # The web tier on loopback passes the browser's address on.
        ("127.0.0.1", "198.51.100.7", LOOPBACK, "198.51.100.7"),
        ("::1", "198.51.100.7", LOOPBACK, "198.51.100.7"),
        ("127.0.0.1", None, LOOPBACK, "127.0.0.1"),
        ("127.0.0.1", "", LOOPBACK, "127.0.0.1"),
        # A chain: edge proxy and web tier are ours, the browser is the first that is not.
        ("172.18.0.5", "198.51.100.7, 172.18.0.2", COMPOSE, "198.51.100.7"),
        # A client-invented entry sits to the left of the real one and is never reached.
        ("172.18.0.5", "10.0.0.1, 198.51.100.7, 172.18.0.2", COMPOSE, "198.51.100.7"),
        ("127.0.0.1", "1.1.1.1, 198.51.100.7", LOOPBACK, "198.51.100.7"),
        # Every hop is ours: the request began inside the deployment.
        ("172.18.0.5", "172.18.0.2", COMPOSE, "172.18.0.5"),
        # Garbage anywhere we would have to rely on means the header is not believed.
        ("127.0.0.1", "not-an-address", LOOPBACK, "127.0.0.1"),
        ("127.0.0.1", "198.51.100.7, unknown", LOOPBACK, "127.0.0.1"),
        # Ports and IPv6 forms.
        ("127.0.0.1", "198.51.100.7:51234", LOOPBACK, "198.51.100.7"),
        ("127.0.0.1", "[2001:db8::1]:443", LOOPBACK, "2001:db8::1"),
        ("127.0.0.1", "2001:db8::1", LOOPBACK, "2001:db8::1"),
        ("::ffff:127.0.0.1", "198.51.100.7", LOOPBACK, "198.51.100.7"),
        # A peer that is not an address at all (a test transport) is simply reported.
        ("testclient", "198.51.100.7", LOOPBACK, "testclient"),
        (None, "198.51.100.7", LOOPBACK, None),
    ],
)
def test_client_address(
    peer: str | None, header: str | None, trusted: tuple[Network, ...], expected: str | None
) -> None:
    assert client_address(peer, header, trusted) == expected


def test_trusted_proxies_default_to_loopback_and_reject_garbage() -> None:
    assert [str(n) for n in parse_trusted_proxies("  ")] == ["127.0.0.1/32", "::1/128"]
    assert [str(n) for n in parse_trusted_proxies("10.0.0.7, 172.16.0.0/12")] == [
        "10.0.0.7/32",
        "172.16.0.0/12",
    ]
    with pytest.raises(TrustedProxyError):
        parse_trusted_proxies("10.0.0.0/8, web")
    with pytest.raises(SettingsError):
        Settings.from_env({"RC_API_TRUSTED_PROXIES": "everyone"})
    assert Settings.from_env({"RC_API_TRUSTED_PROXIES": "192.168.0.0/16"}).trusted_proxies


def _app(tmp_path: Path, clock: Clock, mailer: FakeMailer) -> FastAPI:
    settings = Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path, auth_mode="server")
    return create_app(
        settings, clock=clock, mailer=mailer, auth_config=AuthConfig(bootstrap_admin_email=ADMIN)
    )


def _from(app: FastAPI, peer: str) -> TestClient:
    return TestClient(app, base_url="https://testserver", client=(peer, 50000))


def test_sessions_and_audit_record_the_browser_not_the_web_tier(
    tmp_path: Path, clock: Clock, mailer: FakeMailer
) -> None:
    app = _app(tmp_path, clock, mailer)
    signup(app, "learner@example.org")
    web = _from(app, "127.0.0.1")
    browser = {"X-Forwarded-For": "198.51.100.7", "User-Agent": "Mozilla/5.0 (test browser)"}
    r = web.post(
        "/api/v1/auth/login",
        json={"email": "learner@example.org", "password": PASSWORD},
        headers=browser,
    )
    assert r.status_code == 200, r.text
    session = web.get("/api/v1/me/sessions", headers=browser).json()[0]
    assert session["ip"] == "198.51.100.7"
    assert session["user_agent"] == "Mozilla/5.0 (test browser)"
    entry = app.state.rc.auth.list_audit(1, action_prefix="auth.login.success")[0]
    assert entry.actor_ip == "198.51.100.7"


def test_a_direct_caller_cannot_claim_another_address(
    tmp_path: Path, clock: Clock, mailer: FakeMailer
) -> None:
    app = _app(tmp_path, clock, mailer)
    signup(app, "learner@example.org")
    outsider = _from(app, "203.0.113.50")
    r = outsider.post(
        "/api/v1/auth/login",
        json={"email": "learner@example.org", "password": PASSWORD},
        headers={"X-Forwarded-For": "198.51.100.7"},
    )
    assert r.status_code == 200
    entry = app.state.rc.auth.list_audit(1, action_prefix="auth.login.success")[0]
    assert entry.actor_ip == "203.0.113.50"


def test_the_address_throttle_counts_each_browser_separately(
    tmp_path: Path, clock: Clock, mailer: FakeMailer
) -> None:
    """Behind one web tier, one visitor's failures must not lock the others out."""
    app = _app(tmp_path, clock, mailer)
    signup(app, "learner@example.org")
    web = _from(app, "127.0.0.1")
    limit = app.state.rc.auth.config.max_failures_ip
    for attempt in range(limit):
        # Different unknown addresses, so only the per-address counter fills up.
        r = web.post(
            "/api/v1/auth/login",
            json={"email": f"nobody{attempt}@example.org", "password": "wrong password!!"},
            headers={"X-Forwarded-For": "198.51.100.66"},
        )
        assert r.status_code == 401
    blocked = web.post(
        "/api/v1/auth/login",
        json={"email": "learner@example.org", "password": PASSWORD},
        headers={"X-Forwarded-For": "198.51.100.66"},
    )
    assert blocked.status_code == 429
    other = web.post(
        "/api/v1/auth/login",
        json={"email": "learner@example.org", "password": PASSWORD},
        headers={"X-Forwarded-For": "198.51.100.7"},
    )
    assert other.status_code == 200, other.text


def test_the_server_leaves_forwarded_headers_to_the_app(monkeypatch: pytest.MonkeyPatch) -> None:
    """uvicorn must not rewrite the peer address before the app applies its own trust rule.

    With uvicorn's handling on, a loopback web tier's report arrived looking as if it came
    from the browser, and the page-view endpoint (web tier only) refused its own web tier.
    """
    import uvicorn
    from typer.testing import CliRunner

    from robotics_curriculum.cli import app as cli_app

    seen: list[dict[str, object]] = []
    monkeypatch.setattr(uvicorn, "run", lambda app, **kw: seen.append(kw))
    monkeypatch.setattr("robotics_curriculum.api.log.configure_logging", lambda level: None)
    monkeypatch.setenv("RC_AUTH_MODE", "local")
    result = CliRunner().invoke(cli_app, ["--curriculum", str(CURRICULUM), "api", "serve"])
    assert result.exit_code == 0, result.output
    assert seen and seen[0]["proxy_headers"] is False

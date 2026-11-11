"""Regression tests for the second server review round (SRV-10, 11, 14, 15, 16) and the
SRV-08 follow-up: deleting an account leaves no identifiers behind.
"""

# Fixtures are imported from test_auth and requested by name.
# ruff: noqa: F401, F811

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

import httpx
import pytest
import uvicorn
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from robotics_curriculum.api.app import UnsafeConfiguration, check_exposure, create_app
from robotics_curriculum.api.settings import Settings
from robotics_curriculum.auth.mailer import FakeMailer, Mail, SmtpConfig, SmtpMailer
from robotics_curriculum.auth.models import TokenKind
from robotics_curriculum.auth.oidc import OidcError
from robotics_curriculum.auth.service import AuthConfig, Context
from robotics_curriculum.cli import app as cli_app
from test_auth import (
    ADMIN,
    CURRICULUM,
    PASSWORD,
    VECTORS,
    Clock,
    app,
    assert_problem,
    audit_actions,
    auth_service,
    client_for,
    clock,
    fast_argon2,
    login,
    mailer,
    settings,
    signup,
    user,
)


class BrokenMailer:
    """An SMTP server that is down: every send raises, as smtplib would."""

    def __init__(self) -> None:
        self.attempts = 0

    def send(self, mail: Mail) -> None:
        self.attempts += 1
        raise OSError(111, "Connection refused")


# -- SRV-10: a mail failure must not fail the account action ----------------------------


@pytest.fixture
def broken_app(settings: Settings, clock: Clock) -> FastAPI:
    return create_app(settings, clock=clock, mailer=BrokenMailer())


def test_signup_succeeds_when_mail_is_down(broken_app: FastAPI) -> None:
    c = client_for(broken_app)
    created = c.post(
        "/api/v1/auth/signup", json={"email": "learner@example.org", "password": PASSWORD}
    )
    assert created.status_code == 201, created.text
    assert created.json()["email_verified"] is False
    # the account works, it just has no verification link yet
    assert login(broken_app, "learner@example.org").get("/api/v1/me").status_code == 200
    assert "auth.mail.failed" in audit_actions(broken_app)


def test_forgot_password_succeeds_when_mail_is_down(broken_app: FastAPI) -> None:
    signup(broken_app, "learner@example.org", verify=False)
    c = client_for(broken_app)
    r = c.post("/api/v1/auth/password/forgot", json={"email": "learner@example.org"})
    assert r.status_code == 202, r.text
    mailer = broken_app.state.rc.auth.mailer
    assert isinstance(mailer, BrokenMailer) and mailer.attempts >= 1


def test_undeliverable_token_is_discarded(settings: Settings, clock: Clock) -> None:
    """A token whose mail bounced can never reach anyone, so it must not stay valid."""
    from sqlalchemy import select

    from robotics_curriculum.auth.schema import one_time_tokens

    app = create_app(settings, clock=clock, mailer=BrokenMailer())
    signup(app, "learner@example.org", verify=False)
    store = auth_service(app).store
    with store.engine.begin() as conn:
        rows = conn.execute(select(one_time_tokens.c.used_at)).scalars().all()
    assert rows and all(used is not None for used in rows), "an unsendable token stayed valid"


def test_smtp_mailer_errors_reach_the_service(settings: Settings, clock: Clock) -> None:
    class Failing:
        def __init__(self, host: str, port: int, timeout: int) -> None:
            raise OSError(111, "Connection refused")

    config = SmtpConfig(host="mail.invalid")
    app = create_app(settings, clock=clock, mailer=SmtpMailer(config, smtp=Failing))  # type: ignore[arg-type]
    r = client_for(app).post(
        "/api/v1/auth/signup", json={"email": "learner@example.org", "password": PASSWORD}
    )
    assert r.status_code == 201, r.text


# -- SRV-11: the bind guard lives in the app factory ------------------------------------


def test_create_app_refuses_local_mode_on_public_address(tmp_path: Path) -> None:
    public = Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path, host="0.0.0.0")
    with pytest.raises(UnsafeConfiguration, match="refusing to serve local mode"):
        create_app(public)
    # explicit opt-in, loopback and server mode are all fine
    check_exposure(public, {"RC_API_ALLOW_REMOTE_LOCAL": "1"})
    check_exposure(Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path, host="::1"), {})
    check_exposure(
        Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path, host="0.0.0.0", auth_mode="server"),
        {},
    )


def test_serve_reports_the_refusal_without_a_traceback(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(uvicorn, "run", lambda app, **kw: calls.append(kw["host"]))
    monkeypatch.setattr("robotics_curriculum.api.log.configure_logging", lambda level: None)
    monkeypatch.delenv("RC_API_ALLOW_REMOTE_LOCAL", raising=False)
    monkeypatch.setenv("RC_AUTH_MODE", "local")
    r = CliRunner().invoke(
        cli_app, ["--curriculum", str(CURRICULUM), "api", "serve", "--host", "0.0.0.0"]
    )
    assert r.exit_code == 1
    assert "refusing to serve local mode" in r.output
    assert "Traceback" not in r.output
    assert calls == []


# -- SRV-15: OIDC needs a shared flow key -----------------------------------------------


def test_oidc_without_a_shared_secret_is_refused(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    from robotics_curriculum.auth.oidc import OidcProvider

    server = replace(settings, auth_mode="server")
    providers = {"univ": OidcProvider(id="univ", issuer="https://i", client_id="c")}
    monkeypatch.delenv("RC_AUTH_SECRET", raising=False)
    with pytest.raises(UnsafeConfiguration, match="RC_AUTH_SECRET"):
        create_app(server, mailer=None, oidc_providers=providers)
    monkeypatch.setenv("RC_AUTH_SECRET", "shared")
    assert create_app(server, mailer=None, oidc_providers=providers) is not None
    # no providers configured: no secret needed
    assert create_app(server, mailer=None, oidc_providers={}) is not None


# -- SRV-16: optional metrics token ------------------------------------------------------


def test_metrics_token(tmp_path: Path) -> None:
    settings = Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path, metrics_token="s3cret")
    c = TestClient(create_app(settings))
    assert c.get("/metrics").status_code == 401
    assert c.get("/metrics", headers={"Authorization": "Basic x"}).status_code == 401
    assert c.get("/metrics", headers={"Authorization": "Bearer wrong"}).status_code == 401
    ok = c.get("/metrics", headers={"Authorization": "Bearer s3cret"})
    assert ok.status_code == 200 and "http_requests_total" in ok.text
    assert Settings.from_env({"RC_API_METRICS_TOKEN": " t "}).metrics_token == "t"
    assert Settings.from_env({}).metrics_token is None


# -- promote-admin needs a verified address ----------------------------------------------


def test_promote_admin_requires_verified_email(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("RC_AUTH_MODE", "server")
    monkeypatch.delenv("RC_DATABASE_URL", raising=False)
    app = create_app(settings, mailer=FakeMailer())
    signup(app, "ops@example.org", verify=False)
    base = ["--data-dir", str(settings.data_dir), "--curriculum", str(CURRICULUM)]
    runner = CliRunner()
    refused = runner.invoke(cli_app, [*base, "api", "promote-admin", "ops@example.org"])
    assert refused.exit_code == 1
    assert "has not verified" in refused.output
    assert login(app, "ops@example.org").get("/api/v1/me").json()["role"] == "learner"
    forced = runner.invoke(cli_app, [*base, "api", "promote-admin", "ops@example.org", "--force"])
    assert forced.exit_code == 0, forced.output
    assert login(app, "ops@example.org").get("/api/v1/me").json()["role"] == "admin"


def test_promote_admin_accepts_a_verified_account(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("RC_AUTH_MODE", "server")
    monkeypatch.delenv("RC_DATABASE_URL", raising=False)
    app = create_app(settings, mailer=FakeMailer())
    signup(app, "ops@example.org")  # clicks the mailed link
    base = ["--data-dir", str(settings.data_dir), "--curriculum", str(CURRICULUM)]
    r = CliRunner().invoke(cli_app, [*base, "api", "promote-admin", "ops@example.org"])
    assert r.exit_code == 0, r.output


# -- SRV-08 follow-up: deletion leaves no identifiers ------------------------------------


def test_deletion_removes_every_identifier(app: FastAPI) -> None:
    user(app, ADMIN)
    c = user(app, "learner@example.org")
    uid = c.get("/api/v1/me").json()["id"]
    c.post("/api/v1/progress/log", json={"lesson_id": VECTORS, "minutes": 5})
    c.post("/api/v1/me/tokens", json={"name": "t", "scopes": ["read:progress"]})
    c.post("/api/v1/auth/password/forgot", json={"email": "learner@example.org"})
    assert c.request("DELETE", "/api/v1/me", json={"password": PASSWORD}).status_code == 204

    service = auth_service(app)
    rows = service.list_audit(500)
    assert all(e.actor_user_id != uid for e in rows)
    assert all(e.actor_ip is None or e.actor_user_id != uid for e in rows)
    assert not any("learner@example.org" in str(e.detail) for e in rows)
    erased = service.store.get_user(uid)
    assert erased is not None
    assert erased.email == f"deleted-{uid}@invalid"
    assert erased.display_name is None and not erased.has_password
    assert service.store.list_tokens(uid) == []
    assert service.store.list_sessions(uid, service.clock()) == []
    assert service.store.list_identities(uid) == []
    assert service.store.consume_one_time("any", TokenKind.RESET_PASSWORD, service.clock()) is None
    # the address is free again and belongs to a new account
    fresh = signup(app, "learner@example.org")
    assert fresh["id"] != uid

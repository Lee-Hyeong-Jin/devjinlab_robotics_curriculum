"""Regression tests for docs/reviews/2026-11-11-server-review.md (SRV-01..08), auth side."""

# Fixtures are imported from test_auth and requested by name, which ruff sees as redefinitions.
# ruff: noqa: F811

from __future__ import annotations

import re

import pytest
import uvicorn
from fastapi import FastAPI
from typer.testing import CliRunner

from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.cli import is_loopback
from robotics_curriculum.api.settings import Settings
from robotics_curriculum.auth.mailer import FakeMailer
from robotics_curriculum.auth.service import AuthConfig, Context
from robotics_curriculum.cli import app as cli_app
from test_auth import (  # noqa: F401  (fixtures are used by name)
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


def _token(mail_body: str) -> str:
    found = re.search(r"token=(\S+)", mail_body)
    assert found
    return found[1]


def test_bootstrap_admin_needs_verified_email(app: FastAPI) -> None:
    """SRV-02: claiming RC_AUTH_ADMIN_EMAIL gives nothing until the mailbox is proven."""
    signup(app, ADMIN, verify=False)
    squatter = login(app, ADMIN)
    assert squatter.get("/api/v1/me").json()["role"] == "learner"
    assert_problem(squatter.get("/api/v1/admin/users"), 403)
    mail = next(m for m in reversed(app.state.rc.auth.mailer.outbox) if m.to == ADMIN)
    r = client_for(app).post("/api/v1/auth/verify-email", json={"token": _token(mail.body)})
    assert r.status_code == 204
    assert squatter.get("/api/v1/me").json()["role"] == "admin"
    promo = next(e for e in auth_service(app).list_audit(50) if e.action == "user.role.changed")
    assert promo.detail == {"from": "learner", "to": "admin", "reason": "bootstrap"}


def test_bootstrap_does_not_apply_once_an_admin_exists(
    settings: Settings, clock: Clock, mailer: FakeMailer
) -> None:
    config = AuthConfig(bootstrap_admin_email="late@example.org")
    app = create_app(settings, clock=clock, mailer=mailer, auth_config=config)
    signup(app, "first@example.org")
    auth_service(app).promote_admin("first@example.org", Context())
    signup(app, "late@example.org")
    assert login(app, "late@example.org").get("/api/v1/me").json()["role"] == "learner"


def test_promote_admin_cli(settings: Settings, monkeypatch: pytest.MonkeyPatch) -> None:
    app = create_app(settings, mailer=FakeMailer())
    signup(app, "ops@example.org")
    monkeypatch.setenv("RC_AUTH_MODE", "server")
    monkeypatch.delenv("RC_DATABASE_URL", raising=False)
    base = ["--data-dir", str(settings.data_dir), "--curriculum", str(CURRICULUM)]
    runner = CliRunner()
    ok = runner.invoke(cli_app, [*base, "api", "promote-admin", "ops@example.org"])
    assert ok.exit_code == 0, ok.output
    assert "is now admin" in ok.output
    assert login(app, "ops@example.org").get("/api/v1/me").json()["role"] == "admin"
    assert runner.invoke(cli_app, [*base, "api", "promote-admin", "ops@example.org"]).exit_code == 0
    missing = runner.invoke(cli_app, [*base, "api", "promote-admin", "nobody@example.org"])
    assert missing.exit_code == 1 and "no active account" in missing.output
    monkeypatch.setenv("RC_AUTH_MODE", "local")
    local = runner.invoke(cli_app, [*base, "api", "promote-admin", "ops@example.org"])
    assert local.exit_code == 1 and "server mode" in local.output


def test_serve_refuses_local_mode_on_public_address(monkeypatch: pytest.MonkeyPatch) -> None:
    """SRV-01: local mode (no login) binds only to loopback unless explicitly allowed."""
    calls: list[str] = []
    monkeypatch.setattr(uvicorn, "run", lambda app, **kw: calls.append(kw["host"]))
    monkeypatch.setattr("robotics_curriculum.api.log.configure_logging", lambda level: None)
    monkeypatch.delenv("RC_API_ALLOW_REMOTE_LOCAL", raising=False)
    monkeypatch.setenv("RC_AUTH_MODE", "local")
    runner = CliRunner()
    serve = ["--curriculum", str(CURRICULUM), "api", "serve", "--host"]
    refused = runner.invoke(cli_app, [*serve, "0.0.0.0"])
    assert refused.exit_code == 1 and "refusing to serve local mode" in refused.output
    assert calls == []
    assert runner.invoke(cli_app, [*serve, "127.0.0.1"]).exit_code == 0
    monkeypatch.setenv("RC_API_ALLOW_REMOTE_LOCAL", "1")
    assert runner.invoke(cli_app, [*serve, "0.0.0.0"]).exit_code == 0
    assert calls == ["127.0.0.1", "0.0.0.0"]
    assert is_loopback("localhost") and is_loopback("::1") and not is_loopback("example.org")


def test_reset_requests_are_throttled_without_enumeration(app: FastAPI, mailer: FakeMailer) -> None:
    """SRV-03: three requests per address per 15 minutes, the same for unknown addresses."""
    signup(app, "learner@example.org")
    c = client_for(app)
    sent = len(mailer.outbox)
    for email in ("learner@example.org", "ghost@example.org"):
        codes = [
            c.post("/api/v1/auth/password/forgot", json={"email": email}).status_code
            for _ in range(4)
        ]
        assert codes == [202, 202, 202, 429], email
    assert len(mailer.outbox) == sent + 3
    assert "auth.password.reset_throttled" in audit_actions(app)
    # reset requests from this IP do not count as failed logins
    assert login(app, "learner@example.org").get("/api/v1/me").status_code == 200


def test_reset_ip_throttle(settings: Settings, clock: Clock, mailer: FakeMailer) -> None:
    app = create_app(
        settings, clock=clock, mailer=mailer, auth_config=AuthConfig(max_resets_per_ip=2)
    )
    c = client_for(app)
    codes = [
        c.post("/api/v1/auth/password/forgot", json={"email": f"x{i}@example.org"}).status_code
        for i in range(3)
    ]
    assert codes == [202, 202, 429]
    clock.advance(minutes=16)
    assert (
        c.post("/api/v1/auth/password/forgot", json={"email": "y@example.org"}).status_code == 202
    )


def test_only_newest_reset_token_works(app: FastAPI, mailer: FakeMailer) -> None:
    """SRV-04."""
    signup(app, "learner@example.org")
    c = client_for(app)
    for _ in range(2):
        c.post("/api/v1/auth/password/forgot", json={"email": "learner@example.org"})
    first, second = (_token(m.body) for m in mailer.outbox[-2:])
    stale = c.post("/api/v1/auth/password/reset", json={"token": first, "password": "x" * 14})
    assert_problem(stale, 422)
    fresh = c.post("/api/v1/auth/password/reset", json={"token": second, "password": "y" * 14})
    assert fresh.status_code == 204
    assert "auth.password.reset_invalid" in audit_actions(app)


def test_denials_and_admin_reads_are_audited(app: FastAPI) -> None:
    """SRV-07."""
    admin = user(app, ADMIN)
    learner = user(app, "learner@example.org")
    learner.post(
        "/api/v1/progress/start", json={"lesson_id": VECTORS}, headers={"X-CSRF-Token": "x"}
    )
    learner.get("/api/v1/admin/users")
    client_for(app).get("/api/v1/me", headers={"Authorization": "Bearer rcp_forged"})
    admin.get("/api/v1/admin/users")
    admin_id = admin.get("/api/v1/me").json()["id"]
    admin.get(f"/api/v1/admin/users/{admin_id}")
    admin.get("/api/v1/admin/audit")
    entries = auth_service(app).list_audit(200)
    reasons = {e.detail.get("reason") for e in entries if e.action == "auth.denied"}
    assert {"csrf", "role", "bad_token"} <= reasons
    actions = {e.action for e in entries}
    assert {"admin.users.viewed", "admin.user.viewed", "admin.audit.viewed"} <= actions


def test_account_deletion_anonymizes_audit_now(app: FastAPI) -> None:
    """SRV-08: the deleted user's id and IPs leave the audit log immediately."""
    user(app, ADMIN)
    c = user(app, "learner@example.org")
    uid = c.get("/api/v1/me").json()["id"]
    assert c.request("DELETE", "/api/v1/me", json={"password": PASSWORD}).status_code == 204
    entries = auth_service(app).list_audit(500)
    assert all(e.actor_user_id != uid for e in entries)
    deleted = next(e for e in entries if e.action == "account.deleted")
    assert deleted.actor_user_id is None and deleted.actor_ip is None
    assert deleted.target_id == str(uid)

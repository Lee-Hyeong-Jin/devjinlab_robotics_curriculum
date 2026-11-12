"""Email verification as an operator-visible state: what a server without SMTP tells clients,
and the optional gate that keeps an unproven address from writing (RC_AUTH_REQUIRE_VERIFIED_EMAIL).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
from argon2 import PasswordHasher
from fastapi import FastAPI
from fastapi.testclient import TestClient

import robotics_curriculum.auth.crypto as crypto
from robotics_curriculum.api.app import UnsafeConfiguration, create_app
from robotics_curriculum.api.settings import Settings
from robotics_curriculum.auth.mailer import FakeMailer
from robotics_curriculum.auth.service import AuthConfig

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "tests" / "fixtures" / "curriculum"
VECTORS = "m1-vectors-matrices"
EMAIL = "kim@example.org"
PASSWORD = "correct horse battery staple"


@pytest.fixture(autouse=True)
def fast_argon2(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        crypto, "_HASHER", PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)
    )


def build(tmp_path: Path, *, mailer: FakeMailer | None, require_verified: bool = False) -> FastAPI:
    return create_app(
        Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path, auth_mode="server"),
        mailer=mailer,
        auth_config=AuthConfig(require_verified_email=require_verified),
    )


def client_for(app: FastAPI) -> TestClient:
    return TestClient(app, base_url="https://testserver")


def sign_up(app: FastAPI, email: str = EMAIL) -> tuple[TestClient, dict[str, Any]]:
    c = client_for(app)
    r = c.post("/api/v1/auth/signup", json={"email": email, "password": PASSWORD})
    assert r.status_code == 201, r.text
    body = dict(r.json())
    login = c.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert login.status_code == 200, login.text
    c.headers["X-CSRF-Token"] = login.json()["csrf_token"]
    return c, body


def verify(app: FastAPI, c: TestClient, mailer: FakeMailer, email: str = EMAIL) -> None:
    mail = next(m for m in reversed(mailer.outbox) if m.to == email)
    token = re.search(r"token=(\S+)", mail.body)
    assert token
    assert c.post("/api/v1/auth/verify-email", json={"token": token[1]}).status_code == 204


# -- the state a client reads ---


def test_state_is_unavailable_when_the_server_cannot_send_mail(tmp_path: Path) -> None:
    """The reason the web hides "check your inbox": the link is never coming."""
    app = build(tmp_path, mailer=None)
    c, signup = sign_up(app)
    assert signup["email_verification"] == "unavailable"
    assert signup["email_verified"] is False
    assert c.get("/api/v1/me").json()["email_verification"] == "unavailable"


def test_state_walks_from_pending_to_verified_when_mail_works(tmp_path: Path) -> None:
    mailer = FakeMailer()
    app = build(tmp_path, mailer=mailer)
    c, signup = sign_up(app)
    assert signup["email_verification"] == "pending"
    assert c.get("/api/v1/me").json()["email_verification"] == "pending"
    verify(app, c, mailer)
    me = c.get("/api/v1/me").json()
    assert me["email_verification"] == "verified" and me["email_verified"] is True


def test_login_and_profile_update_report_the_same_state(tmp_path: Path) -> None:
    app = build(tmp_path, mailer=None)
    c, _ = sign_up(app)
    login = c.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
    assert login.json()["user"]["email_verification"] == "unavailable"
    c.headers["X-CSRF-Token"] = login.json()["csrf_token"]
    patched = c.patch("/api/v1/me", json={"display_name": "Kim"})
    assert patched.json()["email_verification"] == "unavailable"


def test_the_admin_user_list_reports_the_state_too(tmp_path: Path) -> None:
    mailer = FakeMailer()
    app = create_app(
        Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path, auth_mode="server"),
        mailer=mailer,
        auth_config=AuthConfig(bootstrap_admin_email=EMAIL),
    )
    c, _ = sign_up(app)
    verify(app, c, mailer)  # the bootstrap admin is promoted on verification
    rows = c.get("/api/v1/admin/users").json()["items"]
    assert [row["email_verification"] for row in rows] == ["verified"]


# -- resending ---


def test_resend_sends_the_link_again_and_invalidates_the_old_one(tmp_path: Path) -> None:
    mailer = FakeMailer()
    app = build(tmp_path, mailer=mailer)
    c, _ = sign_up(app)
    first = re.search(r"token=(\S+)", mailer.outbox[-1].body)
    assert first

    assert c.post("/api/v1/auth/resend-verification").status_code == 202
    assert len(mailer.outbox) == 2
    # The superseded link must not keep working, or a leaked first mail stays usable.
    assert c.post("/api/v1/auth/verify-email", json={"token": first[1]}).status_code == 422
    verify(app, c, mailer)
    assert c.get("/api/v1/me").json()["email_verification"] == "verified"


def test_resend_is_503_when_mail_is_not_configured(tmp_path: Path) -> None:
    app = build(tmp_path, mailer=None)
    c, _ = sign_up(app)
    r = c.post("/api/v1/auth/resend-verification")
    assert r.status_code == 503
    assert r.headers["content-type"].startswith("application/problem+json")


def test_resend_needs_a_session_so_there_is_nothing_to_enumerate(tmp_path: Path) -> None:
    app = build(tmp_path, mailer=FakeMailer())
    assert client_for(app).post("/api/v1/auth/resend-verification").status_code == 401


def test_resend_is_quiet_once_the_address_is_verified(tmp_path: Path) -> None:
    mailer = FakeMailer()
    app = build(tmp_path, mailer=mailer)
    c, _ = sign_up(app)
    verify(app, c, mailer)
    sent = len(mailer.outbox)
    assert c.post("/api/v1/auth/resend-verification").status_code == 202
    assert len(mailer.outbox) == sent


# -- the optional write gate ---


def test_an_unverified_account_may_read_but_not_write_when_the_gate_is_on(
    tmp_path: Path,
) -> None:
    mailer = FakeMailer()
    app = build(tmp_path, mailer=mailer, require_verified=True)
    c, _ = sign_up(app)

    assert c.get("/api/v1/progress/status").status_code == 200
    assert c.get("/api/v1/courses").status_code == 200

    blocked = c.post("/api/v1/progress/log", json={"lesson_id": VECTORS, "minutes": 5})
    assert blocked.status_code == 403
    assert blocked.headers["content-type"].startswith("application/problem+json")
    assert "resend-verification" in blocked.json()["detail"]

    token = c.post("/api/v1/me/tokens", json={"name": "cli", "scopes": ["read:progress"]})
    assert token.status_code == 403

    verify(app, c, mailer)
    assert c.post("/api/v1/progress/log", json={"lesson_id": VECTORS, "minutes": 5}).status_code
    assert (
        c.post("/api/v1/me/tokens", json={"name": "cli", "scopes": ["read:progress"]}).status_code
        == 201
    )


def test_the_gate_is_off_by_default(tmp_path: Path) -> None:
    app = build(tmp_path, mailer=None)
    c, _ = sign_up(app)
    assert c.post(
        "/api/v1/progress/log", json={"lesson_id": VECTORS, "minutes": 5}
    ).status_code in (
        200,
        201,
    )


def test_account_management_keeps_working_behind_the_gate(tmp_path: Path) -> None:
    """Being unable to prove the address must not lock the reader out of their own account."""
    app = build(tmp_path, mailer=FakeMailer(), require_verified=True)
    c, _ = sign_up(app)
    assert c.patch("/api/v1/me", json={"display_name": "Kim"}).status_code == 200
    assert c.post("/api/v1/auth/resend-verification").status_code == 202
    assert c.post("/api/v1/auth/logout").status_code == 204


def test_a_blocked_write_is_audited(tmp_path: Path) -> None:
    app = build(tmp_path, mailer=FakeMailer(), require_verified=True)
    c, _ = sign_up(app)
    c.post("/api/v1/progress/log", json={"lesson_id": VECTORS, "minutes": 5})
    reasons = [
        e.detail.get("reason")
        for e in app.state.rc.auth.list_audit(100)
        if e.action == "auth.denied"
    ]
    assert "email_unverified" in reasons


def test_the_gate_without_mail_refuses_to_start(tmp_path: Path) -> None:
    """Otherwise every write is 403 for everyone, with no way to ask for the link."""
    with pytest.raises(UnsafeConfiguration) as exc:
        build(tmp_path, mailer=None, require_verified=True)
    assert "RC_SMTP_HOST" in str(exc.value)


def test_local_mode_ignores_the_gate(tmp_path: Path) -> None:
    app = create_app(
        Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path, auth_mode="local"), mailer=None
    )
    c = client_for(app)
    assert c.post(
        "/api/v1/progress/log", json={"lesson_id": VECTORS, "minutes": 5}
    ).status_code in (
        200,
        201,
    )


def test_the_flag_is_read_from_the_environment() -> None:
    assert AuthConfig.from_env({}).require_verified_email is False
    assert (
        AuthConfig.from_env({"RC_AUTH_REQUIRE_VERIFIED_EMAIL": "0"}).require_verified_email is False
    )
    assert (
        AuthConfig.from_env({"RC_AUTH_REQUIRE_VERIFIED_EMAIL": "1"}).require_verified_email is True
    )

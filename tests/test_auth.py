"""P2-2 auth: accounts, sessions + CSRF, PATs, roles, isolation, audit, security headers.

Includes the security scenarios from PRD C.3 / docs/architecture/auth.md §7: authentication
bypass, privilege escalation, session fixation, cross-user access, brute force.
"""

from __future__ import annotations

import logging
import re
import sqlite3
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from argon2 import PasswordHasher
from fastapi import FastAPI
from fastapi.testclient import TestClient

import robotics_curriculum.auth.crypto as crypto
from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.settings import Settings, SettingsError
from robotics_curriculum.auth.crypto import PasswordPolicyError, Passwords, check_policy
from robotics_curriculum.auth.mailer import FakeMailer, Mail, SmtpConfig, SmtpMailer
from robotics_curriculum.auth.service import AuthConfig, AuthService, Context
from robotics_curriculum.auth.store import SqlAuthStore

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "tests" / "fixtures" / "curriculum"
VECTORS = "m1-vectors-matrices"
PROBLEM = "application/problem+json"
ADMIN = "admin@example.org"
PASSWORD = "correct horse battery staple"
T0 = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)


class Clock:
    def __init__(self) -> None:
        self.now = T0

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **kw: float) -> None:
        self.now += timedelta(**kw)


@pytest.fixture(autouse=True)
def fast_argon2(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cheap Argon2id parameters for speed; test_password_hash_is_argon2id checks the real ones."""
    monkeypatch.setattr(
        crypto, "_HASHER", PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)
    )


@pytest.fixture
def clock() -> Clock:
    return Clock()


@pytest.fixture
def mailer() -> FakeMailer:
    return FakeMailer()


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path, auth_mode="server")


@pytest.fixture
def app(settings: Settings, clock: Clock, mailer: FakeMailer) -> FastAPI:
    return create_app(
        settings, clock=clock, mailer=mailer, auth_config=AuthConfig(bootstrap_admin_email=ADMIN)
    )


def client_for(app: FastAPI) -> TestClient:
    return TestClient(app, base_url="https://testserver")


@pytest.fixture
def anon(app: FastAPI) -> TestClient:
    return client_for(app)


def signup(
    app: FastAPI, email: str, password: str = PASSWORD, *, verify: bool = True
) -> dict[str, Any]:
    """Sign up and, like a real user, click the mailed verification link."""
    c = client_for(app)
    r = c.post("/api/v1/auth/signup", json={"email": email, "password": password})
    assert r.status_code == 201, r.text
    mailer = app.state.rc.auth.mailer
    if verify and isinstance(mailer, FakeMailer):
        mail = next(m for m in reversed(mailer.outbox) if m.to == email.lower())
        token = re.search(r"token=(\S+)", mail.body)
        assert token
        assert c.post("/api/v1/auth/verify-email", json={"token": token[1]}).status_code == 204
    return dict(r.json())


def login(app: FastAPI, email: str, password: str = PASSWORD) -> TestClient:
    c = client_for(app)
    r = c.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    c.headers["X-CSRF-Token"] = r.json()["csrf_token"]
    return c


def user(app: FastAPI, email: str) -> TestClient:
    signup(app, email)
    return login(app, email)


def assert_problem(r: Any, status: int) -> dict[str, Any]:
    assert r.status_code == status, r.text
    assert r.headers["content-type"].startswith(PROBLEM)
    return dict(r.json())


def auth_service(app: FastAPI) -> AuthService:
    service = app.state.rc.auth
    assert isinstance(service, AuthService)
    return service


def audit_actions(app: FastAPI) -> list[str]:
    return [e.action for e in auth_service(app).list_audit(500)]


# -- modes ---


def test_local_mode_has_no_accounts(tmp_path: Path) -> None:
    c = client_for(create_app(Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path)))
    assert c.get("/api/v1/courses").status_code == 200
    assert c.get("/api/v1/me").json()["id"] == 1
    assert_problem(c.post("/api/v1/auth/login", json={"email": "a@b.co", "password": "x"}), 404)
    assert_problem(c.get("/api/v1/me/tokens"), 404)
    assert "Strict-Transport-Security" not in c.get("/healthz").headers


def test_settings_auth_mode() -> None:
    s = Settings.from_env({"RC_AUTH_MODE": "SERVER", "RC_DATABASE_URL": " sqlite:///x.db "})
    assert s.server_mode and s.database_url == "sqlite:///x.db" and s.cookie_secure
    assert not Settings.from_env({"RC_AUTH_COOKIE_SECURE": "0"}).cookie_secure
    with pytest.raises(SettingsError, match="RC_AUTH_MODE"):
        Settings.from_env({"RC_AUTH_MODE": "cloud"})


def test_unauthenticated_requests_are_401(anon: TestClient) -> None:
    assert anon.get("/healthz").status_code == 200
    assert anon.get("/readyz").status_code == 200
    for path in (
        "/api/v1/courses",
        "/api/v1/progress/status",
        "/api/v1/me",
        "/api/v1/reports/weekly",
        "/api/v1/admin/users",
    ):
        r = anon.get(path)
        assert_problem(r, 401)
        assert r.headers["www-authenticate"].startswith("Bearer")
    anon.cookies.set("sid", "forged")
    assert_problem(anon.get("/api/v1/courses"), 401)


# -- passwords ---


def test_password_hash_is_argon2id_and_never_logged(
    monkeypatch: pytest.MonkeyPatch, settings: Settings, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.undo()  # real parameters from docs/architecture/auth.md §2.1
    app = create_app(settings, mailer=FakeMailer())
    with caplog.at_level(logging.DEBUG):
        signup(app, "learner@example.org")
        login(app, "learner@example.org")
        client_for(app).post(
            "/api/v1/auth/login", json={"email": "learner@example.org", "password": "wrong " * 3}
        )
    stored = auth_service(app).store.password_hash(1)
    assert stored is not None
    assert stored.startswith("$argon2id$v=19$m=65536,t=3,p=4$")
    raw = (settings.data_dir / "auth.db").read_bytes()
    assert PASSWORD.encode() not in raw
    assert PASSWORD not in caplog.text
    assert "wrong wrong" not in caplog.text


def test_password_policy(anon: TestClient) -> None:
    r = anon.post("/api/v1/auth/signup", json={"email": "a@example.org", "password": "short"})
    assert "at least 12" in assert_problem(r, 422)["detail"]
    r = anon.post(
        "/api/v1/auth/signup", json={"email": "jinsoo@example.org", "password": "my-jinsoo-pass-1"}
    )
    assert "email" in assert_problem(r, 422)["detail"]
    with pytest.raises(PasswordPolicyError, match="at most"):
        check_policy("x" * 129, email="a@b.co")
    with pytest.raises(PasswordPolicyError, match="name"):
        check_policy("hello-gildong-123", email="a@b.co", display_name="Gildong")
    assert_problem(
        anon.post("/api/v1/auth/signup", json={"email": "not-an-email", "password": PASSWORD}), 422
    )


def test_pepper_and_rehash() -> None:
    peppered = Passwords("pepper")
    stored = peppered.hash("pw")
    assert peppered.verify(stored, "pw")
    assert not Passwords("other").verify(stored, "pw")
    assert not peppered.verify(None, "pw")
    assert not peppered.verify("not-a-hash", "pw")
    assert Passwords().needs_rehash(stored) is False


# -- signup / email verification ---


def test_signup_verify_email_and_duplicates(app: FastAPI, mailer: FakeMailer) -> None:
    created = signup(app, "Learner@Example.org", verify=False)
    assert created["email"] == "learner@example.org"
    assert created["role"] == "learner"
    assert created["email_verified"] is False
    assert_problem(
        client_for(app).post(
            "/api/v1/auth/signup", json={"email": "LEARNER@example.org", "password": PASSWORD}
        ),
        409,
    )
    token = re.search(r"token=(\S+)", mailer.outbox[-1].body)
    assert token
    c = client_for(app)
    assert c.post("/api/v1/auth/verify-email", json={"token": token[1]}).status_code == 204
    assert_problem(c.post("/api/v1/auth/verify-email", json={"token": token[1]}), 422)
    me = login(app, "learner@example.org").get("/api/v1/me").json()
    assert me["email_verified"] is True
    assert "user.created" in audit_actions(app)
    assert "user.email_verified" in audit_actions(app)


def test_signup_can_be_disabled(settings: Settings) -> None:
    app = create_app(settings, mailer=None, auth_config=AuthConfig(allow_signup=False))
    r = client_for(app).post("/api/v1/auth/signup", json={"email": "a@b.co", "password": PASSWORD})
    assert_problem(r, 403)


# -- login, cookies, throttling, fixation ---


def test_login_sets_hardened_cookies(app: FastAPI) -> None:
    signup(app, "learner@example.org")
    r = client_for(app).post(
        "/api/v1/auth/login", json={"email": "learner@example.org", "password": PASSWORD}
    )
    cookies = r.headers.get_list("set-cookie")
    sid = next(c for c in cookies if c.startswith("sid="))
    csrf = next(c for c in cookies if c.startswith("csrf_token="))
    for flag in ("HttpOnly", "Secure", "SameSite=lax", "Path=/"):
        assert flag.lower() in sid.lower()
    assert "httponly" not in csrf.lower()
    assert "secure" in csrf.lower()
    assert r.json()["csrf_token"] in csrf
    assert r.headers["cache-control"] == "no-store"


def test_login_failures_are_uniform_and_throttled(app: FastAPI, clock: Clock) -> None:
    signup(app, "learner@example.org")
    c = client_for(app)
    wrong = c.post(
        "/api/v1/auth/login", json={"email": "learner@example.org", "password": "x" * 12}
    )
    unknown = c.post(
        "/api/v1/auth/login", json={"email": "nobody@example.org", "password": "x" * 12}
    )
    assert assert_problem(wrong, 401)["detail"] == assert_problem(unknown, 401)["detail"]
    for _ in range(4):
        c.post("/api/v1/auth/login", json={"email": "learner@example.org", "password": "y" * 12})
    blocked = c.post(
        "/api/v1/auth/login", json={"email": "learner@example.org", "password": PASSWORD}
    )
    assert_problem(blocked, 429)
    assert blocked.headers["retry-after"] == "900"
    clock.advance(minutes=16)
    assert login(app, "learner@example.org").get("/api/v1/me").status_code == 200
    actions = audit_actions(app)
    assert actions.count("auth.login.failed") == 6
    assert "auth.login.throttled" in actions
    assert "auth.login.success" in actions


def test_ip_throttle(settings: Settings, clock: Clock) -> None:
    app = create_app(settings, clock=clock, mailer=None, auth_config=AuthConfig(max_failures_ip=3))
    c = client_for(app)
    for i in range(3):
        c.post("/api/v1/auth/login", json={"email": f"u{i}@example.org", "password": "x" * 12})
    assert_problem(
        c.post("/api/v1/auth/login", json={"email": "z@example.org", "password": "x"}), 429
    )


def test_session_fixation_is_prevented(app: FastAPI) -> None:
    signup(app, "learner@example.org")
    c = client_for(app)
    c.cookies.set("sid", "attacker-chosen-session-id", domain="testserver")
    r = c.post("/api/v1/auth/login", json={"email": "learner@example.org", "password": PASSWORD})
    assert r.status_code == 200
    issued = next(v for v in r.headers.get_list("set-cookie") if v.startswith("sid="))
    assert "attacker-chosen-session-id" not in issued
    attacker = client_for(app)
    attacker.cookies.set("sid", "attacker-chosen-session-id")
    assert_problem(attacker.get("/api/v1/me"), 401)


def test_disabled_and_deleted_users_cannot_log_in(app: FastAPI) -> None:
    admin = user(app, ADMIN)
    learner_id = signup(app, "learner@example.org")["id"]
    session = login(app, "learner@example.org")
    r = admin.patch(f"/api/v1/admin/users/{learner_id}", json={"status": "disabled"})
    assert r.status_code == 200 and r.json()["status"] == "disabled"
    assert_problem(session.get("/api/v1/me"), 401)  # sessions revoked
    r = client_for(app).post(
        "/api/v1/auth/login", json={"email": "learner@example.org", "password": PASSWORD}
    )
    assert_problem(r, 401)
    assert (
        admin.patch(f"/api/v1/admin/users/{learner_id}", json={"status": "active"}).status_code
        == 200
    )
    assert login(app, "learner@example.org").get("/api/v1/me").status_code == 200


# -- sessions ---


def test_csrf_required_for_cookie_writes(app: FastAPI) -> None:
    c = user(app, "learner@example.org")
    token = c.headers.pop("X-CSRF-Token")
    assert c.get("/api/v1/progress/status").status_code == 200
    body = {"lesson_id": VECTORS}
    assert_problem(c.post("/api/v1/progress/start", json=body), 403)
    assert_problem(
        c.post("/api/v1/progress/start", json=body, headers={"X-CSRF-Token": "guess"}), 403
    )
    r = c.post("/api/v1/progress/start", json=body, headers={"X-CSRF-Token": token})
    assert r.status_code == 201


def test_logout_revokes_session(app: FastAPI) -> None:
    c = user(app, "learner@example.org")
    r = c.post("/api/v1/auth/logout")
    assert r.status_code == 204
    assert_problem(c.get("/api/v1/me"), 401)
    assert "auth.logout" in audit_actions(app)


def test_session_idle_sliding_and_absolute_expiry(app: FastAPI, clock: Clock) -> None:
    c = user(app, "learner@example.org")
    for _ in range(2):  # active every 10 days: the 14-day idle window keeps sliding
        clock.advance(days=10)
        assert c.get("/api/v1/me").status_code == 200
    clock.advance(days=9, hours=23)  # 29d23h after login, still active
    assert c.get("/api/v1/me").status_code == 200
    clock.advance(hours=2)  # past the 30-day absolute lifetime
    assert_problem(c.get("/api/v1/me"), 401)

    idle = login(app, "learner@example.org")
    clock.advance(days=15)
    assert_problem(idle.get("/api/v1/me"), 401)


def test_list_and_revoke_own_sessions(app: FastAPI) -> None:
    laptop = user(app, "learner@example.org")
    phone = login(app, "learner@example.org")
    sessions = laptop.get("/api/v1/me/sessions").json()
    assert len(sessions) == 2
    other = next(s for s in sessions if not s["current"])
    assert laptop.delete(f"/api/v1/me/sessions/{other['id']}").status_code == 204
    assert_problem(phone.get("/api/v1/me"), 401)
    assert_problem(laptop.delete(f"/api/v1/me/sessions/{other['id']}"), 404)


# -- personal access tokens ---


def test_pat_scopes_and_revocation(app: FastAPI, clock: Clock) -> None:
    c = user(app, "learner@example.org")
    r = c.post("/api/v1/me/tokens", json={"name": "ci", "scopes": ["read:progress"]})
    assert r.status_code == 201
    secret = r.json()["token"]
    assert secret.startswith("rcp_") and r.json()["prefix"] == secret[:10]
    assert "token" not in c.get("/api/v1/me/tokens").json()[0]

    bot = client_for(app)
    bot.headers["Authorization"] = f"Bearer {secret}"
    assert bot.get("/api/v1/progress/status").status_code == 200
    assert (
        "scope"
        in assert_problem(bot.post("/api/v1/progress/start", json={"lesson_id": VECTORS}), 403)[
            "detail"
        ]
    )
    assert_problem(bot.get("/api/v1/me/tokens"), 403)  # tokens cannot manage tokens
    assert_problem(
        bot.post("/api/v1/me/tokens", json={"name": "x", "scopes": ["write:progress"]}), 403
    )

    w = c.post(
        "/api/v1/me/tokens", json={"name": "rw", "scopes": ["write:progress", "read:progress"]}
    )
    writer = client_for(app)
    writer.headers["Authorization"] = f"Bearer {w.json()['token']}"
    assert writer.post("/api/v1/progress/start", json={"lesson_id": VECTORS}).status_code == 201

    token_id = r.json()["id"]
    assert c.delete(f"/api/v1/me/tokens/{token_id}").status_code == 204
    assert_problem(bot.get("/api/v1/progress/status"), 401)
    assert_problem(c.delete(f"/api/v1/me/tokens/{token_id}"), 404)

    short = c.post(
        "/api/v1/me/tokens", json={"name": "s", "scopes": ["read:progress"], "expires_in_days": 1}
    )
    temp = client_for(app)
    temp.headers["Authorization"] = f"Bearer {short.json()['token']}"
    assert temp.get("/api/v1/me").status_code == 200
    clock.advance(days=1, seconds=1)
    assert_problem(temp.get("/api/v1/me"), 401)
    assert {"auth.token.created", "auth.token.revoked"} <= set(audit_actions(app))


def test_bad_authorization_headers(anon: TestClient) -> None:
    assert_problem(anon.get("/api/v1/me", headers={"Authorization": "Basic YTpi"}), 401)
    assert_problem(anon.get("/api/v1/me", headers={"Authorization": "Bearer "}), 401)
    assert_problem(anon.get("/api/v1/me", headers={"Authorization": "Bearer rcp_nope"}), 401)
    assert_problem(anon.get("/api/v1/me", headers={"Authorization": "Bearer nope"}), 401)


def test_learner_cannot_mint_admin_token(app: FastAPI) -> None:
    c = user(app, "learner@example.org")
    r = c.post("/api/v1/me/tokens", json={"name": "x", "scopes": ["admin"]})
    assert_problem(r, 403)
    assert_problem(c.post("/api/v1/me/tokens", json={"name": "x", "scopes": []}), 422)


def test_admin_endpoints_need_admin_scope_on_tokens(app: FastAPI) -> None:
    admin = user(app, ADMIN)
    read = admin.post("/api/v1/me/tokens", json={"name": "r", "scopes": ["read:progress"]})
    full = admin.post("/api/v1/me/tokens", json={"name": "a", "scopes": ["admin", "read:progress"]})
    for secret, status in ((read.json()["token"], 403), (full.json()["token"], 200)):
        bot = client_for(app)
        bot.headers["Authorization"] = f"Bearer {secret}"
        assert bot.get("/api/v1/admin/users").status_code == status


# -- per-user isolation (AC-AUTH.5) ---


def test_progress_is_isolated_between_users(app: FastAPI) -> None:
    alice = user(app, "alice@example.org")
    bob = user(app, "bob@example.org")
    assert (
        alice.post("/api/v1/progress/log", json={"lesson_id": VECTORS, "minutes": 30}).status_code
        == 201
    )
    assert alice.post("/api/v1/progress/start", json={"lesson_id": VECTORS}).status_code == 201

    status = bob.get("/api/v1/progress/status").json()
    assert status["open_session"] is None
    assert all(row["total_seconds"] == 0 for row in status["lessons"])
    assert bob.get(f"/api/v1/progress/lessons/{VECTORS}").json()["status"] == "not_started"
    assert bob.post("/api/v1/progress/start", json={"lesson_id": VECTORS}).status_code == 201

    a_export = alice.get("/api/v1/me/export").json()
    b_export = bob.get("/api/v1/me/export").json()
    alice_id = alice.get("/api/v1/me").json()["id"]
    assert {p["user_id"] for p in a_export["lesson_progress"]} == {alice_id}
    assert all(s["user_id"] != alice_id for s in b_export["sessions"])
    report = bob.get("/api/v1/reports/weekly", params={"week": "2026-W46"}).json()
    assert report["summary"]["total_seconds"] == 0

    alice_session = alice.get("/api/v1/me/sessions").json()[0]["id"]
    assert_problem(bob.delete(f"/api/v1/me/sessions/{alice_session}"), 404)
    tok = alice.post("/api/v1/me/tokens", json={"name": "t", "scopes": ["read:progress"]}).json()
    assert_problem(bob.delete(f"/api/v1/me/tokens/{tok['id']}"), 404)
    assert "data.exported" in audit_actions(app)


# -- role matrix (AC-AUTH.4) ---

MATRIX = [
    # method, path, anonymous, learner, author, admin
    ("GET", "/api/v1/auth/providers", 200, 200, 200, 200),
    ("GET", "/api/v1/courses", 401, 200, 200, 200),
    ("GET", "/api/v1/progress/status", 401, 200, 200, 200),
    ("POST", "/api/v1/progress/log", 401, 201, 201, 201),
    ("GET", "/api/v1/reports/weekly", 401, 200, 200, 200),
    ("GET", "/api/v1/me", 401, 200, 200, 200),
    ("GET", "/api/v1/me/export", 401, 200, 200, 200),
    ("GET", "/api/v1/admin/users", 401, 403, 403, 200),
    ("GET", "/api/v1/admin/users/{learner}", 401, 403, 403, 200),
    ("PATCH", "/api/v1/admin/users/{learner}", 401, 403, 403, 200),
    ("DELETE", "/api/v1/admin/users/{learner}/sessions", 401, 403, 403, 204),
    ("GET", "/api/v1/admin/audit", 401, 403, 403, 200),
]


@pytest.fixture
def role_clients(app: FastAPI) -> Iterator[dict[str, Any]]:
    admin = user(app, ADMIN)
    learner = user(app, "learner@example.org")
    author = user(app, "author@example.org")
    author_id = author.get("/api/v1/me").json()["id"]
    assert (
        admin.patch(f"/api/v1/admin/users/{author_id}", json={"role": "author"}).status_code == 200
    )
    yield {
        "anonymous": client_for(app),
        "learner": learner,
        "author": author,
        "admin": admin,
        "learner_id": learner.get("/api/v1/me").json()["id"],
    }


@pytest.mark.parametrize(("method", "path", *("anonymous", "learner", "author", "admin")), MATRIX)
def test_role_matrix(
    role_clients: dict[str, Any],
    method: str,
    path: str,
    anonymous: int,
    learner: int,
    author: int,
    admin: int,
) -> None:
    url = path.format(learner=role_clients["learner_id"])
    body: dict[str, Any] | None = None
    if url.endswith("/progress/log"):
        body = {"lesson_id": VECTORS, "minutes": 5}
    elif method == "PATCH":
        body = {"role": "learner"}
    for role, expected in (
        ("anonymous", anonymous),
        ("learner", learner),
        ("author", author),
        ("admin", admin),
    ):
        r = role_clients[role].request(method, url, json=body)
        assert r.status_code == expected, (role, method, url, r.text)


# -- admin rules ---


def test_admin_role_changes_and_last_admin(app: FastAPI) -> None:
    admin = user(app, ADMIN)
    admin_id = admin.get("/api/v1/me").json()["id"]
    learner_id = signup(app, "learner@example.org")["id"]
    r = admin.patch(f"/api/v1/admin/users/{learner_id}", json={"role": "admin"})
    assert r.json()["role"] == "admin"
    assert_problem(admin.patch(f"/api/v1/admin/users/{admin_id}", json={"role": "learner"}), 409)
    second = login(app, "learner@example.org")
    assert (
        second.patch(f"/api/v1/admin/users/{admin_id}", json={"role": "author"}).status_code == 200
    )
    assert_problem(admin.get("/api/v1/admin/users"), 403)  # demoted: privilege takes effect now
    assert_problem(
        second.patch(f"/api/v1/admin/users/{learner_id}", json={"status": "disabled"}), 409
    )
    assert_problem(
        second.patch(f"/api/v1/admin/users/{learner_id}", json={"status": "deleted"}), 422
    )
    assert_problem(second.get("/api/v1/admin/users/999"), 404)
    unchanged = second.patch(f"/api/v1/admin/users/{admin_id}", json={})
    assert unchanged.json()["role"] == "author"

    page = second.get("/api/v1/admin/users", params={"limit": 1}).json()
    assert len(page["items"]) == 1 and page["next_cursor"] == str(admin_id)
    rest = second.get("/api/v1/admin/users", params={"cursor": page["next_cursor"]}).json()
    assert [u["id"] for u in rest["items"]] == [learner_id]
    assert_problem(second.get("/api/v1/admin/users", params={"cursor": "x"}), 422)

    audit = second.get("/api/v1/admin/audit", params={"limit": 200}).json()["items"]
    changes = [e for e in audit if e["action"] == "user.role.changed"]
    assert {(e["detail"]["from"], e["detail"]["to"]) for e in changes} >= {
        ("learner", "admin"),
        ("admin", "author"),
    }
    assert all(e["request_id"] for e in changes)
    mine = second.get("/api/v1/admin/audit", params={"actor_user_id": learner_id}).json()["items"]
    assert mine and all(e["actor_user_id"] == learner_id for e in mine)


def test_admin_force_logout(app: FastAPI) -> None:
    admin = user(app, ADMIN)
    learner = user(app, "learner@example.org")
    learner_id = learner.get("/api/v1/me").json()["id"]
    assert admin.delete(f"/api/v1/admin/users/{learner_id}/sessions").status_code == 204
    assert_problem(learner.get("/api/v1/me"), 401)
    assert "auth.sessions.revoked_by_admin" in audit_actions(app)


# -- profile / passwords ---


def test_profile_and_password_change(app: FastAPI) -> None:
    c = user(app, "learner@example.org")
    other = login(app, "learner@example.org")
    r = c.patch("/api/v1/me", json={"display_name": "Kim", "timezone": "Asia/Seoul"})
    assert r.json()["display_name"] == "Kim" and r.json()["timezone"] == "Asia/Seoul"
    assert c.patch("/api/v1/me", json={}).json()["display_name"] == "Kim"
    bad = c.put(
        "/api/v1/me/password", json={"current_password": "nope" * 3, "new_password": "x" * 20}
    )
    assert_problem(bad, 401)
    new = "a brand new passphrase"
    assert (
        c.put(
            "/api/v1/me/password", json={"current_password": PASSWORD, "new_password": new}
        ).status_code
        == 204
    )
    assert c.get("/api/v1/me").status_code == 200  # current session kept
    assert_problem(other.get("/api/v1/me"), 401)  # other sessions ended
    login(app, "learner@example.org", new)
    assert_problem(
        c.put("/api/v1/me/password", json={"current_password": new, "new_password": "short"}), 422
    )


def test_password_reset_flow(app: FastAPI, mailer: FakeMailer, clock: Clock) -> None:
    signup(app, "learner@example.org")
    session = login(app, "learner@example.org")
    anon = client_for(app)
    sent = len(mailer.outbox)
    assert (
        anon.post("/api/v1/auth/password/forgot", json={"email": "nobody@example.org"}).status_code
        == 202
    )
    assert len(mailer.outbox) == sent  # same answer, no mail: no account enumeration
    assert (
        anon.post("/api/v1/auth/password/forgot", json={"email": "learner@example.org"}).status_code
        == 202
    )
    mail: Mail = mailer.outbox[-1]
    assert mail.to == "learner@example.org" and "30분" in mail.body
    token = re.search(r"token=(\S+)", mail.body)
    assert token
    new = "another long passphrase"
    assert (
        anon.post(
            "/api/v1/auth/password/reset", json={"token": token[1], "password": new}
        ).status_code
        == 204
    )
    assert_problem(session.get("/api/v1/me"), 401)  # all sessions ended
    login(app, "learner@example.org", new)
    assert_problem(
        anon.post(
            "/api/v1/auth/login", json={"email": "learner@example.org", "password": PASSWORD}
        ),
        401,
    )
    assert_problem(
        anon.post("/api/v1/auth/password/reset", json={"token": token[1], "password": new}), 422
    )

    anon.post("/api/v1/auth/password/forgot", json={"email": "learner@example.org"})
    late = re.search(r"token=(\S+)", mailer.outbox[-1].body)
    assert late
    clock.advance(minutes=31)
    assert_problem(
        anon.post("/api/v1/auth/password/reset", json={"token": late[1], "password": new}), 422
    )


def test_password_reset_disabled_without_mail(settings: Settings) -> None:
    app = create_app(settings, mailer=None)
    r = client_for(app).post("/api/v1/auth/password/forgot", json={"email": "a@b.co"})
    assert "mail is not configured" in assert_problem(r, 503)["detail"]


# -- account deletion / audit retention (AC-AUTH.6) ---


def test_delete_account_erases_learning_data(app: FastAPI, settings: Settings) -> None:
    user(app, ADMIN)  # keeps a second admin out of the way
    c = user(app, "learner@example.org")
    learner_id = c.get("/api/v1/me").json()["id"]
    other = user(app, "other@example.org")
    c.post("/api/v1/progress/log", json={"lesson_id": VECTORS, "minutes": 30})
    other.post("/api/v1/progress/log", json={"lesson_id": VECTORS, "minutes": 10})
    assert_problem(c.request("DELETE", "/api/v1/me", json={"password": "wrong" * 3}), 401)
    assert c.request("DELETE", "/api/v1/me", json={"password": PASSWORD}).status_code == 204
    assert_problem(c.get("/api/v1/me"), 401)
    assert_problem(
        client_for(app).post(
            "/api/v1/auth/login", json={"email": "learner@example.org", "password": PASSWORD}
        ),
        401,
    )
    with sqlite3.connect(settings.data_dir / "progress.db") as db:
        users_left = {r[0] for r in db.execute("SELECT DISTINCT user_id FROM sessions")}
    assert learner_id not in users_left and users_left
    erased = auth_service(app).store.get_user(learner_id)
    assert erased is not None
    assert erased.email == f"deleted-{learner_id}@invalid" and erased.status == "deleted"
    assert "account.deleted" in audit_actions(app)
    # the email is free again
    signup(app, "learner@example.org")


def test_delete_account_guards(app: FastAPI) -> None:
    admin = user(app, ADMIN)
    assert_problem(admin.request("DELETE", "/api/v1/me", json={"password": PASSWORD}), 409)


def test_audit_retention_anonymizes(app: FastAPI, clock: Clock) -> None:
    user(app, "learner@example.org")
    service = auth_service(app)
    clock.advance(days=91)
    service.store.audit("recent", clock(), actor_user_id=1, actor_ip="10.0.0.1")
    assert service.purge_audit() >= 2
    entries = service.list_audit(100)
    old = [e for e in entries if e.action != "recent"]
    assert all(e.actor_user_id is None and e.actor_ip is None for e in old)
    recent = next(e for e in entries if e.action == "recent")
    assert recent.actor_user_id == 1


# -- headers / readiness ---


def test_security_headers(anon: TestClient) -> None:
    r = anon.get("/healthz")
    assert r.headers["content-security-policy"].startswith("default-src 'none'")
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"
    assert r.headers["referrer-policy"] == "no-referrer"
    assert "max-age=31536000" in r.headers["strict-transport-security"]
    assert "cdn.jsdelivr.net" in anon.get("/docs").headers["content-security-policy"]
    assert anon.get("/api/v1/me").headers["cache-control"] == "no-store"


def test_readyz_reports_missing_auth_tables(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = create_app(settings, mailer=None)
    monkeypatch.setattr(SqlAuthStore, "schema_ready", lambda self: False)
    r = client_for(app).get("/readyz")
    assert r.status_code == 503
    assert "alembic" in r.json()["checks"]["database"]["detail"]


def test_unconfigured_oidc_provider_is_404(anon: TestClient) -> None:
    assert_problem(anon.get("/api/v1/auth/oidc/google/start"), 404)
    assert_problem(anon.get("/api/v1/auth/oidc/google/callback"), 404)


# -- config / mailer ---


def test_auth_config_from_env() -> None:
    cfg = AuthConfig.from_env(
        {
            "RC_AUTH_SESSION_DAYS": "7",
            "RC_AUTH_AUDIT_RETENTION_DAYS": "30",
            "RC_AUTH_ALLOW_SIGNUP": "0",
            "RC_AUTH_ADMIN_EMAIL": "Boss@Example.org",
            "RC_PUBLIC_URL": "https://rc.example.org",
            "RC_AUTH_PEPPER": "p",
        }
    )
    assert cfg.session_idle == timedelta(days=7)
    assert cfg.audit_retention == timedelta(days=30)
    assert not cfg.allow_signup
    assert cfg.bootstrap_admin_email == "boss@example.org"
    assert cfg.public_url == "https://rc.example.org" and cfg.pepper == "p"
    assert AuthConfig.from_env({}) == AuthConfig()


def test_smtp_mailer() -> None:
    assert SmtpConfig.from_env({}) is None
    cfg = SmtpConfig.from_env(
        {
            "RC_SMTP_HOST": "mail.example.org",
            "RC_SMTP_PORT": "2525",
            "RC_SMTP_USER": "u",
            "RC_SMTP_PASSWORD": "p",
            "RC_SMTP_FROM": "rc@example.org",
        }
    )
    assert cfg is not None and cfg.port == 2525
    calls: list[tuple[str, Any]] = []

    class FakeSMTP:
        def __init__(self, host: str, port: int, timeout: int) -> None:
            calls.append(("connect", (host, port)))

        def __enter__(self) -> FakeSMTP:
            return self

        def __exit__(self, *exc: object) -> None:
            calls.append(("quit", None))

        def starttls(self, context: object) -> None:
            calls.append(("starttls", None))

        def login(self, user: str, password: str) -> None:
            calls.append(("login", user))

        def send_message(self, message: Any) -> None:
            calls.append(("send", message["To"]))

    SmtpMailer(cfg, smtp=FakeSMTP).send(Mail("to@example.org", "s", "b"))  # type: ignore[arg-type]
    assert [c[0] for c in calls] == ["connect", "starttls", "login", "send", "quit"]


def test_service_context_defaults() -> None:
    store = SqlAuthStore.from_url("sqlite://")
    service = AuthService(store, mailer=None)
    created = service.signup("x@example.org", PASSWORD, Context())
    assert created.id == 1
    assert not service.mail_enabled
    store.close()

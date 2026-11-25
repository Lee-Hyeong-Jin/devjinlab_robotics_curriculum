# ruff: noqa: F811
# Fixtures are imported from test_auth and requested by name, which ruff sees as redefinitions.
"""Regression tests for the web QA pass of 2026-11-23 (the API side of each finding).

Each test names the finding it pins down. The web side is covered in ``web/src`` unit tests
and ``web/e2e/journey.spec.ts``.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlsplit

import pytest
import yaml
from fastapi import FastAPI
from fastapi.testclient import TestClient

from robotics_curriculum.auth.mailer import FakeMailer
from robotics_curriculum.timezone import is_timezone
from test_auth import (  # noqa: F401  (fixtures are used by name)
    ADMIN,
    PASSWORD,
    Clock,
    anon,
    app,
    assert_problem,
    client_for,
    clock,
    fast_argon2,
    login,
    mailer,
    settings,
    signup,
    user,
)

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "robotics_curriculum"
WEB_APP = ROOT / "web" / "src" / "app"


def _mail_link(mailer: FakeMailer) -> str:
    match = re.search(r"https?://\S+", mailer.outbox[-1].body)
    assert match is not None, mailer.outbox[-1].body
    return match.group(0)


def _web_route_exists(path: str) -> bool:
    return (WEB_APP / path.strip("/") / "page.tsx").is_file()


# -- B-02: the reset mail pointed at a page that does not exist --------------------------------


def test_b02_reset_mail_links_to_a_page_the_web_has(app: FastAPI, mailer: FakeMailer) -> None:
    signup(app, "reader@example.org")
    r = client_for(app).post("/api/v1/auth/password/forgot", json={"email": "reader@example.org"})
    assert r.status_code == 202, r.text
    link = urlsplit(_mail_link(mailer))
    assert link.path == "/password/reset"
    assert link.query.startswith("token=")
    assert _web_route_exists(link.path), "the mailed link has to open a real screen"


def test_b02_every_mailed_link_has_a_screen(app: FastAPI, mailer: FakeMailer) -> None:
    """The verification mail and the operator-sent reset mail, too."""
    signup(app, "reader@example.org", verify=False)
    assert _web_route_exists(urlsplit(_mail_link(mailer)).path)
    admin = user(app, ADMIN)
    reader_id = next(
        row["id"]
        for row in admin.get("/api/v1/admin/users").json()["items"]
        if row["email"] == "reader@example.org"
    )
    r = admin.post(f"/api/v1/admin/users/{reader_id}/password-reset")
    # Accepted with no body at all: a client must not try to parse one (B-08).
    assert (r.status_code, r.content) == (202, b"")
    assert urlsplit(_mail_link(mailer)).path == "/password/reset"


# -- B-03: any string was stored as a time zone -------------------------------------------------


@pytest.mark.parametrize("zone", ["Mars/Phobos", "KST", "+09:00", "../etc/passwd", " Asia/Seoul"])
def test_b03_an_unknown_time_zone_is_refused(app: FastAPI, zone: str) -> None:
    c = user(app, "reader@example.org")
    body = assert_problem(c.patch("/api/v1/me", json={"timezone": zone}), 422)
    assert body["code"] == "invalid_timezone"
    assert c.get("/api/v1/me").json()["timezone"] is None


def test_b03_real_zones_are_kept_and_can_be_cleared(app: FastAPI) -> None:
    c = user(app, "reader@example.org")
    assert c.patch("/api/v1/me", json={"timezone": "America/New_York"}).json()["timezone"] == (
        "America/New_York"
    )
    assert c.patch("/api/v1/me", json={"timezone": None}).json()["timezone"] is None
    assert is_timezone("Asia/Seoul") and is_timezone("UTC")
    assert not is_timezone("") and not is_timezone("Mars/Phobos")


# -- B-05, B-12: refusals carry a code and are written in the reader's language ---------------


def test_b05_a_wrong_current_password_says_so(app: FastAPI) -> None:
    c = user(app, "reader@example.org")
    r = c.put(
        "/api/v1/me/password?lang=ko",
        json={"current_password": "not-my-password-1", "new_password": "another-long-pass-2"},
    )
    body = assert_problem(r, 401)
    # The code is what tells this apart from "your session has ended", which is also a 401.
    assert body["code"] == "wrong_current_password"
    assert body["detail"] == "현재 비밀번호가 올바르지 않습니다."
    assert c.get("/api/v1/me").status_code == 200  # still signed in


def test_b12_login_refusals_follow_the_request_language(app: FastAPI) -> None:
    signup(app, "reader@example.org")
    wrong = {"email": "reader@example.org", "password": "wrong-password-123"}
    c = client_for(app)
    korean = assert_problem(c.post("/api/v1/auth/login?lang=ko", json=wrong), 401)
    assert (korean["code"], korean["detail"]) == (
        "invalid_credentials",
        "이메일 또는 비밀번호가 올바르지 않습니다.",
    )
    # English is what a request that names no language gets.
    english = assert_problem(c.post("/api/v1/auth/login", json=wrong), 401)
    assert (english["code"], english["detail"]) == (
        "invalid_credentials",
        "Invalid email or password.",
    )
    header = c.post("/api/v1/auth/login", json=wrong, headers={"Accept-Language": "ko"})
    assert assert_problem(header, 401)["detail"] == "이메일 또는 비밀번호가 올바르지 않습니다."


def test_b12_other_refusals_are_localized(app: FastAPI, mailer: FakeMailer) -> None:
    signup(app, "reader@example.org")
    c = client_for(app)
    taken = c.post(
        "/api/v1/auth/signup?lang=ko", json={"email": "Reader@Example.org", "password": PASSWORD}
    )
    assert assert_problem(taken, 409)["detail"] == "이미 가입된 이메일입니다."
    token = c.post("/api/v1/auth/verify-email?lang=ko", json={"token": "nope"})
    body = assert_problem(token, 422)
    assert (body["code"], body["detail"]) == (
        "invalid_token",
        "토큰이 올바르지 않거나 만료됐습니다.",
    )
    for _ in range(5):
        c.post("/api/v1/auth/login", json={"email": "reader@example.org", "password": "x" * 12})
    locked = c.post("/api/v1/auth/login", json={"email": "reader@example.org", "password": "x"})
    assert assert_problem(locked, 429)["code"] == "login_throttled"
    admin = user(app, ADMIN)
    me = admin.get("/api/v1/me").json()["id"]
    own = assert_problem(
        admin.patch(f"/api/v1/admin/users/{me}?lang=ko", json={"role": "learner"}), 409
    )
    assert own["detail"] == "자기 자신의 관리자 권한은 내릴 수 없습니다."


def test_b12_every_error_code_has_a_sentence_in_both_languages() -> None:
    """A code without a catalogue entry would fall back to English on a Korean screen."""
    codes: set[str] = set()
    for path in (SRC / "auth").glob("*.py"):
        codes.update(re.findall(r'code="([a-z_]+)"', path.read_text("utf-8")))
        codes.update(re.findall(r'"(password_(?:too|contains)_[a-z]+)"', path.read_text("utf-8")))
    assert {"invalid_credentials", "wrong_current_password", "password_too_short"} <= codes
    for lang in ("ko", "en"):
        catalog = yaml.safe_load((SRC / "i18n" / "locales" / f"{lang}.yaml").read_text("utf-8"))
        missing = sorted(codes - set(catalog["api"]["auth"]))
        assert missing == [], f"{lang}: no sentence for {missing}"


# -- B-14: "keep me signed in" did nothing ------------------------------------------------------


def _session_cookie(response: object) -> str:
    headers = response.headers.get_list("set-cookie")  # type: ignore[attr-defined]
    return next(value for value in headers if value.startswith("sid="))


def test_b14_remember_decides_whether_the_cookie_outlives_the_browser(app: FastAPI) -> None:
    signup(app, "reader@example.org")
    body = {"email": "reader@example.org", "password": PASSWORD}
    kept = _session_cookie(
        client_for(app).post("/api/v1/auth/login", json={**body, "remember": True})
    )
    assert "Max-Age=1209600" in kept  # the 14-day idle window
    plain = client_for(app).post("/api/v1/auth/login", json=body)
    for cookie in plain.headers.get_list("set-cookie"):
        # No Max-Age and no Expires: the cookie ends when the browser is closed.
        assert "max-age" not in cookie.lower() and "expires" not in cookie.lower(), cookie
    assert "HttpOnly" in _session_cookie(plain)


# -- B-33: the CSV opened as mojibake in Excel --------------------------------------------------


def test_b33_the_audit_csv_starts_with_a_byte_order_mark(app: FastAPI) -> None:
    admin = user(app, ADMIN)
    r = admin.get("/api/v1/admin/audit/export")
    assert r.status_code == 200
    assert r.content.startswith(b"\xef\xbb\xbf")
    assert r.content[3:].startswith(b"id,at,action,")


# -- B-09: the container's own health check was counted as visits ------------------------------


def test_b09_the_web_health_check_does_not_request_a_page() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text("utf-8")
    web_stage = dockerfile[dockerfile.index("AS web\n") :]
    check = web_stage[web_stage.index("HEALTHCHECK") : web_stage.index("CMD [")]
    assert "/healthz" in check
    assert (WEB_APP / "healthz" / "route.ts").is_file()


# -- QA follow-up: "visit to sign-up 200%" -----------------------------------------------------


def test_a_signup_ratio_above_one_hundred_percent_is_not_reported(app: FastAPI) -> None:
    """Two sign-ups against one counted visitor is missing visit data, not a 200% conversion."""
    admin = user(app, ADMIN)
    signup(app, "second@example.org")
    web = TestClient(app, base_url="https://testserver", client=("127.0.0.1", 50000))
    r = web.post(
        "/api/v1/telemetry/pageview",
        json={"path": "/"},
        headers={"X-Forwarded-For": "198.51.100.7", "User-Agent": "Mozilla/5.0 Chrome/130"},
    )
    assert r.status_code == 204
    growth = admin.get("/api/v1/admin/monitoring/kpi").json()["growth"]
    assert growth["visitor_days_30d"] == 1
    assert growth["visit_to_signup"] is None

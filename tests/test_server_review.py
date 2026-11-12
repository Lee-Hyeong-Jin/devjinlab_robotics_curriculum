"""Reproductions for docs/reviews/2026-11-11-server-review.md.

Each test asserts the behaviour the acceptance criteria ask for (PRD appendix C.3) and is
marked ``xfail(strict=True)`` while the finding is open, so the gate stays green. When a fix
lands the test XPASSes, strict mode turns that into a failure, and the fixer drops the marker:
the test is then the regression test the engineering rules require. IDs (SRV-xx) match the
review table.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi.testclient import TestClient

from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.settings import Settings
from robotics_curriculum.auth.mailer import Mail

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = Path(__file__).parent / "fixtures" / "curriculum"
COMPOSE = ROOT / "docker-compose.yml"
# Passwords avoid each account's email local part (the policy forbids it).
PASSWORD = "Tr0mbone-Harbor-42"


def _open(reason: str) -> pytest.MarkDecorator:
    return pytest.mark.xfail(strict=True, reason=f"open finding {reason}")


@dataclass
class StubMailer:
    """Collects mail instead of sending it, so token flows are inspectable."""

    sent: list[Mail] = field(default_factory=list)

    def send(self, mail: Mail) -> None:
        self.sent.append(mail)

    def tokens(self) -> list[str]:
        return [m.body.split("token=")[1].split("\n")[0] for m in self.sent]


def _client(
    tmp_path: Path, env: dict[str, str] | None = None, mailer: Any = None, *, server: bool = True
) -> TestClient:
    settings = Settings.from_env(
        {
            "RC_AUTH_MODE": "server" if server else "local",
            "RC_CURRICULUM_DIR": str(FIXTURE),
            "RC_DATA_DIR": str(tmp_path / "data"),
            "RC_AUTH_COOKIE_SECURE": "0",
            **(env or {}),
        }
    )
    return TestClient(create_app(settings, mailer=mailer))


def _signup(client: TestClient, email: str, password: str = PASSWORD) -> Any:
    return client.post("/api/v1/auth/signup", json={"email": email, "password": password})


# -- SRV-01: the shipped deployment runs without authentication ------------------------


def _compose_service(name: str) -> dict[str, Any]:
    data = yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))
    return dict(data["services"][name])


def test_srv01_local_mode_grants_admin_without_credentials(tmp_path: Path) -> None:
    """Not a defect by itself: local mode is documented. It is what SRV-01 exposes."""
    client = _client(tmp_path, server=False)
    me = client.get("/api/v1/me")
    assert me.status_code == 200
    assert me.json()["role"] == "admin"
    write = client.post(
        "/api/v1/progress/log", json={"lesson_id": "m1-vectors-matrices", "minutes": 42}
    )
    assert write.status_code == 201, write.text


def test_srv01_compose_api_runs_in_server_mode() -> None:
    env = _compose_service("api").get("environment", {})
    assert env.get("RC_AUTH_MODE") == "server", (
        "the api service binds 0.0.0.0 inside the container and would serve every request "
        f"as an unauthenticated admin; environment={env}"
    )


def test_compose_passes_the_public_content_settings_to_api_and_web() -> None:
    """Both services need both values, or publishing half-works (ADR 0016, RUNBOOK §8.2).

    This shipped broken: `RC_PUBLIC_CONTENT` reached neither service and the web had no
    `RC_PUBLIC_URL`, so turning the flag on in `.env` did nothing and the canonical links and
    sitemap pointed at `localhost`. The api decides what it serves; the web decides what may
    be indexed and what address every canonical link, hreflang alternate and sitemap entry
    uses. One without the other leaves the two disagreeing.
    """
    for service in ("api", "web"):
        env = _compose_service(service).get("environment", {})
        for name in ("RC_PUBLIC_CONTENT", "RC_PUBLIC_URL"):
            assert name in env, f"the {service} service does not receive {name}: {sorted(env)}"
        # Off unless the deployment asks: publishing is a deliberate decision.
        assert env["RC_PUBLIC_CONTENT"] == "${RC_PUBLIC_CONTENT:-0}", env["RC_PUBLIC_CONTENT"]
        assert env["RC_PUBLIC_URL"].startswith("${RC_PUBLIC_URL:-"), env["RC_PUBLIC_URL"]


def test_compose_gives_api_and_web_the_same_public_url() -> None:
    """A different default on each side would make canonical links disagree with the API."""
    api = _compose_service("api")["environment"]["RC_PUBLIC_URL"]
    web = _compose_service("web")["environment"]["RC_PUBLIC_URL"]
    assert api == web, f"api={api!r} web={web!r}"


# -- SRV-02: anyone can claim the bootstrap admin address ------------------------------


def test_srv02_bootstrap_admin_requires_verified_owner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # AuthConfig reads os.environ directly, so the variable has to be set there.
    monkeypatch.setenv("RC_AUTH_ADMIN_EMAIL", "owner@example.com")
    client = _client(tmp_path)
    created = _signup(client, "owner@example.com")
    assert created.status_code == 201, created.text
    assert created.json()["email_verified"] is False
    assert created.json()["role"] == "learner", "admin granted before the mailbox was proven"
    login = client.post(
        "/api/v1/auth/login", json={"email": "owner@example.com", "password": PASSWORD}
    )
    assert login.status_code == 200, login.text
    assert client.get("/api/v1/admin/users").status_code == 403


# -- SRV-03 / SRV-04: password reset ---------------------------------------------------


def test_srv03_forgot_password_is_rate_limited(tmp_path: Path) -> None:
    mailer = StubMailer()
    client = _client(tmp_path, mailer=mailer)
    assert _signup(client, "victim@example.com").status_code == 201
    mailer.sent.clear()
    codes = [
        client.post(
            "/api/v1/auth/password/forgot", json={"email": "victim@example.com"}
        ).status_code
        for _ in range(12)
    ]
    assert 429 in codes, (
        f"12 reset requests all accepted ({sorted(set(codes))}), mails sent: {len(mailer.sent)}"
    )


def test_srv04_new_reset_token_invalidates_the_previous_one(tmp_path: Path) -> None:
    mailer = StubMailer()
    client = _client(tmp_path, mailer=mailer)
    assert _signup(client, "victim@example.com").status_code == 201
    mailer.sent.clear()
    for _ in range(2):
        client.post("/api/v1/auth/password/forgot", json={"email": "victim@example.com"})
    first, second = mailer.tokens()[0], mailer.tokens()[1]
    assert first != second
    used = client.post(
        "/api/v1/auth/password/reset", json={"token": second, "password": "Quartz-Lantern-91"}
    )
    assert used.status_code == 204, used.text
    stale = client.post(
        "/api/v1/auth/password/reset", json={"token": first, "password": "Quartz-Lantern-82"}
    )
    assert stale.status_code == 422, "the superseded token still reset the password"


# -- SRV-05: error bodies name server paths --------------------------------------------


def test_srv05_readyz_does_not_leak_filesystem_paths(tmp_path: Path) -> None:
    client = _client(tmp_path, {"RC_CURRICULUM_DIR": str(tmp_path / "missing")}, server=False)
    ready = client.get("/readyz")
    assert ready.status_code == 503
    body = ready.text
    courses = client.get("/api/v1/courses").text
    for text, where in ((body, "/readyz"), (courses, "GET /api/v1/courses")):
        assert str(tmp_path) not in text, f"{where} exposes a server path: {text[:200]}"


# -- SRV-06 / SRV-09: compose secrets and container hardening --------------------------


def test_srv06_compose_has_no_default_secrets() -> None:
    text = COMPOSE.read_text(encoding="utf-8")
    assert "rc-dev-only" not in text
    assert "${RC_DB_PASSWORD:?" in text and "${RC_AUTH_SECRET:?" in text


def test_srv09_api_container_is_hardened() -> None:
    for name in ("api", "migrate"):
        service = _compose_service(name)
        assert service.get("read_only") is True, name
        assert service.get("cap_drop") == ["ALL"], name
        assert "no-new-privileges:true" in service.get("security_opt", []), name
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "HEALTHCHECK" in dockerfile and "RC_AUTH_MODE=server" in dockerfile

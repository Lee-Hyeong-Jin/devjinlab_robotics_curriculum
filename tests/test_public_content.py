"""Anonymous read-only access to the curriculum (ADR 0016, `RC_PUBLIC_CONTENT`).

The point of these tests is the boundary: with the flag on, the curriculum is readable
without a session and *nothing else is*. Every endpoint that touches a person's data must
still answer 401.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from argon2 import PasswordHasher
from fastapi import FastAPI
from fastapi.testclient import TestClient

import robotics_curriculum.auth.crypto as crypto
from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.settings import Settings
from robotics_curriculum.auth.mailer import FakeMailer

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "tests" / "fixtures" / "curriculum"
COURSE = "sample-course"
MODULE = "m1-math-physics"
VECTORS = "m1-vectors-matrices"
PASSWORD = "correct horse battery staple"

#: Everything the curriculum is made of: readable by anyone when the flag is on.
PUBLIC_PATHS = (
    "/api/v1/courses",
    f"/api/v1/courses/{COURSE}",
    f"/api/v1/modules/{MODULE}",
    f"/api/v1/lessons/{VECTORS}",
    "/api/v1/resources",
    "/api/v1/search?q=vector",
)

#: A person's own data, or an operator's. Never readable without a session.
PRIVATE_PATHS = (
    "/api/v1/roadmap",
    "/api/v1/progress/status",
    "/api/v1/progress/lessons",
    f"/api/v1/progress/lessons/{VECTORS}",
    "/api/v1/progress/next",
    "/api/v1/reports/weekly",
    f"/api/v1/reports/modules/{MODULE}",
    "/api/v1/review/due",
    f"/api/v1/lessons/{VECTORS}/quiz",
    "/api/v1/me",
    "/api/v1/me/sessions",
    "/api/v1/me/tokens",
    "/api/v1/me/export",
    "/api/v1/admin/users",
    "/api/v1/admin/audit",
)


@pytest.fixture(autouse=True)
def fast_argon2(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        crypto, "_HASHER", PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)
    )


def build(tmp_path: Path, *, public: bool) -> FastAPI:
    return create_app(
        Settings(
            curriculum_dir=CURRICULUM,
            data_dir=tmp_path,
            auth_mode="server",
            public_content=public,
        ),
        mailer=FakeMailer(),
    )


def anon(app: FastAPI) -> TestClient:
    return TestClient(app, base_url="https://testserver")


def test_the_curriculum_is_readable_without_a_session(tmp_path: Path) -> None:
    client = anon(build(tmp_path, public=True))
    for path in PUBLIC_PATHS:
        assert client.get(path).status_code == 200, path


def test_nothing_personal_is_readable_without_a_session(tmp_path: Path) -> None:
    """The whole point of the flag: it opens the curriculum and only the curriculum."""
    client = anon(build(tmp_path, public=True))
    for path in PRIVATE_PATHS:
        assert client.get(path).status_code == 401, path


def test_writes_still_need_a_session(tmp_path: Path) -> None:
    client = anon(build(tmp_path, public=True))
    assert (
        client.post("/api/v1/progress/log", json={"lesson_id": VECTORS, "minutes": 5}).status_code
        == 401
    )
    assert (
        client.post("/api/v1/quiz/runs", json={"lesson_id": VECTORS, "answers": {}}).status_code
        == 401
    )
    assert client.post("/api/v1/progress/done", json={"lesson_id": VECTORS}).status_code == 401


def test_the_flag_is_off_by_default(tmp_path: Path) -> None:
    """A deployment keeps its current behaviour until it decides to publish."""
    client = anon(build(tmp_path, public=False))
    for path in PUBLIC_PATHS:
        assert client.get(path).status_code == 401, path


def test_a_signed_in_reader_is_unaffected(tmp_path: Path) -> None:
    app = build(tmp_path, public=True)
    client = anon(app)
    assert (
        client.post(
            "/api/v1/auth/signup", json={"email": "kim@example.org", "password": PASSWORD}
        ).status_code
        == 201
    )
    login = client.post(
        "/api/v1/auth/login", json={"email": "kim@example.org", "password": PASSWORD}
    )
    assert login.status_code == 200
    client.headers["X-CSRF-Token"] = login.json()["csrf_token"]
    for path in (*PUBLIC_PATHS, "/api/v1/roadmap", "/api/v1/progress/status", "/api/v1/me"):
        assert client.get(path).status_code == 200, path


def test_a_bad_token_is_still_rejected_on_a_public_path(tmp_path: Path) -> None:
    """Anonymous is allowed; *claiming* to be someone with a broken token is not."""
    client = anon(build(tmp_path, public=True))
    r = client.get("/api/v1/courses", headers={"Authorization": "Bearer rcp_nonsense"})
    assert r.status_code == 401
    assert client.get("/api/v1/courses", headers={"Authorization": "Basic abc"}).status_code == 401


def test_local_mode_is_unchanged(tmp_path: Path) -> None:
    app = create_app(
        Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path, auth_mode="local"), mailer=None
    )
    client = anon(app)
    for path in (*PUBLIC_PATHS, "/api/v1/progress/status"):
        assert client.get(path).status_code == 200, path


def test_the_flag_is_read_from_the_environment() -> None:
    base = {"RC_CURRICULUM_DIR": str(CURRICULUM), "RC_DATA_DIR": "/tmp/x"}
    assert Settings.from_env(base).public_content is False
    assert Settings.from_env({**base, "RC_PUBLIC_CONTENT": "0"}).public_content is False
    assert Settings.from_env({**base, "RC_PUBLIC_CONTENT": "1"}).public_content is True

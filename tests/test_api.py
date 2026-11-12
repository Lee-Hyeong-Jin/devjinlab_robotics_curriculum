"""HTTP API (P2-1): every endpoint through TestClient, problem+json errors, OpenAPI snapshot."""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.deps import ContentIndex
from robotics_curriculum.api.log import JsonFormatter, configure_logging, request_id_var
from robotics_curriculum.api.settings import Settings, SettingsError
from robotics_curriculum.cli import app as cli_app
from robotics_curriculum.content import load_courses
from robotics_curriculum.i18n import translator
from robotics_curriculum.progress import ProgressError

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "tests" / "fixtures" / "curriculum"
SNAPSHOT = ROOT / "tests" / "snapshots" / "openapi.json"
DESIGN_DOC = ROOT / "docs" / "api" / "openapi.yaml"
COURSE = "sample-course"
VECTORS = "m1-vectors-matrices"
ROTATION = "m1-rotation-representations"
DH = "m2-dh-parameters"
PROBLEM = "application/problem+json"
T0 = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)


class Clock:
    def __init__(self) -> None:
        self.now = T0

    def __call__(self) -> datetime:
        return self.now


@pytest.fixture
def clock() -> Clock:
    return Clock()


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path / "data")


@pytest.fixture
def client(settings: Settings, clock: Clock) -> TestClient:
    return TestClient(create_app(settings, clock=clock))


def assert_problem(response: Any, status: int) -> dict[str, Any]:
    assert response.status_code == status, response.text
    assert response.headers["content-type"].startswith(PROBLEM)
    body: dict[str, Any] = response.json()
    assert body["status"] == status
    assert body["type"] == "about:blank"
    assert body["request_id"] == response.headers["x-request-id"]
    return body


# -- system ----------------------------------------------------------------------------


def test_healthz_readyz_version(client: TestClient) -> None:
    assert client.get("/healthz").json() == {"status": "ok"}
    ready = client.get("/readyz")
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
    assert ready.json()["checks"]["content"] == {"ok": True, "detail": "3 lessons"}
    assert client.get("/version").json()["version"]


def test_not_ready_when_curriculum_missing(tmp_path: Path) -> None:
    settings = Settings(curriculum_dir=tmp_path / "missing", data_dir=tmp_path / "data")
    client = TestClient(create_app(settings))
    ready = client.get("/readyz")
    assert ready.status_code == 503
    assert ready.json()["status"] == "not_ready"
    assert ready.json()["checks"]["content"]["ok"] is False
    assert ready.json()["checks"]["database"]["ok"] is True
    body = assert_problem(client.get("/api/v1/courses"), 503)
    assert body["detail"] == "curriculum failed to load (see server log)"
    assert str(tmp_path) not in ready.text + body["detail"]  # no server paths


def test_not_ready_when_store_cannot_open(tmp_path: Path) -> None:
    blocker = tmp_path / "file"
    blocker.write_text("not a directory")
    client = TestClient(create_app(Settings(curriculum_dir=CURRICULUM, data_dir=blocker)))
    ready = client.get("/readyz")
    assert ready.status_code == 503
    assert ready.json()["checks"]["database"]["ok"] is False


def test_duplicate_lesson_ids_are_rejected() -> None:
    course = load_courses(CURRICULUM)[0]
    twin = course.model_copy(update={"id": "twin"})
    with pytest.raises(ProgressError, match="globally unique"):
        ContentIndex([course, twin])


# -- content ---------------------------------------------------------------------------


def test_courses_and_course_stages(client: TestClient) -> None:
    courses = client.get("/api/v1/courses").json()
    assert courses == [
        {
            "id": COURSE,
            "title": courses[0]["title"],
            "summary": courses[0]["summary"],
            "tags": courses[0]["tags"],
            "module_count": 2,
            "lesson_count": 3,
            "lang": "ko",
        }
    ]
    detail = client.get(f"/api/v1/courses/{COURSE}").json()
    assert [s["level"] for s in detail["stages"]] == ["기초", None]
    assert [m["id"] for s in detail["stages"] for m in s["modules"]] == [
        "m1-math-physics",
        "m2-kinematics",
    ]
    assert_problem(client.get("/api/v1/courses/nope"), 404)


def test_module_detail(client: TestClient) -> None:
    module = client.get("/api/v1/modules/m1-math-physics").json()
    assert module["course_id"] == COURSE
    assert module["lesson_count"] == 2
    assert [les["id"] for les in module["lessons"]] == [VECTORS, ROTATION]
    assert module["estimated_minutes"] == sum(les["estimated_minutes"] for les in module["lessons"])
    body = assert_problem(client.get("/api/v1/modules/nope"), 404)
    assert body["detail"] == "unknown module 'nope'"
    assert body["instance"] == "/api/v1/modules/nope"


def test_lesson_detail_and_neighbours(client: TestClient) -> None:
    lesson = client.get(f"/api/v1/lessons/{ROTATION}").json()
    assert lesson["prerequisites"] == [VECTORS]
    assert lesson["prev_lesson_id"] == VECTORS
    assert lesson["next_lesson_id"] == DH
    assert lesson["body"].strip()
    assert lesson["objectives"]
    first = client.get(f"/api/v1/lessons/{VECTORS}").json()
    assert first["prev_lesson_id"] is None
    last = client.get(f"/api/v1/lessons/{DH}").json()
    assert last["next_lesson_id"] is None
    assert last["resources"][0]["title"] == "Sample Robotics Textbook"
    assert_problem(client.get("/api/v1/lessons/nope"), 404)


def test_lesson_study_method_from_real_curriculum(tmp_path: Path) -> None:
    client = TestClient(create_app(Settings(ROOT / "curriculum", tmp_path)))
    lesson = client.get(f"/api/v1/lessons/{VECTORS}").json()
    assert lesson["study_method"]
    assert "이 단계 공부법" not in lesson["study_method"]  # heading itself stripped


def test_resources(client: TestClient) -> None:
    every = client.get("/api/v1/resources").json()
    assert every == [
        {
            "title": "Sample Robotics Textbook",
            "url": None,
            "kind": "book",
            "note": "Ch. 3",
            "lesson_ids": [DH],
        }
    ]
    assert client.get("/api/v1/resources", params={"lesson_id": VECTORS}).json() == []
    assert client.get("/api/v1/resources", params={"module_id": "m2-kinematics"}).json() == every
    assert client.get("/api/v1/resources", params={"kind": "video"}).json() == []
    assert_problem(client.get("/api/v1/resources", params={"lesson_id": "nope"}), 404)
    assert_problem(client.get("/api/v1/resources", params={"module_id": "nope"}), 404)
    assert_problem(client.get("/api/v1/resources", params={"kind": "podcast"}), 422)


# -- progress --------------------------------------------------------------------------


def test_timer_start_stop_and_conflicts(client: TestClient, clock: Clock) -> None:
    started = client.post("/api/v1/progress/start", json={"lesson_id": VECTORS})
    assert started.status_code == 201
    assert started.json()["lesson_id"] == VECTORS
    assert started.json()["ended_at"] is None

    body = assert_problem(client.post("/api/v1/progress/start", json={"lesson_id": DH}), 409)
    assert "already running" in body["detail"]
    assert_problem(client.post("/api/v1/progress/start", json={"lesson_id": "nope"}), 404)

    status = client.get("/api/v1/progress/status").json()
    assert status["open_session"]["lesson_id"] == VECTORS

    clock.now += timedelta(minutes=25)
    stopped = client.post("/api/v1/progress/stop", json={"note": "ch1"})
    assert stopped.status_code == 200
    assert stopped.json()["seconds"] == 25 * 60
    assert stopped.json()["note"] == "ch1"
    assert_problem(client.post("/api/v1/progress/stop"), 409)

    row = client.get(f"/api/v1/progress/lessons/{VECTORS}").json()
    assert row["status"] == "in_progress"
    assert row["total_seconds"] == 25 * 60


def test_stop_discard(client: TestClient, clock: Clock) -> None:
    client.post("/api/v1/progress/start", json={"lesson_id": VECTORS})
    clock.now += timedelta(minutes=10)
    stopped = client.post("/api/v1/progress/stop", json={"discard": True}).json()
    assert stopped["seconds"] == 0
    assert client.get(f"/api/v1/progress/lessons/{VECTORS}").json()["total_seconds"] == 0


def test_log_done_and_next(client: TestClient) -> None:
    logged = client.post(
        "/api/v1/progress/log", json={"lesson_id": VECTORS, "minutes": 45, "note": "read"}
    )
    assert logged.status_code == 201
    assert logged.json()["source"] == "manual"
    assert logged.json()["seconds"] == 45 * 60

    nxt = client.get("/api/v1/progress/next").json()
    # `reason` follows Accept-Language; the default is the authoring language.
    # `next` ranks rather than filters (ADR 0015): VECTORS leads because it is in progress.
    assert [n["lesson"]["id"] for n in nxt] == [VECTORS, ROTATION, DH]
    assert nxt[0]["reason"] == translator("ko")("api.next_reason.in_progress")
    english = client.get("/api/v1/progress/next", headers={"Accept-Language": "en"}).json()
    assert english[0]["reason"] == "in progress"

    done = client.post(
        "/api/v1/progress/done", json={"lesson_id": VECTORS, "understanding": 4, "note": "ok"}
    )
    assert done.status_code == 200
    assert done.json()["progress"]["status"] == "done"
    assert done.json()["progress"]["understanding"] == 4
    assert sorted(done.json()["unlocked_lesson_ids"]) == sorted([ROTATION, DH])

    nxt = client.get("/api/v1/progress/next", params={"n": 1}).json()
    assert [n["lesson"]["id"] for n in nxt] == [ROTATION]
    assert nxt[0]["reason"] == translator("ko")("api.next_reason.prerequisites_done")

    status = client.get("/api/v1/progress/status", params={"course": COURSE}).json()
    assert status["open_session"] is None
    # `locked` is deprecated and always false; unfinished prerequisites are advice.
    assert [(s["lesson"]["id"], s["status"], s["locked"]) for s in status["lessons"]] == [
        (VECTORS, "done", False),
        (ROTATION, "not_started", False),
        (DH, "not_started", False),
    ]
    assert [s["missing_prerequisites"] for s in status["lessons"]] == [[], [], []]
    rows = client.get("/api/v1/progress/lessons").json()
    assert [r["lesson_id"] for r in rows] == [VECTORS, ROTATION, DH]


def test_progress_validation_errors(client: TestClient) -> None:
    body = assert_problem(
        client.post("/api/v1/progress/log", json={"lesson_id": VECTORS, "minutes": 0}), 422
    )
    assert body["errors"][0]["loc"] == ["body", "minutes"]
    body = assert_problem(
        client.post("/api/v1/progress/done", json={"lesson_id": VECTORS, "understanding": 9}), 422
    )
    assert body["errors"][0]["loc"] == ["body", "understanding"]
    assert_problem(client.post("/api/v1/progress/start", json={"lesson": VECTORS}), 422)
    assert_problem(
        client.post("/api/v1/progress/log", json={"lesson_id": "nope", "minutes": 5}), 404
    )
    assert_problem(client.post("/api/v1/progress/done", json={"lesson_id": "nope"}), 404)
    assert_problem(client.get("/api/v1/progress/lessons/nope"), 404)
    assert_problem(client.get("/api/v1/progress/status", params={"course": "nope"}), 404)
    assert_problem(client.get("/api/v1/progress/next", params={"course": "nope"}), 404)
    assert_problem(client.get("/api/v1/progress/next", params={"n": 0}), 422)


def test_unknown_route_and_method_are_problems(client: TestClient) -> None:
    body = assert_problem(client.get("/api/v1/nowhere"), 404)
    assert "detail" not in body  # Starlette's default detail only repeats the title
    assert_problem(client.get("/api/v1/progress/start"), 405)


def test_export(client: TestClient) -> None:
    client.post("/api/v1/progress/log", json={"lesson_id": VECTORS, "minutes": 30})
    data = client.get("/api/v1/me/export").json()
    assert data["schema_version"] >= 1
    assert data["exported_at"] == "2026-11-11T09:00:00Z"
    assert [p["lesson_id"] for p in data["lesson_progress"]] == [VECTORS]
    assert len(data["sessions"]) == 1


# -- reports ---------------------------------------------------------------------------


def test_weekly_report_json_and_markdown(client: TestClient) -> None:
    client.post("/api/v1/progress/log", json={"lesson_id": VECTORS, "minutes": 90, "note": "n1"})
    client.post("/api/v1/progress/done", json={"lesson_id": VECTORS, "understanding": 2})
    report = client.get("/api/v1/reports/weekly", params={"week": "2026-W46"}).json()
    assert report["kind"] == "weekly"
    assert report["period"] == "2026-W46"
    summary = report["summary"]
    assert (summary["start"], summary["end"]) == ("2026-11-09", "2026-11-15")
    assert summary["total_seconds"] == 90 * 60
    assert [c["lesson_id"] for c in summary["completed"]] == [VECTORS]
    assert [s["lesson_id"] for s in summary["stuck"]] == [VECTORS]
    assert report["markdown"].startswith("# 주간 리포트 2026-W46")

    md = client.get(
        "/api/v1/reports/weekly", params={"week": "2026-W46"}, headers={"Accept": "text/markdown"}
    )
    assert md.headers["content-type"].startswith("text/markdown")
    assert md.text == report["markdown"]

    default_week = client.get("/api/v1/reports/weekly").json()
    assert default_week["period"] == report["period"] or default_week["period"].startswith("2026-W")


def test_weekly_report_bad_week(client: TestClient) -> None:
    assert_problem(client.get("/api/v1/reports/weekly", params={"week": "46"}), 422)
    body = assert_problem(client.get("/api/v1/reports/weekly", params={"week": "2026-W99"}), 422)
    assert "does not exist" in body["detail"]


def test_module_report(client: TestClient) -> None:
    client.post("/api/v1/progress/done", json={"lesson_id": VECTORS, "understanding": 5})
    report = client.get("/api/v1/reports/modules/m1-math-physics").json()
    assert report["kind"] == "module"
    assert report["summary"]["done_count"] == 1
    assert report["summary"]["lesson_count"] == 2
    assert report["markdown"].startswith("# 모듈 리포트")
    assert_problem(client.get("/api/v1/reports/modules/nope"), 404)


# -- CLI / API equivalence (AC-API.3) ----------------------------------------------------


def test_cli_and_api_agree(client: TestClient, settings: Settings) -> None:
    client.post("/api/v1/progress/log", json={"lesson_id": VECTORS, "minutes": 40, "note": "x"})
    client.post("/api/v1/progress/done", json={"lesson_id": VECTORS, "understanding": 3})
    runner = CliRunner()
    base = ["--data-dir", str(settings.data_dir), "--curriculum", str(CURRICULUM)]

    cli_md = runner.invoke(cli_app, [*base, "report", "module", "m1-math-physics"])
    assert cli_md.exit_code == 0, cli_md.output
    api_md = client.get(
        "/api/v1/reports/modules/m1-math-physics", headers={"Accept": "text/markdown"}
    )
    assert api_md.text == cli_md.output

    cli_export = runner.invoke(cli_app, [*base, "progress", "export"])
    assert cli_export.exit_code == 0, cli_export.output
    cli_data = json.loads(cli_export.output)
    api_data = client.get("/api/v1/me/export").json()
    for key in ("lesson_progress", "sessions", "schema_version"):
        assert api_data[key] == cli_data[key]


# -- request id, logging, unhandled errors ------------------------------------------------


def test_request_id_echoed_or_generated(client: TestClient) -> None:
    given = client.get("/healthz", headers={"X-Request-ID": "abc-123"})
    assert given.headers["x-request-id"] == "abc-123"
    generated = client.get("/healthz", headers={"X-Request-ID": "bad id\x7f"})
    assert generated.headers["x-request-id"] != "bad id\x7f"
    assert len(generated.headers["x-request-id"]) == 32


def test_unhandled_error_is_500_problem(
    settings: Settings, caplog: pytest.LogCaptureFixture
) -> None:
    app: FastAPI = create_app(settings)

    def boom() -> None:
        raise RuntimeError("kaboom")

    app.add_api_route("/boom", boom)
    with caplog.at_level(logging.INFO, logger="robotics_curriculum.api"):
        response = TestClient(app).get("/boom", headers={"X-Request-ID": "req-500"})
    body = assert_problem(response, 500)
    assert body["request_id"] == "req-500"
    assert "kaboom" not in response.text
    messages = [(r.getMessage(), getattr(r, "status", None)) for r in caplog.records]
    assert ("unhandled error", None) in messages
    assert ("request", 500) in messages


def test_json_formatter_includes_request_id_and_extras() -> None:
    record = logging.LogRecord("x", logging.INFO, __file__, 1, "hello %s", ("you",), None)
    record.path = "/healthz"
    token = request_id_var.set("rid-1")
    try:
        line = json.loads(JsonFormatter().format(record))
    finally:
        request_id_var.reset(token)
    assert line["message"] == "hello you"
    assert line["request_id"] == "rid-1"
    assert line["path"] == "/healthz"
    assert line["level"] == "info"

    try:
        raise ValueError("bad")
    except ValueError:
        err = logging.LogRecord("x", logging.ERROR, __file__, 1, "oops", None, sys.exc_info())
    line = json.loads(JsonFormatter().format(err))
    assert "request_id" not in line
    assert "ValueError: bad" in line["exc_info"]


def test_configure_logging_installs_json_handler() -> None:
    root = logging.getLogger()
    saved = (root.handlers[:], root.level)
    try:
        configure_logging("debug")
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0].formatter, JsonFormatter)
        assert root.level == logging.DEBUG
        assert logging.getLogger("uvicorn.access").propagate
    finally:
        root.handlers[:], level = saved
        root.setLevel(level)


# -- OpenAPI ---------------------------------------------------------------------------


def _spec(client: TestClient) -> dict[str, Any]:
    spec: dict[str, Any] = client.get("/openapi.json").json()
    spec["info"].pop("version")  # bumps with every release; not part of the contract
    return spec


def test_openapi_snapshot(client: TestClient) -> None:
    """Fails on any API change. Regenerate with RC_UPDATE_SNAPSHOTS=1 after review."""
    spec = _spec(client)
    if os.environ.get("RC_UPDATE_SNAPSHOTS") == "1":
        SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", "utf-8")
        DESIGN_DOC.write_text(_design_doc(spec, yaml.safe_load(DESIGN_DOC.read_text("utf-8"))))
    assert SNAPSHOT.is_file(), "missing snapshot: run RC_UPDATE_SNAPSHOTS=1 uv run pytest"
    assert spec == json.loads(SNAPSHOT.read_text("utf-8")), (
        "OpenAPI changed. If intended, run RC_UPDATE_SNAPSHOTS=1 uv run pytest tests/test_api.py "
        "(regenerates the snapshot and docs/api/openapi.yaml) and review the diff."
    )


# Paths and schemas the design keeps for later milestones (not served yet).
PLANNED_PATHS = {
    "/api/v1/roadmap",
    "/api/v1/search",
    "/api/v1/progress/sessions",
    "/api/v1/cards",
    "/api/v1/cards/{card_id}",
    "/api/v1/admin/invitations",
    "/api/v1/admin/content",
    "/api/v1/admin/content/reload",
}
_SYSTEM = {"/healthz", "/readyz", "/version", "/metrics"}


def _design_doc(spec: dict[str, Any], old: dict[str, Any]) -> str:
    """docs/api/openapi.yaml = the implementation (paths, schemas) + the design's header
    (description, tags, security schemes, shared parameters) + ``x-planned`` items."""

    def full(path: str) -> str:
        return path if path.startswith("/api/v1") or path in _SYSTEM else "/api/v1" + path

    old_paths = {full(p): item for p, item in old.get("paths", {}).items()}
    planned = old.get("x-planned", {})
    planned_paths = {
        p: item
        for p, item in {**planned.get("paths", {}), **old_paths}.items()
        if p in PLANNED_PATHS and p not in spec["paths"]
    }
    old_components = old.get("components", {})
    old_schemas = {**planned.get("schemas", {}), **old_components.get("schemas", {})}
    planned_schemas = {
        name: schema
        for name, schema in old_schemas.items()
        if name not in spec["components"]["schemas"]
        and name
        in {
            "CardPage",
            "ContentStatus",
            "Level",
            "LockState",
            "Roadmap",
            "SearchHit",
            "StudySessionPage",
        }
    }
    doc = {
        "openapi": spec["openapi"],
        "info": {
            **spec["info"],
            "version": "1 (/api/v1)",
            "description": old.get("info", {}).get("description", ""),
        },
        "servers": [{"url": "/"}],
        "tags": old.get("tags", []),
        "security": old.get("security", []),
        "paths": spec["paths"],
        "components": {
            "securitySchemes": old_components.get("securitySchemes", {}),
            "parameters": old_components.get("parameters", {}),
            "responses": old_components.get("responses", {}),
            "schemas": spec["components"]["schemas"],
        },
        "x-planned": {
            "description": "Designed but not served yet; moves into paths when implemented.",
            "paths": dict(sorted(planned_paths.items())),
            "schemas": dict(sorted(planned_schemas.items())),
        },
    }
    header = (
        "# Generated from the implementation by tests/test_api.py::test_openapi_snapshot\n"
        "# (RC_UPDATE_SNAPSHOTS=1). Edit the header fields or x-planned here; paths and\n"
        "# components.schemas always come from the FastAPI app.\n"
    )

    class Dumper(yaml.SafeDumper):
        pass

    def text(dumper: yaml.SafeDumper, value: str) -> yaml.ScalarNode:
        style = "|" if "\n" in value else None
        return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)

    Dumper.add_representer(str, text)
    body = yaml.dump(doc, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=100)
    return header + body


def test_design_doc_matches_implementation(client: TestClient) -> None:
    """The contract test of docs/platform-design.md §7: design == served API."""
    spec = _spec(client)
    doc = yaml.safe_load(DESIGN_DOC.read_text("utf-8"))
    assert doc["paths"] == spec["paths"], (
        "run RC_UPDATE_SNAPSHOTS=1 uv run pytest tests/test_api.py"
    )
    assert doc["components"]["schemas"] == spec["components"]["schemas"]
    assert not set(doc["x-planned"]["paths"]) & set(spec["paths"])


def test_openapi_errors_are_problem_json(client: TestClient) -> None:
    spec = _spec(client)
    schemas = spec["components"]["schemas"]
    assert "Problem" in schemas
    assert "HTTPValidationError" not in schemas
    for path, item in spec["paths"].items():
        for method, op in item.items():
            for code, resp in op["responses"].items():
                if code.startswith(("4", "5")) and path != "/readyz":
                    assert list(resp["content"]) == [PROBLEM], (path, method, code)
    assert all(
        p.startswith("/api/v1/")
        for p in spec["paths"]
        if p not in {"/healthz", "/readyz", "/version", "/metrics"}
    )


# -- settings & CLI --------------------------------------------------------------------


def test_settings_from_env(tmp_path: Path) -> None:
    env = {
        "RC_CURRICULUM_DIR": str(tmp_path / "c"),
        "RC_DATA_DIR": str(tmp_path / "d"),
        "RC_API_HOST": "0.0.0.0",
        "RC_API_PORT": "9000",
        "RC_API_LOG_LEVEL": "DEBUG",
    }
    s = Settings.from_env(env)
    assert (s.curriculum_dir, s.data_dir) == (tmp_path / "c", tmp_path / "d")
    assert (s.host, s.port, s.log_level) == ("0.0.0.0", 9000, "debug")
    defaults = Settings.from_env({})
    assert (defaults.host, defaults.port, defaults.log_level) == ("127.0.0.1", 8000, "info")
    assert defaults.curriculum_dir.name == "curriculum"
    with pytest.raises(SettingsError, match="RC_API_PORT"):
        Settings.from_env({"RC_API_PORT": "http"})
    with pytest.raises(SettingsError, match="port"):
        Settings.from_env({"RC_API_PORT": "70000"})
    with pytest.raises(SettingsError, match="log level"):
        Settings.from_env({"RC_API_LOG_LEVEL": "loud"})


def test_rc_api_serve_runs_uvicorn(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import uvicorn

    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(uvicorn, "run", lambda app, **kw: calls.append({"app": app, **kw}))
    monkeypatch.setattr("robotics_curriculum.api.log.configure_logging", lambda level: None)
    monkeypatch.setenv("RC_API_ALLOW_REMOTE_LOCAL", "1")  # local mode on 0.0.0.0 needs opt-in
    result = CliRunner().invoke(
        cli_app,
        [
            "--curriculum",
            str(CURRICULUM),
            "--data-dir",
            str(tmp_path),
            "api",
            "serve",
            "--host",
            "0.0.0.0",
            "--port",
            "9123",
        ],
    )
    assert result.exit_code == 0, result.output
    assert calls[0]["host"] == "0.0.0.0"
    assert calls[0]["port"] == 9123
    app = calls[0]["app"]
    assert app.state.rc.settings.curriculum_dir == CURRICULUM
    assert app.state.rc.index is not None


def test_rc_api_serve_rejects_bad_port_and_missing_extra(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    result = runner.invoke(cli_app, ["api", "serve", "--port", "0"])
    assert result.exit_code == 1
    assert "invalid port" in result.output
    monkeypatch.setitem(sys.modules, "uvicorn", None)
    result = runner.invoke(cli_app, ["api", "serve"])
    assert result.exit_code == 1
    assert "'api' extra" in result.output


# -- metrics (P2-5, AC-OPS.1) ------------------------------------------------------------


def _sample(text: str, name: str, **labels: str) -> float:
    for line in text.splitlines():
        if line.startswith(f"{name}{{") and all(f'{k}="{v}"' in line for k, v in labels.items()):
            return float(line.rsplit(" ", 1)[1])
    raise AssertionError(f"{name} {labels} not found")


def test_metrics_count_requests_by_route(client: TestClient) -> None:
    client.get(f"/api/v1/lessons/{VECTORS}")
    client.get("/api/v1/lessons/nope")
    client.get("/api/v1/nowhere")
    r = client.get("/metrics")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/plain")
    text = r.text
    route = "/api/v1/lessons/{lesson_id}"
    assert _sample(text, "http_requests_total", route=route, status="200") == 1
    assert _sample(text, "http_requests_total", route=route, status="404") == 1
    assert _sample(text, "http_requests_total", route="unmatched", status="404") == 1
    assert _sample(text, "http_request_duration_seconds_count", route=route) == 2
    assert "http_requests_in_progress" in text
    assert "/api/v1/lessons/nope" not in text  # raw paths never become labels


def test_metrics_can_be_disabled(tmp_path: Path) -> None:
    settings = Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path, metrics=False)
    assert_problem(TestClient(create_app(settings)).get("/metrics"), 404)
    assert Settings.from_env({"RC_API_METRICS": "0"}).metrics is False


def test_metrics_report_auth_pool(tmp_path: Path) -> None:
    from robotics_curriculum.api.metrics import PoolCollector

    settings = Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path, auth_mode="server")
    client = TestClient(create_app(settings, mailer=None), base_url="https://testserver")
    client.get("/readyz")
    text = client.get("/metrics").text
    assert 'rc_db_pool_connections{pool="auth",state="checked_out"}' in text

    class Pool:
        def checkedout(self) -> int:
            return 3

        def size(self) -> str:  # non-int values are skipped
            return "n/a"

    families = list(PoolCollector(lambda: {"x": Pool(), "y": object()}).collect())
    assert [s.value for s in families[0].samples] == [3]

# ruff: noqa: F811
# Fixtures are imported from test_auth and requested by name, which ruff sees as redefinitions.
"""Monitoring API (P3-2, ADR 0017): request statistics, failed requests, system, visits, KPIs.

The role matrix for these endpoints is in ``tests/test_auth.py`` (``MATRIX``).
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.settings import Settings
from robotics_curriculum.auth.mailer import FakeMailer
from robotics_curriculum.auth.service import AuthConfig
from robotics_curriculum.ops.recorder import Recorder
from test_auth import (  # noqa: F401  (fixtures are used by name)
    ADMIN,
    CURRICULUM,
    PASSWORD,
    VECTORS,
    Clock,
    app,
    assert_problem,
    audit_actions,
    client_for,
    clock,
    fast_argon2,
    login,
    mailer,
    settings,
    signup,
    user,
)

BASE = "/api/v1/admin/monitoring"
BROWSER = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36"


def recorder(app: FastAPI) -> Recorder:
    ops = app.state.rc.ops
    assert isinstance(ops, Recorder)
    return ops


def web(app: FastAPI) -> TestClient:
    """A client connecting from the web tier's address (loopback is a trusted proxy)."""
    return TestClient(app, base_url="https://testserver", client=("127.0.0.1", 50000))


# -- request statistics (AC-MON.1, AC-MON.2) -----------------------------------------------


def test_requests_are_counted_by_route_and_outcome(app: FastAPI) -> None:
    admin = user(app, ADMIN)
    for _ in range(3):
        assert admin.get("/api/v1/courses").status_code == 200
    assert admin.get("/api/v1/lessons/no-such-lesson").status_code == 404
    client_for(app).get("/api/v1/me")  # 401, anonymous

    body = admin.get(f"{BASE}/traffic").json()
    totals = body["totals"]
    assert totals["requests"] >= 5
    assert totals["server_errors"] == 0
    assert totals["client_errors"] >= 2
    assert totals["success_rate"] == 1.0  # 4xx are the callers' mistakes, not downtime
    assert totals["p95_ms"] is not None and totals["apdex"] is not None
    assert body["range"] == "24h" and body["bucket_seconds"] == 3600
    assert len(body["series"]) == 24
    assert body["series"][-1]["requests"] == totals["requests"]
    courses = next(r for r in body["busiest"] if r["route"] == "/api/v1/courses")
    assert courses["requests"] == 3 and courses["method"] == "GET"
    # Routes are templates: the lesson id that was asked for is not a label.
    assert all("no-such-lesson" not in route["route"] for route in body["busiest"])
    assert body["failing"] == []
    assert body["error_budget"]["target"] == 0.999
    assert body["error_budget"]["consumed_ratio"] == 0
    assert "admin.monitoring.viewed" in audit_actions(app)


def test_probes_and_scrapes_are_not_traffic(app: FastAPI) -> None:
    admin = user(app, ADMIN)
    for _ in range(5):
        client_for(app).get("/healthz")
        client_for(app).get("/readyz")
        client_for(app).get("/metrics")
    for index in range(5):
        _view(web(app), "/", ip=f"198.51.100.{index}")
    routes = {r["route"] for r in admin.get(f"{BASE}/traffic").json()["busiest"]}
    assert routes.isdisjoint(
        {"/healthz", "/readyz", "/metrics", "/version", "/api/v1/telemetry/pageview"}
    )


def test_statistics_survive_a_restart(settings: Settings, clock: Clock, mailer: FakeMailer) -> None:
    def build() -> FastAPI:
        return create_app(
            settings,
            clock=clock,
            mailer=mailer,
            auth_config=AuthConfig(bootstrap_admin_email=ADMIN),
        )

    first = build()
    admin = user(first, ADMIN)
    for _ in range(4):
        admin.get("/api/v1/courses")
    with TestClient(first):
        pass  # shutting the app down flushes what is buffered
    second = build()
    again = login(second, ADMIN)
    routes = {r["route"]: r["requests"] for r in again.get(f"{BASE}/traffic").json()["busiest"]}
    assert routes["/api/v1/courses"] == 4


def test_ranges_and_series_shape(app: FastAPI, clock: Clock) -> None:
    admin = user(app, ADMIN)
    admin.get("/api/v1/courses")
    recorder(app).flush()
    clock.advance(days=2)
    admin = login(app, ADMIN)
    admin.get("/api/v1/courses")
    day = admin.get(f"{BASE}/traffic", params={"range": "24h"}).json()
    week = admin.get(f"{BASE}/traffic", params={"range": "7d"}).json()
    month = admin.get(f"{BASE}/traffic", params={"range": "30d"}).json()
    assert (len(day["series"]), len(week["series"]), len(month["series"])) == (24, 28, 30)
    assert (week["bucket_seconds"], month["bucket_seconds"]) == (6 * 3600, 86400)
    by = lambda body: {r["route"]: r["requests"] for r in body["busiest"]}  # noqa: E731
    assert by(day)["/api/v1/courses"] == 1  # the request two days ago is outside the last day
    assert by(week)["/api/v1/courses"] == 2
    assert sum(b["requests"] for b in month["series"]) == month["totals"]["requests"]
    assert_problem(admin.get(f"{BASE}/traffic", params={"range": "1y"}), 422)


# -- failed requests (AC-MON.3) ------------------------------------------------------------


def _crashing_app(settings: Settings, clock: Clock, mailer: FakeMailer) -> FastAPI:
    built = create_app(
        settings, clock=clock, mailer=mailer, auth_config=AuthConfig(bootstrap_admin_email=ADMIN)
    )

    @built.get("/api/v1/_boom/{item}")
    def boom(item: str) -> dict[str, Any]:
        raise RuntimeError(f"cannot handle {item}")

    return built


def test_a_crash_is_logged_with_what_an_operator_needs(
    settings: Settings, clock: Clock, mailer: FakeMailer
) -> None:
    app = _crashing_app(settings, clock, mailer)
    admin = user(app, ADMIN)
    admin_id = admin.get("/api/v1/me").json()["id"]
    crash = TestClient(app, base_url="https://testserver", raise_server_exceptions=False)
    crash.cookies = admin.cookies
    r = crash.get("/api/v1/_boom/widget", params={"token": "do-not-store-me"})
    assert r.status_code == 500
    request_id = r.headers["x-request-id"]

    page = admin.get(f"{BASE}/errors").json()
    assert page["total_24h"] == 1
    (entry,) = page["items"]
    assert entry["status"] == 500
    assert entry["route"] == "/api/v1/_boom/{item}"
    assert entry["path"] == "/api/v1/_boom/widget"
    assert entry["error_type"] == "RuntimeError"
    assert entry["error_message"] == "cannot handle widget"
    # The id in the response is the id in the log: the operator can find the stack trace.
    assert entry["request_id"] == request_id
    assert entry["duration_ms"] >= 0
    # Nothing from the query string is kept anywhere in the record.
    assert "do-not-store-me" not in str(page)
    assert entry["user_id"] in (admin_id, None)

    traffic = admin.get(f"{BASE}/traffic").json()
    assert traffic["totals"]["server_errors"] == 1
    assert traffic["totals"]["success_rate"] < 1
    assert traffic["failing"][0]["route"] == "/api/v1/_boom/{item}"
    assert traffic["error_budget"]["failures"] == 1
    assert any(alert["key"] == "errors" for alert in traffic["alerts"])

    assert admin.get(f"{BASE}/errors", params={"status": 503}).json()["items"] == []
    assert (
        len(admin.get(f"{BASE}/errors", params={"route": "/api/v1/_boom/{item}"}).json()["items"])
        == 1
    )
    assert_problem(admin.get(f"{BASE}/errors", params={"cursor": "x"}), 422)
    assert_problem(admin.get(f"{BASE}/errors", params={"status": 404}), 422)


def test_failed_requests_page_by_cursor(
    settings: Settings, clock: Clock, mailer: FakeMailer
) -> None:
    app = _crashing_app(settings, clock, mailer)
    admin = user(app, ADMIN)
    crash = TestClient(app, base_url="https://testserver", raise_server_exceptions=False)
    for index in range(5):
        crash.get(f"/api/v1/_boom/{index}")
    first = admin.get(f"{BASE}/errors", params={"limit": 2}).json()
    assert [e["path"][-1] for e in first["items"]] == ["4", "3"] and first["next_cursor"]
    second = admin.get(f"{BASE}/errors", params={"limit": 2, "cursor": first["next_cursor"]}).json()
    assert [e["path"][-1] for e in second["items"]] == ["2", "1"]


def test_deleting_an_account_detaches_it_from_the_failure_log(
    settings: Settings, clock: Clock, mailer: FakeMailer
) -> None:
    app = _crashing_app(settings, clock, mailer)
    admin = user(app, ADMIN)
    learner = user(app, "learner@example.org")
    learner_id = learner.get("/api/v1/me").json()["id"]
    recorder(app).store.add_request_error(
        at=clock.now, method="GET", route="/x", path="/x", status=500, duration_ms=1,
        request_id=None, user_id=learner_id, error_type=None, error_message=None,
    )  # fmt: skip
    assert learner.request("DELETE", "/api/v1/me", json={"password": PASSWORD}).status_code in (
        200,
        204,
    )
    (entry,) = admin.get(f"{BASE}/errors").json()["items"]
    assert entry["user_id"] is None


# -- system (AC-MON.4) ---------------------------------------------------------------------


def test_system_status_reports_readings_or_null(app: FastAPI) -> None:
    admin = user(app, ADMIN)
    body = admin.get(f"{BASE}/system").json()
    assert body["version"]
    assert body["process_uptime_seconds"] >= 0
    assert body["cpu"]["count"] >= 1
    assert body["cpu"]["usage_ratio"] is None  # the first reading has nothing to compare with
    assert body["database"]["backend"] == "sqlite"
    assert body["database"]["reachable"] is True
    assert body["database"]["ping_ms"] >= 0
    assert body["database"]["size_bytes"] > 0
    assert body["database"]["connections"] is None
    assert set(body["database"]["monitoring_rows"]) >= {"ops_request_stats", "ops_page_views"}
    assert body["disks"] and 0 <= body["disks"][0]["used_ratio"] <= 1
    assert body["process"]["requests_in_progress"] >= 1  # this request
    for reading in body["temperatures"]:
        assert 1 <= reading["celsius"] <= 150 and reading["level"] in ("ok", "warning", "critical")
    if body["memory"] is not None:
        assert 0 <= body["memory"]["used_ratio"] <= 1
    # A second reading can say how busy the CPU was in between.
    second = admin.get(f"{BASE}/system").json()
    assert second["cpu"]["usage_ratio"] is None or 0 <= second["cpu"]["usage_ratio"] <= 1
    for alert in body["alerts"]:
        assert alert["level"] in ("warning", "critical")


def test_a_full_disk_raises_an_alert(app: FastAPI, monkeypatch: Any) -> None:
    from robotics_curriculum.ops import system

    def nearly_full(path: Path) -> system.Disk:
        return system.Disk(path=str(path), total_bytes=1000, used_bytes=930, free_bytes=70)

    def hot(_root: Path = system.SYS) -> list[system.Temperature]:
        return [system.Temperature("coretemp Package id 0", 84.0)]

    monkeypatch.setattr(system, "read_disk", nearly_full)
    monkeypatch.setattr(system, "read_temperatures", hot)
    admin = user(app, ADMIN)
    body = admin.get(f"{BASE}/system").json()
    assert body["disks"][0]["level"] == "critical"
    assert body["temperatures"][0]["level"] == "warning"
    alerts = {alert["key"]: alert for alert in body["alerts"]}
    assert alerts["disk"]["level"] == "critical" and alerts["disk"]["threshold"] == 0.9
    assert alerts["temperature"]["detail"] == "coretemp Package id 0"


# -- visits (AC-MON.5) ---------------------------------------------------------------------


def _view(client: TestClient, path: str, *, ip: str, agent: str = BROWSER, **body: Any) -> int:
    return client.post(
        "/api/v1/telemetry/pageview",
        json={"path": path, **body},
        headers={"X-Forwarded-For": ip, "User-Agent": agent},
    ).status_code


def test_page_views_are_accepted_from_the_web_tier_only(app: FastAPI) -> None:
    assert _view(web(app), "/", ip="198.51.100.7") == 204
    # A direct caller cannot report views, with or without a forwarded header.
    outsider = TestClient(app, base_url="https://testserver", client=("203.0.113.9", 50000))
    assert_problem(
        outsider.post(
            "/api/v1/telemetry/pageview",
            json={"path": "/"},
            headers={"X-Forwarded-For": "127.0.0.1"},
        ),
        403,
    )
    assert_problem(client_for(app).post("/api/v1/telemetry/pageview", json={"path": "/"}), 403)
    assert_problem(web(app).post("/api/v1/telemetry/pageview", json={}), 422)


def test_visits_report_views_visitors_bots_pages_and_referrers(app: FastAPI, clock: Clock) -> None:
    admin = user(app, ADMIN)
    tier = web(app)
    google = "https://www.google.com/search?q=learn+robotics"
    _view(tier, "/", ip="198.51.100.7", referrer=google, locale="en")
    _view(tier, "/roadmap", ip="198.51.100.7", locale="en")
    _view(
        tier, "/modules/m1-math-physics", ip="198.51.100.8", referrer="https://search.naver.com/x"
    )
    _view(tier, "/", ip="198.51.100.8", signed_in=True)
    _view(tier, "/admin/users/3", ip="198.51.100.8")
    _view(tier, "/", ip="66.249.66.1", agent="Mozilla/5.0 (compatible; Googlebot/2.1)")

    body = admin.get(f"{BASE}/visits", params={"range": "7d"}).json()
    assert len(body["series"]) == 7
    today = body["series"][-1]
    assert today["day"] == clock.now.date().isoformat()
    assert (today["views"], today["visitors"], today["bot_views"]) == (5, 2, 1)
    assert today["signed_in_visitors"] == 1
    totals = body["totals"]
    assert (totals["views"], totals["visitor_days"], totals["bot_views"]) == (5, 2, 1)
    assert totals["signed_in_share"] == 0.2
    assert (totals["views_today"], totals["visitors_today"]) == (5, 2)
    pages = {p["path"]: p["views"] for p in body["top_pages"]}
    assert pages == {"/": 2, "/roadmap": 1, "/modules/m1-math-physics": 1, "(other)": 1}
    assert {r["host"]: r["visits"] for r in body["referrers"]} == {
        "google.com": 1,
        "search.naver.com": 1,
    }
    assert body["by_locale"] == {"en": 2, "ko": 3}
    assert body["active_users_7d"] == 1  # the admin

    # Nothing identifying is kept: not the address, the user agent or the search query.
    rows = str(recorder(app).store.table_rows()) + str(body)
    with recorder(app).store.engine.connect() as conn:
        from sqlalchemy import text

        stored = str(conn.execute(text("SELECT * FROM ops_visitors")).all())
        stored += str(conn.execute(text("SELECT * FROM ops_referrers")).all())
    for secret in ("198.51.100", "Mozilla", "learn+robotics"):
        assert secret not in stored and secret not in rows

    # The next day the same browser is a new visitor, and yesterday's count stands.
    clock.advance(days=1)
    _view(tier, "/", ip="198.51.100.7")
    later = login(app, ADMIN).get(f"{BASE}/visits", params={"range": "7d"}).json()
    assert [d["visitors"] for d in later["series"][-2:]] == [2, 1]
    assert later["totals"]["visitor_days"] == 3


# -- product KPIs --------------------------------------------------------------------------


def test_kpis_cover_active_users_growth_activation_retention_and_learning(
    app: FastAPI, clock: Clock
) -> None:
    user(app, ADMIN)
    early = user(app, "early@example.org")
    assert early.post("/api/v1/progress/done", json={"lesson_id": VECTORS}).status_code == 200
    signup(app, "quiet@example.org")  # signs up and never comes back

    clock.advance(days=10)
    early = login(app, "early@example.org")  # returns in its second week
    early.post("/api/v1/progress/log", json={"lesson_id": VECTORS, "minutes": 30})
    newcomer = user(app, "new@example.org")
    assert newcomer.get("/api/v1/me").status_code == 200
    tier = web(app)
    for index in range(4):
        _view(tier, "/", ip=f"198.51.100.{index}")

    body = login(app, ADMIN).get(f"{BASE}/kpi").json()
    active = body["active_users"]
    # "quiet" has an account but never signed in, so it was never active.
    assert (active["daily"], active["weekly"], active["monthly"]) == (3, 3, 3)
    assert active["stickiness"] == 1.0
    growth = body["growth"]
    assert (growth["users_total"], growth["signups_7d"], growth["signups_30d"]) == (4, 1, 4)
    assert growth["visitor_days_30d"] == 4 and growth["visit_to_signup"] == 1.0
    cohorts = body["cohorts"]
    # Four accounts in the last 30 days, one of which finished a lesson.
    assert (cohorts["activation_cohort"], cohorts["activated"]) == (4, 1)
    assert cohorts["activation_rate"] == 0.25
    # Three accounts are 10 days old; two came back this week (the admin and "early").
    assert (cohorts["retention_cohort"], cohorts["retained"]) == (3, 2)
    assert cohorts["week1_retention"] == 2 / 3
    assert body["learning_7d"]["study_minutes"] == 30
    assert body["learning_7d"]["lessons_completed"] == 0
    assert body["learning_30d"]["lessons_completed"] == 1
    assert body["learning_30d"]["active_learners"] == 1
    assert body["learning_30d"]["quiz_mean_score"] is None


# -- availability of the feature -----------------------------------------------------------


def test_monitoring_can_be_turned_off(tmp_path: Path, clock: Clock, mailer: FakeMailer) -> None:
    off = Settings(
        curriculum_dir=CURRICULUM, data_dir=tmp_path, auth_mode="server", ops_metrics=False
    )
    app = create_app(
        off, clock=clock, mailer=mailer, auth_config=AuthConfig(bootstrap_admin_email=ADMIN)
    )
    admin = user(app, ADMIN)
    for path in ("system", "traffic", "errors", "visits", "kpi"):
        assert_problem(admin.get(f"{BASE}/{path}"), 404)
    assert_problem(web(app).post("/api/v1/telemetry/pageview", json={"path": "/"}), 404)
    assert Settings.from_env({"RC_OPS_METRICS": "0"}).ops_metrics is False
    assert Settings.from_env({}).ops_metrics is True


def test_local_mode_has_no_monitoring(tmp_path: Path) -> None:
    local = create_app(Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path))
    assert client_for(local).get(f"{BASE}/system").status_code == 404
    assert local.state.rc.ops is None


def test_retention_is_enforced_on_flush(app: FastAPI, clock: Clock) -> None:
    ops = recorder(app)
    old = clock.now - timedelta(days=200)
    ops.store.add_request_error(
        at=old, method="GET", route="/x", path="/x", status=500, duration_ms=1,
        request_id=None, user_id=None, error_type=None, error_message=None,
    )  # fmt: skip
    ops.record(method="GET", route="/x", status=200, duration_ms=3)
    ops.flush()  # the first flush of a process also purges
    assert ops.store.request_errors(10) == []

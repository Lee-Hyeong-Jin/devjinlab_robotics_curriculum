# ruff: noqa: F811
# Fixtures are imported from test_auth and requested by name, which ruff sees as redefinitions.
"""The service time zone (``RC_TIMEZONE``, Korea Standard Time by default).

Stored times are instants and do not change. What the zone decides is where a day begins and
how a time is written for a person.
"""

from __future__ import annotations

import csv
import io
import json
import logging
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.log import JsonFormatter
from robotics_curriculum.api.settings import Settings, SettingsError
from robotics_curriculum.auth.mailer import FakeMailer
from robotics_curriculum.auth.service import AuthConfig
from robotics_curriculum.timezone import DEFAULT_TIMEZONE, day_start, default_timezone, local_day
from test_auth import (  # noqa: F401  (fixtures are used by name)
    ADMIN,
    CURRICULUM,
    Clock,
    clock,
    fast_argon2,
    login,
    mailer,
    signup,
    user,
)

KST = ZoneInfo("Asia/Seoul")
# 16:00 UTC on the 11th is 01:00 on the 12th in Korea: the two zones disagree about the day.
LATE = datetime(2026, 11, 11, 16, 0, tzinfo=UTC)


def test_the_default_zone_is_korea_standard_time() -> None:
    assert DEFAULT_TIMEZONE == "Asia/Seoul"
    assert default_timezone().utcoffset(LATE) == timedelta(hours=9)
    assert Settings.from_env({}).timezone.key == "Asia/Seoul"
    assert Settings.from_env({"RC_TIMEZONE": " "}).timezone.key == "Asia/Seoul"
    assert Settings.from_env({"RC_TIMEZONE": "UTC"}).timezone.key == "UTC"
    assert Settings.from_env({"RC_TIMEZONE": "America/New_York"}).timezone.key == "America/New_York"
    for bad in ("KST", "Seoul", "+09:00", "../etc/passwd"):
        with pytest.raises(SettingsError):
            Settings.from_env({"RC_TIMEZONE": bad})


def test_day_helpers() -> None:
    assert local_day(LATE, KST) == date(2026, 11, 12)
    assert local_day(LATE, UTC) == date(2026, 11, 11)
    start = day_start(date(2026, 11, 12), KST)
    assert start.astimezone(UTC) == datetime(2026, 11, 11, 15, 0, tzinfo=UTC)
    assert start <= LATE < day_start(date(2026, 11, 13), KST)


def _app(tmp_path: Path, clock: Clock, mailer: FakeMailer, tz: str | None = None) -> FastAPI:
    env = {"RC_TIMEZONE": tz} if tz else {}
    settings = Settings(
        curriculum_dir=CURRICULUM,
        data_dir=tmp_path,
        auth_mode="server",
        timezone=Settings.from_env(env).timezone,
    )
    return create_app(
        settings, clock=clock, mailer=mailer, auth_config=AuthConfig(bootstrap_admin_email=ADMIN)
    )


def test_local_now_is_the_same_instant_in_the_service_zone(
    tmp_path: Path, clock: Clock, mailer: FakeMailer
) -> None:
    clock.now = LATE
    app = _app(tmp_path, clock, mailer)
    local = app.state.rc.local_now()
    assert local == LATE  # the same instant
    assert local.utcoffset() == timedelta(hours=9)
    assert local.date() == date(2026, 11, 12)
    assert app.state.rc.clock() is LATE  # what gets stored is untouched


def _web(app: FastAPI) -> TestClient:
    return TestClient(app, base_url="https://testserver", client=("127.0.0.1", 50000))


@pytest.mark.parametrize(("tz", "day"), [(None, "2026-11-12"), ("UTC", "2026-11-11")])
def test_a_visit_is_counted_under_the_local_day(
    tmp_path: Path, clock: Clock, mailer: FakeMailer, tz: str | None, day: str
) -> None:
    app = _app(tmp_path, clock, mailer, tz)
    admin = user(app, ADMIN)
    clock.now = LATE
    r = _web(app).post(
        "/api/v1/telemetry/pageview",
        json={"path": "/"},
        headers={"X-Forwarded-For": "198.51.100.7", "User-Agent": "Mozilla/5.0 Chrome/130"},
    )
    assert r.status_code == 204
    body = login(app, ADMIN).get("/api/v1/admin/monitoring/visits", params={"range": "7d"}).json()
    assert admin is not None
    today = body["series"][-1]
    assert (today["day"], today["views"], today["visitors"]) == (day, 1, 1)
    assert body["totals"]["views_today"] == 1


def test_the_signup_trend_uses_local_days(tmp_path: Path, clock: Clock, mailer: FakeMailer) -> None:
    app = _app(tmp_path, clock, mailer)
    user(app, ADMIN)  # 09:00 UTC on the 11th = 18:00 KST the same day
    clock.now = LATE  # 01:00 KST on the 12th
    signup(app, "night@example.org")
    days = login(app, ADMIN).get("/api/v1/admin/overview").json()["users"]["signups_daily"]
    assert len(days) == 14
    assert days[-1] == {"day": "2026-11-12", "count": 1}
    assert days[-2] == {"day": "2026-11-11", "count": 1}


def test_the_weekly_report_week_turns_over_at_local_midnight(
    tmp_path: Path, clock: Clock, mailer: FakeMailer
) -> None:
    app = _app(tmp_path, clock, mailer)
    learner = user(app, "learner@example.org")
    # Sunday 20:00 UTC is already Monday 05:00 in Korea: a new ISO week has begun there.
    clock.now = datetime(2026, 11, 15, 20, 0, tzinfo=UTC)
    learner = login(app, "learner@example.org")
    assert learner.get("/api/v1/reports/weekly").json()["period"] == "2026-W47"
    utc_app = _app(tmp_path / "utc", clock, mailer, "UTC")
    clock.now = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)
    other = user(utc_app, "learner@example.org")
    clock.now = datetime(2026, 11, 15, 20, 0, tzinfo=UTC)
    other = login(utc_app, "learner@example.org")
    assert other.get("/api/v1/reports/weekly").json()["period"] == "2026-W46"


def test_the_daily_traffic_series_is_cut_at_local_midnight(
    tmp_path: Path, clock: Clock, mailer: FakeMailer
) -> None:
    app = _app(tmp_path, clock, mailer)
    admin = user(app, ADMIN)
    clock.now = LATE
    admin = login(app, ADMIN)
    body = admin.get("/api/v1/admin/monitoring/traffic", params={"range": "30d"}).json()
    last = datetime.fromisoformat(body["series"][-1]["start"])
    # The last bucket starts at midnight in Korea on the 12th, i.e. 15:00 UTC on the 11th.
    assert last == datetime(2026, 11, 11, 15, 0, tzinfo=UTC)
    assert len(body["series"]) == 30
    # The requests of the "previous" local day (18:00 KST on the 11th) are in the bucket before.
    assert body["series"][-2]["requests"] > 0 and body["series"][-1]["requests"] > 0


def test_stored_instants_and_api_times_are_unchanged(
    tmp_path: Path, clock: Clock, mailer: FakeMailer
) -> None:
    clock.now = LATE
    app = _app(tmp_path, clock, mailer)
    admin = user(app, ADMIN)
    created = datetime.fromisoformat(admin.get("/api/v1/me").json()["created_at"])
    # The API still answers with the instant; the zone is a matter of presentation.
    assert created == LATE
    entry = app.state.rc.auth.list_audit(1)[0]
    assert entry.at == LATE


def test_log_lines_carry_local_time_with_its_offset() -> None:
    record = logging.LogRecord("rc", logging.INFO, __file__, 1, "hello", None, None)
    record.created = LATE.timestamp()
    kst = json.loads(JsonFormatter(KST).format(record))
    assert kst["ts"] == "2026-11-12T01:00:00.000+09:00"
    assert datetime.fromisoformat(kst["ts"]) == LATE
    assert json.loads(JsonFormatter().format(record))["ts"] == "2026-11-11T16:00:00.000+00:00"


def test_the_audit_export_writes_local_time(
    tmp_path: Path, clock: Clock, mailer: FakeMailer
) -> None:
    clock.now = LATE
    app = _app(tmp_path, clock, mailer)
    admin = user(app, ADMIN)
    text = admin.get("/api/v1/admin/audit/export", params={"action": "auth.login.success"}).text
    row = next(csv.DictReader(io.StringIO(text)))
    assert row["at"] == "2026-11-12T01:00:00+09:00"
    assert datetime.fromisoformat(row["at"]) == LATE
    # A filter given in local time finds it: the 12th in Korea, not the 12th in UTC.
    found = admin.get(
        "/api/v1/admin/audit",
        params={
            "action": "auth.login.success",
            "since": "2026-11-12T00:00:00+09:00",
            "until": "2026-11-13T00:00:00+09:00",
        },
    ).json()["items"]
    assert len(found) == 1

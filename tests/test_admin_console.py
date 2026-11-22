# ruff: noqa: F811
# Fixtures are imported from test_auth and requested by name, which ruff sees as redefinitions.
"""Operator console (P3-1): overview, user search and detail, admin actions, audit filters, CSV.

The role matrix for these endpoints is in ``tests/test_auth.py`` (``MATRIX``).
"""

from __future__ import annotations

import csv
import io
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi import FastAPI

from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.routers.admin import csv_cell
from robotics_curriculum.api.settings import Settings
from robotics_curriculum.auth.mailer import FakeMailer
from robotics_curriculum.auth.service import AuthConfig, Context
from robotics_curriculum.learn.platform import learner_summary, platform_activity
from robotics_curriculum.progress import LessonProgress, LessonStatus, Session
from test_auth import (  # noqa: F401  (fixtures are used by name)
    ADMIN,
    CURRICULUM,
    T0,
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

# -- pure aggregation ----------------------------------------------------------------------


def _lesson(
    user_id: int,
    lesson_id: str,
    status: LessonStatus,
    *,
    started: datetime | None = None,
    completed: datetime | None = None,
) -> LessonProgress:
    return LessonProgress(
        user_id=user_id,
        lesson_id=lesson_id,
        status=status,
        started_at=started,
        completed_at=completed,
    )


def test_platform_activity_counts_only_the_window() -> None:
    now = T0
    old = now - timedelta(days=30)
    recent = now - timedelta(days=2)
    lessons = [
        _lesson(1, "a", LessonStatus.DONE, started=old, completed=old),
        _lesson(1, "b", LessonStatus.DONE, started=recent, completed=recent),
        _lesson(2, "a", LessonStatus.IN_PROGRESS, started=recent),
        _lesson(3, "a", LessonStatus.DONE, started=old, completed=old),
        _lesson(4, "a", LessonStatus.NOT_STARTED),
    ]
    sessions = [
        Session(
            user_id=1, lesson_id="b", started_at=recent, ended_at=recent + timedelta(minutes=30)
        ),
        Session(user_id=3, lesson_id="a", started_at=old, ended_at=old + timedelta(hours=2)),
        # Still running: counts up to `now`.
        Session(user_id=5, lesson_id="a", started_at=now - timedelta(minutes=10)),
    ]
    activity = platform_activity(lessons, sessions, now)
    assert activity.window_days == 7
    assert activity.active_learners == 3  # users 1, 2 and 5; user 3 was last seen a month ago
    assert activity.lessons_completed == 1
    assert activity.lessons_completed_total == 3
    assert activity.study_seconds == 30 * 60 + 10 * 60
    assert activity.learners_total == 4  # user 4 never started anything


def test_platform_activity_of_nothing_is_zero() -> None:
    activity = platform_activity([], [], T0)
    assert (activity.active_learners, activity.lessons_completed, activity.study_seconds) == (
        0,
        0,
        0,
    )


def test_learner_summary_reports_counts_time_and_last_activity() -> None:
    earlier = T0 - timedelta(days=3)
    later = T0 - timedelta(hours=1)
    summary = learner_summary(
        [
            _lesson(7, "a", LessonStatus.DONE, started=earlier, completed=earlier),
            _lesson(7, "b", LessonStatus.IN_PROGRESS, started=earlier),
        ],
        [
            Session(
                user_id=7, lesson_id="b", started_at=later, ended_at=later + timedelta(minutes=20)
            )
        ],
        T0,
    )
    assert (summary.lessons_done, summary.lessons_in_progress) == (1, 1)
    assert summary.study_seconds == 20 * 60
    assert summary.last_activity_at == later + timedelta(minutes=20)
    assert learner_summary([], [], T0).last_activity_at is None


# -- overview (AC-ADM.1) -------------------------------------------------------------------


def test_overview_reports_accounts_signins_learning_and_system(
    app: FastAPI,
    clock: Clock,
) -> None:
    admin = user(app, ADMIN)
    learner = user(app, "learner@example.org")
    signup(app, "pending@example.org", verify=False)
    # One failed sign-in, and a completed lesson by the learner.
    bad = client_for(app).post(
        "/api/v1/auth/login", json={"email": "learner@example.org", "password": "wrong password!!"}
    )
    assert bad.status_code == 401
    assert learner.post("/api/v1/progress/done", json={"lesson_id": VECTORS}).status_code == 200

    body = admin.get("/api/v1/admin/overview").json()
    users = body["users"]
    assert users["total"] == 3
    assert users["by_role"] == {"learner": 2, "author": 0, "admin": 1}
    assert users["by_status"]["active"] == 3
    assert users["unverified"] == 1
    assert users["stale_unverified"] == 0  # the account is minutes old
    assert users["new_7d"] == 3
    assert len(users["signups_daily"]) == 14
    assert users["signups_daily"][-1] == {"day": "2026-11-11", "count": 3}
    assert sum(day["count"] for day in users["signups_daily"]) == 3

    security = body["security"]
    assert security["active_sessions"] == 2  # admin and learner are signed in
    assert security["logins_24h"] == {"succeeded": 2, "failed": 1}

    assert body["learning"]["lessons_completed"] == 1
    assert body["learning"]["active_learners"] == 1
    system = body["system"]
    assert system["lesson_count"] and system["course_count"]
    assert system["mail_enabled"] is True
    assert system["public_content"] is False
    assert system["audit_retention_days"] == 90
    assert "admin.overview.viewed" in audit_actions(app)

    # A week later the unverified account is stale and nobody has signed up since.
    clock.advance(days=8)
    later = login(app, ADMIN).get("/api/v1/admin/overview").json()
    assert later["users"]["stale_unverified"] == 1
    assert later["users"]["new_7d"] == 0
    assert later["users"]["new_30d"] == 3


def test_password_reset_requests_are_not_counted_as_signins(app: FastAPI) -> None:
    admin = user(app, ADMIN)
    before = admin.get("/api/v1/admin/overview").json()["security"]["logins_24h"]
    r = client_for(app).post("/api/v1/auth/password/forgot", json={"email": ADMIN})
    assert r.status_code in (202, 204)
    after = admin.get("/api/v1/admin/overview").json()["security"]["logins_24h"]
    assert after == before


# -- user search (AC-ADM.2) ----------------------------------------------------------------


@pytest.fixture
def populated(app: FastAPI) -> dict[str, int]:
    """An admin, three verified learners, one unverified, one disabled."""
    admin = user(app, ADMIN)
    ids: dict[str, int] = {}
    for email in ("kim@example.org", "lee@example.org", "park@lab.test"):
        ids[email] = signup(app, email)["id"]
    ids["new@example.org"] = signup(app, "new@example.org", verify=False)["id"]
    ids["gone@example.org"] = signup(app, "gone@example.org")["id"]
    target = ids["gone@example.org"]
    assert (
        admin.patch(f"/api/v1/admin/users/{target}", json={"status": "disabled"}).status_code == 200
    )
    kim = ids["kim@example.org"]
    assert admin.patch(f"/api/v1/admin/users/{kim}", json={"role": "author"}).status_code == 200
    return ids


def _emails(response_json: dict[str, object]) -> list[str]:
    items = response_json["items"]
    assert isinstance(items, list)
    return [item["email"] for item in items]


def test_users_are_found_by_part_of_the_address(app: FastAPI, populated: dict[str, int]) -> None:
    admin = login(app, ADMIN)
    body = admin.get("/api/v1/admin/users", params={"q": "LAB.te"}).json()
    assert _emails(body) == ["park@lab.test"]
    assert body["total"] == 1
    assert admin.get("/api/v1/admin/users", params={"q": "nobody"}).json() == {
        "items": [],
        "next_cursor": None,
        "total": 0,
    }


def test_search_text_is_literal_not_a_wildcard(app: FastAPI, populated: dict[str, int]) -> None:
    admin = login(app, ADMIN)
    # `%` and `_` would match every user if they reached LIKE unescaped.
    assert admin.get("/api/v1/admin/users", params={"q": "%"}).json()["total"] == 0
    assert admin.get("/api/v1/admin/users", params={"q": "k_m"}).json()["total"] == 0


def test_users_filter_by_role_status_and_verification(
    app: FastAPI,
    populated: dict[str, int],
) -> None:
    admin = login(app, ADMIN)
    get = lambda **params: admin.get("/api/v1/admin/users", params=params).json()  # noqa: E731
    assert _emails(get(role="author")) == ["kim@example.org"]
    assert _emails(get(status="disabled")) == ["gone@example.org"]
    assert _emails(get(verified="false")) == ["new@example.org"]
    assert get(verified="true")["total"] == 5
    assert get(role="learner", status="active")["total"] == 3
    assert get()["total"] == 6
    assert_problem(admin.get("/api/v1/admin/users", params={"role": "owner"}), 422)


def test_cursor_paging_keeps_the_filters_and_the_total(
    app: FastAPI,
    populated: dict[str, int],
) -> None:
    admin = login(app, ADMIN)
    params = {"q": "example.org", "limit": 2}
    first = admin.get("/api/v1/admin/users", params=params).json()
    assert first["total"] == 5  # the admin and four of the five others
    assert len(first["items"]) == 2 and first["next_cursor"]
    seen = _emails(first)
    cursor = first["next_cursor"]
    while cursor:
        page = admin.get("/api/v1/admin/users", params={**params, "cursor": cursor}).json()
        assert page["total"] == 5
        seen += _emails(page)
        cursor = page["next_cursor"]
    assert sorted(seen) == sorted(
        [ADMIN, "kim@example.org", "lee@example.org", "new@example.org", "gone@example.org"]
    )


def test_a_search_is_audited_without_its_text(app: FastAPI, populated: dict[str, int]) -> None:
    admin = login(app, ADMIN)
    admin.get("/api/v1/admin/users", params={"q": "kim@example.org"})
    entry = app.state.rc.auth.list_audit(1, action_prefix="admin.users.viewed")[0]
    assert entry.detail == {"count": 1, "searched": True}


# -- user detail and actions (AC-ADM.3) ----------------------------------------------------


def test_user_overview_shows_sessions_tokens_learning_and_trail(app: FastAPI) -> None:
    admin = user(app, ADMIN)
    learner = user(app, "learner@example.org")
    learner_id = learner.get("/api/v1/me").json()["id"]
    created = learner.post(
        "/api/v1/me/tokens", json={"name": "laptop", "scopes": ["read:progress"]}
    ).json()
    assert learner.post("/api/v1/progress/done", json={"lesson_id": VECTORS}).status_code == 200
    client_for(app).post(
        "/api/v1/auth/login", json={"email": "learner@example.org", "password": "wrong password!!"}
    )

    r = admin.get(f"/api/v1/admin/users/{learner_id}/overview")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["user"]["email"] == "learner@example.org"
    assert len(body["sessions"]) == 1 and body["sessions"][0]["current"] is False
    assert [t["name"] for t in body["tokens"]] == ["laptop"]
    assert body["failed_logins_24h"] == 1
    assert body["learning"]["lessons_done"] == 1
    assert body["learning"]["last_activity_at"] is not None
    actions = [entry["action"] for entry in body["recent_audit"]]
    assert "auth.token.created" in actions  # the user's own action
    # Neither the secret nor any hash leaves the server.
    assert created["token"] not in r.text
    assert "hash" not in r.text
    assert_problem(admin.get("/api/v1/admin/users/99999/overview"), 404)


def test_admin_revokes_every_token_of_a_user(app: FastAPI) -> None:
    admin = user(app, ADMIN)
    learner = user(app, "learner@example.org")
    learner_id = learner.get("/api/v1/me").json()["id"]
    secret = learner.post(
        "/api/v1/me/tokens", json={"name": "ci", "scopes": ["read:progress"]}
    ).json()["token"]
    bot = client_for(app)
    bot.headers["Authorization"] = f"Bearer {secret}"
    assert bot.get("/api/v1/progress/status").status_code == 200

    r = admin.delete(f"/api/v1/admin/users/{learner_id}/tokens")
    assert r.status_code == 200 and r.json() == {"revoked": 1}
    assert bot.get("/api/v1/progress/status").status_code == 401
    assert learner.get("/api/v1/me").status_code == 200  # the browser session is untouched
    assert admin.delete(f"/api/v1/admin/users/{learner_id}/tokens").json() == {"revoked": 0}
    entry = app.state.rc.auth.list_audit(5, action_prefix="auth.tokens.revoked_by_admin")[-1]
    assert (entry.target_id, entry.detail) == (str(learner_id), {"count": 1})
    assert_problem(admin.delete("/api/v1/admin/users/99999/tokens"), 404)


def test_admin_sends_a_password_reset_mail(app: FastAPI, mailer: FakeMailer) -> None:
    admin = user(app, ADMIN)
    learner_id = signup(app, "learner@example.org")["id"]
    sent_before = len(mailer.outbox)
    r = admin.post(f"/api/v1/admin/users/{learner_id}/password-reset")
    assert r.status_code == 202
    assert len(mailer.outbox) == sent_before + 1
    mail = mailer.outbox[-1]
    assert mail.to == "learner@example.org" and "token=" in mail.body
    # The link works, and the operator never saw it in the response.
    assert r.text == ""
    assert "auth.password.reset_sent_by_admin" in audit_actions(app)

    assert (
        admin.patch(f"/api/v1/admin/users/{learner_id}", json={"status": "disabled"}).status_code
        == 200
    )
    assert_problem(admin.post(f"/api/v1/admin/users/{learner_id}/password-reset"), 409)
    assert_problem(admin.post("/api/v1/admin/users/99999/password-reset"), 404)


def test_password_reset_needs_mail(settings: Settings, clock: Clock) -> None:
    app_without_mail = create_app(
        settings, clock=clock, mailer=None, auth_config=AuthConfig(bootstrap_admin_email=ADMIN)
    )
    # Without mail nobody can verify an address, so the bootstrap rule never promotes; an
    # operator uses the CLI path instead (`rc api promote-admin --force`).
    signup(app_without_mail, ADMIN, verify=False)
    app_without_mail.state.rc.auth.promote_admin(ADMIN, Context(), force=True)
    admin = login(app_without_mail, ADMIN)
    assert_problem(admin.post("/api/v1/admin/users/1/password-reset"), 503)
    assert admin.get("/api/v1/admin/overview").json()["system"]["mail_enabled"] is False


# -- audit filters and export (AC-ADM.4) ---------------------------------------------------


def test_audit_filters_by_action_actor_target_and_time(app: FastAPI, clock: Clock) -> None:
    admin = user(app, ADMIN)
    admin_id = admin.get("/api/v1/me").json()["id"]
    learner_id = signup(app, "learner@example.org")["id"]
    clock.advance(hours=1)
    cut = clock.now
    clock.advance(hours=1)
    assert (
        admin.patch(f"/api/v1/admin/users/{learner_id}", json={"role": "author"}).status_code == 200
    )

    def actions(**params: object) -> list[str]:
        r = admin.get("/api/v1/admin/audit", params={"limit": 200, **params})
        assert r.status_code == 200, r.text
        return [item["action"] for item in r.json()["items"]]

    # The bootstrap promotion of the first admin is a role change too, with no actor.
    assert actions(action="user.role") == ["user.role.changed", "user.role.changed"]
    assert actions(action="user.role", actor_user_id=admin_id) == ["user.role.changed"]
    assert set(actions(action="auth.")) and all(
        a.startswith("auth.") for a in actions(action="auth.")
    )
    assert actions(target_type="user", target_id=str(learner_id), action="user.role") == [
        "user.role.changed"
    ]
    assert "user.role.changed" in actions(actor_user_id=admin_id)
    assert "user.role.changed" not in actions(actor_user_id=learner_id)
    # By the admin, to tell it from the bootstrap promotion that happened before the cut.
    assert "user.role.changed" in actions(since=cut.isoformat(), actor_user_id=admin_id)
    assert "user.role.changed" not in actions(until=cut.isoformat(), actor_user_id=admin_id)
    assert actions(since=cut.isoformat(), until=cut.isoformat()) == []
    # A time without an offset is refused rather than read as server time.
    assert_problem(admin.get("/api/v1/admin/audit", params={"since": "2026-11-11T00:00:00"}), 422)


def test_audit_entries_name_the_actor(app: FastAPI) -> None:
    admin = user(app, ADMIN)
    learner_id = signup(app, "learner@example.org")["id"]
    admin.patch(f"/api/v1/admin/users/{learner_id}", json={"role": "author"})
    items = admin.get("/api/v1/admin/audit", params={"action": "user.role"}).json()["items"]
    assert items[0]["actor_email"] == ADMIN
    assert items[-1]["actor_email"] is None  # the bootstrap promotion: a system event
    # A sign-in failure has no actor: the address stays null rather than guessed.
    client_for(app).post(
        "/api/v1/auth/login", json={"email": "x@example.org", "password": "nope nope nope"}
    )
    failed = admin.get("/api/v1/admin/audit", params={"action": "auth.login.failed"}).json()[
        "items"
    ]
    assert failed and failed[0]["actor_email"] is None


def test_audit_export_is_csv_with_the_same_filters(app: FastAPI) -> None:
    admin = user(app, ADMIN)
    learner_id = signup(app, "learner@example.org")["id"]
    admin.patch(f"/api/v1/admin/users/{learner_id}", json={"role": "author"})

    admin_id = admin.get("/api/v1/me").json()["id"]
    r = admin.get(
        "/api/v1/admin/audit/export", params={"action": "user.role", "actor_user_id": admin_id}
    )
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert "attachment" in r.headers["content-disposition"]
    assert r.headers["cache-control"] == "no-store"
    assert r.headers["x-truncated"] == "false"
    rows = list(csv.DictReader(io.StringIO(r.text)))
    assert len(rows) == 1
    row = rows[0]
    assert row["action"] == "user.role.changed"
    assert row["actor_email"] == ADMIN
    assert row["target_id"] == str(learner_id)
    assert row["detail"] == "from=learner; to=author"
    assert datetime.fromisoformat(row["at"]).tzinfo is not None
    assert "admin.audit.exported" in audit_actions(app)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ('=HYPERLINK("http://evil")', '\'=HYPERLINK("http://evil")'),
        ("+1+1", "'+1+1"),
        ("-2", "'-2"),
        ("@SUM(A1)", "'@SUM(A1)"),
        ("\tx", "'\tx"),
        ("user.role.changed", "user.role.changed"),
        ("", ""),
        (None, ""),
        (42, "42"),
    ],
)
def test_csv_cells_cannot_be_formulas(value: object, expected: str) -> None:
    assert csv_cell(value) == expected


def test_a_hostile_user_agent_is_neutralised_in_the_export(app: FastAPI) -> None:
    admin = user(app, ADMIN)
    # The audit detail records what the client sent; a formula there must not survive export.
    service = app.state.rc.auth
    service.store.audit(
        "test.event",
        datetime(2026, 11, 11, 10, 0, tzinfo=UTC),
        actor_user_id=None,
        actor_ip="=cmd|' /C calc'!A0",
        detail={},
    )
    text = admin.get("/api/v1/admin/audit/export", params={"action": "test."}).text
    row = next(csv.DictReader(io.StringIO(text)))
    assert row["actor_ip"].startswith("'=")


def test_local_mode_has_no_operator_console(tmp_path: Path) -> None:
    local = create_app(Settings(curriculum_dir=CURRICULUM, data_dir=tmp_path))
    assert client_for(local).get("/api/v1/admin/overview").status_code == 404

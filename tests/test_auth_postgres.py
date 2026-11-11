"""The auth store on PostgreSQL: Alembic 0003 must produce a schema SqlAuthStore can use.

``SqlAuthStore.from_url`` only calls ``create_all`` for SQLite; on PostgreSQL the schema comes
from Alembic, so these tests migrate a clean database first. That makes a mismatch between
revision 0003 and ``auth.schema`` show up as a failing operation, not just a failing diff
(``test_postgres_store.py::test_auth_migration_matches_auth_schema`` checks the diff).
Skipped together with the other PostgreSQL tests when no server is available.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest

from robotics_curriculum.auth.models import Role, Scope, TokenKind
from robotics_curriculum.auth.store import SqlAuthStore
from robotics_curriculum.progress import postgres as pg

T0 = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)


@pytest.fixture
def auth_store(clean_postgres_url: str) -> Iterator[SqlAuthStore]:
    engine = pg.make_engine(clean_postgres_url)
    pg.upgrade(engine)  # 0001 -> 0003, the only way the auth tables appear on PostgreSQL
    store = SqlAuthStore(engine)
    yield store
    store.close()


def test_schema_from_migration_is_complete(auth_store: SqlAuthStore) -> None:
    assert auth_store.schema_ready() is True


def test_user_session_token_round_trip(auth_store: SqlAuthStore) -> None:
    user = auth_store.create_user("Learner@Example.COM".lower(), "argon2-hash", Role.LEARNER, T0)
    assert user.id is not None
    assert auth_store.get_user(user.id) == user
    # lower(email) unique index: lookup is case-insensitive
    found = auth_store.get_user_by_email("LEARNER@example.com")
    assert found is not None and found.id == user.id
    assert auth_store.password_hash(user.id) == "argon2-hash"
    assert auth_store.count_users() == 1

    session = auth_store.create_session(
        user.id, "tok-hash", "csrf-hash", T0, T0 + timedelta(days=14), "203.0.113.7", "pytest"
    )
    assert auth_store.session_by_token("tok-hash") is not None
    assert [s.id for s in auth_store.list_sessions(user.id, T0)] == [session.id]
    assert auth_store.revoke_session(session.id, T0, user_id=user.id) is True
    revoked = auth_store.session_by_token("tok-hash")
    assert revoked is not None and revoked.revoked_at == T0  # the row stays, marked revoked
    assert auth_store.list_sessions(user.id, T0) == []

    token = auth_store.create_token(
        user.id, "ci", "pat-hash", "rc_abcd", [Scope.READ_PROGRESS], T0, None
    )
    assert auth_store.token_by_hash("pat-hash") is not None
    assert auth_store.revoke_token(token.id, user.id, T0) is True


def test_duplicate_email_is_rejected_by_the_migrated_index(auth_store: SqlAuthStore) -> None:
    auth_store.create_user("dup@example.com", None, Role.LEARNER, T0)
    with pytest.raises(Exception, match=r"(?i)unique|duplicate"):
        auth_store.create_user("dup@example.com", None, Role.LEARNER, T0)


def test_one_time_token_and_login_attempts(auth_store: SqlAuthStore) -> None:
    user = auth_store.create_user("reset@example.com", None, Role.LEARNER, T0)
    auth_store.create_one_time(
        user.id, TokenKind.RESET_PASSWORD, "ott-hash", T0, T0 + timedelta(hours=1)
    )
    assert auth_store.consume_one_time("ott-hash", TokenKind.RESET_PASSWORD, T0) == user.id
    assert (
        auth_store.consume_one_time("ott-hash", TokenKind.RESET_PASSWORD, T0) is None
    )  # single use

    auth_store.record_login("reset@example.com", "203.0.113.7", False, T0)
    auth_store.record_login("reset@example.com", "203.0.113.7", False, T0)
    auth_store.record_login("reset@example.com", "203.0.113.8", True, T0)
    by_email, by_ip = auth_store.failed_logins(
        "reset@example.com", "203.0.113.7", T0 - timedelta(minutes=5)
    )
    assert (by_email, by_ip) == (2, 2)


def test_audit_entries_survive_user_erasure(auth_store: SqlAuthStore) -> None:
    user = auth_store.create_user("gone@example.com", None, Role.LEARNER, T0)
    auth_store.audit(
        "auth.login.success",
        T0,
        actor_user_id=user.id,
        actor_ip="203.0.113.7",
        target_type="user",
        target_id=str(user.id),
        detail={"method": "password"},
        request_id="req-1",
    )
    auth_store.erase_user(user.id, T0 + timedelta(minutes=1))
    # audit_log.actor_user_id has no FK, so the entry outlives the account
    assert [entry.action for entry in auth_store.list_audit(limit=10)] == ["auth.login.success"]

"""Shared fixtures: a real PostgreSQL server for the store contract tests (P2-3).

Order: ``$RC_TEST_DATABASE_URL`` (e.g. a CI service container) if set, else a throwaway
``postgres`` container via testcontainers when the Docker daemon answers. Without either the
PostgreSQL-backed tests are skipped with the reason printed (``pytest -rs``).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Iterator

import pytest

PG_IMAGE = os.environ.get("RC_TEST_POSTGRES_IMAGE", "postgres:16.13")


def _docker_available() -> str | None:
    """``None`` if ``docker info`` succeeds, else the reason it does not."""
    if shutil.which("docker") is None:
        return "docker CLI not found"
    try:
        result = subprocess.run(
            ["docker", "info", "--format", "{{.ServerVersion}}"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"docker info failed: {exc}"
    if result.returncode != 0:
        return f"docker daemon not reachable: {result.stderr.strip()[:200]}"
    return None


@pytest.fixture(scope="session")
def postgres_url() -> Iterator[str]:
    url = os.environ.get("RC_TEST_DATABASE_URL", "").strip()
    if url:
        yield url
        return
    reason = _docker_available()
    if reason is not None:
        pytest.skip(f"PostgreSQL tests skipped: {reason} (or set RC_TEST_DATABASE_URL)")
    from testcontainers.community.postgres import PostgresContainer

    with PostgresContainer(PG_IMAGE, driver="psycopg") as container:
        yield container.get_connection_url()


@pytest.fixture
def clean_postgres_url(postgres_url: str) -> str:
    """The server URL with an empty ``public`` schema (each test starts from nothing)."""
    from sqlalchemy import create_engine, text

    from robotics_curriculum.progress.postgres import dispose_shared_engines, normalize_url

    dispose_shared_engines()  # cached pools would remember the dropped schema as migrated
    engine = create_engine(normalize_url(postgres_url))
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    engine.dispose()
    return postgres_url

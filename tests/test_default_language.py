"""The service answers in English when a request names no language (ADR 0018).

Two different defaults live side by side and must not be confused:

* ``DEFAULT_LANG`` (``ko``) is the language the curriculum is written in and what the CLI and
  the local tools speak. It also is the catalogue every other language falls back to.
* ``SERVICE_DEFAULT_LANG`` (``en``, ``RC_DEFAULT_LANG``) is what the API answers in when there is
  neither ``?lang=`` nor ``Accept-Language``: a crawler, a script, a first-time visitor.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.settings import Settings, SettingsError
from robotics_curriculum.cli import app as cli_app
from robotics_curriculum.i18n import (
    DEFAULT_LANG,
    SERVICE_DEFAULT_LANG,
    parse_accept_language,
    resolve_lang,
)

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "curriculum"
NOW = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)


def _hangul(text: str) -> bool:
    return any("가" <= ch <= "힣" for ch in text)


def _client(tmp_path: Path, **env: str) -> TestClient:
    base = Settings.from_env({"RC_CURRICULUM_DIR": str(CURRICULUM), "RC_DATA_DIR": str(tmp_path)})
    settings = Settings(
        curriculum_dir=base.curriculum_dir,
        data_dir=base.data_dir,
        default_lang=Settings.from_env(env).default_lang,
    )
    return TestClient(create_app(settings, clock=lambda: NOW))


def test_the_two_defaults_are_what_they_say() -> None:
    assert DEFAULT_LANG == "ko"  # authoring language; the CLI's default
    assert SERVICE_DEFAULT_LANG == "en"
    assert Settings.from_env({}).default_lang == "en"
    assert Settings.from_env({"RC_DEFAULT_LANG": " "}).default_lang == "en"
    assert Settings.from_env({"RC_DEFAULT_LANG": "ko"}).default_lang == "ko"
    assert Settings.from_env({"RC_DEFAULT_LANG": "en-US"}).default_lang == "en"
    with pytest.raises(SettingsError):
        Settings.from_env({"RC_DEFAULT_LANG": "fr"})


def test_resolve_lang_takes_the_default_it_is_given() -> None:
    assert resolve_lang(env={}) == "ko"
    assert resolve_lang(env={}, default="en") == "en"
    # An explicit choice and a stated preference still win over any default.
    assert resolve_lang("ko", env={}, default="en") == "ko"
    assert resolve_lang(accept_language="ko-KR,ko;q=0.9", env={}, default="en") == "ko"
    # A language nobody speaks here, or "anything", is the default.
    assert resolve_lang(accept_language="fr", env={}, default="en") == "en"
    assert parse_accept_language("*", "en") == "en"
    assert parse_accept_language("*") == "ko"


def test_a_request_without_a_language_is_answered_in_english(tmp_path: Path) -> None:
    client = _client(tmp_path)
    courses = client.get("/api/v1/courses").json()
    assert courses[0]["lang"] == "en"
    assert not _hangul(courses[0]["title"])
    assert client.get("/api/v1/lessons/nope").json()["title"] == "Not Found"
    lesson = client.get("/api/v1/lessons/m1-vectors-matrices").json()
    assert lesson["lang"] == "en" and not _hangul(lesson["title"])


def test_korean_is_one_header_or_one_parameter_away(tmp_path: Path) -> None:
    client = _client(tmp_path)
    by_header = client.get("/api/v1/courses", headers={"Accept-Language": "ko-KR,ko;q=0.9"})
    assert by_header.json()[0]["lang"] == "ko" and _hangul(by_header.json()[0]["title"])
    by_query = client.get("/api/v1/courses", params={"lang": "ko"})
    assert by_query.json()[0]["lang"] == "ko"
    # The parameter wins over the header: the web caches by URL.
    both = client.get("/api/v1/courses", params={"lang": "ko"}, headers={"Accept-Language": "en"})
    assert both.json()[0]["lang"] == "ko"


def test_an_operator_can_make_korean_the_default_again(tmp_path: Path) -> None:
    client = _client(tmp_path, RC_DEFAULT_LANG="ko")
    courses = client.get("/api/v1/courses").json()
    assert courses[0]["lang"] == "ko" and _hangul(courses[0]["title"])
    assert client.get("/api/v1/courses", params={"lang": "en"}).json()[0]["lang"] == "en"


def test_the_cli_still_speaks_korean_by_default(tmp_path: Path) -> None:
    """The service default is not the tool default: `rc` output is unchanged."""
    result = CliRunner().invoke(
        cli_app,
        ["--data-dir", str(tmp_path), "--curriculum", str(CURRICULUM), "status"],
        env={"RC_LANG": ""},
    )
    assert result.exit_code == 0, result.output
    assert _hangul(result.output)

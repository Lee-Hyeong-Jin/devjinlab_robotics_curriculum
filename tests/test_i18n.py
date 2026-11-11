"""Message catalogues and language selection (P2-6, ADR 0011)."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from robotics_curriculum.i18n import (
    DEFAULT_LANG,
    LANGS,
    Translator,
    get_translator,
    load_catalog,
    normalize_lang,
    parse_accept_language,
    resolve_lang,
    translator,
)
from robotics_curriculum.i18n.catalog import LOCALES_DIR, _flatten

# -- catalogues ----------------------------------------------------------------


def test_every_language_has_a_locale_file() -> None:
    for lang in LANGS:
        assert (LOCALES_DIR / f"{lang}.yaml").is_file()
    assert DEFAULT_LANG == "ko"


def test_catalogues_share_the_same_keys() -> None:
    korean = set(load_catalog("ko"))
    english = set(load_catalog("en"))
    assert korean, "the Korean catalogue must not be empty"
    assert korean - english == set(), f"missing in en.yaml: {sorted(korean - english)}"
    assert english - korean == set(), f"not in ko.yaml: {sorted(english - korean)}"


def test_nested_yaml_is_flattened_to_dotted_keys() -> None:
    catalog = load_catalog("ko")
    assert catalog["cli.timer.none"] == "열린 타이머: 없음"
    assert "cli" not in catalog  # only leaves become keys
    assert _flatten({"a": {"b": "x"}, "c": "y"}) == {"a.b": "x", "c": "y"}


def test_non_string_leaves_are_dropped_with_a_warning(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING):
        assert _flatten({"a": 3, "b": "ok"}) == {"b": "ok"}
    assert "ignoring non-string value at 'a'" in caplog.text


def test_templates_only_use_named_parameters() -> None:
    import string

    for lang in LANGS:
        for key, template in load_catalog(lang).items():
            for _, field, _, _ in string.Formatter().parse(template):
                assert field is None or field.isidentifier(), f"{lang}:{key} uses {field!r}"


# -- translation ---------------------------------------------------------------


def test_translate_and_interpolate() -> None:
    korean = translator("ko")
    english = translator("en")
    assert korean("cli.timer.none") == "열린 타이머: 없음"
    assert english("cli.timer.none") == "Running timer: none"
    assert korean("quiz.score", correct=3, total=4, percent=75, wrong=1).startswith("결과 3/4")
    assert english("quiz.score", correct=3, total=4, percent=75, wrong=1).startswith("score 3/4")


def test_translator_is_cached_per_language() -> None:
    assert translator("ko") is translator("ko")
    assert translator("ko") is not translator("en")
    assert translator("ko").lang == "ko"
    assert repr(translator("en")) == "Translator('en')"


def test_missing_key_falls_back_to_korean_then_to_the_key(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    english = Translator("en")
    monkeypatch.setattr(english, "_catalog", {}, raising=False)
    monkeypatch.setattr(english, "_fallback", {"cli.no_record": "기록 없음"}, raising=False)
    with caplog.at_level(logging.WARNING):
        assert english("cli.no_record") == "기록 없음"
    assert "is missing from en" in caplog.text

    caplog.clear()
    with caplog.at_level(logging.WARNING):
        assert english("nope.unknown") == "nope.unknown"
    assert "unknown message key 'nope.unknown'" in caplog.text


def test_bad_format_parameters_return_the_template(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING):
        assert (
            translator("ko")("cli.timer.running", wrong_name=1)
            == load_catalog("ko")["cli.timer.running"]
        )
    assert "cannot format" in caplog.text


def test_unreadable_locale_yields_an_empty_catalogue(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr("robotics_curriculum.i18n.catalog.LOCALES_DIR", tmp_path)
    load_catalog.cache_clear()
    with caplog.at_level(logging.WARNING):
        assert load_catalog("en") == {}
    assert "cannot read" in caplog.text
    load_catalog.cache_clear()  # restore for the other tests


# -- language selection --------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("ko", "ko"),
        ("EN", "en"),
        ("en-US", "en"),
        ("en_us", "en"),
        ("  ko-KR  ", "ko"),
        ("fr", None),
        ("", None),
        (None, None),
    ],
)
def test_normalize_lang(value: str | None, expected: str | None) -> None:
    assert normalize_lang(value) == expected


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        ("en", "en"),
        ("en-GB,en;q=0.9", "en"),
        ("fr-FR,fr;q=0.9,en;q=0.5", "en"),
        ("ko-KR,ko;q=0.9,en;q=0.8", "ko"),
        ("en;q=0.4,ko;q=0.8", "ko"),
        ("*", "ko"),
        ("fr", None),
        ("en;q=0", None),
        ("en;q=bad", None),
        ("", None),
        (None, None),
        ("!!!", None),
    ],
)
def test_parse_accept_language(header: str | None, expected: str | None) -> None:
    assert parse_accept_language(header) == expected


def test_resolve_lang_precedence() -> None:
    env = {"RC_LANG": "en"}
    assert resolve_lang("ko", env=env) == "ko"  # explicit wins
    assert resolve_lang(None, env=env) == "en"  # then the environment
    assert resolve_lang("fr", env=env) == "en"  # an unknown explicit value is ignored
    assert resolve_lang(None, accept_language="en", env={}) == "en"
    assert resolve_lang(None, env={"RC_LANG": "ko"}, accept_language="en") == "ko"
    assert resolve_lang(None, env={}) == "ko"  # default
    assert resolve_lang(None, accept_language="fr", env={}) == "ko"


def test_get_translator_resolves_and_caches() -> None:
    assert get_translator("en", env={}).lang == "en"
    assert get_translator(None, accept_language="en-US", env={}) is translator("en")

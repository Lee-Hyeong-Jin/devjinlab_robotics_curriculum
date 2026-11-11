"""Message catalogues: user-facing strings in Korean and English (PRD FR-9, P2-6).

A catalogue is one YAML file per language under ``locales/``, nested for readability and
flattened to dotted keys on load (``cli.timer.none``). Values are :meth:`str.format` templates,
so a message takes named parameters: ``t("cli.quiz.score", correct=3, total=4)``.

Lookup never raises: a key missing from the selected language falls back to Korean (the source
language) and then to the key itself, with a warning logged, so a half-translated catalogue
degrades instead of breaking a command. See ``docs/adr/0011-i18n-message-catalog.md``.
"""

from __future__ import annotations

import logging
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal, get_args

import yaml

Lang = Literal["ko", "en"]
LANGS: tuple[Lang, ...] = get_args(Lang)
DEFAULT_LANG: Lang = "ko"
LANG_ENV = "RC_LANG"
LOCALES_DIR = Path(__file__).parent / "locales"

logger = logging.getLogger(__name__)

# "ko-KR;q=0.9" -> tag "ko-KR", quality 0.9
_ACCEPT_PART = re.compile(r"^(?P<tag>[A-Za-z*][A-Za-z0-9-]*)(?:;\s*q=(?P<q>[0-9.]+))?$")


def _flatten(data: object, prefix: str = "") -> dict[str, str]:
    """``{"cli": {"ok": "좋아"}}`` -> ``{"cli.ok": "좋아"}``; non-string leaves are dropped."""
    flat: dict[str, str] = {}
    if isinstance(data, dict):
        for key, value in data.items():
            flat.update(_flatten(value, f"{prefix}{key}."))
        return flat
    if isinstance(data, str):
        flat[prefix.rstrip(".")] = data
    elif data is not None:
        logger.warning("i18n: ignoring non-string value at '%s'", prefix.rstrip("."))
    return flat


@lru_cache(maxsize=len(LANGS))
def load_catalog(lang: Lang) -> dict[str, str]:
    """Flat ``{key: template}`` for one language (cached; ``yaml.safe_load``)."""
    path = LOCALES_DIR / f"{lang}.yaml"
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:  # a broken locale must not break the program
        logger.warning("i18n: cannot read %s (%s); falling back to keys", path, exc)
        return {}
    return _flatten(raw)


def normalize_lang(value: str | None) -> Lang | None:
    """``"EN"``, ``"en-US"``, ``"en_us"`` -> ``"en"``; unknown or empty -> ``None``."""
    if not value:
        return None
    tag = value.strip().lower().replace("_", "-").split("-")[0]
    for lang in LANGS:  # a loop keeps the Literal type without a cast
        if tag == lang:
            return lang
    return None


def parse_accept_language(header: str | None) -> Lang | None:
    """Best supported language of an ``Accept-Language`` header, honouring ``q`` weights."""
    if not header:
        return None
    ranked: list[tuple[float, int, Lang]] = []
    for position, part in enumerate(header.split(",")):
        match = _ACCEPT_PART.match(part.strip())
        if match is None:
            continue
        try:
            quality = float(match["q"]) if match["q"] is not None else 1.0
        except ValueError:
            continue
        if quality <= 0:
            continue
        if match["tag"] == "*":
            ranked.append((quality, position, DEFAULT_LANG))
            continue
        lang = normalize_lang(match["tag"])
        if lang is not None:
            ranked.append((quality, position, lang))
    if not ranked:
        return None
    # highest quality first; ties keep the header's order
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return ranked[0][2]


def resolve_lang(
    explicit: str | None = None,
    *,
    accept_language: str | None = None,
    env: dict[str, str] | None = None,
) -> Lang:
    """Pick a language: ``explicit`` (``--lang``) > ``RC_LANG`` > ``Accept-Language`` > Korean."""
    environ = os.environ if env is None else env
    for candidate in (explicit, environ.get(LANG_ENV)):
        chosen = normalize_lang(candidate)
        if chosen is not None:
            return chosen
    return parse_accept_language(accept_language) or DEFAULT_LANG


class Translator:
    """Looks messages up in one language, falling back to Korean and then to the key."""

    __slots__ = ("lang", "_catalog", "_fallback")

    def __init__(self, lang: Lang = DEFAULT_LANG) -> None:
        self.lang = lang
        self._catalog = load_catalog(lang)
        self._fallback = load_catalog(DEFAULT_LANG) if lang != DEFAULT_LANG else self._catalog

    def template(self, key: str) -> str:
        """The raw template for ``key`` (the key itself when it is missing everywhere)."""
        found = self._catalog.get(key)
        if found is not None:
            return found
        found = self._fallback.get(key)
        if found is not None:
            logger.warning("i18n: '%s' is missing from %s; using %s", key, self.lang, DEFAULT_LANG)
            return found
        logger.warning("i18n: unknown message key '%s'", key)
        return key

    def __call__(self, key: str, /, **params: Any) -> str:
        """Translate ``key`` and interpolate ``params``."""
        template = self.template(key)
        if not params:
            return template
        try:
            return template.format(**params)
        except (KeyError, IndexError, ValueError) as exc:
            logger.warning("i18n: cannot format '%s' (%s)", key, exc)
            return template

    def __repr__(self) -> str:
        return f"Translator({self.lang!r})"


@lru_cache(maxsize=len(LANGS))
def translator(lang: Lang = DEFAULT_LANG) -> Translator:
    """A cached :class:`Translator` (catalogues are immutable at runtime)."""
    return Translator(lang)


def get_translator(
    explicit: str | None = None,
    *,
    accept_language: str | None = None,
    env: dict[str, str] | None = None,
) -> Translator:
    """:func:`resolve_lang` followed by :func:`translator`."""
    return translator(resolve_lang(explicit, accept_language=accept_language, env=env))

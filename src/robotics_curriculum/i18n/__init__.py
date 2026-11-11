"""User-facing message catalogues and language selection (ko default, en available)."""

from robotics_curriculum.i18n.catalog import (
    DEFAULT_LANG,
    LANG_ENV,
    LANGS,
    Lang,
    Translator,
    get_translator,
    load_catalog,
    normalize_lang,
    parse_accept_language,
    resolve_lang,
    translator,
)

__all__ = [
    "DEFAULT_LANG",
    "LANGS",
    "LANG_ENV",
    "Lang",
    "Translator",
    "get_translator",
    "load_catalog",
    "normalize_lang",
    "parse_accept_language",
    "resolve_lang",
    "translator",
]

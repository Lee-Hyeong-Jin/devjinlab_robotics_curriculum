"""Find Korean text in output that is supposed to be in another language (FR-9).

The English build of the API, the static site, the CLI and the web app must not show
Korean. This module is the single detector those checks share: :func:`find_hangul` on a
string, :func:`scan_json` on an API response, :func:`html_text` to strip markup first.

Proper nouns that are *meant* to stay Korean (the ``한국어`` label of the language picker,
an author's name, a quoted Korean source) are handled by the caller's allow list, not here.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass

__all__ = ["Finding", "find_hangul", "has_hangul", "html_text", "iter_json_strings", "scan_json"]

# Hangul syllables, Jamo, and compatibility Jamo. Anything in these blocks is Korean text.
HANGUL = re.compile(r"[가-힣ᄀ-ᇿ㄰-㆏ꥠ-꥿ힰ-퟿]+")

_SCRIPT_OR_STYLE = re.compile(r"<(script|style)\b[^>]*>.*?</\1\s*>", re.IGNORECASE | re.DOTALL)
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_TAG = re.compile(r"<[^>]+>")
_ENTITY = re.compile(r"&(#\d+|#x[0-9a-fA-F]+|[a-zA-Z]+);")


@dataclass(frozen=True, slots=True)
class Finding:
    """One place Korean text was found: where it is, and the text around it."""

    where: str
    """A JSON pointer, file path, or other locator the caller understands."""
    text: str
    """The Korean run that matched."""
    context: str
    """Up to ~120 characters around the match, for the report."""

    def __str__(self) -> str:
        return f"{self.where}: {self.context}"


def find_hangul(text: str) -> list[str]:
    """Every run of Korean characters in ``text`` (empty when there is none)."""
    return HANGUL.findall(text)


def has_hangul(text: str) -> bool:
    """True when ``text`` contains any Korean character."""
    return HANGUL.search(text) is not None


def _context(text: str, start: int, end: int, width: int = 60) -> str:
    snippet = text[max(0, start - width) : end + width]
    return " ".join(snippet.split())


def scan_text(text: str, where: str) -> list[Finding]:
    """Findings for one string, one per Korean run."""
    return [
        Finding(where, match.group(), _context(text, match.start(), match.end()))
        for match in HANGUL.finditer(text)
    ]


def iter_json_strings(data: object, pointer: str = "") -> Iterator[tuple[str, str]]:
    """Walk decoded JSON yielding ``(json_pointer, string_value)`` for every string.

    Object keys are walked as well, since a key is as visible as a value in a response
    that a client renders generically.
    """
    if isinstance(data, str):
        yield pointer or "/", data
    elif isinstance(data, dict):
        for key, value in data.items():
            child = f"{pointer}/{key}"
            if isinstance(key, str) and has_hangul(key):
                yield f"{child} (key)", key
            yield from iter_json_strings(value, child)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            yield from iter_json_strings(item, f"{pointer}/{index}")


def scan_json(data: object, where: str = "") -> list[Finding]:
    """Findings for every Korean string inside a decoded JSON document."""
    findings: list[Finding] = []
    for pointer, value in iter_json_strings(data):
        findings += [
            Finding(f"{where}{pointer}", f.text, f.context) for f in scan_text(value, pointer)
        ]
    return findings


def html_text(html: str) -> str:
    """Visible text of an HTML document: scripts, styles, comments and tags removed."""
    without_code = _SCRIPT_OR_STYLE.sub(" ", html)
    without_comments = _COMMENT.sub(" ", without_code)
    text = _TAG.sub(" ", without_comments)
    return _ENTITY.sub(" ", text)

"""Allowlist sanitizer for the rendered site HTML (PRD appendix C.0, AC-SEC.1).

Lesson Markdown is untrusted input: it arrives through pull requests and may contain raw
HTML, which Python-Markdown passes through verbatim. Every page's rendered content is
therefore cleaned with :mod:`nh3` (bindings for the Rust *ammonia* sanitizer) before
MkDocs writes it to disk, which drops ``<script>``, event handlers and ``javascript:``
links while keeping the markup the content and the theme legitimately use.

The allowlist covers Markdown output plus what this project's own renderers and the
enabled extensions emit (admonitions, details, tables, task lists, highlighted code,
KaTeX spans, and the ``rc-*`` elements from :mod:`robotics_curriculum.site.pages`).
``style`` is deliberately *not* allowed anywhere: the progress bars use width classes
instead, so no attribute can carry CSS (and with it a remote URL) into a page.
"""

from __future__ import annotations

import nh3

#: Markdown and extension output, plus ``input`` for task-list checkboxes.
ALLOWED_TAGS: frozenset[str] = frozenset(
    nh3.ALLOWED_TAGS | {"input", "label", "section", "nav", "button"}
)

#: Attributes allowed on any tag. ``class`` and ``id`` carry styling and anchors.
GENERIC_ATTRIBUTES: frozenset[str] = frozenset({"class", "id", "title", "dir", "lang", "role"})

ALLOWED_ATTRIBUTES: dict[str, set[str]] = {
    "*": set(GENERIC_ATTRIBUTES),
    # "rel" is managed by nh3's link_rel (noopener noreferrer), so it is not listed here.
    "a": {"href", "hreflang", "name", "target"},
    "img": {"src", "alt", "width", "height", "loading"},
    "input": {"type", "checked", "disabled"},
    "td": {"colspan", "rowspan", "align"},
    "th": {"colspan", "rowspan", "align", "scope"},
    "ol": {"start", "reversed"},
    "details": {"open"},
    "time": {"datetime"},
}

#: Link schemes that may survive sanitizing (``javascript:`` is not one of them).
URL_SCHEMES: frozenset[str] = frozenset({"http", "https", "mailto"})


def clean(html: str) -> str:
    """Return ``html`` with everything outside the allowlist removed."""
    return nh3.clean(
        html,
        tags=set(ALLOWED_TAGS),
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes=set(URL_SCHEMES),
        strip_comments=True,
    )

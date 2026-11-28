"""Three conventions inside a lesson body, beyond plain Markdown.

* **Where you will use this** — a ``## `` section near the top that opens the lesson with one
  concrete robot situation: the robot, the task, and what goes wrong without this lesson.
  Readers asked for it: a lesson that opens with the mathematics scares people away.
* **Expected result** — a fenced ```` ```expected ```` block after an exercise, holding the
  numbers or the qualitative outcome a correct attempt gives. A self-learner has nobody to ask
  whether their answer is right. Screens show it folded, so it is not a spoiler.
* **Figures** — ``![alt text](figures/<name>.svg)``: an image file kept in a ``figures``
  directory next to the lesson, always with alt text.

Pure functions over Markdown text; the loader, the validator and the renderers build on them.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass

from robotics_curriculum.i18n import DEFAULT_LANG, translator

USE_CASE_KEY = "lesson.use_case"
EXPECTED_KEY = "lesson.expected"
FIGURES_DIRNAME = "figures"
FIGURE_SUFFIXES = (".svg", ".png")
FIGURE_MAX_BYTES = 300_000

_FENCE = re.compile(r"^\s{0,3}(?P<fence>`{3,}|~{3,})\s*(?P<info>[^\s`]*)")
_IMAGE = re.compile(
    r"!\[(?P<alt>[^\]]*)\]\(\s*<?(?P<target>[^)\s<>]+)>?(?:\s+[\"'][^\"']*[\"'])?\s*\)"
)
_FIGURE_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*\.(?:svg|png)$")
EXPECTED_INFO = "expected"


def use_case_headings(lang: str | None = None) -> list[str]:
    """Headings that mark the use-case section: the one for ``lang``, then the Korean one."""
    headings = [translator(DEFAULT_LANG)(USE_CASE_KEY)]
    if lang and lang != DEFAULT_LANG:
        headings.insert(0, translator(lang)(USE_CASE_KEY))
    return list(dict.fromkeys(headings))


def has_use_case(body: str, lang: str | None = None) -> bool:
    """Whether the body has a non-empty ``## Where you will use this`` section."""
    from robotics_curriculum.content.sections import extract_section

    return any(bool(extract_section(body, heading)) for heading in use_case_headings(lang))


def _blocks(body: str) -> Iterator[tuple[str, list[str]]]:
    """``(info, lines)`` of each fenced block, in order; an unterminated one runs to the end."""
    info: str | None = None
    closing = ""
    lines: list[str] = []
    for line in body.splitlines():
        match = _FENCE.match(line)
        if info is None:
            if match:
                info, closing, lines = match["info"].lower(), match["fence"], []
            continue
        if match and match["fence"][0] == closing[0] and len(match["fence"]) >= len(closing):
            if not match["info"]:
                yield info, lines
                info = None
                continue
        lines.append(line)
    if info is not None:
        yield info, lines


def extract_expected(body: str) -> list[str]:
    """The Markdown of every ```` ```expected ```` block, in order (stripped; may be empty)."""
    return ["\n".join(lines).strip() for info, lines in _blocks(body) if info == EXPECTED_INFO]


@dataclass(frozen=True, slots=True)
class ImageRef:
    alt: str
    target: str

    @property
    def is_figure(self) -> bool:
        """A file under the lesson's ``figures`` directory, as opposed to a web address."""
        return "://" not in self.target and not self.target.startswith(("#", "/", "mailto:"))

    @property
    def figure_name(self) -> str | None:
        """``frames.svg`` for ``figures/frames.svg``; ``None`` when the path is not that shape."""
        prefix = f"{FIGURES_DIRNAME}/"
        if not self.target.startswith(prefix):
            return None
        name = self.target[len(prefix) :]
        return name if _FIGURE_NAME.match(name) else None


def image_refs(body: str) -> list[ImageRef]:
    """Every Markdown image outside fenced code, in order."""
    found: list[ImageRef] = []
    fence: str | None = None
    for line in body.splitlines():
        marker = _FENCE.match(line)
        if marker:
            char = marker["fence"][0]
            if fence is None:
                fence = char
            elif char == fence:
                fence = None
            continue
        if fence is not None:
            continue
        found.extend(
            ImageRef(match["alt"].strip(), match["target"]) for match in _IMAGE.finditer(line)
        )
    return found


#: What an SVG must not contain to be served from this site: it is shown through ``<img>``,
#: which runs no script, but a file that carries one has no business in the curriculum.
_SVG_FORBIDDEN = re.compile(
    rb"<\s*script|\son[a-z]+\s*=|<\s*foreignObject|javascript:|<\s*iframe|<\s*embed", re.IGNORECASE
)
_SVG_EXTERNAL = re.compile(rb"(?:href|src)\s*=\s*[\"']\s*(?:https?:)?//", re.IGNORECASE)


def svg_problem(data: bytes) -> str | None:
    """Why an SVG file is not acceptable, or ``None`` when it is."""
    if b"<svg" not in data[:2000]:
        return "is not an SVG document"
    if _SVG_FORBIDDEN.search(data):
        return "contains script, an event handler or embedded foreign content"
    if _SVG_EXTERNAL.search(data):
        return "loads something from another site"
    return None

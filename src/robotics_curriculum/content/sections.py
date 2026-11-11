"""Pull a ``## `` section out of a lesson's Markdown body."""

from __future__ import annotations

from robotics_curriculum.i18n import DEFAULT_LANG, translator

STUDY_GUIDE_HEADING = "이 단계 공부법"


def study_guide_headings(lang: str | None = None) -> list[str]:
    """Headings that mark the study-guide section: the one for ``lang``, then the Korean one.

    A translated body (``<lesson>.en.md``) writes the heading in its own language, so the
    section is looked up by the catalogue entry of that language first.
    """
    headings = [STUDY_GUIDE_HEADING]
    if lang and lang != DEFAULT_LANG:
        headings.insert(0, translator(lang)("lesson.study_guide"))
    return list(dict.fromkeys(headings))


def extract_study_guide(body: str, lang: str | None = None) -> str | None:
    """The "how to study this stage" section of ``body``, whatever language it is written in."""
    for heading in study_guide_headings(lang):
        section = extract_section(body, heading)
        if section is not None:
            return section
    return None


def extract_section(body: str, heading: str) -> str | None:
    """Return the Markdown under ``## <heading>`` up to the next ``## `` heading.

    ``heading`` may be given with or without the leading ``## ``. Deeper headings
    (``###``) stay inside the section; lines in fenced code blocks are never treated
    as headings. Returns ``None`` when the heading is absent, else the stripped text
    (possibly ``""``).
    """
    target = heading.removeprefix("##").strip()
    collected: list[str] | None = None
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
        elif not in_fence and line.startswith("## "):
            if collected is not None:
                break
            if line[3:].strip().rstrip("#").strip() == target:
                collected = []
                continue
        if collected is not None:
            collected.append(line)
    return None if collected is None else "\n".join(collected).strip()

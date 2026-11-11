"""Pull a ``## `` section out of a lesson's Markdown body."""

from __future__ import annotations

STUDY_GUIDE_HEADING = "이 단계 공부법"


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

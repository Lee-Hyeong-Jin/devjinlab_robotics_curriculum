"""Simple full-text search over loaded content: lessons and their resources.

In-memory over the content index, so it behaves the same with SQLite or PostgreSQL progress
stores. Every query word must appear (case-insensitive, Unicode-aware) in the hit's text.
Ranking: title matches first, then tags, then other fields; ties keep course order.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

from robotics_curriculum.content.models import Course

SNIPPET_CHARS = 120


@dataclass(frozen=True, slots=True)
class SearchHit:
    kind: Literal["lesson", "resource"]
    id: str
    title: str
    snippet: str
    lesson_id: str
    score: int


def _norm(text: str) -> str:
    return text.casefold()


def _words(query: str) -> list[str]:
    return [w for w in _norm(query).split() if w]


def _snippet(fields: Iterable[str], words: list[str]) -> str:
    """The first field containing a query word, trimmed around the first match."""
    for text in fields:
        low = _norm(text)
        positions = [low.find(w) for w in words if w in low]
        if positions:
            start = max(0, min(positions) - 30)
            piece = text[start : start + SNIPPET_CHARS].strip()
            return (
                ("…" if start else "") + piece + ("…" if start + SNIPPET_CHARS < len(text) else "")
            )
    return ""


def _score(words: list[str], title: str, tags: list[str], rest: list[str]) -> int | None:
    """Sum of per-word weights (title 3, tag 2, other 1); ``None`` if a word is missing."""
    title_n, tags_n, rest_n = _norm(title), [_norm(t) for t in tags], [_norm(r) for r in rest]
    total = 0
    for word in words:
        if word in title_n:
            total += 3
        elif any(word in t for t in tags_n):
            total += 2
        elif any(word in r for r in rest_n):
            total += 1
        else:
            return None
    return total


def search(courses: list[Course], query: str, *, limit: int = 20) -> list[SearchHit]:
    """Lessons (title, summary, objectives, tags) and resources (title, note, kind)."""
    words = _words(query)
    if not words:
        return []
    hits: list[SearchHit] = []
    for course in courses:
        for module in course.modules:
            for lesson in module.lessons:
                rest = [lesson.summary, *lesson.objectives, lesson.id]
                score = _score(words, lesson.title, lesson.tags, rest)
                if score is not None:
                    hits.append(
                        SearchHit(
                            kind="lesson",
                            id=lesson.id,
                            title=lesson.title,
                            snippet=_snippet([lesson.summary, *lesson.objectives], words),
                            lesson_id=lesson.id,
                            score=score,
                        )
                    )
                for i, res in enumerate(lesson.resources):
                    kind = res.kind.value if res.kind else ""
                    rest = [res.note or "", res.url or "", kind]
                    score = _score(words, res.title, [], rest)
                    if score is not None:
                        hits.append(
                            SearchHit(
                                kind="resource",
                                id=f"{lesson.id}#{i}",
                                title=res.title,
                                snippet=_snippet([res.note or "", res.title], words),
                                lesson_id=lesson.id,
                                score=score,
                            )
                        )
    hits.sort(key=lambda h: -h.score)  # stable: equal scores keep course order
    return hits[:limit]

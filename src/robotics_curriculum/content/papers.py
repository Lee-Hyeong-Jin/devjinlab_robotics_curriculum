"""Resolving a lesson's paper references against its course's ``papers.yaml`` registry.

The split is deliberate (ADR 0014): the registry is the *bibliography* (who wrote what,
where, and whether the link was checked) and the lesson decides *which* papers it assigns
and whether they are required. So nothing here is the source of truth — it merges the two
into the :class:`LessonPaper` rows the CLI, the API and the site show.
"""

from __future__ import annotations

from robotics_curriculum.content.models import Course, Lesson, LessonPaper, Paper


def paper_index(course: Course) -> dict[str, Paper]:
    """The course's registry by id. The first entry wins; duplicates are a validation error."""
    index: dict[str, Paper] = {}
    for paper in course.papers:
        index.setdefault(paper.id, paper)
    return index


def resolve_lesson_papers(
    lesson: Lesson, index: dict[str, Paper], lang: str | None = None
) -> list[LessonPaper]:
    """The lesson's papers in its own order, required ones first within that order.

    ``lang`` picks the translated ``note`` from ``<lesson>.<lang>.yaml`` when there is one.
    Nothing else is translated — the title, authors and venue are the published bibliography.

    A reference whose id is not in the registry is skipped: ``rc validate`` reports it as an
    error, and a half-built row with no title would be worse than leaving it out.
    """
    rows: list[LessonPaper] = []
    for ref in lesson.localized_papers(lang):
        paper = index.get(ref.id)
        if paper is None:
            continue
        rows.append(
            LessonPaper(
                id=paper.id,
                title=paper.title,
                authors=list(paper.authors),
                year=paper.year,
                venue=paper.venue,
                url=paper.url,
                verified=paper.verified,
                # The lesson's role wins: the same paper is seminal in one lesson and the
                # thing being criticised in another.
                role=ref.role or paper.role,
                required=ref.required,
                note=ref.note or paper.note,
            )
        )
    # Required reading first, otherwise the author's order. `sorted` is stable, so the
    # lesson's ordering survives inside each group.
    return sorted(rows, key=lambda row: not row.required)


def citation(paper: LessonPaper | Paper) -> str:
    """``Mayne et al. (1966), International Journal of Control`` — the one-line list form.

    Empty parts are dropped, so a registry entry with only a title still renders.
    """
    authors = list(paper.authors)
    if not authors:
        who = ""
    elif len(authors) == 1:
        who = authors[0]
    elif len(authors) == 2:
        who = f"{authors[0]} & {authors[1]}"
    else:
        who = f"{authors[0]} et al."
    head = (
        f"{who} ({paper.year})"
        if who and paper.year
        else who or (f"({paper.year})" if paper.year else "")
    )
    parts = [part for part in (head, paper.venue) if part]
    return ", ".join(parts)

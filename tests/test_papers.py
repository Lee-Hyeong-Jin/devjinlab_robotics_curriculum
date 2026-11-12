"""Course paper registry and lesson paper references (ADR 0014, lesson-standard.md §11-1)."""

from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from robotics_curriculum.cli import app
from robotics_curriculum.content import (
    Course,
    LessonPaper,
    citation,
    load_course,
    paper_index,
    resolve_lesson_papers,
    validate_course,
)

runner = CliRunner()

REGISTRY = {
    "papers": [
        {
            "id": "mayne-1966",
            "title": "A second-order gradient method",
            "authors": ["D. Q. Mayne"],
            "year": 1966,
            "venue": "International Journal of Control",
            "url": "https://doi.org/10.1080/00207176608921369",
            "verified": True,
            "role": "seminal",
        },
        {
            "id": "todorov-2005",
            "title": "A generalized iterative LQG method",
            "authors": ["E. Todorov", "W. Li"],
            "year": 2005,
            "url": "https://example.org/ilqg",
            "verified": False,
        },
    ]
}


def write_course(
    root: Path,
    *,
    lesson_front: str = "",
    registry: dict[str, object] | None = REGISTRY,
) -> Path:
    course = root / "course"
    module = course / "mod"
    module.mkdir(parents=True)
    (course / "course.yaml").write_text(
        "id: course\ntitle: Course\nsummary: S\nmodules: [mod]\n", encoding="utf-8"
    )
    (module / "module.yaml").write_text(
        "id: mod\ntitle: Module\nsummary: S\nlessons: [l1]\n", encoding="utf-8"
    )
    (module / "l1.md").write_text(
        "---\n"
        "id: l1\ntitle: Lesson\nsummary: S\nobjectives: [O]\n"
        "difficulty: 3\nestimated_minutes: 60\n" + lesson_front + "---\n\n# L\n\nBody.\n",
        encoding="utf-8",
    )
    if registry is not None:
        (course / "papers.yaml").write_text(
            yaml.safe_dump(registry, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
    return course


ASSIGNS_BOTH = (
    "papers:\n"
    "  - id: mayne-1966\n"
    "    required: true\n"
    '    note: "§3 only"\n'
    "  - id: todorov-2005\n"
    "    role: critique\n"
)


# -- loading ---


def test_a_course_without_a_registry_still_loads(tmp_path: Path) -> None:
    """Every course that predates the research track has no papers.yaml."""
    course = load_course(write_course(tmp_path, registry=None))
    assert course.papers == []
    assert validate_course(course) == []


def test_the_registry_is_loaded_and_indexed(tmp_path: Path) -> None:
    course = load_course(write_course(tmp_path))
    assert [p.id for p in course.papers] == ["mayne-1966", "todorov-2005"]
    index = paper_index(course)
    assert index["mayne-1966"].venue == "International Journal of Control"
    assert index["todorov-2005"].verified is False


def test_a_malformed_registry_is_an_error_not_a_crash(tmp_path: Path) -> None:
    course_dir = write_course(tmp_path, registry={"papers": [{"id": "no-title"}]})
    try:
        load_course(course_dir)
    except Exception as exc:  # LoadError carries one entry per problem
        assert "title" in str(exc)
    else:
        raise AssertionError("a paper without a title should not load")


# -- resolution: registry is bibliography, lesson is editorial ---


def test_the_lessons_role_overrides_the_registry_default(tmp_path: Path) -> None:
    course = load_course(write_course(tmp_path, lesson_front=ASSIGNS_BOTH))
    rows = resolve_lesson_papers(course.iter_lessons()[0], paper_index(course))
    by_id = {row.id: row for row in rows}
    # mayne has no role on the reference, so the registry's `seminal` stands.
    assert by_id["mayne-1966"].role == "seminal"
    # todorov has no registry role and the lesson calls it a critique.
    assert by_id["todorov-2005"].role == "critique"


def test_required_reading_comes_first_and_keeps_the_authors_order(tmp_path: Path) -> None:
    front = "papers:\n  - id: todorov-2005\n  - id: mayne-1966\n    required: true\n"
    course = load_course(write_course(tmp_path, lesson_front=front))
    rows = resolve_lesson_papers(course.iter_lessons()[0], paper_index(course))
    assert [row.id for row in rows] == ["mayne-1966", "todorov-2005"]
    assert [row.required for row in rows] == [True, False]


def test_the_lessons_note_wins_over_the_registry_note(tmp_path: Path) -> None:
    registry = {"papers": [{**REGISTRY["papers"][0], "note": "whole paper"}]}
    course = load_course(
        write_course(
            tmp_path,
            lesson_front='papers:\n  - id: mayne-1966\n    required: true\n    note: "§3 only"\n',
            registry=registry,
        )
    )
    rows = resolve_lesson_papers(course.iter_lessons()[0], paper_index(course))
    assert rows[0].note == "§3 only"


def test_the_bibliography_travels_with_the_reference(tmp_path: Path) -> None:
    course = load_course(write_course(tmp_path, lesson_front=ASSIGNS_BOTH))
    row = resolve_lesson_papers(course.iter_lessons()[0], paper_index(course))[0]
    assert row.title.startswith("A second-order")
    assert row.authors == ["D. Q. Mayne"]
    assert row.year == 1966 and row.verified is True


# -- validation (rule 10) ---


def messages(course: Course) -> list[str]:
    return [p.message for p in validate_course(course)]


def test_a_reference_to_a_missing_paper_is_an_error(tmp_path: Path) -> None:
    course = load_course(
        write_course(tmp_path, lesson_front="papers:\n  - id: ghost\n    required: true\n")
    )
    problems = validate_course(course)
    assert any("references paper 'ghost'" in p.message and p.blocking for p in problems)


def test_a_duplicate_registry_id_is_an_error(tmp_path: Path) -> None:
    registry = {"papers": [REGISTRY["papers"][0], REGISTRY["papers"][0]]}
    course = load_course(
        write_course(
            tmp_path,
            lesson_front="papers:\n  - id: mayne-1966\n    required: true\n",
            registry=registry,
        )
    )
    assert any("duplicate paper id 'mayne-1966'" in m for m in messages(course))


def test_a_non_http_registry_url_is_an_error(tmp_path: Path) -> None:
    registry = {"papers": [{**REGISTRY["papers"][0], "url": "ftp://example.org/p.pdf"}]}
    course = load_course(
        write_course(
            tmp_path,
            lesson_front="papers:\n  - id: mayne-1966\n    required: true\n",
            registry=registry,
        )
    )
    assert any("invalid url" in m for m in messages(course))


def test_a_lesson_with_papers_must_require_at_least_one(tmp_path: Path) -> None:
    course = load_course(write_course(tmp_path, lesson_front="papers:\n  - id: mayne-1966\n"))
    problems = validate_course(course)
    assert any("marks none 'required: true'" in p.message and p.blocking for p in problems)


def test_listing_the_same_paper_twice_is_an_error(tmp_path: Path) -> None:
    front = "papers:\n  - id: mayne-1966\n    required: true\n  - id: mayne-1966\n"
    course = load_course(write_course(tmp_path, lesson_front=front))
    assert any("lists paper 'mayne-1966' twice" in m for m in messages(course))


def test_an_unreferenced_paper_only_warns(tmp_path: Path) -> None:
    """A bibliography entry waiting for its lesson must not fail the gate."""
    course = load_course(
        write_course(tmp_path, lesson_front="papers:\n  - id: mayne-1966\n    required: true\n")
    )
    problems = validate_course(course)
    unreferenced = [p for p in problems if "no lesson references it" in p.message]
    assert len(unreferenced) == 1
    assert unreferenced[0].severity == "warning" and not unreferenced[0].blocking
    assert [p for p in problems if p.blocking] == []


def test_a_stale_reverse_index_only_warns(tmp_path: Path) -> None:
    registry = {
        "papers": [
            {**REGISTRY["papers"][0], "lessons": ["l1", "l2"]},
            REGISTRY["papers"][1],
        ]
    }
    course = load_course(
        write_course(
            tmp_path,
            lesson_front=ASSIGNS_BOTH,
            registry=registry,
        )
    )
    problems = validate_course(course)
    stale = [p for p in problems if "lists lessons" in p.message]
    assert len(stale) == 1 and stale[0].severity == "warning"
    assert [p for p in problems if p.blocking] == []


def test_a_matching_reverse_index_says_nothing(tmp_path: Path) -> None:
    registry = {
        "papers": [
            {**REGISTRY["papers"][0], "lessons": ["l1"]},
            {**REGISTRY["papers"][1], "lessons": ["l1"]},
        ]
    }
    course = load_course(write_course(tmp_path, lesson_front=ASSIGNS_BOTH, registry=registry))
    assert validate_course(course) == []


# -- citation line ---


def test_citation_drops_the_parts_a_paper_does_not_have() -> None:
    assert citation(LessonPaper(id="a", title="T")) == ""
    assert citation(LessonPaper(id="a", title="T", year=1999)) == "(1999)"
    assert (
        citation(LessonPaper(id="a", title="T", authors=["A", "B"], year=2020, venue="V"))
        == "A & B (2020), V"
    )
    assert "et al." in citation(LessonPaper(id="a", title="T", authors=["A", "B", "C"], year=2020))


# -- rc papers / rc validate ---


def test_rc_papers_lists_required_reading_first(tmp_path: Path) -> None:
    course_dir = write_course(tmp_path, lesson_front=ASSIGNS_BOTH)
    result = runner.invoke(app, ["--curriculum", str(course_dir.parent), "papers", "l1"])
    assert result.exit_code == 0, result.output
    assert "A second-order gradient method" in result.output
    assert "D. Q. Mayne (1966), International Journal of Control" in result.output
    assert "§3 only" in result.output
    # The unverified link is flagged, so a reader knows not to trust it yet.
    assert "(미확인)" in result.output or "(unverified)" in result.output


def test_rc_papers_says_so_when_a_lesson_assigns_none(tmp_path: Path) -> None:
    course_dir = write_course(tmp_path, registry=None)
    result = runner.invoke(app, ["--curriculum", str(course_dir.parent), "papers", "l1"])
    assert result.exit_code == 0, result.output
    assert "없음" in result.output or "no papers" in result.output


def test_rc_papers_refuses_an_unknown_lesson(tmp_path: Path) -> None:
    course_dir = write_course(tmp_path)
    result = runner.invoke(app, ["--curriculum", str(course_dir.parent), "papers", "nope"])
    assert result.exit_code == 1


def test_rc_validate_reports_a_warning_without_failing(tmp_path: Path) -> None:
    course_dir = write_course(
        tmp_path, lesson_front="papers:\n  - id: mayne-1966\n    required: true\n"
    )
    result = runner.invoke(app, ["validate", str(course_dir.parent)])
    assert result.exit_code == 0, result.output
    assert "warning:" in result.output
    assert "1 warning(s)" in result.output

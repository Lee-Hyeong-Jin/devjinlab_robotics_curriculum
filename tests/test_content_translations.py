"""Lesson translations: ``<lesson>.<lang>.md`` loading, validation, API and site (P2-6)."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.settings import Settings
from robotics_curriculum.cli import app
from robotics_curriculum.content import check, load_course, load_courses
from robotics_curriculum.content.loader import split_lang_suffix
from robotics_curriculum.progress import ProgressService, SqliteProgressStore
from robotics_curriculum.site import generate_project

runner = CliRunner()
ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "curriculum"
COURSE = FIXTURE / "sample-course"
MODULE = "m1-math-physics"
VECTORS = "m1-vectors-matrices"
NOW = datetime(2026, 11, 11, 12, 0, tzinfo=UTC)

BASE = """---
id: a-intro
title: 소개
summary: 요약.
objectives:
  - 목표.
difficulty: 1
estimated_minutes: 30
tags: [기초]
---

# 소개

본문.
"""

TRANSLATION = """---
id: a-intro
lang: en
title: Introduction
summary: Summary.
---

# Introduction

Body.
"""


@pytest.fixture
def course_dir(tmp_path: Path):  # type: ignore[no-untyped-def]  # factory fixture
    course = tmp_path / "course"
    (course / "m1").mkdir(parents=True)
    (course / "course.yaml").write_text("id: c\ntitle: C\nsummary: S\n", encoding="utf-8")
    (course / "m1" / "module.yaml").write_text("id: m1\ntitle: M1\nsummary: S\n", encoding="utf-8")
    (course / "m1" / "a-intro.md").write_text(BASE, encoding="utf-8")

    def write(name: str, text: str) -> Path:
        path = course / "m1" / name
        path.write_text(text, encoding="utf-8")
        return path

    return course, write


def errors_of(course: Path) -> list[str]:
    _, found = check(course)
    return [e.message for e in found]


# -- loading -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("stem", "expected"),
    [
        ("vectors-matrices.en", ("vectors-matrices", "en")),
        ("vectors.pt-br", ("vectors", "pt-br")),
        ("vectors-matrices", None),
        ("vectors.markdown", None),
    ],
)
def test_split_lang_suffix(stem: str, expected: tuple[str, str] | None) -> None:
    assert split_lang_suffix(stem) == expected


def test_fixture_lesson_carries_its_english_translation() -> None:
    course = load_course(COURSE)
    lesson = next(les for les in course.iter_lessons() if les.id == VECTORS)
    assert lesson.languages() == ["ko", "en"]
    english = lesson.localized("en")
    assert english.translated is True and english.lang == "en"
    assert english.title == "Vectors and matrices"
    assert english.summary == "Sample lesson, translated."
    assert english.objectives == ["Explain vector and matrix operations."]
    assert "Body in English." in english.body
    # structure is never translated
    assert lesson.difficulty == 1 and lesson.estimated_minutes == 30


def test_untranslated_language_falls_back_to_the_source_language() -> None:
    course = load_course(COURSE)
    lesson = next(les for les in course.iter_lessons() if les.id == VECTORS)
    for lang in (None, "ko", "fr"):
        text = lesson.localized(lang)
        assert text.translated is False
        assert text.title == "벡터와 행렬" and text.lang == "ko"
    other = next(les for les in course.iter_lessons() if les.id == "m2-dh-parameters")
    assert other.languages() == ["ko"]
    assert other.localized("en").title == "DH 파라미터"


def test_translation_inherits_objectives_and_tags_when_omitted(course_dir) -> None:  # type: ignore[no-untyped-def]
    course, write = course_dir
    write("a-intro.en.md", TRANSLATION)
    lesson = load_course(course).iter_lessons()[0]
    english = lesson.localized("en")
    assert english.title == "Introduction"
    assert english.objectives == ["목표."]  # not translated: falls back
    assert english.tags == ["기초"]
    assert errors_of(course) == []


def test_translation_file_is_not_a_separate_lesson(course_dir) -> None:  # type: ignore[no-untyped-def]
    course, write = course_dir
    write("a-intro.en.md", TRANSLATION)
    (course / "m1" / "module.yaml").write_text(
        "id: m1\ntitle: M1\nsummary: S\nlessons: [a-intro]\n", encoding="utf-8"
    )
    lessons = load_course(course).iter_lessons()
    assert [les.id for les in lessons] == ["a-intro"]  # no 'a-intro.en' lesson
    assert errors_of(course) == []


# -- validation ----------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "text", "fragment"),
    [
        ("a-intro.en.md", TRANSLATION.replace("id: a-intro", "id: other-lesson"), "does not match"),
        ("a-intro.en.md", TRANSLATION.replace("lang: en", "lang: ko"), "file name says 'en'"),
        ("a-intro.en.md", TRANSLATION.replace("title: Introduction\n", ""), "title"),
        ("a-intro.en.md", TRANSLATION.replace("summary: Summary.\n", ""), "summary"),
        ("a-intro.en.md", "# no front matter\n", "missing YAML front matter"),
        ("a-intro.en.md", TRANSLATION + "\nx", None),  # valid, just longer
        ("a-intro.fr.md", TRANSLATION.replace("lang: en", "lang: fr"), "unsupported translation"),
        ("a-intro.ko.md", TRANSLATION.replace("lang: en", "lang: ko"), "drop the suffix"),
        ("missing.en.md", TRANSLATION, "no lesson to translate"),
        (
            "a-intro.en.md",
            TRANSLATION.replace("difficulty", "x").replace(
                "---\n\n# Introduction\n\nBody.\n", "difficulty: 2\n---\n\nBody.\n"
            ),
            "difficulty",
        ),
    ],
)
def test_validate_reports_translation_problems(
    course_dir,  # type: ignore[no-untyped-def]
    name: str,
    text: str,
    fragment: str | None,
) -> None:
    course, write = course_dir
    write(name, text)
    messages = errors_of(course)
    if fragment is None:
        assert messages == []
    else:
        assert any(fragment in m for m in messages), messages


def test_empty_translation_body_is_an_error(course_dir) -> None:  # type: ignore[no-untyped-def]
    course, write = course_dir
    write("a-intro.en.md", "---\nid: a-intro\ntitle: T\nsummary: S\n---\n\n   \n")
    assert any("empty body" in m for m in errors_of(course))


def test_rc_validate_accepts_the_fixture_with_translations() -> None:
    result = runner.invoke(app, ["validate", str(FIXTURE)])
    assert result.exit_code == 0, result.output
    assert result.output.startswith("OK: 3 lessons")  # the translation is not a 4th lesson


# -- API -----------------------------------------------------------------------


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    settings = Settings(curriculum_dir=FIXTURE, data_dir=tmp_path / "data")
    return TestClient(create_app(settings, clock=lambda: NOW))


def test_lesson_endpoint_follows_accept_language(client: TestClient) -> None:
    korean = client.get(f"/api/v1/lessons/{VECTORS}").json()
    assert korean["title"] == "벡터와 행렬"
    assert korean["lang"] == "ko"
    assert korean["available_languages"] == ["ko", "en"]

    english = client.get(
        f"/api/v1/lessons/{VECTORS}", headers={"Accept-Language": "en-US,en;q=0.9"}
    ).json()
    assert english["title"] == "Vectors and matrices"
    assert english["lang"] == "en"
    assert english["objectives"] == ["Explain vector and matrix operations."]
    assert "Body in English." in english["body"]
    assert english["study_method"] is not None
    assert "textbook" in english["study_method"].lower()
    # structure and resources stay the same in both languages
    assert english["prerequisites"] == korean["prerequisites"]
    assert english["estimated_minutes"] == korean["estimated_minutes"]


def test_untranslated_lesson_states_the_language_it_answers_in(client: TestClient) -> None:
    body = client.get("/api/v1/lessons/m2-dh-parameters", headers={"Accept-Language": "en"}).json()
    assert body["title"] == "DH 파라미터"
    assert body["lang"] == "ko"
    assert body["available_languages"] == ["ko"]


def test_module_listing_uses_the_requested_language(client: TestClient) -> None:
    body = client.get(f"/api/v1/modules/{MODULE}", headers={"Accept-Language": "en"}).json()
    titles = {lesson["id"]: lesson["title"] for lesson in body["lessons"]}
    assert titles[VECTORS] == "Vectors and matrices"
    assert titles["m1-rotation-representations"] == "회전 표현"  # no translation yet


# -- static site ---------------------------------------------------------------


def test_english_site_uses_the_translated_lesson(tmp_path: Path) -> None:
    root = tmp_path / "curriculum"
    shutil.copytree(FIXTURE, root)
    store = SqliteProgressStore.in_dir(tmp_path / "rcdata")
    service = ProgressService(store, load_courses(root), clock=lambda: NOW)
    try:
        generate_project(service, tmp_path / "en", now=NOW, lang="en")
        generate_project(service, tmp_path / "ko", now=NOW)
    finally:
        store.close()

    english = (tmp_path / "en" / "docs" / f"modules/{MODULE}/{VECTORS}.md").read_text(
        encoding="utf-8"
    )
    assert english.startswith("# Vectors and matrices")
    assert "Body in English." in english
    assert "Explain vector and matrix operations." in english
    assert "벡터와 행렬" not in english

    index = (tmp_path / "en" / "docs" / "index.md").read_text(encoding="utf-8")
    assert "Vectors and matrices" in index  # links use the translated title

    korean = (tmp_path / "ko" / "docs" / f"modules/{MODULE}/{VECTORS}.md").read_text(
        encoding="utf-8"
    )
    assert korean.startswith("# 벡터와 행렬")
    assert "Body in English." not in korean

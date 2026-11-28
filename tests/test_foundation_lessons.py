"""What every foundation lesson (M1-M4, M11) must carry: use case, expected result, figure.

GitHub #59 (where the lesson is used), #48 (what a correct exercise gives) and #60 (figures).
The rules in ``rc validate`` check the shape of these blocks; this file checks that the
foundation stage actually has them, in both languages, so a rewrite cannot drop one unnoticed.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from robotics_curriculum.content import load_course
from robotics_curriculum.content.lesson_blocks import extract_expected, has_use_case, image_refs
from robotics_curriculum.content.models import ActivityKind, Lesson

ROOT = Path(__file__).resolve().parents[1]
FOUNDATION = (
    "m1-math-physics",
    "m2-kinematics",
    "m3-mobile-robots-control",
    "m4-sensors-perception",
    "m11-actuators-embedded",
)
USE_CASE_ONLY = ("m8-ros2-tools",)
WITH_FIGURES = FOUNDATION[:3]


def _lessons(module_ids: tuple[str, ...]) -> list[Lesson]:
    course = load_course(ROOT / "curriculum" / "robotics-expert")
    found = [
        lesson for module in course.modules if module.id in module_ids for lesson in module.lessons
    ]
    assert found, "the foundation modules were not found; did their ids change?"
    return found


def _bodies(lesson: Lesson) -> dict[str, str]:
    bodies = {"ko": lesson.body}
    bodies.update({lang: translation.body for lang, translation in lesson.translations.items()})
    return bodies


@pytest.mark.parametrize("lesson", _lessons(FOUNDATION), ids=lambda lesson: lesson.id)
def test_foundation_lesson_says_where_it_is_used_and_what_the_exercise_gives(
    lesson: Lesson,
) -> None:
    bodies = _bodies(lesson)
    assert set(bodies) == {"ko", "en"}
    for lang, body in bodies.items():
        assert has_use_case(body, lang), f"{lesson.id} ({lang}) has no use-case section"
        blocks = extract_expected(body)
        if not any(activity.kind == ActivityKind.EXERCISE for activity in lesson.activities):
            assert not blocks  # a lesson without an exercise (the optional build) has no answer
            continue
        assert blocks, f"{lesson.id} ({lang}) has no expected-result block"
        assert all(len(block) > 200 for block in blocks), f"{lesson.id} ({lang}): a thin answer"


@pytest.mark.parametrize("lesson", _lessons(USE_CASE_ONLY), ids=lambda lesson: lesson.id)
def test_ros2_module_lesson_says_where_it_is_used(lesson: Lesson) -> None:
    for lang, body in _bodies(lesson).items():
        assert has_use_case(body, lang), f"{lesson.id} ({lang}) has no use-case section"


def test_the_actuators_module_branches_off_without_blocking_the_course() -> None:
    """#63, #53: the module adds lessons; only the capstone hardware lesson builds on it."""
    course = load_course(ROOT / "curriculum" / "robotics-expert")
    lessons = [lesson for module in course.modules for lesson in module.lessons]
    dependants = {
        lesson.id
        for lesson in lessons
        if not lesson.id.startswith("m11-")
        and any(prerequisite.startswith("m11-") for prerequisite in lesson.prerequisites)
    }
    assert dependants == {"m10-hardware-selection-integration"}
    # Nothing at all requires the optional build.
    assert not [x.id for x in lessons if "m11-first-robot-budget" in x.prerequisites]


@pytest.mark.parametrize("lesson", _lessons(WITH_FIGURES), ids=lambda lesson: lesson.id)
def test_m1_to_m3_lesson_has_a_figure_with_alt_text_in_both_languages(lesson: Lesson) -> None:
    for lang, body in _bodies(lesson).items():
        figures = [image for image in image_refs(body) if image.figure_name]
        assert figures, f"{lesson.id} ({lang}) shows no figure"
        assert all(len(image.alt) > 20 for image in figures), f"{lesson.id} ({lang}): alt text"


def test_committed_figures_are_what_the_generator_writes() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "figures" / "make_figures.py"), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr

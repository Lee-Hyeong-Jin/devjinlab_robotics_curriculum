"""``course.<lang>.yaml`` / ``module.<lang>.yaml`` / ``<lesson>.<lang>.yaml`` siblings.

These hold the text that is not lesson prose: course and module titles, activity titles,
resource titles and notes, and the quiz. Prose stays in ``<lesson>.<lang>.md``.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from robotics_curriculum.content import load_courses, localized_quiz, validate_courses
from robotics_curriculum.content.loader import LoadError
from robotics_curriculum.content.models import level_label

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "curriculum"
VECTORS = "m1-vectors-matrices"
ROTATION = "m1-rotation-representations"
DH = "m2-dh-parameters"


@pytest.fixture
def root(tmp_path: Path) -> Path:
    copy = tmp_path / "curriculum"
    shutil.copytree(FIXTURE, copy)
    return copy


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def course_of(root: Path):  # noqa: ANN201 - a loaded Course
    (course,) = load_courses(root)
    return course


def test_course_and_module_text_fall_back_to_the_authoring_language(root: Path) -> None:
    course = course_of(root)
    assert course.localized("en").title == course.title
    assert course.localized("en").translated is False
    module = course.modules[0]
    assert module.localized("en").title == module.title


def test_sibling_yaml_translates_course_and_module(root: Path) -> None:
    write(root / "sample-course" / "course.en.yaml", "title: Sample course\nsummary: A fixture.\n")
    write(
        root / "sample-course" / "m1-math-physics" / "module.en.yaml",
        "id: m1-math-physics\nlang: en\ntitle: Maths\nsummary: Vectors and rotations.\n",
    )
    course = course_of(root)
    assert course.localized("en").title == "Sample course"
    assert course.localized("en").translated is True
    assert course.localized("ko").title == course.title

    module = course.modules[0]
    assert module.localized("en").title == "Maths"
    assert module.localized("en").summary == "Vectors and rotations."
    assert module.localized("en").level == module.level
    assert module.localized("en").level_label == level_label(module.level, "en")


def test_level_label_translates_only_the_display_name() -> None:
    assert level_label("기초", "en") == "Foundation"
    assert level_label("기초", "ko") == "기초"
    assert level_label(None, "en") == "No stage"
    assert level_label("made-up", "en") == "made-up"


def lesson_of(root: Path, lesson_id: str = VECTORS):  # noqa: ANN201 - a loaded Lesson
    for module in course_of(root).modules:
        for lesson in module.lessons:
            if lesson.id == lesson_id:
                return lesson
    raise AssertionError(f"no lesson {lesson_id}")


def meta_path(
    root: Path, stem: str = "rotation-representations", module: str = "m1-math-physics"
) -> Path:
    return root / "sample-course" / module / f"{stem}.en.yaml"


def test_activities_and_resources_are_translated(root: Path) -> None:
    base = lesson_of(root, DH)
    activity_id = base.activities[0].id
    resource_title = base.resources[0].title
    write(
        meta_path(root, "dh-parameters", "m2-kinematics"),
        f"id: {DH}\nlang: en\n"
        f"activities:\n  {activity_id}: Read the lesson\n"
        f'resources:\n  "{resource_title}":\n    title: Linear algebra primer\n'
        f"    note: Watch the first four episodes.\n",
    )
    lesson = lesson_of(root, DH)
    text = lesson.localized("en")
    assert text.activities[0].title == "Read the lesson"
    assert text.activities[0].id == activity_id
    assert text.resources[0].title == "Linear algebra primer"
    assert text.resources[0].note == "Watch the first four episodes."
    assert text.resources[0].url == lesson.resources[0].url
    # untouched in the authoring language
    assert lesson.localized("ko").activities[0].title == base.activities[0].title


def test_the_quiz_keeps_its_ids_and_answers_when_translated(root: Path) -> None:
    lesson = lesson_of(root, ROTATION)
    original = localized_quiz(lesson).questions[0]
    write(
        meta_path(root),
        f"id: {ROTATION}\nquiz:\n  - id: {original.id}\n"
        f"    prompt: What does a dot product of zero mean?\n"
        f"    choices: {[f'choice {i + 1}' for i in range(len(original.choices))]}\n"
        f"    explanation: They are perpendicular.\n"
        f"    concept:\n      front: Dot product of zero\n      back: Perpendicular\n",
    )
    translated = localized_quiz(lesson_of(root, ROTATION), "en").questions[0]
    assert translated.id == original.id
    assert translated.type == original.type
    assert translated.answer == original.answer
    assert translated.prompt == "What does a dot product of zero mean?"
    assert translated.explanation == "They are perpendicular."
    assert translated.concept is not None
    assert translated.concept.front == "Dot product of zero"
    # the untranslated language is untouched
    assert localized_quiz(lesson_of(root, ROTATION)).questions[0].prompt == original.prompt


def test_an_untranslated_question_keeps_its_own_text(root: Path) -> None:
    lesson = lesson_of(root, ROTATION)
    questions = localized_quiz(lesson).questions
    if len(questions) < 2:
        pytest.skip("fixture quiz has a single question")
    write(
        meta_path(root),
        f"quiz:\n  - id: {questions[0].id}\n    prompt: Translated\n    explanation: Because.\n",
    )
    after = localized_quiz(lesson_of(root, ROTATION), "en").questions
    assert after[0].prompt == "Translated"
    assert after[1].prompt == questions[1].prompt


def test_truefalse_answers_and_type_labels_follow_the_language(root: Path) -> None:
    quiz = localized_quiz(lesson_of(root, "m1-rotation-representations"))
    truefalse = next(q for q in quiz.questions if q.type == "truefalse")
    assert truefalse.answer_text("en") == ("O (true)" if truefalse.answer else "X (false)")
    assert "(" in truefalse.answer_text("ko")
    single = next(q for q in quiz.questions if q.type == "single")
    assert single.type_label("en") == "single choice"
    assert single.type_label("ko") == "객관식"


@pytest.mark.parametrize(
    ("body", "message"),
    [
        ("activities:\n  nope: X\n", "no activity 'nope'"),
        ('resources:\n  "nope":\n    note: X\n', "no resource titled 'nope'"),
        ("quiz:\n  - id: nope\n    prompt: X\n    explanation: Y\n", "no quiz question 'nope'"),
    ],
)
def test_a_translation_may_not_name_things_the_lesson_does_not_have(
    root: Path, body: str, message: str
) -> None:
    write(meta_path(root), body)
    errors = validate_courses(load_courses(root))
    assert any(message in str(e) for e in errors), [str(e) for e in errors]


def test_a_choice_count_mismatch_is_an_error(root: Path) -> None:
    question = localized_quiz(lesson_of(root, ROTATION)).questions[0]
    if not question.choices:
        pytest.skip("fixture's first question has no choices")
    write(
        meta_path(root),
        f"quiz:\n  - id: {question.id}\n    prompt: X\n    explanation: Y\n"
        f"    choices: ['only one']\n",
    )
    errors = validate_courses(load_courses(root))
    assert any("choices but the lesson has" in str(e) for e in errors)


def test_the_authoring_language_may_not_be_used_as_a_suffix(root: Path) -> None:
    write(root / "sample-course" / "course.ko.yaml", "title: X\nsummary: Y\n")
    with pytest.raises(LoadError) as excinfo:
        load_courses(root)
    assert "drop the suffix" in str(excinfo.value)


def test_an_unsupported_language_is_rejected(root: Path) -> None:
    write(root / "sample-course" / "m1-math-physics" / "module.fr.yaml", "title: X\nsummary: Y\n")
    with pytest.raises(LoadError) as excinfo:
        load_courses(root)
    assert "unsupported translation language 'fr'" in str(excinfo.value)


def test_a_mismatched_id_is_rejected(root: Path) -> None:
    write(meta_path(root), "id: m9-something\nquiz: []\n")
    with pytest.raises(LoadError) as excinfo:
        load_courses(root)
    assert "does not match lesson id" in str(excinfo.value)


def test_a_mismatched_lang_is_rejected(root: Path) -> None:
    write(root / "sample-course" / "course.en.yaml", "lang: ko\ntitle: X\nsummary: Y\n")
    with pytest.raises(LoadError) as excinfo:
        load_courses(root)
    assert "but the file name says 'en'" in str(excinfo.value)


def test_an_orphan_translation_is_rejected(root: Path) -> None:
    write(root / "sample-course" / "m1-math-physics" / "ghost.en.yaml", "activities: {}\n")
    with pytest.raises(LoadError) as excinfo:
        load_courses(root)
    assert "has no lesson to translate" in str(excinfo.value)

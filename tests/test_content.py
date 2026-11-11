from pathlib import Path

import pytest
from typer.testing import CliRunner

from robotics_curriculum.cli import app
from robotics_curriculum.content import (
    ActivityKind,
    LoadError,
    check,
    load_course,
    load_courses,
    validate_course,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_COURSE = REPO_ROOT / "curriculum" / "robotics-basics"

runner = CliRunner()


def lesson_md(id_: str, prerequisites: list[str] | None = None, **overrides: object) -> str:
    fields: dict[str, object] = {
        "id": id_,
        "title": f"Lesson {id_}",
        "summary": "A summary.",
        "objectives": ["Do a thing."],
        "prerequisites": prerequisites or [],
        "difficulty": 1,
        "estimated_minutes": 10,
        "tags": [],
    }
    fields.update(overrides)
    lines = ["---"]
    for key, value in fields.items():
        if value is None:
            continue
        if isinstance(value, list):
            items = ", ".join(str(v) for v in value)
            lines.append(f"{key}: [{items}]")
        else:
            lines.append(f"{key}: {value}")
    lines += ["---", "", f"# {id_}", "", "Body."]
    return "\n".join(lines) + "\n"


def write_course(root: Path, lessons: dict[str, str]) -> Path:
    """Create ``root/course/mod/<name>.md`` for each lesson; return the course dir."""
    course = root / "course"
    module = course / "mod"
    module.mkdir(parents=True)
    (course / "course.yaml").write_text(
        "id: course\ntitle: Course\nsummary: S\nmodules: [mod]\n", encoding="utf-8"
    )
    names = ", ".join(lessons)
    (module / "module.yaml").write_text(
        f"id: mod\ntitle: Mod\nsummary: S\nlessons: [{names}]\n", encoding="utf-8"
    )
    for name, text in lessons.items():
        (module / f"{name}.md").write_text(text, encoding="utf-8")
    return course


def test_sample_content_loads_and_validates() -> None:
    course = load_course(SAMPLE_COURSE)
    assert course.id == "robotics-basics"
    assert [m.id for m in course.modules] == ["m1-math-physics", "m2-kinematics"]
    assert [lesson.id for lesson in course.iter_lessons()] == [
        "m1-vectors-matrices",
        "m1-rotation-representations",
        "m2-dh-parameters",
    ]
    dh = course.modules[1].lessons[0]
    assert dh.prerequisites == ["m1-vectors-matrices"]
    assert dh.body.lstrip().startswith("# DH 파라미터")
    lab = next(a for a in dh.activities if a.kind is ActivityKind.LAB)
    assert lab.lab_id == "m2-dh-two-link"
    assert validate_course(course) == []


def test_load_courses_from_parent_directory() -> None:
    courses = load_courses(REPO_ROOT / "curriculum")
    assert [c.id for c in courses] == ["robotics-basics"]


def test_missing_required_field_is_reported_with_path(tmp_path: Path) -> None:
    course = write_course(tmp_path, {"a": lesson_md("a", title=None)})
    with pytest.raises(LoadError) as excinfo:
        load_course(course)
    errors = excinfo.value.errors
    assert len(errors) == 1
    assert errors[0].path == course / "mod" / "a.md"
    assert "title" in errors[0].message
    assert "required" in errors[0].message.lower()


def test_unknown_front_matter_key_is_an_error(tmp_path: Path) -> None:
    course = write_course(tmp_path, {"a": lesson_md("a", dificulty=3)})
    with pytest.raises(LoadError) as excinfo:
        load_course(course)
    assert any("dificulty" in e.message for e in excinfo.value.errors)


def test_lab_activity_requires_lab_id(tmp_path: Path) -> None:
    text = lesson_md("a").replace(
        "tags: []",
        "tags: []\nactivities:\n  - id: a-lab\n    kind: lab\n    title: Lab\n",
    )
    course = write_course(tmp_path, {"a": text})
    with pytest.raises(LoadError) as excinfo:
        load_course(course)
    assert any("lab_id" in e.message for e in excinfo.value.errors)


def test_dangling_prerequisite_is_an_error(tmp_path: Path) -> None:
    course = write_course(tmp_path, {"a": lesson_md("a", prerequisites=["ghost"])})
    errors = validate_course(load_course(course))
    assert len(errors) == 1
    assert errors[0].path == course / "mod" / "a.md"
    assert "ghost" in errors[0].message


def test_prerequisite_cycle_is_an_error(tmp_path: Path) -> None:
    course = write_course(
        tmp_path,
        {
            "a": lesson_md("a", prerequisites=["c"]),
            "b": lesson_md("b", prerequisites=["a"]),
            "c": lesson_md("c", prerequisites=["b"]),
        },
    )
    errors = validate_course(load_course(course))
    assert len(errors) == 1
    assert "cycle" in errors[0].message
    for node in ("a", "b", "c"):
        assert node in errors[0].message


def test_duplicate_ids_and_empty_module_are_errors(tmp_path: Path) -> None:
    course = write_course(tmp_path, {"a": lesson_md("a"), "b": lesson_md("a")})
    empty = course / "empty"
    empty.mkdir()
    (empty / "module.yaml").write_text("id: empty\ntitle: E\nsummary: S\n", encoding="utf-8")
    (course / "course.yaml").write_text(
        "id: course\ntitle: Course\nsummary: S\nmodules: [mod, empty]\n", encoding="utf-8"
    )
    messages = [e.message for e in validate_course(load_course(course))]
    assert any("duplicate id 'a'" in m for m in messages)
    assert any("module 'empty' has no lessons" in m for m in messages)


def test_unlisted_lesson_file_is_an_error(tmp_path: Path) -> None:
    course = write_course(tmp_path, {"a": lesson_md("a")})
    (course / "mod" / "stray.md").write_text(lesson_md("stray"), encoding="utf-8")
    _, errors = check(course)
    assert len(errors) == 1
    assert errors[0].path == course / "mod" / "stray.md"
    assert "not listed" in errors[0].message


def test_cli_validate_sample_passes() -> None:
    result = runner.invoke(app, ["validate", str(SAMPLE_COURSE)])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "OK: 3 lessons in 2 modules"


def test_cli_validate_reports_errors_and_exits_1(tmp_path: Path) -> None:
    course = write_course(tmp_path, {"a": lesson_md("a", prerequisites=["ghost"])})
    result = runner.invoke(app, ["validate", str(course)])
    assert result.exit_code == 1
    assert f"{course / 'mod' / 'a.md'}: prerequisite 'ghost'" in result.output

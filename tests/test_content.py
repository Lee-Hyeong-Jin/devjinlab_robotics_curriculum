from pathlib import Path

import pytest
from typer.testing import CliRunner

from robotics_curriculum.cli import app
from robotics_curriculum.content import (
    LEVEL_KEYS,
    ActivityKind,
    LoadError,
    ResourceKind,
    check,
    load_course,
    load_courses,
    validate_course,
)
from robotics_curriculum.content.models import ModuleMeta
from robotics_curriculum.i18n import translator

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_CURRICULUM = Path(__file__).resolve().parent / "fixtures" / "curriculum"
SAMPLE_COURSE = FIXTURE_CURRICULUM / "sample-course"

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
    assert course.id == "sample-course"
    assert [m.id for m in course.modules] == ["m1-math-physics", "m2-kinematics"]
    assert [lesson.id for lesson in course.iter_lessons()] == [
        "m1-vectors-matrices",
        "m1-rotation-representations",
        "m2-dh-parameters",
    ]
    dh = course.modules[1].lessons[0]
    assert dh.prerequisites == ["m1-vectors-matrices"]
    assert dh.body.lstrip().startswith("# DH 파라미터")
    assert [a.kind for a in dh.activities] == [ActivityKind.READING, ActivityKind.EXERCISE]
    assert validate_course(course) == []


def test_load_courses_from_parent_directory() -> None:
    courses = load_courses(FIXTURE_CURRICULUM)
    assert [c.id for c in courses] == ["sample-course"]


def test_live_curriculum_validates() -> None:
    courses = load_courses(REPO_ROOT / "curriculum")
    assert courses
    assert any(len(c.modules) >= 1 for c in courses)
    for course in courses:
        assert validate_course(course) == []


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


def test_lab_activity_kind_is_rejected(tmp_path: Path) -> None:
    text = lesson_md("a").replace(
        "tags: []",
        "tags: []\nactivities:\n  - id: a-lab\n    kind: lab\n    title: Lab\n",
    )
    course = write_course(tmp_path, {"a": text})
    with pytest.raises(LoadError) as excinfo:
        load_course(course)
    assert any("kind" in e.message for e in excinfo.value.errors)


def test_module_level_parses(tmp_path: Path) -> None:
    course = write_course(tmp_path, {"a": lesson_md("a")})
    module_yaml = course / "mod" / "module.yaml"
    module_yaml.write_text(
        module_yaml.read_text(encoding="utf-8") + "level: 중급\n", encoding="utf-8"
    )
    assert load_course(course).modules[0].level == "중급"

    module_yaml.write_text(
        module_yaml.read_text(encoding="utf-8").replace("중급", "전문가"), encoding="utf-8"
    )
    with pytest.raises(LoadError):
        load_course(course)


def test_lesson_resources_parse(tmp_path: Path) -> None:
    text = lesson_md("a").replace(
        "tags: []",
        "tags: []\nresources:\n"
        "  - title: Modern Robotics\n    url: https://example.org/mr\n"
        "    kind: book\n    note: Ch. 3\n"
        "  - title: Just a title\n",
    )
    course = write_course(tmp_path, {"a": text})
    lesson = load_course(course).modules[0].lessons[0]
    assert [r.title for r in lesson.resources] == ["Modern Robotics", "Just a title"]
    first, second = lesson.resources
    assert first.kind == "book" and first.url == "https://example.org/mr" and first.note == "Ch. 3"
    assert second.kind is None and second.url is None


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


# -- research-track vocabulary (lesson-standard.md §11-2, §11-4, §11-5) ---------------


def test_activity_kinds_cover_the_research_track_without_losing_the_old_ones() -> None:
    """`reading` and `paper` have to stay distinguishable: a textbook is not a primary paper."""
    values = {k.value for k in ActivityKind}
    assert {"reading", "quiz", "exercise"} <= values  # existing content keeps working
    assert {"paper", "reproduction", "project"} <= values


def test_resource_kinds_cover_datasets_and_published_code() -> None:
    values = {k.value for k in ResourceKind}
    assert {"book", "course", "video", "article", "other"} <= values
    assert {"paper", "dataset", "code", "notes"} <= values


def test_every_resource_kind_has_a_display_label_in_both_languages() -> None:
    """A kind with no label would render as the bare enum value on the site."""
    for lang in ("ko", "en"):
        t = translator(lang)
        for kind in ResourceKind:
            key = f"resource.kind.{kind.value}"
            assert t(key) != key, (lang, key)


def test_every_activity_kind_has_a_display_label_in_both_languages() -> None:
    for lang in ("ko", "en"):
        t = translator(lang)
        for kind in ActivityKind:
            key = f"site.activity.{kind.value}"
            assert t(key) != key, (lang, key)


def test_the_research_level_is_accepted_and_labelled() -> None:
    assert LEVEL_KEYS["연구"] == "research"
    for lang in ("ko", "en"):
        assert translator(lang)("level.research") != "level.research"


def test_a_module_may_declare_the_research_level(tmp_path: Path) -> None:
    meta = ModuleMeta(id="m-research", title="연구", summary="연구 모듈", level="연구", lessons=[])
    assert meta.level == "연구"

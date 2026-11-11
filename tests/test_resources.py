"""P1-4: study-guide section helper, resource validation, `rc resources`, `rc show`."""

from pathlib import Path

import pytest
from typer.testing import CliRunner, Result

from robotics_curriculum.cli import app
from robotics_curriculum.content import load_course, validate_course
from robotics_curriculum.content.sections import extract_section
from robotics_curriculum.content.validate import is_http_url

runner = CliRunner()

LESSON_A = """---
id: a-intro
title: 소개
summary: S
objectives:
  - 목표 하나를 설명할 수 있다.
difficulty: 1
estimated_minutes: 30
resources:
  - title: Modern Robotics
    kind: book
    url: https://example.org/mr
    note: Ch. 3
  - title: 강의 노트
    kind: course
  - title: 유튜브 강의
    kind: video
    url: https://example.org/v
  - title: 메모
---

# 소개

본문.

## 이 단계 공부법

먼저 3장을 읽고 연습문제 1-5를 푼다.

### 팁

손으로 써 본다.

## 다음 단계

생략.
"""

LESSON_B = """---
id: b-next
title: 다음
summary: S
objectives:
  - 두 번째 목표.
prerequisites: [a-intro]
difficulty: 2
estimated_minutes: 45
resources:
  - title: Blog post
    kind: article
    url: http://example.org/post
---

# 다음

본문 B.
"""


def write_course(root: Path, lessons: dict[str, str]) -> Path:
    course = root / "course"
    module = course / "mod"
    module.mkdir(parents=True)
    (course / "course.yaml").write_text(
        "id: course\ntitle: Course\nsummary: S\nmodules: [mod]\n", encoding="utf-8"
    )
    names = ", ".join(lessons)
    (module / "module.yaml").write_text(
        f"id: mod\ntitle: Mod\nsummary: S\nlevel: 기초\nlessons: [{names}]\n", encoding="utf-8"
    )
    for name, text in lessons.items():
        (module / f"{name}.md").write_text(text, encoding="utf-8")
    return course


@pytest.fixture
def course_dir(tmp_path: Path) -> Path:
    return write_course(tmp_path / "content", {"a-intro": LESSON_A, "b-next": LESSON_B})


def rc(tmp_path: Path, course_dir: Path, *args: str) -> Result:
    base = ["--data-dir", str(tmp_path / "data"), "--curriculum", str(course_dir)]
    return runner.invoke(app, [*base, *args])


# -- extract_section ----------------------------------------------------------


def test_extract_section_returns_text_until_next_h2() -> None:
    text = extract_section(LESSON_A, "이 단계 공부법")
    assert text is not None
    assert text.startswith("먼저 3장을 읽고")
    assert "### 팁" in text and "손으로 써 본다." in text
    assert "다음 단계" not in text


def test_extract_section_accepts_hash_prefix_and_handles_missing() -> None:
    assert extract_section("## 이 단계 공부법\n\nx\n", "## 이 단계 공부법") == "x"
    assert extract_section("## 다른 절\n\nx\n", "이 단계 공부법") is None
    assert extract_section("## 이 단계 공부법\n## 다음\n", "이 단계 공부법") == ""


def test_extract_section_ignores_headings_in_code_fences() -> None:
    body = "## 이 단계 공부법\n\n```md\n## not a heading\n```\n끝\n\n## 다음\n"
    assert extract_section(body, "이 단계 공부법") == "```md\n## not a heading\n```\n끝"


# -- validation ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("url", "ok"),
    [
        ("https://example.org/a?b=1", True),
        ("http://localhost:8000/x", True),
        ("ftp://example.org/file", False),
        ("example.org/page", False),
        ("https://", False),
        ("https://exa mple.org", False),
        ("https://example.org:notaport/", False),
    ],
)
def test_is_http_url(url: str, ok: bool) -> None:
    assert is_http_url(url) is ok


def test_invalid_resource_url_is_a_validation_error(tmp_path: Path) -> None:
    bad = LESSON_A.replace("https://example.org/mr", "www.example.org/mr")
    course = load_course(write_course(tmp_path, {"a-intro": bad}))
    messages = [e.message for e in validate_course(course)]
    assert any("invalid url 'www.example.org/mr'" in m for m in messages), messages


def test_duplicate_resource_title_is_a_validation_error(tmp_path: Path) -> None:
    dup = LESSON_A.replace("title: 강의 노트", "title: Modern Robotics")
    course = load_course(write_course(tmp_path, {"a-intro": dup}))
    messages = [e.message for e in validate_course(course)]
    assert any("duplicate resource title 'Modern Robotics'" in m for m in messages), messages


def test_valid_resources_pass_validation(course_dir: Path) -> None:
    assert validate_course(load_course(course_dir)) == []


# -- rc resources -------------------------------------------------------------


def test_resources_for_lesson_groups_by_kind_and_shows_study_guide(
    tmp_path: Path, course_dir: Path
) -> None:
    result = rc(tmp_path, course_dir, "resources", "a-intro")
    assert result.exit_code == 0, result.output
    out = result.output
    assert out.startswith("소개 (a-intro)")
    order = [out.index(label) for label in ("[교재]", "[강의]", "[영상]", "[기타]")]
    assert order == sorted(order)
    assert "  - Modern Robotics — Ch. 3\n    https://example.org/mr" in out
    assert out.index("메모") > out.index("[기타]")
    assert "## 이 단계 공부법" in out and "먼저 3장을 읽고" in out
    assert "생략." not in out


def test_resources_for_module_groups_by_lesson(tmp_path: Path, course_dir: Path) -> None:
    result = rc(tmp_path, course_dir, "resources", "--module", "mod")
    assert result.exit_code == 0, result.output
    out = result.output
    assert out.startswith("Mod (mod)")
    assert out.index("소개 (a-intro)") < out.index("Modern Robotics")
    assert out.index("다음 (b-next)") < out.index("Blog post")


def test_resources_all_is_a_library_by_kind(tmp_path: Path, course_dir: Path) -> None:
    result = rc(tmp_path, course_dir, "resources", "--all")
    assert result.exit_code == 0, result.output
    out = result.output
    assert "Course 자료 라이브러리 (5개)" in out
    assert "  - Blog post  [b-next]" in out
    assert out.index("[교재]") < out.index("[글]") < out.index("[기타]")


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["resources", "nope"], "unknown lesson 'nope'"),
        (["resources", "--module", "nope"], "unknown module 'nope'"),
        (["resources"], "exactly one of"),
        (["show", "nope"], "unknown lesson 'nope'"),
    ],
)
def test_unknown_ids_exit_1(
    tmp_path: Path, course_dir: Path, args: list[str], message: str
) -> None:
    result = rc(tmp_path, course_dir, *args)
    assert result.exit_code == 1
    assert message in result.output  # CliRunner mixes stderr into output


# -- rc show ------------------------------------------------------------------


def test_show_prints_summary_and_body(tmp_path: Path, course_dir: Path) -> None:
    result = rc(tmp_path, course_dir, "show", "b-next")
    assert result.exit_code == 0, result.output
    out = result.output
    assert out.startswith("# 다음 (b-next)")
    assert "수준: 기초" in out and "예상 시간: 45분" in out
    assert "  - 두 번째 목표." in out
    assert "  - a-intro" in out  # no progress store yet -> no status mark
    assert out.rstrip().endswith("본문 B.")
    assert not (tmp_path / "data").exists()  # viewing does not create a store


def test_show_marks_done_prerequisites(tmp_path: Path, course_dir: Path) -> None:
    assert rc(tmp_path, course_dir, "done", "a-intro").exit_code == 0
    result = rc(tmp_path, course_dir, "show", "b-next")
    assert result.exit_code == 0, result.output
    assert "  [x] a-intro" in result.output


def test_sample_curriculum_resources_run() -> None:
    result = runner.invoke(app, ["resources", "--all"])
    assert result.exit_code == 0, result.output

"""Use-case sections, expected-result blocks and figures in lesson bodies (#59, #48, #60)."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

from robotics_curriculum.api.app import create_app
from robotics_curriculum.api.settings import Settings
from robotics_curriculum.content import check
from robotics_curriculum.content.lesson_blocks import (
    ImageRef,
    extract_expected,
    has_use_case,
    image_refs,
    svg_problem,
    use_case_headings,
)
from robotics_curriculum.site.pages import render_expected_blocks

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "curriculum"
EXPERT = "robotics-expert"
NOW = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)
SVG = (
    b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
    b'<rect width="10" height="10"/></svg>'
)

BODY = """\
# Title

Intro.

## Where you will use this

A camera on the gripper sees a cup.

## Concepts

![Two frames](figures/frames.svg) and ![](figures/no-alt.svg) and ![web](https://x.test/a.png)

**Exercise:** do it.

```expected
The error settles at **4.3**.

- overshoot below 10%
```

```python
print("![not an image](figures/in-code.svg)")
```

~~~expected
second
~~~
"""


def test_use_case_section_is_found_by_its_heading_in_either_language() -> None:
    assert use_case_headings("en") == ["Where you will use this", "어디에 쓰는가"]
    assert use_case_headings() == ["어디에 쓰는가"]
    assert has_use_case(BODY, "en")
    assert not has_use_case(BODY)  # the Korean heading is not there
    assert has_use_case("## 어디에 쓰는가\n\n로봇 팔.\n", "en")  # an untranslated section counts
    assert not has_use_case("## Where you will use this\n\n## Concepts\n", "en")  # empty
    assert not has_use_case("```\n## Where you will use this\ntext\n```\n", "en")  # inside code


def test_expected_blocks_are_extracted_in_order_with_their_markdown() -> None:
    assert extract_expected(BODY) == [
        "The error settles at **4.3**.\n\n- overshoot below 10%",
        "second",
    ]
    assert extract_expected("```python\nx = 1\n```\n") == []
    assert extract_expected("```expected\n\n```\n") == [""]
    # A longer fence can hold a shorter one.
    nested = "````expected\n```python\nprint(1)\n```\n````\n"
    assert extract_expected(nested) == ["```python\nprint(1)\n```"]


def test_images_outside_code_are_found_with_their_alt_text() -> None:
    refs = image_refs(BODY)
    assert refs == [
        ImageRef("Two frames", "figures/frames.svg"),
        ImageRef("", "figures/no-alt.svg"),
        ImageRef("web", "https://x.test/a.png"),
    ]
    assert refs[0].is_figure and refs[0].figure_name == "frames.svg"
    assert not refs[2].is_figure and refs[2].figure_name is None
    for bad in ("figures/../x.svg", "figures/A.svg", "figures/a/b.svg", "img/a.svg", "a.svg"):
        assert ImageRef("alt", bad).figure_name is None, bad


def test_an_svg_that_could_run_or_fetch_something_is_refused() -> None:
    assert svg_problem(SVG) is None
    assert svg_problem(b"<html></html>") == "is not an SVG document"
    for bad in (
        b"<svg><script>alert(1)</script></svg>",
        b'<svg onload="x()"></svg>',
        b"<svg><foreignObject/></svg>",
        b'<svg><a href="javascript:x"/></svg>',
        b'<svg><image href="https://evil.test/a.png"/></svg>',
        b'<svg><use href="//evil.test/a.svg#x"/></svg>',
    ):
        assert svg_problem(bad) is not None, bad
    # A reference inside the same file is fine.
    assert svg_problem(b'<svg><use href="#arrow"/></svg>') is None


def test_the_static_site_folds_an_expected_block() -> None:
    out = render_expected_blocks("Before.\n\n```expected\nValue **1**.\n\nMore.\n```\n\nAfter.\n")
    assert '??? success "기대 결과"' in out
    assert "    Value **1**." in out and "    More." in out
    assert "```expected" not in out and out.rstrip().endswith("After.")


def _course_with(
    tmp_path: Path, lesson_text: str, *, files: dict[str, bytes], translated: bool = False
) -> Path:
    """A copy of the expert course whose first lesson has ``lesson_text`` appended.

    With ``translated`` the English version gets the same text; without it only the original.
    """
    root = tmp_path / "curriculum"
    shutil.copytree(CURRICULUM / EXPERT, root / EXPERT)
    module = root / EXPERT / "m1-math-physics"
    for name in ("vectors-matrices.md", "vectors-matrices.en.md")[: 2 if translated else 1]:
        lesson = module / name
        lesson.write_text(lesson.read_text("utf-8") + lesson_text, "utf-8")
    figures = module / "figures"
    figures.mkdir(exist_ok=True)
    for name, data in files.items():
        (figures / name).write_bytes(data)
    return root


def _messages(root: Path) -> list[str]:
    return [problem.message for problem in check(root)[1]]


def test_validation_of_figures(tmp_path: Path) -> None:
    extra = "\n![A test square](figures/test-square.svg)\n"
    # Only the original shows it: the translation must show the same figures.
    root = _course_with(tmp_path / "a", extra, files={"test-square.svg": SVG})
    assert any("does not show the same figures" in m for m in _messages(root))
    # A missing file, missing alt text, a bad path and a scripted SVG are each refused.
    missing = _course_with(tmp_path / "b", extra, files={})
    assert any("'test-square.svg' does not exist" in m for m in _messages(missing))
    no_alt = _course_with(
        tmp_path / "c", "\n![](figures/test-square.svg)\n", files={"test-square.svg": SVG}
    )
    assert any("has no alt text" in m for m in _messages(no_alt))
    bad_path = _course_with(tmp_path / "d", "\n![x](../figures/x.svg)\n", files={})
    assert any("must be `figures/<name>.svg`" in m for m in _messages(bad_path))
    scripted = _course_with(
        tmp_path / "e", extra, files={"test-square.svg": b"<svg><script>1</script></svg>"}
    )
    assert any("contains script" in m for m in _messages(scripted))


def test_validation_of_expected_blocks(tmp_path: Path) -> None:
    root = _course_with(tmp_path / "a", "\n```expected\n\n```\n", files={})
    messages = _messages(root)
    # The lesson already carries one answer in each language; the appended block is the second.
    assert any("expected-result block 2 is empty" in m for m in messages)
    assert any("2 expected-result block(s) in the original but 1 in 'en'" in m for m in messages)


def test_the_api_serves_only_the_figures_a_lesson_shows(tmp_path: Path) -> None:
    extra = "\n![A test square](figures/test-square.svg)\n"
    root = _course_with(
        tmp_path, extra, files={"test-square.svg": SVG, "unused.svg": SVG}, translated=True
    )
    assert [m for m in _messages(root) if "figure" in m] == []
    client = TestClient(
        create_app(Settings(curriculum_dir=root, data_dir=tmp_path / "data"), clock=lambda: NOW)
    )
    figure = client.get("/api/v1/lessons/m1-vectors-matrices/figures/test-square.svg")
    assert figure.status_code == 200 and figure.content == SVG
    assert figure.headers["content-type"].startswith("image/svg+xml")
    assert "sandbox" in figure.headers["content-security-policy"]
    assert figure.headers["x-content-type-options"] == "nosniff"
    # A file that exists but that no lesson shows, another lesson's figure, and paths out.
    base = "/api/v1/lessons"
    assert client.get(f"{base}/m1-vectors-matrices/figures/unused.svg").status_code == 404
    assert (
        client.get(f"{base}/m1-rotation-representations/figures/test-square.svg").status_code == 404
    )
    assert client.get(f"{base}/m1-vectors-matrices/figures/..%2Fmodule.yaml").status_code == 404
    assert client.get(f"{base}/nope/figures/test-square.svg").status_code == 404

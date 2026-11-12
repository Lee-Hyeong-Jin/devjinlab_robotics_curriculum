"""Rule 12 (lesson body links) and `rc site build --strict`.

Both exist because the same mistake slipped through twice: a lesson linking another lesson
as a relative path. `rc validate` said nothing, and `mkdocs` only warned — so CI stayed
green on a site with a dead link.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from robotics_curriculum.cli import app
from robotics_curriculum.content import load_course, validate_course

runner = CliRunner()

CURRICULUM = Path(__file__).resolve().parent / "fixtures" / "curriculum"


def write_course(root: Path, body: str, *, translation: str | None = None) -> Path:
    course = root / "course"
    module = course / "mod"
    module.mkdir(parents=True, exist_ok=True)
    (course / "course.yaml").write_text(
        "id: course\ntitle: Course\nsummary: S\nmodules: [mod]\n", encoding="utf-8"
    )
    (module / "module.yaml").write_text(
        "id: mod\ntitle: Module\nsummary: S\nlessons: [l1]\n", encoding="utf-8"
    )
    front = (
        "---\nid: l1\ntitle: Lesson\nsummary: S\nobjectives: [O]\n"
        "difficulty: 3\nestimated_minutes: 60\n---\n\n# L\n\n"
    )
    (module / "l1.md").write_text(front + body, encoding="utf-8")
    if translation is not None:
        (module / "l1.en.md").write_text(
            "---\nid: l1\nlang: en\ntitle: Lesson\nsummary: S\nobjectives: [O]\n---\n\n# L\n\n"
            + translation,
            encoding="utf-8",
        )
    return course


_counter = iter(range(1000))


def messages(root: Path, body: str, **kw: str | None) -> list[str]:
    """Each call gets its own directory, so one test can check several bodies."""
    here = root / f"c{next(_counter)}"
    return [p.message for p in validate_course(load_course(write_course(here, body, **kw)))]


# -- rule 12 ---


def test_a_link_to_another_lesson_file_is_rejected(tmp_path: Path) -> None:
    found = messages(tmp_path, "See [rotations](../m1/rotation.md) first.\n")
    assert any("links to a lesson file" in m for m in found)
    assert any("backticks" in m for m in found)


def test_an_anchor_in_the_link_does_not_hide_it(tmp_path: Path) -> None:
    found = messages(tmp_path, "See [§3](rotation.md#section-3).\n")
    assert any("links to a lesson file" in m for m in found)


def test_http_links_pass_and_a_malformed_one_does_not(tmp_path: Path) -> None:
    assert messages(tmp_path, "See [MR](https://example.org/mr) and [#top](#top).\n") == []
    assert any("malformed link" in m for m in messages(tmp_path, "[x](https://).\n"))


def test_an_unexpected_scheme_is_rejected(tmp_path: Path) -> None:
    found = messages(tmp_path, "Grab [it](ftp://example.org/p.pdf).\n")
    assert any("'ftp:' scheme" in m for m in found)


def test_relative_asset_paths_are_left_alone(tmp_path: Path) -> None:
    """Images and data files are legitimate relative links; only `.md` is the mistake."""
    body = "![diagram](images/frame.png)\n\n[data](data/run.csv)\n"
    assert messages(tmp_path, body) == []


def test_a_link_inside_a_fenced_block_is_not_a_link(tmp_path: Path) -> None:
    body = "```markdown\n[see](other.md)\n```\n\nText.\n"
    assert messages(tmp_path, body) == []


def test_mailto_is_allowed(tmp_path: Path) -> None:
    assert messages(tmp_path, "[ask](mailto:someone@example.org)\n") == []


def test_a_translation_is_checked_too(tmp_path: Path) -> None:
    """A `<lesson>.<lang>.md` can introduce its own broken link."""
    found = messages(tmp_path, "Fine [link](https://example.org).\n", translation="[x](other.md)\n")
    assert any("links to a lesson file" in m and "(en)" in m for m in found)


def test_rc_validate_fails_on_a_lesson_file_link(tmp_path: Path) -> None:
    course = write_course(tmp_path, "See [other](other.md).\n")
    result = runner.invoke(app, ["validate", str(course.parent)])
    assert result.exit_code == 1
    assert "links to a lesson file" in result.output


# -- rc site build --strict ---


def test_site_build_strict_fails_on_a_broken_link(tmp_path: Path) -> None:
    """Without --strict mkdocs only warns, which is how a dead link reached a green CI run."""
    data = tmp_path / "data"
    out = tmp_path / "site"
    # An asset path, which rule 12 allows on purpose — only mkdocs can tell it is missing.
    broken = write_course(tmp_path / "content", "![diagram](images/nowhere-at-all.png)\n")
    args = ["--data-dir", str(data), "--curriculum", str(broken.parent), "site", "build", "--out"]

    lenient = runner.invoke(app, [*args, str(out)])
    assert lenient.exit_code == 0, lenient.output

    strict = runner.invoke(app, [*args, str(tmp_path / "site-strict"), "--strict"])
    assert strict.exit_code == 1, strict.output
    assert "strict" in strict.output


def test_site_build_strict_passes_on_the_real_curriculum(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "--data-dir",
            str(tmp_path / "data"),
            "--curriculum",
            str(CURRICULUM),
            "site",
            "build",
            "--strict",
            "--out",
            str(tmp_path / "site"),
        ],
    )
    assert result.exit_code == 0, result.output

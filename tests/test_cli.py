from pathlib import Path

from typer.testing import CliRunner

from robotics_curriculum import __version__
from robotics_curriculum.cli import app

runner = CliRunner()


def test_version_prints_package_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output.strip() == f"rc {__version__}"


def test_validate_counts_markdown_files(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("# a")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.md").write_text("# b")
    (tmp_path / "ignored.txt").write_text("x")
    result = runner.invoke(app, ["validate", str(tmp_path)])
    assert result.exit_code == 0
    assert "2 markdown file(s) found" in result.output


def test_validate_missing_dir_exits_1(tmp_path: Path) -> None:
    result = runner.invoke(app, ["validate", str(tmp_path / "nope")])
    assert result.exit_code == 1
    assert "is not a directory" in result.output

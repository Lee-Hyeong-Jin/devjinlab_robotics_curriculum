from pathlib import Path

from typer.testing import CliRunner

from robotics_curriculum import __version__
from robotics_curriculum.cli import app

runner = CliRunner()


def test_version_prints_package_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output.strip() == f"rc {__version__}"


def test_validate_default_curriculum_passes() -> None:
    result = runner.invoke(app, ["validate", "curriculum"])
    assert result.exit_code == 0, result.output
    assert result.output.startswith("OK: ")


def test_validate_dir_without_course_yaml_exits_1(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("# a")
    result = runner.invoke(app, ["validate", str(tmp_path)])
    assert result.exit_code == 1
    assert "no course.yaml found" in result.output


def test_validate_missing_dir_exits_1(tmp_path: Path) -> None:
    result = runner.invoke(app, ["validate", str(tmp_path / "nope")])
    assert result.exit_code == 1
    assert "is not a directory" in result.output

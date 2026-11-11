"""`rc` command-line interface."""

from pathlib import Path
from typing import Annotated

import typer

from robotics_curriculum import __version__
from robotics_curriculum.content import check

app = typer.Typer(help="Robotics curriculum tools.", no_args_is_help=True)


@app.command()
def version() -> None:
    """Print the installed version."""
    typer.echo(f"rc {__version__}")


@app.command()
def validate(
    path: Annotated[Path, typer.Argument(help="Curriculum content directory.")] = Path(
        "curriculum"
    ),
) -> None:
    """Load and validate curriculum content; exit 1 if any problem is found."""
    if not path.is_dir():
        typer.echo(f"error: {path} is not a directory", err=True)
        raise typer.Exit(code=1)
    courses, errors = check(path)
    if errors:
        for error in errors:
            typer.echo(f"{error.path}: {error.message}", err=True)
        typer.echo(f"{len(errors)} error(s)", err=True)
        raise typer.Exit(code=1)
    modules = sum(len(course.modules) for course in courses)
    lessons = sum(len(course.iter_lessons()) for course in courses)
    typer.echo(f"OK: {lessons} lessons in {modules} modules")


if __name__ == "__main__":
    app()

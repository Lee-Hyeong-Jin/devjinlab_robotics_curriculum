"""`rc` command-line interface."""

from pathlib import Path
from typing import Annotated

import typer

from robotics_curriculum import __version__

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
    """Validate curriculum content (M0 stub: counts Markdown files)."""
    if not path.is_dir():
        typer.echo(f"error: {path} is not a directory", err=True)
        raise typer.Exit(code=1)
    count = sum(1 for _ in path.rglob("*.md"))
    typer.echo(f"{path}: {count} markdown file(s) found")


if __name__ == "__main__":
    app()

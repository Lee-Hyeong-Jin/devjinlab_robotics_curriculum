"""`rc report` sub-commands (registered in ``robotics_curriculum.cli``)."""

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer

from robotics_curriculum.progress import ProgressError, ProgressService, open_service
from robotics_curriculum.progress.service import find_repo_root
from robotics_curriculum.progress.store import StoreError
from robotics_curriculum.report.module import build_module_report, render_module
from robotics_curriculum.report.weekly import IsoWeek, build_weekly_report, render_weekly

report_app = typer.Typer(help="Generate Markdown learning reports.", no_args_is_help=True)


def _fail(message: str) -> typer.Exit:
    typer.echo(f"error: {message}", err=True)
    return typer.Exit(code=1)


def _generate(ctx: typer.Context, make: Callable[[ProgressService], str]) -> str:
    # ctx.obj is the root callback's options (--data-dir / --curriculum and their env vars).
    data_dir = getattr(ctx.obj, "data_dir", None)
    curriculum = getattr(ctx.obj, "curriculum", None)
    try:
        service = open_service(data_dir, curriculum)
    except (ProgressError, StoreError) as exc:
        raise _fail(str(exc)) from None
    try:
        return make(service)
    except (ProgressError, StoreError) as exc:
        raise _fail(str(exc)) from None
    finally:
        service.store.close()


def _emit(text: str, out: Path | None, stdout: bool) -> None:
    if stdout or out is None:
        typer.echo(text, nl=False)
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    typer.echo(str(out))


@report_app.command("weekly")
def weekly(
    ctx: typer.Context,
    week: Annotated[
        str | None, typer.Option("--week", help="ISO week YYYY-Www [default: this week].")
    ] = None,
    out: Annotated[
        Path | None,
        typer.Option("--out", help="Output file [default: <repo>/reports/weekly/YYYY-Www.md]."),
    ] = None,
    stdout: Annotated[bool, typer.Option("--stdout", help="Print instead of writing.")] = False,
) -> None:
    """Weekly report: study time, completed lessons, stuck points, next suggestions."""
    today = datetime.now().astimezone().date()
    try:
        iso = IsoWeek.parse(week) if week else IsoWeek.of(today)
    except ValueError as exc:
        raise _fail(str(exc)) from None
    text = _generate(ctx, lambda s: render_weekly(build_weekly_report(s, iso, today=today)))
    if out is None and not stdout:
        out = find_repo_root() / "reports" / "weekly" / f"{iso}.md"
    _emit(text, out, stdout)


@report_app.command("module")
def module(
    ctx: typer.Context,
    module_id: Annotated[str, typer.Argument(help="Module id, e.g. m1-math-physics.")],
    out: Annotated[
        Path | None, typer.Option("--out", help="Output file [default: stdout].")
    ] = None,
) -> None:
    """Per-module progress table and understanding distribution."""
    text = _generate(ctx, lambda s: render_module(build_module_report(s, module_id)))
    _emit(text, out, stdout=False)

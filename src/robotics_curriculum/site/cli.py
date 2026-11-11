"""`rc site ...` sub-app (registered in :mod:`robotics_curriculum.cli`)."""

from pathlib import Path
from typing import Annotated

import typer

from robotics_curriculum.progress import ProgressError, open_service

site_app = typer.Typer(
    help="Static site (MkDocs): dashboard, roadmap, lessons.", no_args_is_help=True
)


@site_app.command("build")
def build_cmd(
    ctx: typer.Context,
    out: Annotated[Path, typer.Option("--out", "-o", help="Output directory for HTML.")] = Path(
        "site"
    ),
    src: Annotated[
        Path | None,
        typer.Option("--src", help="Keep the generated MkDocs project here [default: temp dir]."),
    ] = None,
    serve: Annotated[
        bool, typer.Option("--serve", help="Run `mkdocs serve` instead of writing --out.")
    ] = False,
) -> None:
    """Generate the site from curriculum/ and your progress, then run mkdocs."""
    from robotics_curriculum.site.build import build_site, serve_site

    # Global --data-dir / --curriculum come from the root callback's context object.
    opts = ctx.obj
    try:
        service = open_service(getattr(opts, "data_dir", None), getattr(opts, "curriculum", None))
    except ProgressError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from None
    try:
        if serve:
            raise typer.Exit(code=serve_site(service, project_dir=src))
        build_site(service, out, project_dir=src)
    finally:
        service.store.close()
    typer.echo(f"site built: {out.resolve() / 'index.html'}")

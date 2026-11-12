"""`rc site ...` sub-app (registered in :mod:`robotics_curriculum.cli`)."""

from pathlib import Path
from typing import Annotated

import typer

from robotics_curriculum.i18n import DEFAULT_LANG
from robotics_curriculum.progress import ProgressError, open_service
from robotics_curriculum.progress.store import StoreError

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
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            help="Overwrite --out / --src even when they hold files from somewhere else.",
        ),
    ] = False,
    lang: Annotated[
        str | None,
        typer.Option("--lang", help="Site language: ko or en [default: the global --lang]."),
    ] = None,
    strict: Annotated[
        bool,
        typer.Option("--strict", help="Fail on any mkdocs warning (broken link, missing page)."),
    ] = False,
) -> None:
    """Generate the site from curriculum/ and your progress, then run mkdocs.

    ``--out`` and ``--src`` are emptied by mkdocs, so a directory that this command did
    not write is refused unless ``--force`` is given.

    ``--strict`` turns a mkdocs warning into a failure. Without it a link to a page that does
    not exist only prints a warning and the build still succeeds, which let broken lesson
    links through CI; the verification gate uses ``--strict``.
    """
    from robotics_curriculum.site.build import SiteError, build_site, serve_site

    # Global --data-dir / --curriculum come from the root callback's context object.
    opts = ctx.obj
    try:
        service = open_service(getattr(opts, "data_dir", None), getattr(opts, "curriculum", None))
    except (ProgressError, StoreError) as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from None
    chosen = lang or getattr(opts, "lang", None) or DEFAULT_LANG
    try:
        if serve:
            raise typer.Exit(code=serve_site(service, project_dir=src, force=force, lang=chosen))
        build_site(service, out, project_dir=src, force=force, lang=chosen, strict=strict)
    except (SiteError, ProgressError, StoreError) as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from None
    finally:
        service.store.close()
    typer.echo(f"site built: {out.resolve() / 'index.html'}")

"""`rc api serve`: run the HTTP API with uvicorn (needs the ``api`` extra).

FastAPI / uvicorn are imported inside the command so ``rc`` works without the extra.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from robotics_curriculum.api.settings import Settings, SettingsError

api_app = typer.Typer(help="HTTP API server (needs the 'api' extra).", no_args_is_help=True)

INSTALL_HINT = (
    "the API needs the 'api' extra: uv sync --extra api (or pip install 'robotics-curriculum[api]')"
)


@api_app.command("serve")
def serve(
    ctx: typer.Context,
    host: Annotated[
        str | None,
        typer.Option("--host", help="Bind address [default: $RC_API_HOST or 127.0.0.1]."),
    ] = None,
    port: Annotated[
        int | None, typer.Option("--port", help="Port [default: $RC_API_PORT or 8000].")
    ] = None,
    log_level: Annotated[
        str | None,
        typer.Option("--log-level", help="Log level [default: $RC_API_LOG_LEVEL or info]."),
    ] = None,
) -> None:
    """Serve /api/v1 (OpenAPI docs at /docs, schema at /openapi.json)."""
    try:
        import uvicorn

        from robotics_curriculum.api.app import create_app
        from robotics_curriculum.api.log import configure_logging
    except ImportError:
        typer.echo(f"error: {INSTALL_HINT}", err=True)
        raise typer.Exit(code=1) from None
    curriculum: Path | None = getattr(ctx.obj, "curriculum", None)
    data_dir: Path | None = getattr(ctx.obj, "data_dir", None)
    try:
        settings = Settings.from_env().with_overrides(
            curriculum_dir=curriculum, data_dir=data_dir, host=host, port=port, log_level=log_level
        )
    except SettingsError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=1) from None
    configure_logging(settings.log_level)
    uvicorn.run(
        create_app(settings),
        host=settings.host,
        port=settings.port,
        log_config=None,
        access_log=False,  # the request middleware logs every request as JSON
        server_header=False,
    )

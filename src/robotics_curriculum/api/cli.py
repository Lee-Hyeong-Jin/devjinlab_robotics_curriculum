"""`rc api serve` / `rc api promote-admin` (need the ``api`` extra).

FastAPI / uvicorn are imported inside the commands so ``rc`` works without the extra.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer

from robotics_curriculum.api.settings import (
    ALLOW_REMOTE_LOCAL_ENV,
    Settings,
    SettingsError,
    is_loopback,
)

__all__ = ["ALLOW_REMOTE_LOCAL_ENV", "api_app", "is_loopback"]

api_app = typer.Typer(help="HTTP API server (needs the 'api' extra).", no_args_is_help=True)

INSTALL_HINT = (
    "the API needs the 'api' extra: uv sync --extra api (or pip install 'robotics-curriculum[api]')"
)


def _fail(message: str) -> typer.Exit:
    typer.echo(f"error: {message}", err=True)
    return typer.Exit(code=1)


def _settings(ctx: typer.Context, **overrides: object) -> Settings:
    curriculum: Path | None = getattr(ctx.obj, "curriculum", None)
    data_dir: Path | None = getattr(ctx.obj, "data_dir", None)
    try:
        return Settings.from_env().with_overrides(
            curriculum_dir=curriculum,
            data_dir=data_dir,
            **overrides,  # type: ignore[arg-type]
        )
    except SettingsError as exc:
        raise _fail(str(exc)) from None


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
    """Serve /api/v1 (OpenAPI docs at /docs, schema at /openapi.json).

    Local mode has no login (every request acts as the admin user 1), so it only binds to a
    loopback address unless RC_API_ALLOW_REMOTE_LOCAL=1 (e.g. inside a container whose port
    is published on the host's loopback only). Use RC_AUTH_MODE=server for anything else.
    """
    try:
        import uvicorn

        from robotics_curriculum.api.app import UnsafeConfiguration, create_app
        from robotics_curriculum.api.log import configure_logging
    except ImportError:
        raise _fail(INSTALL_HINT) from None
    settings = _settings(ctx, host=host, port=port, log_level=log_level)
    configure_logging(settings.log_level)
    try:
        # create_app refuses an unauthenticated or unreliable configuration (SRV-11, SRV-15).
        app = create_app(settings)
    except UnsafeConfiguration as exc:
        raise _fail(str(exc)) from None
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_config=None,
        access_log=False,  # the request middleware logs every request as JSON
        server_header=False,
    )


@api_app.command("promote-admin")
def promote_admin(
    ctx: typer.Context,
    email: Annotated[str, typer.Argument(help="Email of an existing account.")],
    force: Annotated[
        bool, typer.Option("--force", help="Promote even if the email is not verified.")
    ] = False,
) -> None:
    """Make an existing server-mode account an admin (operator bootstrap; audited)."""
    try:
        from robotics_curriculum.api.app import build_auth
        from robotics_curriculum.auth.service import AuthError, Context
    except ImportError:
        raise _fail(INSTALL_HINT) from None
    settings = _settings(ctx)
    if not settings.server_mode:
        raise _fail("accounts exist only in server mode (set RC_AUTH_MODE=server)")
    auth = build_auth(settings, _now, mailer=None)
    try:
        user = auth.promote_admin(email, Context(request_id="cli:promote-admin"), force=force)
    except AuthError as exc:
        raise _fail(exc.detail) from None
    finally:
        auth.store.close()
    typer.echo(f"{user.email} (id {user.id}) is now admin")


def _now() -> datetime:
    return datetime.now(UTC)

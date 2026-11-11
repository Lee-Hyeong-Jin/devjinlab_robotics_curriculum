"""``rc progress transfer``: copy local progress (SQLite or a JSON export) into another store.

Typical use (US-DB.2): move a learner's local ``.rc/progress.db`` into a server PostgreSQL
database. See ``factory.transfer`` for the merge rules and ``docs/adr/0007-postgres-store.md``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError

from robotics_curriculum.progress.factory import (
    DATABASE_URL_ENV,
    TransferError,
    TransferMode,
    database_url,
    open_store,
    transfer,
)
from robotics_curriculum.progress.models import ProgressExport
from robotics_curriculum.progress.service import default_data_dir
from robotics_curriculum.progress.store import ProgressStore, SqliteProgressStore


def _redact(url: str) -> str:
    """Hide the password in ``scheme://user:password@host/...``."""
    scheme, sep, rest = url.partition("://")
    creds, at, host = rest.rpartition("@")
    if not sep or not at or ":" not in creds:
        return url
    return f"{scheme}://{creds.split(':', 1)[0]}:***@{host}"


def _fail(message: str) -> typer.Exit:
    typer.echo(f"error: {message}", err=True)
    return typer.Exit(code=1)


def transfer_command(
    ctx: typer.Context,
    to: Annotated[
        str | None,
        typer.Option(
            "--to",
            help=f"Destination: postgresql://... or sqlite:///path [default: ${DATABASE_URL_ENV}].",
        ),
    ] = None,
    source_file: Annotated[
        Path | None,
        typer.Option(
            "--from",
            help="JSON file from `rc progress export` [default: the local SQLite progress.db].",
        ),
    ] = None,
    mode: Annotated[
        TransferMode,
        typer.Option(
            help="merge: upsert lessons, skip sessions already there; "
            "replace: wipe the destination first; empty: destination must be empty."
        ),
    ] = TransferMode.MERGE,
    user_id: Annotated[
        int | None,
        typer.Option("--user-id", help="Assign every record to this destination user id."),
    ] = None,
) -> None:
    """Copy local progress into another store, e.g. a server PostgreSQL database."""
    url = to or database_url()
    if not url:
        raise _fail(f"no destination: pass --to URL or set {DATABASE_URL_ENV}")

    source: ProgressStore | ProgressExport
    local: SqliteProgressStore | None = None
    if source_file is not None:
        try:
            source = ProgressExport.model_validate_json(source_file.read_text(encoding="utf-8"))
        except OSError as exc:
            raise _fail(f"cannot read {source_file}: {exc.strerror}") from None
        except ValidationError as exc:
            raise _fail(f"{source_file} is not a valid progress export:\n{exc}") from None
        origin = str(source_file)
    else:
        # The local SQLite store, regardless of RC_DATABASE_URL (that names the destination).
        local = SqliteProgressStore.in_dir(getattr(ctx.obj, "data_dir", None) or default_data_dir())
        source, origin = local, str(local.path)

    try:
        try:
            dest = open_store(url=url)
        except (ValueError, RuntimeError) as exc:
            raise _fail(str(exc)) from None
        except Exception as exc:  # connection refused, auth failure, ...
            raise _fail(f"cannot open {_redact(url)}: {type(exc).__name__}: {exc}") from None
        try:
            result = transfer(source, dest, mode=mode, user_id=user_id)
        except TransferError as exc:
            raise _fail(f"{exc} (try --mode merge or --mode replace)") from None
        finally:
            dest.close()
    finally:
        if local is not None:
            local.close()

    skipped = (
        f", skipped {result.skipped_sessions} duplicate sessions" if result.skipped_sessions else ""
    )
    typer.echo(
        f"transferred {result.lessons} lesson rows, {result.sessions} sessions{skipped} "
        f"from {origin} to {_redact(url)}"
    )

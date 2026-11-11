"""Alembic environment for the PostgreSQL progress store.

Connection, in order: ``config.attributes["connection"]`` (set by
``progress.postgres.upgrade``), ``sqlalchemy.url`` in the config, then ``$RC_DATABASE_URL``.
"""

import os

from alembic import context
from sqlalchemy import Connection, engine_from_config, pool

from robotics_curriculum.progress.postgres import DATABASE_URL_ENV, metadata, normalize_url

config = context.config
target_metadata = metadata


def _url() -> str:
    url = config.get_main_option("sqlalchemy.url") or os.environ.get(DATABASE_URL_ENV)
    if not url:
        raise RuntimeError(f"set sqlalchemy.url or ${DATABASE_URL_ENV} to a postgresql:// URL")
    return normalize_url(url)


def _run(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    context.configure(url=_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
elif (conn := config.attributes.get("connection")) is not None:
    _run(conn)
else:
    section = config.get_section(config.config_ini_section, {})
    section["sqlalchemy.url"] = _url()
    engine = engine_from_config(section, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with engine.connect() as connection:
        _run(connection)
        connection.commit()

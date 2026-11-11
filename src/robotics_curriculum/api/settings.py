"""API settings from environment variables (no FastAPI import, so the CLI can load it).

| variable              | default                  |
|-----------------------|--------------------------|
| ``RC_CURRICULUM_DIR`` | ``<repo>/curriculum``    |
| ``RC_DATA_DIR``       | ``<repo>/.rc``           |
| ``RC_API_HOST``       | ``127.0.0.1``            |
| ``RC_API_PORT``       | ``8000``                 |
| ``RC_API_LOG_LEVEL``  | ``info``                 |
| ``RC_AUTH_MODE``      | ``local`` (no login, user 1) or ``server`` (accounts, sessions, PATs) |
| ``RC_DATABASE_URL``   | unset: SQLite in the data dir; ``postgresql://...`` for server mode |
| ``RC_AUTH_COOKIE_SECURE`` | ``1`` (``0`` only for plain-HTTP development) |

Auth policy variables (``RC_AUTH_*``, ``RC_SMTP_*``) are read by
:meth:`robotics_curriculum.auth.service.AuthConfig.from_env` and
:meth:`robotics_curriculum.auth.mailer.SmtpConfig.from_env`.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path

from robotics_curriculum.progress import default_curriculum_dir, default_data_dir

LOG_LEVELS = ("critical", "error", "warning", "info", "debug")
AUTH_MODES = ("local", "server")


class SettingsError(ValueError):
    """A setting has an invalid value."""


@dataclass(frozen=True, slots=True)
class Settings:
    curriculum_dir: Path
    data_dir: Path
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "info"
    auth_mode: str = "local"
    database_url: str | None = None
    cookie_secure: bool = True

    @property
    def server_mode(self) -> bool:
        return self.auth_mode == "server"

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        """Read the ``RC_*`` variables from ``env`` (default ``os.environ``)."""
        env = os.environ if env is None else env
        curriculum = env.get("RC_CURRICULUM_DIR")
        data = env.get("RC_DATA_DIR")
        port = env.get("RC_API_PORT")
        mode = (env.get("RC_AUTH_MODE") or "local").lower()
        if mode not in AUTH_MODES:
            raise SettingsError(f"invalid RC_AUTH_MODE '{mode}' (use local or server)")
        base = cls(
            curriculum_dir=Path(curriculum) if curriculum else default_curriculum_dir(),
            data_dir=Path(data) if data else default_data_dir(),
            auth_mode=mode,
            database_url=(env.get("RC_DATABASE_URL") or "").strip() or None,
            cookie_secure=env.get("RC_AUTH_COOKIE_SECURE", "1") != "0",
        )
        return base.with_overrides(
            host=env.get("RC_API_HOST") or None,
            port=_parse_port(port) if port else None,
            log_level=env.get("RC_API_LOG_LEVEL") or None,
        )

    def with_overrides(
        self,
        *,
        curriculum_dir: Path | None = None,
        data_dir: Path | None = None,
        host: str | None = None,
        port: int | None = None,
        log_level: str | None = None,
    ) -> Settings:
        """A copy with every non-``None`` argument applied (and validated)."""
        if port is not None and not 1 <= port <= 65535:
            raise SettingsError(f"invalid port {port} (use 1-65535)")
        if log_level is not None:
            log_level = log_level.lower()
            if log_level not in LOG_LEVELS:
                raise SettingsError(
                    f"invalid log level '{log_level}' (use one of {', '.join(LOG_LEVELS)})"
                )
        return replace(
            self,
            curriculum_dir=curriculum_dir or self.curriculum_dir,
            data_dir=data_dir or self.data_dir,
            host=host or self.host,
            port=port or self.port,
            log_level=log_level or self.log_level,
        )


def _parse_port(text: str) -> int:
    try:
        return int(text)
    except ValueError:
        raise SettingsError(f"invalid RC_API_PORT '{text}' (use 1-65535)") from None

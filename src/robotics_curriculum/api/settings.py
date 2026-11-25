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
| ``RC_API_METRICS``    | ``1``: serve Prometheus ``/metrics`` (``0`` = 404) |
| ``RC_API_METRICS_TOKEN`` | unset: ``/metrics`` is open; set = require that bearer token |

Auth policy variables (``RC_AUTH_*``, ``RC_SMTP_*``) are read by
:meth:`robotics_curriculum.auth.service.AuthConfig.from_env` and
:meth:`robotics_curriculum.auth.mailer.SmtpConfig.from_env`.
"""

from __future__ import annotations

import ipaddress
import os
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from robotics_curriculum.api.clientip import Network, TrustedProxyError, parse_trusted_proxies
from robotics_curriculum.i18n import LANGS, SERVICE_DEFAULT_LANG, Lang, normalize_lang
from robotics_curriculum.progress import default_curriculum_dir, default_data_dir
from robotics_curriculum.timezone import DEFAULT_TIMEZONE

LOG_LEVELS = ("critical", "error", "warning", "info", "debug")
AUTH_MODES = ("local", "server")
ALLOW_REMOTE_LOCAL_ENV = "RC_API_ALLOW_REMOTE_LOCAL"


def is_loopback(host: str) -> bool:
    """``True`` for ``localhost`` and any loopback IP literal."""
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


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
    metrics: bool = True
    metrics_token: str | None = None
    timezone: ZoneInfo = field(default_factory=lambda: ZoneInfo(DEFAULT_TIMEZONE))
    """The service's time zone (``RC_TIMEZONE``, default ``Asia/Seoul``): where a day begins for
    visits, sign-up trends, streaks and weekly reports, and the zone log lines and exports are
    written in. Stored times stay absolute instants; this only decides how they are cut into
    days and shown."""
    default_lang: Lang = SERVICE_DEFAULT_LANG
    """Language of a request that names none: no ``?lang=``, no ``Accept-Language``
    (``RC_DEFAULT_LANG``, default ``en``). The curriculum's source language is Korean either
    way; this decides what an anonymous client, a crawler or a mail without a known reader
    language gets."""
    ops_metrics: bool = True
    """Record request statistics, failed requests and visits for the admin monitoring page
    (``RC_OPS_METRICS=0`` turns it off; server mode only, ADR 0017)."""
    trusted_proxies: tuple[Network, ...] = field(
        default_factory=lambda: parse_trusted_proxies(None)
    )
    """Addresses of the web tier and reverse proxies allowed to name the client through
    ``X-Forwarded-For`` (``RC_API_TRUSTED_PROXIES``). Loopback by default."""
    public_content: bool = False
    """Serve the curriculum (courses, modules, lessons, resources, search) to anonymous
    readers so it can be crawled and linked (ADR 0016). Progress, notes, quiz results,
    reports and the admin API always need a session. Off by default: turning it on is a
    deliberate decision about what a deployment publishes."""

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
            metrics=env.get("RC_API_METRICS", "1") != "0",
            metrics_token=(env.get("RC_API_METRICS_TOKEN") or "").strip() or None,
            public_content=env.get("RC_PUBLIC_CONTENT", "0") == "1",
            ops_metrics=env.get("RC_OPS_METRICS", "1") != "0",
            timezone=parse_timezone(env.get("RC_TIMEZONE")),
            default_lang=parse_default_lang(env.get("RC_DEFAULT_LANG")),
            trusted_proxies=_parse_proxies(env.get("RC_API_TRUSTED_PROXIES")),
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


def parse_default_lang(value: str | None) -> Lang:
    """``RC_DEFAULT_LANG`` as a supported language; blank means English.

    Raises:
        SettingsError: The value is not one of the languages the service speaks.
    """
    if not (value or "").strip():
        return SERVICE_DEFAULT_LANG
    lang = normalize_lang(value)
    if lang is None:
        raise SettingsError(f"invalid RC_DEFAULT_LANG '{value}' (use one of: {', '.join(LANGS)})")
    return lang


def parse_timezone(value: str | None) -> ZoneInfo:
    """An IANA zone name (``Asia/Seoul``) as a zone; blank means the default.

    Raises:
        SettingsError: The name is not a zone this system knows.
    """
    name = (value or "").strip() or DEFAULT_TIMEZONE
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        raise SettingsError(
            f"invalid RC_TIMEZONE '{name}' (use an IANA name such as Asia/Seoul or UTC)"
        ) from None


def _parse_proxies(value: str | None) -> tuple[Network, ...]:
    try:
        return parse_trusted_proxies(value)
    except TrustedProxyError as exc:
        raise SettingsError(str(exc)) from None


def _parse_port(text: str) -> int:
    try:
        return int(text)
    except ValueError:
        raise SettingsError(f"invalid RC_API_PORT '{text}' (use 1-65535)") from None

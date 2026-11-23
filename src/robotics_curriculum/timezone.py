"""The service's time zone.

Times are stored as absolute instants and stay that way. The zone decides two things only:
where a calendar day begins (today's visits, this week's report, a study streak) and how a time
is written for a person (log lines, exports, screens). It is Korea Standard Time unless
``RC_TIMEZONE`` says otherwise.
"""

from __future__ import annotations

from datetime import date, datetime, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_TIMEZONE = "Asia/Seoul"
"""IANA name of the default zone: Korea Standard Time (UTC+9, no daylight saving)."""


def default_timezone() -> ZoneInfo:
    return ZoneInfo(DEFAULT_TIMEZONE)


def local_day(moment: datetime, tz: tzinfo) -> date:
    """The calendar day ``moment`` falls on in ``tz``."""
    return moment.astimezone(tz).date()


def day_start(day: date, tz: tzinfo) -> datetime:
    """Midnight at the start of ``day`` in ``tz``, as an aware datetime."""
    return datetime(day.year, day.month, day.day, tzinfo=tz)


def is_timezone(name: str) -> bool:
    """True for an IANA zone name this system knows (``Asia/Seoul``, ``UTC``).

    Abbreviations (``KST``), offsets (``+09:00``) and anything path-like are refused: a stored
    zone is handed to every client's date formatter, which rejects them.
    """
    if not name or name != name.strip() or name.startswith(("/", ".")) or ".." in name:
        return False
    try:
        ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, OSError):
        return False
    return True

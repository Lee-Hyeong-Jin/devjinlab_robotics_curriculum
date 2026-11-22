"""The service's time zone.

Times are stored as absolute instants and stay that way. The zone decides two things only:
where a calendar day begins (today's visits, this week's report, a study streak) and how a time
is written for a person (log lines, exports, screens). It is Korea Standard Time unless
``RC_TIMEZONE`` says otherwise.
"""

from __future__ import annotations

from datetime import date, datetime, tzinfo
from zoneinfo import ZoneInfo

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

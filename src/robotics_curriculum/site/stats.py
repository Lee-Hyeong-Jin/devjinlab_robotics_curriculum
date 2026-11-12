"""Dashboard numbers for the static site.

The calculations live in :mod:`robotics_curriculum.learn.stats` so that the site, the CLI and
the API share one implementation (platform-design §6). This module only re-exports them under
the names the page renderers already use.
"""

from robotics_curriculum.learn.stats import (
    NO_STAGE,
    STAGES,
    DashboardStats,
    Ratio,
    StageProgress,
    WeekStats,
    activity_days,
    dashboard,
    format_minutes,
    format_seconds,
    ordered_stages,
    ratio,
    stage_label,
    stage_of,
    streak,
    week_start,
    week_stats,
)

__all__ = [
    "NO_STAGE",
    "STAGES",
    "DashboardStats",
    "Ratio",
    "StageProgress",
    "WeekStats",
    "activity_days",
    "dashboard",
    "format_minutes",
    "format_seconds",
    "stage_label",
    "ordered_stages",
    "ratio",
    "stage_of",
    "streak",
    "week_start",
    "week_stats",
]

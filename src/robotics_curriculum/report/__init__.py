"""Learning reports (PRD FR-7): weekly report and per-module report as Markdown."""

from robotics_curriculum.report.module import ModuleReport, build_module_report, render_module
from robotics_curriculum.report.weekly import (
    IsoWeek,
    WeeklyReport,
    build_weekly_report,
    format_duration,
    render_weekly,
)

__all__ = [
    "IsoWeek",
    "ModuleReport",
    "WeeklyReport",
    "build_module_report",
    "build_weekly_report",
    "format_duration",
    "render_module",
    "render_weekly",
]

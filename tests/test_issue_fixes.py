"""Regression tests for fixes tracked as GitHub issues (the number is in each test's name)."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest

from robotics_curriculum.progress import ProgressService, SqliteProgressStore
from robotics_curriculum.report.weekly import IsoWeek, build_weekly_report

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "curriculum"
NOW = datetime(2026, 11, 11, 9, 0, tzinfo=UTC)
EXPERT = "robotics-expert"
RESEARCH = "robotics-research"


@pytest.fixture
def service(tmp_path: Path) -> Iterator[ProgressService]:
    """A learner on the real curriculum, which has two courses."""
    store = SqliteProgressStore.in_dir(tmp_path)
    svc = ProgressService(store, ProgressService.load_curriculum(CURRICULUM), clock=lambda: NOW)
    yield svc
    store.close()


def _first_lesson(service: ProgressService, course_id: str) -> str:
    return next(s.lesson.id for s in service.status(course_id))


# -- #31: next week's suggestions mixed in another course's lessons ---------------------------


def test_issue_31_a_new_learner_is_offered_the_first_course_only(
    service: ProgressService,
) -> None:
    assert [c.id for c in service.courses][0] == EXPERT
    assert service.focus_course_ids() == [EXPERT]
    assert {s.course.id for s in service.next_lessons()} == {EXPERT}


def test_issue_31_suggestions_stay_in_the_course_being_studied(service: ProgressService) -> None:
    service.done(_first_lesson(service, EXPERT), understanding=4)
    assert service.focus_course_ids() == [EXPERT]
    # The research track's opening lessons have no prerequisites, so they used to outrank the
    # expert course's next lessons.
    assert {s.course.id for s in service.next_lessons(limit=10)} == {EXPERT}
    report = build_weekly_report(service, IsoWeek.of(NOW.date()), today=NOW.date(), tz=UTC)
    suggested = {line.lesson_id for line in report.next_lessons}
    expert_ids = {s.lesson.id for s in service.status(EXPERT)}
    assert suggested and suggested <= expert_ids


def test_issue_31_a_second_course_joins_once_it_is_started(service: ProgressService) -> None:
    service.done(_first_lesson(service, EXPERT), understanding=4)
    service.start(_first_lesson(service, RESEARCH))
    assert service.focus_course_ids() == [EXPERT, RESEARCH]
    assert {s.course.id for s in service.next_lessons()} == {EXPERT, RESEARCH}
    # Asking for one course by name is unchanged.
    assert {s.course.id for s in service.next_lessons(RESEARCH)} == {RESEARCH}
    assert {s.course.id for s in service.next_lessons(EXPERT)} == {EXPERT}

"""Weekly / module reports (P0-4, FR-7): fixed input -> expected Markdown."""

from collections.abc import Iterator
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from robotics_curriculum.cli import app
from robotics_curriculum.progress import ProgressService, SqliteProgressStore
from robotics_curriculum.report import (
    IsoWeek,
    build_module_report,
    build_weekly_report,
    format_duration,
    render_module,
    render_weekly,
)

CURRICULUM = Path(__file__).resolve().parents[1] / "curriculum"
VECTORS = "m1-vectors-matrices"
ROTATION = "m1-rotation-representations"
DH = "m2-dh-parameters"
W46 = IsoWeek(2026, 46)  # Mon 2026-11-09 .. Sun 2026-11-15
TODAY = date(2026, 11, 13)


class Clock:
    def __init__(self) -> None:
        self.now = datetime(2026, 11, 2, 10, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def _service(data_dir: Path, clock: Clock) -> ProgressService:
    store = SqliteProgressStore.in_dir(data_dir)
    return ProgressService(store, ProgressService.load_curriculum(CURRICULUM), clock=clock)


def _seed(service: ProgressService, clock: Clock) -> None:
    def at(month: int, day: int, hour: int) -> None:
        clock.now = datetime(2026, month, day, hour, 0, tzinfo=UTC)

    at(11, 2, 10)  # previous week: DH started, not counted in W46
    service.log(DH, 30)
    at(11, 10, 10)
    service.log(VECTORS, 60, note="행렬 곱 연습")
    at(11, 11, 10)
    service.log(VECTORS, 45)
    service.done(VECTORS, understanding=4, note="벡터 정리 완료")
    at(11, 12, 20)
    service.log(ROTATION, 90)
    service.done(ROTATION, understanding=2)
    at(11, 12, 21)
    service.log(DH, 30)


@pytest.fixture
def seeded(tmp_path: Path) -> Iterator[ProgressService]:
    clock = Clock()
    service = _service(tmp_path, clock)
    _seed(service, clock)
    yield service
    service.store.close()


def test_iso_week_parse_and_bounds() -> None:
    week = IsoWeek.parse("2026-W46")
    assert week == W46 and str(week) == "2026-W46"
    assert (week.monday, week.sunday) == (date(2026, 11, 9), date(2026, 11, 15))
    assert IsoWeek.of(date(2026, 11, 11)) == W46
    for bad in ("2026-46", "2026-W54", "W46"):
        with pytest.raises(ValueError):
            IsoWeek.parse(bad)


def test_format_duration() -> None:
    assert [format_duration(s) for s in (0, 2700, 12000)] == ["0m", "45m", "3h 20m"]


def test_weekly_report_numbers(seeded: ProgressService) -> None:
    report = build_weekly_report(seeded, W46, today=TODAY, tz=UTC)
    assert report.as_of == TODAY
    assert report.total_seconds == (60 + 45 + 90 + 30) * 60
    assert (report.session_count, report.active_days) == (4, 3)
    assert [(c.lesson_id, c.seconds_this_week, c.understanding) for c in report.completed] == [
        (VECTORS, 105 * 60, 4),
        (ROTATION, 90 * 60, 2),
    ]
    assert [p.lesson_id for p in report.in_progress] == [DH]
    assert [(m.module_id, m.seconds) for m in report.module_time] == [
        ("m1-math-physics", 195 * 60),
        ("m2-kinematics", 30 * 60),
    ]
    assert [(s.lesson_id, s.detail) for s in report.stuck] == [
        (ROTATION, "이해도 2/5"),
        (DH, "11일째 진행 중"),
    ]
    assert [n.lesson_id for n in report.next_lessons] == [DH]
    assert [(n.day, n.text) for n in report.notes] == [
        (date(2026, 11, 10), "행렬 곱 연습"),
        (date(2026, 11, 11), "벡터 정리 완료"),
    ]


def test_weekly_report_markdown(seeded: ProgressService) -> None:
    text = render_weekly(build_weekly_report(seeded, W46, today=TODAY, tz=UTC))
    assert text.startswith("# 주간 리포트 2026-W46\n")
    for heading in ("요약", "모듈별 학습 시간", "완료한 레슨", "퀴즈·복습", "메모 요약"):
        assert f"\n## {heading}\n" in text
    for heading in ("막힌 지점", "다음 주 제안"):
        assert f"\n## {heading}\n" in text
    assert "- 학습 시간: 3h 45m" in text
    assert "- 세션: 4회 (학습한 날 3일)" in text
    assert "- 완료한 레슨: 2개" in text
    assert "| 벡터·행렬 (`m1-vectors-matrices`) | 1h 45m | 4/5 |" in text
    assert "| M1 수학·물리 기초 (`m1-math-physics`) | 3h 15m |" in text
    assert "- DH 파라미터 (`m2-dh-parameters`): 11일째 진행 중" in text
    assert "- 11-10 `m1-vectors-matrices`: 행렬 곱 연습" in text
    assert "1. DH 파라미터 (`m2-dh-parameters`): 진행 중" in text


def test_past_week_is_judged_as_of_its_sunday(seeded: ProgressService) -> None:
    report = build_weekly_report(seeded, IsoWeek(2026, 45), today=TODAY, tz=UTC)
    assert report.as_of == date(2026, 11, 8)
    assert report.total_seconds == 30 * 60 and report.completed == []
    # DH started 11-02: 6 days by 11-08, not yet stuck; ROTATION's low score still shows.
    assert [s.lesson_id for s in report.stuck] == [ROTATION]


def test_empty_week_still_renders(tmp_path: Path) -> None:
    service = _service(tmp_path, Clock())
    try:
        text = render_weekly(build_weekly_report(service, W46, today=TODAY, tz=UTC))
    finally:
        service.store.close()
    assert "- 학습 시간: 0m" in text
    assert "이번 주 학습 기록이 없습니다." in text
    assert "이번 주 완료한 레슨이 없습니다." in text
    assert "## 막힌 지점\n\n없음" in text
    assert "1. 벡터·행렬 (`m1-vectors-matrices`): 시작 전" in text


def test_module_report(seeded: ProgressService) -> None:
    text = render_module(build_module_report(seeded, "m1-math-physics"))
    assert "- 진도: 2/2 레슨 (100%)" in text
    assert "| 회전 표현 (오일러 각 / 쿼터니언) (`m1-rotation-representations`) | 완료" in text
    assert "- 4점: 1개" in text and "- 2점: 1개" in text


# -- CLI -----------------------------------------------------------------------

runner = CliRunner()


def _cli_args(data_dir: Path) -> list[str]:
    return ["--data-dir", str(data_dir), "--curriculum", str(CURRICULUM), "report"]


def test_cli_weekly_writes_default_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    clock = Clock()
    service = _service(tmp_path / "data", clock)
    _seed(service, clock)
    service.store.close()
    project = tmp_path / "proj"
    project.mkdir()
    (project / "pyproject.toml").write_text("")
    monkeypatch.chdir(project)

    result = runner.invoke(app, [*_cli_args(tmp_path / "data"), "weekly", "--week", "2026-W46"])
    assert result.exit_code == 0, result.output
    out = project / "reports" / "weekly" / "2026-W46.md"
    assert result.output.strip() == str(out)
    text = out.read_text(encoding="utf-8")
    assert text.startswith("# 주간 리포트 2026-W46")
    assert "- 학습 시간: 3h 45m" in text


def test_cli_weekly_out_and_stdout(tmp_path: Path) -> None:
    args = _cli_args(tmp_path / "data")
    target = tmp_path / "x" / "r.md"
    result = runner.invoke(app, [*args, "weekly", "--week", "2026-W01", "--out", str(target)])
    assert result.exit_code == 0, result.output
    assert target.read_text(encoding="utf-8").startswith("# 주간 리포트 2026-W01")

    result = runner.invoke(app, [*args, "weekly", "--week", "2026-W01", "--stdout"])
    assert result.exit_code == 0, result.output
    assert result.output.startswith("# 주간 리포트 2026-W01")

    result = runner.invoke(app, [*args, "weekly", "--week", "2026-46"])
    assert result.exit_code == 1 and "invalid ISO week" in result.output


def test_cli_module(tmp_path: Path) -> None:
    args = _cli_args(tmp_path / "data")
    result = runner.invoke(app, [*args, "module", "m2-kinematics"])
    assert result.exit_code == 0, result.output
    assert result.output.startswith("# 모듈 리포트: M2 로봇 운동학")
    result = runner.invoke(app, [*args, "module", "nope"])
    assert result.exit_code == 1 and "unknown module" in result.output

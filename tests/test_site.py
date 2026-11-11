"""Static site generation (P1-5) from the fixture curriculum + seeded progress."""

import re
import shutil
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner

from robotics_curriculum.cli import app
from robotics_curriculum.content import load_courses
from robotics_curriculum.progress import ProgressService, Session, SqliteProgressStore
from robotics_curriculum.site import build_site, generate_project
from robotics_curriculum.site.pages import split_study_section
from robotics_curriculum.site.stats import streak, week_stats

FIXTURE = Path(__file__).parent / "fixtures" / "curriculum"
NOW = datetime(2026, 11, 11, 12, 0, tzinfo=UTC)  # a Wednesday
M1 = "modules/m1-math-physics"
M2 = "modules/m2-kinematics"

STUDY = """
## 이 단계 공부법

1. **교재:** Sample Robotics Textbook 3장을 읽는다.
2. **문제:** 연습문제를 푼다.

## 참고
"""


@pytest.fixture
def curriculum(tmp_path: Path) -> Path:
    """Fixture copy with a 공부법 section, math, and a locked lesson (dh needs rotation)."""
    root = tmp_path / "curriculum"
    shutil.copytree(FIXTURE, root)
    course = root / "sample-course"
    dh = course / "m2-kinematics" / "dh-parameters.md"
    text = dh.read_text(encoding="utf-8")
    text = text.replace(
        "prerequisites: [m1-vectors-matrices]", "prerequisites: [m1-rotation-representations]"
    )
    dh.write_text(text + "\n수식 $T = A_1 A_2$ 를 본다.\n" + STUDY, encoding="utf-8")
    return root


@pytest.fixture
def service(curriculum: Path, tmp_path: Path) -> ProgressService:
    store = SqliteProgressStore.in_dir(tmp_path / "rcdata")
    svc = ProgressService(store, load_courses(curriculum), clock=lambda: NOW)
    svc.log("m1-vectors-matrices", 40)
    svc.done("m1-vectors-matrices", understanding=4)
    svc.log("m1-rotation-representations", 30)
    yield svc
    store.close()


@pytest.fixture
def docs(service: ProgressService, tmp_path: Path) -> Path:
    generate_project(service, tmp_path / "project", now=NOW)
    return tmp_path / "project" / "docs"


def read(docs: Path, rel: str) -> str:
    return (docs / rel).read_text(encoding="utf-8")


def test_generates_all_pages_and_config(docs: Path) -> None:
    for rel in [
        "index.md",
        "roadmap.md",
        "resources.md",
        f"{M1}/index.md",
        f"{M1}/m1-vectors-matrices.md",
        f"{M1}/m1-rotation-representations.md",
        f"{M2}/index.md",
        f"{M2}/m2-dh-parameters.md",
        "assets/katex/katex.min.js",
        "assets/rc.css",
    ]:
        assert (docs / rel).is_file(), rel
    config = (docs.parent / "mkdocs.yml").read_text(encoding="utf-8")
    assert "site_name: 샘플 코스" in config
    assert "name: material" in config
    assert "font: false" in config  # no Google Fonts request
    assert "pymdownx.arithmatex" in config
    assert "대시보드: index.md" in config and "자료실: resources.md" in config


def test_dashboard_shows_position_progress_week_and_next(docs: Path) -> None:
    page = read(docs, "index.md")
    for heading in ["## 현재 위치", "## 한눈에 보기", "## 단계별 진행률", "## 다음 레슨"]:
        assert heading in page
    assert "[회전 표현](modules/m1-math-physics/m1-rotation-representations.md)" in page
    assert "#study-method" in page
    assert "1시간 10분" in page  # 40m + 30m this week
    assert "2회 세션" in page
    assert "1 / 3" in page  # lessons done
    assert "1일" in page  # streak
    assert "오늘 복습" in page
    assert "| **기초** |" in page and "50% (1/2)" in page
    assert "단계 미지정" in page  # m2 has no level


def test_roadmap_groups_by_stage_with_statuses(docs: Path) -> None:
    page = read(docs, "roadmap.md")
    assert page.index("## 기초") < page.index("## 중급") < page.index("## 단계 미지정")
    assert "■ 완료</span> [벡터와 행렬]" in page
    assert "▣ 진행 중</span> [회전 표현]" in page
    assert "▨ 잠김</span> [DH 파라미터]" in page
    assert "선수: 회전 표현" in page


def test_module_page_has_lesson_table(docs: Path) -> None:
    page = read(docs, f"{M1}/index.md")
    assert page.startswith("# M1 수학·물리")
    assert "| # | 레슨 | 상태 | 예상 시간 | 난이도 | 선수 레슨 |" in page
    assert "[벡터와 행렬](m1-vectors-matrices.md) (완료)" in page
    assert "30분" in page


def test_lesson_page_header_body_study_and_resources(docs: Path) -> None:
    page = read(docs, f"{M2}/m2-dh-parameters.md")
    assert page.startswith("# DH 파라미터\n")
    assert page.count("# DH 파라미터") == 1  # body H1 dropped
    assert "**학습 목표**" in page and "- DH 파라미터의 의미를 설명할 수 있다." in page
    assert "[회전 표현](../m1-math-physics/m1-rotation-representations.md)" in page
    assert "▣ 진행 중" in page  # prerequisite status
    assert '!!! warning "잠김"' in page
    assert "난이도 ●●●○○ (3/5)" in page
    # 공부법: moved out of the body into the callout, not duplicated.
    assert page.count("이 단계 공부법") == 2  # header link + section heading
    assert "## 이 단계 공부법 {#study-method}" in page
    assert '!!! tip "이렇게 공부하세요"' in page
    assert "    1. **교재:** Sample Robotics Textbook 3장을 읽는다." in page
    assert "## 참고" in page  # rest of the body kept
    assert page.index("## 참고") < page.index("## 이 단계 공부법")
    # resources grouped by kind
    resources = page[page.index("## 학습 자료") :]
    assert "### 교재" in resources
    assert "- Sample Robotics Textbook — Ch. 3" in resources


def test_lesson_without_study_section_gets_fallback(docs: Path) -> None:
    page = read(docs, f"{M1}/m1-vectors-matrices.md")
    assert "공부법이 아직 작성되지 않았습니다" in page
    assert "등록된 자료가 없습니다." in page
    assert "이해도 4/5" in page
    assert "■ 완료" in page


def test_resources_page_links_back_to_lessons(docs: Path) -> None:
    page = read(docs, "resources.md")
    assert page.startswith("# 자료실")
    assert "## 교재" in page
    assert "Sample Robotics Textbook — Ch. 3 · 레슨: [DH 파라미터]" in page
    assert "(modules/m2-kinematics/m2-dh-parameters.md)" in page


def test_split_study_section_ignores_headings_in_code() -> None:
    body = "intro\n## 이 단계 공부법\n\n```\n## not a heading\n```\nstep\n## 다음\nrest\n"
    rest, section = split_study_section(body)
    assert section == "```\n## not a heading\n```\nstep"
    assert rest == "intro\n## 다음\nrest\n"
    assert split_study_section("no section") == ("no section", None)


def test_week_stats_and_streak() -> None:
    def session(day: int, minutes: int) -> Session:
        start = datetime(2026, 11, day, 9, 0, tzinfo=UTC)
        return Session(lesson_id="x", started_at=start, ended_at=start + timedelta(minutes=minutes))

    sessions = [session(8, 60), session(9, 30), session(11, 15)]  # 8th = Sunday, last week
    week = week_stats(sessions, NOW)
    assert week.start == date(2026, 11, 9)
    assert (week.seconds, week.sessions) == (45 * 60, 2)
    days = {date(2026, 11, d) for d in (8, 9, 10)}
    assert streak(days, date(2026, 11, 11)) == 3  # nothing today yet: counts up to yesterday
    assert streak(days | {date(2026, 11, 11)}, date(2026, 11, 11)) == 4
    assert streak({date(2026, 11, 5)}, date(2026, 11, 11)) == 0


def test_mkdocs_build_renders_html_offline(service: ProgressService, tmp_path: Path) -> None:
    out = build_site(service, tmp_path / "site", now=NOW)
    for rel in ["index.html", "roadmap.html", "resources.html", f"{M2}/m2-dh-parameters.html"]:
        assert (out / rel).is_file(), rel
    assert (out / "assets/katex/fonts/KaTeX_Main-Regular.woff2").is_file()
    lesson = (out / f"{M2}/m2-dh-parameters.html").read_text(encoding="utf-8")
    assert '<span class="arithmatex">\\(T = A_1 A_2\\)</span>' in lesson
    assert 'id="study-method"' in lesson
    assert "admonition tip" in lesson
    # every script / stylesheet is local (works without network)
    refs = re.findall(r'<(?:script src|link rel="stylesheet" href)="([^"]+)"', lesson)
    assert refs and not [r for r in refs if r.startswith(("http:", "https:", "//"))]


def test_cli_site_build(curriculum: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    result = CliRunner().invoke(
        app,
        [
            "--data-dir",
            str(tmp_path / "clidata"),
            "--curriculum",
            str(curriculum),
            "site",
            "build",
            "--out",
            str(out),
            "--src",
            str(tmp_path / "src"),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "site built" in result.output
    assert (out / "index.html").is_file()
    assert "시작 전" in (tmp_path / "src" / "docs" / "roadmap.md").read_text(encoding="utf-8")

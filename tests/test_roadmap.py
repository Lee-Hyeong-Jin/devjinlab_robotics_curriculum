"""`rc roadmap` and the recommended-prerequisite note (P1-3, ADR 0015)."""

from pathlib import Path

from typer.testing import CliRunner, Result

from robotics_curriculum.cli import app
from robotics_curriculum.i18n import translator
from robotics_curriculum.progress import DB_FILENAME

CURRICULUM = Path(__file__).resolve().parent / "fixtures" / "curriculum"
VECTORS = "m1-vectors-matrices"
PREREQ_NOTE = translator("ko")("cli.note_prereq", ids=VECTORS)
ROTATION = "m1-rotation-representations"
DH = "m2-dh-parameters"

runner = CliRunner()


def rc(data_dir: Path, *args: str) -> Result:
    return runner.invoke(app, ["--data-dir", str(data_dir), "--curriculum", str(CURRICULUM), *args])


def _line(output: str, lesson_id: str) -> str:
    (line,) = [ln for ln in output.splitlines() if f" {lesson_id} " in ln]
    return line.strip()


# -- recommended-prerequisite note (informational; nothing is blocked) ---------


def test_start_before_the_prerequisites_notes_it_and_still_starts(tmp_path: Path) -> None:
    result = rc(tmp_path, "start", DH)
    assert result.exit_code == 0, result.output
    assert PREREQ_NOTE in result.stderr
    assert DH in result.stdout
    assert _line(rc(tmp_path, "roadmap").stdout, DH).startswith("[>]")


def test_start_with_the_prerequisites_done_says_nothing(tmp_path: Path) -> None:
    result = rc(tmp_path, "start", VECTORS)
    assert result.exit_code == 0, result.output
    assert result.stderr.strip() == ""


def test_log_and_done_before_the_prerequisites_note_it(tmp_path: Path) -> None:
    result = rc(tmp_path, "log", ROTATION, "30")
    assert result.exit_code == 0 and PREREQ_NOTE in result.stderr
    result = rc(tmp_path, "done", ROTATION)
    assert result.exit_code == 0 and PREREQ_NOTE in result.stderr
    # VECTORS has no prerequisites, and DH's are done by now.
    assert rc(tmp_path, "done", VECTORS).stderr.strip() == ""
    assert rc(tmp_path, "log", DH, "10").stderr.strip() == ""


# -- rc roadmap ----------------------------------------------------------------


def test_roadmap_without_progress_db(tmp_path: Path) -> None:
    result = rc(tmp_path, "roadmap")
    assert result.exit_code == 0, result.output
    out = result.stdout
    assert _line(out, VECTORS) == f"[ ] {VECTORS}  벡터와 행렬  (30m; prereq: -)"
    # No locked marker any more (ADR 0015): a lesson with unfinished prerequisites still
    # shows as "not started", with the prerequisite listed on the same line.
    assert _line(out, ROTATION) == f"[ ] {ROTATION}  회전 표현  (30m; prereq: {VECTORS})"
    assert _line(out, DH).startswith("[ ]")
    assert "[-]" not in out
    assert "== 기초 ==" in out and "== (레벨 미지정) ==" in out
    assert "M1 수학·물리 (m1-math-physics)  0/2 done, est 1h" in out
    assert "0/3 lessons done" in out
    assert not (tmp_path / DB_FILENAME).exists()


def test_roadmap_markers_after_progress(tmp_path: Path) -> None:
    assert rc(tmp_path, "done", VECTORS).exit_code == 0
    assert rc(tmp_path, "log", DH, "20").exit_code == 0
    out = rc(tmp_path, "roadmap").stdout
    assert _line(out, VECTORS).startswith("[x]")
    assert _line(out, ROTATION).startswith("[ ]")  # prerequisites done, not started
    assert _line(out, DH).startswith("[>]")
    assert "(m1-math-physics)  1/2 done" in out
    assert "(m2-kinematics)  0/1 done" in out
    assert "1/3 lessons done" in out


def test_roadmap_level_filter(tmp_path: Path) -> None:
    out = rc(tmp_path, "roadmap", "--level", "기초").stdout
    assert VECTORS in out and ROTATION in out and DH not in out
    out = rc(tmp_path, "roadmap", "--level", "고급").stdout
    assert VECTORS not in out and "no modules at level 고급" in out
    result = rc(tmp_path, "roadmap", "--level", "expert")
    assert result.exit_code == 1 and "unknown level 'expert'" in result.stderr


def test_roadmap_course_filter(tmp_path: Path) -> None:
    result = rc(tmp_path, "roadmap", "--course", "sample-course")
    assert result.exit_code == 0 and VECTORS in result.stdout
    result = rc(tmp_path, "roadmap", "--course", "nope")
    assert result.exit_code == 1
    assert "unknown course 'nope'" in result.stderr

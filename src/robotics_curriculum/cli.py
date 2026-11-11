"""`rc` command-line interface."""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError

from robotics_curriculum import __version__
from robotics_curriculum.content import QuizParseError, check, parse_quiz
from robotics_curriculum.learn.quiz import record_quiz_run, run_quiz, select_questions
from robotics_curriculum.learn.review import (
    due_cards,
    due_count,
    recent_accuracy,
    run_review,
)
from robotics_curriculum.library import resources, show
from robotics_curriculum.progress import (
    LessonSummary,
    ProgressError,
    ProgressExport,
    ProgressService,
    open_service,
    parse_duration,
)
from robotics_curriculum.report.cli import report_app
from robotics_curriculum.roadmap import roadmap
from robotics_curriculum.site.cli import site_app

app = typer.Typer(help="Robotics curriculum tools.", no_args_is_help=True)
progress_app = typer.Typer(help="Export / import learner progress (JSON).", no_args_is_help=True)
app.add_typer(progress_app, name="progress")
app.add_typer(report_app, name="report")
app.add_typer(site_app, name="site")


@dataclass
class _Options:
    data_dir: Path | None = None
    curriculum: Path | None = None


@app.callback()
def main(
    ctx: typer.Context,
    data_dir: Annotated[
        Path | None,
        typer.Option(
            "--data-dir",
            envvar="RC_DATA_DIR",
            help="Directory holding progress.db [default: <repo>/.rc].",
        ),
    ] = None,
    curriculum: Annotated[
        Path | None,
        typer.Option(
            "--curriculum",
            envvar="RC_CURRICULUM_DIR",
            help="Curriculum root for progress commands [default: <repo>/curriculum].",
        ),
    ] = None,
) -> None:
    """Robotics curriculum tools."""
    ctx.obj = _Options(data_dir=data_dir, curriculum=curriculum)


def _fail(message: str) -> typer.Exit:
    typer.echo(f"error: {message}", err=True)
    return typer.Exit(code=1)


@contextmanager
def _service(ctx: typer.Context) -> Iterator[ProgressService]:
    opts = ctx.obj if isinstance(ctx.obj, _Options) else _Options()
    try:
        service = open_service(opts.data_dir, opts.curriculum)
    except ProgressError as exc:
        raise _fail(str(exc)) from None
    try:
        yield service
    except ProgressError as exc:
        raise _fail(str(exc)) from None
    finally:
        service.store.close()


def _fmt_seconds(seconds: int) -> str:
    if seconds <= 0:
        return "-"
    minutes = max(1, round(seconds / 60))
    if minutes < 60:
        return f"{minutes}m"
    return f"{minutes // 60}h {minutes % 60:02d}m"


def _width(text: str) -> int:
    """Terminal columns; Hangul / CJK characters take two."""
    return sum(2 if ord(ch) >= 0x1100 else 1 for ch in text)


def _table(headers: list[str], rows: list[list[str]]) -> str:
    cols = [max(_width(row[i]) for row in [headers, *rows]) for i in range(len(headers))]
    lines = []
    for row in [headers, ["-" * c for c in cols], *rows]:
        cells = [cell + " " * (cols[i] - _width(cell)) for i, cell in enumerate(row)]
        lines.append("  ".join(cells).rstrip())
    return "\n".join(lines)


_LABEL = {"done": "done", "in_progress": "in progress", "not_started": "not started"}


def _status_label(summary: LessonSummary) -> str:
    if summary.status == "not_started" and summary.locked:
        return "locked"
    return _LABEL[summary.status.value]


def _local_today(now: datetime) -> date:
    return now.astimezone().date()


def _prompt(text: str) -> str:
    """Terminal input for quiz / review sessions (EOF or Ctrl-C aborts via click)."""
    return str(typer.prompt(text, default="", show_default=False, prompt_suffix=""))


def _review_header(service: ProgressService, now: datetime) -> str:
    """``오늘 복습 N장 · 최근 7일 퀴즈 정답률 X% (c/t)`` for ``rc status`` (AC-4.6)."""
    today = _local_today(now)
    due = due_count(service.store, today=today, user_id=service.user_id)
    accuracy = recent_accuracy(
        service.store.list_quiz_attempts(service.user_id), since=now - timedelta(days=7)
    )
    if accuracy is None:
        rate = "기록 없음"
    else:
        correct, total = accuracy
        rate = f"{round(100 * correct / total)}% ({correct}/{total})"
    return f"오늘 복습: {due}장 · 최근 7일 퀴즈 정답률: {rate}"


def _warn_locked(service: ProgressService, lesson_id: str) -> None:
    """Forced open of a locked lesson: warn on stderr but carry on."""
    missing = service.missing_prerequisites(lesson_id)
    if missing:
        typer.echo(f"warning: prerequisites not done: {', '.join(missing)}", err=True)


@app.command()
def version() -> None:
    """Print the installed version."""
    typer.echo(f"rc {__version__}")


@app.command()
def validate(
    path: Annotated[Path, typer.Argument(help="Curriculum content directory.")] = Path(
        "curriculum"
    ),
) -> None:
    """Load and validate curriculum content; exit 1 if any problem is found."""
    if not path.is_dir():
        typer.echo(f"error: {path} is not a directory", err=True)
        raise typer.Exit(code=1)
    courses, errors = check(path)
    if errors:
        for error in errors:
            typer.echo(f"{error.path}: {error.message}", err=True)
        typer.echo(f"{len(errors)} error(s)", err=True)
        raise typer.Exit(code=1)
    modules = sum(len(course.modules) for course in courses)
    lessons = sum(len(course.iter_lessons()) for course in courses)
    typer.echo(f"OK: {lessons} lessons in {modules} modules")


@app.command()
def status(
    ctx: typer.Context,
    course: Annotated[str | None, typer.Option("--course", help="Only this course id.")] = None,
) -> None:
    """Show per-lesson progress, study time, and the running timer."""
    with _service(ctx) as service:
        summaries = service.status(course)
        running = service.current_session()
        review_line = _review_header(service, service.clock())
    if running is None:
        typer.echo("열린 타이머: 없음")
    else:
        since = f"{running.started_at:%Y-%m-%d %H:%M} UTC"
        typer.echo(f"열린 타이머: {running.lesson_id} (since {since})")
    typer.echo(review_line)
    courses = {s.course.id: s.course for s in summaries}
    for course_obj in courses.values():
        rows = [s for s in summaries if s.course.id == course_obj.id]
        n_done = sum(1 for s in rows if s.status == "done")
        total = sum(s.progress.total_seconds for s in rows)
        pct = round(100 * n_done / len(rows)) if rows else 0
        typer.echo("")
        typer.echo(
            f"{course_obj.title} ({course_obj.id})  {pct}%  "
            f"({n_done}/{len(rows)} lessons, time {_fmt_seconds(total)})"
        )
        table_rows = [
            [
                s.module.id,
                s.lesson.id,
                s.lesson.title,
                _status_label(s),
                _fmt_seconds(s.progress.total_seconds),
                f"{s.lesson.estimated_minutes}m",
                f"{s.progress.completed_at:%Y-%m-%d}" if s.progress.completed_at else "-",
            ]
            for s in rows
        ]
        headers = ["module", "lesson", "title", "status", "time", "est", "completed"]
        typer.echo(_table(headers, table_rows))


@app.command()
def start(
    ctx: typer.Context,
    lesson_id: Annotated[str, typer.Argument(help="Lesson id, e.g. m1-vectors-matrices.")],
) -> None:
    """Start a study timer for a lesson (only one may run at a time)."""
    with _service(ctx) as service:
        session = service.start(lesson_id)
        _warn_locked(service, lesson_id)
        title = service.lesson(lesson_id).title
    typer.echo(f"started {lesson_id} ({title}) at {session.started_at:%Y-%m-%d %H:%M} UTC")


@app.command()
def stop(
    ctx: typer.Context,
    note: Annotated[str | None, typer.Option("--note", "-m", help="Session note.")] = None,
    discard: Annotated[
        bool, typer.Option("--discard", help="Delete the running session instead.")
    ] = False,
) -> None:
    """Stop the running timer and add the elapsed time to its lesson."""
    with _service(ctx) as service:
        session, seconds = service.stop(note, discard=discard)
    if discard:
        typer.echo(f"discarded session for {session.lesson_id}")
    else:
        typer.echo(f"stopped {session.lesson_id}: {_fmt_seconds(seconds)}")


@app.command()
def log(
    ctx: typer.Context,
    lesson_id: Annotated[str, typer.Argument(help="Lesson id.")],
    duration: Annotated[str, typer.Argument(help="Minutes: 45, 45m, 1h or 1h30m.")],
    note: Annotated[str | None, typer.Option("--note", "-m", help="Session note.")] = None,
) -> None:
    """Record study time manually (a session ending now)."""
    with _service(ctx) as service:
        minutes = parse_duration(duration)
        service.log(lesson_id, minutes, note)
        _warn_locked(service, lesson_id)
    typer.echo(f"logged {_fmt_seconds(minutes * 60)} on {lesson_id}")


@app.command()
def done(
    ctx: typer.Context,
    lesson_id: Annotated[str, typer.Argument(help="Lesson id.")],
    understanding: Annotated[
        int | None,
        typer.Option("--understanding", "-u", min=1, max=5, help="Self-rated understanding 1-5."),
    ] = None,
    note: Annotated[str | None, typer.Option("--note", "-m", help="Free-form note.")] = None,
) -> None:
    """Mark a lesson done (stops its running timer, if any)."""
    with _service(ctx) as service:
        progress, unlocked = service.done(lesson_id, understanding=understanding, note=note)
        _warn_locked(service, lesson_id)
        title = service.lesson(lesson_id).title
    extra = f", 이해도 {progress.understanding}" if progress.understanding else ""
    typer.echo(f"done {lesson_id} ({title}), time {_fmt_seconds(progress.total_seconds)}{extra}")
    for lesson in unlocked:
        typer.echo(f"  unlocked: {lesson.id} ({lesson.title})")


@app.command("next")
def next_(
    ctx: typer.Context,
    course: Annotated[str | None, typer.Option("--course", help="Only this course id.")] = None,
    count: Annotated[int, typer.Option("-n", min=1, help="How many to show.")] = 3,
) -> None:
    """Recommend lessons whose prerequisites are done (in-progress first, then course order)."""
    with _service(ctx) as service:
        lessons = service.next_lessons(course, limit=count)
    if not lessons:
        typer.echo("nothing to do: every available lesson is done")
        return
    rows = [
        [
            str(i),
            s.lesson.id,
            s.lesson.title,
            _LABEL[s.status.value],
            f"{s.lesson.estimated_minutes}m",
            str(s.lesson.difficulty),
        ]
        for i, s in enumerate(lessons, 1)
    ]
    typer.echo(_table(["#", "lesson", "title", "status", "est", "difficulty"], rows))
    typer.echo(f"\nstart: rc start {lessons[0].lesson.id}")


@app.command()
def quiz(
    ctx: typer.Context,
    lesson_id: Annotated[str, typer.Argument(help="Lesson id.")],
    only: Annotated[
        str | None, typer.Option("--only", help="Comma-separated question ids to ask.")
    ] = None,
    retry_wrong: Annotated[
        bool, typer.Option("--retry-wrong", help="Only questions last answered wrong.")
    ] = False,
) -> None:
    """Take the lesson's quiz in the terminal; wrong answers become flashcards."""
    with _service(ctx) as service:
        lesson = service.lesson(lesson_id)
        try:
            lesson_quiz = parse_quiz(lesson)
        except QuizParseError as exc:
            raise _fail(f"quiz of '{lesson_id}' is invalid (run `rc validate`):\n{exc}") from None
        if not lesson_quiz.questions:
            raise _fail(f"lesson '{lesson_id}' has no quiz block")
        wanted = [q.strip() for q in only.split(",") if q.strip()] if only else None
        try:
            questions = select_questions(
                lesson_quiz,
                only=wanted,
                retry_wrong=retry_wrong,
                store=service.store,
                user_id=service.user_id,
            )
        except ValueError as exc:
            raise _fail(str(exc)) from None
        if not questions:
            typer.echo("풀 문항이 없습니다 (마지막 시도에서 모두 정답)")
            return
        typer.echo(f"퀴즈: {lesson.title} ({lesson.id}) — {len(questions)}문항\n")
        try:
            result = run_quiz(
                lesson,
                lesson_quiz,
                questions,
                prompt=_prompt,
                echo=typer.echo,
                clock=service.clock,
            )
        except (typer.Abort, EOFError, KeyboardInterrupt):
            typer.echo("\n중단: 결과를 저장하지 않았습니다", err=True)
            raise typer.Exit(code=1) from None
        recorded = record_quiz_run(service.store, lesson, result, user_id=service.user_id)
    cards = recorded.new_cards
    if cards:
        detail = f"오답 {recorded.new_quiz_cards} + 개념 {recorded.new_concept_cards}"
        typer.echo(f"새 카드 {len(cards)}장 ({detail}) → `rc review` 로 복습")
    typer.echo(f"소요 {_fmt_seconds(recorded.run.seconds)} · 저장됨")


@app.command()
def review(
    ctx: typer.Context,
    count: Annotated[int | None, typer.Option("-n", min=1, help="At most this many cards.")] = None,
    lesson: Annotated[
        str | None, typer.Option("--lesson", help="Only cards from this lesson id.")
    ] = None,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="List due cards without reviewing.")
    ] = False,
) -> None:
    """Review due flashcards with SM-2 (1 again · 2 hard · 3 good · 4 easy)."""
    with _service(ctx) as service:
        now = service.clock()
        today = _local_today(now)
        if lesson is not None:
            service.lesson(lesson)  # validates the id
        cards = due_cards(
            service.store, today=today, user_id=service.user_id, lesson_id=lesson, limit=count
        )
        if not cards:
            typer.echo("오늘 복습할 카드가 없습니다")
            return
        if dry_run:
            rows = [
                [d.card.id, d.card.lesson_id, d.card.source, f"{d.state.due:%Y-%m-%d}"]
                for d in cards
            ]
            typer.echo(_table(["card", "lesson", "source", "due"], rows))
            typer.echo(f"\n{len(cards)}장 due")
            return
        typer.echo(f"복습 {len(cards)}장\n")
        try:
            run_review(
                service.store,
                cards,
                prompt=_prompt,
                echo=typer.echo,
                now=now,
                today=today,
                user_id=service.user_id,
            )
        except (typer.Abort, EOFError, KeyboardInterrupt):
            typer.echo("\n중단: 답한 카드까지는 저장되었습니다", err=True)
            raise typer.Exit(code=1) from None


@progress_app.command("export")
def progress_export(
    ctx: typer.Context,
    file: Annotated[Path | None, typer.Argument(help="Output JSON file [default: stdout].")] = None,
) -> None:
    """Write all progress rows and sessions as JSON."""
    with _service(ctx) as service:
        data = service.export()
    text = data.model_dump_json(indent=2)
    if file is None:
        typer.echo(text)
        return
    file.write_text(text + "\n", encoding="utf-8")
    typer.echo(
        f"exported {len(data.lesson_progress)} lesson rows, {len(data.sessions)} sessions to {file}"
    )


@progress_app.command("import")
def progress_import(
    ctx: typer.Context,
    file: Annotated[Path, typer.Argument(help="JSON file from `rc progress export`.")],
    replace: Annotated[
        bool, typer.Option("--replace", help="Overwrite existing progress.")
    ] = False,
) -> None:
    """Load progress from a JSON export (the store must be empty unless --replace)."""
    try:
        data = ProgressExport.model_validate_json(file.read_text(encoding="utf-8"))
    except OSError as exc:
        raise _fail(f"cannot read {file}: {exc.strerror}") from None
    except ValidationError as exc:
        raise _fail(f"{file} is not a valid progress export:\n{exc}") from None
    with _service(ctx) as service:
        n_lessons, n_sessions = service.import_(data, replace=replace)
    typer.echo(f"imported {n_lessons} lesson rows, {n_sessions} sessions")


app.command()(resources)
app.command()(show)
app.command()(roadmap)


if __name__ == "__main__":
    app()

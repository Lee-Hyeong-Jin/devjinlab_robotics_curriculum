"""`rc` command-line interface."""

import logging
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError

from robotics_curriculum import __version__
from robotics_curriculum.api.cli import api_app
from robotics_curriculum.content import QuizParseError, check, parse_quiz
from robotics_curriculum.i18n import LANG_ENV, Translator, get_translator
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
from robotics_curriculum.progress.store import StoreError
from robotics_curriculum.progress.transfer_cli import transfer_command
from robotics_curriculum.report.cli import report_app
from robotics_curriculum.roadmap import roadmap
from robotics_curriculum.site.cli import site_app

app = typer.Typer(help="Robotics curriculum tools.", no_args_is_help=True)
progress_app = typer.Typer(help="Export, import, transfer progress.", no_args_is_help=True)
app.add_typer(progress_app, name="progress")
app.add_typer(report_app, name="report")
app.add_typer(site_app, name="site")
app.add_typer(api_app, name="api")


@dataclass
class _Options:
    data_dir: Path | None = None
    curriculum: Path | None = None
    verbose: bool = False
    lang: str | None = None


def _setup_logging(verbose: bool) -> None:
    """Send library logs to stderr; -v turns on debug detail.

    Study notes and other personal data are never logged (engineering rules),
    so the handler is safe to leave on at warning level.
    """
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )


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
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Log what the command does to stderr."),
    ] = False,
    lang: Annotated[
        str | None,
        typer.Option(
            "--lang",
            envvar=LANG_ENV,
            help="Message language: ko or en [default: ko].",
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
    _setup_logging(verbose)
    ctx.obj = _Options(data_dir=data_dir, curriculum=curriculum, verbose=verbose, lang=lang)


def _t(ctx: typer.Context | None = None) -> Translator:
    """The translator for this invocation (``--lang`` / ``RC_LANG`` / Korean)."""
    lang = getattr(ctx.obj, "lang", None) if ctx is not None else None
    return get_translator(lang)


def _fail(message: str, ctx: typer.Context | None = None) -> typer.Exit:
    typer.echo(_t(ctx)("cli.error_prefix", message=message), err=True)
    return typer.Exit(code=1)


@contextmanager
def _service(ctx: typer.Context) -> Iterator[ProgressService]:
    opts = ctx.obj if isinstance(ctx.obj, _Options) else _Options()
    try:
        service = open_service(opts.data_dir, opts.curriculum)
    except (ProgressError, StoreError) as exc:
        raise _fail(str(exc)) from None
    try:
        yield service
    # StoreError carries a user-facing sentence (locked database, constraint);
    # the CLI is the only place that turns an exception into a message.
    except (ProgressError, StoreError) as exc:
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


def _status_label(summary: LessonSummary, t: Translator) -> str:
    if summary.status == "not_started" and summary.locked:
        return t("cli.state.locked")
    return t(f"cli.state.{summary.status.value}")


def _local_today(now: datetime) -> date:
    return now.astimezone().date()


def _prompt(text: str) -> str:
    """Terminal input for quiz / review sessions (EOF or Ctrl-C aborts via click)."""
    return str(typer.prompt(text, default="", show_default=False, prompt_suffix=""))


def _review_header(service: ProgressService, now: datetime, t: Translator) -> str:
    """Cards due today and the 7-day quiz accuracy, for ``rc status`` (AC-4.6)."""
    today = _local_today(now)
    due = due_count(service.store, today=today, user_id=service.user_id)
    accuracy = recent_accuracy(
        service.store.list_quiz_attempts(service.user_id), since=now - timedelta(days=7)
    )
    if accuracy is None:
        rate = t("cli.no_record")
    else:
        correct, total = accuracy
        rate = f"{round(100 * correct / total)}% ({correct}/{total})"
    return t("cli.review_line", due=due, rate=rate)


def _warn_locked(service: ProgressService, lesson_id: str, t: Translator) -> None:
    """Forced open of a locked lesson: warn on stderr but carry on."""
    missing = service.missing_prerequisites(lesson_id)
    if missing:
        typer.echo(t("cli.warn_prereq", ids=", ".join(missing)), err=True)


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
    t = _t(ctx)
    with _service(ctx) as service:
        summaries = service.status(course)
        running = service.current_session()
        review_line = _review_header(service, service.clock(), t)
    if running is None:
        typer.echo(t("cli.timer.none"))
    else:
        since = f"{running.started_at:%Y-%m-%d %H:%M}"
        typer.echo(t("cli.timer.running", lesson_id=running.lesson_id, since=since))
    typer.echo(review_line)
    courses = {s.course.id: s.course for s in summaries}
    for course_obj in courses.values():
        rows = [s for s in summaries if s.course.id == course_obj.id]
        n_done = sum(1 for s in rows if s.status == "done")
        total = sum(s.progress.total_seconds for s in rows)
        pct = round(100 * n_done / len(rows)) if rows else 0
        typer.echo("")
        typer.echo(
            t(
                "cli.status.course_line",
                title=course_obj.title,
                course_id=course_obj.id,
                percent=pct,
                done=n_done,
                total=len(rows),
                time=_fmt_seconds(total),
            )
        )
        table_rows = [
            [
                s.module.id,
                s.lesson.id,
                s.lesson.title,
                _status_label(s, t),
                _fmt_seconds(s.progress.total_seconds),
                f"{s.lesson.estimated_minutes}m",
                f"{s.progress.completed_at:%Y-%m-%d}" if s.progress.completed_at else "-",
            ]
            for s in rows
        ]
        headers = [
            t("cli.status.header_module"),
            t("cli.status.header_lesson"),
            t("cli.status.header_title"),
            t("cli.status.header_state"),
            t("cli.status.header_time"),
            t("cli.status.header_estimate"),
            t("cli.status.header_completed"),
        ]
        typer.echo(_table(headers, table_rows))


@app.command()
def start(
    ctx: typer.Context,
    lesson_id: Annotated[str, typer.Argument(help="Lesson id, e.g. m1-vectors-matrices.")],
) -> None:
    """Start a study timer for a lesson (only one may run at a time)."""
    t = _t(ctx)
    with _service(ctx) as service:
        session = service.start(lesson_id)
        _warn_locked(service, lesson_id, t)
        title = service.lesson(lesson_id).title
    at = f"{session.started_at:%Y-%m-%d %H:%M}"
    typer.echo(t("cli.start", lesson_id=lesson_id, title=title, at=at))


@app.command()
def stop(
    ctx: typer.Context,
    note: Annotated[str | None, typer.Option("--note", "-m", help="Session note.")] = None,
    discard: Annotated[
        bool, typer.Option("--discard", help="Delete the running session instead.")
    ] = False,
) -> None:
    """Stop the running timer and add the elapsed time to its lesson."""
    t = _t(ctx)
    with _service(ctx) as service:
        session, seconds = service.stop(note, discard=discard)
    if discard:
        typer.echo(t("cli.stop_discarded", lesson_id=session.lesson_id))
    else:
        typer.echo(t("cli.stop", lesson_id=session.lesson_id, time=_fmt_seconds(seconds)))


@app.command()
def log(
    ctx: typer.Context,
    lesson_id: Annotated[str, typer.Argument(help="Lesson id.")],
    duration: Annotated[str, typer.Argument(help="Minutes: 45, 45m, 1h or 1h30m.")],
    note: Annotated[str | None, typer.Option("--note", "-m", help="Session note.")] = None,
) -> None:
    """Record study time manually (a session ending now)."""
    t = _t(ctx)
    with _service(ctx) as service:
        minutes = parse_duration(duration)
        service.log(lesson_id, minutes, note)
        _warn_locked(service, lesson_id, t)
    typer.echo(t("cli.logged", lesson_id=lesson_id, time=_fmt_seconds(minutes * 60)))


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
    t = _t(ctx)
    with _service(ctx) as service:
        progress, unlocked = service.done(lesson_id, understanding=understanding, note=note)
        _warn_locked(service, lesson_id, t)
        title = service.lesson(lesson_id).title
    extra = (
        t("cli.done_understanding", value=progress.understanding) if progress.understanding else ""
    )
    typer.echo(
        t(
            "cli.done_line",
            lesson_id=lesson_id,
            title=title,
            time=_fmt_seconds(progress.total_seconds),
            extra=extra,
        )
    )
    for lesson in unlocked:
        typer.echo(t("cli.unlocked", lesson_id=lesson.id, title=lesson.title))


@app.command("next")
def next_(
    ctx: typer.Context,
    course: Annotated[str | None, typer.Option("--course", help="Only this course id.")] = None,
    count: Annotated[int, typer.Option("-n", min=1, help="How many to show.")] = 3,
) -> None:
    """Recommend lessons whose prerequisites are done (in-progress first, then course order)."""
    t = _t(ctx)
    with _service(ctx) as service:
        lessons = service.next_lessons(course, limit=count)
    if not lessons:
        typer.echo(t("cli.next.empty"))
        return
    rows = [
        [
            str(i),
            s.lesson.id,
            s.lesson.title,
            t(f"cli.state.{s.status.value}"),
            f"{s.lesson.estimated_minutes}m",
            str(s.lesson.difficulty),
        ]
        for i, s in enumerate(lessons, 1)
    ]
    headers = [
        t("cli.status.header_index"),
        t("cli.status.header_lesson"),
        t("cli.status.header_title"),
        t("cli.status.header_state"),
        t("cli.status.header_estimate"),
        t("cli.status.header_difficulty"),
    ]
    typer.echo(_table(headers, rows))
    typer.echo("\n" + t("cli.next.hint", lesson_id=lessons[0].lesson.id))


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
    t = _t(ctx)
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
            typer.echo(t("quiz.nothing_to_ask"))
            return
        typer.echo(
            t("quiz.intro", title=lesson.title, lesson_id=lesson.id, count=len(questions)) + "\n"
        )
        try:
            result = run_quiz(
                lesson,
                lesson_quiz,
                questions,
                prompt=_prompt,
                echo=typer.echo,
                clock=service.clock,
                t=t,
            )
        except (typer.Abort, EOFError, KeyboardInterrupt):
            typer.echo("\n" + t("quiz.aborted"), err=True)
            raise typer.Exit(code=1) from None
        recorded = record_quiz_run(service.store, lesson, result, user_id=service.user_id)
    cards = recorded.new_cards
    if cards:
        detail = t(
            "quiz.new_cards_detail",
            wrong=recorded.new_quiz_cards,
            concept=recorded.new_concept_cards,
        )
        typer.echo(t("quiz.new_cards", count=len(cards), detail=detail))
    typer.echo(t("quiz.elapsed", time=_fmt_seconds(recorded.run.seconds)))


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
    t = _t(ctx)
    with _service(ctx) as service:
        now = service.clock()
        today = _local_today(now)
        if lesson is not None:
            service.lesson(lesson)  # validates the id
        cards = due_cards(
            service.store, today=today, user_id=service.user_id, lesson_id=lesson, limit=count
        )
        if not cards:
            typer.echo(t("review.none_due"))
            return
        if dry_run:
            rows = [
                [d.card.id, d.card.lesson_id, d.card.source, f"{d.state.due:%Y-%m-%d}"]
                for d in cards
            ]
            headers = [
                t("review.header.card"),
                t("review.header.lesson"),
                t("review.header.source"),
                t("review.header.due"),
            ]
            typer.echo(_table(headers, rows))
            typer.echo("\n" + t("review.due_count", count=len(cards)))
            return
        typer.echo(t("review.session_intro", count=len(cards)) + "\n")
        try:
            run_review(
                service.store,
                cards,
                prompt=_prompt,
                echo=typer.echo,
                now=now,
                today=today,
                user_id=service.user_id,
                t=t,
            )
        except (typer.Abort, EOFError, KeyboardInterrupt):
            typer.echo("\n" + t("review.aborted"), err=True)
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
    allow_unknown: Annotated[
        bool,
        typer.Option(
            "--allow-unknown",
            help="Import rows whose lesson ids are not in this curriculum.",
        ),
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
        n_lessons, n_sessions = service.import_(data, replace=replace, allow_unknown=allow_unknown)
    typer.echo(f"imported {n_lessons} lesson rows, {n_sessions} sessions")


app.command()(resources)
app.command()(show)
app.command()(roadmap)
progress_app.command("transfer")(transfer_command)


if __name__ == "__main__":
    app()

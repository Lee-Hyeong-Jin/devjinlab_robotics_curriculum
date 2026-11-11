"""Quiz grading and ``rc quiz`` sessions (PRD FR-4.1, FR-4.2; appendix C.1 AC-4.2, AC-4.3).

Grading is pure (:func:`grade_answer`). :func:`run_quiz` drives a session through an injected
``prompt`` / ``echo`` pair so the CLI and tests share it, and :func:`record_quiz_run` writes
the outcome (run, attempts, cards, activity state) in one transaction only after every
question was answered, so an aborted session leaves no trace.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime

from robotics_curriculum.content import Lesson, LessonQuiz, QuizQuestion
from robotics_curriculum.content.quiz_block import resolve_activity
from robotics_curriculum.i18n import DEFAULT_LANG, Translator, translator
from robotics_curriculum.learn.sm2 import Sm2State
from robotics_curriculum.progress import (
    DEFAULT_USER,
    ActivityProgress,
    Card,
    CardState,
    LessonStatus,
    ProgressStore,
    QuizAttempt,
    QuizRun,
)

Prompt = Callable[[str], str]
Echo = Callable[[str], None]


def _default_t() -> Translator:
    """Korean, the source language; callers that know better pass their own translator."""
    return translator(DEFAULT_LANG)


_TRUE = {"o", "t", "true", "y", "yes", "참", "예", "맞다", "1"}
_FALSE = {"x", "f", "false", "n", "no", "거짓", "아니오", "틀리다", "0"}
_SEPARATORS = re.compile(r"[,\s]+")


class InvalidAnswer(ValueError):
    """The typed answer cannot be interpreted for this question type (ask again)."""


def normalize_short(text: str) -> str:
    """trim, lower-case and collapse whitespace (short-answer comparison)."""
    return " ".join(text.strip().lower().split())


def parse_choice_indexes(text: str, count: int, t: Translator | None = None) -> set[int]:
    """``"1, 3"`` -> ``{0, 2}`` for a question with ``count`` choices."""
    t = t or _default_t()
    tokens = [token for token in _SEPARATORS.split(text.strip()) if token]
    if not tokens:
        raise InvalidAnswer(t("quiz.invalid.need_number", count=count))
    indexes: set[int] = set()
    for token in tokens:
        if not token.isdigit() or not 1 <= int(token) <= count:
            raise InvalidAnswer(t("quiz.invalid.not_in_range", token=token, count=count))
        indexes.add(int(token) - 1)
    return indexes


def parse_truefalse(text: str, t: Translator | None = None) -> bool:
    value = text.strip().lower()
    if value in _TRUE:
        return True
    if value in _FALSE:
        return False
    raise InvalidAnswer((t or _default_t())("quiz.invalid.truefalse"))


@dataclass(frozen=True, slots=True)
class GradedAnswer:
    question: QuizQuestion
    given: str
    correct: bool


def grade_answer(question: QuizQuestion, text: str, t: Translator | None = None) -> GradedAnswer:
    """Grade ``text`` against ``question``; raises :class:`InvalidAnswer` if unparseable."""
    t = t or _default_t()
    kind = question.type
    if kind == "single":
        chosen = parse_choice_indexes(text, len(question.choices), t)
        if len(chosen) != 1:
            raise InvalidAnswer(t("quiz.invalid.one_number"))
        correct = chosen == question.correct_indexes
        given = str(next(iter(chosen)) + 1)
    elif kind == "multiple":
        chosen = parse_choice_indexes(text, len(question.choices), t)
        correct = chosen == question.correct_indexes
        given = ",".join(str(i + 1) for i in sorted(chosen))
    elif kind == "truefalse":
        value = parse_truefalse(text, t)
        correct = value is question.answer
        given = "O" if value else "X"
    else:  # short
        given = text.strip()
        if not given:
            raise InvalidAnswer(t("quiz.invalid.need_answer"))
        accepted = {normalize_short(a) for a in question.accepted_short}
        correct = normalize_short(given) in accepted
    return GradedAnswer(question, given, correct)


@dataclass(slots=True)
class QuizResult:
    lesson_id: str
    activity_ids: list[str]
    started_at: datetime
    finished_at: datetime
    graded: list[GradedAnswer] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.graded)

    @property
    def correct_count(self) -> int:
        return sum(1 for g in self.graded if g.correct)

    @property
    def percent(self) -> int:
        return round(100 * self.correct_count / self.total) if self.total else 0

    @property
    def wrong(self) -> list[GradedAnswer]:
        return [g for g in self.graded if not g.correct]


def format_question(
    question: QuizQuestion, number: int, total: int, t: Translator | None = None
) -> str:
    """Prompt text for one question: ``[2/4] (single choice) ...`` plus numbered choices."""
    t = t or _default_t()
    lines = [
        t(
            "quiz.question",
            number=number,
            total=total,
            kind=t(f"quiz.kind.{question.type}"),
            prompt=question.prompt,
        )
    ]
    lines += [f"  {i + 1}. {choice}" for i, choice in enumerate(question.choices)]
    lines.append(f"> {t(f'quiz.hint.{question.type}')}: ")
    return "\n".join(lines)


def run_quiz(
    lesson: Lesson,
    quiz: LessonQuiz,
    questions: list[QuizQuestion],
    *,
    prompt: Prompt,
    echo: Echo,
    clock: Callable[[], datetime],
    t: Translator | None = None,
) -> QuizResult:
    """Ask ``questions`` in order, grading each immediately. Nothing is persisted here.

    ``prompt`` may raise (EOF, interrupt) to abort; the partial result is then discarded by the
    caller because this function never returns it.
    """
    t = t or _default_t()
    started = clock()
    result = QuizResult(lesson.id, quiz.activity_ids(lesson), started, started)
    for number, question in enumerate(questions, 1):
        text = format_question(question, number, len(questions), t)
        while True:
            try:
                graded = grade_answer(question, prompt(text), t)
                break
            except InvalidAnswer as exc:
                echo(f"  ! {exc}")
                text = "> "
        mark = (
            t("quiz.correct") if graded.correct else t("quiz.wrong", answer=question.answer_text())
        )
        echo(f"  {'✔' if graded.correct else '✘'} {mark}")
        echo(t("quiz.explanation", text=question.explanation))
        echo("")
        result.graded.append(graded)
    result.finished_at = clock()
    echo(
        t(
            "quiz.score",
            correct=result.correct_count,
            total=result.total,
            percent=result.percent,
            wrong=len(result.wrong),
        )
    )
    return result


@dataclass(frozen=True, slots=True)
class RecordedRun:
    run: QuizRun
    new_cards: list[Card]

    @property
    def new_quiz_cards(self) -> int:
        return sum(1 for c in self.new_cards if c.source == "quiz")

    @property
    def new_concept_cards(self) -> int:
        return sum(1 for c in self.new_cards if c.source == "concept")


def card_id(lesson_id: str, source: str, question_id: str) -> str:
    return f"{lesson_id}-{source}-{question_id}"


def quiz_card(lesson: Lesson, question: QuizQuestion, now: datetime, user_id: int) -> Card:
    front = question.prompt
    if question.choices:
        front += "\n" + "\n".join(f"{i + 1}. {c}" for i, c in enumerate(question.choices))
    return Card(
        id=card_id(lesson.id, "quiz", question.id),
        user_id=user_id,
        lesson_id=lesson.id,
        question_id=question.id,
        front=front,
        back=f"{question.answer_text()}\n{question.explanation}",
        source="quiz",
        created_at=now,
    )


def concept_card(lesson: Lesson, question: QuizQuestion, now: datetime, user_id: int) -> Card:
    assert question.concept is not None
    return Card(
        id=card_id(lesson.id, "concept", question.id),
        user_id=user_id,
        lesson_id=lesson.id,
        question_id=question.id,
        front=question.concept.front,
        back=question.concept.back,
        source="concept",
        created_at=now,
    )


def record_quiz_run(
    store: ProgressStore,
    lesson: Lesson,
    result: QuizResult,
    *,
    user_id: int = DEFAULT_USER,
) -> RecordedRun:
    """Persist a finished quiz: run row, one attempt per question, cards, activity done.

    Wrong answers become ``source=quiz`` cards and questions with ``concept`` become
    ``source=concept`` cards; an existing card (same id) is left untouched, so answering the
    same question wrong twice never duplicates it (AC-4.3). Every quiz activity the asked
    questions belong to is marked ``done`` regardless of score (AC-4.2).
    """
    now = result.finished_at
    today = now.astimezone().date()
    new_cards: list[Card] = []
    with store.transaction():
        run = store.add_quiz_run(
            QuizRun(
                user_id=user_id,
                lesson_id=lesson.id,
                activity_id=result.activity_ids[0] if result.activity_ids else None,
                started_at=result.started_at,
                finished_at=now,
                correct=result.correct_count,
                total=result.total,
            )
        )
        for graded in result.graded:
            store.add_quiz_attempt(
                QuizAttempt(
                    user_id=user_id,
                    lesson_id=lesson.id,
                    question_id=graded.question.id,
                    answered_at=now,
                    answer=graded.given,
                    correct=graded.correct,
                )
            )
            wanted: list[Card] = []
            if not graded.correct:
                wanted.append(quiz_card(lesson, graded.question, now, user_id))
            if graded.question.concept is not None:
                wanted.append(concept_card(lesson, graded.question, now, user_id))
            for card in wanted:
                if store.get_card(card.id, user_id) is not None:
                    continue
                store.save_card(card)
                fresh = Sm2State.new(today)
                store.save_card_state(
                    CardState(
                        card_id=card.id,
                        user_id=user_id,
                        repetitions=fresh.repetitions,
                        interval_days=fresh.interval_days,
                        ease=fresh.ease,
                        due=fresh.due,
                    )
                )
                new_cards.append(card)
        for activity_id in result.activity_ids:
            store.save_activity(
                ActivityProgress(
                    user_id=user_id,
                    activity_id=activity_id,
                    lesson_id=lesson.id,
                    status=LessonStatus.DONE,
                    updated_at=now,
                )
            )
    return RecordedRun(run, new_cards)


def select_questions(
    quiz: LessonQuiz,
    *,
    only: list[str] | None = None,
    retry_wrong: bool = False,
    store: ProgressStore | None = None,
    user_id: int = DEFAULT_USER,
) -> list[QuizQuestion]:
    """Questions to ask: all, ``--only`` ids (in quiz order), or those last answered wrong.

    Raises ``ValueError`` naming unknown ``--only`` ids.
    """
    questions = quiz.questions
    if only:
        known = {q.id for q in questions}
        unknown = [qid for qid in only if qid not in known]
        if unknown:
            raise ValueError(f"unknown question id(s): {', '.join(unknown)}")
        questions = [q for q in questions if q.id in set(only)]
    if retry_wrong and store is not None:
        latest: dict[str, bool] = {}
        for attempt in store.list_quiz_attempts(user_id, quiz.lesson_id):
            latest[attempt.question_id] = attempt.correct  # attempts are in id order
        questions = [q for q in questions if latest.get(q.id) is False]
    return questions


def quiz_activity_of(quiz: LessonQuiz, lesson: Lesson) -> str | None:
    """First quiz activity the lesson's blocks record against (for display)."""
    for block in quiz.blocks:
        activity = resolve_activity(block, lesson)
        if activity is not None:
            return activity
    return None

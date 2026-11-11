"""Non-interactive quiz and review operations for callers that are not a terminal.

The ``rc`` commands drive a dialogue (ask, grade, print, ask again); an HTTP endpoint gets a
whole submission at once and must never leak answers before the learner has answered. This
module is that second shape: plain values in, plain values out, no prompting and no printing,
so the API routers (P2-1) call these instead of re-implementing the rules.

Everything here is either pure or performs exactly one store transaction.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime

from robotics_curriculum.content import Lesson, LessonQuiz, QuizQuestion, parse_quiz
from robotics_curriculum.learn.quiz import (
    GradedAnswer,
    InvalidAnswer,
    QuizResult,
    RecordedRun,
    grade_answer,
    record_quiz_run,
)
from robotics_curriculum.learn.review import DueCard, apply_rating, due_cards, due_on
from robotics_curriculum.learn.sm2 import Rating
from robotics_curriculum.learn.stats import DashboardStats, dashboard
from robotics_curriculum.progress import (
    DEFAULT_USER,
    CardState,
    ProgressError,
    ProgressService,
    ProgressStore,
)


class QuizSubmissionError(ProgressError):
    """A submission names unknown questions, misses some, or cannot be graded."""


@dataclass(frozen=True, slots=True)
class QuestionView:
    """A question as a learner may see it *before* answering: no answer, no explanation."""

    id: str
    type: str
    type_label: str
    prompt: str
    choices: list[str]

    @classmethod
    def of(cls, question: QuizQuestion) -> QuestionView:
        return cls(
            id=question.id,
            type=question.type,
            type_label=question.type_label,
            prompt=question.prompt,
            choices=list(question.choices),
        )


@dataclass(frozen=True, slots=True)
class AnswerFeedback:
    """What the learner gets back per question once the submission is graded."""

    question_id: str
    given: str
    correct: bool
    answer: str
    explanation: str

    @classmethod
    def of(cls, graded: GradedAnswer) -> AnswerFeedback:
        return cls(
            question_id=graded.question.id,
            given=graded.given,
            correct=graded.correct,
            answer=graded.question.answer_text(),
            explanation=graded.question.explanation,
        )


@dataclass(frozen=True, slots=True)
class SubmissionResult:
    """Outcome of one submitted quiz: feedback, score and the cards it created."""

    lesson_id: str
    feedback: list[AnswerFeedback]
    correct: int
    total: int
    seconds: int
    new_card_ids: list[str]

    @property
    def percent(self) -> int:
        return round(100 * self.correct / self.total) if self.total else 0


@dataclass(frozen=True, slots=True)
class CardView:
    """A due card for the review screen, with its current schedule."""

    card_id: str
    lesson_id: str
    question_id: str
    front: str
    back: str
    source: str
    due: date
    interval_days: int

    @classmethod
    def of(cls, due: DueCard) -> CardView:
        return cls(
            card_id=due.card.id,
            lesson_id=due.card.lesson_id,
            question_id=due.card.question_id,
            front=due.card.front,
            back=due.card.back,
            source=due.card.source,
            due=due.state.due,
            interval_days=due.state.interval_days,
        )


def lesson_quiz(lesson: Lesson) -> LessonQuiz:
    """Parse a lesson's quiz, raising :class:`QuizSubmissionError` when it has none."""
    quiz = parse_quiz(lesson)
    if not quiz.questions:
        raise QuizSubmissionError(f"lesson '{lesson.id}' has no quiz block")
    return quiz


def question_views(quiz: LessonQuiz) -> list[QuestionView]:
    """The quiz without answers or explanations (what a GET endpoint may return)."""
    return [QuestionView.of(q) for q in quiz.questions]


def grade_submission(
    quiz: LessonQuiz,
    answers: Mapping[str, str],
    *,
    started_at: datetime,
    finished_at: datetime,
    lesson: Lesson,
    partial: bool = False,
) -> QuizResult:
    """Grade a whole submission.

    ``answers`` maps question id to the raw answer text, in the same notation the CLI accepts
    (``"2"``, ``"1,3"``, ``"o"``, free text). Unknown ids are rejected; missing ids are too
    unless ``partial`` is set, which grades only what was submitted. Ungradable text raises
    :class:`QuizSubmissionError` naming the question.
    """
    known = {q.id: q for q in quiz.questions}
    unknown = sorted(set(answers) - set(known))
    if unknown:
        raise QuizSubmissionError(f"unknown question id(s): {', '.join(unknown)}")
    asked = [q for q in quiz.questions if q.id in answers]
    if not partial:
        missing = [q.id for q in quiz.questions if q.id not in answers]
        if missing:
            raise QuizSubmissionError(f"missing answer(s) for: {', '.join(missing)}")
    if not asked:
        raise QuizSubmissionError("submission has no answers")
    graded: list[GradedAnswer] = []
    for question in asked:
        try:
            graded.append(grade_answer(question, answers[question.id]))
        except InvalidAnswer as exc:
            raise QuizSubmissionError(f"question '{question.id}': {exc}") from None
    result = QuizResult(lesson.id, quiz.activity_ids(lesson), started_at, finished_at)
    result.graded.extend(graded)
    return result


def submit_quiz(
    store: ProgressStore,
    lesson: Lesson,
    answers: Mapping[str, str],
    *,
    started_at: datetime,
    finished_at: datetime,
    user_id: int = DEFAULT_USER,
    partial: bool = False,
) -> SubmissionResult:
    """Grade a submission and record it (run, attempts, cards, activity) in one transaction."""
    quiz = lesson_quiz(lesson)
    result = grade_submission(
        quiz,
        answers,
        started_at=started_at,
        finished_at=finished_at,
        lesson=lesson,
        partial=partial,
    )
    recorded: RecordedRun = record_quiz_run(store, lesson, result, user_id=user_id)
    return SubmissionResult(
        lesson_id=lesson.id,
        feedback=[AnswerFeedback.of(g) for g in result.graded],
        correct=result.correct_count,
        total=result.total,
        seconds=recorded.run.seconds,
        new_card_ids=[c.id for c in recorded.new_cards],
    )


def review_queue(
    store: ProgressStore,
    *,
    today: date,
    user_id: int = DEFAULT_USER,
    lesson_id: str | None = None,
    limit: int | None = None,
) -> list[CardView]:
    """Cards due on or before ``today``, earliest first."""
    return [
        CardView.of(d)
        for d in due_cards(store, today=today, user_id=user_id, lesson_id=lesson_id, limit=limit)
    ]


def rate_card(
    store: ProgressStore,
    card_id: str,
    rating: Rating,
    *,
    now: datetime,
    today: date,
    user_id: int = DEFAULT_USER,
) -> CardState:
    """Apply one review rating (SM-2) and return the card's new schedule."""
    if store.get_card(card_id, user_id) is None:
        raise ProgressError(f"unknown card '{card_id}'")
    return apply_rating(store, card_id, rating, now=now, today=today, user_id=user_id)


def scheduled_on(store: ProgressStore, *, day: date, user_id: int = DEFAULT_USER) -> int:
    """How many cards come up for review exactly on ``day``."""
    return due_on(store, day=day, user_id=user_id)


def dashboard_stats(service: ProgressService, *, now: datetime) -> DashboardStats:
    """The dashboard aggregate (stage progress, week time, streak, due today, accuracy)."""
    return dashboard(service, now=now)

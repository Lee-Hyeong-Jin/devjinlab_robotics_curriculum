"""Quizzes: read a lesson's questions and submit an attempt (PRD FR-4.1, FR-4.2).

The rules live in :mod:`robotics_curriculum.learn.service`; these routes only translate HTTP
to it. Answers and explanations are never part of the ``GET`` response: a learner receives
them in the ``POST`` reply, after answering.

Unlike the terminal flow, one request carries the whole attempt. That keeps the "an
unfinished quiz records nothing" rule (AC-4.2) without an open run row in the database.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from robotics_curriculum.api.deps import (
    ContentIndex,
    Index,
    Progress,
    State,
    get_principal,
    require_verified_email,
)
from robotics_curriculum.api.problems import problem_responses
from robotics_curriculum.api.schemas import (
    QuizPublic,
    QuizQuestionPublic,
    QuizRun,
    QuizSubmission,
)
from robotics_curriculum.content import Lesson, LessonQuiz, QuizParseError
from robotics_curriculum.learn import (
    QuizSubmissionError,
    lesson_quiz,
    question_views,
    submit_quiz,
)

router = APIRouter(
    dependencies=[Depends(get_principal), Depends(require_verified_email)],
    prefix="/api/v1",
    tags=["quiz"],
    responses=problem_responses(403, 404, 409, 422, 503),
)


def _quiz_of(lesson_id: str, index: ContentIndex) -> tuple[Lesson, LessonQuiz]:
    """Parse the lesson's quiz: 404 when it has none, 422 when the block is broken."""
    lesson = index.lesson(lesson_id).lesson
    try:
        return lesson, lesson_quiz(lesson)
    except QuizSubmissionError as exc:
        raise HTTPException(404, str(exc)) from None
    except QuizParseError as exc:
        raise HTTPException(422, f"lesson '{lesson_id}' has an invalid quiz block: {exc}") from None


@router.get("/lessons/{lesson_id}/quiz", response_model=QuizPublic)
def get_lesson_quiz(lesson_id: str, index: Index) -> QuizPublic:
    """A lesson's quiz questions in order, without answers or explanations."""
    lesson, quiz = _quiz_of(lesson_id, index)
    activities = quiz.activity_ids(lesson)
    return QuizPublic(
        lesson_id=lesson.id,
        activity_id=activities[0] if activities else None,
        questions=[QuizQuestionPublic.of(v) for v in question_views(quiz)],
    )


@router.post("/quiz/runs", response_model=QuizRun, status_code=status.HTTP_201_CREATED)
def submit_run(body: QuizSubmission, index: Index, progress: Progress, state: State) -> QuizRun:
    """Grade a whole attempt, store it, and return the feedback and any cards it created.

    Recording is one transaction: the run, one attempt per question, flashcards for wrong
    answers and for questions carrying a ``concept``, and the quiz activity marked done.
    """
    lesson, _ = _quiz_of(body.lesson_id, index)
    finished = state.clock()
    with progress.open() as service:
        try:
            outcome = submit_quiz(
                service.store,
                lesson,
                body.answers,
                started_at=finished,
                finished_at=finished,
                user_id=service.user_id,
                partial=body.partial,
            )
        except QuizSubmissionError as exc:
            raise HTTPException(422, str(exc)) from None
    return QuizRun.of(outcome)

"""Flashcard review: today's queue and rating a card with SM-2 (PRD FR-4.3).

Scheduling lives in :mod:`robotics_curriculum.learn.sm2`; these routes only translate HTTP.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from robotics_curriculum.api.deps import (
    Index,
    Progress,
    State,
    get_principal,
    require_verified_email,
)
from robotics_curriculum.api.problems import problem_responses
from robotics_curriculum.api.schemas import RateRequest, ReviewCard, ReviewResult
from robotics_curriculum.learn import Rating, rate_card, review_queue, scheduled_on
from robotics_curriculum.progress import ProgressError

router = APIRouter(
    dependencies=[Depends(get_principal), Depends(require_verified_email)],
    prefix="/api/v1/review",
    tags=["review"],
    responses=problem_responses(403, 404, 409, 422, 503),
)

LessonFilter = Annotated[str | None, Query(alias="lesson_id", description="Only this lesson.")]
Limit = Annotated[int | None, Query(ge=1, le=100, description="At most this many cards.")]


@router.get("/due", response_model=list[ReviewCard])
def get_due(
    progress: Progress,
    state: State,
    index: Index,
    lesson_id: LessonFilter = None,
    limit: Limit = None,
) -> list[ReviewCard]:
    """Cards due today (earliest due first), optionally limited to one lesson."""
    if lesson_id is not None:
        index.lesson(lesson_id)
    today = state.clock().astimezone().date()
    with progress.open() as service:
        cards = review_queue(
            service.store,
            today=today,
            user_id=service.user_id,
            lesson_id=lesson_id,
            limit=limit,
        )
    return [ReviewCard.of(c) for c in cards]


@router.post("/{card_id}", response_model=ReviewResult)
def rate(card_id: str, body: RateRequest, progress: Progress, state: State) -> ReviewResult:
    """Rate a card (again / hard / good / easy) and get its next review date."""
    now = state.clock()
    today = now.astimezone().date()
    with progress.open() as service:
        try:
            saved = rate_card(
                service.store,
                card_id,
                Rating(body.rating),
                now=now,
                today=today,
                user_id=service.user_id,
            )
        except ProgressError as exc:
            raise HTTPException(404, str(exc)) from None
        tomorrow = scheduled_on(
            service.store, day=today + timedelta(days=1), user_id=service.user_id
        )
    return ReviewResult.of(saved, tomorrow)

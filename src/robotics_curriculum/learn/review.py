"""Flashcard review with SM-2 (PRD FR-4.3; appendix C.1 AC-4.4): ``rc review``.

:func:`due_cards` picks what to show, :func:`apply_rating` persists one answer (state +
append-only review log), and :func:`run_review` drives a terminal session through injected
``prompt`` / ``echo`` callables. Cards rated *again* are shown once more at the end of the
session (at most ``MAX_REQUEUE`` times) without touching their SM-2 state again.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from robotics_curriculum.learn.sm2 import Rating, Sm2State, parse_rating, schedule
from robotics_curriculum.progress import (
    DEFAULT_USER,
    Card,
    CardState,
    ProgressStore,
    QuizAttempt,
    Review,
)

Prompt = Callable[[str], str]
Echo = Callable[[str], None]

MAX_REQUEUE = 2
RATING_MENU = "1 again · 2 hard · 3 good · 4 easy"


@dataclass(frozen=True, slots=True)
class DueCard:
    card: Card
    state: CardState


def _states_by_card(store: ProgressStore, user_id: int) -> dict[str, CardState]:
    return {s.card_id: s for s in store.list_card_states(user_id)}


def due_cards(
    store: ProgressStore,
    *,
    today: date,
    user_id: int = DEFAULT_USER,
    lesson_id: str | None = None,
    limit: int | None = None,
) -> list[DueCard]:
    """Unsuspended cards with ``due <= today``, earliest due first (ties by card id)."""
    states = _states_by_card(store, user_id)
    found: list[DueCard] = []
    for card in store.list_cards(user_id, lesson_id):
        state = states.get(card.id)
        if card.suspended or state is None or state.due > today:
            continue
        found.append(DueCard(card, state))
    found.sort(key=lambda d: (d.state.due, d.card.id))
    return found if limit is None else found[:limit]


def due_count(store: ProgressStore, *, today: date, user_id: int = DEFAULT_USER) -> int:
    return len(due_cards(store, today=today, user_id=user_id))


def due_on(store: ProgressStore, *, day: date, user_id: int = DEFAULT_USER) -> int:
    """Cards whose next review falls exactly on ``day`` (used for "내일 예정")."""
    suspended = {c.id for c in store.list_cards(user_id) if c.suspended}
    return sum(
        1 for s in store.list_card_states(user_id) if s.due == day and s.card_id not in suspended
    )


def apply_rating(
    store: ProgressStore,
    card_id: str,
    rating: Rating,
    *,
    now: datetime,
    today: date,
    user_id: int = DEFAULT_USER,
) -> CardState:
    """Schedule the card with SM-2, save the new state and append a review row."""
    with store.transaction():
        current = store.get_card_state(card_id, user_id)
        before = (
            Sm2State.new(today)
            if current is None
            else Sm2State(current.repetitions, current.interval_days, current.ease, current.due)
        )
        after = schedule(before, rating, today)
        state = CardState(
            card_id=card_id,
            user_id=user_id,
            repetitions=after.repetitions,
            interval_days=after.interval_days,
            ease=after.ease,
            due=after.due,
        )
        store.save_card_state(state)
        store.add_review(
            Review(
                card_id=card_id,
                user_id=user_id,
                reviewed_at=now,
                rating=rating.value,
                interval_before=before.interval_days,
                interval_after=after.interval_days,
                ease_after=after.ease,
            )
        )
    return state


@dataclass(slots=True)
class ReviewSummary:
    reviewed: int = 0
    counts: dict[Rating, int] = field(default_factory=lambda: dict.fromkeys(Rating, 0))
    requeued: int = 0
    due_tomorrow: int = 0

    def line(self) -> str:
        parts = " · ".join(f"{r.value} {self.counts[r]}" for r in Rating)
        return f"완료 {self.reviewed}장  {parts}   내일 예정 {self.due_tomorrow}장"


def _ask_rating(prompt: Prompt, echo: Echo) -> Rating:
    while True:
        rating = parse_rating(prompt(f"> {RATING_MENU}: "))
        if rating is not None:
            return rating
        echo("  ! 1-4 또는 again/hard/good/easy 로 답하세요")


def run_review(
    store: ProgressStore,
    cards: list[DueCard],
    *,
    prompt: Prompt,
    echo: Echo,
    now: datetime,
    today: date,
    user_id: int = DEFAULT_USER,
) -> ReviewSummary:
    """Show each due card (front, Enter, back, rating) and persist every first answer.

    A card answered *again* is queued once more at the end (up to ``MAX_REQUEUE`` passes);
    those extra showings are practice only and are not scheduled or logged.
    """
    summary = ReviewSummary()
    queue: list[tuple[DueCard, int]] = [(d, 0) for d in cards]
    total = len(cards)
    shown = 0
    while queue:
        due, pass_no = queue.pop(0)
        shown += 1
        label = f"[{shown}/{total}]" if pass_no == 0 else f"[다시 {pass_no}/{MAX_REQUEUE}]"
        prompt(f"{label} {due.card.front}\n  ({due.card.lesson_id})\n> Enter 로 뒷면 보기 ")
        echo(f"  답: {due.card.back}")
        rating = _ask_rating(prompt, echo)
        if pass_no == 0:
            state = apply_rating(store, due.card.id, rating, now=now, today=today, user_id=user_id)
            summary.reviewed += 1
            summary.counts[rating] += 1
            echo(f"  다음 복습: {state.due:%Y-%m-%d} ({state.interval_days}일 뒤)")
        if rating is Rating.AGAIN and pass_no < MAX_REQUEUE:
            queue.append((due, pass_no + 1))
            if pass_no == 0:
                summary.requeued += 1
        echo("")
    summary.due_tomorrow = due_on(store, day=today + timedelta(days=1), user_id=user_id)
    echo(summary.line())
    return summary


def recent_accuracy(attempts: list[QuizAttempt], *, since: datetime) -> tuple[int, int] | None:
    """``(correct, total)`` of attempts answered at or after ``since``; ``None`` if none."""
    recent = [a for a in attempts if a.answered_at >= since]
    if not recent:
        return None
    return sum(1 for a in recent if a.correct), len(recent)

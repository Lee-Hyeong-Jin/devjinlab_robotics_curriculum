"""SM-2 spaced-repetition scheduling (PRD FR-4.3, decision 2; ADR 0005).

Pure functions only: no I/O, no clock. ``schedule`` maps a card's current state and the
learner's rating to the next state. Ratings map to SM-2 quality ``q`` as
again=1, hard=3, good=4, easy=5::

    if q < 3: repetitions = 0; interval = 1
    else:
        repetitions += 1
        interval = 1 if repetitions == 1 else 6 if repetitions == 2 else round(interval * ease)
    ease = max(1.3, ease + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))
    due = today + interval days
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, timedelta
from enum import StrEnum

DEFAULT_EASE = 2.5
MIN_EASE = 1.3


class Rating(StrEnum):
    AGAIN = "again"
    HARD = "hard"
    GOOD = "good"
    EASY = "easy"

    @property
    def quality(self) -> int:
        return QUALITY[self]


QUALITY: dict[Rating, int] = {Rating.AGAIN: 1, Rating.HARD: 3, Rating.GOOD: 4, Rating.EASY: 5}

# Terminal shortcuts for `rc review`: 1 again · 2 hard · 3 good · 4 easy (plus the words).
RATING_KEYS: dict[str, Rating] = {
    "1": Rating.AGAIN,
    "2": Rating.HARD,
    "3": Rating.GOOD,
    "4": Rating.EASY,
    "again": Rating.AGAIN,
    "hard": Rating.HARD,
    "good": Rating.GOOD,
    "easy": Rating.EASY,
    "a": Rating.AGAIN,
    "h": Rating.HARD,
    "g": Rating.GOOD,
    "e": Rating.EASY,
}


@dataclass(frozen=True, slots=True)
class Sm2State:
    """Scheduling state of one card."""

    repetitions: int = 0
    interval_days: int = 0
    ease: float = DEFAULT_EASE
    due: date = date.min

    @classmethod
    def new(cls, today: date) -> Sm2State:
        """State of a freshly created card: due immediately."""
        return cls(due=today)


def parse_rating(text: str) -> Rating | None:
    """``"1"``/``"again"``/``"a"`` -> :attr:`Rating.AGAIN` ...; ``None`` if unrecognised."""
    return RATING_KEYS.get(text.strip().lower())


def next_ease(ease: float, quality: int) -> float:
    """SM-2 ease update with the 1.3 floor, rounded to avoid float drift."""
    updated = ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    return round(max(MIN_EASE, updated), 4)


def schedule(state: Sm2State, rating: Rating, today: date) -> Sm2State:
    """Next state after answering a card with ``rating`` on ``today``."""
    quality = rating.quality
    if quality < 3:
        repetitions, interval = 0, 1
    else:
        repetitions = state.repetitions + 1
        if repetitions == 1:
            interval = 1
        elif repetitions == 2:
            interval = 6
        else:
            interval = max(1, round(state.interval_days * state.ease))
    return replace(
        state,
        repetitions=repetitions,
        interval_days=interval,
        ease=next_ease(state.ease, quality),
        due=today + timedelta(days=interval),
    )

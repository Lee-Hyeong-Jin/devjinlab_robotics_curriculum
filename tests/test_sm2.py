"""SM-2 scheduling (P1-2, FR-4.3, AC-4.4): fixed dates -> expected interval / ease / due."""

from datetime import date, timedelta

import pytest

from robotics_curriculum.learn import Rating, Sm2State, parse_rating, schedule

TODAY = date(2026, 11, 11)


def test_new_card_is_due_today() -> None:
    state = Sm2State.new(TODAY)
    assert (state.repetitions, state.interval_days, state.ease, state.due) == (0, 0, 2.5, TODAY)


@pytest.mark.parametrize(
    ("rating", "interval", "ease"),
    [
        (Rating.AGAIN, 1, 2.5 - 0.54),  # q=1: reset, ease drops
        (Rating.HARD, 1, 2.5 - 0.14),  # q=3
        (Rating.GOOD, 1, 2.5),  # q=4: ease unchanged
        (Rating.EASY, 1, 2.5 + 0.1),  # q=5
    ],
)
def test_first_answer_table(rating: Rating, interval: int, ease: float) -> None:
    nxt = schedule(Sm2State.new(TODAY), rating, TODAY)
    assert nxt.interval_days == interval
    assert nxt.ease == pytest.approx(ease, abs=1e-4)
    assert nxt.due == TODAY + timedelta(days=interval)
    assert nxt.repetitions == (0 if rating is Rating.AGAIN else 1)


def test_each_rating_changes_the_schedule_differently() -> None:
    state = schedule(schedule(Sm2State.new(TODAY), Rating.GOOD, TODAY), Rating.GOOD, TODAY)
    assert state.interval_days == 6  # second success
    third = {rating: schedule(state, rating, TODAY) for rating in Rating}
    # again resets to tomorrow; a success uses the ease *before* this answer (classic SM-2)
    assert third[Rating.AGAIN].due == TODAY + timedelta(days=1)
    assert all(
        third[r].due == TODAY + timedelta(days=15) for r in (Rating.HARD, Rating.GOOD, Rating.EASY)
    )
    assert third[Rating.HARD].ease < third[Rating.GOOD].ease < third[Rating.EASY].ease
    # ... and that ease difference shows up in the following interval
    fourth = {r: schedule(third[r], Rating.GOOD, third[r].due) for r in Rating}
    assert fourth[Rating.AGAIN].due < fourth[Rating.HARD].due < fourth[Rating.GOOD].due
    assert fourth[Rating.GOOD].due < fourth[Rating.EASY].due
    assert [fourth[r].interval_days for r in (Rating.HARD, Rating.GOOD, Rating.EASY)] == [
        35,
        38,
        39,
    ]


def test_good_good_good_sequence_is_1_6_then_interval_times_ease() -> None:
    state = Sm2State.new(TODAY)
    day = TODAY
    expected_intervals = []
    for _ in range(4):
        state = schedule(state, Rating.GOOD, day)
        expected_intervals.append(state.interval_days)
        day = state.due
    # ease stays 2.5 on "good": 1, 6, round(6*2.5)=15, round(15*2.5)=38
    assert expected_intervals == [1, 6, 15, 38]
    assert state.repetitions == 4


def test_again_resets_repetitions_and_interval_but_keeps_lowered_ease() -> None:
    state = Sm2State(repetitions=3, interval_days=15, ease=2.5, due=TODAY)
    nxt = schedule(state, Rating.AGAIN, TODAY)
    assert (nxt.repetitions, nxt.interval_days) == (0, 1)
    assert nxt.ease == pytest.approx(1.96)
    assert nxt.due == TODAY + timedelta(days=1)
    # the next success restarts at 1 day, not at interval * ease
    assert schedule(nxt, Rating.GOOD, nxt.due).interval_days == 1


def test_ease_never_drops_below_1_3() -> None:
    state = Sm2State.new(TODAY)
    for _ in range(10):
        state = schedule(state, Rating.AGAIN, TODAY)
    assert state.ease == 1.3
    # and a hard answer at the floor stays at the floor
    assert schedule(state, Rating.HARD, TODAY).ease == 1.3


def test_interval_is_at_least_one_day() -> None:
    state = Sm2State(repetitions=2, interval_days=0, ease=1.3, due=TODAY)
    assert schedule(state, Rating.GOOD, TODAY).interval_days == 1


@pytest.mark.parametrize(
    ("text", "rating"),
    [("1", Rating.AGAIN), (" 2 ", Rating.HARD), ("good", Rating.GOOD), ("E", Rating.EASY)],
)
def test_parse_rating(text: str, rating: Rating) -> None:
    assert parse_rating(text) is rating


def test_parse_rating_rejects_unknown() -> None:
    assert parse_rating("5") is None
    assert parse_rating("") is None


from data import ROOMS, BATCHES, COURSES
from rules import make_classes, cost
from simulated_annealing import solve


def test_solve_returns_valid_structure():

    classes = make_classes(COURSES)

    timetable = solve(
        classes,
        ROOMS,
        BATCHES,
        iters=100,
        seed=42
    )

    assert len(timetable) == len(classes)

    for entry in timetable:
        day, period, room = entry

        assert 0 <= day < 5
        assert room in ROOMS


def test_same_seed_same_result():

    classes = make_classes(COURSES)

    result1 = solve(
        classes, ROOMS, BATCHES, 100, 42
    )

    result2 = solve(
        classes, ROOMS, BATCHES, 100, 42
    )

    assert result1 == result2


def test_cost_is_nonnegative():

    classes = make_classes(COURSES)

    timetable = solve(
        classes, ROOMS, BATCHES, 100, 42
    )

    assert cost(
        timetable, classes, ROOMS, BATCHES
    ) >= 0

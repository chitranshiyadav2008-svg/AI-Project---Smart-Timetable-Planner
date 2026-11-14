# test_rules.py - one passing and one failing case per rule. Run: pytest test_rules.py
from rules import Class, make_classes, hard_violations, soft_penalty, cost
from data import COURSES

ROOMS = {"L1": (60, "Lecture"), "L2": (60, "Lecture"),
         "Lab1": (60, "Lab"), "SmallLab": (30, "Lab")}
BATCHES = {"A": 55, "B": 28}


def hv(classes, tt):
    return hard_violations(tt, classes, ROOMS, BATCHES)


def day_of_lectures(periods):
    # one lecture per period, batch A, Monday, all different courses/teachers
    classes = [Class(f"C{i}", f"T{i}", "A", 1, "Lecture") for i in range(len(periods))]
    tt = [(0, p, "L1") for p in periods]
    return classes, tt


lec = Class("Math", "T1", "A", 1, "Lecture")
lab = Class("MathLab", "T1", "A", 2, "Lab")


# ---------- hard rules ----------
def test_room_type():
    assert hv([lec], [(0, 0, "L1")]) == 0
    assert hv([lec], [(0, 0, "Lab1")]) == 1


def test_room_size():
    assert hv([lab], [(0, 0, "Lab1")]) == 0
    assert hv([lab], [(0, 0, "SmallLab")]) == 1


def test_ends_by_17():
    assert hv([lab], [(0, 6, "Lab1")]) == 0   # starts 15:00, ends 17:00
    assert hv([lab], [(0, 7, "Lab1")]) == 1   # starts 16:00, ends 18:00


def test_teacher_clash():
    a = Class("Math", "T1", "A", 1, "Lecture")
    b = Class("Phys", "T1", "B", 1, "Lecture")
    assert hv([a, b], [(0, 0, "L1"), (0, 1, "L2")]) == 0
    assert hv([a, b], [(0, 0, "L1"), (0, 0, "L2")]) == 1


def test_batch_clash():
    a = Class("Math", "T1", "A", 1, "Lecture")
    b = Class("Phys", "T2", "A", 1, "Lecture")
    assert hv([a, b], [(0, 0, "L1"), (0, 1, "L2")]) == 0
    assert hv([a, b], [(0, 0, "L1"), (0, 0, "L2")]) == 1


def test_room_clash():
    a = Class("Math", "T1", "A", 1, "Lecture")
    b = Class("Phys", "T2", "B", 1, "Lecture")
    assert hv([a, b], [(0, 0, "L1"), (0, 1, "L1")]) == 0
    assert hv([a, b], [(0, 0, "L1"), (0, 0, "L1")]) == 1


def test_course_max_two_per_day():
    assert hv([lec, lec], [(0, 0, "L1"), (0, 1, "L1")]) == 0
    assert hv([lec, lec, lec], [(0, 0, "L1"), (0, 1, "L1"), (0, 2, "L1")]) == 1


def test_batch_max_six_hours():
    classes, tt = day_of_lectures([0, 1, 2, 3, 4, 5])
    assert hv(classes, tt) == 0
    classes, tt = day_of_lectures([0, 1, 2, 3, 4, 5, 6])
    assert hv(classes, tt) == 1


# ---------- soft rules ----------
def test_gaps():
    classes, tt = day_of_lectures([0, 1])
    assert soft_penalty(tt, classes) == 0
    classes, tt = day_of_lectures([0, 2])
    assert soft_penalty(tt, classes) == 1


def test_four_in_a_row_no_penalty():
    classes, tt = day_of_lectures([0, 1, 2, 3])
    assert soft_penalty(tt, classes) == 0


def test_five_in_a_row_penalty_one():
    classes, tt = day_of_lectures([0, 1, 2, 3, 4])
    assert soft_penalty(tt, classes) == 1


# ---------- cost and data ----------
def test_cost():
    a = Class("Math", "T1", "A", 1, "Lecture")
    b = Class("Phys", "T2", "A", 1, "Lecture")
    # same batch, same hour: 1 clash, no gaps -> 100
    assert cost([(0, 0, "L1"), (0, 0, "L2")], [a, b], ROOMS, BATCHES) == 100


def test_demo_data_loads():
    assert len(make_classes(COURSES)) == 31


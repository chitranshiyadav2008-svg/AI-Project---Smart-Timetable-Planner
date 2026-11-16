from rules import Class, hard_violations, soft_penalty, make_classes

ROOMS = {"L1": (60, "Lecture"), "L2": (60, "Lecture"), "L3": (60, "Lecture")}
BATCHES = {"B": 28}
def hv(classes, tt): return hard_violations(tt, classes, ROOMS, BATCHES)

om  = Class("OM-1", "T1", "B", 1, "Lecture", "Elective")
erg = Class("Erg",  "T2", "B", 1, "Lecture", "Elective")
coa = Class("COA",  "T3", "B", 1, "Lecture", "Elective")
dbms = Class("DBMS", "T4", "B", 1, "Lecture")

def test_electives_may_run_together():
    # three electives, same hour, different rooms and teachers -> no violation
    assert hv([om, erg, coa], [(0, 0, "L1"), (0, 0, "L2"), (0, 0, "L3")]) == 0

def test_electives_still_need_own_room():
    assert hv([om, erg], [(0, 0, "L1"), (0, 0, "L1")]) == 1          # same room = clash

def test_elective_vs_normal_course_still_clashes():
    assert hv([om, dbms], [(0, 0, "L1"), (0, 0, "L2")]) == 1          # batch double-booked

def test_parallel_electives_count_once_for_daily_load():
    # 3 electives in parallel + 5 lectures = 6 hours for a student, not 8
    lec = [Class(f"C{i}", f"T{i}", "B", 1, "Lecture") for i in range(5)]
    tt = [(0, 0, "L1"), (0, 0, "L2"), (0, 0, "L3")] + [(0, p, "L1") for p in range(1, 6)]
    assert hv([om, erg, coa] + lec, tt) == 0

def test_make_classes_accepts_optional_group():
    cl = make_classes([("OM-1", "T1", "B", 2, 1, "Lecture", "Elective"), ("DBMS", "T4", "B", 1, 1, "Lecture")])
    assert [c.group for c in cl] == ["Elective", "Elective", ""]

def test_two_sessions_same_day_back_to_back_ok():
    assert soft_penalty([(0, 0, "L1"), (0, 1, "L1")], [dbms, dbms]) == 0

def test_two_sessions_same_day_apart_penalised():
    # 09:00 and 13:00: gap rule gives 3 empty hours, plus 1 for not being back to back
    assert soft_penalty([(0, 0, "L1"), (0, 4, "L1")], [dbms, dbms]) == 4

def test_two_sessions_different_days_fine():
    assert soft_penalty([(0, 0, "L1"), (1, 0, "L1")], [dbms, dbms]) == 0
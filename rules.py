from collections import Counter, defaultdict, namedtuple

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
PERIODS = [f"{h:02d}:00-{h + 1:02d}:00" for h in range(9, 17)]  # 8 one-hour periods, 09:00-17:00

MAX_PER_DAY = 6   # hard rule: max class-hours per batch per day
SOFT_RUN = 4      # soft rule: more than this many hours in a row is penalised

# One weekly class. hours = 1 (lecture) or 2 (lab). kind = room type needed.
Class = namedtuple("Class", "course teacher batch hours kind")


def make_classes(courses):
    """[(name, teacher, batch, sessions, hours, kind)] -> one Class per weekly session."""
    return [Class(name, teacher, batch, hours, kind)
            for name, teacher, batch, n, hours, kind in courses
            for _ in range(n)]


def hard_violations(tt, classes, rooms, batches):
    """Count broken MUST-rules. 0 means valid.
    tt: list of (day, period, room), same order as classes.
    rooms: {name: (capacity, kind)}; batches: {name: students}."""
    bad = 0
    count = Counter()
    for c, (day, period, room) in zip(classes, tt):
        capacity, kind = rooms[room]
        if kind != c.kind:                          # wrong room type
            bad += 1
        if capacity < batches[c.batch]:             # room too small
            bad += 1
        if period + c.hours > len(PERIODS):         # runs past 17:00
            bad += 1
        count[("course", c.course, day)] += 1       # sessions of a course in a day
        for p in range(period, period + c.hours):   # every hour the class occupies
            count[("teacher", c.teacher, day, p)] += 1
            count[("batch", c.batch, day, p)] += 1
            count[("room", room, day, p)] += 1
            count[("load", c.batch, day)] += 1      # batch class-hours in the day
    for key, n in count.items():
        if key[0] == "load":
            bad += max(0, n - MAX_PER_DAY)
        elif key[0] == "course":
            bad += max(0, n - 2)                    # at most 2 sessions a day
        else:
            bad += n - 1                            # claimed twice = clash
    return bad


def soft_penalty(tt, classes):
    """Count broken preferences: gaps in a batch's day, and runs longer than SOFT_RUN."""
    busy = defaultdict(set)                         # (batch, day) -> busy periods
    for c, (day, period, room) in zip(classes, tt):
        busy[(c.batch, day)].update(range(period, period + c.hours))
    total = 0
    for hours in busy.values():
        ordered = sorted(hours)
        total += (ordered[-1] - ordered[0] + 1) - len(ordered)   # empty hours between classes
        run = 1
        for a, b in zip(ordered, ordered[1:]):
            if b == a + 1:
                run += 1
            else:
                total += max(0, run - SOFT_RUN)
                run = 1
        total += max(0, run - SOFT_RUN)             # last stretch
    return total


def cost(tt, classes, rooms, batches):
    """One number: 100 x hard violations + soft penalty. 0 is perfect."""
    return 100 * hard_violations(tt, classes, rooms, batches) + soft_penalty(tt, classes)


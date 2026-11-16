from collections import Counter, defaultdict, namedtuple

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
PERIODS = [f"{h:02d}:00-{h + 1:02d}:00" for h in range(9, 17)]  # 8 one-hour periods, 09:00-17:00

MAX_PER_DAY = 6   # hard rule: max class-hours per batch per day
SOFT_RUN = 4      # soft rule: more than this many hours in a row is penalised

# One weekly class. hours = 1 (lecture) or 2 (lab). kind = room type needed.
# group = elective group name, or "" for a normal course. Courses in the same group run
# in parallel: a student attends only ONE of them, so they share the batch's time slot.
Class = namedtuple("Class", "course teacher batch hours kind group", defaults=[""])


def make_classes(courses):
    """[(name, teacher, batch, sessions, hours, kind[, group])] -> one Class per weekly session."""
    classes = []
    for row in courses:
        name, teacher, batch, n, hours, kind = row[:6]
        group = row[6] if len(row) > 6 and row[6] else ""
        classes += [Class(name, teacher, batch, hours, kind, group) for _ in range(n)]
    return classes


def slot_key(c):
    """What occupies the BATCH's time: the course itself, or its elective group."""
    return c.group or c.course


def hard_violations(tt, classes, rooms, batches):
    """Count broken MUST-rules. 0 means valid.
    tt: list of (day, period, room), same order as classes.
    rooms: {name: (capacity, kind)}; batches: {name: students}."""
    bad = 0
    count = Counter()
    seen = set()                                    # (batch, slot_key, day, period) already counted
    for c, (day, period, room) in zip(classes, tt):
        capacity, kind = rooms[room]
        if kind != c.kind:                          # wrong room type
            bad += 1
        if capacity < batches[c.batch]:             # room too small
            bad += 1
        if period + c.hours > len(PERIODS):         # runs past 17:00
            bad += 1
        for p in range(period, period + c.hours):   # every hour the class occupies
            count[("teacher", c.teacher, day, p)] += 1
            count[("room", room, day, p)] += 1
            # the batch's time: electives of one group at the same hour count ONCE
            key = (c.batch, slot_key(c), day, p)
            if key not in seen:
                seen.add(key)
                count[("batch", c.batch, day, p)] += 1
                count[("load", c.batch, day)] += 1  # batch class-hours in the day
        # sessions of a course (or group) in a day, counted per start
        key = (c.batch, slot_key(c), day, period)
        if ("start",) + key not in seen:
            seen.add(("start",) + key)
            count[("course", c.batch, slot_key(c), day)] += 1
    for key, n in count.items():
        if key[0] == "load":
            bad += max(0, n - MAX_PER_DAY)
        elif key[0] == "course":
            bad += max(0, n - 2)                    # at most 2 sessions a day
        else:
            bad += n - 1                            # claimed twice = clash
    return bad


def soft_penalty(tt, classes):
    """Count broken preferences: gaps in a batch's day, runs longer than SOFT_RUN,
    and two sessions of one course on the same day that are not back to back."""
    busy = defaultdict(set)                         # (batch, day) -> busy periods
    starts = defaultdict(list)                      # (batch, course/group, day) -> [(period, hours)]
    for c, (day, period, room) in zip(classes, tt):
        busy[(c.batch, day)].update(range(period, period + c.hours))
        starts[(c.batch, slot_key(c), day)].append((period, c.hours))
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
    for sessions in starts.values():                # same course twice in a day -> must touch
        distinct = sorted(set(sessions))
        for (p1, h1), (p2, h2) in zip(distinct, distinct[1:]):
            if p1 + h1 != p2:                       # a gap between the two sessions
                total += 1
    return total


def cost(tt, classes, rooms, batches):
    """One number: 100 x hard violations + soft penalty. 0 is perfect."""
    return 100 * hard_violations(tt, classes, rooms, batches) + soft_penalty(tt, classes)
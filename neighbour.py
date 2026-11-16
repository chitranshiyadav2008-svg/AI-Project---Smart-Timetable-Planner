import random

DAYS = 5
PERIODS_PER_DAY = 8


def suitable_rooms(cls, rooms, batches):
    """Rooms of the right type that are big enough for the class's batch."""
    return [
        room_name
        for room_name, (capacity, room_type) in rooms.items()
        if room_type == cls.kind
        and capacity >= batches[cls.batch]
    ]


def generate_neighbor(timetable, classes, rooms, batches, rng):

    new_timetable = timetable.copy()

    # Select one random class
    index = rng.randrange(len(classes))
    cls = classes[index]

    # Select a new day and a valid period for it
    day = rng.randint(0, DAYS - 1)
    period = rng.choice(range(PERIODS_PER_DAY - cls.hours + 1))

    if cls.group:
        # ELECTIVE: move the whole parallel block together. The block is the n-th session of
        # every course in this group (n = which session of its course this class is).
        # The moved courses all land on the same day and period, each in a different room.
        n = sum(1 for c in classes[:index] if c.course == cls.course)
        members = []
        for j, c in enumerate(classes):
            if c.batch == cls.batch and c.group == cls.group:
                if sum(1 for d in classes[:j] if d.course == c.course) == n:
                    members.append(j)
        free_rooms = suitable_rooms(cls, rooms, batches)
        rng.shuffle(free_rooms)
        for k, j in enumerate(members):
            room = free_rooms[k % len(free_rooms)]    # a different room for each course (if enough)
            new_timetable[j] = (day, period, room)
    else:
        room = rng.choice(suitable_rooms(cls, rooms, batches))
        new_timetable[index] = (day, period, room)

    return new_timetable
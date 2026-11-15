
import random

DAYS = 5
PERIODS_PER_DAY = 8


def generate_neighbor(timetable, classes, rooms, batches, rng):

    new_timetable = timetable.copy()

    # Select one random class
    index = rng.randrange(len(classes))
    cls = classes[index]

    # Find suitable rooms
    suitable_rooms = [
        room_name
        for room_name, (capacity, room_type) in rooms.items()
        if room_type == cls.kind
        and capacity >= batches[cls.batch]
    ]

    # Select a new day
    day = rng.randint(0, DAYS - 1)

    # Select a valid period
    valid_periods = list(
        range(PERIODS_PER_DAY - cls.hours + 1)
    )

    period = rng.choice(valid_periods)

    # Select a suitable room
    room = rng.choice(suitable_rooms)

    # Replace the selected assignment
    new_timetable[index] = (day, period, room)

    return new_timetable

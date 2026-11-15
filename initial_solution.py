
import random

DAYS = 5
PERIODS_PER_DAY = 8


def generate_initial_solution(classes, rooms, batches, rng):
    """
    Generate a random initial timetable.

    Each entry:
    (day, period, room)
    """

    timetable = []

    for cls in classes:

        # Find rooms matching class type and batch capacity
        suitable_rooms = [
            room_name
            for room_name, (capacity, room_type) in rooms.items()
            if room_type == cls.kind
            and capacity >= batches[cls.batch]
        ]

        if not suitable_rooms:
            raise ValueError(
                f"No suitable room for {cls.course}"
            )

        # Select random day
        day = rng.randint(0, DAYS - 1)

        # Select valid starting period
        valid_periods = list(
            range(PERIODS_PER_DAY - cls.hours + 1)
        )

        period = rng.choice(valid_periods)

        # Select suitable room
        room = rng.choice(suitable_rooms)

        timetable.append((day, period, room))

    return timetable

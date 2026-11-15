
import random
import math

from rules import cost
from initial_solution import generate_initial_solution
from neighbour import generate_neighbor


def solve(classes, rooms, batches, iters, seed):

    # Create random generator
    rng = random.Random(seed)

    # Step 1: Generate initial timetable
    current = generate_initial_solution(
        classes, rooms, batches, rng
    )

    # Step 2: Calculate initial cost
    current_cost = cost(
        current, classes, rooms, batches
    )

    # Step 3: Store best timetable
    best = current.copy()
    best_cost = current_cost

    # Step 4: Set initial temperature
    temperature = 100.0

    # Step 5: Set cooling rate
    cooling_rate = 0.995

    # Step 6: Repeat optimization
    for iteration in range(iters):

        # Stop if perfect timetable found
        if best_cost == 0:
            break

        # Generate neighboring timetable
        candidate = generate_neighbor(
            current, classes, rooms, batches, rng
        )

        # Calculate candidate cost
        candidate_cost = cost(
            candidate, classes, rooms, batches
        )

        # Calculate cost difference
        delta = candidate_cost - current_cost

        # Step 7: Decide whether to accept
        if delta <= 0:
            accept = True

        else:
            probability = math.exp(
                -delta / temperature
            )

            accept = rng.random() < probability

        # Step 8: Update current solution
        if accept:
            current = candidate
            current_cost = candidate_cost

        # Step 9: Update best solution
        if current_cost < best_cost:
            best = current.copy()
            best_cost = current_cost

        # Step 10: Reduce temperature
        temperature *= cooling_rate

        temperature = max(temperature, 0.0001)

    return best

import random
import math

from rules import cost
from initial_solution import generate_initial_solution
from neighbour import generate_neighbor


def solve(classes, rooms, batches, iters, seed):

    rng = random.Random(seed)

    current = generate_initial_solution( classes, rooms, batches, rng)

    current_cost = cost(current, classes, rooms, batches)
    best = current.copy()
    best_cost = current_cost
    history = [best_cost]
    temperature = 100.0
    cooling_rate = 0.995

    for iteration in range(iters):

        if best_cost == 0:
            break

        candidate = generate_neighbor(current, classes, rooms, batches, rng)
        candidate_cost = cost( candidate, classes, rooms, batches)

        delta = candidate_cost - current_cost

        if delta <= 0:
            accept = True

        else:
            probability = math.exp( -delta / temperature)
            accept = rng.random() < probability

        if accept:
            current = candidate
            current_cost = candidate_cost

        if current_cost < best_cost:
            best = current.copy()
            best_cost = current_cost

        if iteration % 100 == 0:
            history.append(best_cost)

        temperature *= cooling_rate
        temperature = max(temperature, 0.0001)

    history.append(best_cost) 
    return best, history 
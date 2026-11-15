
from data import ROOMS, BATCHES, COURSES
from rules import make_classes, cost, hard_violations, soft_penalty
from simulated_annealing import solve

# Convert course data into individual weekly classes
classes = make_classes(COURSES)

# Run the simulated annealing algorithm
best_timetable = solve(
    classes,
    ROOMS,
    BATCHES,
    iters=10000,
    seed=42
)

# Display the generated timetable
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

print("\n========== GENERATED TIMETABLE ==========\n")

for cls, (day, period, room) in zip(classes, best_timetable):
    start_time = 9 + period
    end_time = start_time + cls.hours

    print(
        f"{cls.course:15} | "
        f"{DAYS[day]:10} | "
        f"{start_time:02d}:00-{end_time:02d}:00 | "
        f"{room}"
    )

# Display final scores
print("\n========== FINAL RESULTS ==========")
print("Total classes:", len(classes))
print("Hard violations:", hard_violations(
    best_timetable, classes, ROOMS, BATCHES
))
print("Soft penalty:", soft_penalty(best_timetable, classes))
print("Final cost:", cost(best_timetable, classes, ROOMS, BATCHES))

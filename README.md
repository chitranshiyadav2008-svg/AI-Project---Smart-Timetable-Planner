# Smart Timetable Generator

An AI course project that builds a clash-free weekly timetable for a university department. You enter the rooms, batches and courses on a web page; a simulated-annealing search assigns every class a day, a start time and a room.

The timetable runs Monday to Friday, 09:00 to 17:00, in one-hour periods. Lectures are one hour; labs are two-hour blocks in lab rooms.

## Running it

```
pip install -r requirements.txt
streamlit run app.py
```

Then open the address Streamlit prints (usually http://localhost:8501). Edit the three tables, press **Generate timetable**, and switch between batches to see each one's week. The timetable can be downloaded as a CSV.

To run the tests:

```
python -m pytest
```

## How it works

A timetable is a list with one `(day, start period, room)` entry per class. The search starts from a random timetable and repeatedly moves one class to a new slot. A move that makes the timetable better is always kept; a move that makes it worse is kept with a probability that shrinks as the search goes on (the "temperature" falls). This lets the search escape local minima early and settle on a good timetable late.

Every timetable gets a cost: **100 × hard violations + soft penalty**. A cost of 0 is a perfect timetable. Because a clash costs 100 times more than a preference, the search removes clashes first and tidies the rest afterwards.

### Hard rules (must hold)

- A lecture is in a lecture room and a lab is in a lab room.
- The room is big enough for the batch.
- Every class finishes by 17:00.
- No teacher, batch or room is in two places in the same hour.
- A course has at most 2 sessions on one day.
- A batch has at most 6 class-hours on one day.

### Soft rules (preferred)

- No empty hours between a batch's first and last class of the day.
- No more than 4 class-hours in a row without a break.
- If a course has two sessions on one day, they are back to back.

### Elective groups

Courses with the same **Group** name (for example COA, OM-1 and ErgDesign) are alternatives: a student takes one of them. They are scheduled in parallel, in the same time slot but different rooms, and they count once towards a student's hours. All courses in a group must have the same number of sessions per week and the same length.

## Files

| File | What it holds |
| --- | --- |
| `app.py` | The Streamlit web page: input tables, the Generate button, the timetable grid, the cost chart and the CSV download. |
| `rules.py` | The timetable model (`Class`, `make_classes`), the hard and soft rules, and the cost function. |
| `data.py` | Demo data. Subjects, teachers and rooms come from a real college timetable; room capacities and batch sizes are invented. |
| `simulated_annealing.py` | The search: `solve(classes, rooms, batches, iters, seed)` returns the best timetable and a history of the best cost. |
| `initial_solution.py` | Builds the random starting timetable. |
| `neighbour.py` | Makes one move: relocates a class, or a whole elective group together. |
| `main.py` | Runs the search from the command line and prints the result. |
| `test_rules.py`, `test_new_rules.py`, `test_simulated_annealing.py` | Tests: one passing and one failing case per rule, plus checks on the search. |

## Scope: how big a problem it handles

The project is designed for **one department**: a few batches, a shared pool of rooms and teachers, and one week that repeats. It is not a university-wide scheduler.

Measured on randomly generated departments (each batch: five 3-session lecture courses and two 2-hour labs; 20,000 search steps; five runs each, on a laptop-class machine):

| Batches | Lecture rooms | Classes per week | Clash-free runs | Avg soft penalty | Time per run |
| --- | --- | --- | --- | --- | --- |
| 2 | 1 | 34 | 5 / 5 | 0.0 | 0.9 s |
| 4 | 2 | 68 | 5 / 5 | 0.8 | 5.5 s |
| 8 | 4 | 136 | 5 / 5 | 5.8 | 10.6 s |
| 12 | 6 | 204 | 5 / 5 | 15.6 | 16 s |
| 16 | 8 | 272 | 5 / 5 | 25.8 | 23 s |

What this means in practice:

- **Up to about 4 batches** (the size of the demo and of a typical department year group) the result is clash-free and almost perfect within a few seconds.
- **Up to about 8 batches** it is still clash-free, but some gaps and long days remain, and a run takes around 10 seconds.
- **Beyond that**, timetables stay valid but the preference penalty grows, and runs take 15 to 25 seconds. More search steps improve quality at the cost of time. The limit is the search time and the quality of preferences, not a hard cap in the code.

The room and teacher supply matters as much as the batch count. If the rooms or teachers are too few for the classes, no valid timetable exists and the page reports the remaining clashes.

## Limitations

- **Clashes are penalised, not forbidden.** The search almost always finds a clash-free timetable, but it cannot guarantee one. If the input is too tight, the page shows how many clashes remain.
- **No teacher availability.** Teachers are assumed free all week, and there is no cap on a teacher's hours per day.
- **No lunch break rule.** Classes can occupy any hour from 09:00 to 17:00.
- **Soft rules are preferences.** A long day or a split session is discouraged, not impossible.
- **Elective groups move as a block.** Every course in a group must have the same session count and length. A group with uneven sessions is rejected on the page.
- **Results depend on the seed.** Different seeds give different, equally valid timetables. The same seed always reproduces the same result.

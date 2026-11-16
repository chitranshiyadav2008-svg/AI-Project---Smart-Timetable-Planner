# data.py - demo data. Subjects, teachers and room names come from the college timetable.
# Room capacities and batch sizes are INVENTED for the demo.

# room name: (capacity, type)
ROOMS = {
    "LH-3":            (60, "Lecture"),
    "410 IT Block":    (60, "Lecture"),
    "Seminar Hall":    (60, "Lecture"),
    "Computer Center": (60, "Lab"),
    "CoE-AI Lab":      (30, "Lab"),
}

# batch name: number of students
BATCHES = {"Batch A": 55, "Batch B": 28}

# (course, teacher, batch, sessions per week, hours per session, room type, elective group)
# Elective group: courses with the same group name run in PARALLEL (a student picks one).
# Leave it "" for a normal course.
COURSES = [
    # Batch A
    ("AI ",        "Dr. Dipty Tripathi",  "Batch A", 3, 1, "Lecture", ""),
    ("DBMS ",      "Prof. Poonam Bansal", "Batch A", 3, 1, "Lecture", ""),
    ("DisM ",      "Ms. Deepika",         "Batch A", 3, 1, "Lecture", ""),
    ("OOPS ",      "Mr. Rohan Bajaj",     "Batch A", 3, 1, "Lecture", ""),
    ("AI Lab ",    "Dr. Dipty Tripathi",  "Batch A", 1, 2, "Lab",     ""),
    ("DBMS Lab ",  "Prof. Poonam Bansal", "Batch A", 1, 2, "Lab",     ""),
    ("OOPS Lab ",  "Mr. Rohan Bajaj",     "Batch A", 1, 2, "Lab",     ""),
    # Batch B
    ("DisM ",      "Ms. Deepika",         "Batch B", 3, 1, "Lecture", ""),
    ("DBMS ",      "Prof. Poonam Bansal", "Batch B", 3, 1, "Lecture", ""),
    ("COA ",       "Ms. Shipra Rani",     "Batch B", 3, 1, "Lecture", "Elective"),
    ("OM-1 ",      "Mr. Dinesh Kumar",    "Batch B", 3, 1, "Lecture", "Elective"),
    ("ErgDesign ", "Dr. Pooja Bhati",     "Batch B", 3, 1, "Lecture", "Elective"),
    ("COA Lab)",   "Ms. Shipra Rani",     "Batch B", 1, 2, "Lab",     ""),
    ("DBMS Lab ",  "Prof. Poonam Bansal", "Batch B", 1, 2, "Lab",     ""),
]
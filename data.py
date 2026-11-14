# data.py - demo data. Subjects, teachers and room names come from the college timetable.
# Room capacities and batch sizes are INVENTED for the demo.

# room name: (capacity, type)
ROOMS = {
    "LH-3":            (60, "Lecture"),
    "Computer Center": (60, "Lab"),
    "CoE-AI Lab":      (30, "Lab"),
}

# batch name: number of students
BATCHES = {"Batch A": 55, "Batch B": 28}

# (course, teacher, batch, sessions per week, hours per session, room type)
COURSES = [
    # Batch A
    ("AI (A)",        "Dr. Dipty Tripathi",  "Batch A", 3, 1, "Lecture"),
    ("DBMS (A)",      "Prof. Poonam Bansal", "Batch A", 3, 1, "Lecture"),
    ("DisM (A)",      "Ms. Deepika",         "Batch A", 3, 1, "Lecture"),
    ("OOPS (A)",      "Mr. Rohan Bajaj",     "Batch A", 3, 1, "Lecture"),
    ("AI Lab (A)",    "Dr. Dipty Tripathi",  "Batch A", 1, 2, "Lab"),
    ("DBMS Lab (A)",  "Prof. Poonam Bansal", "Batch A", 1, 2, "Lab"),
    ("OOPS Lab (A)",  "Mr. Rohan Bajaj",     "Batch A", 1, 2, "Lab"),
    # Batch B
    ("DisM (B)",      "Ms. Deepika",         "Batch B", 3, 1, "Lecture"),
    ("DBMS (B)",      "Prof. Poonam Bansal", "Batch B", 3, 1, "Lecture"),
    ("COA (B)",       "Ms. Shipra Rani",     "Batch B", 3, 1, "Lecture"),
    ("OM-1 (B)",      "Mr. Dinesh Kumar",    "Batch B", 3, 1, "Lecture"),
    ("ErgDesign (B)", "Dr. Pooja Bhati",     "Batch B", 2, 1, "Lecture"),
    ("COA Lab (B)",   "Ms. Shipra Rani",     "Batch B", 1, 2, "Lab"),
    ("DBMS Lab (B)",  "Prof. Poonam Bansal", "Batch B", 1, 2, "Lab"),
]


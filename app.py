import html

import pandas as pd
import streamlit as st

from data import BATCHES, COURSES, ROOMS
from rules import DAYS, PERIODS, hard_violations, make_classes, soft_penalty
from simulated_annealing import solve

# 1. Page settings: must be the FIRST Streamlit call in the file
st.set_page_config(page_title="Smart Timetable", page_icon="🗓️", layout="wide")

# 2. Custom styling (CSS) injected into the page
st.markdown("""
<style>
[data-testid="stMainBlockContainer"] { padding-top: 4.5rem; max-width: 1250px; }
[data-testid="stAppDeployButton"] { display: none; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

.hero {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    border-radius: 18px;
    padding: 28px 34px;
    margin-bottom: 1.2rem;
    box-shadow: 0 8px 24px rgba(79, 70, 229, 0.25);
}
.hero h1 { color: white; margin: 0; font-size: 2.1rem; font-weight: 700; }
.stat {
    background: white; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 16px 20px; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
}
.stat .num { font-size: 1.9rem; font-weight: 700; color: #4F46E5; line-height: 1.1; }
.stat .lab { font-size: 0.85rem; color: #64748B; margin-top: 2px; }

.panel { background: white; border: 1px solid #E2E8F0; border-radius: 16px; padding: 8px 12px 12px 12px;
         box-shadow: 0 2px 10px rgba(15, 23, 42, 0.05); overflow-x: auto; }
.tt td, .tt th { border: none !important; }
.tt tr, .tt tr:nth-child(even) { background: transparent !important; border: none !important; }
.panel table.tt { border-collapse: separate !important; border-spacing: 7px !important; }
.tt td.cls { transition: box-shadow 0.15s; }
.tt td.cls:hover { box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15); }
.tt { width: 100%; border-collapse: separate; border-spacing: 6px; table-layout: fixed; }
.tt th { font-size: 0.72rem; font-weight: 600; color: #64748B; text-align: center; padding: 2px 0; }
.tt .day { width: 56px; font-weight: 700; color: #4F46E5; font-size: 0.95rem; text-align: center; }
.tt td.empty { background: #F1F5F9; border-radius: 10px; height: 68px; }
.tt td.cls { border-radius: 10px; padding: 8px 10px; vertical-align: top; font-size: 0.8rem; line-height: 1.3; }
.tt td.cls b { display: block; font-size: 0.86rem; }
.tt td.cls span { display: block; opacity: 0.8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.chip { display: inline-block; border-radius: 999px; padding: 3px 12px; margin: 0 6px 6px 0; font-size: 0.8rem; }

/* section headings: a numbered circle + title */
.sec { display: flex; align-items: center; gap: 12px; margin: 1.8rem 0 0.9rem 0; }
.sec .n { background: #4F46E5; color: white; border-radius: 50%; width: 30px; height: 30px;
          display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.9rem; }
.sec .t { font-size: 1.2rem; font-weight: 700; color: #0F172A; }

/* cards: icon in the corner, lift on hover */
.stat { position: relative; transition: transform 0.15s, box-shadow 0.15s; }
.stat:hover { transform: translateY(-2px); box-shadow: 0 10px 22px rgba(79, 70, 229, 0.14); }
.stat .ico { position: absolute; top: 14px; right: 16px; font-size: 1.3rem; }

/* the Generate button */
[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); border: none; border-radius: 12px;
    padding: 0.7rem 1rem; font-weight: 600; box-shadow: 0 6px 16px rgba(79, 70, 229, 0.30);
    transition: transform 0.15s, box-shadow 0.15s, filter 0.15s;
}
[data-testid="stBaseButton-primary"]:hover {
    transform: translateY(-1px); filter: brightness(1.08); box-shadow: 0 10px 22px rgba(79, 70, 229, 0.38);
}

/* pill-shaped tabs */
[role="tablist"] { gap: 8px; border-bottom: none !important; }
[data-testid="stTab"] { background: #EEF2FF; border-radius: 999px; padding: 6px 18px; height: auto; }
[data-testid="stTab"][aria-selected="true"] { background: #4F46E5; }
[data-testid="stTab"][aria-selected="true"] p { color: white; }
[role="tablist"]::after { display: none; }

/* download / secondary buttons */
[data-testid="stBaseButton-secondary"] { border-radius: 10px; border-color: #C7D2FE; }
[data-testid="stBaseButton-secondary"]:hover { border-color: #4F46E5; color: #4F46E5; }

.hero p  { color: rgba(255, 255, 255, 0.88); margin: 8px 0 0 0; font-size: 1.02rem; }
</style>
""", unsafe_allow_html=True)

# 3. The header banner
st.markdown("""
<div class="hero">
    <h1>🗓️ Smart Timetable Generator</h1>
    <p>Enter your rooms, batches and courses. An AI search (simulated annealing)
       builds a clash-free weekly timetable from 09:00 to 17:00.</p>
</div>
""", unsafe_allow_html=True)

# 4. Sidebar controls
st.sidebar.header("⚙️ Search settings")
steps = st.sidebar.slider("Annealing steps", 2000, 50000, 20000, step=2000,
                          help="More steps = better timetable, but slower.")
seed = st.sidebar.number_input("Random seed", value=1, step=1,
                               help="Same seed gives the same timetable every time.")
st.sidebar.caption("Hard rules (clashes) cost 100 points each. Soft rules (gaps) cost 1.")
st.sidebar.divider()
if st.sidebar.button("↺ Reset to demo data", width="stretch"):
    for key in ("rooms", "batches", "courses", "result"):
        st.session_state.pop(key, None)
    st.rerun()


# 5. Helper: builds the HTML for one summary card
def stat_card(number, label, icon=""):
    return (f'<div class="stat"><div class="ico">{icon}</div>'
            f'<div class="num">{number}</div><div class="lab">{label}</div></div>')


# 5a. Helper: a numbered section heading
def section(number, title):
    st.markdown(f'<div class="sec"><div class="n">{number}</div><div class="t">{title}</div></div>',
                unsafe_allow_html=True)


# 5b. Colours: one (background, text) pair per course
PALETTE = [("#E0E7FF", "#3730A3"), ("#FCE7F3", "#9D174D"), ("#DCFCE7", "#166534"), ("#FEF3C7", "#92400E"),
           ("#CFFAFE", "#155E75"), ("#EDE9FE", "#5B21B6"), ("#FFE4E6", "#9F1239"), ("#ECFCCB", "#3F6212"),
           ("#FFEDD5", "#9A3412"), ("#E2E8F0", "#334155")]


def course_colors(classes):
    """Gives every course name a colour; the same course always gets the same colour."""
    names = list(dict.fromkeys(c.group or c.course for c in classes))   # a group shares one colour
    colors = {name: PALETTE[i % len(PALETTE)] for i, name in enumerate(names)}
    for c in classes:
        if c.group:
            colors[c.course] = colors[c.group]
    return colors


def short(name):
    """'OM-1 (B)' -> 'OM-1': drops a trailing batch tag to save space in a shared cell."""
    return name.rsplit(" (", 1)[0] if name.endswith(")") else name


def grid_html(classes, timetable, batch, colors):
    """Builds the weekly grid for one batch: a row per day, a column per time slot."""
    drawn = 0                                                   # how many classes get a cell
    out = ['<div class="panel"><table class="tt"><tr><th></th>']
    out += [f"<th>{p.replace('-', '–')}</th>" for p in PERIODS]
    out.append("</tr>")
    for d, day in enumerate(DAYS):
        starts = {}                                             # start period -> (class, room)
        for c, (cd, start, room) in zip(classes, timetable):
            if c.batch == batch and cd == d:
                starts.setdefault(start, []).append((c, room))
        out.append(f'<tr><td class="day">{day}</td>')
        p = 0
        while p < len(PERIODS):
            if p not in starts:
                out.append('<td class="empty"></td>')
                p += 1
                continue
            here = starts[p]
            c, room = here[0]
            same_group = [x for x in here if c.group and x[0].group == c.group]
            if len(same_group) > 1:                             # parallel electives: one shared cell
                drawn += len(same_group)
                bg, fg = colors[c.group]
                lines = "".join(f"<span>{html.escape(short(x.course))} &middot; {html.escape(r)}</span>"
                                for x, r in same_group)
                out.append(f'<td class="cls" colspan="{c.hours}" style="background:{bg};color:{fg}">'
                           f'<b>{html.escape(c.group)} &#9662;</b>{lines}</td>')
            else:
                drawn += 1
                bg, fg = colors[c.course]
                out.append(f'<td class="cls" colspan="{c.hours}" style="background:{bg};color:{fg}"><b>{html.escape(c.course)}</b>'
                           f'<span>{html.escape(room)}</span><span>{html.escape(c.teacher)}</span></td>')
            p += c.hours
        out.append("</tr>")
    out.append("</table></div>")
    total = sum(1 for c in classes if c.batch == batch)
    return "".join(out), total - drawn                         # second value = classes not drawn


# 5c. Turns the timetable into a plain table (one row per class) for download
def timetable_table(classes, timetable):
    rows = []
    for c, (day, start, room) in zip(classes, timetable):
        rows.append({"Batch": c.batch, "Course": c.course, "Teacher": c.teacher, "Day": DAYS[day],
                     "Day no.": day, "Start": PERIODS[start][:5], "End": PERIODS[start + c.hours - 1][-5:],
                     "Room": room, "Elective group": c.group})
    table = pd.DataFrame(rows).sort_values(["Batch", "Day no.", "Start"])
    return table.drop(columns="Day no.")


# 6. The three editable tables, one per tab
section("1", "Your data")
tab_rooms, tab_batches, tab_courses = st.tabs(["🏫 Rooms", "👥 Batches", "📚 Courses"])

with tab_rooms:
    rooms_df = st.data_editor(
        pd.DataFrame([(name, cap, kind) for name, (cap, kind) in ROOMS.items()],
                     columns=["Room", "Capacity", "Type"]),
        num_rows="dynamic", hide_index=True, width="stretch", key="rooms",
        column_config={
            "Capacity": st.column_config.NumberColumn(min_value=1, max_value=500, step=1),
            "Type": st.column_config.SelectboxColumn(options=["Lecture", "Lab"], required=True),
        })

with tab_batches:
    batches_df = st.data_editor(
        pd.DataFrame({"Batch": list(BATCHES), "Students": list(BATCHES.values())}),
        num_rows="dynamic", hide_index=True, width="stretch", key="batches",
        column_config={"Students": st.column_config.NumberColumn(min_value=1, max_value=500, step=1)})

with tab_courses:
    courses_df = st.data_editor(
        pd.DataFrame(COURSES, columns=["Course", "Teacher", "Batch", "Sessions", "Hours", "Type", "Group"]),
        num_rows="dynamic", hide_index=True, width="stretch", key="courses",
        column_config={
            "Batch": st.column_config.SelectboxColumn(options=list(batches_df["Batch"].dropna())),
            "Sessions": st.column_config.NumberColumn("Sessions / week", min_value=1, max_value=7, step=1),
            "Hours": st.column_config.NumberColumn("Hours each", min_value=1, max_value=2, step=1,
                                                   help="1 = lecture, 2 = lab"),
            "Type": st.column_config.SelectboxColumn("Room type", options=["Lecture", "Lab"]),
            "Group": st.column_config.TextColumn("Elective group",
                                                 help="Courses with the same group name run in parallel; a student picks one. Leave empty for a normal course."),
        })

# 7. Summary cards that update as the tables are edited
_c = courses_df.dropna(subset=["Sessions", "Hours"]).copy()
_c["Group"] = _c["Group"].fillna("").astype(str).str.strip()
_student = _c[_c["Group"] == ""]                                  # normal courses: count each
_elective = _c[_c["Group"] != ""].drop_duplicates(["Batch", "Group"])  # parallel group: count once
_both = pd.concat([_student, _elective])
n_classes = int(_both["Sessions"].sum())
n_hours = int((_both["Sessions"] * _both["Hours"]).sum())
c1, c2, c3, c4 = st.columns(4)
c1.markdown(stat_card(len(rooms_df.dropna()), "Rooms", "🏫"), unsafe_allow_html=True)
c2.markdown(stat_card(len(batches_df.dropna()), "Batches", "👥"), unsafe_allow_html=True)
c3.markdown(stat_card(n_classes, "Classes per week (per student)", "📚"), unsafe_allow_html=True)
c4.markdown(stat_card(n_hours, "Class-hours per week (per student)", "⏱️"), unsafe_allow_html=True)


# 8. Helper: reads the three tables and returns a list of problems (empty list = all fine)
def check_inputs(rooms, batches, courses):
    problems = []
    if not rooms or not batches or not courses:
        return ["Rooms, Batches and Courses must each have at least one row."]
    room_types = {kind for _, kind in rooms.values()}
    for course, teacher, batch, sessions, hours, kind, group in courses:
        if batch not in batches:
            problems.append(f"{course}: batch '{batch}' is not in the Batches table.")
        elif kind not in room_types:
            problems.append(f"{course}: no room of type '{kind}' exists.")
        elif not any(k == kind and cap >= batches[batch] for cap, k in rooms.values()):
            problems.append(f"{course}: no {kind} room is big enough for {batch} ({batches[batch]} students).")
    groups = {}                                               # (batch, group) -> set of (sessions, hours)
    for course, teacher, batch, sessions, hours, kind, group in courses:
        if group:
            groups.setdefault((batch, group), set()).add((sessions, hours))
    for (batch, group), shapes in groups.items():
        if len(shapes) > 1:
            problems.append(f"Elective group '{group}' ({batch}): all its courses need the same sessions per week and hours.")
    return problems


# 9. The Generate button
section("2", "Generate")
if st.button("✨ Generate timetable", type="primary", width="stretch"):
    rooms = {r.Room: (int(r.Capacity), r.Type) for r in rooms_df.dropna().itertuples()}
    batches = {r.Batch: int(r.Students) for r in batches_df.dropna().itertuples()}
    courses = [(r.Course, r.Teacher, r.Batch, int(r.Sessions), int(r.Hours), r.Type,
                "" if pd.isna(r.Group) else str(r.Group).strip())
               for r in courses_df.dropna(subset=["Course", "Teacher", "Batch", "Sessions", "Hours", "Type"]).itertuples()]
    problems = check_inputs(rooms, batches, courses)
    if problems:
        for p in problems:
            st.error(p)
        st.stop()
    classes = make_classes(courses)
    with st.spinner("Searching for a timetable..."):
        timetable, history = solve(classes, rooms, batches, iters=steps, seed=int(seed))
    st.toast("Timetable generated!", icon="✅")
    st.session_state.result = dict(timetable=timetable, classes=classes, rooms=rooms,
                                   batches=batches, history=history, steps=steps)

# 10. Show the result (it stays on screen between re-runs because it lives in session_state)
result = st.session_state.get("result")
if result:
    hard = hard_violations(result["timetable"], result["classes"], result["rooms"], result["batches"])
    soft = soft_penalty(result["timetable"], result["classes"])
    if hard == 0:
        st.success("Valid timetable: no clashes.")
    else:
        st.error(f"{hard} clash(es) remain. Try more steps or add a room.")
    r1, r2, r3 = st.columns(3)
    r1.markdown(stat_card(hard, "Clashes (must be 0)", "✅" if hard == 0 else "⚠️"), unsafe_allow_html=True)
    r2.markdown(stat_card(soft, "Preference penalty", "🎯"), unsafe_allow_html=True)
    r3.markdown(stat_card(f"{result['steps']:,}", "Step limit", "🔍"), unsafe_allow_html=True)

    section("3", "Your timetable")
    batch = st.radio("Show timetable for", list(result["batches"]), horizontal=True)
    colors = course_colors(result["classes"])
    table, hidden = grid_html(result["classes"], result["timetable"], batch, colors)
    st.markdown(table, unsafe_allow_html=True)
    if hidden:
        st.warning(f"{hidden} class(es) overlap another class in this batch and are not drawn.")
    if any(c.group for c in result["classes"] if c.batch == batch):
        st.caption("Cells marked &#9662; are elective groups: the courses listed run in parallel and a student attends one of them.")
    legend = "".join(
        f'<span class="chip" style="background:{bg};color:{fg}">{html.escape(name)}</span>'
        for name, (bg, fg) in colors.items()
        if any((c.group or c.course) == name and c.batch == batch for c in result["classes"]))
    st.markdown(legend, unsafe_allow_html=True)

    st.write("")
    left, right = st.columns([3, 2])
    with left:
        st.markdown("#### 📈 How the search improved")
        steps_axis = [i * 100 for i in range(len(result["history"]))]
        st.line_chart(pd.DataFrame({"step": steps_axis, "best cost so far": result["history"]}),
                      x="step", y="best cost so far", color="#4F46E5")
    with right:
        st.markdown("#### ⬇️ Export")
        st.caption("One row per class, sorted by batch, day and time.")
        st.download_button("Download timetable (CSV)",
                           data=timetable_table(result["classes"], result["timetable"]).to_csv(index=False),
                           file_name="timetable.csv", mime="text/csv", width="stretch")
else:
    st.info("Check the tables above, then press **Generate timetable**. "
            "Your timetable will appear here.")
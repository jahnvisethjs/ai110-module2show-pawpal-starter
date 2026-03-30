"""
PawPal+ Streamlit App — Interactive UI for pet care scheduling.

Run with:  streamlit run app.py
"""

import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Smart pet care scheduling — track, plan, and prioritize daily routines.")

# ── Session state initialization ─────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", email="jordan@example.com", time_available_minutes=120)

if "schedule_result" not in st.session_state:
    st.session_state.schedule_result = None

owner: Owner = st.session_state.owner

# ── Sidebar — Owner settings ────────────────────────────────────────────────
with st.sidebar:
    st.header("👤 Owner Settings")
    new_name = st.text_input("Owner name", value=owner.name)
    new_budget = st.number_input(
        "Daily time budget (minutes)", min_value=15, max_value=480, value=owner.time_available_minutes
    )
    if new_name != owner.name:
        owner.name = new_name
    if new_budget != owner.time_available_minutes:
        owner.time_available_minutes = new_budget

    st.divider()
    st.header("🐾 Add a Pet")
    with st.form("add_pet_form", clear_on_submit=True):
        pet_name = st.text_input("Pet name")
        species = st.selectbox("Species", ["dog", "cat", "other"])
        pet_age = st.number_input("Age", min_value=0, max_value=30, value=1)
        submitted_pet = st.form_submit_button("Add Pet")
        if submitted_pet and pet_name.strip():
            if owner.get_pet(pet_name):
                st.warning(f"A pet named '{pet_name}' already exists.")
            else:
                owner.add_pet(Pet(name=pet_name.strip(), species=species, age=pet_age))
                st.success(f"Added {pet_name}!")

# ── Main area — Pets overview ────────────────────────────────────────────────
if not owner.pets:
    st.info("No pets yet — add one using the sidebar.")
else:
    # ── Add Task section ─────────────────────────────────────────────────
    st.subheader("📝 Add a Task")
    pet_names = [p.name for p in owner.pets]
    with st.form("add_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            selected_pet = st.selectbox("For pet", pet_names)
            task_title = st.text_input("Task title", placeholder="e.g. Morning walk")
            task_time = st.text_input("Time (HH:MM)", value="08:00")
        with col2:
            task_duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
            task_priority = st.selectbox("Priority", ["high", "medium", "low"])
            task_frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        submitted_task = st.form_submit_button("Add Task")
        if submitted_task and task_title.strip():
            pet = owner.get_pet(selected_pet)
            if pet:
                new_task = Task(
                    title=task_title.strip(),
                    time=task_time,
                    duration_minutes=task_duration,
                    priority=task_priority,
                    frequency=task_frequency,
                )
                pet.add_task(new_task)
                st.success(f"Added '{task_title}' for {selected_pet}!")

    st.divider()

    # ── Current pets and tasks ───────────────────────────────────────────
    st.subheader("🐾 Your Pets & Tasks")
    for pet in owner.pets:
        with st.expander(f"{pet}", expanded=True):
            if pet.tasks:
                for i, task in enumerate(pet.tasks):
                    cols = st.columns([0.5, 3, 1])
                    with cols[0]:
                        if not task.completed:
                            if st.button("✅", key=f"complete_{pet.name}_{i}", help="Mark complete"):
                                scheduler = Scheduler(owner)
                                new_t = scheduler.mark_task_complete(task)
                                if new_t:
                                    st.toast(f"🔄 Next '{new_t.title}' scheduled!")
                                st.rerun()
                        else:
                            st.write("✅")
                    with cols[1]:
                        status = "~~" if task.completed else ""
                        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "⚪")
                        st.markdown(
                            f"{status}{priority_emoji} **{task.time}** — {task.title} "
                            f"({task.duration_minutes}min, {task.frequency}){status}"
                        )
                    with cols[2]:
                        st.caption(task.priority)
            else:
                st.caption("No tasks yet for this pet.")

    st.divider()

    # ── Schedule generation ──────────────────────────────────────────────
    st.subheader("📅 Generate Daily Schedule")
    st.caption(
        f"Your time budget: **{owner.time_available_minutes} minutes**. "
        "Tasks are prioritized (high → low) and fit within the budget."
    )

    if st.button("🗓️ Generate Schedule", type="primary"):
        scheduler = Scheduler(owner)
        st.session_state.schedule_result = scheduler.generate_schedule()

    result = st.session_state.schedule_result
    if result:
        # Conflicts
        if result["conflicts"]:
            for w in result["conflicts"]:
                st.warning(w)

        # Scheduled tasks table
        if result["scheduled"]:
            st.success(
                f"Scheduled {len(result['scheduled'])} tasks "
                f"({result['total_minutes']}/{owner.time_available_minutes} min used)"
            )
            table_data = [
                {
                    "Time": t.time,
                    "Task": t.title,
                    "Pet": t.pet_name,
                    "Priority": {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}.get(t.priority, t.priority),
                    "Duration": f"{t.duration_minutes} min",
                    "Frequency": t.frequency,
                }
                for t in result["scheduled"]
            ]
            st.table(table_data)
        else:
            st.info("No tasks to schedule.")

        # Skipped tasks
        if result["skipped"]:
            with st.expander("⏭️ Skipped tasks (not enough time)"):
                for t in result["skipped"]:
                    st.write(f"- {t.title} for {t.pet_name} [{t.priority}] ({t.duration_minutes} min)")

        # Explanation
        with st.expander("💡 Schedule Reasoning", expanded=False):
            st.text(result["explanation"])

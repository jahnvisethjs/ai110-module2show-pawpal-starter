"""
PawPal+ CLI Demo — verifies the backend logic in the terminal.

Run with:  python main.py
"""

from pawpal_system import Task, Pet, Owner, Scheduler


def main():
    # ── 1. Create an Owner ───────────────────────────────────────────────
    owner = Owner(name="Jordan", email="jordan@example.com", time_available_minutes=90)
    print(owner)
    print()

    # ── 2. Create Pets ───────────────────────────────────────────────────
    mochi = Pet(name="Mochi", species="dog", age=3)
    whiskers = Pet(name="Whiskers", species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    # ── 3. Add Tasks (intentionally out of order) ────────────────────────
    mochi.add_task(Task(title="Evening walk",      time="18:00", duration_minutes=30, priority="high",   frequency="daily"))
    mochi.add_task(Task(title="Morning walk",      time="07:30", duration_minutes=25, priority="high",   frequency="daily"))
    mochi.add_task(Task(title="Flea medication",   time="09:00", duration_minutes=5,  priority="high",   frequency="weekly"))
    mochi.add_task(Task(title="Brush coat",        time="10:00", duration_minutes=15, priority="low",    frequency="weekly"))

    whiskers.add_task(Task(title="Morning feeding", time="07:30", duration_minutes=10, priority="high",   frequency="daily"))
    whiskers.add_task(Task(title="Litter box clean", time="08:00", duration_minutes=10, priority="medium", frequency="daily"))
    whiskers.add_task(Task(title="Play session",    time="16:00", duration_minutes=20, priority="medium", frequency="daily"))

    # ── 4. Scheduler ─────────────────────────────────────────────────────
    scheduler = Scheduler(owner)

    # Sorting demo
    print("=" * 60)
    print("📋 ALL TASKS SORTED BY TIME")
    print("=" * 60)
    for t in scheduler.sort_by_time():
        print(f"  {t}")
    print()

    # Filtering demo
    print("=" * 60)
    print("🐶 MOCHI'S TASKS ONLY")
    print("=" * 60)
    for t in scheduler.filter_by_pet("Mochi"):
        print(f"  {t}")
    print()

    # Conflict detection demo (07:30 overlap)
    print("=" * 60)
    print("⚠️  CONFLICT DETECTION")
    print("=" * 60)
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for w in conflicts:
            print(f"  {w}")
    else:
        print("  No conflicts found.")
    print()

    # Full schedule generation
    print("=" * 60)
    print("📅 GENERATED DAILY SCHEDULE")
    print("=" * 60)
    result = scheduler.generate_schedule()
    print(result["explanation"])
    print()

    # Recurring task demo
    print("=" * 60)
    print("🔄 RECURRING TASK DEMO")
    print("=" * 60)
    morning_walk = mochi.tasks[1]  # Morning walk
    print(f"  Completing: {morning_walk}")
    new_task = scheduler.mark_task_complete(morning_walk)
    print(f"  Status after: {morning_walk}")
    if new_task:
        print(f"  Next occurrence created: {new_task}")
    print(f"  Mochi now has {len(mochi.tasks)} tasks")
    print()

    print("✅ Demo complete!")


if __name__ == "__main__":
    main()

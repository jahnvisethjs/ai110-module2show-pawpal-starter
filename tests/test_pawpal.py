"""
Automated test suite for PawPal+ system.

Run with:  python -m pytest
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import Task, Pet, Owner, Scheduler


# ── Task tests ───────────────────────────────────────────────────────────────

class TestTask:
    def test_mark_complete_changes_status(self):
        task = Task(title="Walk", time="08:00", duration_minutes=30)
        assert task.completed is False
        task.mark_complete()
        assert task.completed is True

    def test_end_time_calculation(self):
        task = Task(title="Feed", time="07:30", duration_minutes=15)
        assert task.end_time() == "07:45"

    def test_end_time_crosses_hour(self):
        task = Task(title="Play", time="09:50", duration_minutes=20)
        assert task.end_time() == "10:10"


# ── Pet tests ────────────────────────────────────────────────────────────────

class TestPet:
    def test_add_task_increases_count(self):
        pet = Pet(name="Mochi", species="dog")
        assert len(pet.tasks) == 0
        pet.add_task(Task(title="Walk", time="08:00", duration_minutes=30))
        assert len(pet.tasks) == 1

    def test_add_task_sets_pet_name(self):
        pet = Pet(name="Mochi", species="dog")
        task = Task(title="Walk", time="08:00", duration_minutes=30)
        pet.add_task(task)
        assert task.pet_name == "Mochi"

    def test_remove_task(self):
        pet = Pet(name="Mochi", species="dog")
        pet.add_task(Task(title="Walk", time="08:00", duration_minutes=30))
        assert pet.remove_task("Walk") is True
        assert len(pet.tasks) == 0

    def test_pending_tasks_excludes_completed(self):
        pet = Pet(name="Mochi", species="dog")
        t1 = Task(title="Walk", time="08:00", duration_minutes=30)
        t2 = Task(title="Feed", time="09:00", duration_minutes=10)
        pet.add_task(t1)
        pet.add_task(t2)
        t1.mark_complete()
        assert len(pet.pending_tasks()) == 1
        assert pet.pending_tasks()[0].title == "Feed"


# ── Owner tests ──────────────────────────────────────────────────────────────

class TestOwner:
    def test_add_pet(self):
        owner = Owner(name="Jordan")
        owner.add_pet(Pet(name="Mochi", species="dog"))
        assert len(owner.pets) == 1

    def test_get_pet_case_insensitive(self):
        owner = Owner(name="Jordan")
        owner.add_pet(Pet(name="Mochi", species="dog"))
        assert owner.get_pet("mochi") is not None

    def test_all_tasks_aggregates(self):
        owner = Owner(name="Jordan")
        p1 = Pet(name="Mochi", species="dog")
        p2 = Pet(name="Whiskers", species="cat")
        p1.add_task(Task(title="Walk", time="08:00", duration_minutes=30))
        p2.add_task(Task(title="Feed", time="09:00", duration_minutes=10))
        owner.add_pet(p1)
        owner.add_pet(p2)
        assert len(owner.all_tasks()) == 2


# ── Scheduler tests ──────────────────────────────────────────────────────────

class TestScheduler:
    def _make_scheduler(self):
        owner = Owner(name="Jordan", time_available_minutes=60)
        mochi = Pet(name="Mochi", species="dog")
        mochi.add_task(Task(title="Evening walk", time="18:00", duration_minutes=30, priority="high", frequency="daily"))
        mochi.add_task(Task(title="Morning walk", time="07:30", duration_minutes=25, priority="high", frequency="daily"))
        mochi.add_task(Task(title="Brush coat",   time="10:00", duration_minutes=15, priority="low",  frequency="weekly"))
        owner.add_pet(mochi)
        return Scheduler(owner), owner, mochi

    def test_sort_by_time_chronological(self):
        sched, _, _ = self._make_scheduler()
        sorted_tasks = sched.sort_by_time()
        times = [t.time for t in sorted_tasks]
        assert times == sorted(times)

    def test_sort_by_priority_high_first(self):
        sched, _, _ = self._make_scheduler()
        sorted_tasks = sched.sort_by_priority()
        assert sorted_tasks[0].priority == "high"
        assert sorted_tasks[-1].priority == "low"

    def test_filter_by_pet(self):
        sched, _, _ = self._make_scheduler()
        tasks = sched.filter_by_pet("Mochi")
        assert len(tasks) == 3

    def test_filter_by_status(self):
        sched, _, mochi = self._make_scheduler()
        mochi.tasks[0].mark_complete()
        pending = sched.filter_by_status(completed=False)
        assert len(pending) == 2

    def test_detect_conflicts_overlapping(self):
        owner = Owner(name="Jordan")
        pet = Pet(name="Mochi", species="dog")
        pet.add_task(Task(title="Walk",  time="08:00", duration_minutes=30, priority="high"))
        pet.add_task(Task(title="Feed",  time="08:15", duration_minutes=10, priority="high"))
        owner.add_pet(pet)
        sched = Scheduler(owner)
        conflicts = sched.detect_conflicts()
        assert len(conflicts) == 1
        assert "Conflict" in conflicts[0]

    def test_detect_conflicts_no_overlap(self):
        owner = Owner(name="Jordan")
        pet = Pet(name="Mochi", species="dog")
        pet.add_task(Task(title="Walk", time="08:00", duration_minutes=30, priority="high"))
        pet.add_task(Task(title="Feed", time="09:00", duration_minutes=10, priority="high"))
        owner.add_pet(pet)
        sched = Scheduler(owner)
        assert sched.detect_conflicts() == []

    def test_recurring_daily_task(self):
        sched, _, mochi = self._make_scheduler()
        original = mochi.tasks[0]  # Evening walk, daily
        new_task = sched.mark_task_complete(original)
        assert original.completed is True
        assert new_task is not None
        assert new_task.completed is False
        assert new_task.frequency == "daily"
        assert len(mochi.tasks) == 4  # original 3 + 1 new

    def test_generate_schedule_respects_budget(self):
        sched, owner, _ = self._make_scheduler()
        result = sched.generate_schedule()
        total = sum(t.duration_minutes for t in result["scheduled"])
        assert total <= owner.time_available_minutes

    def test_generate_schedule_has_explanation(self):
        sched, _, _ = self._make_scheduler()
        result = sched.generate_schedule()
        assert "explanation" in result
        assert len(result["explanation"]) > 0

    def test_pet_with_no_tasks(self):
        owner = Owner(name="Jordan")
        owner.add_pet(Pet(name="Ghost", species="cat"))
        sched = Scheduler(owner)
        result = sched.generate_schedule()
        assert result["scheduled"] == []
        assert result["conflicts"] == []

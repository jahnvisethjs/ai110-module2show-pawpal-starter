"""
PawPal+ System — Core logic layer for pet care scheduling.

This module defines the four main classes: Task, Pet, Owner, and Scheduler.
Together they represent a modular system for tracking, organizing, and
prioritizing daily pet care activities.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional


# ── Task ────────────────────────────────────────────────────────────────────

@dataclass
class Task:
    """A single pet-care activity (walk, feeding, medication, etc.)."""

    title: str
    time: str                       # "HH:MM" format
    duration_minutes: int           # how long the task takes
    priority: str = "medium"        # "low", "medium", or "high"
    frequency: str = "once"         # "once", "daily", or "weekly"
    completed: bool = False
    pet_name: str = ""              # back-reference for display purposes

    # ── helpers ──────────────────────────────────────────────────────────

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task as done. If it recurs, return a new Task for the next occurrence."""
        self.completed = True
        if self.frequency == "daily":
            return self._next_occurrence(days=1)
        elif self.frequency == "weekly":
            return self._next_occurrence(days=7)
        return None

    def _next_occurrence(self, days: int) -> "Task":
        """Create the next recurring instance shifted by *days*."""
        current = datetime.strptime(self.time, "%H:%M")
        next_time = current  # time-of-day stays the same for daily/weekly
        return Task(
            title=self.title,
            time=next_time.strftime("%H:%M"),
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            completed=False,
            pet_name=self.pet_name,
        )

    def end_time(self) -> str:
        """Calculate the end time of this task as 'HH:MM'."""
        start = datetime.strptime(self.time, "%H:%M")
        end = start + timedelta(minutes=self.duration_minutes)
        return end.strftime("%H:%M")

    def __repr__(self) -> str:
        status = "✅" if self.completed else "⬜"
        return (
            f"{status} [{self.priority.upper()}] {self.time} - {self.title} "
            f"({self.duration_minutes}min, {self.frequency})"
        )


# ── Pet ─────────────────────────────────────────────────────────────────────

@dataclass
class Pet:
    """A pet belonging to an owner, with its own task list."""

    name: str
    species: str                    # e.g. "dog", "cat", "other"
    age: int = 0
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, title: str) -> bool:
        """Remove the first task that matches *title*. Returns True if found."""
        for i, t in enumerate(self.tasks):
            if t.title == title:
                self.tasks.pop(i)
                return True
        return False

    def pending_tasks(self) -> List[Task]:
        """Return only incomplete tasks."""
        return [t for t in self.tasks if not t.completed]

    def __repr__(self) -> str:
        return f"🐾 {self.name} ({self.species}) — {len(self.tasks)} task(s)"


# ── Owner ───────────────────────────────────────────────────────────────────

@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    email: str = ""
    time_available_minutes: int = 120   # daily time budget
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Look up a pet by name (case-insensitive)."""
        for p in self.pets:
            if p.name.lower() == name.lower():
                return p
        return None

    def all_tasks(self) -> List[Task]:
        """Aggregate every task across all pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks

    def __repr__(self) -> str:
        pet_names = ", ".join(p.name for p in self.pets) or "none"
        return f"👤 {self.name} — pets: {pet_names}"


# ── Scheduler ───────────────────────────────────────────────────────────────

PRIORITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}


class Scheduler:
    """The 'brain' — retrieves, sorts, filters, and validates tasks."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    # ── sorting ──────────────────────────────────────────────────────────

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks sorted chronologically by their start time."""
        if tasks is None:
            tasks = self.owner.all_tasks()
        return sorted(tasks, key=lambda t: t.time)

    def sort_by_priority(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks sorted by priority (high → low), then by time."""
        if tasks is None:
            tasks = self.owner.all_tasks()
        return sorted(
            tasks,
            key=lambda t: (-PRIORITY_WEIGHT.get(t.priority, 0), t.time),
        )

    # ── filtering ────────────────────────────────────────────────────────

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        """Return only tasks belonging to a specific pet."""
        return [t for t in self.owner.all_tasks() if t.pet_name.lower() == pet_name.lower()]

    def filter_by_status(self, completed: bool = False) -> List[Task]:
        """Return tasks filtered by completion status."""
        return [t for t in self.owner.all_tasks() if t.completed == completed]

    def filter_by_priority(self, priority: str) -> List[Task]:
        """Return tasks that match the given priority level."""
        return [t for t in self.owner.all_tasks() if t.priority == priority]

    # ── conflict detection ───────────────────────────────────────────────

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """Find tasks whose time ranges overlap and return warning strings."""
        if tasks is None:
            tasks = self.sort_by_time(self.filter_by_status(completed=False))
        else:
            tasks = self.sort_by_time(tasks)

        warnings: List[str] = []
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                a, b = tasks[i], tasks[j]
                if a.end_time() > b.time:
                    warnings.append(
                        f"⚠️ Conflict: '{a.title}' ({a.time}–{a.end_time()}) "
                        f"overlaps with '{b.title}' ({b.time}–{b.end_time()})"
                    )
        return warnings

    # ── recurring task management ────────────────────────────────────────

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Mark a task complete and, if recurring, add the next occurrence to the same pet."""
        new_task = task.mark_complete()
        if new_task is not None:
            # find the pet that owns this task and add the next occurrence
            for pet in self.owner.pets:
                if pet.name.lower() == task.pet_name.lower():
                    pet.add_task(new_task)
                    break
        return new_task

    # ── schedule generation ──────────────────────────────────────────────

    def generate_schedule(self) -> dict:
        """Build a daily schedule respecting the owner's time budget.

        Returns a dict with 'scheduled', 'skipped', 'conflicts', and 'explanation' keys.
        """
        pending = self.filter_by_status(completed=False)
        ranked = self.sort_by_priority(pending)

        scheduled: List[Task] = []
        skipped: List[Task] = []
        total_minutes = 0
        budget = self.owner.time_available_minutes

        for task in ranked:
            if total_minutes + task.duration_minutes <= budget:
                scheduled.append(task)
                total_minutes += task.duration_minutes
            else:
                skipped.append(task)

        # sort the scheduled tasks by time for the final timeline
        scheduled = self.sort_by_time(scheduled)
        conflicts = self.detect_conflicts(scheduled)

        explanation = self._build_explanation(scheduled, skipped, total_minutes, budget, conflicts)

        return {
            "scheduled": scheduled,
            "skipped": skipped,
            "conflicts": conflicts,
            "total_minutes": total_minutes,
            "explanation": explanation,
        }

    # ── explanation builder ──────────────────────────────────────────────

    @staticmethod
    def _build_explanation(
        scheduled: List[Task],
        skipped: List[Task],
        used: int,
        budget: int,
        conflicts: List[str],
    ) -> str:
        """Produce a human-readable explanation of the generated schedule."""
        lines = [f"📅 Daily Schedule — {used}/{budget} minutes used\n"]
        lines.append("Scheduled tasks (by time):")
        for i, t in enumerate(scheduled, 1):
            lines.append(
                f"  {i}. {t.time} — {t.title} for {t.pet_name} "
                f"[{t.priority}] ({t.duration_minutes} min)"
            )

        if skipped:
            lines.append("\nSkipped (not enough time):")
            for t in skipped:
                lines.append(f"  - {t.title} for {t.pet_name} [{t.priority}] ({t.duration_minutes} min)")

        if conflicts:
            lines.append("\n⚠️ Time conflicts detected:")
            for w in conflicts:
                lines.append(f"  {w}")

        lines.append(
            f"\n💡 Reasoning: Tasks were ranked by priority (high → low), "
            f"then fit into the {budget}-minute daily budget. "
            f"The final timeline is ordered by start time."
        )
        return "\n".join(lines)

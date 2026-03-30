# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial UML design includes four core classes that follow a clear hierarchy of responsibility:

- **Task** (dataclass): Represents a single pet-care activity with attributes for title, scheduled time (HH:MM), duration, priority (low/medium/high), frequency (once/daily/weekly), and completion status. It owns the `mark_complete()` method which also handles recurring-task generation via `_next_occurrence()`.
- **Pet** (dataclass): Stores pet info (name, species, age) and maintains a list of Task objects. Responsible for adding/removing tasks and filtering by completion status.
- **Owner** (dataclass): Represents the pet owner with a time-budget constraint (`time_available_minutes`). Manages multiple Pet objects and aggregates all tasks across pets.
- **Scheduler**: The algorithmic "brain" that takes an Owner and provides sorting (by time, by priority), filtering (by pet, status, priority), conflict detection (overlapping time ranges), recurring task management, and full schedule generation with explanations.

The three core actions a user should be able to perform are:
1. Add pets and assign care tasks with time, duration, and priority.
2. Generate a prioritized daily schedule that fits within their available time budget.
3. View conflicts, mark tasks complete, and see recurring tasks auto-regenerate.

**b. Design changes**

Yes, the design evolved during implementation. Initially the Scheduler was conceived as a simple sorter, but it grew into the central orchestration class that also handles conflict detection, recurring task creation, and explanation generation. The `generate_schedule()` method was added to produce a complete daily plan with a reasoning explanation, which was not part of the original skeleton. This change was necessary because the project required the system to "explain the plan," and placing that logic in the Scheduler kept the other classes clean and focused on data representation.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints:
- **Priority**: Tasks are ranked high → medium → low using a weight map (3, 2, 1). High-priority tasks always get scheduled first.
- **Time budget**: The owner's `time_available_minutes` acts as a hard cap. Tasks are added greedily until the budget is exhausted.
- **Time conflicts**: After scheduling, the system detects overlapping time ranges and surfaces warnings.

Priority was ranked as the most important constraint because in a pet-care context, missing a medication (high priority) is far worse than skipping a grooming session (low priority).

**b. Tradeoffs**

The scheduler uses a greedy priority-first algorithm rather than an optimal knapsack approach. This means it may skip a combination of smaller low-priority tasks that could collectively fit in the remaining budget if a single medium-priority task takes up the space. This tradeoff is reasonable because:
1. Pet care tasks are time-sensitive (a walk at 7:30 AM can't move to 3 PM), so optimal packing matters less than getting high-priority items done.
2. The greedy approach is simple, readable, and easy to debug — important qualities for a system a pet owner will trust.

---

## 3. AI Collaboration

**a. How you used AI**

AI tools were used throughout this project in several ways:
- **Design brainstorming**: I used AI to help identify the four core classes and their relationships, resulting in the Mermaid.js UML diagram.
- **Scaffolding**: AI generated the initial dataclass skeletons for Task, Pet, and Owner, which I then refined with custom methods.
- **Algorithm design**: I used AI to draft the conflict detection algorithm and the greedy scheduling approach, then reviewed and modified both.
- **Test generation**: AI helped draft the pytest suite, suggesting edge cases like "pet with no tasks" and "overlapping time ranges."
- **Debugging**: When the recurring task logic initially duplicated tasks incorrectly, I used AI inline chat to trace the issue.

The most helpful prompts were specific and contextual, like "Given my Task dataclass with a time field in HH:MM format, how should I detect overlapping tasks based on their duration?"

**b. Judgment and verification**

One example where I did not accept an AI suggestion as-is: AI initially suggested using `datetime.date` objects for task scheduling with full date tracking. I rejected this because PawPal+ is a daily planner — tracking dates adds complexity without benefit for the MVP. Instead, I kept tasks as time-of-day strings ("HH:MM") and used `timedelta` only for calculating end times and recurrence. I verified this decision by running the demo script and confirming that all sorting, filtering, and conflict detection worked correctly with the simpler representation.

---

## 4. Testing and Verification

**a. What you tested**

The test suite covers 16 test cases across all four classes:
- **Task**: completion status change, end-time calculation, hour-boundary crossing.
- **Pet**: task addition, pet-name back-reference, task removal, pending-task filtering.
- **Owner**: pet management, case-insensitive lookup, cross-pet task aggregation.
- **Scheduler**: chronological sorting, priority sorting, pet filtering, status filtering, overlap conflict detection, no-conflict scenario, daily recurrence generation, budget enforcement, explanation presence, and the edge case of a pet with zero tasks.

These tests are important because they verify the core contract of each class — if sorting breaks, every schedule is wrong; if recurrence fails, daily tasks vanish after one completion.

**b. Confidence**

Confidence level: ⭐⭐⭐⭐ (4/5)

The system is well-tested for standard scenarios. Edge cases I would test next with more time:
- Tasks that span midnight (e.g., 23:45 + 30 min).
- Very large numbers of tasks (performance).
- Concurrent modifications to the task list during scheduling.
- Weekly recurrence with actual date tracking across multiple days.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the Scheduler's `generate_schedule()` method and its explanation output. It cleanly ties together sorting, filtering, conflict detection, and budget management into a single coherent result that a user can understand. The explanation text makes the system's decisions transparent.

**b. What you would improve**

If I had another iteration, I would:
1. Add actual date-based scheduling (not just time-of-day) to support multi-day planning.
2. Implement a smarter algorithm (e.g., weighted interval scheduling) that considers both priority and time-slot optimization.
3. Add data persistence with JSON save/load so pets and tasks survive between app restarts.

**c. Key takeaway**

The most important thing I learned is that AI is most effective as a collaborator, not an autopilot. It excels at generating boilerplate, suggesting algorithms, and catching edge cases — but the human architect needs to make design decisions about what to include, what to simplify, and when an AI suggestion adds unnecessary complexity. Keeping the system modular (separate classes with clear responsibilities) made it much easier to iterate on individual pieces without breaking the whole.

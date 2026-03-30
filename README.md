# 🐾 PawPal+ (Module 2 Project)

PawPal+ is a smart pet care management system that helps owners keep their furry friends happy and healthy. It tracks daily routines — feedings, walks, medications, and appointments — while using algorithmic logic to organize and prioritize tasks within a daily time budget.

## Scenario

A busy pet owner needs help staying consistent with pet care. PawPal+ is an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

## Features

### Core System (OOP)
- **Task** dataclass with title, time, duration, priority, frequency, and completion tracking
- **Pet** dataclass that manages its own task list with add/remove/filter operations
- **Owner** dataclass that manages multiple pets and aggregates all tasks
- **Scheduler** class that serves as the algorithmic brain of the system

### Smarter Scheduling
- **Sorting by time**: Tasks are arranged chronologically using lambda-based sorting on "HH:MM" strings
- **Priority-based scheduling**: Tasks ranked high → medium → low with a weighted greedy algorithm that fits within the owner's daily time budget
- **Conflict detection**: Identifies overlapping tasks by comparing time ranges (start + duration) and surfaces clear warnings
- **Recurring tasks**: Daily and weekly tasks auto-regenerate when marked complete, using `timedelta` for accurate scheduling
- **Filtering**: Filter tasks by pet name, completion status, or priority level
- **Plan explanation**: Every generated schedule includes a human-readable explanation of why tasks were chosen and ordered

### Streamlit UI
- Sidebar for owner settings and adding pets
- Form-based task creation with time, duration, priority, and frequency
- Per-pet task views with inline completion buttons
- Color-coded priority indicators (🔴 High, 🟡 Medium, 🟢 Low)
- One-click schedule generation with conflict warnings and reasoning display

## System Architecture

The system follows a layered design:

```
Owner → has many → Pet → has many → Task
                    ↑
              Scheduler (reads from Owner, operates on Tasks)
```

See `uml_final.png` for the complete Mermaid.js class diagram.

## Getting Started

### Setup
```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the CLI Demo
```bash
python main.py
```

### Run the Streamlit App
```bash
streamlit run app.py
```

## Testing PawPal+

Run the automated test suite with:

```bash
python -m pytest
```

The test suite includes **16 tests** covering:

- **Task tests**: completion status, end-time calculation, hour-boundary crossing
- **Pet tests**: task addition, pet-name assignment, task removal, pending-task filtering
- **Owner tests**: pet management, case-insensitive lookup, cross-pet aggregation
- **Scheduler tests**: chronological sorting, priority sorting, pet filtering, status filtering, overlap conflict detection, no-conflict verification, daily recurrence, budget enforcement, explanation generation, and empty-pet edge case

**Confidence Level**: ⭐⭐⭐⭐ (4/5) — All core behaviors are tested. Future iterations would add midnight-spanning tasks, performance testing, and multi-day scheduling.

## 📸 Demo

*Screenshot of the Streamlit app showing the generated daily schedule with priority indicators and conflict warnings.*

## Tech Stack

- Python 3.10+ with dataclasses
- Streamlit for the interactive UI
- pytest for automated testing

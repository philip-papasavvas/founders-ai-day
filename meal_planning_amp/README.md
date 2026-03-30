# Meal Planning Amp

A household weekly meal planner built on Sunday 29 March 2026 at Dr Will's head office during the AI Founders Day.

This app was generated using [Ampcode](https://ampcode.com), Sourcegraph's agentic coding tool.

## Contents

- `meal_planning_amp.py` — Streamlit entrypoint
- `meal_planning/` — planning engine, UI helpers, PDF export, and meal history storage
- `tests/` — focused regression tests for the planner
- `data/meal_planner/` — local history output directory created/used by the app

## Setup

From inside [founders-ai-day/meal_planning_amp](file:///Users/philip.papasavvas/PycharmProjects/founders-ai-day/meal_planning_amp):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Locally

```bash
streamlit run meal_planning_amp.py
```

Streamlit will print a local URL, usually `http://localhost:8501`.

## Run Tests

```bash
pytest tests/test_meal_planner.py
```

## Notes

- Meal ratings/history are written to `data/meal_planner/history.json` inside this folder.
- The PDF export is built into the app and can be downloaded from the shopping list tab.
- This copy is self-contained and does not rely on the main portfolio app.

# Meal Planner — Claude Code Edition

A household weekly meal planner with 32 recipes, weekly plan generation, shopping lists, and a meal rating system. Built on Sunday 29 March 2026 at Dr Will's head office during the AI Founders Day.

This app was generated using [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview), Anthropic's agentic coding tool.

## Contents

- `app.py` — Streamlit home page
- `pages/` — Weekly Planner, Shopping List, Meal Ratings, Preferences, Recipe Library
- `database.py` — SQLite persistence layer
- `generator.py` — Meal plan generation with weighted random selection
- `seed_data.py` — Full recipe catalogue (32 recipes with ingredients and macros)
- `styles.py` — Dark mode theme with pink accents

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Locally

```bash
streamlit run app.py
```
"""Persistence helpers for meal history and retrospective ratings."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from hashlib import sha1
from typing import Any

from meal_planning.catalog import MEAL_LOOKUP
from meal_planning.planner import MealPlannerPreferences, WeeklyMealPlan, unique_meals_from_plan
from meal_planning.storage import resolve_data_file

HISTORY_RELATIVE_PATH = "meal_planner/history.json"
MAX_SIGNATURES = 250


@dataclass(frozen=True)
class MealHistoryRecord:
    """Stored history for a meal that has appeared in a generated plan."""

    key: str
    name: str
    meal_type: str
    seen_count: int
    last_planned: str
    rating: int | None = None


def _default_payload() -> dict[str, Any]:
    """Return the empty persisted structure."""

    return {"plan_signatures": [], "meals": {}}


def _read_payload() -> dict[str, Any]:
    """Read meal history from disk, falling back to an empty structure."""

    history_path = resolve_data_file(HISTORY_RELATIVE_PATH)
    if not history_path.exists():
        return _default_payload()

    try:
        return json.loads(history_path.read_text())
    except json.JSONDecodeError:
        return _default_payload()


def _write_payload(payload: dict[str, Any]) -> None:
    """Persist meal history to the writable data location."""

    resolved_path = resolve_data_file(HISTORY_RELATIVE_PATH)
    history_path = resolved_path
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def load_meal_history() -> dict[str, MealHistoryRecord]:
    """Load the persisted meal history records."""

    raw_payload = _read_payload()
    records: dict[str, MealHistoryRecord] = {}
    for meal_key, payload in raw_payload.get("meals", {}).items():
        records[meal_key] = MealHistoryRecord(
            key=meal_key,
            name=str(payload.get("name", meal_key)),
            meal_type=str(payload.get("meal_type", "dinner")),
            seen_count=int(payload.get("seen_count", 0)),
            last_planned=str(payload.get("last_planned", "")),
            rating=payload.get("rating"),
        )
    return records


def build_plan_signature(
    preferences: MealPlannerPreferences, plan: WeeklyMealPlan
) -> str:
    """Create a stable signature for the current generated plan."""

    payload = {
        "office_days": preferences.office_days,
        "budget": preferences.weekly_budget_gbp,
        "hosted_dinners": preferences.hosted_dinners,
        "guests_per_hosted_dinner": preferences.guests_per_hosted_dinner,
        "nutrition_focus": preferences.nutrition_focus,
        "variety_mode": preferences.variety_mode,
        "week_index": preferences.week_index,
        "meals": [
            f"{planned.slot}:{planned.meal.key}:{planned.servings}"
            for planned in plan.breakfasts + plan.lunches + plan.dinners
        ],
    }
    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    return sha1(encoded).hexdigest()


def sync_plan_to_history(
    plan: WeeklyMealPlan, preferences: MealPlannerPreferences
) -> dict[str, MealHistoryRecord]:
    """Store meals from a generated weekly plan only once per unique signature."""

    payload = _read_payload()
    plan_signature = build_plan_signature(preferences, plan)
    signatures = list(payload.get("plan_signatures", []))
    if plan_signature in signatures:
        return load_meal_history()

    today = date.today().isoformat()
    meals_payload = payload.setdefault("meals", {})
    for meal in unique_meals_from_plan(plan):
        existing = meals_payload.get(meal.key, {})
        meals_payload[meal.key] = {
            "name": meal.name,
            "meal_type": meal.meal_type,
            "seen_count": int(existing.get("seen_count", 0)) + 1,
            "last_planned": today,
            "rating": existing.get("rating"),
        }

    signatures.append(plan_signature)
    payload["plan_signatures"] = signatures[-MAX_SIGNATURES:]
    _write_payload(payload)
    return load_meal_history()


def set_meal_rating(meal_key: str, rating: int) -> dict[str, MealHistoryRecord]:
    """Persist a one-click rating for a meal in the library."""

    payload = _read_payload()
    meal = MEAL_LOOKUP[meal_key]
    meals_payload = payload.setdefault("meals", {})
    existing = meals_payload.get(meal_key, {})
    meals_payload[meal_key] = {
        "name": existing.get("name", meal.name),
        "meal_type": existing.get("meal_type", meal.meal_type),
        "seen_count": int(existing.get("seen_count", 0)),
        "last_planned": existing.get("last_planned", ""),
        "rating": rating,
    }
    _write_payload(payload)
    return load_meal_history()


def sorted_history_records(
    records: dict[str, MealHistoryRecord], meal_type: str = "All"
) -> list[MealHistoryRecord]:
    """Return meal history ordered by rating, then familiarity, then name."""

    filtered_records = [
        record
        for record in records.values()
        if meal_type == "All" or record.meal_type == meal_type.lower()
    ]
    return sorted(
        filtered_records,
        key=lambda record: (
            record.rating is None,
            -(record.rating or 0),
            -record.seen_count,
            record.name,
        ),
    )


def rating_stars(rating: int | None) -> str:
    """Render a simple star representation for display."""

    if rating is None:
        return "Unrated"
    return "★" * rating + "☆" * (5 - rating)


def repeat_label(record: MealHistoryRecord) -> str:
    """Translate a stored rating into a repeat recommendation."""

    if record.rating is None:
        return "Needs a verdict"
    if record.rating >= 5:
        return "Anchor meal"
    if record.rating == 4:
        return "Repeat soon"
    if record.rating == 3:
        return "Keep in rotation"
    if record.rating == 2:
        return "Only if convenient"
    return "Retire it"

"""Meal plan generator.

Selects recipes for each slot in the week, respecting constraints:
- Philip's weekday breakfasts: prep-ahead / portable
- Weekday lunches: wife only (Philip at office)
- Batch dinners Mon-Thu, fresh dinners Fri-Sun
- Avoid recently used recipes, favour well-rated ones
"""

import json
import random
from datetime import date, timedelta

import database as db

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
WEEKDAYS = DAYS[:5]
WEEKEND = DAYS[5:]


def _weight_recipes(
    recipes: list[dict],
    ratings: dict[int, dict],
    recent_ids: set[int],
) -> list[tuple[dict, float]]:
    """Return (recipe, weight) pairs. Higher weight = more likely to be selected."""
    weighted = []
    for r in recipes:
        rid = r["id"]
        # Base weight
        w = 2.0
        # Boost/penalise by rating
        if rid in ratings:
            avg = ratings[rid]["avg_rating"]
            if avg >= 4.5:
                w = 5.0
            elif avg >= 3.5:
                w = 4.0
            elif avg >= 2.5:
                w = 2.0
            elif avg >= 1.5:
                w = 0.5
            else:
                w = 0.0  # disliked — exclude
        # Penalise recently used
        if rid in recent_ids:
            w *= 0.1
        if w > 0:
            weighted.append((r, w))
    return weighted


def _pick(weighted: list[tuple[dict, float]], count: int, exclude_ids: set[int] | None = None) -> list[dict]:
    """Weighted random selection without replacement."""
    if exclude_ids is None:
        exclude_ids = set()
    pool = [(r, w) for r, w in weighted if r["id"] not in exclude_ids]
    selected = []
    for _ in range(count):
        if not pool:
            break
        recipes, weights = zip(*pool)
        chosen = random.choices(recipes, weights=weights, k=1)[0]
        selected.append(chosen)
        pool = [(r, w) for r, w in pool if r["id"] != chosen["id"]]
    return selected


def generate_plan(week_start: str) -> list[dict]:
    """Generate a full week meal plan, returning a list of plan items."""

    prefs = db.get_all_preferences()
    ratings = db.get_all_ratings()
    recent = db.get_recent_recipe_ids(weeks=3)
    office_days = set(json.loads(prefs.get("office_days", "[]")))

    # Load recipe pools
    prep_breakfasts = db.get_all_recipes(meal_type="breakfast", cooking_method="prep-ahead")
    fresh_breakfasts = db.get_all_recipes(meal_type="breakfast", cooking_method="fresh")
    lunches = db.get_all_recipes(meal_type="lunch")
    batch_dinners = db.get_all_recipes(meal_type="dinner", cooking_method="batch")
    fresh_dinners = db.get_all_recipes(meal_type="dinner", cooking_method="fresh")

    # Weight each pool
    w_prep_bk = _weight_recipes(prep_breakfasts, ratings, recent)
    w_fresh_bk = _weight_recipes(fresh_breakfasts, ratings, recent)
    w_lunch = _weight_recipes(lunches, ratings, recent)
    w_batch_din = _weight_recipes(batch_dinners, ratings, recent)
    w_fresh_din = _weight_recipes(fresh_dinners, ratings, recent)

    # ── Select recipes ────────────────────────────────────────────────
    used: set[int] = set()

    # Philip's weekday breakfast: 1 prep-ahead recipe for the whole week
    philip_bk = _pick(w_prep_bk, 1)
    if philip_bk:
        used.add(philip_bk[0]["id"])

    # Wife's weekday breakfast: 2-3 easy recipes (can be prep-ahead or fresh)
    all_bk_weighted = w_prep_bk + w_fresh_bk
    wife_bk_pool = _pick(all_bk_weighted, 3, exclude_ids=used)
    for r in wife_bk_pool:
        used.add(r["id"])

    # Weekend breakfasts: 2 fresh (shared)
    weekend_bk = _pick(w_fresh_bk, 2, exclude_ids=used)
    for r in weekend_bk:
        used.add(r["id"])

    # Weekday lunches for wife: 5 different
    wife_lunches = _pick(w_lunch, 5, exclude_ids=used)
    for r in wife_lunches:
        used.add(r["id"])

    # Weekend lunches (shared): 2
    weekend_lunches = _pick(w_lunch, 2, exclude_ids=used)
    for r in weekend_lunches:
        used.add(r["id"])

    # Batch dinners: 2 recipes × 2 nights each (Mon+Tue, Wed+Thu)
    batch_dins = _pick(w_batch_din, 2, exclude_ids=used)
    for r in batch_dins:
        used.add(r["id"])

    # Fresh dinners: 3 for Fri-Sun
    fresh_dins = _pick(w_fresh_din, 3, exclude_ids=used)

    # ── Assemble plan items ───────────────────────────────────────────
    items: list[dict] = []

    for i, day in enumerate(DAYS):
        is_weekend = day in WEEKEND
        is_office = day in office_days

        # --- Breakfast ---
        if is_weekend:
            idx = WEEKEND.index(day)
            bk_recipe = weekend_bk[idx] if idx < len(weekend_bk) else (weekend_bk[0] if weekend_bk else None)
            if bk_recipe:
                items.append({
                    "day": day,
                    "meal_type": "breakfast",
                    "recipe_id": bk_recipe["id"],
                    "servings": 2,
                    "person": "both",
                    "notes": "Weekend breakfast",
                })
        else:
            # Philip's prep-ahead breakfast
            if philip_bk:
                items.append({
                    "day": day,
                    "meal_type": "breakfast",
                    "recipe_id": philip_bk[0]["id"],
                    "servings": 1,
                    "person": "philip",
                    "notes": "Prep-ahead (grab and go)" if is_office else "",
                })
            # Wife's breakfast
            wd_idx = WEEKDAYS.index(day)
            wife_recipe = wife_bk_pool[wd_idx % len(wife_bk_pool)] if wife_bk_pool else None
            if wife_recipe:
                items.append({
                    "day": day,
                    "meal_type": "breakfast",
                    "recipe_id": wife_recipe["id"],
                    "servings": 1,
                    "person": "wife",
                    "notes": "",
                })

        # --- Lunch ---
        if is_weekend:
            idx = WEEKEND.index(day)
            lunch_recipe = weekend_lunches[idx] if idx < len(weekend_lunches) else None
            if lunch_recipe:
                items.append({
                    "day": day,
                    "meal_type": "lunch",
                    "recipe_id": lunch_recipe["id"],
                    "servings": 2,
                    "person": "both",
                    "notes": "Weekend lunch",
                })
        else:
            wd_idx = WEEKDAYS.index(day)
            lunch_recipe = wife_lunches[wd_idx] if wd_idx < len(wife_lunches) else None
            if lunch_recipe:
                items.append({
                    "day": day,
                    "meal_type": "lunch",
                    "recipe_id": lunch_recipe["id"],
                    "servings": 1,
                    "person": "wife",
                    "notes": "Philip at office" if is_office else "",
                })

        # --- Dinner ---
        if day == "friday":
            din_recipe = fresh_dins[0] if fresh_dins else None
            if din_recipe:
                items.append({
                    "day": day,
                    "meal_type": "dinner",
                    "recipe_id": din_recipe["id"],
                    "servings": 2,
                    "person": "both",
                    "notes": "Fresh (Friday night)",
                })
        elif is_weekend:
            idx = WEEKEND.index(day) + 1  # +1 because Friday took index 0
            din_recipe = fresh_dins[idx] if idx < len(fresh_dins) else None
            if din_recipe:
                items.append({
                    "day": day,
                    "meal_type": "dinner",
                    "recipe_id": din_recipe["id"],
                    "servings": 2,
                    "person": "both",
                    "notes": "Fresh (weekend)",
                })
        else:
            # Mon+Tue → batch 0, Wed+Thu → batch 1
            wd_idx = WEEKDAYS.index(day)
            batch_idx = wd_idx // 2
            din_recipe = batch_dins[batch_idx] if batch_idx < len(batch_dins) else None
            if din_recipe:
                items.append({
                    "day": day,
                    "meal_type": "dinner",
                    "recipe_id": din_recipe["id"],
                    "servings": 2,
                    "person": "both",
                    "notes": "Batch-cooked (made Sunday)" if wd_idx < 2 else "Batch-cooked",
                })

    return items


def get_alternatives(meal_type: str, cooking_method: str | None = None, exclude_id: int | None = None) -> list[dict]:
    """Get alternative recipes for swapping a meal."""
    recipes = db.get_all_recipes(meal_type=meal_type, cooking_method=cooking_method)
    if exclude_id:
        recipes = [r for r in recipes if r["id"] != exclude_id]
    return recipes


def get_next_monday(from_date: date | None = None) -> str:
    """Return the next Monday as YYYY-MM-DD."""
    d = from_date or date.today()
    days_ahead = (7 - d.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return (d + timedelta(days=days_ahead)).isoformat()

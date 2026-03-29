"""Planning logic for generating a weekly household meal plan."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Literal

from meal_planning.catalog import (
    BREAKFAST_OPTIONS,
    DINNER_OPTIONS,
    LUNCH_OPTIONS,
    Meal,
    get_meal_details,
)

WEEK_DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
HOSTING_DAYS = ("Saturday", "Sunday")
VARIETY_BONUS = {"Calm": 0, "Balanced": 1, "High": 2}


@dataclass(frozen=True)
class MealPlannerPreferences:
    """Inputs that influence the weekly meal plan."""

    office_days: int = 4
    weekly_budget_gbp: float = 110.0
    hosted_dinners: int = 0
    guests_per_hosted_dinner: int = 2
    nutrition_focus: bool = True
    variety_mode: Literal["Calm", "Balanced", "High"] = "Balanced"
    week_index: int = 0
    adults: int = 2
    commuter_breakfasts: int = 5


@dataclass(frozen=True)
class PlannedMeal:
    """One scheduled meal instance within the generated plan."""

    slot: str
    meal: Meal
    servings: int
    notes: str = ""


@dataclass(frozen=True)
class DailyMealSlot:
    """A day-specific meal assignment derived from a batch plan."""

    meal: Meal
    servings: int
    batch_name: str
    note: str


@dataclass(frozen=True)
class DailyMealPlan:
    """The day-by-day schedule shown in the weekly board."""

    day: str
    breakfast: DailyMealSlot
    lunch: DailyMealSlot
    dinner: DailyMealSlot


@dataclass(frozen=True)
class ShoppingListItem:
    """Aggregated shopping list line item."""

    name: str
    quantity: float
    unit: str


@dataclass(frozen=True)
class WeeklyMealPlan:
    """Complete generated weekly plan with shopping list and metrics."""

    breakfasts: tuple[PlannedMeal, ...]
    lunches: tuple[PlannedMeal, ...]
    dinners: tuple[PlannedMeal, ...]
    shopping_list: dict[str, tuple[ShoppingListItem, ...]]
    estimated_cost_gbp: float
    home_lunch_portions: int
    budget_status: str


def _rotated(meals: tuple[Meal, ...], seed: int) -> list[Meal]:
    """Rotate catalogue order so each week starts from a different point."""

    if not meals:
        return []
    offset = seed % len(meals)
    return list(meals[offset:]) + list(meals[:offset])


def _budget_cost_weight(preferences: MealPlannerPreferences) -> float:
    """Return stronger cost penalties when the weekly budget is tighter."""

    if preferences.weekly_budget_gbp <= 80:
        return 1.2
    if preferences.weekly_budget_gbp <= 110:
        return 0.9
    if preferences.weekly_budget_gbp <= 140:
        return 0.6
    return 0.35


def _meal_score(
    meal: Meal,
    preferences: MealPlannerPreferences,
    *,
    rotation_index: int,
    hosting_required: bool = False,
    breakfast_required: bool = False,
) -> tuple[float, int]:
    """Score a meal according to current constraints and heuristics."""

    score = float(rotation_index) * 0.15

    if hosting_required:
        score += 5.0 if meal.hosting_friendly else -10.0
    elif meal.hosting_friendly:
        score -= 0.4

    if breakfast_required:
        score += 2.0 if meal.make_ahead else -6.0

    if preferences.nutrition_focus and meal.nutrition_focus:
        score += 2.5

    score += VARIETY_BONUS[preferences.variety_mode]
    score += meal.protein_g / 18
    score -= meal.estimated_cost_gbp * _budget_cost_weight(preferences)
    return (-score, rotation_index)


def _pick_unique_meals(
    meals: tuple[Meal, ...],
    count: int,
    preferences: MealPlannerPreferences,
    *,
    seed_offset: int,
    hosting_required: bool = False,
    breakfast_required: bool = False,
    exclude_keys: set[str] | None = None,
) -> list[Meal]:
    """Select unique meals with week rotation and simple scoring rules."""

    exclude_keys = exclude_keys or set()
    rotated = _rotated(meals, preferences.week_index + seed_offset)
    ranked = sorted(
        [meal for meal in rotated if meal.key not in exclude_keys],
        key=lambda meal: _meal_score(
            meal,
            preferences,
            rotation_index=rotated.index(meal),
            hosting_required=hosting_required,
            breakfast_required=breakfast_required,
        ),
    )

    picked: list[Meal] = []
    for meal in ranked:
        if hosting_required and not meal.hosting_friendly:
            continue
        if breakfast_required and not meal.make_ahead:
            continue
        picked.append(meal)
        if len(picked) == count:
            break

    if len(picked) < count:
        fallback_pool = [meal for meal in rotated if meal.key not in exclude_keys]
        for meal in fallback_pool:
            if meal not in picked:
                picked.append(meal)
            if len(picked) == count:
                break

    return picked[:count]


def _contiguous_day_groups(total_days: int, group_count: int) -> tuple[tuple[int, ...], ...]:
    """Split a run of days into compact contiguous groups."""

    base_size = total_days // group_count
    remainder = total_days % group_count
    groups: list[tuple[int, ...]] = []
    start = 0

    for index in range(group_count):
        size = base_size + (1 if index < remainder else 0)
        groups.append(tuple(range(start, start + size)))
        start += size

    return tuple(groups)


def _format_day_range(day_indices: tuple[int, ...]) -> str:
    """Format a contiguous set of day indices as a readable range."""

    first_day = WEEK_DAYS[day_indices[0]]
    last_day = WEEK_DAYS[day_indices[-1]]
    if first_day == last_day:
        return first_day
    return f"{first_day} to {last_day}"


def _daily_home_lunch_portions(preferences: MealPlannerPreferences) -> tuple[int, ...]:
    """Return lunch demand for each day of the week."""

    portions: list[int] = []
    for index in range(len(WEEK_DAYS)):
        if index < 5:
            user_home = index >= preferences.office_days
        else:
            user_home = True
        portions.append(1 + int(user_home))
    return tuple(portions)


def _build_breakfast_plan(preferences: MealPlannerPreferences) -> tuple[PlannedMeal, ...]:
    """Create a commuter-focused breakfast plan plus one weekend family breakfast."""

    first_batch = max(1, (preferences.commuter_breakfasts + 1) // 2)
    second_batch = max(0, preferences.commuter_breakfasts - first_batch)

    commuter_meals = _pick_unique_meals(
        BREAKFAST_OPTIONS,
        count=2,
        preferences=preferences,
        seed_offset=0,
        breakfast_required=True,
    )
    breakfast_plan = [
        PlannedMeal(
            slot="Weekday breakfast prep A",
            meal=commuter_meals[0],
            servings=first_batch,
            notes="Portable batch for the first part of the working week.",
        ),
        PlannedMeal(
            slot="Weekday breakfast prep B",
            meal=commuter_meals[1],
            servings=second_batch,
            notes="Second batch to stop breakfast fatigue by Thursday.",
        ),
    ]

    weekend_meal = _pick_unique_meals(
        BREAKFAST_OPTIONS,
        count=1,
        preferences=preferences,
        seed_offset=2,
        exclude_keys={meal.key for meal in commuter_meals},
    )[0]
    breakfast_plan.append(
        PlannedMeal(
            slot="Weekend breakfast",
            meal=weekend_meal,
            servings=preferences.adults * 2,
            notes="One relaxed breakfast recipe for Saturday and Sunday.",
        )
    )
    return tuple(breakfast_plan)


def _build_lunch_plan(preferences: MealPlannerPreferences) -> tuple[PlannedMeal, ...]:
    """Create batch lunches for the at-home lunches needed that week."""

    daily_portions = _daily_home_lunch_portions(preferences)
    home_lunch_portions = sum(daily_portions)
    meal_count = 3 if home_lunch_portions >= 9 else 2
    lunch_meals = _pick_unique_meals(
        LUNCH_OPTIONS,
        count=meal_count,
        preferences=preferences,
        seed_offset=4,
    )
    day_groups = _contiguous_day_groups(len(WEEK_DAYS), meal_count)

    lunch_plan: list[PlannedMeal] = []
    for index, meal in enumerate(lunch_meals):
        day_group = day_groups[index]
        servings = sum(daily_portions[day_index] for day_index in day_group)
        lunch_plan.append(
            PlannedMeal(
                slot=f"Batch lunch {index + 1}",
                meal=meal,
                servings=servings,
                notes=f"Covers {_format_day_range(day_group)} lunches.",
            )
        )

    return tuple(lunch_plan)


def _hosting_slots(preferences: MealPlannerPreferences) -> dict[str, int]:
    """Map hosted weekend dinners to the number of servings they need."""

    slots: dict[str, int] = {}
    hosted_days = HOSTING_DAYS[: preferences.hosted_dinners]
    for day in hosted_days:
        slots[day] = preferences.adults + preferences.guests_per_hosted_dinner
    return slots


def _regular_dinner_servings(meal: Meal, preferences: MealPlannerPreferences) -> int:
    """Regular dinners default to household servings only."""

    if preferences.variety_mode == "Calm" and meal.base_servings >= 4:
        return 3
    return preferences.adults


def _build_dinner_plan(preferences: MealPlannerPreferences) -> tuple[PlannedMeal, ...]:
    """Create a seven-day dinner plan with optional hosted weekend meals."""

    hosting_slots = _hosting_slots(preferences)
    used_keys: set[str] = set()
    dinners: list[PlannedMeal] = []

    hosting_meals = _pick_unique_meals(
        DINNER_OPTIONS,
        count=len(hosting_slots),
        preferences=preferences,
        seed_offset=6,
        hosting_required=True,
    )
    hosting_meals_by_day = dict(zip(hosting_slots, hosting_meals, strict=False))
    used_keys.update(meal.key for meal in hosting_meals)

    regular_meals = _pick_unique_meals(
        DINNER_OPTIONS,
        count=len(WEEK_DAYS) - len(hosting_slots),
        preferences=preferences,
        seed_offset=10,
        exclude_keys=used_keys,
    )
    regular_iter = iter(regular_meals)

    for day in WEEK_DAYS:
        if day in hosting_slots:
            meal = hosting_meals_by_day[day]
            dinners.append(
                PlannedMeal(
                    slot=f"{day} dinner",
                    meal=meal,
                    servings=hosting_slots[day],
                    notes="Hosting-friendly dinner with enough flex for guests.",
                )
            )
            continue

        meal = next(regular_iter)
        dinners.append(
            PlannedMeal(
                slot=f"{day} dinner",
                meal=meal,
                servings=_regular_dinner_servings(meal, preferences),
                notes="Standard household dinner slot.",
            )
        )

    return tuple(dinners)


def _aggregate_shopping_list(planned_meals: tuple[PlannedMeal, ...]) -> dict[str, tuple[ShoppingListItem, ...]]:
    """Aggregate ingredients across the full week into category groups."""

    grouped: dict[str, dict[tuple[str, str], float]] = defaultdict(lambda: defaultdict(float))

    for planned_meal in planned_meals:
        scale = planned_meal.servings / planned_meal.meal.base_servings
        for ingredient in planned_meal.meal.ingredients:
            grouped[ingredient.category][(ingredient.name, ingredient.unit)] += (
                ingredient.quantity * scale
            )

    shopping_list: dict[str, tuple[ShoppingListItem, ...]] = {}
    for category in sorted(grouped):
        items = [
            ShoppingListItem(name=name, unit=unit, quantity=quantity)
            for (name, unit), quantity in sorted(
                grouped[category].items(), key=lambda item: item[0][0]
            )
        ]
        shopping_list[category] = tuple(items)
    return shopping_list


def _estimated_cost(planned_meals: tuple[PlannedMeal, ...]) -> float:
    """Estimate the weekly spend from planned servings."""

    return round(
        sum(
            planned_meal.meal.estimated_cost_gbp * planned_meal.servings
            for planned_meal in planned_meals
        ),
        2,
    )


def _budget_status(preferences: MealPlannerPreferences, estimated_cost_gbp: float) -> str:
    """Describe how the estimated cost compares with budget."""

    if estimated_cost_gbp <= preferences.weekly_budget_gbp * 0.95:
        return "Comfortably inside budget"
    if estimated_cost_gbp <= preferences.weekly_budget_gbp * 1.05:
        return "Right on budget"
    return "Above budget - swap one premium dinner for a cheaper batch meal"


def generate_weekly_plan(preferences: MealPlannerPreferences) -> WeeklyMealPlan:
    """Generate a weekly meal plan and shopping list for the household."""

    breakfasts = _build_breakfast_plan(preferences)
    lunches = _build_lunch_plan(preferences)
    dinners = _build_dinner_plan(preferences)

    all_meals = breakfasts + lunches + dinners
    estimated_cost_gbp = _estimated_cost(all_meals)
    return WeeklyMealPlan(
        breakfasts=breakfasts,
        lunches=lunches,
        dinners=dinners,
        shopping_list=_aggregate_shopping_list(all_meals),
        estimated_cost_gbp=estimated_cost_gbp,
        home_lunch_portions=sum(planned_meal.servings for planned_meal in lunches),
        budget_status=_budget_status(preferences, estimated_cost_gbp),
    )


def build_daily_meal_schedule(
    plan: WeeklyMealPlan, preferences: MealPlannerPreferences
) -> tuple[DailyMealPlan, ...]:
    """Expand the batch plan into a calendar-style weekly schedule."""

    weekday_breakfasts: list[DailyMealSlot] = []
    for planned_breakfast in plan.breakfasts[:2]:
        for _ in range(planned_breakfast.servings):
            weekday_breakfasts.append(
                DailyMealSlot(
                    meal=planned_breakfast.meal,
                    servings=1,
                    batch_name=planned_breakfast.slot,
                    note=planned_breakfast.notes,
                )
            )

    fallback_breakfast = plan.breakfasts[1] if len(plan.breakfasts) > 1 else plan.breakfasts[0]
    while len(weekday_breakfasts) < 5:
        weekday_breakfasts.append(
            DailyMealSlot(
                meal=fallback_breakfast.meal,
                servings=1,
                batch_name=fallback_breakfast.slot,
                note=fallback_breakfast.notes,
            )
        )

    daily_lunch_portions = _daily_home_lunch_portions(preferences)
    lunch_groups = _contiguous_day_groups(len(WEEK_DAYS), len(plan.lunches))
    lunch_slots_by_day: dict[int, DailyMealSlot] = {}
    for day_group, planned_lunch in zip(lunch_groups, plan.lunches, strict=False):
        for day_index in day_group:
            lunch_slots_by_day[day_index] = DailyMealSlot(
                meal=planned_lunch.meal,
                servings=daily_lunch_portions[day_index],
                batch_name=planned_lunch.slot,
                note=planned_lunch.notes,
            )

    weekend_breakfast = plan.breakfasts[-1]
    schedule: list[DailyMealPlan] = []
    for day_index, planned_dinner in enumerate(plan.dinners):
        if day_index < 5:
            breakfast_slot = weekday_breakfasts[day_index]
        else:
            breakfast_slot = DailyMealSlot(
                meal=weekend_breakfast.meal,
                servings=preferences.adults,
                batch_name=weekend_breakfast.slot,
                note=weekend_breakfast.notes,
            )

        schedule.append(
            DailyMealPlan(
                day=WEEK_DAYS[day_index],
                breakfast=breakfast_slot,
                lunch=lunch_slots_by_day[day_index],
                dinner=DailyMealSlot(
                    meal=planned_dinner.meal,
                    servings=planned_dinner.servings,
                    batch_name=planned_dinner.slot,
                    note=planned_dinner.notes,
                ),
            )
        )

    return tuple(schedule)


def unique_meals_from_plan(plan: WeeklyMealPlan) -> tuple[Meal, ...]:
    """Return the unique meals in the order they appear through the week."""

    seen_keys: set[str] = set()
    ordered_meals: list[Meal] = []
    for planned_meal in plan.breakfasts + plan.lunches + plan.dinners:
        if planned_meal.meal.key in seen_keys:
            continue
        seen_keys.add(planned_meal.meal.key)
        ordered_meals.append(planned_meal.meal)
    return tuple(ordered_meals)


def estimate_kitchen_load_hours(plan: WeeklyMealPlan) -> float:
    """Estimate total kitchen time for the week's planned meals."""

    total_minutes = 0
    for planned_meal in plan.breakfasts + plan.lunches + plan.dinners:
        details = get_meal_details(planned_meal.meal.key)
        total_minutes += details.prep_minutes + details.cook_minutes
    return round(total_minutes / 60, 1)


def shopping_list_rows(plan: WeeklyMealPlan) -> tuple[dict[str, str], ...]:
    """Flatten the shopping list into rows for tabular display."""

    rows: list[dict[str, str]] = []
    for category, items in plan.shopping_list.items():
        for item in items:
            rows.append(
                {
                    "Category": category,
                    "Item": item.name,
                    "Quantity": f"{format_quantity(item.quantity)} {item.unit}".strip(),
                }
            )
    return tuple(rows)


def format_quantity(quantity: float) -> str:
    """Format shopping quantities cleanly for display."""

    rounded = round(quantity, 1)
    if abs(rounded - round(rounded)) < 0.05:
        return str(int(round(rounded)))
    return f"{rounded:.1f}".rstrip("0").rstrip(".")


def shopping_list_as_text(plan: WeeklyMealPlan) -> str:
    """Render the shopping list as plain text for download or copy/paste."""

    lines = ["Weekly shopping list"]
    for category, items in plan.shopping_list.items():
        lines.append("")
        lines.append(category)
        for item in items:
            lines.append(f"- {format_quantity(item.quantity)} {item.unit} {item.name}".strip())
    return "\n".join(lines)

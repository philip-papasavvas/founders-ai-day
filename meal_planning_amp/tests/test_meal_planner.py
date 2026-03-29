"""Tests for the weekly meal planning engine."""

from meal_planning import MealPlannerPreferences, generate_weekly_plan, shopping_list_as_text
from meal_planning.pdf_export import build_weekly_plan_pdf
from meal_planning.planner import (
    WEEK_DAYS,
    build_daily_meal_schedule,
    estimate_kitchen_load_hours,
    shopping_list_rows,
)


def test_generate_weekly_plan_matches_household_routine() -> None:
    """Hosted dinners and lunch counts should reflect the stated household inputs."""

    plan = generate_weekly_plan(
        MealPlannerPreferences(
            office_days=5,
            hosted_dinners=2,
            guests_per_hosted_dinner=2,
            weekly_budget_gbp=130,
            nutrition_focus=True,
            variety_mode="Balanced",
            week_index=1,
        )
    )

    assert len(plan.breakfasts) == 3
    assert sum(planned.servings for planned in plan.breakfasts[:2]) == 5
    assert plan.home_lunch_portions == 9
    assert len(plan.dinners) == 7

    hosted_dinners = [planned for planned in plan.dinners if planned.meal.hosting_friendly]
    assert len(hosted_dinners) == 2
    assert all(planned.servings == 4 for planned in hosted_dinners)

    assert plan.estimated_cost_gbp > 0
    assert "Weekly shopping list" in shopping_list_as_text(plan)


def test_daily_schedule_is_explicit_for_each_day() -> None:
    """The daily board should map the batch plan onto all seven days clearly."""

    preferences = MealPlannerPreferences(office_days=4, hosted_dinners=1, week_index=2)
    plan = generate_weekly_plan(preferences)
    daily_schedule = build_daily_meal_schedule(plan, preferences)

    assert len(daily_schedule) == 7
    assert [day.day for day in daily_schedule] == list(WEEK_DAYS)
    assert daily_schedule[4].lunch.servings == 2
    assert daily_schedule[5].breakfast.servings == 2
    assert daily_schedule[5].dinner.servings == 4


def test_pdf_export_and_compact_views_are_generated() -> None:
    """Compact shopping rows and PDF export should both be available for the UI."""

    preferences = MealPlannerPreferences(office_days=3, weekly_budget_gbp=120, week_index=3)
    plan = generate_weekly_plan(preferences)
    daily_schedule = build_daily_meal_schedule(plan, preferences)
    pdf_bytes = build_weekly_plan_pdf(plan, preferences, daily_schedule)

    assert shopping_list_rows(plan)
    assert estimate_kitchen_load_hours(plan) > 0
    assert pdf_bytes.startswith(b"%PDF-1.4")
    assert b"Mitchell family meal plan" in pdf_bytes

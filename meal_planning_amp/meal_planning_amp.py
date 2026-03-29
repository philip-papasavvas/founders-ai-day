"""Streamlit app for planning weekly meals and shopping for a household."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from meal_planning.catalog import MEAL_LOOKUP
from meal_planning.catalog import get_meal_details
from meal_planning.history import (
    load_meal_history,
    set_meal_rating,
    sorted_history_records,
    sync_plan_to_history,
)
from meal_planning.pdf_export import build_weekly_plan_pdf
from meal_planning.planner import (
    MealPlannerPreferences,
    build_daily_meal_schedule,
    estimate_kitchen_load_hours,
    generate_weekly_plan,
    shopping_list_as_text,
    shopping_list_rows,
    unique_meals_from_plan,
)
from meal_planning.ui import (
    inject_page_css,
    render_day_card,
    render_hero,
    render_library_card,
    render_recipe_card,
    render_stat_card,
)


def _render_weekly_board(daily_schedule, ratings: dict[str, int | None]) -> None:
    """Render the seven-day weekly board in a compact grid."""

    first_row = st.columns(4)
    for index, day_plan in enumerate(daily_schedule[:4]):
        with first_row[index]:
            render_day_card(day_plan, ratings)

    second_row = st.columns(3)
    for index, day_plan in enumerate(daily_schedule[4:]):
        with second_row[index]:
            render_day_card(day_plan, ratings)


def _render_recipe_section(plan) -> None:
    """Render recipe summaries grouped by meal type."""

    grouped = {"breakfast": [], "lunch": [], "dinner": []}
    for planned_meal in plan.breakfasts + plan.lunches + plan.dinners:
        grouped[planned_meal.meal.meal_type].append(planned_meal)

    breakfast_tab, lunch_tab, dinner_tab = st.tabs(["Breakfast", "Lunch", "Dinner"])
    for tab, meal_type in zip(
        (breakfast_tab, lunch_tab, dinner_tab),
        ("breakfast", "lunch", "dinner"),
        strict=False,
    ):
        with tab:
            meal_columns = st.columns(2)
            for index, planned_meal in enumerate(grouped[meal_type]):
                with meal_columns[index % 2]:
                    render_recipe_card(
                        meal=planned_meal.meal,
                        servings_label=f"{planned_meal.servings} portions",
                        source_label=planned_meal.slot,
                    )


def _render_shopping_table(plan, pdf_bytes: bytes) -> None:
    """Render the compact shopping table with downloads."""

    rows = shopping_list_rows(plan)
    shopping_df = pd.DataFrame(rows)
    summary_cols = st.columns([1.2, 1.2, 1])
    with summary_cols[0]:
        st.caption(
            f"{len(shopping_df)} line items across {shopping_df['Category'].nunique()} grocery zones."
        )
    with summary_cols[1]:
        st.download_button(
            label="Export week as PDF",
            data=pdf_bytes,
            file_name="mitchell-family-meal-plan.pdf",
            mime="application/pdf",
        )
    with summary_cols[2]:
        st.download_button(
            label="Download shopping text",
            data=shopping_list_as_text(plan),
            file_name="weekly-shopping-list.txt",
            mime="text/plain",
        )

    st.dataframe(shopping_df, hide_index=True, use_container_width=True, height=500)


def _render_library(history_records) -> None:
    """Render the persistent meal library with one-click ratings."""

    st.caption("One click is enough here: 1 means retire it, 5 means make it part of the family canon.")
    selected_type = st.selectbox(
        "Filter meals",
        options=["All", "Breakfast", "Lunch", "Dinner"],
        index=0,
    )

    ordered_records = sorted_history_records(history_records, meal_type=selected_type)
    if not ordered_records:
        st.info("No saved meals in the library yet. Generate a week and they will appear here.")
        return

    for record in ordered_records:
        summary_col, action_col = st.columns([1.3, 1.7])
        with summary_col:
            render_library_card(record)
        with action_col:
            button_cols = st.columns(5)
            for rating, button_col in enumerate(button_cols, start=1):
                with button_col:
                    if st.button(str(rating), key=f"rate_{record.key}_{rating}", use_container_width=True):
                        set_meal_rating(record.key, rating)
                        st.rerun()

            meal = MEAL_LOOKUP[record.key]
            details = get_meal_details(record.key)
            st.caption(meal.description)
            st.caption("Method: " + " -> ".join(details.method_summary[:2]))
            with st.expander("See recipe summary", expanded=False):
                render_recipe_card(
                    meal=meal,
                    servings_label=f"Seen {record.seen_count} week(s)",
                    source_label="Meal library",
                )


def main() -> None:
    """Run the household meal planner app."""

    st.set_page_config(
        page_title="Meal Planning Amp",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_page_css()

    if "meal_week_index" not in st.session_state:
        st.session_state["meal_week_index"] = 0

    render_hero()
    st.caption(
        "What the old version got wrong: the pills carried too much meaning, the week itself was hard to read, and the shopping list wasted space. This version fixes those first."
    )

    controls_a, controls_b, controls_c, controls_d = st.columns(4)
    with controls_a:
        office_days = st.slider("Office days", min_value=0, max_value=5, value=4)
        variety_mode = st.selectbox("Variety", options=["Calm", "Balanced", "High"], index=1)
    with controls_b:
        weekly_budget_gbp = st.number_input(
            "Budget (GBP)", min_value=50, max_value=250, value=115, step=5
        )
        nutrition_focus = st.toggle("Nutrient-dense bias", value=True)
    with controls_c:
        hosted_dinners = st.slider("Hosted dinners", min_value=0, max_value=2, value=0)
        guests_per_hosted_dinner = st.slider("Guests each", min_value=1, max_value=6, value=2)
    with controls_d:
        st.write("")
        if st.button("Rotate to another week", use_container_width=True):
            st.session_state["meal_week_index"] += 1
        st.caption(
            f"Rotation seed {st.session_state['meal_week_index']} keeps the rhythm but changes the menu."
        )

    preferences = MealPlannerPreferences(
        office_days=office_days,
        weekly_budget_gbp=float(weekly_budget_gbp),
        hosted_dinners=hosted_dinners,
        guests_per_hosted_dinner=guests_per_hosted_dinner,
        nutrition_focus=nutrition_focus,
        variety_mode=variety_mode,
        week_index=st.session_state["meal_week_index"],
    )
    plan = generate_weekly_plan(preferences)
    daily_schedule = build_daily_meal_schedule(plan, preferences)
    history_records = sync_plan_to_history(plan, preferences)
    ratings = {meal_key: record.rating for meal_key, record in history_records.items()}
    pdf_bytes = build_weekly_plan_pdf(plan, preferences, daily_schedule)

    top_rated_count = sum(
        1 for meal in unique_meals_from_plan(plan) if ratings.get(meal.key, 0) and ratings.get(meal.key, 0) >= 4
    )

    metric_cols = st.columns(5)
    with metric_cols[0]:
        render_stat_card("Estimated spend", f"GBP {plan.estimated_cost_gbp:.0f}", plan.budget_status)
    with metric_cols[1]:
        render_stat_card(
            "Kitchen load",
            f"{estimate_kitchen_load_hours(plan):.1f}h",
            "Total prep and cook time across the batched week.",
        )
    with metric_cols[2]:
        render_stat_card(
            "At-home lunches",
            str(plan.home_lunch_portions),
            "Mat leave lunches plus the days you are home.",
        )
    with metric_cols[3]:
        render_stat_card(
            "Hosted dinners",
            str(hosted_dinners),
            "Weekend dinners scaled for guests rather than guesswork.",
        )
    with metric_cols[4]:
        render_stat_card(
            "Loved meals",
            str(top_rated_count),
            "Meals in this week already rated 4 or 5 in the library.",
        )

    weekly_tab, recipe_tab, shopping_tab, library_tab = st.tabs(
        ["Weekly pattern", "Recipes & methods", "Shopping list", "Meal library"]
    )

    with weekly_tab:
        st.caption(
            "This is the view that matters most on the go: every day is explicit, so you can see the actual household plan instead of a pile of batches."
        )
        _render_weekly_board(daily_schedule, ratings)

    with recipe_tab:
        st.caption(
            "Each generated meal now carries a short method so you can remember how it is meant to come together without opening another notes app."
        )
        _render_recipe_section(plan)

    with shopping_tab:
        st.caption(
            "Compact by design: one table, fast export, and enough context to send to your phone as a PDF attachment."
        )
        _render_shopping_table(plan, pdf_bytes)

    with library_tab:
        _render_library(load_meal_history())


if __name__ == "__main__":
    main()

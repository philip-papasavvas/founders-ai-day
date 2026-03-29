"""Presentation helpers for the Mitchell family meal planner."""

from __future__ import annotations

from html import escape

import streamlit as st

from meal_planning.catalog import Meal, get_meal_details
from meal_planning.history import MealHistoryRecord, rating_stars, repeat_label
from meal_planning.planner import DailyMealPlan


def inject_page_css() -> None:
    """Apply the celebratory scrapbook styling for the meal planner."""

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

        :root {
            --cream: #fff7f7;
            --cream-strong: #fff1f4;
            --blush: #ffdbe6;
            --petal: #f7bfd0;
            --berry: #bf4f77;
            --plum: #4f2740;
            --rosewood: #7f3557;
            --sage: #dcebd8;
            --gold: #eabf6a;
            --ink: #34232d;
            --muted: #735865;
            --line: rgba(127, 53, 87, 0.14);
            --shadow: 0 18px 38px rgba(105, 56, 79, 0.12);
        }

        .stApp {
            background:
                radial-gradient(circle at top right, rgba(191, 79, 119, 0.15), transparent 26%),
                radial-gradient(circle at 15% 0%, rgba(255, 209, 220, 0.6), transparent 20%),
                radial-gradient(circle at bottom left, rgba(220, 235, 216, 0.7), transparent 24%),
                linear-gradient(180deg, #fff8fb 0%, #fff3f6 100%);
            color: var(--ink);
            font-family: 'IBM Plex Sans', sans-serif;
        }

        .block-container {
            max-width: 1440px;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3 {
            font-family: 'Cormorant Garamond', serif;
            color: var(--plum);
            letter-spacing: -0.02em;
        }

        .hero-shell {
            position: relative;
            overflow: hidden;
            background: linear-gradient(135deg, rgba(255,247,247,0.96), rgba(255,236,242,0.92));
            border: 1px solid var(--line);
            border-radius: 28px;
            padding: 1.35rem 1.45rem 1.15rem;
            box-shadow: var(--shadow);
            margin-bottom: 0.85rem;
        }

        .hero-shell::before,
        .hero-shell::after {
            content: '';
            position: absolute;
            border-radius: 999px;
            pointer-events: none;
        }

        .hero-shell::before {
            width: 240px;
            height: 240px;
            right: -80px;
            top: -100px;
            background: radial-gradient(circle, rgba(191,79,119,0.18), rgba(191,79,119,0));
        }

        .hero-shell::after {
            width: 200px;
            height: 200px;
            left: -70px;
            bottom: -120px;
            background: radial-gradient(circle, rgba(220,235,216,0.9), rgba(220,235,216,0));
        }

        .hero-kicker {
            text-transform: uppercase;
            letter-spacing: 0.18em;
            font-size: 0.72rem;
            font-weight: 700;
            color: var(--berry);
            margin-bottom: 0.35rem;
        }

        .hero-title {
            font-family: 'Cormorant Garamond', serif;
            font-size: 3rem;
            line-height: 0.92;
            margin: 0;
            color: var(--plum);
            max-width: 10ch;
        }

        .hero-copy {
            max-width: 65rem;
            margin-top: 0.65rem;
            margin-bottom: 0.4rem;
            line-height: 1.45;
            color: var(--muted);
            font-size: 0.97rem;
        }

        .hero-ribbon {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: rgba(191, 79, 119, 0.10);
            color: var(--rosewood);
            font-size: 0.82rem;
            font-weight: 600;
            margin-top: 0.35rem;
        }

        .stat-card,
        .day-card,
        .recipe-card,
        .library-card {
            background: rgba(255, 251, 252, 0.94);
            border: 1px solid var(--line);
            border-radius: 22px;
            box-shadow: var(--shadow);
        }

        .stat-card {
            padding: 0.9rem 1rem;
            min-height: 116px;
            margin-bottom: 0.65rem;
        }

        .stat-label {
            text-transform: uppercase;
            letter-spacing: 0.13em;
            color: var(--berry);
            font-size: 0.72rem;
            font-weight: 700;
            margin-bottom: 0.45rem;
        }

        .stat-value {
            font-family: 'Cormorant Garamond', serif;
            font-size: 2rem;
            color: var(--plum);
            margin-bottom: 0.2rem;
        }

        .stat-copy {
            color: var(--muted);
            line-height: 1.35;
            font-size: 0.9rem;
        }

        .day-card {
            padding: 0.82rem 0.88rem 0.88rem;
            margin-bottom: 0.75rem;
            min-height: 320px;
        }

        .day-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.7rem;
        }

        .day-title {
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.45rem;
            color: var(--plum);
        }

        .day-stamp {
            font-size: 0.72rem;
            color: var(--berry);
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-weight: 700;
        }

        .slot-card {
            display: grid;
            grid-template-columns: 50px 1fr;
            gap: 0.65rem;
            padding: 0.65rem;
            border-radius: 18px;
            background: rgba(255, 241, 244, 0.72);
            border: 1px solid rgba(191, 79, 119, 0.12);
            margin-bottom: 0.55rem;
        }

        .slot-art {
            width: 50px;
            height: 50px;
            border-radius: 16px;
            display: grid;
            place-items: center;
            font-size: 1.35rem;
            background: linear-gradient(135deg, rgba(255,255,255,0.88), rgba(255, 215, 227, 0.82));
            box-shadow: inset 0 1px 1px rgba(255,255,255,0.85);
        }

        .slot-kind {
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--berry);
            margin-bottom: 0.18rem;
        }

        .slot-title {
            font-size: 0.93rem;
            font-weight: 600;
            color: var(--ink);
            line-height: 1.22;
            margin-bottom: 0.18rem;
        }

        .slot-meta,
        .slot-note {
            font-size: 0.8rem;
            color: var(--muted);
            line-height: 1.28;
        }

        .slot-note {
            margin-top: 0.18rem;
        }

        .recipe-card {
            padding: 0.95rem 1rem;
            margin-bottom: 0.8rem;
        }

        .recipe-top {
            display: grid;
            grid-template-columns: 70px 1fr;
            gap: 0.85rem;
            margin-bottom: 0.6rem;
            align-items: center;
        }

        .recipe-art {
            width: 70px;
            height: 70px;
            border-radius: 22px;
            display: grid;
            place-items: center;
            font-size: 1.9rem;
            background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(255,223,232,0.88));
        }

        .recipe-title {
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.6rem;
            color: var(--plum);
            margin: 0;
            line-height: 1;
        }

        .recipe-subtitle {
            color: var(--muted);
            font-size: 0.87rem;
            margin-top: 0.22rem;
        }

        .recipe-copy {
            color: var(--ink);
            line-height: 1.42;
            font-size: 0.92rem;
            margin-bottom: 0.45rem;
        }

        .method-list {
            margin: 0.45rem 0 0;
            padding-left: 1rem;
            color: var(--ink);
            line-height: 1.42;
            font-size: 0.9rem;
        }

        .recipe-note {
            margin-top: 0.55rem;
            color: var(--rosewood);
            font-size: 0.82rem;
            font-weight: 600;
        }

        .badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
            margin-top: 0.45rem;
        }

        .tiny-badge {
            display: inline-block;
            padding: 0.22rem 0.55rem;
            border-radius: 999px;
            background: rgba(191,79,119,0.10);
            color: var(--rosewood);
            font-size: 0.75rem;
            font-weight: 700;
        }

        .library-card {
            padding: 0.9rem 1rem;
            margin-bottom: 0.75rem;
        }

        .library-title {
            font-size: 1rem;
            font-weight: 700;
            color: var(--ink);
            margin-bottom: 0.12rem;
        }

        .library-meta {
            color: var(--muted);
            font-size: 0.83rem;
            line-height: 1.28;
        }

        .rating-line {
            font-size: 0.82rem;
            color: var(--rosewood);
            font-weight: 700;
            margin-top: 0.3rem;
        }

        .stButton > button,
        .stDownloadButton > button {
            background: linear-gradient(135deg, #bf4f77, #d76f95);
            color: #fff9fb;
            border: 0;
            border-radius: 999px;
            padding: 0.5rem 0.95rem;
            font-weight: 700;
            box-shadow: 0 12px 28px rgba(191, 79, 119, 0.18);
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #a74368, #bf5f84);
            color: #fff9fb;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.35rem;
            margin-bottom: 0.3rem;
        }

        .stTabs [data-baseweb="tab"] {
            background: rgba(255, 244, 248, 0.72);
            border: 1px solid rgba(191, 79, 119, 0.12);
            border-radius: 999px;
            padding: 0.58rem 0.95rem;
        }

        .stTabs [aria-selected="true"] {
            background: rgba(191, 79, 119, 0.10);
            border-color: rgba(191, 79, 119, 0.22);
        }

        [data-testid="stDataFrame"] {
            border-radius: 18px;
            border: 1px solid var(--line);
            overflow: hidden;
            box-shadow: var(--shadow);
        }

        .stCaption {
            color: var(--muted);
        }

        @media (max-width: 900px) {
            .hero-title {
                font-size: 2.2rem;
            }

            .day-card {
                min-height: auto;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    """Render the family-focused hero header."""

    st.markdown(
        """
        <section class="hero-shell">
            <div class="hero-kicker">Mitchell family kitchen club</div>
            <h1 class="hero-title">A pink little planning studio for the week ahead.</h1>
            <p class="hero-copy">
                This version is built for a household about to meet a new little girl: clearer week structure, compact shopping, quicker rating decisions, and recipes that feel like a family system instead of a one-off spreadsheet.
            </p>
            <div class="hero-ribbon">Baby-ready meals · commuter breakfasts · guest-proof weekends</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_stat_card(label: str, value: str, subtitle: str) -> None:
    """Render a compact headline metric card."""

    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">{escape(label)}</div>
            <div class="stat-value">{escape(value)}</div>
            <div class="stat-copy">{escape(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _slot_html(slot_name: str, meal: Meal, servings: int, note: str, rating: int | None) -> str:
    """Render one breakfast/lunch/dinner slot."""

    details = get_meal_details(meal.key)
    rating_markup = escape(rating_stars(rating)) if rating is not None else ""
    return f"""
        <div class="slot-card">
            <div class="slot-art" style="border: 1px solid {escape(details.accent)}33;">{escape(details.visual_emoji)}</div>
            <div>
                <div class="slot-kind">{escape(slot_name)}</div>
                <div class="slot-title">{escape(meal.name)}</div>
                <div class="slot-meta">{servings} portions · {meal.protein_g}g protein {('· ' + rating_markup) if rating_markup else ''}</div>
                <div class="slot-note">{escape(note)}</div>
            </div>
        </div>
    """


def render_day_card(day_plan: DailyMealPlan, ratings: dict[str, int | None]) -> None:
    """Render one day card in the weekly board."""

    st.markdown(
        f"""
        <div class="day-card">
            <div class="day-head">
                <div class="day-title">{escape(day_plan.day)}</div>
                <div class="day-stamp">weekly pattern</div>
            </div>
            {_slot_html('Breakfast', day_plan.breakfast.meal, day_plan.breakfast.servings, day_plan.breakfast.note, ratings.get(day_plan.breakfast.meal.key))}
            {_slot_html('Lunch', day_plan.lunch.meal, day_plan.lunch.servings, day_plan.lunch.note, ratings.get(day_plan.lunch.meal.key))}
            {_slot_html('Dinner', day_plan.dinner.meal, day_plan.dinner.servings, day_plan.dinner.note, ratings.get(day_plan.dinner.meal.key))}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recipe_card(meal: Meal, servings_label: str, source_label: str) -> None:
    """Render a recipe summary card with method highlights."""

    details = get_meal_details(meal.key)
    method_items = "".join(
        f"<li>{escape(step)}</li>" for step in details.method_summary
    )
    tag_badges = "".join(
        f'<span class="tiny-badge">{escape(tag.replace("_", " "))}</span>' for tag in meal.tags[:4]
    )

    st.markdown(
        f"""
        <div class="recipe-card">
            <div class="recipe-top">
                <div class="recipe-art" style="border: 1px solid {escape(details.accent)}33;">{escape(details.visual_emoji)}</div>
                <div>
                    <div class="recipe-title">{escape(meal.name)}</div>
                    <div class="recipe-subtitle">{escape(source_label)} · {escape(servings_label)} · prep {details.prep_minutes}m · cook {details.cook_minutes}m</div>
                </div>
            </div>
            <div class="recipe-copy">{escape(meal.description)}</div>
            <ol class="method-list">{method_items}</ol>
            <div class="recipe-note">Finish: {escape(details.plating_note)}</div>
            <div class="badge-row">{tag_badges}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_library_card(record: MealHistoryRecord) -> None:
    """Render the text summary for a meal library entry."""

    st.markdown(
        f"""
        <div class="library-card">
            <div class="library-title">{escape(record.name)}</div>
            <div class="library-meta">Seen in {record.seen_count} generated week(s) · last planned {escape(record.last_planned or 'not yet saved')}</div>
            <div class="rating-line">{escape(rating_stars(record.rating))} · {escape(repeat_label(record))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

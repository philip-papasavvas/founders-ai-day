"""Preferences — household setup, dietary restrictions, budget."""

import json
import streamlit as st

st.set_page_config(page_title="Preferences", page_icon="\u2699\uFE0F", layout="wide")

from styles import inject_theme, banner
from database import init_db, get_all_preferences, set_preference

inject_theme()
init_db()

banner()
st.markdown("#### \u2699\uFE0F Preferences")

prefs = get_all_preferences()


def _get(key: str, default: str = "") -> str:
    return prefs.get(key, default)


# ── Household ─────────────────────────────────────────────────────────
st.markdown("##### Household")
col1, col2 = st.columns(2)

with col1:
    name1 = st.text_input("Person 1", value=_get("household_name_1", "Philip"), key="name1")
    weight1 = st.number_input("Weight (kg)", value=int(_get("person_1_weight_kg", "75")), key="w1")
    activity1 = st.selectbox(
        "Activity level",
        ["low", "moderate", "high", "very high"],
        index=["low", "moderate", "high", "very high"].index(_get("person_1_activity", "high")),
        key="act1",
    )

with col2:
    name2 = st.text_input("Person 2", value=_get("household_name_2", "Partner"), key="name2")
    weight2 = st.number_input("Weight (kg)", value=int(_get("person_2_weight_kg", "55")), key="w2")
    activity2 = st.selectbox(
        "Activity level",
        ["low", "moderate", "high", "very high"],
        index=["low", "moderate", "high", "very high"].index(_get("person_2_activity", "moderate")),
        key="act2",
    )
    breastfeeding = st.checkbox(
        "Currently breastfeeding (+500 kcal/day, prioritise iron, calcium, omega-3)",
        value=_get("person_2_breastfeeding", "false") == "true",
    )

# ── Schedule ──────────────────────────────────────────────────────────
st.markdown("##### Work & schedule")
ALL_DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_LABELS = {"monday": "Mon", "tuesday": "Tue", "wednesday": "Wed",
              "thursday": "Thu", "friday": "Fri", "saturday": "Sat", "sunday": "Sun"}

c1, c2, c3 = st.columns(3)
with c1:
    current_office = json.loads(_get("office_days", "[]"))
    office_days = st.multiselect(
        f"{name1}'s office days",
        options=ALL_DAYS, default=current_office,
        format_func=lambda x: DAY_LABELS.get(x, x.title()),
    )
with c2:
    planning_day = st.selectbox(
        "Planning day", options=ALL_DAYS,
        index=ALL_DAYS.index(_get("planning_day", "friday")),
        format_func=lambda x: DAY_LABELS.get(x, x.title()),
    )
with c3:
    delivery_day = st.selectbox(
        "Delivery day", options=ALL_DAYS,
        index=ALL_DAYS.index(_get("delivery_day", "sunday")),
        format_func=lambda x: DAY_LABELS.get(x, x.title()),
    )

# ── Dietary ───────────────────────────────────────────────────────────
st.markdown("##### Dietary")
c1, c2 = st.columns(2)
with c1:
    RESTRICTION_OPTIONS = [
        "vegetarian", "vegan", "gluten-free", "dairy-free",
        "nut-free", "shellfish-free", "low-carb", "halal", "kosher",
    ]
    current_restrictions = json.loads(_get("dietary_restrictions", "[]"))
    restrictions = st.multiselect("Restrictions", RESTRICTION_OPTIONS, default=current_restrictions)
with c2:
    current_disliked = json.loads(_get("disliked_ingredients", "[]"))
    disliked_input = st.text_input(
        "Disliked ingredients (comma-separated)",
        value=", ".join(current_disliked),
    )
    disliked = [x.strip().lower() for x in disliked_input.split(",") if x.strip()]

# ── Meal structure + budget ──────────────────────────────────────────
st.markdown("##### Meal structure & budget")
c1, c2, c3 = st.columns(3)
with c1:
    batch_count = st.slider("Batch dinners/week", 0, 7, int(_get("batch_dinners_per_week", "4")))
with c2:
    st.metric("Fresh dinners/week", 7 - batch_count)
with c3:
    budget = st.number_input("Weekly budget (\u00A3)", 30, 500, int(_get("weekly_budget_gbp", "100")), step=10)

# ── Calorie targets ──────────────────────────────────────────────────
st.markdown("##### Daily targets (computed)")
ACTIVITY_MULT = {"low": 1.4, "moderate": 1.6, "high": 1.8, "very high": 2.0}

bmr1 = 10 * weight1 + 6.25 * 175 - 5 * 32 + 5
tdee1 = bmr1 * ACTIVITY_MULT.get(activity1, 1.6)
bmr2 = 10 * weight2 + 6.25 * 163 - 5 * 32 - 161
tdee2 = bmr2 * ACTIVITY_MULT.get(activity2, 1.6)
if breastfeeding:
    tdee2 += 500

protein1 = weight1 * 1.8
protein2 = weight2 * (1.4 if breastfeeding else 1.2)

c1, c2, c3, c4 = st.columns(4)
c1.metric(f"{name1} TDEE", f"{tdee1:,.0f} kcal")
c2.metric(f"{name1} protein", f"{protein1:.0f}g")
c3.metric(f"{name2} TDEE", f"{tdee2:,.0f} kcal")
c4.metric(f"{name2} protein", f"{protein2:.0f}g")

# ── Save ──────────────────────────────────────────────────────────────
if st.button("\U0001F4BE Save all preferences", type="primary", use_container_width=True):
    for k, v in {
        "household_name_1": name1,
        "household_name_2": name2,
        "person_1_weight_kg": str(weight1),
        "person_2_weight_kg": str(weight2),
        "person_1_activity": activity1,
        "person_2_activity": activity2,
        "person_2_breastfeeding": str(breastfeeding).lower(),
        "office_days": json.dumps(office_days),
        "dietary_restrictions": json.dumps(restrictions),
        "disliked_ingredients": json.dumps(disliked),
        "weekly_budget_gbp": str(budget),
        "batch_dinners_per_week": str(batch_count),
        "fresh_dinners_per_week": str(7 - batch_count),
        "planning_day": planning_day,
        "delivery_day": delivery_day,
    }.items():
        set_preference(k, v)
    st.success("Preferences saved!")

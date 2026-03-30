"""Meal Planning Amp — home page."""

import streamlit as st

st.set_page_config(
    page_title="Meal Planning Amp",
    page_icon="\U0001F380",
    layout="wide",
)

from styles import inject_theme, banner
from database import init_db, get_all_recipes, get_finalized_plans, get_all_ratings

inject_theme()
init_db()

banner()

st.markdown(
    """
**Your weekly workflow:**
1. **Friday** \u2014 Open **Weekly Planner**, answer quick check-in, generate the plan
2. **Tweak** \u2014 Swap any meals you don't fancy
3. **Finalise** \u2014 Lock it in
4. **Shopping List** \u2014 Copy or download the auto-generated list
5. **Sunday** \u2014 Food arrives, batch cook for the week
6. **Rate** \u2014 One-click ratings to improve future suggestions
""",
)

# Quick stats
recipes = get_all_recipes()
plans = get_finalized_plans()
ratings = get_all_ratings()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Recipes", len(recipes))
c2.metric("Weeks planned", len(plans))
c3.metric("Meals rated", sum(r["count"] for r in ratings.values()))
c4.metric(
    "Est. budget",
    f"\u00A3{int(st.session_state.get('budget', 100))}/wk"
    if "budget" in st.session_state
    else "\u00A3100/wk",
)

# Recipe breakdown in compact row
st.markdown("##### Recipe library")
b_count = len([r for r in recipes if r["meal_type"] == "breakfast"])
l_count = len([r for r in recipes if r["meal_type"] == "lunch"])
d_count = len([r for r in recipes if r["meal_type"] == "dinner"])

cols = st.columns(6)
cols[0].metric("\U0001F373 Breakfasts", b_count)
cols[1].metric("\U0001F957 Lunches", l_count)
cols[2].metric("\U0001F37D\uFE0F Dinners", d_count)
cols[3].metric("\U0001F4E6 Prep-ahead", len([r for r in recipes if r["cooking_method"] == "prep-ahead"]))
cols[4].metric("\U0001F372 Batch", len([r for r in recipes if r["cooking_method"] == "batch"]))
cols[5].metric("\U0001F373 Fresh", len([r for r in recipes if r["cooking_method"] == "fresh"]))

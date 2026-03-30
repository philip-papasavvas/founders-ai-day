"""Meal Ratings — one-click rating buttons."""

import streamlit as st

st.set_page_config(page_title="Meal Ratings", page_icon="\u2B50", layout="wide")

from styles import inject_theme, banner, get_meal_emoji
from database import (
    init_db, get_finalized_plans, get_plan_meals_for_rating,
    save_rating, get_all_ratings, get_all_recipes,
)

inject_theme()
init_db()

banner()
st.markdown("#### \u2B50 Meal Ratings")
st.caption("One click to rate \u2014 your feedback shapes future plans.")

# Rating buttons config
RATINGS = [
    (1, "\U0001F44E", "Nope"),
    (2, "\U0001F610", "Meh"),
    (3, "\U0001F642", "Good"),
    (4, "\U0001F60B", "Great"),
    (5, "\u2764\uFE0F", "Love"),
]

# ── Rate from past plans ─────────────────────────────────────────────
plans = get_finalized_plans()

if not plans:
    st.info("No finalised plans yet. Generate and finalise a plan first.")
else:
    for plan in plans[:5]:
        with st.expander(f"Week of {plan['week_start']} ({plan['meal_count']} meals)"):
            meals = get_plan_meals_for_rating(plan["id"])

            for meal in meals:
                emoji = get_meal_emoji(meal["name"], meal["meal_type"])
                current = round(meal["current_rating"]) if meal["current_rating"] else 0

                cols = st.columns([3, 1, 1, 1, 1, 1])

                with cols[0]:
                    method_icon = {
                        "fresh": "\U0001F373", "batch": "\U0001F372",
                        "prep-ahead": "\U0001F4E6", "no-cook": "\u2744\uFE0F",
                    }
                    badge = method_icon.get(meal["cooking_method"], "")
                    current_stars = "\u2B50" * current if current else ""
                    st.markdown(
                        f"{emoji} **{meal['name']}** {badge}  \n"
                        f"<small>{meal['meal_type'].title()} {current_stars}</small>",
                        unsafe_allow_html=True,
                    )

                for i, (val, btn_emoji, label) in enumerate(RATINGS):
                    with cols[i + 1]:
                        btn_key = f"r_{plan['id']}_{meal['recipe_id']}_{val}"
                        highlight = "\u2705 " if val == current else ""
                        if st.button(
                            f"{highlight}{btn_emoji}",
                            key=btn_key,
                            help=label,
                            use_container_width=True,
                        ):
                            save_rating(meal["recipe_id"], val)
                            st.rerun()

# ── Ratings overview ──────────────────────────────────────────────────
st.markdown("---")
st.markdown("##### All ratings")

all_recipes = get_all_recipes()
recipe_map = {r["id"]: r for r in all_recipes}
ratings = get_all_ratings()

if ratings:
    html = '<table class="shop-table"><thead><tr><th>Recipe</th><th>Rating</th><th>Count</th></tr></thead><tbody>'
    for rid, data in sorted(ratings.items(), key=lambda x: x[1]["avg_rating"], reverse=True):
        r = recipe_map.get(rid)
        if not r:
            continue
        emoji = get_meal_emoji(r["name"], r["meal_type"])
        stars = "\u2B50" * round(data["avg_rating"])
        html += f"<tr><td>{emoji} {r['name']}</td><td>{stars}</td><td>{data['count']}</td></tr>"
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)
else:
    st.caption("No ratings yet \u2014 rate meals above to get started.")

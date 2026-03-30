"""Recipe Library — browse, filter, and rate all recipes."""

import json
import streamlit as st

st.set_page_config(page_title="Recipe Library", page_icon="\U0001F4DA", layout="wide")

from styles import inject_theme, banner, get_meal_emoji, method_label
from database import init_db, get_all_recipes, get_all_ratings, save_rating, get_recipe_by_id

inject_theme()
init_db()

banner()
st.markdown("#### \U0001F4DA Recipe Library")

# ── Filters ──────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    meal_filter = st.selectbox("Meal type", ["All", "Breakfast", "Lunch", "Dinner"])
with c2:
    method_filter = st.selectbox("Method", ["All", "Prep-ahead", "Batch", "Fresh"])
with c3:
    sort_by = st.selectbox("Sort by", ["Name", "Rating (high first)", "Calories (low first)", "Protein (high first)"])

# ── Load data ─────────────────────────────────────────────────────────
recipes = get_all_recipes()
ratings = get_all_ratings()

# Apply filters
if meal_filter != "All":
    recipes = [r for r in recipes if r["meal_type"] == meal_filter.lower()]
if method_filter != "All":
    method_val = method_filter.lower().replace("-", "-")
    if method_val == "prep-ahead":
        recipes = [r for r in recipes if r["cooking_method"] == "prep-ahead"]
    else:
        recipes = [r for r in recipes if r["cooking_method"] == method_val.lower()]

# Sort
if sort_by == "Name":
    recipes.sort(key=lambda r: r["name"])
elif sort_by == "Rating (high first)":
    recipes.sort(key=lambda r: ratings.get(r["id"], {}).get("avg_rating", 0), reverse=True)
elif sort_by == "Calories (low first)":
    recipes.sort(key=lambda r: r.get("calories") or 999)
elif sort_by == "Protein (high first)":
    recipes.sort(key=lambda r: r.get("protein") or 0, reverse=True)

st.caption(f"Showing {len(recipes)} recipes")

# ── Rating buttons ───────────────────────────────────────────────────
RATINGS = [
    (1, "\U0001F44E"),
    (2, "\U0001F610"),
    (3, "\U0001F642"),
    (4, "\U0001F60B"),
    (5, "\u2764\uFE0F"),
]

# ── Recipe cards ─────────────────────────────────────────────────────
# Display in rows of 3
for row_start in range(0, len(recipes), 3):
    cols = st.columns(3)
    for col_idx, recipe in enumerate(recipes[row_start : row_start + 3]):
        with cols[col_idx]:
            rid = recipe["id"]
            emoji = get_meal_emoji(recipe["name"], recipe["meal_type"])
            ml = method_label(
                recipe["cooking_method"],
                recipe.get("prep_minutes", 0),
                recipe.get("cook_minutes", 0),
            )

            # Rating
            r_data = ratings.get(rid, {})
            avg = r_data.get("avg_rating", 0)
            stars = "\u2B50" * round(avg) if avg else ""
            count = r_data.get("count", 0)

            tags = json.loads(recipe.get("tags", "[]")) if isinstance(recipe.get("tags"), str) else recipe.get("tags", [])
            tag_pills = " ".join(
                f'<span class="macro-pill">{t}</span>' for t in tags[:3]
            )

            cals = recipe.get("calories", 0) or 0
            prot = recipe.get("protein", 0) or 0
            carbs = recipe.get("carbs", 0) or 0
            fat = recipe.get("fat", 0) or 0

            card_html = f"""
            <div class="recipe-card">
                <span class="card-emoji">{emoji}</span>
                <span class="card-title">{recipe['name']}</span><br>
                <span class="card-meta">{recipe['meal_type'].title()} \u00B7 {ml} {stars}</span>
                <div class="card-macros">
                    <span class="macro-pill">{cals} kcal</span>
                    <span class="macro-pill">{prot:.0f}g protein</span>
                    <span class="macro-pill">{carbs:.0f}g carbs</span>
                    <span class="macro-pill">{fat:.0f}g fat</span>
                </div>
                {'<div class="card-macros">' + tag_pills + '</div>' if tag_pills else ''}
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

            # One-click rating row
            rcols = st.columns(5)
            for i, (val, btn_emoji) in enumerate(RATINGS):
                with rcols[i]:
                    highlight = "\u2713" if val == round(avg) else ""
                    if st.button(
                        f"{btn_emoji}{highlight}",
                        key=f"lib_{rid}_{val}",
                        use_container_width=True,
                    ):
                        save_rating(rid, val)
                        st.rerun()

            # Expandable details
            with st.expander("Details"):
                full = get_recipe_by_id(rid)
                if full:
                    instructions = full.get("instructions", "")
                    if instructions:
                        st.markdown(instructions)
                    if full.get("ingredients"):
                        st.markdown("**Ingredients:**")
                        ing_lines = []
                        for ing in full["ingredients"]:
                            qty = ing["quantity"]
                            qty_s = str(int(qty)) if qty == int(qty) else f"{qty:.1f}"
                            unit = ing["unit"] or ""
                            ing_lines.append(f"- {qty_s}{unit} {ing['ingredient']}")
                        st.markdown("\n".join(ing_lines))
                    cost = recipe.get("cost_per_serving")
                    if cost:
                        st.markdown(f"Est. cost: **\u00A3{cost:.2f}**/serving")

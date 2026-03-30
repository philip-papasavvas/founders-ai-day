"""Weekly Planner — generate and customise the meal plan."""

import json
import streamlit as st
from datetime import date

st.set_page_config(page_title="Weekly Planner", page_icon="\U0001F4C5", layout="wide")

from styles import inject_theme, banner, get_meal_emoji, method_label
from database import (
    init_db, get_meal_plan, save_meal_plan, finalize_plan,
    save_weekly_answers, get_weekly_answers, get_preference,
)
from generator import generate_plan, get_next_monday, DAYS, get_alternatives

inject_theme()
init_db()

banner()
st.markdown("#### \U0001F4C5 Weekly Planner")

# ── Week selector ─────────────────────────────────────────────────────
next_mon = get_next_monday()
week_start = st.date_input(
    "Week starting (Monday)",
    value=date.fromisoformat(next_mon),
    help="Select the Monday of the week you want to plan",
)
week_key = week_start.isoformat()

# ── Weekly check-in (compact) ────────────────────────────────────────
existing_answers = get_weekly_answers(week_key)

with st.expander("\U0001F4CB Weekly check-in", expanded=existing_answers is None):
    c1, c2 = st.columns(2)
    with c1:
        cooking_hours = st.slider(
            "Cooking hours this week?", 1.0, 10.0, 5.0, 0.5,
        )
        cravings = st.text_input("Cravings?", placeholder="e.g. Mexican, more fish")
    with c2:
        guests = st.number_input("Guests?", 0, 10, 0)
        guest_meal = ""
        if guests > 0:
            guest_meal = st.selectbox("Which meal?", ["Friday dinner", "Saturday dinner", "Sunday lunch", "Other"])
        avoid = st.text_input("Avoid?", placeholder="e.g. no red meat")

    if st.button("Save check-in", use_container_width=True):
        save_weekly_answers(week_key, cooking_hours, guests, guest_meal, cravings, avoid)
        st.success("Saved!")
        st.rerun()

# ── Plan ──────────────────────────────────────────────────────────────
existing_plan = get_meal_plan(week_key)

if existing_plan is None:
    if st.button("\U0001F500 Generate meal plan", type="primary", use_container_width=True):
        items = generate_plan(week_key)
        save_meal_plan(week_key, items)
        st.rerun()
    st.stop()

plan_data = existing_plan
plan_status = plan_data["plan"]["status"]
items = plan_data["items"]

if plan_status == "finalized":
    st.success("\u2705 Plan finalised")
else:
    st.caption("Draft \u2014 swap meals below, then finalise.")

# ── Group items ───────────────────────────────────────────────────────
by_day: dict[str, dict[str, list]] = {}
for item in items:
    by_day.setdefault(item["day"], {}).setdefault(item["meal_type"], []).append(item)

DAY_SHORT = {
    "monday": "Mon", "tuesday": "Tue", "wednesday": "Wed",
    "thursday": "Thu", "friday": "Fri", "saturday": "Sat", "sunday": "Sun",
}

name2 = get_preference("household_name_2", "Partner")

# ── At-a-glance grid (HTML) ──────────────────────────────────────────
st.markdown("##### Week at a glance")

html = '<div style="overflow-x:auto;"><table class="meal-grid"><thead><tr><th></th>'
for day in DAYS:
    html += f"<th>{DAY_SHORT[day]}</th>"
html += "</tr></thead><tbody>"

for meal_type in ["breakfast", "lunch", "dinner"]:
    html += f'<tr><td class="meal-label">{meal_type.title()}</td>'
    for day in DAYS:
        meals = by_day.get(day, {}).get(meal_type, [])
        if meals:
            cell = ""
            for m in meals:
                emoji = get_meal_emoji(m["recipe_name"], meal_type)
                person = ""
                if m["person"] == "philip":
                    person = '<span class="person-badge" style="background:#2196F3;">P</span>'
                elif m["person"] == "wife":
                    person = f'<span class="person-badge">{name2[0]}</span>'  # pink default
                ml = method_label(m["cooking_method"], m.get("prep_minutes", 0), m.get("cook_minutes", 0))
                cell += (
                    f'<div class="meal-cell-item">'
                    f'<span class="emoji">{emoji}</span>{person}<br>'
                    f'<span class="name">{m["recipe_name"]}</span><br>'
                    f'<span class="meta">{ml} \u00B7 {m.get("calories", 0) or 0} kcal</span>'
                    f"</div>"
                )
            html += f'<td class="meal-cell">{cell}</td>'
        else:
            html += '<td class="meal-cell"><span class="meta">\u2014</span></td>'
    html += "</tr>"

html += "</tbody></table></div>"
st.markdown(html, unsafe_allow_html=True)

# ── Detail cards with swap ────────────────────────────────────────────
st.markdown("##### Meal details & method")

for day in DAYS:
    day_meals = by_day.get(day, {})
    with st.expander(f"{DAY_SHORT[day]} \u2014 {day.title()}"):
        cols = st.columns(3)
        for col, meal_type in zip(cols, ["breakfast", "lunch", "dinner"]):
            with col:
                meal_items = day_meals.get(meal_type, [])
                if not meal_items:
                    st.caption(f"**{meal_type.title()}**: \u2014")
                    continue

                for mi in meal_items:
                    emoji = get_meal_emoji(mi["recipe_name"], meal_type)
                    person_lbl = ""
                    if mi["person"] == "philip":
                        person_lbl = " (Philip)"
                    elif mi["person"] == "wife":
                        person_lbl = f" ({name2})"

                    st.markdown(f"{emoji} **{mi['recipe_name']}**{person_lbl}")

                    cals = mi.get("calories", 0) or 0
                    prot = mi.get("protein", 0) or 0
                    ml = method_label(
                        mi["cooking_method"],
                        mi.get("prep_minutes", 0),
                        mi.get("cook_minutes", 0),
                    )
                    st.caption(f"{ml} \u00B7 {cals} kcal \u00B7 {prot:.0f}g protein")

                    if mi.get("notes"):
                        st.caption(f"_{mi['notes']}_")

                    # Swap (draft only)
                    if plan_status == "draft":
                        swap_key = f"s_{day}_{meal_type}_{mi['recipe_id']}_{mi['person']}"
                        if st.button("\U0001F504 Swap", key=swap_key, use_container_width=True):
                            st.session_state[f"sw_{swap_key}"] = True

                        if st.session_state.get(f"sw_{swap_key}"):
                            method = mi["cooking_method"] if meal_type == "dinner" else None
                            alts = get_alternatives(meal_type, cooking_method=method, exclude_id=mi["recipe_id"])
                            alt_map = {
                                a["id"]: f"{get_meal_emoji(a['name'], meal_type)} {a['name']} ({a['calories']} kcal)"
                                for a in alts
                            }
                            new_id = st.selectbox(
                                "Replace with:",
                                list(alt_map.keys()),
                                format_func=lambda x: alt_map[x],
                                key=f"a_{swap_key}",
                            )
                            if st.button("\u2705 Confirm", key=f"c_{swap_key}"):
                                updated = []
                                for it in items:
                                    row = {
                                        "day": it["day"],
                                        "meal_type": it["meal_type"],
                                        "recipe_id": it["recipe_id"],
                                        "servings": it["servings"],
                                        "person": it["person"],
                                        "notes": it.get("notes", ""),
                                    }
                                    if (
                                        it["day"] == day
                                        and it["meal_type"] == meal_type
                                        and it["recipe_id"] == mi["recipe_id"]
                                        and it["person"] == mi["person"]
                                    ):
                                        row["recipe_id"] = new_id
                                    updated.append(row)
                                save_meal_plan(week_key, updated)
                                st.session_state[f"sw_{swap_key}"] = False
                                st.rerun()

# ── Summary + actions ─────────────────────────────────────────────────
total_cal = sum((i.get("calories", 0) or 0) * i["servings"] for i in items)
total_cost = sum((i.get("cost_per_serving", 0) or 0) * i["servings"] for i in items)

s1, s2, s3 = st.columns(3)
s1.metric("Meals", len(items))
s2.metric("Est. calories", f"{total_cal:,.0f}")
s3.metric("Est. cost", f"\u00A3{total_cost:.2f}")

if plan_status == "draft":
    c1, c2 = st.columns(2)
    with c1:
        if st.button("\U0001F504 Regenerate", use_container_width=True):
            new_items = generate_plan(week_key)
            save_meal_plan(week_key, new_items)
            st.rerun()
    with c2:
        if st.button("\u2705 Finalise plan", type="primary", use_container_width=True):
            finalize_plan(week_key)
            st.rerun()

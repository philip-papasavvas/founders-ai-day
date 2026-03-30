"""Database operations for Meal Planning Amp.

Uses SQLite to store recipes, meal plans, ratings and preferences.
"""

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "meal_planning_amp.db"


def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            meal_type TEXT NOT NULL CHECK(meal_type IN ('breakfast', 'lunch', 'dinner')),
            cooking_method TEXT NOT NULL CHECK(cooking_method IN ('fresh', 'batch', 'prep-ahead', 'no-cook')),
            servings INTEGER DEFAULT 2,
            prep_minutes INTEGER DEFAULT 0,
            cook_minutes INTEGER DEFAULT 0,
            calories INTEGER,
            protein REAL,
            carbs REAL,
            fat REAL,
            fibre REAL,
            cost_per_serving REAL,
            tags TEXT DEFAULT '[]',
            instructions TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
            ingredient TEXT NOT NULL,
            quantity REAL,
            unit TEXT,
            category TEXT CHECK(category IN (
                'produce', 'dairy', 'meat', 'fish', 'bakery',
                'pantry', 'frozen', 'spices', 'other'
            )),
            optional INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS meal_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_start TEXT NOT NULL,
            status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'finalized')),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS meal_plan_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL REFERENCES meal_plans(id) ON DELETE CASCADE,
            day TEXT NOT NULL,
            meal_type TEXT NOT NULL CHECK(meal_type IN ('breakfast', 'lunch', 'dinner')),
            recipe_id INTEGER REFERENCES recipes(id),
            servings REAL DEFAULT 2,
            person TEXT DEFAULT 'both' CHECK(person IN ('philip', 'wife', 'both')),
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS meal_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL REFERENCES recipes(id),
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            notes TEXT,
            rated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS weekly_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_start TEXT NOT NULL,
            cooking_hours REAL DEFAULT 5,
            guests INTEGER DEFAULT 0,
            guest_meal TEXT,
            cravings TEXT,
            avoid TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Seed recipes if empty
    count = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    if count == 0:
        _seed_recipes(conn)

    # Seed default preferences if empty
    pref_count = conn.execute("SELECT COUNT(*) FROM preferences").fetchone()[0]
    if pref_count == 0:
        _seed_preferences(conn)

    conn.commit()
    conn.close()


def _seed_recipes(conn):
    from seed_data import RECIPES

    for recipe in RECIPES:
        conn.execute(
            """INSERT INTO recipes
               (name, meal_type, cooking_method, servings, prep_minutes, cook_minutes,
                calories, protein, carbs, fat, fibre, cost_per_serving, tags, instructions)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                recipe["name"],
                recipe["meal_type"],
                recipe["cooking_method"],
                recipe.get("servings", 2),
                recipe.get("prep_minutes", 0),
                recipe.get("cook_minutes", 0),
                recipe.get("calories"),
                recipe.get("protein"),
                recipe.get("carbs"),
                recipe.get("fat"),
                recipe.get("fibre"),
                recipe.get("cost_per_serving"),
                json.dumps(recipe.get("tags", [])),
                recipe.get("instructions", ""),
            ),
        )
        recipe_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        for ing in recipe.get("ingredients", []):
            conn.execute(
                """INSERT INTO recipe_ingredients
                   (recipe_id, ingredient, quantity, unit, category, optional)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (recipe_id, ing[0], ing[1], ing[2], ing[3], ing[4] if len(ing) > 4 else 0),
            )


def _seed_preferences(conn):
    defaults = {
        "household_name_1": "Philip",
        "household_name_2": "Partner",
        "person_1_weight_kg": "75",
        "person_2_weight_kg": "55",
        "person_1_activity": "high",
        "person_2_activity": "moderate",
        "person_2_breastfeeding": "false",
        "office_days": json.dumps(
            ["monday", "tuesday", "wednesday", "thursday", "friday"]
        ),
        "dietary_restrictions": "[]",
        "disliked_ingredients": "[]",
        "weekly_budget_gbp": "100",
        "batch_dinners_per_week": "4",
        "fresh_dinners_per_week": "3",
        "planning_day": "friday",
        "delivery_day": "sunday",
    }
    for key, value in defaults.items():
        conn.execute("INSERT INTO preferences (key, value) VALUES (?, ?)", (key, value))


# ── Recipe queries ────────────────────────────────────────────────────


def get_all_recipes(meal_type=None, cooking_method=None):
    conn = get_connection()
    query = "SELECT * FROM recipes WHERE is_active = 1"
    params: list = []
    if meal_type:
        query += " AND meal_type = ?"
        params.append(meal_type)
    if cooking_method:
        query += " AND cooking_method = ?"
        params.append(cooking_method)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recipe_by_id(recipe_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    if row:
        ings = conn.execute(
            "SELECT * FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,)
        ).fetchall()
        result = dict(row)
        result["ingredients"] = [dict(i) for i in ings]
        conn.close()
        return result
    conn.close()
    return None


def get_recipe_ingredients(recipe_id: int):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Preferences ───────────────────────────────────────────────────────


def get_preference(key: str, default=None):
    conn = get_connection()
    row = conn.execute("SELECT value FROM preferences WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_preference(key: str, value):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)",
        (key, str(value)),
    )
    conn.commit()
    conn.close()


def get_all_preferences():
    conn = get_connection()
    rows = conn.execute("SELECT key, value FROM preferences").fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}


# ── Ratings ───────────────────────────────────────────────────────────


def get_all_ratings():
    conn = get_connection()
    rows = conn.execute(
        """SELECT recipe_id, AVG(rating) AS avg_rating, COUNT(*) AS cnt
           FROM meal_ratings GROUP BY recipe_id"""
    ).fetchall()
    conn.close()
    return {r["recipe_id"]: {"avg_rating": r["avg_rating"], "count": r["cnt"]} for r in rows}


def save_rating(recipe_id: int, rating: int, notes: str = ""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO meal_ratings (recipe_id, rating, notes) VALUES (?, ?, ?)",
        (recipe_id, rating, notes),
    )
    conn.commit()
    conn.close()


def get_ratings_for_recipes(recipe_ids: list[int]):
    if not recipe_ids:
        return {}
    conn = get_connection()
    placeholders = ",".join("?" for _ in recipe_ids)
    rows = conn.execute(
        f"""SELECT recipe_id, AVG(rating) AS avg_rating, COUNT(*) AS cnt
            FROM meal_ratings WHERE recipe_id IN ({placeholders})
            GROUP BY recipe_id""",
        recipe_ids,
    ).fetchall()
    conn.close()
    return {r["recipe_id"]: {"avg_rating": r["avg_rating"], "count": r["cnt"]} for r in rows}


# ── Recent history (for variety) ──────────────────────────────────────


def get_recent_recipe_ids(weeks: int = 3) -> set[int]:
    conn = get_connection()
    rows = conn.execute(
        """SELECT DISTINCT mpi.recipe_id
           FROM meal_plan_items mpi
           JOIN meal_plans mp ON mpi.plan_id = mp.id
           WHERE mp.week_start >= date('now', ? || ' days')""",
        (str(-weeks * 7),),
    ).fetchall()
    conn.close()
    return {r["recipe_id"] for r in rows}


# ── Meal plans ────────────────────────────────────────────────────────


def save_meal_plan(week_start: str, items: list[dict], notes: str = "") -> int:
    conn = get_connection()
    # Remove existing drafts for the same week
    conn.execute(
        "DELETE FROM meal_plan_items WHERE plan_id IN "
        "(SELECT id FROM meal_plans WHERE week_start = ? AND status = 'draft')",
        (week_start,),
    )
    conn.execute(
        "DELETE FROM meal_plans WHERE week_start = ? AND status = 'draft'",
        (week_start,),
    )

    conn.execute(
        "INSERT INTO meal_plans (week_start, notes) VALUES (?, ?)", (week_start, notes)
    )
    plan_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    for item in items:
        conn.execute(
            """INSERT INTO meal_plan_items
               (plan_id, day, meal_type, recipe_id, servings, person, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                plan_id,
                item["day"],
                item["meal_type"],
                item["recipe_id"],
                item.get("servings", 2),
                item.get("person", "both"),
                item.get("notes", ""),
            ),
        )

    conn.commit()
    conn.close()
    return plan_id


def get_meal_plan(week_start: str):
    conn = get_connection()
    plan = conn.execute(
        "SELECT * FROM meal_plans WHERE week_start = ? ORDER BY created_at DESC LIMIT 1",
        (week_start,),
    ).fetchone()
    if not plan:
        conn.close()
        return None

    items = conn.execute(
        """SELECT mpi.*, r.name AS recipe_name, r.calories, r.protein, r.carbs, r.fat,
                  r.cooking_method, r.prep_minutes, r.cook_minutes, r.cost_per_serving,
                  r.tags
           FROM meal_plan_items mpi
           JOIN recipes r ON mpi.recipe_id = r.id
           WHERE mpi.plan_id = ?
           ORDER BY
               CASE mpi.day
                   WHEN 'monday' THEN 1 WHEN 'tuesday' THEN 2 WHEN 'wednesday' THEN 3
                   WHEN 'thursday' THEN 4 WHEN 'friday' THEN 5
                   WHEN 'saturday' THEN 6 WHEN 'sunday' THEN 7
               END,
               CASE mpi.meal_type
                   WHEN 'breakfast' THEN 1 WHEN 'lunch' THEN 2 WHEN 'dinner' THEN 3
               END""",
        (plan["id"],),
    ).fetchall()
    conn.close()
    return {"plan": dict(plan), "items": [dict(i) for i in items]}


def finalize_plan(week_start: str):
    conn = get_connection()
    conn.execute(
        "UPDATE meal_plans SET status = 'finalized' WHERE week_start = ?",
        (week_start,),
    )
    conn.commit()
    conn.close()


def get_finalized_plans():
    conn = get_connection()
    rows = conn.execute(
        """SELECT mp.*, COUNT(mpi.id) AS meal_count
           FROM meal_plans mp
           LEFT JOIN meal_plan_items mpi ON mp.id = mpi.plan_id
           WHERE mp.status = 'finalized'
           GROUP BY mp.id
           ORDER BY mp.week_start DESC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_plan_meals_for_rating(plan_id: int):
    conn = get_connection()
    rows = conn.execute(
        """SELECT DISTINCT mpi.recipe_id, r.name, r.meal_type, r.cooking_method,
                  COALESCE(mr.avg_rating, 0) AS current_rating
           FROM meal_plan_items mpi
           JOIN recipes r ON mpi.recipe_id = r.id
           LEFT JOIN (
               SELECT recipe_id, AVG(rating) AS avg_rating
               FROM meal_ratings GROUP BY recipe_id
           ) mr ON r.id = mr.recipe_id
           WHERE mpi.plan_id = ?
           ORDER BY r.meal_type, r.name""",
        (plan_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Shopping list ─────────────────────────────────────────────────────


def get_shopping_list(plan_id: int) -> dict[str, list[dict]]:
    conn = get_connection()
    rows = conn.execute(
        """SELECT ri.ingredient, ri.quantity, ri.unit, ri.category,
                  mpi.servings AS plan_servings, r.servings AS recipe_servings
           FROM meal_plan_items mpi
           JOIN recipes r ON mpi.recipe_id = r.id
           JOIN recipe_ingredients ri ON r.id = ri.recipe_id
           WHERE mpi.plan_id = ?""",
        (plan_id,),
    ).fetchall()
    conn.close()

    aggregated: dict[tuple, float] = {}
    for row in rows:
        key = (row["ingredient"], row["unit"], row["category"])
        scale = row["plan_servings"] / row["recipe_servings"] if row["recipe_servings"] else 1
        qty = (row["quantity"] or 0) * scale
        aggregated[key] = aggregated.get(key, 0) + qty

    shopping: dict[str, list[dict]] = {}
    for (ingredient, unit, category), quantity in sorted(aggregated.items()):
        cat = category or "other"
        shopping.setdefault(cat, []).append(
            {"ingredient": ingredient, "quantity": round(quantity, 1), "unit": unit}
        )
    return shopping


# ── Weekly answers ────────────────────────────────────────────────────


def save_weekly_answers(
    week_start: str,
    cooking_hours: float,
    guests: int = 0,
    guest_meal: str = "",
    cravings: str = "",
    avoid: str = "",
    notes: str = "",
):
    conn = get_connection()
    conn.execute(
        """INSERT OR REPLACE INTO weekly_answers
           (week_start, cooking_hours, guests, guest_meal, cravings, avoid, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (week_start, cooking_hours, guests, guest_meal, cravings, avoid, notes),
    )
    conn.commit()
    conn.close()


def get_weekly_answers(week_start: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM weekly_answers WHERE week_start = ? ORDER BY created_at DESC LIMIT 1",
        (week_start,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None

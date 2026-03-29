"""Structured meal catalogue for the household meal planner."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

MealType = Literal["breakfast", "lunch", "dinner"]


@dataclass(frozen=True)
class Ingredient:
    """Single ingredient entry used for shopping list aggregation."""

    name: str
    quantity: float
    unit: str
    category: str


@dataclass(frozen=True)
class Meal:
    """Meal metadata used for planning, budgeting, and nutrition heuristics."""

    key: str
    name: str
    meal_type: MealType
    base_servings: int
    protein_g: int
    estimated_cost_gbp: float
    make_ahead: bool
    hosting_friendly: bool
    nutrition_focus: bool
    description: str
    tags: tuple[str, ...]
    ingredients: tuple[Ingredient, ...]


def ingredient(name: str, quantity: float, unit: str, category: str) -> Ingredient:
    """Shortcut for readable catalogue definitions."""

    return Ingredient(name=name, quantity=quantity, unit=unit, category=category)


BREAKFAST_OPTIONS: tuple[Meal, ...] = (
    Meal(
        key="skyr_overnight_oats",
        name="Skyr overnight oats with chia and berries",
        meal_type="breakfast",
        base_servings=4,
        protein_g=31,
        estimated_cost_gbp=1.85,
        make_ahead=True,
        hosting_friendly=False,
        nutrition_focus=True,
        description="Cold, portable, and easy to eat on the train or at the desk.",
        tags=("portable", "high_protein", "fiber"),
        ingredients=(
            ingredient("Skyr or Greek yogurt", 700, "g", "Fridge"),
            ingredient("Rolled oats", 320, "g", "Cupboard"),
            ingredient("Milk", 700, "ml", "Fridge"),
            ingredient("Chia seeds", 60, "g", "Cupboard"),
            ingredient("Frozen berries", 320, "g", "Frozen"),
            ingredient("Honey", 40, "g", "Cupboard"),
        ),
    ),
    Meal(
        key="egg_muffins",
        name="Egg, spinach, and feta breakfast muffins",
        meal_type="breakfast",
        base_servings=6,
        protein_g=27,
        estimated_cost_gbp=1.95,
        make_ahead=True,
        hosting_friendly=False,
        nutrition_focus=True,
        description="A fast batch bake with good protein and iron support.",
        tags=("portable", "high_protein", "iron"),
        ingredients=(
            ingredient("Eggs", 10, "item", "Fridge"),
            ingredient("Spinach", 200, "g", "Produce"),
            ingredient("Feta", 180, "g", "Fridge"),
            ingredient("Red peppers", 2, "item", "Produce"),
            ingredient("Oatcakes", 12, "item", "Cupboard"),
        ),
    ),
    Meal(
        key="cottage_pots",
        name="Cottage cheese pots with granola and fruit",
        meal_type="breakfast",
        base_servings=4,
        protein_g=29,
        estimated_cost_gbp=1.65,
        make_ahead=True,
        hosting_friendly=False,
        nutrition_focus=True,
        description="Low-effort protein pots for commuter mornings.",
        tags=("portable", "high_protein", "calcium"),
        ingredients=(
            ingredient("Cottage cheese", 800, "g", "Fridge"),
            ingredient("Granola", 200, "g", "Cupboard"),
            ingredient("Apples", 4, "item", "Produce"),
            ingredient("Pumpkin seeds", 80, "g", "Cupboard"),
            ingredient("Cinnamon", 8, "g", "Cupboard"),
        ),
    ),
    Meal(
        key="protein_pancakes",
        name="Blender protein pancakes with banana",
        meal_type="breakfast",
        base_servings=4,
        protein_g=26,
        estimated_cost_gbp=2.2,
        make_ahead=True,
        hosting_friendly=True,
        nutrition_focus=False,
        description="Works for weekend brunch and reheats well.",
        tags=("family", "freezer_friendly"),
        ingredients=(
            ingredient("Eggs", 6, "item", "Fridge"),
            ingredient("Cottage cheese", 300, "g", "Fridge"),
            ingredient("Oats", 220, "g", "Cupboard"),
            ingredient("Bananas", 4, "item", "Produce"),
            ingredient("Maple syrup", 60, "ml", "Cupboard"),
        ),
    ),
)

LUNCH_OPTIONS: tuple[Meal, ...] = (
    Meal(
        key="chicken_pasta_salad",
        name="Chicken pesto pasta salad jars",
        meal_type="lunch",
        base_servings=4,
        protein_g=34,
        estimated_cost_gbp=2.95,
        make_ahead=True,
        hosting_friendly=False,
        nutrition_focus=True,
        description="Cold lunch that survives a busy weekday without fuss.",
        tags=("batch", "portable", "high_protein"),
        ingredients=(
            ingredient("Chicken thighs", 700, "g", "Protein"),
            ingredient("Pasta", 320, "g", "Cupboard"),
            ingredient("Cherry tomatoes", 250, "g", "Produce"),
            ingredient("Spinach", 120, "g", "Produce"),
            ingredient("Pesto", 180, "g", "Fridge"),
            ingredient("Mozzarella", 180, "g", "Fridge"),
        ),
    ),
    Meal(
        key="lentil_soup",
        name="Red lentil soup with yogurt and flatbread",
        meal_type="lunch",
        base_servings=4,
        protein_g=23,
        estimated_cost_gbp=1.9,
        make_ahead=True,
        hosting_friendly=False,
        nutrition_focus=True,
        description="Budget-friendly, warm, and useful for postpartum recovery weeks.",
        tags=("batch", "budget", "iron", "fiber"),
        ingredients=(
            ingredient("Red lentils", 320, "g", "Cupboard"),
            ingredient("Carrots", 4, "item", "Produce"),
            ingredient("Onions", 2, "item", "Produce"),
            ingredient("Garlic cloves", 4, "item", "Produce"),
            ingredient("Vegetable stock", 1, "item", "Cupboard"),
            ingredient("Greek yogurt", 240, "g", "Fridge"),
            ingredient("Flatbreads", 4, "item", "Bakery"),
        ),
    ),
    Meal(
        key="tuna_bean_bowls",
        name="Tuna, white bean, and lemon crunch bowls",
        meal_type="lunch",
        base_servings=4,
        protein_g=32,
        estimated_cost_gbp=2.45,
        make_ahead=True,
        hosting_friendly=False,
        nutrition_focus=True,
        description="No-cook lunch with omega-3s and plenty of texture.",
        tags=("batch", "high_protein", "omega3"),
        ingredients=(
            ingredient("Tuna tins", 4, "item", "Cupboard"),
            ingredient("White beans", 2, "tin", "Cupboard"),
            ingredient("Cucumber", 1, "item", "Produce"),
            ingredient("Cherry tomatoes", 250, "g", "Produce"),
            ingredient("Rocket", 120, "g", "Produce"),
            ingredient("Lemons", 2, "item", "Produce"),
        ),
    ),
    Meal(
        key="turkey_rice_boxes",
        name="Turkey taco rice boxes",
        meal_type="lunch",
        base_servings=4,
        protein_g=35,
        estimated_cost_gbp=2.7,
        make_ahead=True,
        hosting_friendly=False,
        nutrition_focus=False,
        description="Microwave-friendly lunch that keeps protein high.",
        tags=("batch", "reheat", "high_protein"),
        ingredients=(
            ingredient("Turkey mince", 600, "g", "Protein"),
            ingredient("Rice", 300, "g", "Cupboard"),
            ingredient("Sweetcorn", 1, "tin", "Cupboard"),
            ingredient("Black beans", 1, "tin", "Cupboard"),
            ingredient("Tomato salsa", 240, "g", "Fridge"),
            ingredient("Avocados", 2, "item", "Produce"),
        ),
    ),
)

DINNER_OPTIONS: tuple[Meal, ...] = (
    Meal(
        key="lemon_chicken_traybake",
        name="Lemon chicken traybake with potatoes and greens",
        meal_type="dinner",
        base_servings=4,
        protein_g=38,
        estimated_cost_gbp=3.4,
        make_ahead=False,
        hosting_friendly=False,
        nutrition_focus=True,
        description="One-pan dinner that covers protein, carbs, and greens cleanly.",
        tags=("traybake", "family", "iron"),
        ingredients=(
            ingredient("Chicken thighs", 900, "g", "Protein"),
            ingredient("Baby potatoes", 900, "g", "Produce"),
            ingredient("Broccoli", 2, "item", "Produce"),
            ingredient("Lemons", 2, "item", "Produce"),
            ingredient("Greek yogurt", 150, "g", "Fridge"),
        ),
    ),
    Meal(
        key="salmon_rice_bowls",
        name="Teriyaki salmon rice bowls with edamame",
        meal_type="dinner",
        base_servings=4,
        protein_g=36,
        estimated_cost_gbp=4.7,
        make_ahead=False,
        hosting_friendly=False,
        nutrition_focus=True,
        description="High-protein dinner with omega-3s and minimal assembly.",
        tags=("quick", "omega3", "recovery"),
        ingredients=(
            ingredient("Salmon fillets", 700, "g", "Protein"),
            ingredient("Jasmine rice", 320, "g", "Cupboard"),
            ingredient("Edamame", 300, "g", "Frozen"),
            ingredient("Cucumber", 1, "item", "Produce"),
            ingredient("Teriyaki sauce", 180, "ml", "Cupboard"),
        ),
    ),
    Meal(
        key="turkey_meatball_orzo",
        name="Turkey meatball orzo bake",
        meal_type="dinner",
        base_servings=4,
        protein_g=37,
        estimated_cost_gbp=3.3,
        make_ahead=False,
        hosting_friendly=False,
        nutrition_focus=True,
        description="Comfort-food dinner with lighter protein and easy leftovers.",
        tags=("bake", "family", "reheat"),
        ingredients=(
            ingredient("Turkey mince", 700, "g", "Protein"),
            ingredient("Orzo", 320, "g", "Cupboard"),
            ingredient("Passata", 700, "g", "Cupboard"),
            ingredient("Mozzarella", 200, "g", "Fridge"),
            ingredient("Spinach", 160, "g", "Produce"),
        ),
    ),
    Meal(
        key="lentil_dal_eggs",
        name="Spinach dal with jammy eggs and naan",
        meal_type="dinner",
        base_servings=4,
        protein_g=24,
        estimated_cost_gbp=2.3,
        make_ahead=False,
        hosting_friendly=False,
        nutrition_focus=True,
        description="Budget dinner that still lands well nutritionally.",
        tags=("budget", "vegetarian", "iron"),
        ingredients=(
            ingredient("Red lentils", 360, "g", "Cupboard"),
            ingredient("Spinach", 200, "g", "Produce"),
            ingredient("Onions", 2, "item", "Produce"),
            ingredient("Garlic cloves", 4, "item", "Produce"),
            ingredient("Eggs", 6, "item", "Fridge"),
            ingredient("Naan breads", 4, "item", "Bakery"),
        ),
    ),
    Meal(
        key="beef_broccoli_noodles",
        name="Beef and broccoli sesame noodles",
        meal_type="dinner",
        base_servings=4,
        protein_g=35,
        estimated_cost_gbp=4.1,
        make_ahead=False,
        hosting_friendly=False,
        nutrition_focus=True,
        description="Fast iron-rich dinner for heavier training weeks.",
        tags=("quick", "iron", "stir_fry"),
        ingredients=(
            ingredient("Beef strips", 650, "g", "Protein"),
            ingredient("Egg noodles", 320, "g", "Cupboard"),
            ingredient("Broccoli", 2, "item", "Produce"),
            ingredient("Spring onions", 1, "bunch", "Produce"),
            ingredient("Sesame oil", 40, "ml", "Cupboard"),
        ),
    ),
    Meal(
        key="halloumi_chickpea_tray",
        name="Harissa chickpea and halloumi tray",
        meal_type="dinner",
        base_servings=4,
        protein_g=26,
        estimated_cost_gbp=2.9,
        make_ahead=False,
        hosting_friendly=False,
        nutrition_focus=False,
        description="A low-effort vegetarian traybake with good crunch.",
        tags=("traybake", "vegetarian"),
        ingredients=(
            ingredient("Halloumi", 450, "g", "Fridge"),
            ingredient("Chickpeas", 2, "tin", "Cupboard"),
            ingredient("Peppers", 3, "item", "Produce"),
            ingredient("Courgettes", 2, "item", "Produce"),
            ingredient("Harissa paste", 70, "g", "Cupboard"),
        ),
    ),
    Meal(
        key="hosting_taco_bar",
        name="Build-your-own chicken taco bar",
        meal_type="dinner",
        base_servings=6,
        protein_g=34,
        estimated_cost_gbp=3.6,
        make_ahead=False,
        hosting_friendly=True,
        nutrition_focus=False,
        description="Easy crowd-pleaser that scales without much mental load.",
        tags=("hosting", "interactive", "weekend"),
        ingredients=(
            ingredient("Chicken thighs", 1200, "g", "Protein"),
            ingredient("Tortilla wraps", 12, "item", "Bakery"),
            ingredient("Black beans", 2, "tin", "Cupboard"),
            ingredient("Avocados", 3, "item", "Produce"),
            ingredient("Tomatoes", 6, "item", "Produce"),
            ingredient("Greek yogurt", 250, "g", "Fridge"),
        ),
    ),
    Meal(
        key="hosting_roast_chicken",
        name="Roast chicken with carrots, potatoes, and gravy",
        meal_type="dinner",
        base_servings=6,
        protein_g=39,
        estimated_cost_gbp=4.0,
        make_ahead=False,
        hosting_friendly=True,
        nutrition_focus=True,
        description="Classic hosting dinner that also leaves useful leftovers.",
        tags=("hosting", "roast", "weekend"),
        ingredients=(
            ingredient("Whole chicken", 1.8, "kg", "Protein"),
            ingredient("Potatoes", 1500, "g", "Produce"),
            ingredient("Carrots", 8, "item", "Produce"),
            ingredient("Onions", 3, "item", "Produce"),
            ingredient("Green beans", 300, "g", "Produce"),
            ingredient("Gravy granules", 1, "item", "Cupboard"),
        ),
    ),
    Meal(
        key="hosting_beef_ragu",
        name="Slow-cooked beef ragu with pappardelle",
        meal_type="dinner",
        base_servings=6,
        protein_g=37,
        estimated_cost_gbp=4.4,
        make_ahead=False,
        hosting_friendly=True,
        nutrition_focus=True,
        description="Hands-off weekend dinner with enough substance for guests.",
        tags=("hosting", "slow_cook", "iron"),
        ingredients=(
            ingredient("Beef shin or chuck", 1200, "g", "Protein"),
            ingredient("Pappardelle", 500, "g", "Cupboard"),
            ingredient("Passata", 700, "g", "Cupboard"),
            ingredient("Carrots", 4, "item", "Produce"),
            ingredient("Celery", 1, "item", "Produce"),
            ingredient("Parmesan", 120, "g", "Fridge"),
        ),
    ),
)

MEALS_BY_TYPE: dict[MealType, tuple[Meal, ...]] = {
    "breakfast": BREAKFAST_OPTIONS,
    "lunch": LUNCH_OPTIONS,
    "dinner": DINNER_OPTIONS,
}


@dataclass(frozen=True)
class MealDetails:
    """Presentation and preparation details for a meal."""

    visual_emoji: str
    accent: str
    prep_minutes: int
    cook_minutes: int
    method_summary: tuple[str, ...]
    plating_note: str


def details(
    visual_emoji: str,
    accent: str,
    prep_minutes: int,
    cook_minutes: int,
    method_summary: tuple[str, ...],
    plating_note: str,
) -> MealDetails:
    """Shortcut for concise meal presentation metadata."""

    return MealDetails(
        visual_emoji=visual_emoji,
        accent=accent,
        prep_minutes=prep_minutes,
        cook_minutes=cook_minutes,
        method_summary=method_summary,
        plating_note=plating_note,
    )


MEAL_DETAILS: dict[str, MealDetails] = {
    "skyr_overnight_oats": details(
        visual_emoji="🥣",
        accent="#cf5f87",
        prep_minutes=12,
        cook_minutes=0,
        method_summary=(
            "Whisk the skyr, milk, chia, and honey until smooth.",
            "Fold through the oats and berries, then portion into jars.",
            "Leave overnight and grab straight from the fridge in the morning.",
        ),
        plating_note="Top with a few extra berries so it still feels deliberate at 7am.",
    ),
    "egg_muffins": details(
        visual_emoji="🧁",
        accent="#d36d8b",
        prep_minutes=15,
        cook_minutes=22,
        method_summary=(
            "Saute the spinach and peppers briefly so the muffins stay firm.",
            "Whisk eggs with feta, fill the tray, and bake until just set.",
            "Cool fully before boxing them up with oatcakes for grab-and-go mornings.",
        ),
        plating_note="Pack two muffins with a small pot of hot sauce or ketchup.",
    ),
    "cottage_pots": details(
        visual_emoji="🍎",
        accent="#c85b7e",
        prep_minutes=10,
        cook_minutes=0,
        method_summary=(
            "Spoon cottage cheese into jars and season lightly with cinnamon.",
            "Add chopped apple and pumpkin seeds for crunch.",
            "Keep granola separate until eating so the texture stays sharp.",
        ),
        plating_note="A tiny drizzle of honey makes this feel less functional and more breakfast-y.",
    ),
    "protein_pancakes": details(
        visual_emoji="🥞",
        accent="#e48aa3",
        prep_minutes=10,
        cook_minutes=18,
        method_summary=(
            "Blend the batter until smooth and leave it for two minutes to thicken.",
            "Cook small pancakes in batches on a lightly oiled pan.",
            "Serve fresh or cool and refrigerate for a reheatable weekend stack.",
        ),
        plating_note="Stack high with sliced banana so the weekend version feels celebratory.",
    ),
    "chicken_pasta_salad": details(
        visual_emoji="🥗",
        accent="#9fbc8c",
        prep_minutes=18,
        cook_minutes=20,
        method_summary=(
            "Roast or pan-cook the chicken while the pasta boils.",
            "Toss pasta, pesto, tomatoes, spinach, and mozzarella while still slightly warm.",
            "Layer into jars so each lunch is ready without morning assembly.",
        ),
        plating_note="Finish with black pepper and a few halved tomatoes right on top.",
    ),
    "lentil_soup": details(
        visual_emoji="🍲",
        accent="#d58b63",
        prep_minutes=14,
        cook_minutes=28,
        method_summary=(
            "Soften onion, garlic, and carrot until sweet and glossy.",
            "Add lentils and stock, then simmer until the soup turns silky.",
            "Serve with yogurt and warm flatbread for a fuller lunch.",
        ),
        plating_note="A spoon of yogurt and a dusting of paprika make it look finished, not improvised.",
    ),
    "tuna_bean_bowls": details(
        visual_emoji="🐟",
        accent="#6d9ec2",
        prep_minutes=12,
        cook_minutes=0,
        method_summary=(
            "Drain the beans and tuna well so the bowls stay bright rather than soggy.",
            "Toss everything with lemon and olive oil at the last moment.",
            "Pack rocket separately if you want maximum crunch.",
        ),
        plating_note="Keep a lemon wedge in the lunch box for a final squeeze before eating.",
    ),
    "turkey_rice_boxes": details(
        visual_emoji="🍚",
        accent="#c96a57",
        prep_minutes=16,
        cook_minutes=24,
        method_summary=(
            "Brown the turkey mince hard so it actually picks up flavor.",
            "Cook the rice while the mince simmers with salsa, beans, and sweetcorn.",
            "Box the components with avocado added at the end or on the day.",
        ),
        plating_note="Add lime or coriander if you want it to feel less lunch-prep coded.",
    ),
    "lemon_chicken_traybake": details(
        visual_emoji="🍋",
        accent="#d9bb59",
        prep_minutes=16,
        cook_minutes=42,
        method_summary=(
            "Toss potatoes with seasoning first so they get the longest blast in the oven.",
            "Add the chicken and lemon, then roast until the skin turns glossy and deep gold.",
            "Finish the greens separately and spoon over yogurt just before serving.",
        ),
        plating_note="Pile everything onto one platter and let the lemon halves sit visibly on top.",
    ),
    "salmon_rice_bowls": details(
        visual_emoji="🍣",
        accent="#f08a82",
        prep_minutes=14,
        cook_minutes=18,
        method_summary=(
            "Start the rice first, then roast or air-fry the salmon with teriyaki glaze.",
            "Steam the edamame while you slice the cucumber.",
            "Assemble in bowls so the hot salmon lands against the cold crunchy veg.",
        ),
        plating_note="A sesame sprinkle on top makes these feel much more restaurant than spreadsheet.",
    ),
    "turkey_meatball_orzo": details(
        visual_emoji="🍝",
        accent="#bb5c72",
        prep_minutes=22,
        cook_minutes=28,
        method_summary=(
            "Roll the turkey mince into small meatballs so they cook quickly and evenly.",
            "Simmer the orzo in passata until it turns glossy and saucy.",
            "Nestle in the meatballs, top with mozzarella, and bake until bubbling.",
        ),
        plating_note="Serve in shallow bowls with extra greens folded through at the end.",
    ),
    "lentil_dal_eggs": details(
        visual_emoji="🥚",
        accent="#c67a4d",
        prep_minutes=12,
        cook_minutes=30,
        method_summary=(
            "Cook the onions and garlic until sweet before adding the lentils.",
            "Simmer the dal until thick, then fold through spinach at the end.",
            "Boil the eggs until jammy and serve with warm naan.",
        ),
        plating_note="Split the eggs on top so the yolk becomes part of the sauce.",
    ),
    "beef_broccoli_noodles": details(
        visual_emoji="🥩",
        accent="#8d4a4d",
        prep_minutes=16,
        cook_minutes=16,
        method_summary=(
            "Cook the noodles first and rinse quickly so they do not clump.",
            "Sear the beef fast over high heat, then add the broccoli and sesame oil.",
            "Return the noodles and toss until everything is glossy and hot.",
        ),
        plating_note="Finish with spring onions for a proper takeaway-at-home feel.",
    ),
    "halloumi_chickpea_tray": details(
        visual_emoji="🧆",
        accent="#d9896d",
        prep_minutes=14,
        cook_minutes=32,
        method_summary=(
            "Coat the vegetables and chickpeas in harissa first so everything roasts together.",
            "Add the halloumi later so it browns without turning rubbery.",
            "Serve straight from the tray with a spoon of yogurt if you want extra contrast.",
        ),
        plating_note="Let the halloumi sit on top in visible golden slabs rather than mixing it through.",
    ),
    "hosting_taco_bar": details(
        visual_emoji="🌮",
        accent="#d35f6f",
        prep_minutes=20,
        cook_minutes=26,
        method_summary=(
            "Roast or pan-cook the chicken with bold seasoning and shred it while warm.",
            "Set out the beans, tomatoes, avocado, and yogurt in bowls.",
            "Warm the tortillas last so the table feels abundant the moment people sit down.",
        ),
        plating_note="This works best as a spread in the middle of the table, not pre-built plates.",
    ),
    "hosting_roast_chicken": details(
        visual_emoji="🍗",
        accent="#c78858",
        prep_minutes=24,
        cook_minutes=85,
        method_summary=(
            "Season the chicken well and get the potatoes into very hot fat.",
            "Roast the chicken until the skin is dark gold and the vegetables are caramelized.",
            "Make the gravy while the chicken rests so the table timing stays calm.",
        ),
        plating_note="Bring it out whole first - the reveal is half the charm with this one.",
    ),
    "hosting_beef_ragu": details(
        visual_emoji="🍝",
        accent="#8a4159",
        prep_minutes=22,
        cook_minutes=160,
        method_summary=(
            "Brown the beef deeply before adding the vegetables and passata.",
            "Let the sauce go low and slow until the meat collapses.",
            "Cook the pasta last minute and loosen the ragu with pasta water before serving.",
        ),
        plating_note="Twist the pasta into nests and finish with a proper shower of parmesan.",
    ),
}

ALL_MEALS: tuple[Meal, ...] = BREAKFAST_OPTIONS + LUNCH_OPTIONS + DINNER_OPTIONS
MEAL_LOOKUP: dict[str, Meal] = {meal.key: meal for meal in ALL_MEALS}


def get_meal_details(meal_key: str) -> MealDetails:
    """Return presentation metadata for a meal."""

    return MEAL_DETAILS[meal_key]

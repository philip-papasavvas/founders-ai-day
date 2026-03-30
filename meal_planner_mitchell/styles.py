"""Mitchell Family Kitchen — dark mode theme with pink accents."""

import streamlit as st

# Pink accents on dark
PINK = "#FF4081"
PINK_LIGHT = "#3D1A2E"
PINK_MEDIUM = "#F48FB1"
PINK_DARK = "#FF80AB"
BG = "#0E1117"
BG_CARD = "#1A1D24"
BG_CARD_HOVER = "#252830"
BORDER = "#2D2F36"
TEXT = "#EAEAEA"
TEXT_MUTED = "#9CA3AF"


def inject_theme():
    """Inject dark mode pink-accent theme."""
    st.markdown(
        f"""
    <style>
    /* ── Global ───────────────────────────────────────────── */
    .stApp {{ background-color: {BG}; }}
    .block-container {{ padding-top: 1rem; padding-bottom: 1rem; max-width: 1200px; }}
    h1, h2, h3, h4 {{ color: {PINK_DARK}; }}
    h1 {{ margin-bottom: 0.3rem !important; }}
    p, li, span, label, small, caption {{ color: {TEXT}; }}

    /* ── Sidebar ──────────────────────────────────────────── */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #1A0E14 0%, {BG} 100%);
    }}
    section[data-testid="stSidebar"] .stMarkdown p {{
        font-size: 0.9rem;
    }}

    /* ── Metrics ──────────────────────────────────────────── */
    [data-testid="stMetric"] {{
        background: {BG_CARD};
        border-radius: 10px;
        padding: 0.6rem 0.8rem;
        border-left: 4px solid {PINK};
    }}
    [data-testid="stMetricLabel"] {{ font-size: 0.8rem; color: {PINK_MEDIUM}; }}
    [data-testid="stMetricValue"] {{ color: {PINK_DARK}; font-weight: 700; }}

    /* ── Buttons ──────────────────────────────────────────── */
    [data-testid="stBaseButton-primary"] {{
        background-color: {PINK} !important;
        border-color: {PINK} !important;
        color: white !important;
    }}
    [data-testid="stBaseButton-primary"]:hover {{
        background-color: #E91E63 !important;
    }}
    .stButton > button {{
        background-color: {BG_CARD} !important;
        border-color: {BORDER} !important;
        color: {PINK_MEDIUM} !important;
        border-radius: 8px !important;
    }}
    .stButton > button:hover {{
        background-color: {BG_CARD_HOVER} !important;
        border-color: {PINK} !important;
    }}

    /* ── Inputs ───────────────────────────────────────────── */
    .stSelectbox > div > div,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background-color: {BG_CARD} !important;
        color: {TEXT} !important;
        border-color: {BORDER} !important;
    }}

    /* ── Expanders ────────────────────────────────────────── */
    .streamlit-expanderHeader {{
        background-color: {BG_CARD} !important;
        border-radius: 8px;
        color: {PINK_MEDIUM} !important;
    }}
    details {{
        border-color: {BORDER} !important;
    }}

    /* ── Compact spacing ─────────────────────────────────── */
    .stMarkdown {{ margin-bottom: -0.2rem; }}
    hr {{ margin: 0.5rem 0 !important; border-color: {BORDER} !important; }}

    /* ── Meal grid table ─────────────────────────────────── */
    .meal-grid {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 4px;
        font-size: 0.82rem;
    }}
    .meal-grid th {{
        background: {PINK};
        color: white;
        padding: 6px 8px;
        border-radius: 6px 6px 0 0;
        text-align: center;
        font-weight: 600;
    }}
    .meal-grid .meal-label {{
        background: #880E4F;
        color: white;
        padding: 6px 10px;
        border-radius: 6px 0 0 6px;
        font-weight: 600;
        text-align: center;
        width: 80px;
        vertical-align: top;
    }}
    .meal-grid td.meal-cell {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 8px;
        vertical-align: top;
        min-width: 110px;
    }}
    .meal-grid td.meal-cell:hover {{
        background: {BG_CARD_HOVER};
        border-color: {PINK};
    }}
    .meal-cell-item {{
        margin-bottom: 4px;
    }}
    .meal-cell-item .emoji {{ font-size: 1.3rem; }}
    .meal-cell-item .name {{ font-weight: 600; color: {TEXT}; font-size: 0.8rem; }}
    .meal-cell-item .meta {{ color: {TEXT_MUTED}; font-size: 0.7rem; }}
    .person-badge {{
        display: inline-block;
        background: {PINK};
        color: white;
        font-size: 0.6rem;
        padding: 1px 5px;
        border-radius: 8px;
        margin-left: 3px;
        font-weight: 600;
    }}

    /* ── Recipe cards ─────────────────────────────────────── */
    .recipe-card {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 8px;
        border-left: 4px solid {PINK};
    }}
    .recipe-card:hover {{
        border-left-color: {PINK_MEDIUM};
        box-shadow: 0 2px 12px rgba(255,64,129,0.15);
        background: {BG_CARD_HOVER};
    }}
    .recipe-card .card-emoji {{ font-size: 2rem; }}
    .recipe-card .card-title {{ font-weight: 700; color: {PINK_DARK}; font-size: 0.95rem; }}
    .recipe-card .card-meta {{ color: {TEXT_MUTED}; font-size: 0.78rem; }}
    .recipe-card .card-macros {{
        display: flex; gap: 8px; margin-top: 4px;
        font-size: 0.75rem; color: {TEXT};
    }}
    .recipe-card .macro-pill {{
        background: {PINK_LIGHT};
        color: {PINK_MEDIUM};
        padding: 2px 8px;
        border-radius: 10px;
        border: 1px solid #4A2035;
    }}

    /* ── Shopping table ──────────────────────────────────── */
    .shop-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
    }}
    .shop-table th {{
        background: {PINK};
        color: white;
        padding: 6px 10px;
        text-align: left;
    }}
    .shop-table td {{
        padding: 4px 10px;
        border-bottom: 1px solid {BORDER};
        color: {TEXT};
    }}
    .shop-table tr:hover td {{
        background: {BG_CARD_HOVER};
    }}
    .shop-cat-header {{
        background: {PINK_LIGHT} !important;
        font-weight: 700;
        color: {PINK_MEDIUM} !important;
        padding: 6px 10px;
    }}

    /* ── Banner ──────────────────────────────────────────── */
    .family-banner {{
        background: linear-gradient(135deg, #1A0E14 0%, {BG_CARD} 50%, #1A0E14 100%);
        border: 2px solid {PINK};
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        text-align: center;
    }}
    .family-banner h2 {{
        margin: 0 0 4px 0 !important;
        color: {PINK_DARK};
    }}
    .family-banner p {{
        margin: 0;
        color: {TEXT_MUTED};
        font-size: 0.9rem;
    }}

    /* ── Alerts (semantic colours on dark bg) ────────────── */
    .stAlert {{
        background-color: {BG_CARD} !important;
        color: {TEXT} !important;
    }}
    [data-testid="stAlert"][data-baseweb*="positive"] {{
        border-left: 4px solid #4CAF50 !important;
    }}
    [data-testid="stAlert"][data-baseweb*="warning"] {{
        border-left: 4px solid #FF9800 !important;
    }}
    [data-testid="stAlert"][data-baseweb*="info"] {{
        border-left: 4px solid #2196F3 !important;
    }}
    [data-testid="stAlert"][data-baseweb*="negative"] {{
        border-left: 4px solid #f44336 !important;
    }}
    </style>""",
        unsafe_allow_html=True,
    )


def banner():
    st.markdown(
        '<div class="family-banner">'
        "<h2>\U0001F37D\uFE0F Meal Planning Amp \U0001F380</h2>"
        "<p>Weekly meal planning, shopping, and recipe feedback in one place</p>"
        "</div>",
        unsafe_allow_html=True,
    )


# ── Meal emoji mapping ───────────────────────────────────────────────


def get_meal_emoji(recipe_name: str, meal_type: str = "") -> str:
    n = recipe_name.lower()
    if "oats" in n or "porridge" in n:
        return "\U0001F963"
    if "muffin" in n:
        return "\U0001F9C1"
    if "yogurt" in n or "yoghurt" in n:
        return "\U0001F95B"
    if "pancake" in n:
        return "\U0001F95E"
    if "shakshuka" in n:
        return "\U0001F373"
    if "avocado" in n:
        return "\U0001F951"
    if "smoothie" in n:
        return "\U0001FAD0"
    if "wrap" in n or "burrito" in n:
        return "\U0001F32F"
    if "soup" in n:
        return "\U0001F372"
    if "salad" in n:
        return "\U0001F957"
    if "rice bowl" in n or "grain bowl" in n:
        return "\U0001F35A"
    if "stir-fry" in n or "stir fry" in n:
        return "\U0001F958"
    if "tikka" in n or "masala" in n or "curry" in n or "dal" in n:
        return "\U0001F35B"
    if "bolognese" in n or "spaghetti" in n:
        return "\U0001F35D"
    if "chilli" in n or "chili" in n:
        return "\U0001F336\uFE0F"
    if "tagine" in n:
        return "\U0001FAD5"
    if "steak" in n or "beef" in n:
        return "\U0001F969"
    if "chicken" in n and "fajita" in n:
        return "\U0001F32E"
    if "chicken" in n:
        return "\U0001F357"
    if "prawn" in n or "shrimp" in n:
        return "\U0001F990"
    if "salmon" in n:
        return "\U0001F41F"
    if "sea bass" in n or "fish" in n:
        return "\U0001F41F"
    if "risotto" in n:
        return "\U0001F35A"
    if "sausage" in n or "casserole" in n:
        return "\U0001F372"
    if "blt" in n or "sandwich" in n:
        return "\U0001F96A"
    if "fried rice" in n:
        return "\U0001F373"
    if "halloumi" in n:
        return "\U0001F9C0"
    if "scramble" in n or "egg" in n:
        return "\U0001F373"
    if "tuna" in n:
        return "\U0001F41F"
    # Fallback
    if meal_type == "breakfast":
        return "\U0001F373"
    if meal_type == "lunch":
        return "\U0001F957"
    if meal_type == "dinner":
        return "\U0001F37D\uFE0F"
    return "\U0001F374"


def method_label(cooking_method: str, prep_min: int = 0, cook_min: int = 0) -> str:
    total = (prep_min or 0) + (cook_min or 0)
    method_names = {
        "prep-ahead": "Prep-ahead",
        "batch": "Batch",
        "fresh": "Fresh",
        "no-cook": "No-cook",
    }
    name = method_names.get(cooking_method, cooking_method)
    if total > 0:
        return f"{name} \u00B7 {total}m"
    return name


def format_qty(qty: float, unit: str, ingredient: str) -> str:
    qty_str = str(int(qty)) if qty == int(qty) else f"{qty:.1f}"
    if unit in ("whole", "pinch"):
        return f"{qty_str} {ingredient}" if unit == "whole" else f"{ingredient} ({qty_str} pinch)"
    if unit in ("rashers", "slice"):
        return f"{qty_str} {unit} {ingredient}"
    return f"{qty_str}{unit} {ingredient}"

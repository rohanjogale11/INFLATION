"""
Data loading + core computation utilities, shared across all pages.
All disk reads are wrapped in @st.cache_data so each CSV is parsed once
per session.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

CATEGORIES = [
    "Food and Beverages",
    "Housing",
    "Fuel and Light",
    "Clothing and Footwear",
    "Health",
    "Education",
    "Transport and Communication",
    "Miscellaneous",
]

CITIES = [
    "Mumbai", "Delhi", "Chennai", "Bengaluru",
    "Kolkata", "Hyderabad", "Ahmedabad", "Lucknow",
]

CATEGORY_WEIGHTS_NATIONAL = {
    "Food and Beverages": 0.4547,
    "Housing": 0.1007,
    "Fuel and Light": 0.0658,
    "Clothing and Footwear": 0.0659,
    "Health": 0.0559,
    "Education": 0.0328,
    "Transport and Communication": 0.0842,
    "Miscellaneous": 0.1400,
}


@st.cache_data
def load_national_cpi() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "national_cpi.csv", parse_dates=["date"])
    return df


@st.cache_data
def load_city_cpi() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "city_cpi.csv", parse_dates=["date"])
    return df


@st.cache_data
def national_pivot() -> pd.DataFrame:
    """date-indexed, category-columned national CPI table."""
    df = load_national_cpi()
    return df.pivot(index="date", columns="category", values="cpi").sort_index()


@st.cache_data
def city_pivot(city: str) -> pd.DataFrame:
    df = load_city_cpi()
    sub = df[df.city == city]
    return sub.pivot(index="date", columns="category", values="cpi").sort_index()


def compute_personal_inflation(spending: dict) -> pd.DataFrame:
    """
    Laspeyres-style personalised inflation index.

    spending: {category_name: monthly_rupee_amount}

    Returns a DataFrame indexed by date with columns:
        personal_cpi        - normalised personal cost-of-living index (base=100)
        personal_yoy        - year-on-year % change of the personal index
        general_yoy         - year-on-year % change of official national CPI
    """
    total = sum(spending.values())
    if total <= 0:
        raise ValueError("Total spending must be greater than zero.")

    weights = {cat: amt / total for cat, amt in spending.items()}

    pivot = national_pivot()
    cats = [c for c in weights if c in pivot.columns]

    # Personal index = weighted average of category indices (each already base=100)
    weight_sum = sum(weights[c] for c in cats)
    personal_cpi = sum(pivot[c] * weights[c] for c in cats) / weight_sum
    # normalise so the personal index starts at 100 in the first month for readability
    personal_cpi = personal_cpi / personal_cpi.iloc[0] * 100

    general_cpi = pivot["General"] if "General" in pivot.columns else None

    out = pd.DataFrame({"personal_cpi": personal_cpi})
    out["personal_yoy"] = out["personal_cpi"].pct_change(12) * 100
    if general_cpi is not None:
        out["general_cpi"] = general_cpi
        out["general_yoy"] = out["general_cpi"].pct_change(12) * 100
    return out.dropna(how="all")


def project_future_expenses(current_monthly_total: float, rate_pct: float, years=(1, 3, 5)) -> dict:
    """Compound inflation projection: FV = PV * (1+r)^n"""
    r = rate_pct / 100
    return {y: current_monthly_total * (1 + r) ** y for y in years}


def project_by_category(spending: dict, rate_pct: float, years=(1, 3, 5)) -> pd.DataFrame:
    r = rate_pct / 100
    rows = []
    for cat, amt in spending.items():
        row = {"category": cat, "current": amt}
        for y in years:
            row[f"year_{y}"] = amt * (1 + r) ** y
        rows.append(row)
    return pd.DataFrame(rows)

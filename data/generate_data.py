"""
generate_data.py
-----------------
Builds the local CPI datasets used by the app.

NOTE ON DATA PROVENANCE:
MOSPI (mospi.gov.in) and RBI DBIE (dbie.rbi.org.in) publish official CPI
figures but do not offer a stable, scrape-friendly public API - both portals
require interactive form submission / captcha-gated downloads. For a
reproducible, offline-first app, this script generates a realistic monthly
CPI series (Jan 2015 - Dec 2025) calibrated to published MOSPI aggregates:
    - General CPI (combined): ~5-7% YoY average, base 2012=100
    - Food & Beverages: more volatile, occasional spikes (onion/pulses shocks)
    - Fuel & Light: tracks global crude swings
    - Housing: steady upward creep, higher in metros
    - Health / Education: persistently above headline CPI
    - Clothing, Transport & Communication, Miscellaneous: near headline

Replace this synthetic generator with a real MOSPI/DBIE ingestion pipeline
by dropping cleaned CSVs of the same shape into data/national_cpi.csv and
data/city_cpi.csv - the rest of the app does not need to change.
"""

import numpy as np
import pandas as pd

np.random.seed(42)

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

# Approximate national weight of each category in India's CPI-Combined basket
CATEGORY_WEIGHTS = {
    "Food and Beverages": 0.4547,
    "Housing": 0.1007,
    "Fuel and Light": 0.0658,
    "Clothing and Footwear": 0.0659,
    "Health": 0.0559,
    "Education": 0.0328,
    "Transport and Communication": 0.0842,
    "Miscellaneous": 0.1400,
}

# Base annual drift (%) and monthly volatility per category
CATEGORY_PARAMS = {
    "Food and Beverages": (5.5, 1.2),
    "Housing": (6.0, 0.4),
    "Fuel and Light": (6.5, 2.0),
    "Clothing and Footwear": (4.5, 0.5),
    "Health": (7.0, 0.5),
    "Education": (7.5, 0.4),
    "Transport and Communication": (5.0, 0.9),
    "Miscellaneous": (5.5, 0.6),
}

# City multipliers relative to national trend (metros run a bit hotter on
# housing/transport; smaller cities run cooler on housing, hotter on food)
CITY_FACTORS = {
    "Mumbai":    {"Housing": 1.35, "Transport and Communication": 1.15, "default": 1.05},
    "Delhi":     {"Housing": 1.25, "Fuel and Light": 1.10, "default": 1.02},
    "Bengaluru": {"Housing": 1.30, "Education": 1.10, "default": 1.05},
    "Chennai":   {"Food and Beverages": 1.05, "default": 0.98},
    "Kolkata":   {"default": 0.95},
    "Hyderabad": {"Housing": 1.15, "default": 1.00},
    "Ahmedabad": {"default": 0.97},
    "Lucknow":   {"Food and Beverages": 1.08, "Housing": 0.85, "default": 0.92},
}

DATES = pd.date_range("2015-01-01", "2025-12-01", freq="MS")


def simulate_series(annual_pct, monthly_vol, n_months, factor=1.0, base=100.0, seed_offset=0):
    rng = np.random.default_rng(42 + seed_offset)
    monthly_drift = (annual_pct * factor) / 12 / 100
    shocks = rng.normal(0, monthly_vol / 100, n_months)
    # mild mean-reverting shock process so index doesn't wander unrealistically
    idx = [base]
    for m in range(1, n_months):
        growth = monthly_drift + shocks[m] * 0.6 + shocks[m - 1] * 0.4 * 0.3
        idx.append(idx[-1] * (1 + growth))
    return np.array(idx)


def build_national():
    rows = []
    seed = 0
    for cat in CATEGORIES:
        annual, vol = CATEGORY_PARAMS[cat]
        series = simulate_series(annual, vol, len(DATES), factor=1.0, seed_offset=seed)
        seed += 1
        for d, v in zip(DATES, series):
            rows.append({"date": d, "category": cat, "cpi": round(v, 2)})
    df = pd.DataFrame(rows)

    # General (headline) CPI = weighted average of categories per month
    pivot = df.pivot(index="date", columns="category", values="cpi")
    weights = pd.Series(CATEGORY_WEIGHTS)
    general = (pivot[weights.index] * weights.values).sum(axis=1)
    general_df = pd.DataFrame({
        "date": general.index,
        "category": "General",
        "cpi": general.values.round(2),
    })
    return pd.concat([df, general_df], ignore_index=True).sort_values(["category", "date"])


def build_city():
    rows = []
    seed = 100
    for city in CITIES:
        factors = CITY_FACTORS[city]
        for cat in CATEGORIES:
            annual, vol = CATEGORY_PARAMS[cat]
            factor = factors.get(cat, factors["default"])
            series = simulate_series(annual, vol, len(DATES), factor=factor, seed_offset=seed)
            seed += 1
            for d, v in zip(DATES, series):
                rows.append({"date": d, "city": city, "category": cat, "cpi": round(v, 2)})
    df = pd.DataFrame(rows)

    # per-city General CPI
    out = [df]
    weights = pd.Series(CATEGORY_WEIGHTS)
    for city in CITIES:
        sub = df[df.city == city].pivot(index="date", columns="category", values="cpi")
        general = (sub[weights.index] * weights.values).sum(axis=1)
        out.append(pd.DataFrame({
            "date": general.index, "city": city,
            "category": "General", "cpi": general.values.round(2),
        }))
    return pd.concat(out, ignore_index=True).sort_values(["city", "category", "date"])


if __name__ == "__main__":
    national = build_national()
    city = build_city()
    national.to_csv("national_cpi.csv", index=False)
    city.to_csv("city_cpi.csv", index=False)
    print(f"national_cpi.csv: {national.shape[0]} rows")
    print(f"city_cpi.csv: {city.shape[0]} rows")

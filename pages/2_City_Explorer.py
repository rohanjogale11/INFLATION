import streamlit as st
import pandas as pd

from utils.data_loader import CITIES, city_pivot
from utils.charts import multi_category_lines, city_comparison

st.set_page_config(page_title="City Explorer", page_icon="🏙️", layout="wide")

st.title("🏙️ Regional Inflation Explorer")
st.write(
    "Compare CPI trends across major Indian cities. Select one city for a full "
    "category breakdown, or two cities to see a direct overlay with a divergence band."
)

mode = st.radio("Mode", ["Single city", "Compare two cities"], horizontal=True)

if mode == "Single city":
    city = st.selectbox("Select a city", CITIES)
    pivot = city_pivot(city)

    date_range = st.slider(
        "Date range", min_value=pivot.index.min().to_pydatetime(),
        max_value=pivot.index.max().to_pydatetime(),
        value=(pivot.index.min().to_pydatetime(), pivot.index.max().to_pydatetime()),
        format="MMM YYYY",
    )
    filtered = pivot.loc[date_range[0]:date_range[1]]

    st.plotly_chart(
        multi_category_lines(filtered, title=f"{city} — CPI by Category"),
        use_container_width=True,
    )

    st.subheader(f"{city} Summary")
    latest = filtered.iloc[-1]
    yoy = filtered.pct_change(12).iloc[-1] * 100
    rolling_12m = filtered.tail(12).mean()

    summary = pd.DataFrame({
        "Category": filtered.columns,
        "Latest CPI": latest.values.round(2),
        "12-Month Rolling Avg": rolling_12m.values.round(2),
        "YoY Change (%)": yoy.values.round(2),
    })
    st.dataframe(summary, hide_index=True, use_container_width=True)

else:
    c1, c2 = st.columns(2)
    with c1:
        city_a = st.selectbox("City A", CITIES, index=0)
    with c2:
        city_b = st.selectbox("City B", CITIES, index=1)

    if city_a == city_b:
        st.warning("Select two different cities to compare.")
        st.stop()

    category = st.selectbox("Category to compare", city_pivot(city_a).columns.tolist(),
                             index=list(city_pivot(city_a).columns).index("General")
                             if "General" in city_pivot(city_a).columns else 0)

    series_a = city_pivot(city_a)[category]
    series_b = city_pivot(city_b)[category]

    st.plotly_chart(
        city_comparison(series_a, series_b, city_a, city_b),
        use_container_width=True,
    )

    st.subheader("Quantitative Comparison")
    def city_stats(series):
        yoy = series.pct_change(12).iloc[-1] * 100
        return {
            "Latest CPI": round(series.iloc[-1], 2),
            "12-Month Rolling Avg": round(series.tail(12).mean(), 2),
            "YoY Change (%)": round(yoy, 2),
        }

    stats_df = pd.DataFrame({city_a: city_stats(series_a), city_b: city_stats(series_b)}).T
    st.dataframe(stats_df, use_container_width=True)

    diff = series_a.iloc[-1] - series_b.iloc[-1]
    higher = city_a if diff > 0 else city_b
    st.info(f"On **{category}**, **{higher}** currently runs the higher CPI level by "
            f"{abs(diff):.2f} index points.")

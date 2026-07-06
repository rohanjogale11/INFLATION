import streamlit as st
import pandas as pd

from utils.data_loader import CATEGORIES, compute_personal_inflation
from utils.charts import dual_line_comparison

st.set_page_config(page_title="Personal Calculator", page_icon="🧮", layout="wide")

st.title("🧮 Personal Inflation Calculator")
st.write(
    "Enter your average monthly spending in each category. Your personal inflation "
    "rate is computed as a weighted average of category-level CPI changes, "
    "weighted by your own spending — the same Laspeyres-index logic behind the "
    "official CPI, but parameterised by *your* basket."
)

DEFAULTS = {
    "Food and Beverages": 8000,
    "Housing": 12000,
    "Fuel and Light": 2500,
    "Clothing and Footwear": 1500,
    "Health": 2000,
    "Education": 3000,
    "Transport and Communication": 3000,
    "Miscellaneous": 3000,
}

st.subheader("Your Monthly Spending (INR)")
spending = {}
cols = st.columns(2)
for i, cat in enumerate(CATEGORIES):
    with cols[i % 2]:
        spending[cat] = st.number_input(
            cat, min_value=0, value=DEFAULTS[cat], step=500, key=f"spend_{cat}"
        )

total = sum(spending.values())
st.metric("Total Monthly Spending", f"₹{total:,.0f}")

if total <= 0:
    st.warning("Enter at least one non-zero spending amount to compute your inflation rate.")
    st.stop()

with st.expander("Your spending weights"):
    weights_df = pd.DataFrame({
        "Category": list(spending.keys()),
        "Monthly Spend (INR)": list(spending.values()),
        "Weight (%)": [round(v / total * 100, 1) for v in spending.values()],
    }).sort_values("Weight (%)", ascending=False)
    st.dataframe(weights_df, hide_index=True, use_container_width=True)

result = compute_personal_inflation(spending)

st.subheader("Personal vs. Official National Inflation")
fig = dual_line_comparison(result)
st.plotly_chart(fig, use_container_width=True)

latest = result.dropna(subset=["personal_yoy"]).iloc[-1]
c1, c2, c3 = st.columns(3)
c1.metric("Your Latest Inflation Rate", f"{latest['personal_yoy']:.2f}%")
if "general_yoy" in result.columns:
    c2.metric("Official National CPI Rate", f"{latest['general_yoy']:.2f}%")
    divergence = latest["personal_yoy"] - latest["general_yoy"]
    c3.metric("Divergence", f"{divergence:+.2f} pp",
              help="How much higher/lower your personal rate is vs. the national headline figure")

    avg_divergence = (result["personal_yoy"] - result["general_yoy"]).mean()
    direction = "higher" if avg_divergence > 0 else "lower"
    st.info(
        f"On average across the available history, your personalised inflation rate has run "
        f"**{abs(avg_divergence):.2f} percentage points {direction}** than the official national CPI. "
        f"This gap comes from how your spending is distributed across categories compared to the "
        f"nationally averaged basket."
    )

st.caption(
    "Methodology: personal index = Σ(category CPI × your category weight), rebased to 100 at "
    "the start of the series; YoY change computed over a 12-month lag."
)

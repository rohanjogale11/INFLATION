import streamlit as st
import pandas as pd

from utils.data_loader import CATEGORIES, project_future_expenses, project_by_category
from utils.charts import projection_bar_chart

st.set_page_config(page_title="Future Simulator", page_icon="🔮", layout="wide")

st.title("🔮 Future Expense Projection Simulator")
st.write(
    "Project how your current monthly expenses will grow over 1, 3, and 5 years "
    "using the standard compound inflation model: "
    "**Future Value = Present Value × (1 + r)ⁿ**"
)

input_mode = st.radio("Input type", ["Total monthly expense", "Category breakdown"], horizontal=True)

SCENARIOS = {"Optimistic": 3.0, "Baseline": 6.0, "Pessimistic": 10.0}

if input_mode == "Total monthly expense":
    current_total = st.number_input("Current total monthly expense (INR)", min_value=0,
                                     value=30000, step=1000)

    custom_rate = st.slider("Custom inflation rate assumption (%)", 1.0, 15.0, 6.0, 0.5)

    if current_total <= 0:
        st.warning("Enter a positive monthly expense to run the projection.")
        st.stop()

    rows = []
    for name, rate in {**SCENARIOS, "Custom": custom_rate}.items():
        proj = project_future_expenses(current_total, rate)
        rows.append({"scenario": name, "rate": rate,
                     "year_1": proj[1], "year_3": proj[3], "year_5": proj[5]})
    df = pd.DataFrame(rows)

    st.plotly_chart(projection_bar_chart(df), use_container_width=True)

    st.subheader("Projected Values")
    display_df = df.copy()
    for col in ["year_1", "year_3", "year_5"]:
        display_df[col] = display_df[col].map(lambda x: f"₹{x:,.0f}")
    display_df["rate"] = display_df["rate"].map(lambda x: f"{x:.1f}%")
    st.dataframe(display_df.rename(columns={
        "scenario": "Scenario", "rate": "Annual Rate",
        "year_1": "Year 1", "year_3": "Year 3", "year_5": "Year 5",
    }), hide_index=True, use_container_width=True)

    baseline_5y = df.loc[df.scenario == "Baseline", "year_5"].values[0]
    increase_pct = (baseline_5y / current_total - 1) * 100
    st.info(
        f"Under the **Baseline** scenario (6% annual inflation), your ₹{current_total:,.0f} "
        f"monthly budget today would need to grow to roughly **₹{baseline_5y:,.0f}** in 5 years "
        f"— a **{increase_pct:.1f}% increase** — just to maintain your current standard of living."
    )

else:
    st.subheader("Your Monthly Spending (INR)")
    DEFAULTS = {
        "Food and Beverages": 8000, "Housing": 12000, "Fuel and Light": 2500,
        "Clothing and Footwear": 1500, "Health": 2000, "Education": 3000,
        "Transport and Communication": 3000, "Miscellaneous": 3000,
    }
    spending = {}
    cols = st.columns(2)
    for i, cat in enumerate(CATEGORIES):
        with cols[i % 2]:
            spending[cat] = st.number_input(cat, min_value=0, value=DEFAULTS[cat], step=500,
                                             key=f"proj_{cat}")

    rate = st.slider("Inflation rate assumption (%)", 1.0, 15.0, 6.0, 0.5)

    if sum(spending.values()) <= 0:
        st.warning("Enter at least one non-zero spending amount.")
        st.stop()

    proj_df = project_by_category(spending, rate)
    display_df = proj_df.copy()
    for col in ["current", "year_1", "year_3", "year_5"]:
        display_df[col] = display_df[col].map(lambda x: f"₹{x:,.0f}")
    st.dataframe(display_df.rename(columns={
        "category": "Category", "current": "Current",
        "year_1": "Year 1", "year_3": "Year 3", "year_5": "Year 5",
    }), hide_index=True, use_container_width=True)

    totals = proj_df[["current", "year_1", "year_3", "year_5"]].sum()
    single_row = pd.DataFrame([{
        "scenario": "Custom", "year_1": totals["year_1"],
        "year_3": totals["year_3"], "year_5": totals["year_5"],
    }])
    st.plotly_chart(projection_bar_chart(single_row), use_container_width=True)

    increase_pct = (totals["year_5"] / totals["current"] - 1) * 100
    st.info(
        f"At a {rate:.1f}% annual rate, your total monthly expenses would grow from "
        f"₹{totals['current']:,.0f} to **₹{totals['year_5']:,.0f}** in 5 years "
        f"(**+{increase_pct:.1f}%**)."
    )

st.caption("Model: Future Value = Present Value × (1 + r)ⁿ, applied per scenario or per category.")

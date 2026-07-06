"""Reusable Plotly chart builders so pages stay thin."""

import plotly.graph_objects as go
import pandas as pd

BRAND = {
    "personal": "#FF6B35",
    "general": "#2E5266",
    "grid": "#E8E8E8",
}


def dual_line_comparison(df: pd.DataFrame, y1="personal_yoy", y2="general_yoy",
                          name1="Your Personal Inflation", name2="Official National CPI"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df[y1], mode="lines", name=name1,
        line=dict(color=BRAND["personal"], width=3),
    ))
    if y2 in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df[y2], mode="lines", name=name2,
            line=dict(color=BRAND["general"], width=2, dash="dot"),
        ))
    fig.update_layout(
        template="plotly_white",
        yaxis_title="Year-on-Year Inflation (%)",
        xaxis_title="Date",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(l=10, r=10, t=40, b=10),
        hovermode="x unified",
    )
    return fig


def multi_category_lines(pivot_df: pd.DataFrame, title=""):
    fig = go.Figure()
    for col in pivot_df.columns:
        fig.add_trace(go.Scatter(x=pivot_df.index, y=pivot_df[col], mode="lines", name=col))
    fig.update_layout(
        template="plotly_white", title=title,
        yaxis_title="CPI (base = 100)", xaxis_title="Date",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(l=10, r=10, t=60, b=10),
        hovermode="x unified",
    )
    return fig


def city_comparison(city_a_series: pd.Series, city_b_series: pd.Series, name_a: str, name_b: str):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=city_a_series.index, y=city_a_series.values,
                              mode="lines", name=name_a, line=dict(color=BRAND["personal"], width=3)))
    fig.add_trace(go.Scatter(x=city_b_series.index, y=city_b_series.values,
                              mode="lines", name=name_b, line=dict(color=BRAND["general"], width=3)))
    diff = city_a_series - city_b_series
    fig.add_trace(go.Scatter(x=diff.index, y=diff.values, mode="lines", name="Difference",
                              line=dict(color="#999999", width=1, dash="dot"),
                              yaxis="y2"))
    fig.update_layout(
        template="plotly_white",
        yaxis=dict(title="CPI (base = 100)"),
        yaxis2=dict(title="Difference", overlaying="y", side="right", showgrid=False),
        xaxis_title="Date",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(l=10, r=10, t=40, b=10),
        hovermode="x unified",
    )
    return fig


def projection_bar_chart(df: pd.DataFrame, years=(1, 3, 5)):
    """df has columns: scenario, year_1, year_3, year_5 (totals)"""
    fig = go.Figure()
    colors = {"Optimistic": "#2A9D8F", "Baseline": "#E9C46A", "Pessimistic": "#E76F51",
              "Custom": BRAND["personal"]}
    for _, row in df.iterrows():
        fig.add_trace(go.Bar(
            name=row["scenario"],
            x=[f"Year {y}" for y in years],
            y=[row[f"year_{y}"] for y in years],
            marker_color=colors.get(row["scenario"], "#888"),
        ))
    fig.update_layout(
        template="plotly_white", barmode="group",
        yaxis_title="Projected Monthly Expense (INR)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig

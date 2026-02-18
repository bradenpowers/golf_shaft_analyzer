"""Golf Shaft Analytics — Analysis: Data visualizations and insights."""

import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ingestion.load_data import load_database_df

st.set_page_config(page_title="Shaft Analysis", page_icon="📊", layout="wide")
st.title("📊 Shaft Analysis")


@st.cache_data
def get_data():
    return load_database_df()


df = get_data()

if df.empty:
    st.warning("No shaft data loaded. Run `python -m src.ingestion.load_data` first.")
    st.stop()

# --- Filter by club type for analysis ---
club_type = st.selectbox("Club Type", options=sorted(df["club_type"].unique()), index=0)
subset = df[df["club_type"] == club_type].copy()

st.markdown("---")

# --- Weight vs Torque Scatter ---
st.markdown("### Weight vs. Torque by Manufacturer")
scatter_df = subset.dropna(subset=["torque_degrees"])
if not scatter_df.empty:
    fig = px.scatter(
        scatter_df,
        x="weight_grams",
        y="torque_degrees",
        color="manufacturer",
        hover_name="model",
        hover_data=["flex", "launch", "spin"],
        labels={"weight_grams": "Weight (g)", "torque_degrees": "Torque (°)"},
        height=500,
    )
    fig.update_layout(
        xaxis_title="Weight (g)",
        yaxis_title="Torque (°)",
        legend_title="Manufacturer",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "💡 Lower-right = heavier and stiffer (tour profile). "
        "Upper-left = lighter and more flexible (game improvement)."
    )
else:
    st.info("No torque data available for this club type.")

st.markdown("---")

# --- Launch/Spin Distribution ---
st.markdown("### Launch & Spin Profile Distribution")
col1, col2 = st.columns(2)

with col1:
    launch_counts = subset["launch"].dropna().value_counts()
    if not launch_counts.empty:
        fig_launch = px.pie(
            values=launch_counts.values,
            names=launch_counts.index,
            title="Launch Profiles",
            color_discrete_sequence=px.colors.sequential.Greens_r,
        )
        st.plotly_chart(fig_launch, use_container_width=True)

with col2:
    spin_counts = subset["spin"].dropna().value_counts()
    if not spin_counts.empty:
        fig_spin = px.pie(
            values=spin_counts.values,
            names=spin_counts.index,
            title="Spin Profiles",
            color_discrete_sequence=px.colors.sequential.Blues_r,
        )
        st.plotly_chart(fig_spin, use_container_width=True)

st.markdown("---")

# --- Weight Distribution by Manufacturer ---
st.markdown("### Weight Distribution by Manufacturer")
fig_box = px.box(
    subset,
    x="manufacturer",
    y="weight_grams",
    color="manufacturer",
    labels={"weight_grams": "Weight (g)", "manufacturer": ""},
    height=400,
)
fig_box.update_layout(showlegend=False)
st.plotly_chart(fig_box, use_container_width=True)

st.markdown("---")

# --- Model Weight Progression ---
st.markdown("### Weight Progression Across Flexes")
mfr_select = st.selectbox(
    "Manufacturer",
    options=sorted(subset["manufacturer"].unique()),
    key="mfr_prog",
)

models_available = sorted(subset[subset["manufacturer"] == mfr_select]["model"].unique())
model_select = st.selectbox("Model", options=models_available, key="model_prog")

if mfr_select and model_select:
    prog_df = subset[
        (subset["manufacturer"] == mfr_select) & (subset["model"] == model_select)
    ].sort_values("weight_grams")

    if len(prog_df) > 1:
        fig_prog = go.Figure()
        fig_prog.add_trace(go.Bar(
            x=prog_df["flex"],
            y=prog_df["weight_grams"],
            marker_color="#1B5E20",
            text=prog_df["weight_grams"].apply(lambda x: f"{x:.0f}g"),
            textposition="outside",
        ))
        fig_prog.update_layout(
            title=f"{mfr_select} {model_select} — Weight by Flex",
            yaxis_title="Weight (g)",
            height=350,
        )
        st.plotly_chart(fig_prog, use_container_width=True)
    else:
        st.info("Only one flex available for this model.")

# --- Price Comparison ---
st.markdown("---")
st.markdown("### MSRP by Manufacturer")
price_df = subset.dropna(subset=["msrp_usd"]).drop_duplicates(subset=["manufacturer", "model"])
if not price_df.empty:
    avg_prices = price_df.groupby("manufacturer")["msrp_usd"].mean().sort_values()
    fig_price = go.Figure(
        data=[go.Bar(
            x=avg_prices.index,
            y=avg_prices.values,
            marker_color="#0D47A1",
            text=avg_prices.apply(lambda x: f"${x:.0f}"),
            textposition="outside",
        )]
    )
    fig_price.update_layout(yaxis_title="Average MSRP ($)", height=350)
    st.plotly_chart(fig_price, use_container_width=True)

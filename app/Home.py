"""Golf Shaft Analytics — Home: Search & Filter Shaft Database."""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.compare import filter_shafts
from src.ingestion.load_data import load_database_df

st.set_page_config(
    page_title="Golf Shaft Analytics",
    page_icon="⛳",
    layout="wide",
)

st.title("⛳ Golf Shaft Analytics")
st.markdown("Search, filter, and compare golf shaft specifications across manufacturers.")


@st.cache_data
def get_data() -> pd.DataFrame:
    from src.ingestion.load_data import DB_FILE, main as build_db
    if not DB_FILE.exists():
        build_db()
    return load_database_df()


df = get_data()

if df.empty:
    st.warning(
        "No shaft data loaded. Run `python -m src.ingestion.load_data` first."
    )
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")

manufacturers = st.sidebar.multiselect(
    "Manufacturer",
    options=sorted(df["manufacturer"].unique()),
    default=[],
)

club_types = st.sidebar.multiselect(
    "Club Type",
    options=sorted(df["club_type"].unique()),
    default=[],
)

flexes = st.sidebar.multiselect(
    "Flex",
    options=["Ladies", "Senior", "Regular", "Stiff", "X-Stiff", "TX"],
    default=[],
)

st.sidebar.subheader("Weight Range (g)")
col1, col2 = st.sidebar.columns(2)
weight_min = col1.number_input("Min", value=0.0, min_value=0.0, max_value=300.0, step=5.0)
weight_max = col2.number_input("Max", value=300.0, min_value=0.0, max_value=300.0, step=5.0)

st.sidebar.subheader("Torque Range (°)")
col3, col4 = st.sidebar.columns(2)
torque_min = col3.number_input("Min ", value=0.0, min_value=0.0, max_value=15.0, step=0.5)
torque_max = col4.number_input("Max ", value=15.0, min_value=0.0, max_value=15.0, step=0.5)

launch_profiles = st.sidebar.multiselect(
    "Launch Profile",
    options=["Low", "Low-Mid", "Mid", "Mid-High", "High"],
    default=[],
)

spin_profiles = st.sidebar.multiselect(
    "Spin Profile",
    options=["Low", "Low-Mid", "Mid", "Mid-High", "High"],
    default=[],
)

price_max = st.sidebar.number_input(
    "Max MSRP ($)",
    value=500.0,
    min_value=0.0,
    max_value=1000.0,
    step=25.0,
)

# --- Apply Filters ---
filtered = filter_shafts(
    df,
    manufacturers=manufacturers or None,
    club_types=club_types or None,
    flexes=flexes or None,
    weight_min=weight_min if weight_min > 0 else None,
    weight_max=weight_max if weight_max < 300 else None,
    torque_min=torque_min if torque_min > 0 else None,
    torque_max=torque_max if torque_max < 15 else None,
    launch_profiles=launch_profiles or None,
    spin_profiles=spin_profiles or None,
    price_max=price_max if price_max < 500 else None,
)

# --- Display Results ---
st.markdown(f"### Showing {len(filtered)} of {len(df)} shafts")

# Display columns
display_cols = [
    "manufacturer", "model", "generation", "club_type", "flex",
    "weight_grams", "torque_degrees", "launch", "spin",
    "kickpoint", "tip_stiff", "material", "msrp_usd",
]
available_cols = [c for c in display_cols if c in filtered.columns]

st.dataframe(
    filtered[available_cols].sort_values(["manufacturer", "model", "weight_grams"]),
    use_container_width=True,
    hide_index=True,
    column_config={
        "manufacturer": "Manufacturer",
        "model": "Model",
        "generation": "Gen",
        "club_type": "Type",
        "flex": "Flex",
        "weight_grams": st.column_config.NumberColumn("Weight (g)", format="%.1f"),
        "torque_degrees": st.column_config.NumberColumn("Torque (°)", format="%.1f"),
        "launch": "Launch",
        "spin": "Spin",
        "kickpoint": "Kickpoint",
        "tip_stiff": "Tip",
        "material": "Material",
        "msrp_usd": st.column_config.NumberColumn("MSRP ($)", format="$%.0f"),
    },
)

# --- Export ---
st.markdown("---")
col_a, col_b, _ = st.columns([1, 1, 3])
with col_a:
    csv_data = filtered[available_cols].to_csv(index=False)
    st.download_button("📥 Download CSV", csv_data, "shaft_specs.csv", "text/csv")
with col_b:
    json_data = filtered[available_cols].to_json(orient="records", indent=2)
    st.download_button("📥 Download JSON", json_data, "shaft_specs.json", "application/json")

# --- Quick Stats ---
st.markdown("---")
st.markdown("### Quick Stats")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Manufacturers", filtered["manufacturer"].nunique())
c2.metric("Models", filtered["model"].nunique())
c3.metric("Avg Weight", f"{filtered['weight_grams'].mean():.1f}g")
c4.metric(
    "Avg Torque",
    f"{filtered['torque_degrees'].dropna().mean():.1f}°"
    if not filtered["torque_degrees"].dropna().empty
    else "N/A"
)

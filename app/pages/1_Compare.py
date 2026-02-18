"""Golf Shaft Analytics — Compare: Side-by-side shaft comparison."""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.analysis.compare import compare_shafts
from src.ingestion.load_data import load_database
from src.ingestion.schemas import ShaftSpec

st.set_page_config(page_title="Compare Shafts", page_icon="⚖️", layout="wide")
st.title("⚖️ Compare Shafts")
st.markdown("Select up to 4 shafts for a side-by-side comparison.")


@st.cache_data
def get_specs() -> list[dict]:
    specs = load_database()
    return [s.model_dump() for s in specs]


specs_data = get_specs()

if not specs_data:
    st.warning("No shaft data loaded. Run `python -m src.ingestion.load_data` first.")
    st.stop()

# Build display names for selection
specs = [ShaftSpec(**s) for s in specs_data]
name_map = {s.display_name: s for s in specs}
sorted_names = sorted(name_map.keys())

selected = st.multiselect(
    "Select shafts to compare (max 4)",
    options=sorted_names,
    max_selections=4,
    default=[],
)

if selected:
    selected_specs = [name_map[name] for name in selected]
    comparison = compare_shafts(selected_specs)

    st.dataframe(comparison, use_container_width=True)

    # Visual comparison charts
    if len(selected_specs) >= 2:
        import plotly.graph_objects as go

        st.markdown("---")
        st.markdown("### Visual Comparison")

        names = [s.display_name for s in selected_specs]

        # Weight comparison
        weights = [s.weight_grams for s in selected_specs]
        fig_weight = go.Figure(
            data=[go.Bar(x=names, y=weights, marker_color=["#1B5E20", "#4CAF50", "#81C784", "#C8E6C9"][:len(names)])]
        )
        fig_weight.update_layout(title="Weight (g)", yaxis_title="Grams", height=350)
        st.plotly_chart(fig_weight, use_container_width=True)

        # Torque comparison
        torques = [s.torque_degrees if s.torque_degrees else 0 for s in selected_specs]
        if any(t > 0 for t in torques):
            fig_torque = go.Figure(
                data=[go.Bar(x=names, y=torques, marker_color=["#0D47A1", "#1976D2", "#64B5F6", "#BBDEFB"][:len(names)])]
            )
            fig_torque.update_layout(title="Torque (°)", yaxis_title="Degrees", height=350)
            st.plotly_chart(fig_torque, use_container_width=True)
else:
    st.info("👆 Select shafts above to begin comparing.")

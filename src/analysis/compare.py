"""Shaft comparison and analysis utilities."""

from typing import Optional

import pandas as pd

from ..ingestion.schemas import FLEX_ORDER, Flex, ShaftSpec


def compare_shafts(specs: list[ShaftSpec]) -> pd.DataFrame:
    """
    Create a side-by-side comparison DataFrame for a list of shafts.

    Returns a transposed DataFrame where columns are shaft names and rows are spec fields.
    """
    if not specs:
        return pd.DataFrame()

    rows = []
    for spec in specs:
        rows.append({
            "Shaft": spec.display_name,
            "Manufacturer": spec.manufacturer,
            "Model": spec.model,
            "Club Type": spec.club_type.value.title(),
            "Flex": spec.flex.value,
            "Weight (g)": spec.weight_grams,
            "Length (in)": spec.length_inches or "N/A",
            "Torque (°)": spec.torque_degrees or "N/A",
            "Launch": spec.launch.value if spec.launch else "N/A",
            "Spin": spec.spin.value if spec.spin else "N/A",
            "Kickpoint": spec.kickpoint.value if spec.kickpoint else "N/A",
            "Tip Stiffness": spec.tip_stiff.value if spec.tip_stiff else "N/A",
            "Tip (in)": spec.tip_diameter_inches or "N/A",
            "Butt (in)": spec.butt_diameter_inches or "N/A",
            "Material": spec.material.title(),
            "MSRP": f"${spec.msrp_usd:.0f}" if spec.msrp_usd else "N/A",
        })

    df = pd.DataFrame(rows).set_index("Shaft").T
    return df


def filter_shafts(
    df: pd.DataFrame,
    manufacturers: Optional[list[str]] = None,
    club_types: Optional[list[str]] = None,
    flexes: Optional[list[str]] = None,
    weight_min: Optional[float] = None,
    weight_max: Optional[float] = None,
    torque_min: Optional[float] = None,
    torque_max: Optional[float] = None,
    launch_profiles: Optional[list[str]] = None,
    spin_profiles: Optional[list[str]] = None,
    price_max: Optional[float] = None,
) -> pd.DataFrame:
    """Apply filters to a shaft database DataFrame."""
    filtered = df.copy()

    if manufacturers:
        filtered = filtered[filtered["manufacturer"].isin(manufacturers)]
    if club_types:
        filtered = filtered[filtered["club_type"].isin(club_types)]
    if flexes:
        filtered = filtered[filtered["flex"].isin(flexes)]
    if weight_min is not None:
        filtered = filtered[filtered["weight_grams"] >= weight_min]
    if weight_max is not None:
        filtered = filtered[filtered["weight_grams"] <= weight_max]
    if torque_min is not None:
        filtered = filtered[filtered["torque_degrees"].notna() & (filtered["torque_degrees"] >= torque_min)]
    if torque_max is not None:
        filtered = filtered[filtered["torque_degrees"].notna() & (filtered["torque_degrees"] <= torque_max)]
    if launch_profiles:
        filtered = filtered[filtered["launch"].isin(launch_profiles)]
    if spin_profiles:
        filtered = filtered[filtered["spin"].isin(spin_profiles)]
    if price_max is not None:
        filtered = filtered[filtered["msrp_usd"].notna() & (filtered["msrp_usd"] <= price_max)]

    return filtered


def weight_progression(df: pd.DataFrame, manufacturer: str, model: str) -> pd.DataFrame:
    """
    Get weight progression across flexes for a specific shaft model.

    Useful for visualizing how weight increases through a product line.
    """
    subset = df[(df["manufacturer"] == manufacturer) & (df["model"] == model)].copy()
    subset["flex_order"] = subset["flex"].map(lambda f: FLEX_ORDER.get(Flex(f), 3))
    return subset.sort_values("flex_order")

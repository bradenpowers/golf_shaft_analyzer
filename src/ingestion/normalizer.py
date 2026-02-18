"""Normalize raw shaft data from various manufacturer formats into the standard schema."""

import re
from typing import Optional

import pandas as pd

from .schemas import (
    ClubType,
    Flex,
    Kickpoint,
    LaunchProfile,
    ShaftSpec,
    SpinProfile,
    TipStiffness,
)

# --- Flex normalization mappings ---
FLEX_MAP: dict[str, Flex] = {
    "l": Flex.LADIES,
    "ladies": Flex.LADIES,
    "a": Flex.SENIOR,
    "sr": Flex.SENIOR,
    "senior": Flex.SENIOR,
    "r": Flex.REGULAR,
    "regular": Flex.REGULAR,
    "s": Flex.STIFF,
    "stiff": Flex.STIFF,
    "x": Flex.X_STIFF,
    "xs": Flex.X_STIFF,
    "x-stiff": Flex.X_STIFF,
    "xstiff": Flex.X_STIFF,
    "tx": Flex.TX,
    "xxx": Flex.TX,
}

LAUNCH_MAP: dict[str, LaunchProfile] = {
    "low": LaunchProfile.LOW,
    "low-mid": LaunchProfile.LOW_MID,
    "low/mid": LaunchProfile.LOW_MID,
    "mid": LaunchProfile.MID,
    "mid-high": LaunchProfile.MID_HIGH,
    "mid/high": LaunchProfile.MID_HIGH,
    "high": LaunchProfile.HIGH,
}

SPIN_MAP: dict[str, SpinProfile] = {
    "low": SpinProfile.LOW,
    "low-mid": SpinProfile.LOW_MID,
    "low/mid": SpinProfile.LOW_MID,
    "mid": SpinProfile.MID,
    "mid-high": SpinProfile.MID_HIGH,
    "mid/high": SpinProfile.MID_HIGH,
    "high": SpinProfile.HIGH,
}

KICKPOINT_MAP: dict[str, Kickpoint] = {
    "low": Kickpoint.LOW,
    "low-mid": Kickpoint.LOW_MID,
    "low/mid": Kickpoint.LOW_MID,
    "mid": Kickpoint.MID,
    "mid-high": Kickpoint.MID_HIGH,
    "mid/high": Kickpoint.MID_HIGH,
    "high": Kickpoint.HIGH,
    "front": Kickpoint.LOW,
    "front-mid": Kickpoint.LOW_MID,
    "rear": Kickpoint.HIGH,
}

TIP_STIFF_MAP: dict[str, TipStiffness] = {
    "soft": TipStiffness.SOFT,
    "medium": TipStiffness.MEDIUM,
    "med": TipStiffness.MEDIUM,
    "firm": TipStiffness.FIRM,
    "very firm": TipStiffness.VERY_FIRM,
    "extra firm": TipStiffness.VERY_FIRM,
}


def normalize_flex(raw: str) -> Flex:
    """Convert various flex representations to standard Flex enum."""
    cleaned = raw.strip().lower().replace(" ", "")
    if cleaned in FLEX_MAP:
        return FLEX_MAP[cleaned]
    # Try to extract flex from weight+flex combos like "6.0S" or "60X"
    match = re.search(r"[0-9.]+(s|r|x|tx|xs|a|l)$", cleaned)
    if match:
        return FLEX_MAP.get(match.group(1), Flex.STIFF)
    raise ValueError(f"Cannot normalize flex: '{raw}'")


def normalize_launch(raw: Optional[str]) -> Optional[LaunchProfile]:
    """Convert launch description to standard enum."""
    if not raw or pd.isna(raw):
        return None
    cleaned = raw.strip().lower()
    return LAUNCH_MAP.get(cleaned)


def normalize_spin(raw: Optional[str]) -> Optional[SpinProfile]:
    """Convert spin description to standard enum."""
    if not raw or pd.isna(raw):
        return None
    cleaned = raw.strip().lower()
    return SPIN_MAP.get(cleaned)


def normalize_kickpoint(raw: Optional[str]) -> Optional[Kickpoint]:
    """Convert kickpoint description to standard enum."""
    if not raw or pd.isna(raw):
        return None
    cleaned = raw.strip().lower()
    return KICKPOINT_MAP.get(cleaned)


def normalize_tip_stiffness(raw: Optional[str]) -> Optional[TipStiffness]:
    """Convert tip stiffness description to standard enum."""
    if not raw or pd.isna(raw):
        return None
    cleaned = raw.strip().lower()
    return TIP_STIFF_MAP.get(cleaned)


def safe_float(val) -> Optional[float]:
    """Safely convert a value to float, returning None on failure."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def normalize_row(row: dict, manufacturer: str, club_type: ClubType) -> ShaftSpec:
    """
    Normalize a single row of raw shaft data into a ShaftSpec.

    Expects a dict with keys matching common column names from manufacturer spec sheets.
    Handles variations in column naming across manufacturers.
    """
    # Extract model name — try common column names
    model = str(
        row.get("model")
        or row.get("shaft")
        or row.get("name")
        or row.get("product")
        or "Unknown"
    ).strip()

    generation = row.get("generation") or row.get("gen") or row.get("version")
    if generation:
        generation = str(generation).strip()

    # Flex
    flex_raw = str(
        row.get("flex") or row.get("stiffness") or row.get("Flex") or "S"
    )
    flex = normalize_flex(flex_raw)

    # Weight
    weight = safe_float(
        row.get("weight") or row.get("weight_grams") or row.get("wt")
    )
    if weight is None:
        raise ValueError(f"Missing weight for {model}")

    # Length
    length = safe_float(
        row.get("length") or row.get("length_inches") or row.get("raw_length")
    )

    # Torque
    torque = safe_float(
        row.get("torque") or row.get("torque_degrees")
    )

    # Launch, spin, kickpoint
    launch = normalize_launch(
        row.get("launch") or row.get("launch_profile")
    )
    spin = normalize_spin(
        row.get("spin") or row.get("spin_profile")
    )
    kickpoint = normalize_kickpoint(
        row.get("kickpoint") or row.get("kick_point") or row.get("bend_point")
    )
    tip_stiff = normalize_tip_stiffness(
        row.get("tip_stiff") or row.get("tip_stiffness") or row.get("tip")
    )

    # Diameters
    butt_dia = safe_float(row.get("butt_diameter") or row.get("butt"))
    tip_dia = safe_float(row.get("tip_diameter") or row.get("tip_dia"))

    # Material
    material = str(row.get("material", "graphite")).strip().lower()

    # Price
    msrp = safe_float(row.get("msrp") or row.get("msrp_usd") or row.get("price"))

    return ShaftSpec(
        manufacturer=manufacturer,
        model=model,
        generation=generation,
        club_type=club_type,
        flex=flex,
        weight_grams=weight,
        length_inches=length,
        torque_degrees=torque,
        launch=launch,
        spin=spin,
        butt_diameter_inches=butt_dia,
        tip_diameter_inches=tip_dia,
        tip_stiff=tip_stiff,
        kickpoint=kickpoint,
        material=material,
        msrp_usd=msrp,
    )


def normalize_dataframe(
    df: pd.DataFrame,
    manufacturer: str,
    club_type: ClubType,
) -> list[ShaftSpec]:
    """
    Normalize an entire DataFrame of raw shaft data.

    Returns a list of valid ShaftSpec objects. Logs warnings for rows that fail validation.
    """
    specs = []
    errors = []

    for idx, row in df.iterrows():
        try:
            spec = normalize_row(row.to_dict(), manufacturer, club_type)
            specs.append(spec)
        except (ValueError, KeyError) as e:
            errors.append(f"Row {idx}: {e}")

    if errors:
        print(f"⚠️  {len(errors)} rows failed normalization for {manufacturer}:")
        for err in errors[:5]:
            print(f"   {err}")
        if len(errors) > 5:
            print(f"   ... and {len(errors) - 5} more")

    print(f"✅ Normalized {len(specs)} shafts for {manufacturer} ({club_type.value})")
    return specs

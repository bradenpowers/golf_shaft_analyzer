"""Load and normalize shaft data from raw CSV files into the processed database."""

import json
from pathlib import Path

import pandas as pd

from .normalizer import normalize_dataframe
from .schemas import ClubType, ShaftSpec

DATA_DIR = Path(__file__).parent.parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DB_FILE = PROCESSED_DIR / "shaft_database.json"


def load_raw_csv(filepath: Path) -> pd.DataFrame:
    """Load a raw CSV file with shaft specifications."""
    df = pd.read_csv(filepath)
    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df


def detect_club_type(df: pd.DataFrame) -> dict[str, list[int]]:
    """
    Group rows by club type.

    If the dataframe has a 'club_type' column, use it.
    Otherwise, default to 'woods'.
    """
    if "club_type" in df.columns:
        groups = {}
        for idx, row in df.iterrows():
            ct = row["club_type"].strip().lower()
            groups.setdefault(ct, []).append(idx)
        return groups
    return {"woods": list(df.index)}


CLUB_TYPE_MAP = {
    "woods": ClubType.WOODS,
    "fairway": ClubType.FAIRWAY,
    "hybrid": ClubType.HYBRID,
    "iron": ClubType.IRON,
    "wedge": ClubType.WEDGE,
    "putter": ClubType.PUTTER,
}


def load_and_normalize(filepath: Path) -> list[ShaftSpec]:
    """Load a raw CSV and normalize all rows into ShaftSpec objects."""
    df = load_raw_csv(filepath)
    all_specs: list[ShaftSpec] = []

    # Group by manufacturer and club type
    if "manufacturer" in df.columns:
        for manufacturer, mfr_group in df.groupby("manufacturer"):
            type_groups = detect_club_type(mfr_group)
            for type_name, indices in type_groups.items():
                club_type = CLUB_TYPE_MAP.get(type_name, ClubType.WOODS)
                subset = mfr_group.loc[indices]
                specs = normalize_dataframe(subset, str(manufacturer), club_type)
                all_specs.extend(specs)
    else:
        raise ValueError("CSV must have a 'manufacturer' column")

    return all_specs


def save_database(specs: list[ShaftSpec], filepath: Path = DB_FILE) -> None:
    """Save normalized specs to JSON database."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    data = [spec.model_dump(mode="json") for spec in specs]
    filepath.write_text(json.dumps(data, indent=2))
    print(f"💾 Saved {len(data)} shafts to {filepath}")


def load_database(filepath: Path = DB_FILE) -> list[ShaftSpec]:
    """Load the processed shaft database."""
    if not filepath.exists():
        print("⚠️  No processed database found. Run load_data first.")
        return []
    data = json.loads(filepath.read_text())
    return [ShaftSpec(**item) for item in data]


def load_database_df(filepath: Path = DB_FILE) -> pd.DataFrame:
    """Load the processed shaft database as a pandas DataFrame."""
    specs = load_database(filepath)
    if not specs:
        return pd.DataFrame()
    return pd.DataFrame([spec.model_dump() for spec in specs])


def main():
    """Main entry point — load all raw CSVs and build the database."""
    all_specs: list[ShaftSpec] = []

    csv_files = list(RAW_DIR.glob("*.csv"))
    if not csv_files:
        print("❌ No CSV files found in data/raw/")
        return

    for csv_file in csv_files:
        print(f"\n📂 Processing {csv_file.name}...")
        specs = load_and_normalize(csv_file)
        all_specs.extend(specs)

    print(f"\n{'='*50}")
    print(f"Total shafts normalized: {len(all_specs)}")

    # Deduplicate by display_name
    seen = set()
    unique_specs = []
    for spec in all_specs:
        key = spec.display_name
        if key not in seen:
            seen.add(key)
            unique_specs.append(spec)

    print(f"Unique shafts after dedup: {len(unique_specs)}")
    save_database(unique_specs)


if __name__ == "__main__":
    main()

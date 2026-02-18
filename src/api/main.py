"""Golf Shaft Analytics REST API."""

import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.analysis.compare import filter_shafts
from src.ingestion.load_data import load_database, load_database_df
from src.ingestion.schemas import ShaftSpec

app = FastAPI(
    title="Golf Shaft Analytics API",
    description="Search, filter, and compare golf shaft specifications.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "Golf Shaft Analytics API",
        "version": "0.1.0",
        "endpoints": ["/shafts", "/shafts/search", "/manufacturers", "/stats"],
    }


@app.get("/shafts", response_model=list[dict])
def list_shafts(
    manufacturer: Optional[str] = Query(None, description="Filter by manufacturer"),
    club_type: Optional[str] = Query(None, description="Filter by club type"),
    flex: Optional[str] = Query(None, description="Filter by flex"),
    weight_min: Optional[float] = Query(None, description="Minimum weight in grams"),
    weight_max: Optional[float] = Query(None, description="Maximum weight in grams"),
    limit: int = Query(50, ge=1, le=500, description="Max results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """List shafts with optional filters."""
    df = load_database_df()
    if df.empty:
        return []

    filtered = filter_shafts(
        df,
        manufacturers=[manufacturer] if manufacturer else None,
        club_types=[club_type] if club_type else None,
        flexes=[flex] if flex else None,
        weight_min=weight_min,
        weight_max=weight_max,
    )

    result = filtered.iloc[offset : offset + limit]
    return result.to_dict(orient="records")


@app.get("/shafts/search", response_model=list[dict])
def search_shafts(
    q: str = Query(..., min_length=1, description="Search query (searches model and manufacturer)"),
):
    """Free-text search across shaft models and manufacturers."""
    df = load_database_df()
    if df.empty:
        return []

    query = q.lower()
    mask = (
        df["manufacturer"].str.lower().str.contains(query, na=False)
        | df["model"].str.lower().str.contains(query, na=False)
    )
    return df[mask].to_dict(orient="records")


@app.get("/manufacturers")
def list_manufacturers():
    """List all manufacturers in the database."""
    df = load_database_df()
    if df.empty:
        return []
    return sorted(df["manufacturer"].unique().tolist())


@app.get("/stats")
def database_stats():
    """Get database statistics."""
    df = load_database_df()
    if df.empty:
        return {"total_shafts": 0}

    return {
        "total_shafts": len(df),
        "manufacturers": int(df["manufacturer"].nunique()),
        "models": int(df["model"].nunique()),
        "club_types": df["club_type"].value_counts().to_dict(),
        "flex_distribution": df["flex"].value_counts().to_dict(),
        "weight_range": {
            "min": float(df["weight_grams"].min()),
            "max": float(df["weight_grams"].max()),
            "mean": round(float(df["weight_grams"].mean()), 1),
        },
    }

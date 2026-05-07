from fastapi import APIRouter, Query
from app.core.data_loader import df, resolve_player_id
import numpy as np
import pandas as pd
from app.core.player_resolver import (
    get_player_snapshot,
    get_player_history,
)
from app.core.year_utils import normalize_year
from app.data.cleaner import prepare_for_display

router = APIRouter()

SORTABLE_COLUMNS = set(df.columns)

PCT_COLS = [
    "off_usage",
    "off_assist",
    "off_to",
    "off_orb",
    "def_orb",
    "off_ftr",
    "def_stl",
    "def_blk",
    "off_threepr"
]

@router.get("/players")
def get_players(
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    sort: str = Query("adj_rapm_margin", description="Sort column"),
    order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    year: int | str | None = Query(None, description="Filter by year"),
    conf: str | None = Query(None, description="Filter by conference")
):
    """
    List players with filtering and pagination.
    
    This endpoint provides player listing functionality. For search functionality,
    use the /search endpoint.
    """
    year = normalize_year(year)
    data = df.copy()

    # -------------------------
    # YEAR FILTER
    # -------------------------
    if isinstance(year, int):
        data = data[data["year"] == year]

    # -------------------------
    # CONF FILTER
    # -------------------------
    if conf:
        data = data[data["conf"] == conf]

    total_filtered = len(data)

    # -------------------------
    # DATA PREPARATION
    # -------------------------
    # Numeric cleaning
    for col in data.columns:
        if col not in ["player_name", "player_code", "player_id", "team", "conf"]:
            data[col] = pd.to_numeric(data[col], errors="ignore")

    # Percentage conversion
    for col in PCT_COLS:
        if col in data.columns:
            data[col] = data[col] * 100

    # Sorting
    if sort in SORTABLE_COLUMNS:
        data = data.sort_values(
            by=[sort, "player_name"],
            ascending=(order == "asc")
        )

    # Pagination
    data = data.iloc[offset:offset + limit]
    data = data.replace({np.nan: None})

    return {
        "count": len(df),
        "filtered_count": total_filtered,
        "results": data.to_dict(orient="records")
    }


# -------------------------
# PLAYER PAGE
# -------------------------
@router.get("/players/{player_identifier}")
def get_player(player_identifier: str, year: int | str | None = None):
    """
    Get player data by either player_id or player_code.
    
    Args:
        player_identifier: Either player_id (preferred) or player_code (legacy)
        year: Year to get data for, or "career" for career stats
        
    Returns:
        Player data with available years
    """
    year = normalize_year(year)

    record = get_player_snapshot(player_identifier, year)

    if record is None:
        return {"error": "Player not found"}

    history = get_player_history(player_identifier)

    years = sorted(
        history["year"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    def nest_player(row):
        out = {}

        for k, v in row.items():
            if "." in k:
                parent, child = k.split(".", 1)
                out.setdefault(parent, {})
                out[parent][child] = None if pd.isna(v) else v
            else:
                out[k] = None if pd.isna(v) else v

        return out

    return {
        "player": nest_player(record),
        "available_years": years,
        "player_id": record.get("player_id"),  # Include new player_id for frontend migration
        "player_code": record.get("player_code")  # Keep legacy player_code for compatibility
    }
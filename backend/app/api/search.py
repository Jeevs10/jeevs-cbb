"""
Search API Routes
Handles all search functionality separated from player listing.
"""

from fastapi import APIRouter, Query
from app.core.data_loader import df
from app.core.year_utils import normalize_year
from app.data.merger import search_players
from app.data.cleaner import prepare_for_display
import numpy as np
import pandas as pd

router = APIRouter()

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

SORTABLE_COLUMNS = set(df.columns)

@router.get("/search")
def search_players_endpoint(
    q: str = Query(..., description="Search query for player names, teams, or player codes"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    year: int | str | None = Query(None, description="Filter by year"),
    conf: str | None = Query(None, description="Filter by conference"),
    sort: str = Query("adj_rapm_margin", description="Sort column"),
    order: str = Query("desc", regex="^(asc|desc)$", description="Sort order")
):
    """
    Search players by name, team, or player code.
    
    This endpoint provides dedicated search functionality separated from the players listing.
    """
    year = normalize_year(year)
    
    # Start with full dataset
    data = df.copy()
    
    # Apply search filter first (most selective)
    if q and q.strip():
        data = search_players(data, q.strip())
    
    # Apply additional filters
    if isinstance(year, int):
        data = data[data["year"] == year]
    
    if conf:
        data = data[data["conf"] == conf]
    
    total_filtered = len(data)
    
    # -------------------------
    # DATA PREPARATION
    # -------------------------
    # Numeric cleaning
    for col in data.columns:
        if col not in ["player_name", "player_code", "team", "conf"]:
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
        "query": q.strip(),
        "count": len(df),
        "filtered_count": total_filtered,
        "results": data.to_dict(orient="records")
    }


@router.get("/search/suggestions")
def search_suggestions(
    q: str = Query(..., description="Partial search query"),
    limit: int = Query(10, ge=1, le=50, description="Number of suggestions")
):
    """
    Get search suggestions for autocomplete.
    
    Returns player names and codes that match the partial query.
    """
    if not q or len(q.strip()) < 2:
        return {"suggestions": []}
    
    query = q.strip().lower()
    
    # Search in player names and codes
    name_matches = df[df["player_name"].str.lower().str.contains(query, na=False)]
    code_matches = df[df["player_code"].str.lower().str.contains(query, na=False)]
    
    # Combine and deduplicate
    combined = pd.concat([name_matches, code_matches]).drop_duplicates(subset=['player_id'])
    
    # Get unique players with their most recent data
    suggestions = (
        combined.sort_values(['player_id', 'year'])
               .groupby('player_id')
               .tail(1)
               .head(limit)
    )
    
    suggestions = suggestions.replace({np.nan: None})
    
    return {
        "query": q.strip(),
        "suggestions": [
            {
                "player_id": row["player_id"],
                "player_code": row["player_code"],
                "player_name": row["player_name"],
                "team": row["team"],
                "year": row["year"]
            }
            for _, row in suggestions.iterrows()
        ]
    }

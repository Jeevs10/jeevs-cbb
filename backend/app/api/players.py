from fastapi import APIRouter
from app.core.data_loader import df
import numpy as np
import pandas as pd
from app.core.player_resolver import (
    get_player_snapshot,
    get_player_history,
)
from app.core.year_utils import normalize_year

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

# -------------------------
# PRE-COMPUTE LOWERCASE COLUMNS (🔥 SPEED FIX)
# -------------------------
df["_player_name_lc"] = df["player_name"].fillna("").astype(str).str.lower()
df["_team_lc"] = df["team"].fillna("").astype(str).str.lower()
df["_player_code_lc"] = df["player_code"].fillna("").astype(str).str.lower()


@router.get("/players")
def get_players(
    limit: int = 50,
    offset: int = 0,
    sort: str = "adj_rapm_margin",
    order: str = "desc",
    year: int | str | None = None,
    conf: str | None = None,
    search: str | None = None,
):

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

    # -------------------------
    # SEARCH FILTER (IMPROVED)
    # -------------------------
    if search and search.strip():

        q = search.strip().lower()

        mask = (
            data["_player_name_lc"].str.contains(q, na=False) |
            data["_team_lc"].str.contains(q, na=False) |
            data["_player_code_lc"].str.contains(q, na=False)
        )

        data = data[mask]

    total_filtered = len(data)

    # -------------------------
    # NUMERIC CLEANING
    # -------------------------
    for col in data.columns:
        if col not in ["player_name", "player_code", "team", "conf"]:
            data[col] = pd.to_numeric(data[col], errors="ignore")

    # -------------------------
    # PERCENT CONVERSION
    # -------------------------
    for col in PCT_COLS:
        if col in data.columns:
            data[col] = data[col] * 100

    # -------------------------
    # SORT
    # -------------------------
    if sort in SORTABLE_COLUMNS:
        data = data.sort_values(
            by=[sort, "player_name"],
            ascending=(order == "asc")
        )

    # -------------------------
    # PAGINATION
    # -------------------------
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
@router.get("/players/{player_code}")
def get_player(player_code: str, year: int | str | None = None):

    year = normalize_year(year)

    record = get_player_snapshot(player_code, year)

    if record is None:
        return {"error": "Player not found"}

    history = get_player_history(player_code)

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
        "available_years": years
    }
from typing import Union
from app.core.data_loader import df
import pandas as pd
import numpy as np

# -------------------------
# CONFIG
# -------------------------

WEIGHT_COLUMN = "off_poss"

CATEGORICAL_FIELDS = {
    "player_name",
    "roster.ncaa_id",
    "team",
    "conf",
    "posClass",
    "roster.number",
    "roster.height",
    "roster.year_class",
    "roster.pos",
    "roster.origin",
    "Position",
}

# 🚨 CRITICAL: NEVER AGGREGATE THESE
EXCLUDE_FROM_CAREER_AGG = {
    "year",
}

# -------------------------
# CORE SNAPSHOT
# -------------------------

def get_player_snapshot(ncaa_id: str, year: Union[int, str, None] = None):
    # Convert to float to match dataframe dtype
    try:
        ncaa_id_float = float(ncaa_id)
    except (ValueError, TypeError):
        return None
    
    player = df[df["player_key"] == str(ncaa_id)]

    if player.empty:
        return None

    # CAREER MODE
    if year == "career":
        return build_career_snapshot(player)

    # YEAR MODE
    if year is not None:
        filtered = player[player["year"] == year]
        if not filtered.empty:
            player = filtered

    player = player.sort_values("year")
    return player.iloc[-1].to_dict()


# -------------------------
# CAREER SNAPSHOT BUILDER
# -------------------------

def build_career_snapshot(player_df: pd.DataFrame):
    player_df = player_df.copy()

    latest = player_df.sort_values("year").iloc[-1]

    out = {}

    # Determine data_tier: if any year has enriched data, career should be enriched
    is_enriched = False
    if "data_tier" in player_df.columns:
        has_enriched = (player_df["data_tier"] == "enriched").any()
        out["data_tier"] = "enriched" if has_enriched else "basic"
        is_enriched = has_enriched

    # keep categorical fields
    for col in CATEGORICAL_FIELDS:
        if col in player_df.columns:
            out[col] = latest.get(col)

    weight_col = WEIGHT_COLUMN if WEIGHT_COLUMN in player_df.columns else None
    numeric_cols = player_df.select_dtypes(include=[np.number]).columns

    # Stats that should use simple averages (percentages and rates)
    SIMPLE_AVERAGE_STATS = {
        "TrueShootingPct", "OffensiveRating", "DefensiveRating", "NetRating",
        "off_efg", "off_usage", "off_assist", "off_to", "off_ftr"
    }

    # First, calculate total games
    total_games = player_df["Games"].fillna(0).values.sum()

    for col in numeric_cols:
        if col in CATEGORICAL_FIELDS:
            continue
        if col in EXCLUDE_FROM_CAREER_AGG:
            continue

        values = player_df[col].fillna(0).values

        # Special handling for Games: sum
        if col == "Games":
            out[col] = float(total_games)
        # Use simple average for percentages and rates
        elif col in SIMPLE_AVERAGE_STATS:
            out[col] = float(values.mean())
        elif weight_col:
            weights = player_df[weight_col].fillna(0).values
            out[col] = float(np.average(values, weights=weights)) if weights.sum() > 0 else float(values.mean())
        else:
            out[col] = float(values.mean())

    # Explicitly calculate per-game stats from total columns
    per_game_calculations = [
        ("PPG", "Points"),
        ("APG", "Assists"),
        ("RPG", "Rebounds Total"),
        ("SPG", "Steals"),
        ("BPG", "Blocks"),
        ("MPG", "Minutes"),
        ("ORB_PG", "Rebounds Offensive"),
        ("DRB_PG", "Rebounds Defensive"),
    ]

    for per_game_col, total_col in per_game_calculations:
        if total_col in player_df.columns:
            total_stat = player_df[total_col].fillna(0).values.sum()
            out[per_game_col] = float(total_stat / total_games) if total_games > 0 else 0

    # ✅ FIX: explicit mode flag
    years = sorted(player_df["year"].dropna().astype(int).unique().tolist())

    out["year"] = "career"   # 🔥 CRITICAL FIX
    out["is_career"] = True

    if len(years) == 1:
        out["career_year_label"] = str(years[0])
    else:
        out["career_year_label"] = f"{years[0]}–{years[-1]}"

    return out


# -------------------------
# HISTORY
# -------------------------

def get_player_history(ncaa_id: str):
    # Use player_key instead of roster.ncaa_id to support both basic and enriched players
    return df[df["player_key"] == str(ncaa_id)].sort_values("year")
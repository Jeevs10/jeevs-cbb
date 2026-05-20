from app.core.data_loader import df
from app.features.vectors import build_style_vector, build_impact_vector
import numpy as np
import pandas as pd

PLAYER_VECTORS = {}
PLAYER_INDEX = []
PLAYER_INFO = {}

# -------------------------
# GLOBAL RAPM STORAGE
# -------------------------
ALL_RAPM_VALUES = []


def percentile_rank(value):
    """Calculate percentile rank of a value within ALL_RAPM_VALUES"""
    if not ALL_RAPM_VALUES:
        return 0.5  # Default to middle if no data
    
    values = np.array(ALL_RAPM_VALUES)
    if len(values) == 0:
        return 0.5
    
    # Calculate percentile: (count of values less than this value) / (total count - 1)
    return (np.sum(values < value) / (len(values) - 1))


def safe_year(y):
    try:
        if y is None:
            return None
        return int(float(y))
    except:
        return None


def get_name_from_row(player):
    return (
        player.get("player_name")
        or player.get("Name")
        or player.get("name")
        or player.get("player")
        or player.get("playerName")
    )


def build_cache():
    global PLAYER_VECTORS, PLAYER_INDEX, PLAYER_INFO, ALL_RAPM_VALUES

    PLAYER_VECTORS.clear()
    PLAYER_INDEX.clear()
    PLAYER_INFO.clear()
    ALL_RAPM_VALUES = []

    print("[CACHE] building player vectors...")

    # -------------------------
    # PASS 1: BUILD RAW + COLLECT RAPM
    # -------------------------
    raw_rows = []

    for _, row in df.iterrows():
        player = row.to_dict()

        # Only process enriched players (those with roster.ncaa_id)
        ncaa_id = player.get("roster.ncaa_id")
        year = safe_year(player.get("year"))

        # Skip basic players (those without roster.ncaa_id)
        if not ncaa_id or pd.isna(ncaa_id) or year is None:
            continue

        # Calculate composite RAPM percentile from existing percentile fields
        pctile_off_adj_rapm = player.get("pctile_off_adj_rapm")
        pctile_def_adj_rapm = player.get("pctile_def_adj_rapm")
        pctile_off_adj_rapm_prod = player.get("pctile_off_adj_rapm_prod")
        pctile_def_adj_rapm_prod = player.get("pctile_def_adj_rapm_prod")
        pctile_adj_rapm_margin = player.get("pctile_adj_rapm_margin")
        pctile_adj_rapm_prod_margin = player.get("pctile_adj_rapm_prod_margin")
        
        # Collect valid percentile values
        percentile_values = []
        for val in [pctile_off_adj_rapm, pctile_def_adj_rapm, pctile_off_adj_rapm_prod, 
                   pctile_def_adj_rapm_prod, pctile_adj_rapm_margin, pctile_adj_rapm_prod_margin]:
            if val is not None and not pd.isna(val):
                try:
                    percentile_values.append(float(val))
                except:
                    pass
        
        # Calculate composite RAPM percentile as average of available percentiles
        if percentile_values:
            composite_rapm_pct = sum(percentile_values) / len(percentile_values)
        else:
            composite_rapm_pct = 0.5  # Default to middle if no data

        raw_rows.append((player, ncaa_id, year, composite_rapm_pct))

    # -------------------------
    # PASS 2: BUILD STRUCTURES
    # -------------------------
    for player, ncaa_id, year, composite_rapm_pct in raw_rows:

        style_vec = np.nan_to_num(build_style_vector(player))
        impact_vec = np.nan_to_num(build_impact_vector(player))

        player_name = get_name_from_row(player)
        team = player.get("team")
        pos = player.get("pos") or player.get("position")

        # Use the composite percentile directly (already calculated from existing percentile fields)
        rapm_pct = composite_rapm_pct

        if ncaa_id not in PLAYER_VECTORS:
            PLAYER_VECTORS[ncaa_id] = {}

        PLAYER_VECTORS[ncaa_id][year] = {
            "style": style_vec,
            "impact": impact_vec,

            # 🔥 CLEAN SINGLE SOURCE OF TRUTH
            "rapm": composite_rapm_pct,
            "rapm_pct": rapm_pct,

            "player_name": player_name,
            "team": team,
            "pos": pos,
        }

        if ncaa_id not in PLAYER_INFO:
            PLAYER_INFO[ncaa_id] = {
                "player_name": player_name or ncaa_id,
                "team": team,
                "pos": pos,
            }

        PLAYER_INDEX.append((ncaa_id, year))

    print("[CACHE DONE]", len(PLAYER_VECTORS))
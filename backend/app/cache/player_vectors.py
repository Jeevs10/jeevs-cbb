from app.core.data_loader import df
from app.features.vectors import build_style_vector, build_impact_vector
import numpy as np
import pandas as pd
import pickle
import os
import json

PLAYER_VECTORS = {}
PLAYER_INDEX = []
PLAYER_INFO = {}

# -------------------------
# GLOBAL METRIC STORAGE
# -------------------------
ALL_RAPM_VALUES = []
ALL_BPM_VALUES = []
ALL_VORP_VALUES = []

# -------------------------
# CACHE FILE PATH
# -------------------------
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "player_vectors_cache.pkl")
CACHE_METADATA_FILE = os.path.join(CACHE_DIR, "player_vectors_cache_metadata.json")

# -------------------------
# DATA FILES TO TRACK FOR CACHE INVALIDATION
# -------------------------
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATA_FILES_TO_TRACK = [
    os.path.join(DATA_DIR, "players", "2019-PlayerData.csv"),
    os.path.join(DATA_DIR, "players", "2020-PlayerData.csv"),
    os.path.join(DATA_DIR, "players", "2021-PlayerData.csv"),
    os.path.join(DATA_DIR, "players", "2022-PlayerData.csv"),
    os.path.join(DATA_DIR, "players", "2023-PlayerData.csv"),
    os.path.join(DATA_DIR, "players", "2024-PlayerData.csv"),
    os.path.join(DATA_DIR, "players", "2025-PlayerData.csv"),
    os.path.join(DATA_DIR, "players", "2026-PlayerData.csv"),
    os.path.join(DATA_DIR, "players", "2025-roster-info.csv"),
    os.path.join(DATA_DIR, "players", "2026-roster-info.csv"),
]


def percentile_rank(value, metric_values):
    """Calculate percentile rank of a value within the provided metric values"""
    if not metric_values:
        return 0.5  # Default to middle if no data
    
    values = np.array(metric_values)
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


def get_data_file_mod_times():
    """Get modification times of all tracked data files."""
    mod_times = {}
    for file_path in DATA_FILES_TO_TRACK:
        if os.path.exists(file_path):
            mod_times[file_path] = os.path.getmtime(file_path)
        else:
            mod_times[file_path] = None
    return mod_times

def is_cache_valid():
    """Check if the cache is still valid by comparing data file modification times."""
    if not os.path.exists(CACHE_METADATA_FILE):
        return False
    
    try:
        with open(CACHE_METADATA_FILE, 'r') as f:
            metadata = json.load(f)
        
        cached_mod_times = metadata.get("data_file_mod_times", {})
        current_mod_times = get_data_file_mod_times()
        
        # Check if any tracked data file has been modified since cache was built
        for file_path, cached_time in cached_mod_times.items():
            current_time = current_mod_times.get(file_path)
            if current_time is None:
                # File no longer exists, cache is invalid
                return False
            if cached_time is None:
                # File was missing when cache was built but exists now, cache is invalid
                return False
            if current_time > cached_time:
                # File has been modified, cache is invalid
                return False
        
        return True
    except Exception as e:
        return False

def save_cache():
    """Save the cache to disk for faster startup."""
    global PLAYER_VECTORS, PLAYER_INDEX, PLAYER_INFO, ALL_RAPM_VALUES, ALL_BPM_VALUES, ALL_VORP_VALUES
    
    # Ensure cache directory exists
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    cache_data = {
        "PLAYER_VECTORS": PLAYER_VECTORS,
        "PLAYER_INDEX": PLAYER_INDEX,
        "PLAYER_INFO": PLAYER_INFO,
        "ALL_RAPM_VALUES": ALL_RAPM_VALUES,
        "ALL_BPM_VALUES": ALL_BPM_VALUES,
        "ALL_VORP_VALUES": ALL_VORP_VALUES,
    }
    
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(cache_data, f)
    
    # Save metadata including data file modification times
    metadata = {
        "built_at": os.path.getmtime(CACHE_FILE),
        "data_file_mod_times": get_data_file_mod_times(),
        "num_players": len(PLAYER_VECTORS),
    }
    
    with open(CACHE_METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)
    

def load_cache():
    """Load the cache from disk if available."""
    global PLAYER_VECTORS, PLAYER_INDEX, PLAYER_INFO, ALL_RAPM_VALUES, ALL_BPM_VALUES, ALL_VORP_VALUES
    
    if not os.path.exists(CACHE_FILE):
        return False
    
    try:
        with open(CACHE_FILE, 'rb') as f:
            cache_data = pickle.load(f)
        
        PLAYER_VECTORS = cache_data.get("PLAYER_VECTORS", {})
        PLAYER_INDEX = cache_data.get("PLAYER_INDEX", [])
        PLAYER_INFO = cache_data.get("PLAYER_INFO", {})
        ALL_RAPM_VALUES = cache_data.get("ALL_RAPM_VALUES", [])
        ALL_BPM_VALUES = cache_data.get("ALL_BPM_VALUES", [])
        ALL_VORP_VALUES = cache_data.get("ALL_VORP_VALUES", [])
        
        return True
    except Exception as e:
        return False

def build_cache(force_rebuild=False):
    global PLAYER_VECTORS, PLAYER_INDEX, PLAYER_INFO, ALL_RAPM_VALUES, ALL_BPM_VALUES, ALL_VORP_VALUES

    # Try to load from cache first, but only if cache is valid
    if not force_rebuild and is_cache_valid() and load_cache():
        return
    
    if not force_rebuild and not is_cache_valid():
        pass

    PLAYER_VECTORS.clear()
    PLAYER_INDEX.clear()
    PLAYER_INFO.clear()
    ALL_RAPM_VALUES = []
    ALL_BPM_VALUES = []
    ALL_VORP_VALUES = []


    # -------------------------
    # PASS 1: BUILD RAW + COLLECT METRICS
    # -------------------------
    raw_rows = []
    skipped_count = 0
    total_rows = 0

    for _, row in df.iterrows():
        total_rows += 1
        player = row.to_dict()

        # Try to get ncaa_id from roster.ncaa_id first, fallback to AthleteSourceId
        ncaa_id = player.get("roster.ncaa_id") or player.get("AthleteSourceId")
        year = safe_year(player.get("year"))

        # Skip if no ID or year
        if not ncaa_id or pd.isna(ncaa_id) or year is None:
            skipped_count += 1
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

        # Get BPM and VORP values
        bpm = player.get("BPM")
        vorp = player.get("VORP")
        
        # Collect valid BPM and VORP values
        if bpm is not None and not pd.isna(bpm):
            try:
                ALL_BPM_VALUES.append(float(bpm))
            except:
                pass
        
        if vorp is not None and not pd.isna(vorp):
            try:
                ALL_VORP_VALUES.append(float(vorp))
            except:
                pass

        raw_rows.append((player, ncaa_id, year, composite_rapm_pct, bpm, vorp))

    # -------------------------
    # PASS 2: BUILD STRUCTURES
    # -------------------------
    
    for player, ncaa_id, year, composite_rapm_pct, bpm, vorp in raw_rows:

        style_vec = np.nan_to_num(build_style_vector(player))
        impact_vec = np.nan_to_num(build_impact_vector(player))

        player_name = get_name_from_row(player)
        team = player.get("team")
        pos = player.get("pos") or player.get("position")

        # Use the composite percentile directly (already calculated from existing percentile fields)
        rapm_pct = composite_rapm_pct
        
        # Calculate BPM and VORP percentiles
        bpm_pct = percentile_rank(bpm, ALL_BPM_VALUES) if bpm is not None and not pd.isna(bpm) else 0.5
        vorp_pct = percentile_rank(vorp, ALL_VORP_VALUES) if vorp is not None and not pd.isna(vorp) else 0.5

        if ncaa_id not in PLAYER_VECTORS:
            PLAYER_VECTORS[ncaa_id] = {}

        PLAYER_VECTORS[ncaa_id][year] = {
            "style": style_vec,
            "impact": impact_vec,

            # 🔥 CLEAN SINGLE SOURCE OF TRUTH
            "rapm": composite_rapm_pct,
            "rapm_pct": rapm_pct,
            "bpm": bpm,
            "bpm_pct": bpm_pct,
            "vorp": vorp,
            "vorp_pct": vorp_pct,

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

    
    # Save to disk for future startups
    save_cache()
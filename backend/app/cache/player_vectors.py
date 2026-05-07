from app.core.data_loader import df
from app.features.vectors import build_style_vector, build_impact_vector
import numpy as np

PLAYER_VECTORS = {}
PLAYER_INDEX = []
PLAYER_INFO = {}

# -------------------------
# GLOBAL RAPM STORAGE
# -------------------------
ALL_RAPM_VALUES = []


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

        code = player.get("player_code")
        year = safe_year(player.get("year"))

        if not code or year is None:
            continue

        rapm = player.get("pctile_adj_rapm_margin")

        try:
            rapm = float(rapm)
            if rapm > 1:
                rapm /= 100.0
        except:
            rapm = 0.0

        ALL_RAPM_VALUES.append(rapm)

        raw_rows.append((player, code, year, rapm))

    # -------------------------
    # GLOBAL PERCENTILE MAP
    # -------------------------
    ALL_RAPM_VALUES = np.array(ALL_RAPM_VALUES)

    def percentile_rank(x):
        return np.mean(ALL_RAPM_VALUES <= x)

    # -------------------------
    # PASS 2: BUILD STRUCTURES
    # -------------------------
    for player, code, year, rapm in raw_rows:

        style_vec = np.nan_to_num(build_style_vector(player))
        impact_vec = np.nan_to_num(build_impact_vector(player))

        player_name = get_name_from_row(player)
        team = player.get("team")
        pos = player.get("pos") or player.get("position")

        rapm_pct = percentile_rank(rapm)

        if code not in PLAYER_VECTORS:
            PLAYER_VECTORS[code] = {}

        PLAYER_VECTORS[code][year] = {
            "style": style_vec,
            "impact": impact_vec,

            # 🔥 CLEAN SINGLE SOURCE OF TRUTH
            "rapm": rapm,
            "rapm_pct": rapm_pct,

            "player_name": player_name,
            "team": team,
            "pos": pos,
        }

        if code not in PLAYER_INFO:
            PLAYER_INFO[code] = {
                "player_name": player_name or code,
                "team": team,
                "pos": pos,
            }

        PLAYER_INDEX.append((code, year))

    print("[CACHE DONE]", len(PLAYER_VECTORS))
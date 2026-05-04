from app.core.data_loader import df
from app.features.vectors import build_style_vector, build_impact_vector
import numpy as np

PLAYER_VECTORS = {}
PLAYER_INDEX = []


def safe_year(y):
    try:
        if y is None:
            return None
        return int(float(y))
    except:
        return None


def build_cache():
    global PLAYER_VECTORS, PLAYER_INDEX

    PLAYER_VECTORS.clear()
    PLAYER_INDEX.clear()

    for _, row in df.iterrows():
        player = row.to_dict()

        code = player.get("player_code")
        year = safe_year(player.get("year"))

        # 🔥 IMPORTANT FIX: do NOT drop silently unless BOTH invalid
        if not code:
            continue

        if year is None:
            continue

        style_vec = build_style_vector(player)
        impact_vec = build_impact_vector(player)

        style_vec = np.nan_to_num(style_vec, nan=0.0)
        impact_vec = np.nan_to_num(impact_vec, nan=0.0)

        if code not in PLAYER_VECTORS:
            PLAYER_VECTORS[code] = {}

        PLAYER_VECTORS[code][year] = {
            "style": style_vec,
            "impact": impact_vec
        }

        PLAYER_INDEX.append((code, year))

    print("PLAYER COUNT:", len(PLAYER_VECTORS))
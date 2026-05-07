import numpy as np

# -------------------------
# SAFE PARSING
# -------------------------

def safe(v):
    try:
        if v is None:
            return 0.0
        v = float(v)
        if np.isnan(v) or np.isinf(v):
            return 0.0
        return v
    except:
        return 0.0


# -------------------------
# MAIN ENTRY
# -------------------------

def build_player_vector(player: dict):
    return {
        "style": build_style_vector(player),
        "impact": build_impact_vector(player),
    }


# -------------------------
# STYLE VECTOR
# -------------------------

def build_style_vector(player):
    vec = np.array([
        safe(player.get("pctile_off_usage")),
        safe(player.get("pctile_off_assist")),
        1.0 - safe(player.get("pctile_off_to")),

        safe(player.get("pctile_off_threep")),

        safe(player.get("pctile_off_style_rim_attack_usg")),
        safe(player.get("pctile_off_style_mid_range_usg")),
        safe(player.get("pctile_off_style_transition_usg")),
        safe(player.get("pctile_off_style_post_up_usg")),

        safe(player.get("pctile_off_ftr")),
        safe(player.get("pctile_off_efg")),
    ], dtype=float)

    return np.nan_to_num(vec, nan=0.0, posinf=0.0, neginf=0.0)


# -------------------------
# IMPACT VECTOR (FOR SIMILARITY ONLY)
# -------------------------
# IMPORTANT: DO NOT MIX WITH RTG OR DUPLICATES

def build_impact_vector(player):
    vec = np.array([
        safe(player.get("pctile_adj_rapm_margin")),
        safe(player.get("pctile_off_adj_rapm")),
        safe(player.get("pctile_def_adj_rapm")),

        safe(player.get("pctile_off_efg")),
        safe(player.get("pctile_off_usage")),
        safe(player.get("pctile_def_stl")),
        safe(1 - player.get("pctile_def_blk")),
    ], dtype=float)

    return np.nan_to_num(vec, nan=0.0, posinf=0.0, neginf=0.0)
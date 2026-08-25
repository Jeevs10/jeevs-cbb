import numpy as np
import pandas as pd

STYLE_COLS = [
    "pctile_off_usage",
    "pctile_off_assist",
    "pctile_off_to",  # inverted: 1 - value
    "pctile_off_threep",
    "pctile_off_style_rim_attack_usg",
    "pctile_off_style_mid_range_usg",
    "pctile_off_style_transition_usg",
    "pctile_off_style_post_up_usg",
    "pctile_off_ftr",
    "pctile_off_efg",
]

IMPACT_COLS = [
    "pctile_adj_rapm_margin",
    "pctile_off_adj_rapm",
    "pctile_def_adj_rapm",
    "pctile_off_efg",
    "pctile_off_usage",
    "pctile_def_stl",
    "pctile_def_blk",
]


def _safe_series(df, col):
    """Vectorized equivalent of safe(player.get(col)) applied to a whole column."""
    if col in df.columns:
        s = pd.to_numeric(df[col], errors="coerce")
    else:
        s = pd.Series(0.0, index=df.index)
    return s.replace([np.inf, -np.inf], np.nan).fillna(0.0)


def build_style_vectors_batch(df):
    """Vectorized equivalent of calling build_style_vector(row) for every row.
    Returns an (n_rows, len(STYLE_COLS)) array in df's row order."""
    cols = []
    for col in STYLE_COLS:
        s = _safe_series(df, col)
        if col == "pctile_off_to":
            s = 1.0 - s
        cols.append(s.to_numpy(dtype=float))
    return np.column_stack(cols)


def build_impact_vectors_batch(df):
    """Vectorized equivalent of calling build_impact_vector(row) for every row.
    Returns an (n_rows, len(IMPACT_COLS)) array in df's row order."""
    cols = [_safe_series(df, col).to_numpy(dtype=float) for col in IMPACT_COLS]
    return np.column_stack(cols)


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


def build_player_vector(player: dict):
    return {
        "style": build_style_vector(player),
        "impact": build_impact_vector(player),
    }


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


def build_impact_vector(player):
    vec = np.array([
        safe(player.get("pctile_adj_rapm_margin")),
        safe(player.get("pctile_off_adj_rapm")),
        safe(player.get("pctile_def_adj_rapm")),

        safe(player.get("pctile_off_efg")),
        safe(player.get("pctile_off_usage")),
        safe(player.get("pctile_def_stl")),
        safe(player.get("pctile_def_blk")),
    ], dtype=float)

    return np.nan_to_num(vec, nan=0.0, posinf=0.0, neginf=0.0)
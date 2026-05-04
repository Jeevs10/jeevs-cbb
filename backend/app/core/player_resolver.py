from app.core.data_loader import df
import pandas as pd
import numpy as np

# -------------------------
# CONFIG
# -------------------------

WEIGHT_COLUMN = "off_poss"

CATEGORICAL_FIELDS = {
    "player_name",
    "player_code",
    "team",
    "conf",
    "posClass",
    "roster.ncaa_id",
    "roster.number",
    "roster.height",
    "roster.year_class",
    "roster.pos",
    "roster.origin",
}

# 🚨 CRITICAL: NEVER AGGREGATE THESE
EXCLUDE_FROM_CAREER_AGG = {
    "year",
}

# -------------------------
# CORE SNAPSHOT
# -------------------------

def get_player_snapshot(player_code: str, year: int | str | None = None):
    player = df[df["player_code"] == player_code]

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

    # keep categorical fields
    for col in CATEGORICAL_FIELDS:
        if col in player_df.columns:
            out[col] = latest.get(col)

    weight_col = WEIGHT_COLUMN if WEIGHT_COLUMN in player_df.columns else None
    numeric_cols = player_df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        if col in CATEGORICAL_FIELDS:
            continue
        if col in EXCLUDE_FROM_CAREER_AGG:
            continue

        values = player_df[col].fillna(0).values

        if weight_col:
            weights = player_df[weight_col].fillna(0).values
            out[col] = float(np.average(values, weights=weights)) if weights.sum() > 0 else float(values.mean())
        else:
            out[col] = float(values.mean())

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

def get_player_history(player_code: str):
    return df[df["player_code"] == player_code].sort_values("year")
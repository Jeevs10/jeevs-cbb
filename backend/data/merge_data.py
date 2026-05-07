import pandas as pd
import numpy as np

old_df = pd.read_csv("backend/data/2024-players.csv")
new_df = pd.read_csv("backend/data/2024-PlayerData.csv")

# -------------------------
# CLEAN IDS
# -------------------------
def clean_id(x):
    if pd.isna(x):
        return np.nan
    return str(x).replace(".0", "").strip()

old_df["roster.ncaa_id"] = old_df["roster.ncaa_id"].apply(clean_id)
new_df["AthleteSourceId"] = new_df["AthleteSourceId"].apply(clean_id)

# -------------------------
# CLEAN YEAR
# -------------------------
def clean_year(x):
    try:
        x = str(x)
        if "/" in x:
            return int(x.split("/")[-1]) + 2000
        return int(float(x))
    except:
        return np.nan

old_df["year"] = old_df["year"].apply(clean_year)
new_df["Season"] = pd.to_numeric(new_df["Season"], errors="coerce")

old_df = old_df[old_df["year"].notna()]
new_df = new_df[new_df["Season"].notna()]

# -------------------------
# DEDUPE (CRITICAL FIX)
# one row per player-season
# -------------------------
old_df = old_df.drop_duplicates(subset=["roster.ncaa_id", "year"])
new_df = new_df.drop_duplicates(subset=["AthleteSourceId", "Season"])

# -------------------------
# ALIGN KEYS
# -------------------------
new_df = new_df.rename(columns={
    "AthleteSourceId": "roster.ncaa_id",
    "Season": "year"
})

# -------------------------
# MERGE (KEEP ALL PLAYERS)
# -------------------------
merged = old_df.merge(
    new_df,
    on=["roster.ncaa_id", "year"],
    how="right",   # 🔥 IMPORTANT: keeps ALL players
    suffixes=("", "_new")
)

# -------------------------
# OPTIONAL: sanity check
# -------------------------
print("Old rows:", len(old_df))
print("New rows:", len(new_df))
print("Merged rows:", len(merged))

# -------------------------
# SAVE
# -------------------------
merged.to_csv("backend/data/2024-players_enriched.csv", index=False)
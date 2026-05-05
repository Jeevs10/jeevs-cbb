import pandas as pd

old_df = pd.read_csv("backend/data/2025_players.csv")
new_df = pd.read_csv("backend/data/2025-PlayerData.csv")

# -------------------------
# Normalize years
# -------------------------
def normalize_year(val):
    if pd.isna(val):
        return None

    val = str(val)

    # handle "2025/26"
    if "/" in val:
        return int(val.split("/")[-1]) + 2000

    return int(val)

old_df["year"] = old_df["year"].apply(normalize_year)
new_df["Season"] = pd.to_numeric(new_df["Season"], errors="coerce")

# -------------------------
# Merge (ONLY overlapping players)
# -------------------------
merged = old_df.merge(
    new_df,
    left_on=["roster.ncaa_id", "year"],
    right_on=["AthleteSourceId", "Season"],
    how="inner"
)

# -------------------------
# Save
# -------------------------
merged.to_csv("backend/data/players_enriched.csv", index=False)
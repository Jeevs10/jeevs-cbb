import pandas as pd
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PLAYERS_DIR = BASE_DIR / "players"

def merge_data_for_year(year):
    """Merge advanced player data with basic player data for a specific year"""
    print(f"Merging data for {year}...")
    
    # Load data files
    old_df = pd.read_csv(PLAYERS_DIR / f"{year}-players.csv")
    new_df = pd.read_csv(PLAYERS_DIR / f"{year}-PlayerData.csv")

# -------------------------
    # Normalize years
    # -------------------------
    def normalize_year(val):
        if pd.isna(val):
            return None

        val = str(val)

        # handle "2018/9" (2018-2019 season) -> 2019
        if "/" in val:
            return int(val.split("/")[0]) + 1

        return int(val)

    old_df["year"] = old_df["year"].apply(normalize_year)
    new_df["Season"] = pd.to_numeric(new_df["Season"], errors="coerce")

    # -------------------------
    # Merge (ONLY overlapping players)
    # -------------------------
    # Convert IDs to strings and clean float values for proper matching
    old_df["roster.ncaa_id_clean"] = old_df["roster.ncaa_id"].astype(str).str.replace('.0', '', regex=False)
    new_df["AthleteSourceId_str"] = new_df["AthleteSourceId"].astype(str)

    merged = old_df.merge(
        new_df,
        left_on=["roster.ncaa_id_clean", "year"],
        right_on=["AthleteSourceId_str", "Season"],
        how="inner"
    )

    # Clean up temporary columns
    merged = merged.drop(['roster.ncaa_id_clean', 'AthleteSourceId_str'], axis=1)

    # -------------------------
    # Save
    # -------------------------
    output_file = PLAYERS_DIR / f"{year}-players_enriched.csv"
    merged.to_csv(output_file, index=False)
    
    print(f"✓ Created {output_file} with {len(merged):,} enriched players")
    return merged

if __name__ == "__main__":
    # Get year from command line argument or use default
    year = sys.argv[1] if len(sys.argv) > 1 else "2024"
    
    # Merge data for the specified year
    merge_data_for_year(year)
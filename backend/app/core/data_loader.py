import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def load_enriched_players():
    """Load enriched players with advanced metrics (subset of all players)"""
    csv_2024 = os.path.join(BASE_DIR, "data", "2024-players_enriched.csv")
    csv_2025 = os.path.join(BASE_DIR, "data", "2025-players_enriched.csv")
    csv_2026 = os.path.join(BASE_DIR, "data", "2026-players_enriched.csv")

    df_2024 = pd.read_csv(csv_2024)
    df_2025 = pd.read_csv(csv_2025)
    df_2026 = pd.read_csv(csv_2026)

    # Force clean year format
    df_2024["year"] = 2024
    df_2025["year"] = 2025
    df_2026["year"] = 2026

    df = pd.concat([df_2024, df_2025, df_2026], ignore_index=True)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").fillna(0).astype(int)
    
    # Mark as enriched data
    df["data_tier"] = "enriched"
    
    return df

def load_basic_players():
    """Load all players with basic stats (complete coverage)"""
    csv_2024 = os.path.join(BASE_DIR, "data", "2024-players_basic.csv")
    csv_2025 = os.path.join(BASE_DIR, "data", "2025-players_basic.csv")
    csv_2026 = os.path.join(BASE_DIR, "data", "2026-players_basic.csv")

    df_2024 = pd.read_csv(csv_2024)
    df_2025 = pd.read_csv(csv_2025)
    df_2026 = pd.read_csv(csv_2026)

    # Force clean year format
    df_2024["year"] = 2024
    df_2025["year"] = 2025
    df_2026["year"] = 2026

    df = pd.concat([df_2024, df_2025, df_2026], ignore_index=True)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").fillna(0).astype(int)
    
    # Map basic player fields to match enriched player field names
    df["player_name"] = df["Name"]
    df["team"] = df["Team"]
    df["conf"] = df["Conference"]
    
    # Mark as basic data
    df["data_tier"] = "basic"
    
    return df

def load_all_players():
    """Load both basic and enriched players, preferring enriched when available"""
    basic_df = load_basic_players()
    enriched_df = load_enriched_players()
    
    # Filter out D2 players (no conference) from basic data to improve performance
    basic_df = basic_df[basic_df['conf'].notna() & (basic_df['conf'] != '')]
    
    # Combine datasets, enriched data takes precedence
    # Use roster.ncaa_id/AthleteSourceId as the key
    basic_df['player_key'] = basic_df['AthleteSourceId'].astype(str)
    enriched_df['player_key'] = enriched_df['roster.ncaa_id'].astype(str).str.replace('.0', '', regex=False)
    
    # Preserve Position from basic data before combining
    basic_position_map = basic_df.set_index('player_key')['Position'].to_dict()
    
    # Mark enriched rows to prioritize them
    enriched_df['_is_enriched'] = True
    basic_df['_is_enriched'] = False
    
    # Combine datasets
    combined = pd.concat([basic_df, enriched_df], ignore_index=True)
    
    # For players with both basic and enriched data, keep enriched version
    # Sort by enriched status (True first) then take first occurrence
    combined = combined.sort_values(['player_key', 'year', '_is_enriched'], 
                                  ascending=[True, True, False])
    combined = combined.drop_duplicates(subset=['player_key', 'year'], keep='first')
    
    # Clean up temporary column
    combined = combined.drop('_is_enriched', axis=1)
    
    # Restore Position field from basic data for enriched players
    combined['Position'] = combined['player_key'].map(basic_position_map).fillna(combined.get('Position', ''))
    
    # Add pre-computed lowercase columns for efficient search
    combined['_player_name_lc'] = combined['player_name'].str.lower().fillna('')
    combined['_team_lc'] = combined['team'].str.lower().fillna('')
    combined['_ncaa_id_lc'] = combined['player_key'].str.lower().fillna('')
    
    return combined

# Load all players (this maintains backward compatibility)
df = load_all_players()

# Create player lookup (latest year per player)
players_df = (
    df.sort_values(["player_key", "year"])
      .groupby("player_key")
      .tail(1)
)

# Create lookup dictionaries for both ID types
PLAYER_LOOKUP_BASIC = players_df[players_df['data_tier'] == 'basic'].set_index("AthleteSourceId").to_dict("index")
PLAYER_LOOKUP_ENRICHED = players_df[players_df['data_tier'] == 'enriched'].set_index("roster.ncaa_id").to_dict("index")

# Combined lookup for backward compatibility
PLAYER_LOOKUP = players_df.set_index("player_key").to_dict("index")
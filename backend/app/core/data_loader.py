import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def load_enriched_players():
    """Load enriched players with advanced metrics (subset of all players)"""
    dfs = []
    
    # Load all available years (2019-2026)
    for year in range(2019, 2027):
        csv_path = os.path.join(BASE_DIR, "data", f"{year}-players_enriched.csv")
        if os.path.exists(csv_path):
            df_year = pd.read_csv(csv_path)
            df_year["year"] = year
            dfs.append(df_year)
            print(f"Loaded {year} enriched players: {len(df_year)} players")
    
    if not dfs:
        print("Warning: No enriched player files found")
        return pd.DataFrame()
    
    df = pd.concat(dfs, ignore_index=True)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").fillna(0).astype(int)
    
    # Mark as enriched data
    df["data_tier"] = "enriched"
    
    return df

def load_roster_info():
    """Load roster info for players"""
    dfs = []
    
    # Load all available years (2019-2026)
    for year in range(2019, 2027):
        csv_path = os.path.join(BASE_DIR, "data", f"{year}-roster-info.csv")
        if os.path.exists(csv_path):
            df_year = pd.read_csv(csv_path)
            df_year["Season"] = df_year["Season"].astype(str)
            # Convert Season to year (e.g., "2025" -> 2025)
            df_year["year"] = pd.to_numeric(df_year["Season"], errors='coerce')
            dfs.append(df_year)
            print(f"Loaded {year} roster info: {len(df_year)} entries")
    
    if not dfs:
        print("Warning: No roster info files found")
        return pd.DataFrame()
    
    df = pd.concat(dfs, ignore_index=True)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").fillna(0).astype(int)

    # Ensure Sourceid is string type for consistent lookup
    if 'Sourceid' in df.columns:
        df['Sourceid'] = df['Sourceid'].astype(str)

    return df

def load_basic_players():
    """Load all players with basic stats (complete coverage)"""
    dfs = []
    
    print("Loading basic players...")
    
    # Load all available years (2019-2026)
    for year in range(2019, 2027):
        # Try new format first (players_basic.csv)
        csv_path = os.path.join(BASE_DIR, "data", f"{year}-players_basic.csv")
        if os.path.exists(csv_path):
            df_year = pd.read_csv(csv_path)
            df_year["year"] = year
            dfs.append(df_year)
            print(f"Loaded {year} basic players: {len(df_year)} players")
        else:
            # Try old format (players.csv)
            csv_path_old = os.path.join(BASE_DIR, "data", f"{year}-players.csv")
            print(f"Checking for old format file: {csv_path_old}, exists: {os.path.exists(csv_path_old)}")
            if os.path.exists(csv_path_old):
                df_year = pd.read_csv(csv_path_old)
                # Old format has year as "2018/9" format (2018-2019 season), extract the ending year
                if 'year' in df_year.columns:
                    df_year["year"] = df_year["year"].apply(lambda x: int(str(x).split('/')[0]) + 1 if '/' in str(x) else int(x))
                    print(f"Parsed years from {year}-players.csv: {df_year['year'].unique()}")
                else:
                    df_year["year"] = year
                dfs.append(df_year)
                print(f"Loaded {year} players (old format): {len(df_year)} players")
            else:
                print(f"No file found for year {year}")
    
    if not dfs:
        print("Warning: No basic player files found")
        return pd.DataFrame()
    
    df = pd.concat(dfs, ignore_index=True)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").fillna(0).astype(int)
    
    print(f"Combined basic players df has years: {sorted(df['year'].unique())}")
    
    # Ensure AthleteSourceId is string type for consistent lookup
    if 'AthleteSourceId' in df.columns:
        df['AthleteSourceId'] = df['AthleteSourceId'].astype(str)
    
    # Map basic player fields to match enriched player field names
    if 'Name' in df.columns:
        df["player_name"] = df["Name"]
    if 'Team' in df.columns:
        df["team"] = df["Team"]
    if 'Conference' in df.columns:
        df["conf"] = df["Conference"]
    
    # Mark as basic data
    df["data_tier"] = "basic"
    
    return df

def load_all_players():
    """Load both basic and enriched players, preferring enriched when available"""
    print("Loading all players...")
    basic_df = load_basic_players()
    enriched_df = load_enriched_players()
    roster_df = load_roster_info()
    
    print(f"Basic df years: {sorted(basic_df['year'].unique()) if not basic_df.empty else 'empty'}")
    print(f"Enriched df years: {sorted(enriched_df['year'].unique()) if not enriched_df.empty else 'empty'}")
    print(f"Roster df years: {sorted(roster_df['year'].unique()) if not roster_df.empty else 'empty'}")
    
    # Join basic players with roster info to get height, weight, hometown
    if not roster_df.empty and not basic_df.empty:
        # Create join key using Sourceid from roster and AthleteSourceId from basic
        basic_df['_join_key'] = basic_df['AthleteSourceId'].astype(str)
        roster_df_basic = roster_df.copy()
        roster_df_basic['_join_key'] = roster_df_basic['Sourceid'].astype(str)
        
        # Select roster fields to add
        roster_fields = ['_join_key', 'Height', 'Weight', 'HometownCity', 'HometownState', 'HometownCountry']
        roster_to_join = roster_df_basic[roster_fields].copy()
        
        # Merge with roster info
        basic_df = pd.merge(
            basic_df,
            roster_to_join,
            on='_join_key',
            how='left'
        )
        
        basic_df = basic_df.drop('_join_key', axis=1)
    
    # Calculate per-game stats for enriched players if not present
    if not enriched_df.empty:
        if 'PPG' not in enriched_df.columns and 'Points' in enriched_df.columns and 'Games' in enriched_df.columns:
            enriched_df['PPG'] = (enriched_df['Points'] / enriched_df['Games']).round(1)
        if 'RPG' not in enriched_df.columns and 'Rebounds Total' in enriched_df.columns and 'Games' in enriched_df.columns:
            enriched_df['RPG'] = (enriched_df['Rebounds Total'] / enriched_df['Games']).round(1)
        if 'APG' not in enriched_df.columns and 'Assists' in enriched_df.columns and 'Games' in enriched_df.columns:
            enriched_df['APG'] = (enriched_df['Assists'] / enriched_df['Games']).round(1)
        
        # Handle division by zero
        if 'PPG' in enriched_df.columns:
            enriched_df['PPG'] = enriched_df['PPG'].fillna(0)
        if 'RPG' in enriched_df.columns:
            enriched_df['RPG'] = enriched_df['RPG'].fillna(0)
        if 'APG' in enriched_df.columns:
            enriched_df['APG'] = enriched_df['APG'].fillna(0)
    
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
    
    print(f"Combined df years: {sorted(combined['year'].unique()) if not combined.empty else 'empty'}")
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
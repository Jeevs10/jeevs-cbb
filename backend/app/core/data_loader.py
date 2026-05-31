import os
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
PLAYERS_DIR = DATA_DIR / "players"
AGGREGATE_DIR = DATA_DIR / "aggregate"

def load_enriched_players():
    """Load enriched players with advanced metrics (subset of all players)"""
    dfs = []
    
    # Load all available years (2019-2026)
    for year in range(2019, 2027):
        csv_path = PLAYERS_DIR / f"{year}-players_enriched.csv"
        if csv_path.exists():
            df_year = pd.read_csv(csv_path)
            # If 'Season' column exists, use it for year, otherwise add year column
            if 'Season' in df_year.columns:
                df_year["year"] = pd.to_numeric(df_year["Season"], errors="coerce").fillna(year).astype(int)
            else:
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
        csv_path = PLAYERS_DIR / f"{year}-roster-info.csv"
        if csv_path.exists():
            df_year = pd.read_csv(csv_path)
            df_year["Season"] = df_year["Season"].astype(str)
            # Convert Season to year (e.g., "2025" -> 2025)
            df_year["year"] = pd.to_numeric(df_year["Season"], errors='coerce')
            # Filter out players without conferences
            df_year = df_year[df_year['Conference'].notna() & (df_year['Conference'] != '')]
            dfs.append(df_year)
            print(f"Loaded {year} roster info: {len(df_year)} entries (filtered by conference)")
    
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
        csv_path = PLAYERS_DIR / f"{year}-players_basic.csv"
        if csv_path.exists():
            df_year = pd.read_csv(csv_path)
            df_year["year"] = year
            dfs.append(df_year)
            print(f"Loaded {year} basic players: {len(df_year)} players")
        else:
            # Try old format (players.csv)
            csv_path_old = PLAYERS_DIR / f"{year}-players.csv"
            print(f"Checking for old format file: {csv_path_old}, exists: {csv_path_old.exists()}")
            if csv_path_old.exists():
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

def load_torvik_players():
    """Load Torvik players with BPM values"""
    dfs = []
    
    print("Loading Torvik players...")
    
    # Load all available years (2019-2026)
    for year in range(2019, 2027):
        csv_path = PLAYERS_DIR / f"{year}_torvik.csv"
        if csv_path.exists():
            df_year = pd.read_csv(csv_path)
            df_year["year"] = year
            dfs.append(df_year)
            print(f"Loaded {year} Torvik players: {len(df_year)} players")
    
    if not dfs:
        print("Warning: No Torvik player files found")
        return pd.DataFrame()
    
    df = pd.concat(dfs, ignore_index=True)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").fillna(0).astype(int)
    
    # Normalize AthleteSourceId to string for consistent lookup
    if 'AthleteSourceId' in df.columns:
        df['AthleteSourceId'] = df['AthleteSourceId'].astype(str).str.replace('.0', '', regex=False)
    
    print(f"Combined Torvik df has years: {sorted(df['year'].unique()) if not df.empty else 'empty'}")
    return df

def load_all_time_players():
    """Load all-time players from all_players.csv for historical percentile comparisons"""
    csv_path = AGGREGATE_DIR / "all_players.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        # Handle year parsing - all_players.csv has season format like "2025/26"
        # Extract the ending year (e.g., "2025/26" -> 2026)
        if 'year' in df.columns:
            df["year"] = df["year"].apply(lambda x: int(str(x).split('/')[0]) + 1 if '/' in str(x) else int(x))
        # Ensure roster.ncaa_id is string for consistent lookup
        if 'roster.ncaa_id' in df.columns:
            df['roster.ncaa_id'] = df['roster.ncaa_id'].astype(str)
        
        print(f"Loaded all-time players: {len(df)} players")
        print(f"All-time years range: {df['year'].min()} to {df['year'].max()}")
        return df
    else:
        print(f"Warning: all_players.csv not found at {csv_path}")
        return pd.DataFrame()

def load_all_players():
    """Load both basic and enriched players, preferring enriched when available"""
    print("Loading all players...")
    basic_df = load_basic_players()
    enriched_df = load_enriched_players()
    roster_df = load_roster_info()
    torvik_df = load_torvik_players()
    
    print(f"Basic df years: {sorted(basic_df['year'].unique()) if not basic_df.empty else 'empty'}")
    print(f"Enriched df years: {sorted(enriched_df['year'].unique()) if not enriched_df.empty else 'empty'}")
    print(f"Roster df years: {sorted(roster_df['year'].unique()) if not roster_df.empty else 'empty'}")
    print(f"Torvik df years: {sorted(torvik_df['year'].unique()) if not torvik_df.empty else 'empty'}")
    
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
    # Normalize both to remove .0 suffix to avoid duplicates
    basic_df['player_key'] = basic_df['AthleteSourceId'].astype(str).str.replace('.0', '', regex=False)
    enriched_df['player_key'] = enriched_df['roster.ncaa_id'].astype(str).str.replace('.0', '', regex=False)
    
    # Preserve Position from basic data before combining
    # Use composite key (player_key, year) to preserve year-specific values
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
    
    # Merge BPM values and Torvik stats from Torvik data
    if not torvik_df.empty and not combined.empty:
        # Create lookup key from torvik using (AthleteSourceId, year) as key
        torvik_df['_bpm_key'] = torvik_df['AthleteSourceId'].astype(str) + '_' + torvik_df['year'].astype(str)
        # Drop duplicates to ensure unique index
        torvik_df = torvik_df.drop_duplicates(subset=['_bpm_key'], keep='first')
        
        # Select columns to merge (BPM, OBPM, DBPM + Torvik stats)
        torvik_cols_to_merge = ['bpm', 'obpm', 'dbpm', 'GP', 'Min_per', 'ORtg', 'usgG1', 'eFG', 'TS_per',
                                'ORB_per', 'DRB_per', 'AST_per', 'TO_per', 'FT_per', 'twoP_per', 'TP_per',
                                'blk_per', 'stl_per', 'ftr', 'porpag', 'adjoe', 'pfr', 'drtg', 'adrtg',
                                'dporpag', 'stops', 'oreb', 'dreb', 'treb', 'ast', 'stl', 'blk', 'pts']
        
        available_torvik_cols = [col for col in torvik_cols_to_merge if col in torvik_df.columns]
        
        if available_torvik_cols:
            torvik_map = torvik_df.set_index('_bpm_key')[available_torvik_cols].to_dict('index')
            
            print(f"Torvik map has {len(torvik_map)} entries with {len(available_torvik_cols)} columns")
            print(f"Sample Torvik keys: {list(torvik_map.keys())[:5]}")
            
            combined['_bpm_key'] = combined['player_key'].astype(str) + '_' + combined['year'].astype(str)
            
            print(f"Combined has {len(combined)} rows")
            print(f"Sample combined player_keys: {combined['player_key'].head(5).tolist()}")
            print(f"Sample combined _bpm_keys: {combined['_bpm_key'].head(5).tolist()}")
            
            def get_torvik_values(row):
                key = row['_bpm_key']
                if key in torvik_map:
                    values = torvik_map[key]
                    result = {}
                    # Map lowercase torvik columns to uppercase for consistency
                    col_mapping = {'bpm': 'BPM', 'obpm': 'OBPM', 'dbpm': 'DBPM'}
                    for col in available_torvik_cols:
                        target_col = col_mapping.get(col, col)
                        result[target_col] = values[col]
                    return pd.Series(result)
                # Return None for all columns if no match
                result = {}
                col_mapping = {'bpm': 'BPM', 'obpm': 'OBPM', 'dbpm': 'DBPM'}
                for col in available_torvik_cols:
                    target_col = col_mapping.get(col, col)
                    result[target_col] = None
                return pd.Series(result)
            
            torvik_values = combined.apply(get_torvik_values, axis=1)
            for col in torvik_values.columns:
                combined[col] = torvik_values[col]
            
            combined = combined.drop('_bpm_key', axis=1)
            print(f"Merged Torvik data for {combined['BPM'].notna().sum()} players")
    
    # Add pre-computed lowercase columns for efficient search
    combined['_player_name_lc'] = combined['player_name'].str.lower().fillna('')
    combined['_team_lc'] = combined['team'].str.lower().fillna('')
    combined['_ncaa_id_lc'] = combined['player_key'].str.lower().fillna('')
    
    print(f"Combined df years: {sorted(combined['year'].unique()) if not combined.empty else 'empty'}")
    return combined

# Load all players (this maintains backward compatibility)
df = load_all_players()

# Load all-time players for historical percentile comparisons
# Temporarily disabled due to performance issues
# all_time_df = load_all_time_players()
all_time_df = pd.DataFrame()
print("⚠️  All-time players loading disabled (performance)")

# Merge Height and Position from main df into all_time_df
# Temporarily disabled due to performance issues
# if not all_time_df.empty and not df.empty and 'Height' in df.columns and 'Position' in df.columns:
#     # Create join keys
#     all_time_df['_join_key'] = all_time_df['roster.ncaa_id'].str.replace('.0', '', regex=False)
#     df_copy = df.copy()
#     df_copy['_join_key'] = df_copy['player_key']
#     
#     # Get Height and Position from main df (first non-null value per player)
#     # Sort by year to prefer more recent data, but take first non-null
#     df_copy = df_copy.sort_values(['player_key', 'year'], ascending=[True, False])
#     
#     # For each player, get the first row with non-null Height and Position
#     def get_first_non_null(group):
#         height_row = group[group['Height'].notna()]
#         if not height_row.empty:
#             return height_row.iloc[0]
#         return group.iloc[0]
#     
#     height_pos = df_copy.groupby('player_key').apply(get_first_non_null)[['_join_key', 'Height', 'Position']].reset_index(drop=True)
#     
#     # Merge Height and Position
#     all_time_df = pd.merge(all_time_df, height_pos, on='_join_key', how='left')
#     all_time_df = all_time_df.drop('_join_key', axis=1)
#     
#     print(f"Merged Height and Position from main df into all_time_df")
#     print(f"Height non-null after merge: {all_time_df['Height'].notna().sum()}")
#     print(f"Position non-null after merge: {all_time_df['Position'].notna().sum()}")

# Create player lookup (latest year per player)
# Temporarily disabled due to performance issues
# players_df = (
#     df.sort_values(["player_key", "year"])
#       .groupby("player_key")
#       .tail(1)
# )
players_df = df.copy()
print("⚠️  Player lookup optimization disabled (performance)")

# Create lookup dictionaries for both ID types
# Temporarily disabled due to performance issues
# PLAYER_LOOKUP_BASIC = players_df[players_df['data_tier'] == 'basic'].set_index("AthleteSourceId").to_dict("index")
PLAYER_LOOKUP_BASIC = {}
print("⚠️  PLAYER_LOOKUP_BASIC disabled (performance)")

# Temporarily disabled due to performance issues
# PLAYER_LOOKUP_ENRICHED = players_df[players_df['data_tier'] == 'enriched'].set_index("roster.ncaa_id").to_dict("index")
PLAYER_LOOKUP_ENRICHED = {}
print("⚠️  PLAYER_LOOKUP_ENRICHED disabled (performance)")

# Combined lookup for backward compatibility
# Temporarily disabled due to performance issues
# PLAYER_LOOKUP = players_df.set_index("player_key").to_dict("index")
PLAYER_LOOKUP = {}
print("⚠️  PLAYER_LOOKUP disabled (performance)")
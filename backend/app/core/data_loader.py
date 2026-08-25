import os
import pandas as pd
import gzip
import glob
import pickle
import json
import time
from pathlib import Path

from app.core.roster_data import get_roster_data

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
PLAYERS_DIR = DATA_DIR / "players"
AGGREGATE_DIR = DATA_DIR / "aggregate"

CACHE_DIR = BASE_DIR / "app" / "cache"
CACHE_FILE = CACHE_DIR / "data_loader_cache.pkl"
CACHE_METADATA_FILE = CACHE_DIR / "data_loader_cache_metadata.json"


def _tracked_source_files():
    """Every CSV that load_all_players()/load_all_time_players() actually read."""
    patterns = [
        str(PLAYERS_DIR / "*-players_basic.csv*"),
        str(PLAYERS_DIR / "*-players_enriched.csv*"),
        str(PLAYERS_DIR / "*-players.csv*"),
        str(PLAYERS_DIR / "*_torvik.csv"),
        str(PLAYERS_DIR / "*-roster-info.csv"),
        str(AGGREGATE_DIR / "all_players.csv*"),
    ]
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
    return sorted(files)


def _source_mod_times():
    return {f: os.path.getmtime(f) for f in _tracked_source_files()}


def _cache_valid():
    if not CACHE_FILE.exists() or not CACHE_METADATA_FILE.exists():
        return False
    try:
        with open(CACHE_METADATA_FILE, 'r') as f:
            metadata = json.load(f)
        return metadata.get("source_mod_times") == _source_mod_times()
    except Exception:
        return False


def _load_cache():
    with open(CACHE_FILE, 'rb') as f:
        cached = pickle.load(f)
    return cached["df"], cached["all_time_df"], cached["players_df"], cached["PLAYER_LOOKUP"]


def _save_cache(df, all_time_df, players_df, PLAYER_LOOKUP):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump({
            "df": df,
            "all_time_df": all_time_df,
            "players_df": players_df,
            "PLAYER_LOOKUP": PLAYER_LOOKUP,
        }, f)
    with open(CACHE_METADATA_FILE, 'w') as f:
        json.dump({
            "built_at": time.time(),
            "source_mod_times": _source_mod_times(),
            "num_rows": len(df),
        }, f, indent=2)

def read_csv_with_compression(csv_path: Path) -> pd.DataFrame:
    """Read CSV file, automatically handling gzip compression."""
    gz_path = csv_path.with_suffix('.csv.gz')

    if gz_path.exists():
        return pd.read_csv(gz_path, compression='gzip')
    elif csv_path.exists():
        return pd.read_csv(csv_path)
    else:
        return pd.DataFrame()

def load_enriched_players():
    """Load enriched players with advanced metrics (subset of all players)"""
    dfs = []

    for year in range(2019, 2027):
        csv_path = PLAYERS_DIR / f"{year}-players_enriched.csv"
        df_year = read_csv_with_compression(csv_path)
        if not df_year.empty:
            if 'Season' in df_year.columns:
                df_year["year"] = pd.to_numeric(df_year["Season"], errors="coerce").fillna(year).astype(int)
            else:
                df_year["year"] = year
            dfs.append(df_year)
    
    if not dfs:
        return pd.DataFrame()
    
    df = pd.concat(dfs, ignore_index=True)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").fillna(0).astype(int)

    df = pd.concat([df, pd.DataFrame({"data_tier": "enriched"}, index=df.index)], axis=1)
    
    return df

def load_roster_info():
    """Load roster info for players"""
    df = get_roster_data()
    if df.empty:
        return pd.DataFrame()

    df = df[df['Conference'].notna() & (df['Conference'] != '')].copy()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").fillna(0).astype(int)

    if 'Sourceid' in df.columns:
        df['Sourceid'] = df['Sourceid'].astype(str)

    return df

def load_basic_players():
    """Load all players with basic stats (complete coverage)"""
    dfs = []

    for year in range(2019, 2027):
        csv_path = PLAYERS_DIR / f"{year}-players_basic.csv"
        df_year = read_csv_with_compression(csv_path)
        if not df_year.empty:
            df_year["year"] = year
            dfs.append(df_year)
        else:
            csv_path_old = PLAYERS_DIR / f"{year}-players.csv"
            df_year = read_csv_with_compression(csv_path_old)
            if not df_year.empty:
                if 'year' in df_year.columns:
                    df_year["year"] = df_year["year"].apply(lambda x: int(str(x).split('/')[0]) + 1 if '/' in str(x) else int(x))
                else:
                    df_year["year"] = year
                dfs.append(df_year)
            else:
                pass
    
    if not dfs:
        return pd.DataFrame()
    
    df = pd.concat(dfs, ignore_index=True)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").fillna(0).astype(int)
    
    
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
    
    
    # Load all available years (2019-2026)
    for year in range(2019, 2027):
        csv_path = PLAYERS_DIR / f"{year}_torvik.csv"
        df_year = read_csv_with_compression(csv_path)
        if not df_year.empty:
            df_year["year"] = year
            dfs.append(df_year)
    
    if not dfs:
        return pd.DataFrame()
    
    df = pd.concat(dfs, ignore_index=True)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").fillna(0).astype(int)
    
    # Normalize AthleteSourceId to string for consistent lookup
    if 'AthleteSourceId' in df.columns:
        df['AthleteSourceId'] = df['AthleteSourceId'].astype(str).str.replace('.0', '', regex=False)
    
    return df

def load_all_time_players():
    """Load all-time players from all_players.csv for historical percentile comparisons"""
    csv_path = AGGREGATE_DIR / "all_players.csv"
    df = read_csv_with_compression(csv_path)
    if not df.empty:
        # Handle year parsing - all_players.csv has season format like "2025/26"
        if 'year' in df.columns:
            df["year"] = df["year"].apply(lambda x: int(str(x).split('/')[0]) + 1 if '/' in str(x) else int(x))
        # Ensure roster.ncaa_id is string for consistent lookup
        if 'roster.ncaa_id' in df.columns:
            df['roster.ncaa_id'] = df['roster.ncaa_id'].astype(str)
        
        return df
    else:
        return pd.DataFrame()

def load_all_players():
    """Load both basic and enriched players, preferring enriched when available"""
    basic_df = load_basic_players()
    enriched_df = load_enriched_players()
    roster_df = load_roster_info()
    torvik_df = load_torvik_players()
    
    
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
        new_cols = {}
        if 'PPG' not in enriched_df.columns and 'Points' in enriched_df.columns and 'Games' in enriched_df.columns:
            new_cols['PPG'] = (enriched_df['Points'] / enriched_df['Games']).round(1)
        if 'RPG' not in enriched_df.columns and 'Rebounds Total' in enriched_df.columns and 'Games' in enriched_df.columns:
            new_cols['RPG'] = (enriched_df['Rebounds Total'] / enriched_df['Games']).round(1)
        if 'APG' not in enriched_df.columns and 'Assists' in enriched_df.columns and 'Games' in enriched_df.columns:
            new_cols['APG'] = (enriched_df['Assists'] / enriched_df['Games']).round(1)
        
        # Handle division by zero
        if 'PPG' in new_cols:
            new_cols['PPG'] = new_cols['PPG'].fillna(0)
        if 'RPG' in new_cols:
            new_cols['RPG'] = new_cols['RPG'].fillna(0)
        if 'APG' in new_cols:
            new_cols['APG'] = new_cols['APG'].fillna(0)
        
        # Add all columns at once to avoid fragmentation
        if new_cols:
            enriched_df = pd.concat([enriched_df, pd.DataFrame(new_cols, index=enriched_df.index)], axis=1)
    
    # Combine datasets, enriched data takes precedence
    basic_df = pd.concat([basic_df, pd.DataFrame({'player_key': basic_df['AthleteSourceId'].astype(str).str.replace('.0', '', regex=False)}, index=basic_df.index)], axis=1)
    enriched_df = pd.concat([enriched_df, pd.DataFrame({'player_key': enriched_df['roster.ncaa_id'].astype(str).str.replace('.0', '', regex=False)}, index=enriched_df.index)], axis=1)
    
    # Preserve Position from basic data before combining
    basic_position_map = basic_df.set_index('player_key')['Position'].to_dict()
    
    # Mark enriched rows to prioritize them
    enriched_df = pd.concat([enriched_df, pd.DataFrame({'_is_enriched': True}, index=enriched_df.index)], axis=1)
    basic_df = pd.concat([basic_df, pd.DataFrame({'_is_enriched': False}, index=basic_df.index)], axis=1)
    
    # Combine datasets
    combined = pd.concat([basic_df, enriched_df], ignore_index=True)
    
    # For players with both basic and enriched data, keep enriched version
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
            # Map lowercase torvik columns to uppercase for consistency
            col_mapping = {'bpm': 'BPM', 'obpm': 'OBPM', 'dbpm': 'DBPM'}
            torvik_to_merge = torvik_df[['_bpm_key'] + available_torvik_cols].rename(columns=col_mapping)

            # Add _bpm_key column using concat to avoid fragmentation
            bpm_key_col = pd.DataFrame({
                '_bpm_key': combined['player_key'].astype(str) + '_' + combined['year'].astype(str)
            }, index=combined.index)
            combined = pd.concat([combined, bpm_key_col], axis=1)

            # Vectorized left merge instead of a per-row Python apply (was O(n) function
            # calls + pd.Series construction over the whole player table)
            combined = combined.merge(torvik_to_merge, on='_bpm_key', how='left')
            combined = combined.drop('_bpm_key', axis=1)
    
    # Add pre-computed lowercase columns for efficient search
    lowercase_cols = pd.DataFrame({
        '_player_name_lc': combined['player_name'].str.lower().fillna(''),
        '_team_lc': combined['team'].str.lower().fillna(''),
        '_ncaa_id_lc': combined['player_key'].str.lower().fillna('')
    })
    combined = pd.concat([combined, lowercase_cols], axis=1)
    
    return combined

def _build_all():
    """Run the full load/merge pipeline from source CSVs. Expensive - only call
    when the on-disk cache is missing or stale (see _cache_valid)."""

    # Load all players (maintains backward compatibility)
    df = load_all_players()

    # Load all-time players for historical percentile comparisons
    all_time_df = load_all_time_players()

    # Merge Height and Position from main df into all_time_df
    if not all_time_df.empty and not df.empty and 'Height' in df.columns and 'Position' in df.columns:
        # Create join keys using concat to avoid fragmentation
        all_time_df = pd.concat([all_time_df, pd.DataFrame({'_join_key': all_time_df['roster.ncaa_id'].str.replace('.0', '', regex=False)}, index=all_time_df.index)], axis=1)
        df_copy = df.copy()
        df_copy = pd.concat([df_copy, pd.DataFrame({'_join_key': df_copy['player_key']}, index=df_copy.index)], axis=1)

        # Get Height and Position from main df (first non-null value per player).
        # Sort so rows with a non-null Height sort first within each player, tie-broken
        # by year desc, then take each group's literal first row - vectorized equivalent
        # of the old groupby().apply(get_first_non_null) row-by-row scan.
        has_height_col = pd.DataFrame({'_has_height': df_copy['Height'].notna()}, index=df_copy.index)
        df_copy = pd.concat([df_copy, has_height_col], axis=1)
        df_copy = df_copy.sort_values(
            ['player_key', '_has_height', 'year'], ascending=[True, False, False]
        )

        height_pos = (
            df_copy.groupby('player_key', sort=False)
            .head(1)[['_join_key', 'Height', 'Position']]
            .reset_index(drop=True)
        )

        # Merge Height and Position
        all_time_df = pd.merge(all_time_df, height_pos, on='_join_key', how='left')
        all_time_df = all_time_df.drop('_join_key', axis=1)

    # Create player lookup (latest year per player)
    players_df = (
        df.sort_values(["player_key", "year"])
          .groupby("player_key")
          .tail(1)
    )

    # Combined lookup, keyed by player_key (only lookup actually used elsewhere;
    # per-tier PLAYER_LOOKUP_BASIC/PLAYER_LOOKUP_ENRICHED were built here but never
    # read anywhere, so they were pure duplicate memory - removed)
    PLAYER_LOOKUP = players_df.set_index("player_key").to_dict("index")

    return df, all_time_df, players_df, PLAYER_LOOKUP


# Load from the on-disk cache when the source CSVs haven't changed since it was
# built, instead of re-running the full load/merge pipeline on every startup.
if _cache_valid():
    try:
        df, all_time_df, players_df, PLAYER_LOOKUP = _load_cache()
    except Exception:
        df, all_time_df, players_df, PLAYER_LOOKUP = _build_all()
        _save_cache(df, all_time_df, players_df, PLAYER_LOOKUP)
else:
    df, all_time_df, players_df, PLAYER_LOOKUP = _build_all()
    _save_cache(df, all_time_df, players_df, PLAYER_LOOKUP)
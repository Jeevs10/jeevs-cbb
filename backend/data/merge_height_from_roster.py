"""
Script to merge Height data from roster info into player data files.
This ensures all players have height data by pulling from roster info when missing.
"""

import pandas as pd
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

def load_roster_info():
    """Load all roster info files and combine them."""
    roster_files = []
    for year in range(2019, 2027):
        roster_file = BASE_DIR / f"{year}-roster-info.csv"
        if roster_file.exists():
            df = pd.read_csv(roster_file)
            df['year'] = year
            roster_files.append(df)
    
    if not roster_files:
        print("No roster info files found")
        return pd.DataFrame()
    
    combined = pd.concat(roster_files, ignore_index=True)
    print(f"Loaded {len(combined)} roster entries from {len(roster_files)} files")
    return combined

def load_player_data(year):
    """Load basic and enriched player data for a specific year."""
    basic_file = BASE_DIR / f"{year}-players.csv"
    enriched_file = BASE_DIR / f"{year}-players_enriched.csv"
    
    basic_df = pd.read_csv(basic_file) if basic_file.exists() else pd.DataFrame()
    enriched_df = pd.read_csv(enriched_file) if enriched_file.exists() else pd.DataFrame()
    
    return basic_df, enriched_df

def merge_height_to_player_data(player_df, roster_df):
    """Merge Height from roster info into player data."""
    if player_df.empty or roster_df.empty:
        return player_df
    
    # Create join keys - use Sourceid from roster and AthleteSourceId from basic
    # For enriched, use roster.ncaa_id
    
    if 'AthleteSourceId' in player_df.columns:
        # Basic data
        player_df['_join_key'] = player_df['AthleteSourceId'].astype(str)
        roster_df['_join_key'] = roster_df['Sourceid'].astype(str)
    elif 'roster.ncaa_id' in player_df.columns:
        # Enriched data
        player_df['_join_key'] = player_df['roster.ncaa_id'].astype(str).str.replace('.0', '', regex=False)
        roster_df['_join_key'] = roster_df['Sourceid'].astype(str)
    else:
        print("No matching ID column found in player data")
        return player_df
    
    # Get height from roster (prefer matching year, otherwise any year)
    roster_with_height = roster_df[roster_df['Height'].notna()][['_join_key', 'Height', 'year']].copy()
    
    # For each player, try to get height from matching year first
    def get_height_for_player(row):
        player_key = row['_join_key']
        player_year = row.get('year')
        
        # Try to match by year
        if player_year:
            year_match = roster_with_height[(roster_with_height['_join_key'] == player_key) & 
                                            (roster_with_height['year'] == player_year)]
            if not year_match.empty:
                return year_match.iloc[0]['Height']
        
        # Otherwise get any available height for this player
        any_match = roster_with_height[roster_with_height['_join_key'] == player_key]
        if not any_match.empty:
            return any_match.iloc[0]['Height']
        
        return None
    
    # Only update where Height is missing
    if 'Height' in player_df.columns:
        player_df['Height'] = player_df.apply(
            lambda row: row['Height'] if pd.notna(row['Height']) else get_height_for_player(row),
            axis=1
        )
    else:
        player_df['Height'] = player_df.apply(get_height_for_player, axis=1)
    
    # Clean up join key
    player_df = player_df.drop('_join_key', axis=1)
    
    return player_df

def process_year(year):
    """Process player data for a specific year."""
    print(f"\nProcessing year {year}...")
    
    # Load roster info
    roster_df = load_roster_info()
    if roster_df.empty:
        print("No roster data available, skipping")
        return
    
    # Load player data
    basic_df, enriched_df = load_player_data(year)
    
    # Process basic data
    if not basic_df.empty:
        print(f"Basic data before: {basic_df['Height'].notna().sum() if 'Height' in basic_df.columns else 0} players with height")
        basic_df = merge_height_to_player_data(basic_df, roster_df)
        print(f"Basic data after: {basic_df['Height'].notna().sum()} players with height")
        
        # Save updated basic data
        basic_file = BASE_DIR / f"{year}-players.csv"
        basic_df.to_csv(basic_file, index=False)
        print(f"Saved updated basic data to {basic_file}")
    
    # Process enriched data
    if not enriched_df.empty:
        print(f"Enriched data before: {enriched_df['Height'].notna().sum() if 'Height' in enriched_df.columns else 0} players with height")
        enriched_df = merge_height_to_player_data(enriched_df, roster_df)
        print(f"Enriched data after: {enriched_df['Height'].notna().sum()} players with height")
        
        # Save updated enriched data
        enriched_file = BASE_DIR / f"{year}-players_enriched.csv"
        enriched_df.to_csv(enriched_file, index=False)
        print(f"Saved updated enriched data to {enriched_file}")

def main():
    """Main function to process all years."""
    print("Starting height merge from roster info...")
    
    for year in range(2019, 2027):
        process_year(year)
    
    print("\nHeight merge complete!")

if __name__ == "__main__":
    main()

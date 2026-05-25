import pandas as pd
import numpy as np
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PLAYERS_DIR = BASE_DIR / "players"

def normalize_team_name(team_name):
    """Normalize team names to handle different conventions"""
    if pd.isna(team_name):
        return team_name
    
    team = str(team_name).strip().lower()
    
    # Handle common abbreviations
    replacements = {
        'st.': 'state',
        'st ': 'state ',
        'state': 'state',
        'university': '',
        'a&m': 'a&m',
        'pine bluff': 'pine-bluff',
        'pine-bluff': 'pine-bluff',
    }
    
    for old, new in replacements.items():
        team = team.replace(old, new)
    
    # Remove extra spaces and punctuation
    team = re.sub(r'\s+', ' ', team)
    team = re.sub(r'[^\w\s-]', '', team)
    team = team.strip()
    
    return team

def normalize_player_name(player_name):
    """Normalize player names to handle suffixes and formatting differences"""
    if pd.isna(player_name):
        return player_name
    
    name = str(player_name).strip().lower()
    
    # Remove common suffixes that might appear in one source but not another
    suffixes = [
        r'\s+jr\.?', r'\s+sr\.?', r'\s+ii\b', r'\s+iii\b', r'\s+iv\b',
        r'\s+2nd', r'\s+3rd', r'\s+4th', r'\s+v\b', r'\s+vi\b'
    ]
    
    for suffix in suffixes:
        name = re.sub(suffix, '', name)
    
    # Remove extra spaces and punctuation
    name = re.sub(r'\s+', ' ', name)
    name = name.strip()
    
    return name

# Load the data
print("Loading datasets...")
trank = pd.read_csv('2026_trank.csv', header=None)
roster = pd.read_csv(PLAYERS_DIR / '2026-roster-info.csv')
players_basic = pd.read_csv(PLAYERS_DIR / '2026-players_basic.csv')

# Define column names for trank (67 columns total)
trank_cols = ['player_name', 'team', 'conf', 'GP', 'Min_per', 'ORtg', 'usg', 'eFG', 'TS_per', 
              'ORB_per', 'DRB_per', 'AST_per', 'TO_per', 'FTM', 'FTA', 'FT_per', 'twoPM', 'twoPA', 
              'twoP_per', 'TPM', 'TPA', 'TP_per', 'blk_per', 'stl_per', 'ftr', 'yr', 'ht', 'num', 
              'porpag', 'adjoe', 'pfr', 'year', 'pid', 'type', 'Rec Rank', 'ast/tov', 'rimmade', 
              'rimmade+ri', 'midmade', 'midmade+m', 'rimmade/(ri', 'midmade/(m', 'dunksmade', 
              'dunksmiss+', 'dunksmade/', 'pick', 'drtg', 'adrtg', 'dporpag', 'stops', 'bpm', 
              'obpm', 'dbpm', 'gbpm', 'mp', 'ogbpm', 'dgbpm', 'oreb', 'dreb', 'treb', 'ast', 
              'stl', 'blk', 'pts', 'role', '3p/100?', 'extra_col']

trank.columns = trank_cols

# Normalize names and teams for matching
trank['name_normalized'] = trank['player_name'].apply(normalize_player_name)
trank['team_normalized'] = trank['team'].apply(normalize_team_name)

roster['name_normalized'] = roster['Name'].apply(normalize_player_name)
roster['team_normalized'] = roster['Team'].apply(normalize_team_name)

players_basic['name_normalized'] = players_basic['Name'].apply(normalize_player_name)
players_basic['team_normalized'] = players_basic['Team'].apply(normalize_team_name)

print(f"Trank: {len(trank)} players")
print(f"Roster: {len(roster)} players")
print(f"Players Basic: {len(players_basic)} players")

# Step 1: Link trank to roster-info using both name AND team
print("\n=== Step 1: Linking Trank to Roster-Info (Name + Team) ===")
trank_roster = pd.merge(
    trank,
    roster,
    on=['name_normalized', 'team_normalized'],
    how='left',
    suffixes=('_trank', '_roster')
)

# Check what columns exist after merge
print(f"Columns after merge: {[col for col in trank_roster.columns if 'Name' in col or 'name' in col]}")

# Use the correct column name
name_col = 'Name_roster' if 'Name_roster' in trank_roster.columns else 'Name'
print(f"Matches found: {trank_roster[name_col].notna().sum()} out of {len(trank)}")
print(f"Match rate: {trank_roster[name_col].notna().sum() / len(trank) * 100:.1f}%")

# Check for duplicate matches and handle them
duplicate_matches = trank_roster['name_normalized'].value_counts()
if duplicate_matches.max() > 1:
    print(f"Warning: Some names match multiple roster entries")
    print(f"Top duplicates: {duplicate_matches[duplicate_matches > 1].head()}")
    # Keep only the first match for each player
    trank_roster = trank_roster.drop_duplicates(subset='name_normalized', keep='first')
    print(f"After deduplication: {len(trank_roster)} rows")

# Step 2: Link combined data to players_basic using both name AND team
print("\n=== Step 2: Linking to Players-Basic (Name + Team) ===")
final_merged = pd.merge(
    trank_roster,
    players_basic,
    on=['name_normalized', 'team_normalized'],
    how='left',
    suffixes=('', '_basic')
)

print(f"Final matches: {final_merged['SeasonLabel'].notna().sum()} out of {len(trank_roster)}")
print(f"Final match rate: {final_merged['SeasonLabel'].notna().sum() / len(trank_roster) * 100:.1f}%")

# Handle duplicates from players_basic as well
if final_merged['name_normalized'].duplicated().any():
    final_merged = final_merged.drop_duplicates(subset='name_normalized', keep='first')
    print(f"After deduplication: {len(final_merged)} rows")

# Clean up the merged dataset
# Remove duplicate columns and normalize (but keep name_normalized for unmatched analysis)
cols_to_drop = []  # Don't drop name_normalized yet
final_merged = final_merged.drop(columns=[col for col in cols_to_drop if col in final_merged.columns])

# Rename key columns for clarity
final_merged = final_merged.rename(columns={
    'Name_roster': 'roster_name',
    'Team_roster': 'roster_team',
    'Conference_roster': 'roster_conference',
    'Season_roster': 'roster_season',
    'Team': 'basic_team',
    'Conference': 'basic_conference',
    'Season': 'basic_season',
    'AthleteId': 'basic_athlete_id',
    'AthleteSourceId': 'basic_athlete_source_id'
})

# Select and reorder key columns
key_cols = [
    'player_name', 'team', 'conf', 'year',
    'roster_name', 'roster_team', 'roster_conference', 'roster_season',
    'basic_team', 'basic_conference', 'basic_season',
    'TeamId', 'basic_athlete_id', 'basic_athlete_source_id',
    'GP', 'Min_per', 'ORtg', 'usg', 'eFG', 'TS_per',
    'porpag', 'bpm', 'obpm', 'dbpm', 'gbpm',
    'Games', 'Starts', 'Minutes', 'Points', 'Usage'
]

# Get available columns
available_cols = [col for col in key_cols if col in final_merged.columns]
final_output = final_merged[available_cols + [col for col in final_merged.columns if col not in key_cols]]

# Save the merged dataset
output_file = PLAYERS_DIR / '2026-players_trank_merged.csv'
final_output.to_csv(output_file, index=False)
print(f"\n=== Results ===")
print(f"Merged dataset saved to: {output_file}")
print(f"Total rows: {len(final_output)}")
print(f"Total columns: {len(final_output.columns)}")

# Print sample data with available columns
sample_cols = ['player_name', 'team', 'roster_name', 'roster_team']
available_sample_cols = [col for col in sample_cols if col in final_output.columns]
if available_sample_cols:
    print(f"\nSample of merged data:")
    print(final_output[available_sample_cols].head(10))

# Identify and save unmatched players
print(f"\n=== Unmatched Players ===")

# Players that didn't match in step 1 (trank to roster) - check if Name column is NaN
unmatched_step1 = trank_roster[trank_roster['Name'].isna()]
print(f"Unmatched after Step 1 (Trank → Roster): {len(unmatched_step1)}")
if len(unmatched_step1) > 0:
    print(f"Sample unmatched players:")
    print(unmatched_step1[['player_name', 'team']].head(20))
    unmatched_step1[['player_name', 'team']].to_csv(PLAYERS_DIR / 'unmatched_trank_to_roster.csv', index=False)
    print(f"Saved to: unmatched_trank_to_roster.csv")

# Players that matched step 1 but not step 2 (combined to players_basic) - check if SeasonLabel is NaN
unmatched_step2 = final_merged[final_merged['SeasonLabel'].isna()]
print(f"\nUnmatched after Step 2 (Combined → Players-Basic): {len(unmatched_step2)}")
if len(unmatched_step2) > 0:
    print(f"Sample unmatched players:")
    print(unmatched_step2[['player_name', 'team']].head(20))
    unmatched_step2[['player_name', 'team']].to_csv(PLAYERS_DIR / 'unmatched_combined_to_basic.csv', index=False)
    print(f"Saved to: unmatched_combined_to_basic.csv")

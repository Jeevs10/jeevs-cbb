"""Add AthleteSourceId to Torvik files and add proper headers.

This script:
1. Loads Torvik data for each year (2019-2026)
2. Loads corresponding player basic data
3. Matches players using name and team normalization
4. Adds AthleteSourceId to Torvik data
5. Adds proper headers
6. Saves updated Torvik files
"""

import pandas as pd
import numpy as np
import os
import unicodedata
from difflib import SequenceMatcher

# Team name mapping from game data format to roster format
TEAM_NAME_MAP = {
    "McNeese St.": "McNeese",
    "Gardner Webb": "Gardner-Webb",
    "Appalachian St.": "App State",
    "Chicago St.": "Chicago State",
    "Northwestern St.": "Northwestern State",
    "Texas St.": "Texas State",
    "South Carolina St.": "South Carolina State",
    "Connecticut": "UConn",
    "San Jose St.": "San José State",
    "Arizona St.": "Arizona State",
    "Tennessee Martin": "UT Martin",
    "Grambling St.": "Grambling",
    "Cal St. Northridge": "Cal State Northridge",
    "Boise St.": "Boise State",
    "Saint Francis": "St. Francis (PA)",
    "South Dakota St.": "South Dakota State",
    "Illinois Chicago": "UIC",
    "Tennessee St.": "Tennessee State",
    "Louisiana Monroe": "UL Monroe",
    "Alabama St.": "Alabama State",
    "Kennesaw St.": "Kennesaw State",
    "Jacksonville St.": "Jacksonville State",
    "San Diego St.": "San Diego State",
    "Penn St.": "Penn State",
    "Cal Baptist": "California Baptist",
    "Florida St.": "Florida State",
    "Oklahoma St.": "Oklahoma State",
    "Murray St.": "Murray State",
    "East Tennessee St.": "East Tennessee State",
    "Sam Houston St.": "Sam Houston",
    "Hawaii": "Hawai'i",
    "Mississippi St.": "Mississippi State",
    "North Dakota St.": "North Dakota State",
    "Georgia St.": "Georgia State",
    "Montana St.": "Montana State",
    "Coppin St.": "Coppin State",
    "IU Indy": "IU Indianapolis",
    "Alcorn St.": "Alcorn State",
    "Colorado St.": "Colorado State",
    "Southeast Missouri St.": "Southeast Missouri State",
    "Washington St.": "Washington State",
    "Jackson St.": "Jackson State",
    "Illinois St.": "Illinois State",
    "Miami FL": "Miami",
    "Penn": "Pennsylvania",
    "FIU": "Florida International",
    "Seattle": "Seattle U",
    "Wichita St.": "Wichita State",
    "UMKC": "Kansas City",
    "Portland St.": "Portland State",
    "Tarleton St.": "Tarleton State",
    "Cleveland St.": "Cleveland State",
    "Missouri St.": "Missouri State",
    "Miami OH": "Miami (OH)",
    "St. Thomas": "St. Thomas-Minnesota",
    "Weber St.": "Weber State",
    "Nicholls St.": "Nicholls",
    "Bethune Cookman": "Bethune-Cookman",
    "Albany": "UAlbany",
    "Indiana St.": "Indiana State",
    "Morehead St.": "Morehead State",
    "USC Upstate": "South Carolina Upstate",
    "Michigan St.": "Michigan State",
    "New Mexico St.": "New Mexico State",
    "Iowa St.": "Iowa State",
    "Long Beach St.": "Long Beach State",
    "Ohio St.": "Ohio State",
    "Norfolk St.": "Norfolk State",
    "Sacramento St.": "Sacramento State",
    "Cal St. Fullerton": "Cal State Fullerton",
    "Ball St.": "Ball State",
    "Idaho St.": "Idaho State",
    "Arkansas Pine Bluff": "Arkansas-Pine Bluff",
    "Kansas St.": "Kansas State",
    "Arkansas St.": "Arkansas State",
    "Utah St.": "Utah State",
    "Oregon St.": "Oregon State",
    "Morgan St.": "Morgan State",
    "Kent St.": "Kent State",
    "Queens": "Queens University",
    "Texas A&M Corpus Chris": "Texas A&M-Corpus Christi",
    "Loyola MD": "Loyola Maryland",
    "American": "American University",
    "Southeastern Louisiana": "SE Louisiana",
    "LIU": "Long Island University",
    "N.C. State": "NC State",
    "Cal St. Bakersfield": "Cal State Bakersfield",
    "Youngstown St.": "Youngstown State",
    "Delaware St.": "Delaware State",
    "Mississippi Valley St.": "Mississippi Valley State",
    "Nebraska Omaha": "Omaha",
    "Fresno St.": "Fresno State",
    "Mississippi": "Ole Miss",
    "Wright St.": "Wright State",
    "East Texas A&M": "Texas A&M-Commerce",
    "Texas A&M": "Texas A&M",
    "UNC Greensboro": "UNC Greensboro",
    "Loyola Marymount": "Loyola Marymount",
    "UCF": "UCF",
    "High Point": "High Point",
    "Liberty": "Liberty",
    "Marshall": "Marshall",
    "Southern Miss": "Southern Miss",
    "Rhode Island": "Rhode Island",
    "Evansville": "Evansville",
    "Eastern Michigan": "Eastern Michigan",
    "Nebraska": "Nebraska",
    "Gonzaga": "Gonzaga",
}

def normalize_team_name(team_name):
    """Normalize team name from game data to roster format."""
    return TEAM_NAME_MAP.get(team_name, team_name)

def normalize_player_name(name):
    """Normalize player name by removing suffixes, punctuation, accents, and special characters."""
    if pd.isna(name) or not name:
        return ""
    
    # Convert to string if not already
    name = str(name)
    
    # Remove trailing comma before suffix
    if name.endswith(','):
        name = name[:-1].strip()
    
    # Remove common suffixes (with and without commas)
    suffixes = [' Jr.', ' Jr', ' II', ' III', ' IV', ' Sr.', ' Sr', ' II,', ' III,', ' IV,']
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)].strip()
    
    # Handle lowercase roman numerals (lll -> III, ll -> II)
    if name.endswith(' lll'):
        name = name[:-4].strip()
    elif name.endswith(' ll'):
        name = name[:-3].strip()
    
    # Remove periods from initials (e.g., "D.J." -> "DJ")
    name = name.replace('.', '')
    
    # Remove apostrophes
    name = name.replace("'", "")
    
    # Remove accents and special characters (normalize to ASCII)
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    
    return name

def fuzzy_match(name1, name2):
    """Fuzzy match two names using SequenceMatcher."""
    return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()

# Proper headers provided by user (67 columns total)
TORVIK_HEADERS = [
    'player_name', 'team', 'conf', 'GP', 'Min_per', 'ORtg', 'usgG1', 'eFG', 'TS_per',
    'ORB_per', 'DRB_per', 'AST_per', 'TO_per', 'FTM', 'FTA', 'FT_per', 'twoPM',
    'twoPA', 'twoP_per', 'TPM', 'TPA', 'TP_per', 'blk_per', 'stl_per', 'ftr',
    'yr', 'ht', 'num', 'porpag', 'adjoe', 'pfr', 'year', 'pid', 'type', 'Rec Rank',
    'ast/tov', 'rimmade', 'rimmade+ri', 'midmade', 'midmade+m',
    'rimmade/(ri', 'midmade/(m', 'dunksmade',
    'dunksmiss+', 'dunksmade/', 'pick', 'drtg',
    'adrtg', 'dporpag', 'stops', 'bpm', 'obpm', 'dbpm', 'gbpm', 'mp',
    'ogbpm', 'dgbpm', 'oreb', 'dreb', 'treb', 'ast', 'stl', 'blk', 'pts', 'role', '3p/100?',
    'col_66'
]

def load_game_data_ncaa_ids(year):
    """Load ncaa_id mappings from game data as fallback."""
    game_data_file = os.path.join(os.path.dirname(__file__), "data", "games", f"{year}_player_game_data.json")
    
    if not os.path.exists(game_data_file):
        print(f"  Warning: Game data file not found for {year}")
        return {}
    
    import json
    with open(game_data_file, 'r', encoding='utf-8') as f:
        game_data = json.load(f)
    
    # Create mapping from (normalized_name, normalized_team) to ncaa_id
    game_lookup = {}
    for record in game_data:
        player_name = record.get('pp')
        team = record.get('tt')
        ncaa_id = record.get('ncaa_id')
        
        if player_name and team and ncaa_id:
            normalized_name = normalize_player_name(player_name)
            normalized_team = normalize_team_name(team)
            key = (normalized_name, normalized_team)
            game_lookup[key] = ncaa_id
    
    print(f"  Loaded {len(game_lookup)} ncaa_id mappings from game data")
    return game_lookup

def process_torvik_file(year):
    """Process a single Torvik file for a given year."""
    print(f"\nProcessing {year} Torvik data...")
    
    # Load Torvik data (headers are now present)
    torvik_file = os.path.join(os.path.dirname(__file__), "data", "players", f"{year}_torvik.csv")
    
    if not os.path.exists(torvik_file):
        print(f"  Warning: Torvik file not found for {year}, skipping")
        return
    
    torvik_df = pd.read_csv(torvik_file)
    
    # Load PlayerData.csv
    player_file = os.path.join(os.path.dirname(__file__), "data", "players", f"{year}-PlayerData.csv")
    
    if not os.path.exists(player_file):
        print(f"  Warning: PlayerData file not found for {year}, skipping")
        return
    
    player_df = pd.read_csv(player_file)
    
    # Load game data as fallback
    game_lookup = load_game_data_ncaa_ids(year)
    
    print(f"  Loaded {len(torvik_df)} Torvik records")
    print(f"  Loaded {len(player_df)} PlayerData records")
    
    # Create normalized keys for matching
    torvik_df['normalized_name'] = torvik_df['player_name'].apply(normalize_player_name)
    torvik_df['normalized_team'] = torvik_df['team'].apply(normalize_team_name)
    
    player_df['normalized_name'] = player_df['Name'].apply(normalize_player_name)
    player_df['normalized_team'] = player_df['Team'].apply(normalize_team_name)
    
    # Initialize AthleteSourceId column
    torvik_df['AthleteSourceId'] = np.nan
    
    # Create lookup dictionary from PlayerData
    player_lookup = {}
    for _, row in player_df.iterrows():
        key = (row['normalized_name'], row['normalized_team'])
        player_lookup[key] = row['AthleteSourceId']
    
    matches = 0
    fuzzy_matches = 0
    game_data_matches = 0
    no_matches = 0
    
    # Match players
    for idx, torvik_row in torvik_df.iterrows():
        key = (torvik_row['normalized_name'], torvik_row['normalized_team'])
        
        if key in player_lookup:
            torvik_df.at[idx, 'AthleteSourceId'] = player_lookup[key]
            matches += 1
        else:
            # Try fuzzy matching against PlayerData
            torvik_name = torvik_row['normalized_name']
            torvik_team = torvik_row['normalized_team']
            
            team_players = player_df[player_df['normalized_team'] == torvik_team]
            
            if len(team_players) > 0:
                best_match = None
                best_score = 0.8  # Threshold for fuzzy match
                
                for _, player_row in team_players.iterrows():
                    score = fuzzy_match(torvik_name, player_row['normalized_name'])
                    if score > best_score:
                        best_score = score
                        best_match = player_row
                
                if best_match is not None:
                    torvik_df.at[idx, 'AthleteSourceId'] = best_match['AthleteSourceId']
                    fuzzy_matches += 1
                else:
                    # Try game data as fallback
                    if key in game_lookup:
                        torvik_df.at[idx, 'AthleteSourceId'] = game_lookup[key]
                        game_data_matches += 1
                    else:
                        no_matches += 1
            else:
                # Try game data as fallback
                if key in game_lookup:
                    torvik_df.at[idx, 'AthleteSourceId'] = game_lookup[key]
                    game_data_matches += 1
                else:
                    no_matches += 1
    
    print(f"  Exact matches from PlayerData: {matches}")
    print(f"  Fuzzy matches from PlayerData: {fuzzy_matches}")
    print(f"  Matches from game data fallback: {game_data_matches}")
    print(f"  No matches: {no_matches}")
    print(f"  Total matches: {matches + fuzzy_matches + game_data_matches}")
    print(f"  Match rate: {(matches + fuzzy_matches + game_data_matches)/len(torvik_df)*100:.1f}%")
    
    # Drop temporary columns
    torvik_df = torvik_df.drop(columns=['normalized_name', 'normalized_team'])
    
    # Reorder columns to put AthleteSourceId first
    cols = ['AthleteSourceId'] + [col for col in torvik_df.columns if col != 'AthleteSourceId']
    torvik_df = torvik_df[cols]
    
    # Save updated Torvik file
    torvik_df.to_csv(torvik_file, index=False)
    print(f"  Saved updated Torvik file with AthleteSourceId")

def main():
    """Process all Torvik files from 2019-2026."""
    print("="*60)
    print("Adding AthleteSourceId to Torvik Files")
    print("="*60)
    
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    
    for year in years:
        process_torvik_file(year)
    
    print(f"\n{'='*60}")
    print("Processing Complete")
    print("="*60)

if __name__ == "__main__":
    main()

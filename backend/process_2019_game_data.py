import json
import pandas as pd
import os
import unicodedata
from difflib import get_close_matches

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def remove_accents(text):
    """Remove accents from text"""
    if pd.isna(text):
        return ""
    # Normalize to NFD and remove combining characters
    return ''.join(c for c in unicodedata.normalize('NFD', str(text))
                   if unicodedata.category(c) != 'Mn')

def normalize_name(name):
    """Normalize player name for comparison"""
    if pd.isna(name):
        return ""
    name = str(name).strip()
    # Remove accents
    name = remove_accents(name)
    # Remove special characters (hyphens, apostrophes, etc.)
    name = name.replace('-', ' ')
    name = name.replace("'", '')
    name = name.lower()
    for suffix in [" jr.", " sr.", " ii", " iii", " iv", " jr", " sr"]:
        name = name.replace(suffix, "")
    return name.strip()

def extract_first_last_name(name):
    """Extract first and last name from full name"""
    if pd.isna(name):
        return "", ""
    name = str(name).strip()
    # Remove accents and special characters
    name = remove_accents(name)
    name = name.replace('-', ' ')
    name = name.replace("'", '')
    name = name.lower()
    # Remove suffixes
    for suffix in [" jr.", " sr.", " ii", " iii", " iv", " jr", " sr"]:
        name = name.replace(suffix, "")
    name = name.strip()
    
    parts = name.split()
    if len(parts) == 0:
        return "", ""
    elif len(parts) == 1:
        return parts[0], ""
    else:
        # First name is first part, last name is last part
        return parts[0], parts[-1]

def normalize_team_name(team):
    """Normalize team name for comparison - handle St. vs State variations"""
    if pd.isna(team):
        return ""
    team = str(team).strip()
    # Remove accents
    team = remove_accents(team)
    
    # Specific team name mappings
    team_mappings = {
        'mississippi': 'ole miss',
        'miami fl': 'miami',
        'grambling st.': 'grambling',
        'grambling st': 'grambling',
        'appalachian st.': 'app state',
        'appalachian st': 'app state',
    }
    
    # Expand state abbreviations
    team = team.replace(' St.', ' State')
    team = team.replace(' St', ' State')
    team = team.replace('N.C.', 'NC')
    team = team.replace('S.C.', 'SC')
    team = team.replace('N.C', 'NC')
    team = team.replace('S.C', 'SC')
    
    # Convert to lowercase for comparison
    team_lower = team.lower()
    
    # Apply specific mappings
    if team_lower in team_mappings:
        return team_mappings[team_lower]
    
    return team_lower

def link_player_ids(game_data_file, roster_file, player_data_file, output_file):
    """Link player IDs from roster to game data using team, name, and year matching"""
    
    # Load game data
    print(f"Loading game data from {game_data_file}...")
    with open(game_data_file, 'r') as f:
        game_data = json.load(f)
    
    print(f"Loaded {len(game_data)} game records")
    
    # Load roster info
    print(f"Loading roster info from {roster_file}...")
    roster_df = pd.read_csv(roster_file)
    roster_df['Sourceid'] = roster_df['Sourceid'].astype(str)
    roster_df['year'] = pd.to_numeric(roster_df['Season'], errors='coerce')
    
    # Create lookup: (team, normalized_name, year) -> ncaa_id
    roster_lookup = {}
    for _, row in roster_df.iterrows():
        team = row.get('Team')
        name = row.get('Name')
        year = row.get('year')
        ncaa_id = row.get('Sourceid')
        
        if pd.notna(team) and pd.notna(name) and pd.notna(year) and pd.notna(ncaa_id):
            norm_team = normalize_team_name(team)
            norm_name = normalize_name(name)
            key = (norm_team, norm_name, int(year))
            roster_lookup[key] = ncaa_id
    
    print(f"Created roster lookup with {len(roster_lookup)} entries")
    
    # Load player data for additional name matching
    print(f"Loading player data from {player_data_file}...")
    player_df = pd.read_csv(player_data_file)
    player_df['roster.ncaa_id'] = player_df.iloc[:, 6].astype(str)
    
    # Create player name lookup: (team, normalized_name) -> ncaa_id
    player_lookup = {}
    for _, row in player_df.iterrows():
        team = row.get('Team')
        name = row.get('Name')
        ncaa_id = row.get('roster.ncaa_id')
        
        if pd.notna(team) and pd.notna(name) and pd.notna(ncaa_id):
            norm_team = normalize_team_name(team)
            norm_name = normalize_name(name)
            key = (norm_team, norm_name)
            player_lookup[key] = ncaa_id
    
    print(f"Created player lookup with {len(player_lookup)} entries")
    
    # Build list of all normalized team names for fuzzy matching
    all_teams = set()
    for (norm_team, norm_name) in player_lookup.keys():
        all_teams.add(norm_team)
    for (norm_team, norm_name, year) in roster_lookup.keys():
        all_teams.add(norm_team)
    all_teams = list(all_teams)
    
    # Link player IDs in game data
    matched = 0
    unmatched = []
    unmatched_players = set()
    
    # Build name-only lookup (name -> list of ncaa_ids)
    name_only_lookup = {}
    for (norm_team, norm_name), ncaa_id in player_lookup.items():
        if norm_name not in name_only_lookup:
            name_only_lookup[norm_name] = []
        if ncaa_id not in name_only_lookup[norm_name]:
            name_only_lookup[norm_name].append(ncaa_id)
    
    # Build first/last name lookup
    first_last_lookup = {}
    for _, row in player_df.iterrows():
        team = row.get('Team')
        name = row.get('Name')
        ncaa_id = row.get('roster.ncaa_id')
        
        if pd.notna(team) and pd.notna(name) and pd.notna(ncaa_id):
            norm_team = normalize_team_name(team)
            first_name, last_name = extract_first_last_name(name)
            if first_name and last_name:
                key = (norm_team, first_name, last_name)
                first_last_lookup[key] = ncaa_id
    
    # Build first name lookup (team, first_name -> list of ncaa_ids)
    first_name_lookup = {}
    for _, row in player_df.iterrows():
        team = row.get('Team')
        name = row.get('Name')
        ncaa_id = row.get('roster.ncaa_id')
        
        if pd.notna(team) and pd.notna(name) and pd.notna(ncaa_id):
            norm_team = normalize_team_name(team)
            first_name, _ = extract_first_last_name(name)
            if first_name:
                key = (norm_team, first_name)
                if key not in first_name_lookup:
                    first_name_lookup[key] = []
                if ncaa_id not in first_name_lookup[key]:
                    first_name_lookup[key].append(ncaa_id)
    
    # Build last name lookup (team, last_name -> list of ncaa_ids)
    last_name_lookup = {}
    for _, row in player_df.iterrows():
        team = row.get('Team')
        name = row.get('Name')
        ncaa_id = row.get('roster.ncaa_id')
        
        if pd.notna(team) and pd.notna(name) and pd.notna(ncaa_id):
            norm_team = normalize_team_name(team)
            _, last_name = extract_first_last_name(name)
            if last_name:
                key = (norm_team, last_name)
                if key not in last_name_lookup:
                    last_name_lookup[key] = []
                if ncaa_id not in last_name_lookup[key]:
                    last_name_lookup[key].append(ncaa_id)
    
    for game in game_data:
        team = game.get('tt')
        player_name = game.get('pp')
        year = game.get('year')
        
        if not team or not player_name or not year:
            continue
        
        norm_team = normalize_team_name(team)
        norm_name = normalize_name(player_name)
        year_int = int(year)
        
        # Try roster lookup first
        key = (norm_team, norm_name, year_int)
        ncaa_id = roster_lookup.get(key)
        
        # If not found, try player lookup (without year)
        if not ncaa_id:
            key = (norm_team, norm_name)
            ncaa_id = player_lookup.get(key)
        
        # If still not found, try fuzzy team name matching
        if not ncaa_id:
            fuzzy_teams = get_close_matches(norm_team, all_teams, n=1, cutoff=0.85)
            if fuzzy_teams:
                fuzzy_team = fuzzy_teams[0]
                key = (fuzzy_team, norm_name)
                ncaa_id = player_lookup.get(key)
        
        # If still not found, try name-only matching
        if not ncaa_id and norm_name in name_only_lookup:
            matching_ids = name_only_lookup[norm_name]
            if len(matching_ids) == 1:
                ncaa_id = matching_ids[0]
            else:
                # Name matches multiple teams, keep in unmatched
                ncaa_id = None
        
        # If still not found, try first/last name matching
        if not ncaa_id:
            first_name, last_name = extract_first_last_name(player_name)
            if first_name and last_name:
                # Try with exact team
                key = (norm_team, first_name, last_name)
                ncaa_id = first_last_lookup.get(key)
                
                # If not found, try with fuzzy team
                if not ncaa_id:
                    fuzzy_teams = get_close_matches(norm_team, all_teams, n=1, cutoff=0.85)
                    if fuzzy_teams:
                        fuzzy_team = fuzzy_teams[0]
                        key = (fuzzy_team, first_name, last_name)
                        ncaa_id = first_last_lookup.get(key)
        
        # If still not found, try fuzzy first name + fuzzy team
        if not ncaa_id:
            first_name, last_name = extract_first_last_name(player_name)
            if first_name:
                # Get all first names from player data
                all_first_names = set()
                for (team, fname) in first_name_lookup.keys():
                    all_first_names.add(fname)
                all_first_names = list(all_first_names)
                
                # Try fuzzy first name match
                fuzzy_first_names = get_close_matches(first_name, all_first_names, n=1, cutoff=0.85)
                if fuzzy_first_names:
                    fuzzy_first_name = fuzzy_first_names[0]
                    # Try with exact team
                    key = (norm_team, fuzzy_first_name)
                    matching_ids = first_name_lookup.get(key, [])
                    if len(matching_ids) == 1:
                        ncaa_id = matching_ids[0]
                    # If not found or multiple matches, try with fuzzy team
                    if not ncaa_id:
                        fuzzy_teams = get_close_matches(norm_team, all_teams, n=1, cutoff=0.85)
                        if fuzzy_teams:
                            fuzzy_team = fuzzy_teams[0]
                            key = (fuzzy_team, fuzzy_first_name)
                            matching_ids = first_name_lookup.get(key, [])
                            if len(matching_ids) == 1:
                                ncaa_id = matching_ids[0]
        
        # If still not found, try fuzzy last name + fuzzy team
        if not ncaa_id:
            first_name, last_name = extract_first_last_name(player_name)
            if last_name:
                # Get all last names from player data
                all_last_names = set()
                for (team, lname) in last_name_lookup.keys():
                    all_last_names.add(lname)
                all_last_names = list(all_last_names)
                
                # Try fuzzy last name match
                fuzzy_last_names = get_close_matches(last_name, all_last_names, n=1, cutoff=0.85)
                if fuzzy_last_names:
                    fuzzy_last_name = fuzzy_last_names[0]
                    # Try with exact team
                    key = (norm_team, fuzzy_last_name)
                    matching_ids = last_name_lookup.get(key, [])
                    if len(matching_ids) == 1:
                        ncaa_id = matching_ids[0]
                    # If not found or multiple matches, try with fuzzy team
                    if not ncaa_id:
                        fuzzy_teams = get_close_matches(norm_team, all_teams, n=1, cutoff=0.85)
                        if fuzzy_teams:
                            fuzzy_team = fuzzy_teams[0]
                            key = (fuzzy_team, fuzzy_last_name)
                            matching_ids = last_name_lookup.get(key, [])
                            if len(matching_ids) == 1:
                                ncaa_id = matching_ids[0]
        
        if ncaa_id:
            game['ncaa_id'] = ncaa_id
            matched += 1
        else:
            game['ncaa_id'] = None
            if (team, player_name) not in unmatched_players:
                unmatched_players.add((team, player_name))
                unmatched.append({'team': team, 'player_name': player_name})
    
    print(f"Matched {matched} players ({matched/len(game_data)*100:.1f}%)")
    print(f"Unmatched players: {len(unmatched)}")
    
    # Save unmatched players
    unmatched_file = os.path.join(os.path.dirname(output_file), "unmatched_players_2019.csv")
    if unmatched:
        unmatched_df = pd.DataFrame(unmatched)
        unmatched_df.to_csv(unmatched_file, index=False)
        print(f"Saved unmatched players to {unmatched_file}")
    
    # Save updated game data
    print(f"Saving updated game data to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(game_data, f)
    
    print("Done!")

if __name__ == "__main__":
    game_data_file = os.path.join(BASE_DIR, "data", "games", "2019_player_game_data.json")

    # Check if data is already in dict format
    with open(game_data_file, 'r') as f:
        data = json.load(f)

    if isinstance(data[0], dict):
        print("Data is already in dict format, skipping conversion")
    else:
        # Step 1: Convert list format to dict format
        keys_2026 = [
            'numdate', 'datetext', 'opstyle', 'quality', 'win1', 'opponent', 'muid', 'win2',
            'Min_per', 'ORtg', 'Usage', 'eFG', 'TS_per', 'ORB_per', 'DRB_per', 'AST_per', 'TO_per',
            'dunksmade', 'dunksatt', 'rimmade', 'rimatt', 'midmade', 'midatt',
            'twoPM', 'twoPA', 'TPM', 'TPA', 'FTM', 'FTA',
            'bpm_rd', 'Obpm', 'Dbpm', 'bpm_net',
            'pts', 'ORB', 'DRB', 'AST', 'TOV', 'STL', 'BLK',
            'stl_per', 'blk_per', 'PF', 'possessions', 'bpm', 'sbpm',
            'loc', 'tt', 'pp', 'inches', 'cls', 'pid', 'year', 'ncaa_id'
        ]

        print(f'Loaded {len(data)} games from 2019')
        print(f'Each game has {len(data[0])} fields')
        print(f'Expected {len(keys_2026)} keys')

        # Convert to dict format
        converted_data = []
        for game_list in data:
            game_dict = {}
            for i, key in enumerate(keys_2026):
                if i < len(game_list):
                    game_dict[key] = game_list[i]
                else:
                    game_dict[key] = None
            converted_data.append(game_dict)

        print(f'Converted {len(converted_data)} games to dict format')

        # Save converted data
        with open(game_data_file, 'w') as f:
            json.dump(converted_data, f)

        print('Saved converted data to 2019_player_game_data.json')

    # Step 2: Link player IDs
    roster_file = os.path.join(BASE_DIR, "data", "players", "2019-roster-info.csv")
    player_data_file = os.path.join(BASE_DIR, "data", "players", "2019-PlayerData.csv")
    output_file = game_data_file

    link_player_ids(game_data_file, roster_file, player_data_file, output_file)

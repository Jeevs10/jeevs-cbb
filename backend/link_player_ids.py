import json
import csv
from collections import defaultdict
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
}

def normalize_team_name(team_name):
    """Normalize team name from game data to roster format."""
    return TEAM_NAME_MAP.get(team_name, team_name)

def normalize_player_name(name):
    """Normalize player name by removing suffixes, punctuation, accents, and special characters."""
    if not name:
        return name
    
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
    import unicodedata
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    
    return name

def extract_last_name(name):
    """Extract last name from full name, removing suffixes first."""
    if not name:
        return name
    
    # Normalize name first to remove suffixes (Jr., II, III, etc.)
    name = normalize_player_name(name)
    
    # Split by comma first (for "Last, First" format)
    if ',' in name:
        parts = name.split(',')
        name = parts[0].strip()
    
    # Otherwise, split by space and take last part
    parts = name.split()
    if parts:
        return parts[-1].strip()
    return name

def fuzzy_name_similarity(name1, name2):
    """Calculate similarity between two names using SequenceMatcher."""
    return SequenceMatcher(None, name1, name2).ratio()

def load_player_data(player_data_file):
    """Load player data from PlayerData.csv for fuzzy matching."""
    player_data = []
    
    with open(player_data_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            player_data.append({
                'team': row['Team'],
                'name': row['Name'],
                'athlete_id': row['AthleteId']
            })
    
    return player_data

def load_roster_info(roster_file):
    """Load roster info and create mappings for full name and last name matching."""
    player_map = {}  # (normalized_name, team, year) -> ncaa_id
    last_name_map = {}  # (normalized_last_name, team, year) -> ncaa_id
    
    with open(roster_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['Name']
            team = row['Team']
            season = row['Season']
            # Use Sourceid as the ncaa_id to match the player API (AthleteSourceId)
            ncaa_id = row['Sourceid'] if row['Sourceid'] else row['Id']
            
            # Create normalized key for full name matching
            normalized_name = normalize_player_name(name)
            key = (normalized_name, team, season)
            player_map[key] = ncaa_id
            
            # Create normalized key for last name matching
            # extract_last_name already normalizes the name
            last_name = extract_last_name(name)
            last_name_key = (last_name, team, season)
            last_name_map[last_name_key] = ncaa_id
    
    return player_map, last_name_map

def link_player_ids(game_data_file, roster_file, player_data_file, output_file):
    """Link player IDs from roster info to game data."""
    # Load roster info mapping
    player_map, last_name_map = load_roster_info(roster_file)
    
    # Load player data for fuzzy matching
    player_data = load_player_data(player_data_file)
    
    # Create a mapping from (team, normalized_name) to athlete_id for fuzzy matching
    player_data_map = defaultdict(list)
    for player in player_data:
        normalized_name = normalize_player_name(player['name'])
        player_data_map[(player['team'], normalized_name)].append(player['athlete_id'])
    
    # Load game data
    with open(game_data_file, 'r', encoding='utf-8') as f:
        game_data = json.load(f)
    
    # Track statistics
    matched_count = 0
    matched_by_full_name = 0
    matched_by_last_name = 0
    matched_by_fuzzy = 0
    unmatched_count = 0
    unmatched_players = defaultdict(set)
    
    # Add ncaa_id to each game record
    for record in game_data:
        player_name = record.get('pp')
        team = record.get('tt')
        year = str(record.get('year'))
        
        if player_name and team and year:
            # Normalize team name and player name
            normalized_team = normalize_team_name(team)
            normalized_name = normalize_player_name(player_name)
            key = (normalized_name, normalized_team, year)
            ncaa_id = player_map.get(key)
            
            if ncaa_id:
                record['ncaa_id'] = ncaa_id
                matched_count += 1
                matched_by_full_name += 1
            else:
                # Try last name match as fallback
                # extract_last_name already normalizes the name
                last_name = extract_last_name(player_name)
                last_name_key = (last_name, normalized_team, year)
                ncaa_id = last_name_map.get(last_name_key)
                
                if ncaa_id:
                    record['ncaa_id'] = ncaa_id
                    matched_count += 1
                    matched_by_last_name += 1
                else:
                    # Try fuzzy matching against PlayerData.csv
                    best_match = None
                    best_score = 0
                    
                    # Get all players from the same team in PlayerData
                    for (pd_team, pd_name), athlete_ids in player_data_map.items():
                        if pd_team == normalized_team:
                            score = fuzzy_name_similarity(normalized_name, pd_name)
                            if score > best_score and score > 0.7:  # 70% similarity threshold
                                best_score = score
                                best_match = athlete_ids[0] if athlete_ids else None
                    
                    if best_match:
                        record['ncaa_id'] = best_match
                        matched_count += 1
                        matched_by_fuzzy += 1
                    else:
                        record['ncaa_id'] = None
                        unmatched_count += 1
                        unmatched_players[team].add(player_name)
    
    # Save updated game data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(game_data, f, indent=2)
    
    # Print statistics
    total = matched_count + unmatched_count
    print(f"Total game records: {total}")
    print(f"Matched: {matched_count} ({matched_count/total*100:.1f}%)")
    print(f"  - By full name: {matched_by_full_name}")
    print(f"  - By last name: {matched_by_last_name}")
    print(f"  - By fuzzy match: {matched_by_fuzzy}")
    print(f"Unmatched: {unmatched_count} ({unmatched_count/total*100:.1f}%)")
    
    if unmatched_players:
        print("\nUnmatched players by team:")
        for team, players in sorted(unmatched_players.items()):
            print(f"  {team}: {len(players)} players")
            for player in sorted(players)[:5]:  # Show first 5
                print(f"    - {player}")
            if len(players) > 5:
                print(f"    ... and {len(players) - 5} more")
        
        # Save unmatched players to a file for detailed analysis
        with open('/Users/sanjiv/jeevs-cbb/backend/data/games/unmatched_players_2026.csv', 'w', encoding='utf-8') as f:
            f.write("team,player_name\n")
            for team, players in sorted(unmatched_players.items()):
                for player in sorted(players):
                    f.write(f"{team},{player}\n")
        print(f"\nUnmatched players saved to unmatched_players_2026.csv")

if __name__ == "__main__":
    game_data_file = "/Users/sanjiv/jeevs-cbb/backend/data/games/2026_player_game_data.json"
    roster_file = "/Users/sanjiv/jeevs-cbb/backend/data/players/2026-roster-info.csv"
    player_data_file = "/Users/sanjiv/jeevs-cbb/backend/data/players/2026-PlayerData.csv"
    output_file = "/Users/sanjiv/jeevs-cbb/backend/data/games/2026_player_game_data.json"
    
    link_player_ids(game_data_file, roster_file, player_data_file, output_file)

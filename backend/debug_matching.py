import pandas as pd
import unicodedata
from difflib import SequenceMatcher

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
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    
    return name

print("Reading Torvik CSV without column names...")
torvik_df_raw = pd.read_csv('data/players/2026_torvik.csv', header=None)
print(f"Shape: {torvik_df_raw.shape}")
print(f"First row: {torvik_df_raw.iloc[0].tolist()[:10]}")
print(f"Second row: {torvik_df_raw.iloc[1].tolist()[:10]}")

# Now try with column names
column_names = [
    'player_name', 'team', 'conf', 'GP', 'Min_per', 'ORtg', 'usg', 'eFG', 'TS_per',
    'ORB_per', 'DRB_per', 'AST_per', 'TO_per', 'FTM', 'FTA', 'FT_per', 'twoPM',
    'twoPA', 'twoP_per', 'TPM', 'TPA', 'TP_per', 'blk_per', 'stl_per', 'ftr',
    'yr', 'ht', 'num', 'porpag', 'adjoe', 'pfr', 'pid', 'type', 'Rec Rank',
    'ast/tov', 'rimmade', 'rimmade+rimmiss', 'midmade', 'midmade+midmiss',
    'rimmade/(rimmade+rimmiss)', 'midmade/(midmade+midmiss)', 'dunksmade',
    'dunksmiss+dunksmade', 'dunksmade/(dunksmade+dunksmiss)', 'pick', 'drtg',
    'adrtg', 'dporpag', 'stops', 'bpm', 'obpm', 'dbpm', 'gbpm', 'oreb',
    'dreb', 'treb', 'ast', 'stl', 'blk', 'pts', 'role', '3p/100?', 'ogbpm',
    'dgbpm', 'H24'
]

print(f"\nExpected columns: {len(column_names)}")

torvik_df = pd.read_csv('data/players/2026_torvik.csv', header=None, names=column_names)
print(f"Actual columns: {len(torvik_df.columns)}")
print(f"First row: {torvik_df.iloc[0].tolist()[:5]}")
print(f"Player name column: {torvik_df.iloc[0]['player_name']}")
print(f"Team column: {torvik_df.iloc[0]['team']}")
print(f"Conf column: {torvik_df.iloc[0]['conf']}")
print(f"GP column: {torvik_df.iloc[0]['GP']}")

player_df = pd.read_csv('data/players/2026-players_basic.csv')

print("Torvik sample (first 5):")
for i in range(5):
    name = torvik_df.iloc[i]['player_name']
    team = torvik_df.iloc[i]['team']
    conf = torvik_df.iloc[i]['conf']
    norm_name = normalize_player_name(name)
    norm_team = normalize_team_name(team)
    print(f"  {name} @ {team} ({conf}) -> {norm_name} @ {norm_team}")

print("\nPlayer sample (first 5):")
for i in range(5):
    name = player_df.iloc[i]['Name']
    team = player_df.iloc[i]['Team']
    norm_name = normalize_player_name(name)
    norm_team = normalize_team_name(team)
    print(f"  {name} @ {team} -> {norm_name} @ {norm_team}")

print("\nChecking for Nebraska players:")
nebraska_torvik = torvik_df[torvik_df['team'] == 'Nebraska']
print(f"Torvik Nebraska players: {len(nebraska_torvik)}")
if len(nebraska_torvik) > 0:
    print(nebraska_torvik['player_name'].head())

nebraska_players = player_df[player_df['Team'] == 'Nebraska']
print(f"Player data Nebraska players: {len(nebraska_players)}")
if len(nebraska_players) > 0:
    print(nebraska_players['Name'].head())

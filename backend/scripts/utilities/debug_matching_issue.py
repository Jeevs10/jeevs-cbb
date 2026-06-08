import pandas as pd
from difflib import SequenceMatcher

# Load 2025 Torvik data
torvik_file = 'data/players/2025_torvik.csv'
torvik_df = pd.read_csv(torvik_file, header=None, names=[
    'player_name', 'team', 'conf', 'GP', 'Min_per', 'ORtg', 'usg', 'eFG', 'TS_per',
    'ORB_per', 'DRB_per', 'AST_per', 'TO_per', 'FTM', 'FTA', 'FT_per',
    'twoPM', 'twoPA', 'twoP_per', 'TPM', 'TPA', 'TP_per', 'blk_per', 'stl_per',
    'ftr', 'yr', 'ht', 'num', 'porpag', 'adjoe', 'pfr', 'year', 'pid', 'type',
    'Rec Rank', 'ast/tov', 'rimmade', 'rimmade+rimmiss', 'midmade', 'midmade+midmiss',
    'rimmade/(rimmade+rimmiss)', 'midmade/(midmade+midmiss)', 'dunksmade',
    'dunksmiss+dunksmade', 'dunksmade/(dunksmade+dunksmiss)', 'pick', 'drtg',
    'adrtg', 'dporpag', 'stops', 'bpm', 'obpm', 'dbpm', 'gbpm', 'mp',
    'ogbpm', 'dgbpm', 'oreb', 'dreb', 'treb', 'ast', 'stl', 'blk', 'pts', 'role', '3p/100?'
])

# Load 2025 player data
player_file = 'data/players/2025-players_basic.csv'
player_df = pd.read_csv(player_file)

print(f"Torvik shape: {torvik_df.shape}")
print(f"Player shape: {player_df.shape}")
print(f"\nTorvik columns: {torvik_df.columns.tolist()[:5]}")
print(f"Player columns: {player_df.columns.tolist()[:5]}")

print(f"\nFirst Torvik row (player_name, team): {torvik_df.iloc[0]['player_name']}, {torvik_df.iloc[0]['team']}")
print(f"First Player row (Name, Team): {player_df.iloc[0]['Name']}, {player_df.iloc[0]['Team']}")

# Check team normalization
TEAM_MAPPING = {
    'Arizona St.': 'Arizona State',
    'Texas St.': 'Texas State',
    'Florida Atlantic': 'FAU',
    'UCF': 'Central Florida',
    'UC Irvine': 'UC Irvine',
    'USC': 'Southern California',
    'Miami (FL)': 'Miami',
    'Miami (OH)': 'Miami (OH)',
    'Pitt': 'Pittsburgh',
    'LSU': 'Louisiana State',
    'Ole Miss': 'Mississippi',
    'UNC': 'North Carolina',
    'NC State': 'North Carolina State',
    'UAB': 'Alabama Birmingham',
    'SMU': 'Southern Methodist',
    'TCU': 'Texas Christian',
    'UTSA': 'Texas San Antonio',
    'UConn': 'Connecticut',
    'UMass': 'Massachusetts',
    'UNLV': 'Nevada Las Vegas',
    'USF': 'South Florida',
    'UTEP': 'Texas El Paso',
    'UVA': 'Virginia',
    'Cal': 'California',
    'Penn St': 'Penn State',
    'Michigan St': 'Michigan State',
    'Ohio St': 'Ohio State',
    'Oregon St': 'Oregon State',
    'Washington St': 'Washington State',
    'Colorado St': 'Colorado State',
    'Utah St': 'Utah State',
    'New Mexico St': 'New Mexico State',
    'San Jose St': 'San Jose State',
    'Georgia St': 'Georgia State',
    'Georgia Southern': 'Georgia Southern',
    'Louisiana Lafayette': 'Louisiana',
    'Louisiana Monroe': 'Louisiana Monroe',
    'Texas A&M': 'Texas A&M',
    'Texas A&M Corpus Christi': 'Texas A&M Corpus Christi',
    'Texas Tech': 'Texas Tech',
    'West Virginia': 'West Virginia',
    'Iowa St': 'Iowa State',
    'Kansas St': 'Kansas State',
    'Oklahoma St': 'Oklahoma State',
    'Baylor': 'Baylor',
    'TCU': 'Texas Christian',
    'Texas Christian': 'Texas Christian',
    'BYU': 'BYU',
    'Houston': 'Houston',
    'Cincinnati': 'Cincinnati',
    'UCF': 'Central Florida',
    'Central Florida': 'Central Florida',
}

def normalize_team_name(team):
    """Normalize team name using mapping."""
    if pd.isna(team):
        return team
    team = str(team).strip()
    return TEAM_MAPPING.get(team, team)

def normalize_player_name(name):
    """Normalize player name."""
    if pd.isna(name):
        return name
    name = str(name).strip()
    # Remove common suffixes
    for suffix in [' Jr.', ' Jr', ' Sr.', ' Sr', ' III', ' II', ' IV']:
        name = name.replace(suffix, '')
    # Remove punctuation
    name = name.replace('.', '').replace(',', '').replace('-', ' ')
    # Remove extra spaces
    name = ' '.join(name.split())
    return name.lower()

# Test normalization
torvik_name = normalize_player_name(torvik_df.iloc[0]['player_name'])
torvik_team = normalize_team_name(torvik_df.iloc[0]['team'])
player_name = normalize_player_name(player_df.iloc[0]['Name'])
player_team = normalize_team_name(player_df.iloc[0]['Team'])

print(f"\nNormalized Torvik: {torvik_name}, {torvik_team}")
print(f"Normalized Player: {player_name}, {player_team}")

# Check if they match
print(f"\nName match: {torvik_name == player_name}")
print(f"Team match: {torvik_team == player_team}")

# Check a few more samples
print(f"\n--- Sample 2 ---")
torvik_name2 = normalize_player_name(torvik_df.iloc[1]['player_name'])
torvik_team2 = normalize_team_name(torvik_df.iloc[1]['team'])
player_name2 = normalize_player_name(player_df.iloc[1]['Name'])
player_team2 = normalize_team_name(player_df.iloc[1]['Team'])
print(f"Torvik: {torvik_df.iloc[1]['player_name']}, {torvik_df.iloc[1]['team']} -> {torvik_name2}, {torvik_team2}")
print(f"Player: {player_df.iloc[1]['Name']}, {player_df.iloc[1]['Team']} -> {player_name2}, {player_team2}")

# Check unique teams in both datasets
print(f"\n--- Unique Teams ---")
print(f"Torvik unique teams (first 10): {torvik_df['team'].unique()[:10].tolist()}")
print(f"Player unique teams (first 10): {player_df['Team'].unique()[:10].tolist()}")

# Check if any team names overlap
torvik_teams = set(torvik_df['team'].unique())
player_teams = set(player_df['Team'].unique())
overlap = torvik_teams.intersection(player_teams)
print(f"\nTeam name overlap: {len(overlap)} teams")
print(f"Overlapping teams: {list(overlap)[:10]}")

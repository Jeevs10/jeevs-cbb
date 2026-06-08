import pandas as pd
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TEAMS_DIR = DATA_DIR / "teams"
PLAYERS_DIR = DATA_DIR / "players"

print("Filtering out D2 teams (teams without conferences)...")

# 1. Filter historical-team-info.csv
print("\n1. Processing historical-team-info.csv...")
historical_file = TEAMS_DIR / "historical-team-info.csv"
df_historical = pd.read_csv(historical_file, encoding='utf-8-sig')

print(f"Original: {len(df_historical)} teams")
print(f"Teams without conference: {df_historical['Conference'].isna().sum()}")

# Filter to keep only teams with conferences
df_historical_filtered = df_historical[df_historical['Conference'].notna()]
print(f"After filtering: {len(df_historical_filtered)} teams")

# Save filtered file
df_historical_filtered.to_csv(historical_file, index=False, encoding='utf-8-sig')

# 2. Filter 2026-hoop-explorer-teams.csv
print("\n2. Processing 2026-hoop-explorer-teams.csv...")
analytics_file = TEAMS_DIR / "2026-hoop-explorer-teams.csv"
df_analytics = pd.read_csv(analytics_file, encoding='utf-8-sig')

print(f"Original: {len(df_analytics)} teams")
print(f"Teams without conference: {df_analytics['conf'].isna().sum()}")

# Filter to keep only teams with conferences
df_analytics_filtered = df_analytics[df_analytics['conf'].notna()]
print(f"After filtering: {len(df_analytics_filtered)} teams")

# Save filtered file
df_analytics_filtered.to_csv(analytics_file, index=False, encoding='utf-8-sig')

# 3. Filter 2026-roster-info.csv
print("\n3. Processing 2026-roster-info.csv...")
roster_file = PLAYERS_DIR / "2026-roster-info.csv"
df_roster = pd.read_csv(roster_file, encoding='utf-8-sig')

print(f"Original: {len(df_roster)} players")

# Get list of valid team IDs from filtered historical data
valid_team_ids = set(df_historical_filtered['Id'].astype(str))
print(f"Valid team IDs: {len(valid_team_ids)}")

# Filter roster to keep only players from valid teams
df_roster_filtered = df_roster[df_roster['TeamId'].astype(str).isin(valid_team_ids)]
print(f"After filtering: {len(df_roster_filtered)} players")

# Save filtered file
df_roster_filtered.to_csv(roster_file, index=False, encoding='utf-8-sig')

print("\n✅ Filtering complete!")
print(f"Summary:")
print(f"- Historical teams: {len(df_historical)} → {len(df_historical_filtered)}")
print(f"- Analytics teams: {len(df_analytics)} → {len(df_analytics_filtered)}")
print(f"- Roster players: {len(df_roster)} → {len(df_roster_filtered)}")

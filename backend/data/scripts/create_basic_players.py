import pandas as pd
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PLAYERS_DIR = BASE_DIR / "players"

def create_basic_players(year):
    """
    Create basic players dataset from PlayerData.csv
    This ensures all players have basic data for player pages and team rosters
    """
    print(f"Creating basic players dataset for {year}...")
    
    # Load basic player data
    player_data = pd.read_csv(PLAYERS_DIR / f"{year}-PlayerData.csv")
    
    # Select key columns for basic player info
    basic_columns = [
        "Season", "SeasonLabel", "TeamId", "Team", "Conference",
        "AthleteId", "AthleteSourceId", "Name", "Position",
        "Games", "Starts", "Minutes", "Points", "Turnovers", "Fouls",
        "Assists", "Steals", "Blocks", "OffensiveRating", "DefensiveRating",
        "NetRating", "PORPAG", "Usage", "AssistsTurnoverRatio",
        "OffensiveReboundPct", "FreeThrowRate", "EffectiveFieldGoalPct",
        "TrueShootingPct", "FieldGoals Made", "FieldGoals Attempted",
        "FieldGoals Pct", "TwoPointFieldGoals Made", "TwoPointFieldGoals Attempted",
        "TwoPointFieldGoals Pct", "ThreePointFieldGoals Made", "ThreePointFieldGoals Attempted",
        "ThreePointFieldGoals Pct", "FreeThrows Made", "FreeThrows Attempted",
        "FreeThrows Pct", "Rebounds Offensive", "Rebounds Defensive",
        "Rebounds Total", "WinShares Offensive", "WinShares Defensive",
        "WinShares Total", "WinShares TotalPer40"
    ]
    
    # Create basic players dataset
    basic_players = player_data[basic_columns].copy()
    
    # Calculate per-game stats
    basic_players['PPG'] = (basic_players['Points'] / basic_players['Games']).round(1)
    basic_players['RPG'] = (basic_players['Rebounds Total'] / basic_players['Games']).round(1)
    basic_players['APG'] = (basic_players['Assists'] / basic_players['Games']).round(1)
    basic_players['SPG'] = (basic_players['Steals'] / basic_players['Games']).round(1)
    basic_players['BPG'] = (basic_players['Blocks'] / basic_players['Games']).round(1)
    basic_players['TOPG'] = (basic_players['Turnovers'] / basic_players['Games']).round(1)
    basic_players['FPG'] = (basic_players['Fouls'] / basic_players['Games']).round(1)
    basic_players['MPG'] = (basic_players['Minutes'] / basic_players['Games']).round(1)
    
    # Handle division by zero (Games = 0)
    basic_players['PPG'] = basic_players['PPG'].fillna(0)
    basic_players['RPG'] = basic_players['RPG'].fillna(0)
    basic_players['APG'] = basic_players['APG'].fillna(0)
    basic_players['SPG'] = basic_players['SPG'].fillna(0)
    basic_players['BPG'] = basic_players['BPG'].fillna(0)
    basic_players['TOPG'] = basic_players['TOPG'].fillna(0)
    basic_players['FPG'] = basic_players['FPG'].fillna(0)
    basic_players['MPG'] = basic_players['MPG'].fillna(0)
    
    # Add a flag to indicate this is basic data only
    basic_players['data_tier'] = 'basic'
    
    # Save basic players dataset
    output_file = PLAYERS_DIR / f"{year}-players_basic.csv"
    basic_players.to_csv(output_file, index=False)
    
    print(f"✓ Created {output_file} with {len(basic_players):,} players")
    return basic_players

def create_data_summary():
    """Create a summary of all data sources"""
    years = ['2024', '2025', '2026']
    
    print("=== DATA SUMMARY ===")
    for year in years:
        print(f"\n{year} Season:")
        
        # Basic data
        player_data = pd.read_csv(PLAYERS_DIR / f"{year}-PlayerData.csv")
        print(f"  PlayerData: {len(player_data):,} players")
        
        # Advanced data
        try:
            players = pd.read_csv(PLAYERS_DIR / f"{year}-players.csv")
            print(f"  Advanced: {len(players):,} players")
        except:
            print(f"  Advanced: Not available")
        
        # Enriched data
        try:
            enriched = pd.read_csv(PLAYERS_DIR / f"{year}-players_enriched.csv")
            print(f"  Enriched: {len(enriched):,} players ({len(enriched)/len(player_data)*100:.1f}% coverage)")
        except:
            print(f"  Enriched: Not available")
        
        # Basic data (new)
        try:
            basic = pd.read_csv(PLAYERS_DIR / f"{year}-players_basic.csv")
            print(f"  Basic: {len(basic):,} players (100% coverage)")
        except:
            print(f"  Basic: Not created yet")

if __name__ == "__main__":
    # Create basic players for all available years (2019-2026)
    for year in ['2019', '2020', '2021', '2022', '2023', '2024', '2025', '2026']:
        create_basic_players(year)
    
    # Show summary
    create_data_summary()

import pandas as pd
import os

def create_basic_players(year):
    """
    Create basic players dataset from PlayerData.csv
    This ensures all players have basic data for player pages and team rosters
    """
    print(f"Creating basic players dataset for {year}...")
    
    # Load basic player data
    player_data = pd.read_csv(f"{year}-PlayerData.csv")
    
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
    
    # Add a flag to indicate this is basic data only
    basic_players['data_tier'] = 'basic'
    
    # Save basic players dataset
    output_file = f"{year}-players_basic.csv"
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
        player_data = pd.read_csv(f"{year}-PlayerData.csv")
        print(f"  PlayerData: {len(player_data):,} players")
        
        # Advanced data
        try:
            players = pd.read_csv(f"{year}-players.csv")
            print(f"  Advanced: {len(players):,} players")
        except:
            print(f"  Advanced: Not available")
        
        # Enriched data
        try:
            enriched = pd.read_csv(f"{year}-players_enriched.csv")
            print(f"  Enriched: {len(enriched):,} players ({len(enriched)/len(player_data)*100:.1f}% coverage)")
        except:
            print(f"  Enriched: Not available")
        
        # Basic data (new)
        try:
            basic = pd.read_csv(f"{year}-players_basic.csv")
            print(f"  Basic: {len(basic):,} players (100% coverage)")
        except:
            print(f"  Basic: Not created yet")

if __name__ == "__main__":
    # Create basic players for all available years
    for year in ['2024', '2025', '2026']:
        create_basic_players(year)
    
    # Show summary
    create_data_summary()

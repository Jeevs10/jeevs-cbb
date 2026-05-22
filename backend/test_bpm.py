"""Test script for BPM calculations."""

import pandas as pd
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app.utils.bpm_calculator import BPMCalculator

# Load sample data from the basic CSV
basic_csv_path = os.path.join(os.path.dirname(__file__), 'data', '2026-players_basic.csv')

print("Loading sample data from basic CSV...")
df = pd.read_csv(basic_csv_path)

print(f"Loaded {len(df)} players from basic CSV")

# Test BPM calculation on a single player
print("\n" + "="*50)
print("Testing BPM calculation on a single player")
print("="*50)

sample_player = df.iloc[0].to_dict()
print(f"\nSample player: {sample_player.get('Name', 'Unknown')}")
print(f"Team: {sample_player.get('Team', 'Unknown')}")
print(f"Position: {sample_player.get('Position', 'Unknown')}")
print(f"Minutes: {sample_player.get('Minutes', 0)}")
print(f"Games: {sample_player.get('Games', 0)}")
print(f"Points: {sample_player.get('Points', 0)}")
print(f"Rebounds: {sample_player.get('Rebounds Total', 0)}")
print(f"Assists: {sample_player.get('Assists', 0)}")
print(f"Steals: {sample_player.get('Steals', 0)}")
print(f"Blocks: {sample_player.get('Blocks', 0)}")
print(f"Turnovers: {sample_player.get('Turnovers', 0)}")

bpm = BPMCalculator.calculate_bpm(sample_player)
print(f"\nCalculated BPM: {bpm}")

# Test BPM components
bpm_components = BPMCalculator.calculate_bpm_components(sample_player)
if bpm_components:
    print(f"BPM Components: {bpm_components}")

# Test BPM calculation on the entire DataFrame
print("\n" + "="*50)
print("Testing BPM calculation on entire DataFrame")
print("="*50)

df_with_bpm = BPMCalculator.calculate_bpm_for_dataframe(df)

# Count how many players have valid BPM values
valid_bpm_count = df_with_bpm['BPM'].notna().sum()
total_count = len(df_with_bpm)

print(f"\nTotal players: {total_count}")
print(f"Players with valid BPM: {valid_bpm_count}")
print(f"Players with insufficient data: {total_count - valid_bpm_count}")

# Show some statistics
if valid_bpm_count > 0:
    bpm_values = df_with_bpm['BPM'].dropna()
    print(f"\nBPM Statistics:")
    print(f"  Mean: {bpm_values.mean():.2f}")
    print(f"  Median: {bpm_values.median():.2f}")
    print(f"  Std Dev: {bpm_values.std():.2f}")
    print(f"  Min: {bpm_values.min():.2f}")
    print(f"  Max: {bpm_values.max():.2f}")
    
    # Show top 10 players by BPM
    print("\n" + "="*50)
    print("Top 10 Players by BPM")
    print("="*50)
    top_players = df_with_bpm.nlargest(10, 'BPM')[['Name', 'Team', 'BPM', 'Points', 'Rebounds Total', 'Assists']]
    print(top_players.to_string(index=False))
    
    # Show bottom 10 players by BPM
    print("\n" + "="*50)
    print("Bottom 10 Players by BPM")
    print("="*50)
    bottom_players = df_with_bpm.nsmallest(10, 'BPM')[['Name', 'Team', 'BPM', 'Points', 'Rebounds Total', 'Assists']]
    print(bottom_players.to_string(index=False))

print("\n" + "="*50)
print("BPM calculation test completed successfully!")
print("="*50)

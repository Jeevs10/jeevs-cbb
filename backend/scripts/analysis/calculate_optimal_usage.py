"""Calculate optimal usage rate for each player based on game-level data."""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent / "data"
GAMES_DIR = DATA_DIR / "games"
PLAYERS_DIR = DATA_DIR / "players"

def calculate_optimal_usage():
    """Calculate optimal usage rate for each player based on game-level BPM."""
    print("Calculating optimal usage rates...")
    
    # Load 2026 game data
    with open(GAMES_DIR / '2026_player_game_data.json', 'r') as f:
        games = json.load(f)
    
    print(f"Loaded {len(games)} game records")
    
    # Group games by player using ncaa_id (AthleteSourceId)
    player_games = defaultdict(list)
    for game in games:
        ncaa_id = game.get('ncaa_id')
        if ncaa_id:
            player_games[ncaa_id].append(game)
    
    print(f"Found {len(player_games)} unique players by ncaa_id")
    
    # Calculate optimal usage for each player
    optimal_usage_data = []
    
    for player_id, games_list in player_games.items():
        if len(games_list) < 5:  # Need at least 5 games for meaningful analysis
            continue
        
        # Create DataFrame for this player's games
        df = pd.DataFrame(games_list)
        
        # Filter out games with missing data
        df = df.dropna(subset=['Usage', 'bpm'])
        
        if len(df) < 5:
            continue
        
        # Bin usage into ranges (e.g., 0-10, 10-20, 20-30, 30+)
        df['usage_bin'] = pd.cut(df['Usage'], bins=[0, 10, 20, 30, 100], labels=['0-10', '10-20', '20-30', '30+'])
        
        # Calculate average BPM by usage bin
        bpm_by_usage = df.groupby('usage_bin')['bpm'].agg(['mean', 'count'])
        
        # Only consider bins with at least 3 games
        bpm_by_usage = bpm_by_usage[bpm_by_usage['count'] >= 3]
        
        if len(bpm_by_usage) == 0:
            continue
        
        # Find the usage bin with highest average BPM
        optimal_bin = bpm_by_usage['mean'].idxmax()
        optimal_bpm = bpm_by_usage['mean'].max()
        
        # Get the midpoint of the optimal bin as the optimal usage
        if optimal_bin == '0-10':
            optimal_usage = 5
        elif optimal_bin == '10-20':
            optimal_usage = 15
        elif optimal_bin == '20-30':
            optimal_usage = 25
        else:  # 30+
            optimal_usage = 35
        
        # Get current season average usage
        current_usage = df['Usage'].mean()
        current_bpm = df['bpm'].mean()
        
        # Get player name
        player_name = games_list[0].get('pp', 'Unknown')
        team = games_list[0].get('tt', 'Unknown')
        
        optimal_usage_data.append({
            'ncaa_id': player_id,
            'Name': player_name,
            'Team': team,
            'current_usage': current_usage,
            'optimal_usage': optimal_usage,
            'optimal_bpm': optimal_bpm,
            'current_bpm': current_bpm,
            'usage_gap': current_usage - optimal_usage,
            'games_analyzed': len(df)
        })
    
    # Create DataFrame
    optimal_df = pd.DataFrame(optimal_usage_data)
    print(f"Calculated optimal usage for {len(optimal_df)} players")
    
    # Save to CSV
    output_file = PLAYERS_DIR / '2026_optimal_usage.csv'
    optimal_df.to_csv(output_file, index=False)
    print(f"Saved optimal usage data to {output_file}")
    
    # Show some statistics
    print(f"\nOptimal Usage Statistics:")
    print(f"Average optimal usage: {optimal_df['optimal_usage'].mean():.2f}")
    print(f"Average current usage: {optimal_df['current_usage'].mean():.2f}")
    print(f"Players with too much usage (gap > 5): {len(optimal_df[optimal_df['usage_gap'] > 5])}")
    print(f"Players being held back (gap < -5): {len(optimal_df[optimal_df['usage_gap'] < -5])}")
    
    # Show examples
    print(f"\nPlayers with too much on their plate (current > optimal by > 5):")
    too_much = optimal_df[optimal_df['usage_gap'] > 5].nlargest(5, 'usage_gap')
    for _, row in too_much.iterrows():
        print(f"  {row['Name']} ({row['Team']}): {row['current_usage']:.1f}% → {row['optimal_usage']:.1f}% (gap: {row['usage_gap']:.1f})")
    
    print(f"\nPlayers being held back (current < optimal by > 5):")
    held_back = optimal_df[optimal_df['usage_gap'] < -5].nsmallest(5, 'usage_gap')
    for _, row in held_back.iterrows():
        print(f"  {row['Name']} ({row['Team']}): {row['current_usage']:.1f}% → {row['optimal_usage']:.1f}% (gap: {row['usage_gap']:.1f})")
    
    return optimal_df

if __name__ == "__main__":
    calculate_optimal_usage()

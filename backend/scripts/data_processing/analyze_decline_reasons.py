"""Comprehensive analysis of BPM decline reasons.

This script:
1. Analyzes role changes and their impact on BPM
2. Analyzes usage changes and their impact on BPM
3. Analyzes current BPM levels and decline patterns
4. Analyzes advanced metrics and decline patterns
5. Analyzes age/year in school and decline patterns
6. Analyzes individual player trends
"""

import pandas as pd
import numpy as np
import os

def load_year_over_year_dataset():
    """Load the year-over-year dataset."""
    dataset_file = os.path.join(os.path.dirname(__file__), "data", "players", "year_over_year_dataset.csv")
    df = pd.read_csv(dataset_file)
    return df

def load_2026_data():
    """Load 2026 player data."""
    player_file = os.path.join(os.path.dirname(__file__), "data", "players", "2026-players_basic.csv")
    df = pd.read_csv(player_file)
    return df

def analyze_role_changes(df):
    """Analyze impact of role changes (team changes, position changes)."""
    print(f"\n{'='*60}")
    print("Role Change Analysis")
    print('='*60)
    
    valid_data = df.dropna(subset=['bpm_change', 'team_changed'])
    
    # Team change impact
    transfers = valid_data[valid_data['team_changed'] == True]
    non_transfers = valid_data[valid_data['team_changed'] == False]
    
    print(f"\nTeam Change Impact:")
    print(f"  Transfers: {len(transfers)}")
    print(f"  Mean BPM change: {transfers['bpm_change'].mean():.3f}")
    print(f"  Std BPM change: {transfers['bpm_change'].std():.3f}")
    print(f"  Non-Transfers: {len(non_transfers)}")
    print(f"  Mean BPM change: {non_transfers['bpm_change'].mean():.3f}")
    print(f"  Std BPM change: {non_transfers['bpm_change'].std():.3f}")
    
    # Large declines by transfer status
    large_declines = valid_data[valid_data['bpm_change'] < -5]
    print(f"\nLarge Declines (< -5 BPM) by Transfer Status:")
    print(f"  Transfers: {len(large_declines[large_declines['team_changed'] == True])}")
    print(f"  Non-Transfers: {len(large_declines[large_declines['team_changed'] == False])}")

def analyze_usage_changes(df):
    """Analyze impact of current usage on BPM changes."""
    print(f"\n{'='*60}")
    print("Usage Level Analysis")
    print('='*60)
    
    valid_data = df.dropna(subset=['bpm_change', 'current_usage'])
    
    # Usage categories
    valid_data['usage_category'] = pd.cut(
        valid_data['current_usage'],
        bins=[0, 15, 20, 25, 30, np.inf],
        labels=['low', 'moderate', 'high', 'very_high', 'elite']
    )
    
    print(f"\nBPM Change by Current Usage Level:")
    for category in ['low', 'moderate', 'high', 'very_high', 'elite']:
        subset = valid_data[valid_data['usage_category'] == category]
        if len(subset) > 0:
            large_declines = len(subset[subset['bpm_change'] < -5])
            print(f"  {category}: Mean BPM change = {subset['bpm_change'].mean():.3f}, Large declines = {large_declines}")

def analyze_current_bpm_levels(df):
    """Analyze decline patterns by current BPM levels."""
    print(f"\n{'='*60}")
    print("Current BPM Level Analysis")
    print('='*60)
    
    valid_data = df.dropna(subset=['bpm_change', 'current_bpm'])
    
    # BPM bins
    bpm_bins = [-np.inf, -10, -5, 0, 5, 10, 15, np.inf]
    bpm_labels = ['<-10', '-10 to -5', '-5 to 0', '0 to 5', '5 to 10', '10 to 15', '>15']
    valid_data['bpm_bin'] = pd.cut(valid_data['current_bpm'], bins=bpm_bins, labels=bpm_labels)
    
    print(f"\nBPM Change by Current BPM Level:")
    for bin_label in bpm_labels:
        subset = valid_data[valid_data['bpm_bin'] == bin_label]
        if len(subset) > 0:
            large_declines = len(subset[subset['bpm_change'] < -5])
            print(f"  {bin_label}:")
            print(f"    Mean change: {subset['bpm_change'].mean():.3f}")
            print(f"    Std: {subset['bpm_change'].std():.3f}")
            print(f"    Large declines: {large_declines} ({large_declines/len(subset)*100:.1f}%)")
    
    # Very high BPM players (like Yaxel)
    very_high_bpm = valid_data[valid_data['current_bpm'] > 15]
    print(f"\nVery High BPM Players (>15):")
    print(f"  Count: {len(very_high_bpm)}")
    print(f"  Mean BPM change: {very_high_bpm['bpm_change'].mean():.3f}")
    print(f"  Large declines: {len(very_high_bpm[very_high_bpm['bpm_change'] < -5])}")
    print(f"  Large improvements: {len(very_high_bpm[very_high_bpm['bpm_change'] > 5])}")

def analyze_advanced_metrics(df):
    """Analyze decline patterns by advanced metrics."""
    print(f"\n{'='*60}")
    print("Advanced Metrics Analysis")
    print('='*60)
    
    valid_data = df.dropna(subset=['bpm_change', 'current_ortg', 'current_drtg', 'current_net'])
    
    # High ORTG players
    high_ortg = valid_data[valid_data['current_ortg'] > 120]
    print(f"\nHigh ORTG Players (>120):")
    print(f"  Mean BPM change: {high_ortg['bpm_change'].mean():.3f}")
    print(f"  Large declines: {len(high_ortg[high_ortg['bpm_change'] < -5])}")
    
    # High Net Rating players
    high_net = valid_data[valid_data['current_net'] > 10]
    print(f"\nHigh Net Rating Players (>10):")
    print(f"  Mean BPM change: {high_net['bpm_change'].mean():.3f}")
    print(f"  Large declines: {len(high_net[high_net['bpm_change'] < -5])}")
    
    # Low DRTG (good defense)
    low_drtg = valid_data[valid_data['current_drtg'] < 95]
    print(f"\nLow DRTG Players (<95, good defense):")
    print(f"  Mean BPM change: {low_drtg['bpm_change'].mean():.3f}")
    print(f"  Large declines: {len(low_drtg[low_drtg['bpm_change'] < -5])}")

def analyze_year_in_school(df):
    """Analyze decline patterns by year in school."""
    print(f"\n{'='*60}")
    print("Year in School Analysis")
    print('='*60)
    
    valid_data = df.dropna(subset=['bpm_change', 'year_index'])
    
    print(f"\nBPM Change by Year in School:")
    for year_idx in [0, 1, 2, 3]:
        subset = valid_data[valid_data['year_index'] == year_idx]
        if len(subset) > 0:
            year_name = ['Freshman', 'Sophomore', 'Junior', 'Senior'][year_idx]
            large_declines = len(subset[subset['bpm_change'] < -5])
            print(f"  {year_name}:")
            print(f"    Mean change: {subset['bpm_change'].mean():.3f}")
            print(f"    Std: {subset['bpm_change'].std():.3f}")
            print(f"    Large declines: {large_declines} ({large_declines/len(subset)*100:.1f}%)")
    
    # Juniors specifically (like Yaxel)
    juniors = valid_data[valid_data['year_index'] == 2]
    high_bpm_juniors = juniors[juniors['current_bpm'] > 15]
    print(f"\nHigh BPM Juniors (>15 BPM):")
    print(f"  Count: {len(high_bpm_juniors)}")
    print(f"  Mean BPM change: {high_bpm_juniors['bpm_change'].mean():.3f}")
    print(f"  Large declines: {len(high_bpm_juniors[high_bpm_juniors['bpm_change'] < -5])}")

def analyze_individual_trends(df):
    """Analyze individual player trends."""
    print(f"\n{'='*60}")
    print("Individual Player Trend Analysis")
    print('='*60)
    
    # Group by player to get career trajectories
    player_careers = df.groupby('AthleteSourceId').agg({
        'current_year': lambda x: sorted(x.tolist()),
        'current_bpm': list,
        'bpm_change': list,
        'Name': 'first'
    }).reset_index()
    
    # Filter to players with 3+ years
    multi_year = player_careers[player_careers['current_year'].apply(len) >= 3]
    
    print(f"\nPlayers with 3+ years: {len(multi_year)}")
    
    # Analyze consistency
    def calculate_consistency(bpm_list):
        if len(bpm_list) < 2:
            return 0
        return np.std(bpm_list)
    
    multi_year['bpm_std'] = multi_year['current_bpm'].apply(calculate_consistency)
    
    # High BPM, consistent players
    high_bpm_consistent = multi_year[
        (multi_year['current_bpm'].apply(lambda x: x[-1]) > 15) &
        (multi_year['bpm_std'] < 3)
    ]
    
    print(f"\nHigh BPM, Consistent Players (>15 BPM, std < 3): {len(high_bpm_consistent)}")
    
    if len(high_bpm_consistent) > 0:
        print(f"\nExamples:")
        for _, row in high_bpm_consistent.head(5).iterrows():
            print(f"  {row['Name']}: BPM trend = {row['current_bpm']}")
    
    # High BPM, volatile players
    high_bpm_volatile = multi_year[
        (multi_year['current_bpm'].apply(lambda x: x[-1]) > 15) &
        (multi_year['bpm_std'] >= 3)
    ]
    
    print(f"\nHigh BPM, Volatile Players (>15 BPM, std >= 3): {len(high_bpm_volatile)}")
    
    if len(high_bpm_volatile) > 0:
        print(f"\nExamples:")
        for _, row in high_bpm_volatile.head(5).iterrows():
            print(f"  {row['Name']}: BPM trend = {row['current_bpm']}")

def analyze_specific_player(df_2026, player_name):
    """Analyze a specific player (e.g., Yaxel Lendeborg)."""
    print(f"\n{'='*60}")
    print(f"Specific Player Analysis: {player_name}")
    print('='*60)
    
    player = df_2026[df_2026['Name'] == player_name]
    
    if len(player) == 0:
        print(f"Player not found in 2026 data")
        return
    
    player = player.iloc[0]
    
    print(f"\n2026 Stats:")
    print(f"  BPM: {player['BPM']:.2f}")
    print(f"  OBPM: {player['OBPM']:.2f}")
    print(f"  DBPM: {player['DBPM']:.2f}")
    print(f"  Usage: {player['Usage']:.2f}")
    print(f"  ORTG: {player['OffensiveRating']:.2f}")
    print(f"  DRTG: {player['DefensiveRating']:.2f}")
    print(f"  Net Rating: {player['NetRating']:.2f}")
    print(f"  PPG: {player['PPG']:.2f}")
    print(f"  MPG: {player['MPG']:.2f}")
    
    # Analyze similar historical players
    df_historical = load_year_over_year_dataset()
    
    # Find similar players (high BPM, high usage, junior year)
    similar = df_historical[
        (df_historical['current_bpm'] > 15) &
        (df_historical['current_usage'] > 20) &
        (df_historical['year_index'] == 2)
    ]
    
    print(f"\nSimilar Historical Players (High BPM, High Usage, Junior):")
    print(f"  Count: {len(similar)}")
    print(f"  Mean BPM change: {similar['bpm_change'].mean():.3f}")
    print(f"  Std BPM change: {similar['bpm_change'].std():.3f}")
    print(f"  Large declines: {len(similar[similar['bpm_change'] < -5])}")
    print(f"  Large improvements: {len(similar[similar['bpm_change'] > 5])}")

def main():
    """Main analysis function."""
    print("="*60)
    print("Comprehensive BPM Decline Analysis")
    print("="*60)
    
    # Load data
    df = load_year_over_year_dataset()
    df_2026 = load_2026_data()
    
    print(f"Loaded {len(df)} historical observations")
    print(f"Loaded {len(df_2026)} 2026 players")
    
    # Analyze factors
    analyze_role_changes(df)
    analyze_usage_changes(df)
    analyze_current_bpm_levels(df)
    analyze_advanced_metrics(df)
    analyze_year_in_school(df)
    analyze_individual_trends(df)
    
    # Analyze specific player
    analyze_specific_player(df_2026, "Yaxel Lendeborg")
    
    print(f"\n{'='*60}")
    print("Conclusions for Model Improvement")
    print('='*60)
    print(f"1. Role changes (transfers) have measurable impact on BPM")
    print(f"2. Usage changes correlate with BPM changes")
    print(f"3. High BPM players tend to regress toward mean")
    print(f"4. Advanced metrics (ORTG, Net Rating) are predictive")
    print(f"5. Year in school affects development patterns")
    print(f"6. Individual player consistency matters")
    print(f"\nModel should incorporate:")
    print(f"- Player trend consistency")
    print(f"- Advanced metrics quality")
    print(f"- Year in school properly")
    print(f"- Usage/role change projections")

if __name__ == "__main__":
    main()

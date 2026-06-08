"""Analyze survivorship bias in the player development dataset."""

import pandas as pd
import numpy as np
import os

def load_dataset():
    """Load the player development dataset."""
    dataset_file = os.path.join(os.path.dirname(__file__), "data", "players", "player_development_dataset.csv")
    df = pd.read_csv(dataset_file)
    return df

def analyze_single_year_players():
    """Analyze players who only have one year of data (potential NBA departures)."""
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    single_year_players = []
    
    for year in years:
        player_file = os.path.join(os.path.dirname(__file__), "data", "players", f"{year}-players_basic.csv")
        
        if not os.path.exists(player_file):
            continue
        
        df = pd.read_csv(player_file)
        df['year'] = year
        single_year_players.append(df)
    
    combined = pd.concat(single_year_players, ignore_index=True)
    
    # Count players by year
    players_by_year = combined.groupby('year')['AthleteSourceId'].nunique()
    print("Total players by year:")
    print(players_by_year)
    
    return combined

def analyze_freshman_departure():
    """Analyze freshman departure patterns."""
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
    
    freshman_departures = []
    
    for year in years:
        # Load current year data
        current_file = os.path.join(os.path.dirname(__file__), "data", "players", f"{year}-players_basic.csv")
        if not os.path.exists(current_file):
            continue
        
        current_df = pd.read_csv(current_file)
        current_df['year'] = year
        
        # Load next year data
        next_year = year + 1
        next_file = os.path.join(os.path.dirname(__file__), "data", "players", f"{next_year}-players_basic.csv")
        if not os.path.exists(next_file):
            continue
        
        next_df = pd.read_csv(next_file)
        next_df['year'] = next_year
        
        # Find players in current year but not next year
        current_ids = set(current_df['AthleteSourceId'].tolist())
        next_ids = set(next_df['AthleteSourceId'].tolist())
        
        departed_ids = current_ids - next_ids
        
        # Get info on departed players
        departed_players = current_df[current_df['AthleteSourceId'].isin(departed_ids)]
        
        # Filter to likely freshmen (first year in our data)
        # This is approximate - we'd need actual year in school data
        departed_players['departure_year'] = year
        freshman_departures.append(departed_players)
    
    if freshman_departures:
        departed_df = pd.concat(freshman_departures, ignore_index=True)
        
        print(f"\n{'='*60}")
        print("Freshman Departure Analysis")
        print('='*60)
        print(f"Total departures: {len(departed_df)}")
        
        # Analyze by BPM
        print(f"\nDeparted players BPM stats:")
        print(f"  Mean: {departed_df['BPM'].mean():.2f}")
        print(f"  Median: {departed_df['BPM'].median():.2f}")
        print(f"  Std: {departed_df['BPM'].std():.2f}")
        
        # Analyze by usage
        print(f"\nDeparted players Usage stats:")
        print(f"  Mean: {departed_df['Usage'].mean():.2f}")
        print(f"  Median: {departed_df['Usage'].median():.2f}")
        
        # High BPM departures (likely NBA)
        high_bpm_departures = departed_df[departed_df['BPM'] > 5]
        print(f"\nHigh BPM departures (>5 BPM): {len(high_bpm_departures)}")
        print(f"  Mean BPM: {high_bpm_departures['BPM'].mean():.2f}")
        
        return departed_df
    
    return None

def analyze_dataset_bias():
    """Analyze bias in the current development dataset."""
    df = load_dataset()
    
    print(f"\n{'='*60}")
    print("Current Dataset Bias Analysis")
    print('='*60)
    
    # Analyze by year index
    print(f"\nObservations by year index:")
    print(df['year_index'].value_counts().sort_index())
    
    # Analyze current BPM distribution
    print(f"\nCurrent BPM distribution:")
    print(f"  Mean: {df['current_bpm'].mean():.2f}")
    print(f"  Median: {df['current_bpm'].median():.2f}")
    print(f"  Std: {df['current_bpm'].std():.2f}")
    
    # High BPM players in dataset
    high_bpm = df[df['current_bpm'] > 5]
    print(f"\nHigh BPM players (>5 BPM) in dataset: {len(high_bpm)}")
    print(f"  Percentage: {len(high_bpm) / len(df) * 100:.1f}%")
    
    # Very high BPM players (likely NBA candidates)
    very_high_bpm = df[df['current_bpm'] > 10]
    print(f"\nVery high BPM players (>10 BPM) in dataset: {len(very_high_bpm)}")
    print(f"  Percentage: {len(very_high_bpm) / len(df) * 100:.1f}%")
    
    # Analyze by year index for high BPM players
    print(f"\nHigh BPM players by year index:")
    print(high_bpm['year_index'].value_counts().sort_index())

def main():
    """Main analysis function."""
    print("="*60)
    print("Survivorship Bias Analysis")
    print("="*60)
    
    # Analyze single year players
    print("\n1. Analyzing all players (including single-year)...")
    all_players = analyze_single_year_players()
    
    # Analyze freshman departures
    print("\n2. Analyzing freshman departures...")
    departed = analyze_freshman_departure()
    
    # Analyze current dataset bias
    print("\n3. Analyzing current dataset bias...")
    analyze_dataset_bias()
    
    print(f"\n{'='*60}")
    print("Key Findings:")
    print("="*60)
    print("1. Current dataset only includes players with multiple years")
    print("2. High-performing freshmen who leave for NBA are excluded")
    print("3. This creates upward bias in development expectations")
    print("4. Model cannot learn from one-and-done patterns")
    print("\nRecommendations:")
    print("- Add NBA departure indicator")
    print("- Model departure probability separately")
    print("- Use censored regression for right-censored data")
    print("- Include transfer portal data")

if __name__ == "__main__":
    main()

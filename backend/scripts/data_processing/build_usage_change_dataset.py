"""Build dataset with usage changes across years."""

import pandas as pd
import os

def load_player_data(year):
    """Load player data for a specific year."""
    file_path = os.path.join(os.path.dirname(__file__), "data", "players", f"{year}-players_basic.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['year'] = year
        return df
    return None

def build_usage_change_dataset():
    """Build dataset with usage changes between years."""
    print("Building usage change dataset...")
    
    # Load data for multiple years
    years = [2022, 2023, 2024, 2025, 2026]
    all_data = []
    
    for year in years:
        df = load_player_data(year)
        if df is not None:
            all_data.append(df)
            print(f"Loaded {len(df)} players from {year}")
    
    if not all_data:
        print("No data loaded")
        return
    
    combined = pd.concat(all_data, ignore_index=True)
    print(f"Total records: {len(combined)}")
    
    # Sort by player and year
    combined = combined.sort_values(['AthleteSourceId', 'year'])
    
    # Calculate year-over-year changes
    combined['next_year'] = combined.groupby('AthleteSourceId')['year'].shift(-1)
    combined['next_usage'] = combined.groupby('AthleteSourceId')['Usage'].shift(-1)
    combined['usage_change'] = combined['next_usage'] - combined['Usage']
    
    # Calculate year index (years in college)
    combined['years_in_college'] = combined.groupby('AthleteSourceId').cumcount()
    
    # Filter to valid pairs
    valid_pairs = combined.dropna(subset=['next_usage', 'usage_change'])
    
    print(f"Valid year-over-year pairs: {len(valid_pairs)}")
    
    # Save dataset
    output_file = os.path.join(os.path.dirname(__file__), "data", "players", "usage_change_dataset.csv")
    valid_pairs.to_csv(output_file, index=False)
    print(f"Saved to {output_file}")
    
    return valid_pairs

if __name__ == "__main__":
    build_usage_change_dataset()

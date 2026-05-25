"""Build corrected departure dataset excluding seniors.

This script:
1. Identifies seniors (4th+ year or no more eligibility)
2. Only classifies non-senior departures as potential NBA
3. Seniors who depart are classified as graduation
"""

import pandas as pd
import numpy as np
import os

def load_all_years():
    """Load player data for all years."""
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    all_data = []
    
    for year in years:
        player_file = os.path.join(os.path.dirname(__file__), "data", "players", f"{year}-players_basic.csv")
        
        if not os.path.exists(player_file):
            continue
        
        df = pd.read_csv(player_file)
        df['year'] = year
        all_data.append(df)
    
    combined = pd.concat(all_data, ignore_index=True)
    return combined

def identify_player_career_years(df):
    """Identify career year for each player to determine senior status."""
    # Group by player to get career trajectory
    player_careers = df.groupby('AthleteSourceId').agg({
        'year': lambda x: sorted(x.tolist()),
        'Name': 'first'
    }).reset_index()
    
    # Create mapping of player -> career year for each season
    career_year_map = {}
    for _, row in player_careers.iterrows():
        years = row['year']
        for i, year in enumerate(years):
            career_year_map[(row['AthleteSourceId'], year)] = i + 1  # 1-indexed (1 = freshman)
    
    return career_year_map

def identify_departures_corrected(df, career_year_map):
    """Identify departures, excluding seniors from NBA classification."""
    years = sorted(df['year'].unique())
    
    departure_records = []
    
    for i, year in enumerate(years[:-1]):  # Exclude last year
        current_year = year
        next_year = year + 1
        
        # Get players in current year
        current_players = df[df['year'] == current_year].copy()
        
        # Add career year
        current_players['career_year'] = current_players.apply(
            lambda row: career_year_map.get((row['AthleteSourceId'], row['year']), np.nan), axis=1
        )
        
        # Get players in next year
        next_players = df[df['year'] == next_year]
        
        current_ids = set(current_players['AthleteSourceId'].tolist())
        next_ids = set(next_players['AthleteSourceId'].tolist())
        
        departed_ids = current_ids - next_ids
        
        # Get info on departed players
        departed = current_players[current_players['AthleteSourceId'].isin(departed_ids)].copy()
        
        departed['departure_year'] = current_year
        departed['next_year'] = next_year
        departed['departed'] = True
        
        # Classify departure type (excluding seniors from NBA classification)
        departed['departure_type'] = departed.apply(
            lambda row: classify_departure_corrected(row), axis=1
        )
        
        departure_records.append(departed)
    
    if departure_records:
        departures_df = pd.concat(departure_records, ignore_index=True)
        return departures_df
    
    return pd.DataFrame()

def classify_departure_corrected(row):
    """Classify departure reason with year-specific NBA thresholds.
    
    Freshmen: Lower BPM threshold (drafted on potential)
    Juniors: Higher BPM threshold (drafted on performance/track record)
    """
    # Seniors (4th+ year) are always graduation
    if pd.notna(row['career_year']) and row['career_year'] >= 4:
        return 'graduation'
    
    career_year = row['career_year'] if pd.notna(row['career_year']) else 1
    
    # Year-specific NBA thresholds
    # Freshmen: Lower bar - drafted on potential (athleticism, size, upside)
    if career_year == 1:
        if row['BPM'] > 4 and row['Usage'] > 22:
            return 'nba_likely'
        elif row['BPM'] > 6:
            return 'nba_likely'
        elif row['Usage'] > 26 and row['BPM'] > 2:
            return 'nba_possible'
    # Sophomores: Moderate bar - mix of potential and performance
    elif career_year == 2:
        if row['BPM'] > 5 and row['Usage'] > 24:
            return 'nba_likely'
        elif row['BPM'] > 7:
            return 'nba_likely'
        elif row['Usage'] > 27 and row['BPM'] > 3:
            return 'nba_possible'
    # Juniors: Higher bar - must show actual performance (development further along)
    elif career_year == 3:
        if row['BPM'] > 7 and row['Usage'] > 26:
            return 'nba_likely'
        elif row['BPM'] > 9:
            return 'nba_likely'
        elif row['Usage'] > 28 and row['BPM'] > 5:
            return 'nba_possible'
    
    # Low BPM = likely transfer
    if row['BPM'] < -2:
        return 'transfer_likely'
    # Average non-seniors = transfer or other
    else:
        return 'transfer_or_other'

def build_corrected_dataset(df, departures_df, career_year_map):
    """Build corrected dataset with proper departure classification."""
    # Add career_year to main dataframe
    df['career_year'] = df.apply(
        lambda row: career_year_map.get((row['AthleteSourceId'], row['year']), np.nan), axis=1
    )
    
    # Merge departure information
    df = df.merge(departures_df[['AthleteSourceId', 'year', 'departed', 'departure_type']], 
                  on=['AthleteSourceId', 'year'], how='left')
    
    # Fill non-departed players
    df['departed'] = df['departed'].fillna(False)
    df['departure_type'] = df['departure_type'].fillna('returned')
    
    # Create NBA departure indicator (only for non-seniors)
    df['nba_departure'] = df['departure_type'].isin(['nba_likely', 'nba_possible'])
    
    # Create transfer indicator
    df['transfer_departure'] = df['departure_type'].isin(['transfer_likely', 'transfer_or_other'])
    
    # Create graduation indicator
    df['graduation'] = df['departure_type'] == 'graduation'
    
    return df

def analyze_departure_patterns(df):
    """Analyze departure patterns after correction."""
    print(f"\n{'='*60}")
    print("Departure Pattern Analysis (Corrected)")
    print('='*60)
    
    # Add year_index based on career_year
    df['year_index'] = df['career_year'] - 1
    
    # Overall departure breakdown
    print(f"\nDeparture Type Breakdown:")
    print(df['departure_type'].value_counts())
    
    # NBA departure rate by career year
    print(f"\nNBA Departure Rate by Career Year:")
    for career_year in [1, 2, 3]:
        subset = df[df['year_index'] == career_year - 1]  # year_index is 0-indexed
        if len(subset) > 0:
            nba_rate = subset['nba_departure'].mean()
            print(f"  Year {career_year}: {nba_rate:.2%} ({subset['nba_departure'].sum()}/{len(subset)})")
    
    # NBA departure by BPM (non-seniors only)
    non_seniors = df[df['year_index'] < 3]  # Exclude seniors
    print(f"\nNBA Departure Rate by BPM (Non-Seniors Only):")
    bpm_bins = [-np.inf, -5, 0, 5, 10, np.inf]
    bpm_labels = ['<-5', '-5 to 0', '0 to 5', '5 to 10', '>10']
    non_seniors['bpm_bin'] = pd.cut(non_seniors['BPM'], bins=bpm_bins, labels=bpm_labels)
    nba_by_bpm = non_seniors.groupby('bpm_bin')['nba_departure'].agg(['mean', 'count'])
    print(nba_by_bpm)

def main():
    """Build corrected departure dataset."""
    print("="*60)
    print("Building Corrected Departure Dataset")
    print("="*60)
    
    # Load all years
    df = load_all_years()
    print(f"Loaded {len(df)} total player records")
    
    # Identify career years
    career_year_map = identify_player_career_years(df)
    print(f"Mapped career years for {len(career_year_map)} player-seasons")
    
    # Identify departures (corrected)
    departures_df = identify_departures_corrected(df, career_year_map)
    print(f"Identified {len(departures_df)} departures")
    
    # Build corrected dataset
    df_corrected = build_corrected_dataset(df, departures_df, career_year_map)
    
    # Analyze patterns
    analyze_departure_patterns(df_corrected)
    
    # Save dataset
    output_file = os.path.join(os.path.dirname(__file__), "data", "players", "corrected_development_dataset.csv")
    df_corrected.to_csv(output_file, index=False)
    
    print(f"\nSaved corrected dataset to {output_file}")
    print(f"Total observations: {len(df_corrected)}")

if __name__ == "__main__":
    main()

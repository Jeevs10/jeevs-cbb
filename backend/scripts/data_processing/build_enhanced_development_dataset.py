"""Build enhanced player development dataset with departure indicators.

This script:
1. Loads player data across all years
2. Identifies players who departed (NBA, transfer, graduation)
3. Creates departure indicators and reasons
4. Builds features for both development and departure modeling
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

def identify_departures(df):
    """Identify players who departed and classify departure reason."""
    years = sorted(df['year'].unique())
    
    departure_records = []
    
    for i, year in enumerate(years[:-1]):  # Exclude last year (no next year data)
        current_year = year
        next_year = year + 1
        
        # Get players in current year
        current_players = df[df['year'] == current_year]
        
        # Get players in next year
        next_players = df[df['year'] == next_year]
        
        current_ids = set(current_players['AthleteSourceId'].tolist())
        next_ids = set(next_players['AthleteSourceId'].tolist())
        
        departed_ids = current_ids - next_ids
        
        # Get info on departed players
        departed = current_players[current_players['AthleteSourceId'].isin(departed_ids)].copy()
        
        # Classify departure reason
        departed['departure_year'] = current_year
        departed['next_year'] = next_year
        departed['departed'] = True
        
        # Classify departure type
        departed['departure_type'] = departed.apply(classify_departure, axis=1)
        
        departure_records.append(departed)
    
    if departure_records:
        departures_df = pd.concat(departure_records, ignore_index=True)
        return departures_df
    
    return pd.DataFrame()

def classify_departure(row):
    """Classify departure reason based on player characteristics."""
    # High BPM + high usage = likely NBA
    if row['BPM'] > 5 and row['Usage'] > 25:
        return 'nba_likely'
    # Very high BPM = likely NBA regardless of usage
    elif row['BPM'] > 8:
        return 'nba_likely'
    # High usage + decent BPM = potential NBA
    elif row['Usage'] > 28 and row['BPM'] > 2:
        return 'nba_possible'
    # Low BPM = likely transfer or graduation
    elif row['BPM'] < -2:
        return 'transfer_likely'
    # Average players = graduation or transfer
    else:
        return 'graduation_or_transfer'

def build_enhanced_dataset(df, departures_df):
    """Build enhanced dataset with departure indicators."""
    # Merge departure information
    df = df.merge(departures_df[['AthleteSourceId', 'year', 'departed', 'departure_type']], 
                  on=['AthleteSourceId', 'year'], how='left')
    
    # Fill non-departed players
    df['departed'] = df['departed'].fillna(False)
    df['departure_type'] = df['departure_type'].fillna('returned')
    
    # Create NBA departure indicator
    df['nba_departure'] = df['departure_type'].isin(['nba_likely', 'nba_possible'])
    
    # Create transfer indicator
    df['transfer_departure'] = df['departure_type'] == 'transfer_likely'
    
    return df

def create_year_over_year_with_departures(df):
    """Create year-over-year features with departure indicators."""
    # Group by player to get career trajectories
    player_careers = df.groupby('AthleteSourceId').agg({
        'year': lambda x: sorted(x.tolist()),
        'Name': 'first',
        'Team': list,
        'Conference': list,
        'Position': list,
        'Games': list,
        'Minutes': list,
        'Points': list,
        'BPM': list,
        'OBPM': list,
        'DBPM': list,
        'VORP': list,
        'Usage': list,
        'OffensiveRating': list,
        'DefensiveRating': list,
        'NetRating': list,
        'PPG': list,
        'MPG': list,
        'departed': list,
        'departure_type': list,
        'nba_departure': list,
        'transfer_departure': list
    }).reset_index()
    
    features = []
    
    for _, row in player_careers.iterrows():
        years = row['year']
        n_years = len(years)
        
        for i in range(n_years):
            current_year = years[i]
            
            feature = {
                'AthleteSourceId': row['AthleteSourceId'],
                'Name': row['Name'],
                'year': current_year,
                'year_index': i,
                'total_years': n_years,
                
                # Current stats
                'current_team': row['Team'][i],
                'current_conference': row['Conference'][i],
                'current_position': row['Position'][i],
                'current_games': row['Games'][i],
                'current_minutes': row['Minutes'][i],
                'current_points': row['Points'][i],
                'current_bpm': row['BPM'][i] if row['BPM'][i] is not None else np.nan,
                'current_obpm': row['OBPM'][i] if row['OBPM'][i] is not None else np.nan,
                'current_dbpm': row['DBPM'][i] if row['DBPM'][i] is not None else np.nan,
                'current_vorp': row['VORP'][i] if row['VORP'][i] is not None else np.nan,
                'current_usage': row['Usage'][i] if row['Usage'][i] is not None else np.nan,
                'current_ortg': row['OffensiveRating'][i] if row['OffensiveRating'][i] is not None else np.nan,
                'current_drtg': row['DefensiveRating'][i] if row['DefensiveRating'][i] is not None else np.nan,
                'current_net': row['NetRating'][i] if row['NetRating'][i] is not None else np.nan,
                'current_ppg': row['PPG'][i] if row['PPG'][i] is not None else np.nan,
                'current_mpg': row['MPG'][i] if row['MPG'][i] is not None else np.nan,
                
                # Departure indicators
                'departed': row['departed'][i],
                'departure_type': row['departure_type'][i],
                'nba_departure': row['nba_departure'][i],
                'transfer_departure': row['transfer_departure'][i],
            }
            
            # Next year info if available
            if i < n_years - 1:
                feature['next_year'] = years[i + 1]
                feature['next_team'] = row['Team'][i + 1]
                feature['next_bpm'] = row['BPM'][i + 1] if row['BPM'][i + 1] is not None else np.nan
                feature['bpm_change'] = feature['next_bpm'] - feature['current_bpm']
                feature['team_changed'] = feature['current_team'] != feature['next_team']
            else:
                feature['next_year'] = np.nan
                feature['next_team'] = np.nan
                feature['next_bpm'] = np.nan
                feature['bpm_change'] = np.nan
                feature['team_changed'] = np.nan
            
            features.append(feature)
    
    features_df = pd.DataFrame(features)
    return features_df

def main():
    """Build enhanced dataset."""
    print("="*60)
    print("Building Enhanced Player Development Dataset")
    print("="*60)
    
    # Load all years
    df = load_all_years()
    print(f"Loaded {len(df)} total player records")
    
    # Identify departures
    departures_df = identify_departures(df)
    print(f"Identified {len(departures_df)} departures")
    
    # Departure type breakdown
    print(f"\nDeparture Type Breakdown:")
    print(departures_df['departure_type'].value_counts())
    
    # Build enhanced dataset
    df_enhanced = build_enhanced_dataset(df, departures_df)
    
    # Create year-over-year features
    features_df = create_year_over_year_with_departures(df_enhanced)
    print(f"\nCreated {len(features_df)} year observations")
    
    # Save dataset
    output_file = os.path.join(os.path.dirname(__file__), "data", "players", "enhanced_development_dataset.csv")
    features_df.to_csv(output_file, index=False)
    
    print(f"\nSaved enhanced dataset to {output_file}")
    
    # Statistics
    print(f"\nDataset Statistics:")
    print(f"  Total observations: {len(features_df)}")
    print(f"  NBA departures: {features_df['nba_departure'].sum()}")
    print(f"  Transfer departures: {features_df['transfer_departure'].sum()}")
    print(f"  Returned players: {(~features_df['departed']).sum()}")
    
    # NBA departure rate by BPM
    print(f"\nNBA Departure Rate by BPM:")
    bpm_bins = [-np.inf, -5, 0, 5, 10, np.inf]
    bpm_labels = ['<-5', '-5 to 0', '0 to 5', '5 to 10', '>10']
    features_df['bpm_bin'] = pd.cut(features_df['current_bpm'], bins=bpm_bins, labels=bpm_labels)
    nba_by_bpm = features_df.groupby('bpm_bin')['nba_departure'].agg(['mean', 'count'])
    print(nba_by_bpm)

if __name__ == "__main__":
    main()

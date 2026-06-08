"""Build proper year-over-year dataset for position-specific modeling.

This script:
1. Creates year-over-year observations with next-year BPM as target
2. Adds team quality and conference strength
3. Separates by position for position-specific modeling
"""

import pandas as pd
import numpy as np
import os

def load_corrected_dataset():
    """Load the corrected development dataset."""
    dataset_file = os.path.join(os.path.dirname(__file__), "data", "players", "corrected_development_dataset.csv")
    
    if not os.path.exists(dataset_file):
        print(f"Dataset file not found: {dataset_file}")
        return None
    
    df = pd.read_csv(dataset_file)
    return df

def load_team_data():
    """Load team data for conference strength."""
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    team_data = {}
    
    for year in years:
        team_file = os.path.join(os.path.dirname(__file__), "data", "teams", f"{year}-hoop-explorer-teams.csv")
        
        if not os.path.exists(team_file):
            continue
        
        df = pd.read_csv(team_file)
        team_map = {}
        for _, row in df.iterrows():
            team_map[row['team_name']] = {
                'adj_net': row.get('adj_net', 0),
                'conf': row.get('conf', '')
            }
        team_data[year] = team_map
    
    return team_data

def create_year_over_year_observations(df, team_data):
    """Create year-over-year observations with next-year BPM as target."""
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
        'nba_departure': list,
        'transfer_departure': list
    }).reset_index()
    
    # Filter to players with multiple years
    multi_year = player_careers[player_careers['year'].apply(len) > 1]
    
    observations = []
    
    for _, row in multi_year.iterrows():
        years = row['year']
        n_years = len(years)
        
        for i in range(n_years - 1):
            current_year = years[i]
            next_year = years[i + 1]
            
            # Get team quality
            current_team_quality = team_data.get(current_year, {}).get(row['Team'][i], {}).get('adj_net', 0)
            next_team_quality = team_data.get(next_year, {}).get(row['Team'][i + 1], {}).get('adj_net', 0)
            
            obs = {
                'AthleteSourceId': row['AthleteSourceId'],
                'Name': row['Name'],
                'current_year': current_year,
                'next_year': next_year,
                'year_index': i,
                'total_years': n_years,
                'position': row['Position'][i],
                
                # Current year stats
                'current_team': row['Team'][i],
                'current_conference': row['Conference'][i],
                'current_games': row['Games'][i],
                'current_minutes': row['Minutes'][i],
                'current_points': row['Points'][i],
                'current_bpm': row['BPM'][i] if row['BPM'][i] is not None else np.nan,
                'current_obpm': row['OBPM'][i] if row['OBPM'][i] is not None else np.nan,
                'current_dbpm': row['DBPM'][i] if row['DBPM'][i] is not None else np.nan,
                'current_usage': row['Usage'][i] if row['Usage'][i] is not None else np.nan,
                'current_ortg': row['OffensiveRating'][i] if row['OffensiveRating'][i] is not None else np.nan,
                'current_drtg': row['DefensiveRating'][i] if row['DefensiveRating'][i] is not None else np.nan,
                'current_net': row['NetRating'][i] if row['NetRating'][i] is not None else np.nan,
                'current_ppg': row['PPG'][i] if row['PPG'][i] is not None else np.nan,
                'current_mpg': row['MPG'][i] if row['MPG'][i] is not None else np.nan,
                'current_team_quality': current_team_quality,
                
                # Next year stats (target)
                'next_team': row['Team'][i + 1],
                'next_conference': row['Conference'][i + 1],
                'next_bpm': row['BPM'][i + 1] if row['BPM'][i + 1] is not None else np.nan,
                'next_team_quality': next_team_quality,
                
                # Changes
                'team_changed': row['Team'][i] != row['Team'][i + 1],
                'conference_changed': row['Conference'][i] != row['Conference'][i + 1],
                'team_quality_change': next_team_quality - current_team_quality,
            }
            
            # Calculate BPM change
            if not pd.isna(obs['current_bpm']) and not pd.isna(obs['next_bpm']):
                obs['bpm_change'] = obs['next_bpm'] - obs['current_bpm']
            else:
                obs['bpm_change'] = np.nan
            
            observations.append(obs)
    
    obs_df = pd.DataFrame(observations)
    return obs_df

def main():
    """Build year-over-year dataset."""
    print("="*60)
    print("Building Year-Over-Year Dataset")
    print("="*60)
    
    # Load dataset
    df = load_corrected_dataset()
    if df is None:
        return
    
    # Load team data
    team_data = load_team_data()
    
    # Create year-over-year observations
    obs_df = create_year_over_year_observations(df, team_data)
    
    print(f"Created {len(obs_df)} year-over-year observations")
    
    # Save dataset
    output_file = os.path.join(os.path.dirname(__file__), "data", "players", "year_over_year_dataset.csv")
    obs_df.to_csv(output_file, index=False)
    
    print(f"Saved to {output_file}")
    
    # Statistics
    print(f"\nObservations by position:")
    print(obs_df['position'].value_counts())
    
    print(f"\nTransfer observations:")
    print(f"  Team changed: {obs_df['team_changed'].sum()}")
    print(f"  Team stayed: {(~obs_df['team_changed']).sum()}")

if __name__ == "__main__":
    main()

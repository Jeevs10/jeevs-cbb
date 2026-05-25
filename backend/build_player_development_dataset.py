"""Build a dataset for player development/projection modeling.

This script:
1. Loads player data across all years (2019-2026)
2. Links players across years using AthleteSourceId
3. Creates year-over-year performance changes
4. Builds features for development modeling
"""

import pandas as pd
import numpy as np
import os
from collections import defaultdict

def load_roster_data():
    """Load roster data for physical attributes."""
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    roster_data = {}
    
    for year in years:
        roster_file = os.path.join(os.path.dirname(__file__), "data", "players", f"{year}-roster-info.csv")
        
        if not os.path.exists(roster_file):
            continue
        
        df = pd.read_csv(roster_file)
        # Create mapping from Sourceid to physical attributes
        roster_map = {}
        for _, row in df.iterrows():
            roster_map[row['Sourceid']] = {
                'height': row.get('Height', np.nan),
                'weight': row.get('Weight', np.nan),
                'position': row.get('Position', '')
            }
        roster_data[year] = roster_map
        print(f"Loaded roster data for year {year}")
    
    return roster_data

def load_all_years():
    """Load player data for all years."""
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    all_data = []
    
    for year in years:
        player_file = os.path.join(os.path.dirname(__file__), "data", "players", f"{year}-players_basic.csv")
        
        if not os.path.exists(player_file):
            print(f"Player data file not found for year {year}")
            continue
        
        df = pd.read_csv(player_file)
        df['year'] = year
        all_data.append(df)
        print(f"Loaded {len(df)} players for year {year}")
    
    combined = pd.concat(all_data, ignore_index=True)
    print(f"\nTotal records across all years: {len(combined)}")
    
    return combined

def link_players_across_years(df, roster_data):
    """Link player performance across years."""
    # Group by AthleteSourceId to track career trajectories
    player_careers = df.groupby('AthleteSourceId').agg({
        'year': lambda x: sorted(x.tolist()),
        'Name': 'first',
        'Team': list,
        'Conference': list,
        'Position': list,
        'Games': list,
        'Starts': list,
        'Minutes': list,
        'Points': list,
        'Turnovers': list,
        'Fouls': list,
        'Assists': list,
        'Steals': list,
        'Blocks': list,
        'BPM': list,
        'OBPM': list,
        'DBPM': list,
        'VORP': list,
        'Usage': list,
        'AssistsTurnoverRatio': list,
        'OffensiveReboundPct': list,
        'FreeThrowRate': list,
        'EffectiveFieldGoalPct': list,
        'TrueShootingPct': list,
        'OffensiveRating': list,
        'DefensiveRating': list,
        'NetRating': list,
        'PORPAG': list,
        'PPG': list,
        'RPG': list,
        'APG': list,
        'SPG': list,
        'BPG': list,
        'TOPG': list,
        'FPG': list,
        'MPG': list,
        'data_tier': 'first'
    }).reset_index()
    
    # Add physical attributes from roster data
    def get_physical_attrs(row):
        heights = []
        weights = []
        for i, year in enumerate(row['year']):
            if year in roster_data and row['AthleteSourceId'] in roster_data[year]:
                heights.append(roster_data[year][row['AthleteSourceId']]['height'])
                weights.append(roster_data[year][row['AthleteSourceId']]['weight'])
            else:
                heights.append(np.nan)
                weights.append(np.nan)
        return heights, weights
    
    player_careers['height'], player_careers['weight'] = zip(*player_careers.apply(get_physical_attrs, axis=1))
    
    # Filter to players with multiple years
    multi_year_players = player_careers[player_careers['year'].apply(len) > 1]
    print(f"\nPlayers with multiple years: {len(multi_year_players)}")
    
    return multi_year_players

def create_year_over_year_features(careers_df):
    """Create year-over-year features for modeling."""
    features = []
    
    for _, row in careers_df.iterrows():
        years = row['year']
        n_years = len(years)
        
        # For each consecutive year pair, create features
        for i in range(n_years - 1):
            current_year = years[i]
            next_year = years[i + 1]
            
            feature = {
                'AthleteSourceId': row['AthleteSourceId'],
                'Name': row['Name'],
                'current_year': current_year,
                'next_year': next_year,
                'year_index': i,  # 0 = freshman year, 1 = sophomore, etc.
                'total_years': n_years,
                
                # Current year stats
                'current_team': row['Team'][i],
                'current_conference': row['Conference'][i],
                'current_position': row['Position'][i],
                'current_games': row['Games'][i],
                'current_starts': row['Starts'][i],
                'current_minutes': row['Minutes'][i],
                'current_points': row['Points'][i],
                'current_turnovers': row['Turnovers'][i],
                'current_fouls': row['Fouls'][i],
                'current_assists': row['Assists'][i],
                'current_steals': row['Steals'][i],
                'current_blocks': row['Blocks'][i],
                'current_bpm': row['BPM'][i] if row['BPM'][i] is not None else np.nan,
                'current_obpm': row['OBPM'][i] if row['OBPM'][i] is not None else np.nan,
                'current_dbpm': row['DBPM'][i] if row['DBPM'][i] is not None else np.nan,
                'current_vorp': row['VORP'][i] if row['VORP'][i] is not None else np.nan,
                'current_usage': row['Usage'][i] if row['Usage'][i] is not None else np.nan,
                'current_ast_to_ratio': row['AssistsTurnoverRatio'][i] if row['AssistsTurnoverRatio'][i] is not None else np.nan,
                'current_orb_pct': row['OffensiveReboundPct'][i] if row['OffensiveReboundPct'][i] is not None else np.nan,
                'current_ftr': row['FreeThrowRate'][i] if row['FreeThrowRate'][i] is not None else np.nan,
                'current_efg_pct': row['EffectiveFieldGoalPct'][i] if row['EffectiveFieldGoalPct'][i] is not None else np.nan,
                'current_ts_pct': row['TrueShootingPct'][i] if row['TrueShootingPct'][i] is not None else np.nan,
                'current_ortg': row['OffensiveRating'][i] if row['OffensiveRating'][i] is not None else np.nan,
                'current_drtg': row['DefensiveRating'][i] if row['DefensiveRating'][i] is not None else np.nan,
                'current_net': row['NetRating'][i] if row['NetRating'][i] is not None else np.nan,
                'current_porpag': row['PORPAG'][i] if row['PORPAG'][i] is not None else np.nan,
                'current_ppg': row['PPG'][i] if row['PPG'][i] is not None else np.nan,
                'current_rpg': row['RPG'][i] if row['RPG'][i] is not None else np.nan,
                'current_apg': row['APG'][i] if row['APG'][i] is not None else np.nan,
                'current_spg': row['SPG'][i] if row['SPG'][i] is not None else np.nan,
                'current_bpg': row['BPG'][i] if row['BPG'][i] is not None else np.nan,
                'current_topg': row['TOPG'][i] if row['TOPG'][i] is not None else np.nan,
                'current_fpg': row['FPG'][i] if row['FPG'][i] is not None else np.nan,
                'current_mpg': row['MPG'][i] if row['MPG'][i] is not None else np.nan,
                
                # Physical attributes
                'current_height': row['height'][i] if row['height'][i] is not None else np.nan,
                'current_weight': row['weight'][i] if row['weight'][i] is not None else np.nan,
                
                # Next year stats (target variables)
                'next_team': row['Team'][i + 1],
                'next_conference': row['Conference'][i + 1],
                'next_position': row['Position'][i + 1],
                'next_games': row['Games'][i + 1],
                'next_starts': row['Starts'][i + 1],
                'next_minutes': row['Minutes'][i + 1],
                'next_points': row['Points'][i + 1],
                'next_turnovers': row['Turnovers'][i + 1],
                'next_fouls': row['Fouls'][i + 1],
                'next_assists': row['Assists'][i + 1],
                'next_steals': row['Steals'][i + 1],
                'next_blocks': row['Blocks'][i + 1],
                'next_bpm': row['BPM'][i + 1] if row['BPM'][i + 1] is not None else np.nan,
                'next_obpm': row['OBPM'][i + 1] if row['OBPM'][i + 1] is not None else np.nan,
                'next_dbpm': row['DBPM'][i + 1] if row['DBPM'][i + 1] is not None else np.nan,
                'next_vorp': row['VORP'][i + 1] if row['VORP'][i + 1] is not None else np.nan,
                'next_usage': row['Usage'][i + 1] if row['Usage'][i + 1] is not None else np.nan,
                'next_ast_to_ratio': row['AssistsTurnoverRatio'][i + 1] if row['AssistsTurnoverRatio'][i + 1] is not None else np.nan,
                'next_orb_pct': row['OffensiveReboundPct'][i + 1] if row['OffensiveReboundPct'][i + 1] is not None else np.nan,
                'next_ftr': row['FreeThrowRate'][i + 1] if row['FreeThrowRate'][i + 1] is not None else np.nan,
                'next_efg_pct': row['EffectiveFieldGoalPct'][i + 1] if row['EffectiveFieldGoalPct'][i + 1] is not None else np.nan,
                'next_ts_pct': row['TrueShootingPct'][i + 1] if row['TrueShootingPct'][i + 1] is not None else np.nan,
                'next_ortg': row['OffensiveRating'][i + 1] if row['OffensiveRating'][i + 1] is not None else np.nan,
                'next_drtg': row['DefensiveRating'][i + 1] if row['DefensiveRating'][i + 1] is not None else np.nan,
                'next_net': row['NetRating'][i + 1] if row['NetRating'][i + 1] is not None else np.nan,
                'next_porpag': row['PORPAG'][i + 1] if row['PORPAG'][i + 1] is not None else np.nan,
                'next_ppg': row['PPG'][i + 1] if row['PPG'][i + 1] is not None else np.nan,
                'next_rpg': row['RPG'][i + 1] if row['RPG'][i + 1] is not None else np.nan,
                'next_apg': row['APG'][i + 1] if row['APG'][i + 1] is not None else np.nan,
                'next_spg': row['SPG'][i + 1] if row['SPG'][i + 1] is not None else np.nan,
                'next_bpg': row['BPG'][i + 1] if row['BPG'][i + 1] is not None else np.nan,
                'next_topg': row['TOPG'][i + 1] if row['TOPG'][i + 1] is not None else np.nan,
                'next_fpg': row['FPG'][i + 1] if row['FPG'][i + 1] is not None else np.nan,
                'next_mpg': row['MPG'][i + 1] if row['MPG'][i + 1] is not None else np.nan,
                
                # Next year physical attributes
                'next_height': row['height'][i + 1] if row['height'][i + 1] is not None else np.nan,
                'next_weight': row['weight'][i + 1] if row['weight'][i + 1] is not None else np.nan,
            }
            
            # Calculate changes
            feature['team_changed'] = feature['current_team'] != feature['next_team']
            feature['conference_changed'] = feature['current_conference'] != feature['next_conference']
            feature['position_changed'] = feature['current_position'] != feature['next_position']
            
            # Calculate year-over-year changes (if not null)
            if not pd.isna(feature['current_bpm']) and not pd.isna(feature['next_bpm']):
                feature['bpm_change'] = feature['next_bpm'] - feature['current_bpm']
            else:
                feature['bpm_change'] = np.nan
            
            if not pd.isna(feature['current_usage']) and not pd.isna(feature['next_usage']):
                feature['usage_change'] = feature['next_usage'] - feature['current_usage']
            else:
                feature['usage_change'] = np.nan
            
            if not pd.isna(feature['current_mpg']) and not pd.isna(feature['next_mpg']):
                feature['mpg_change'] = feature['next_mpg'] - feature['current_mpg']
            else:
                feature['mpg_change'] = np.nan
            
            # Additional change features
            if not pd.isna(feature['current_ppg']) and not pd.isna(feature['next_ppg']):
                feature['ppg_change'] = feature['next_ppg'] - feature['current_ppg']
            else:
                feature['ppg_change'] = np.nan
            
            if not pd.isna(feature['current_ast_to_ratio']) and not pd.isna(feature['next_ast_to_ratio']):
                feature['ast_to_change'] = feature['next_ast_to_ratio'] - feature['current_ast_to_ratio']
            else:
                feature['ast_to_change'] = np.nan
            
            if not pd.isna(feature['current_efg_pct']) and not pd.isna(feature['next_efg_pct']):
                feature['efg_change'] = feature['next_efg_pct'] - feature['current_efg_pct']
            else:
                feature['efg_change'] = np.nan
            
            features.append(feature)
    
    features_df = pd.DataFrame(features)
    print(f"\nCreated {len(features_df)} year-over-year observations")
    
    return features_df

def add_team_context_features(features_df):
    """Add team context features (team quality, SOS)."""
    # Load team data for each year
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
    
    # Add team quality features
    def get_team_quality(team_name, year):
        if year in team_data and team_name in team_data[year]:
            return team_data[year][team_name]['adj_net']
        return 0.0
    
    def get_conference_strength(team_name, year):
        if year in team_data and team_name in team_data[year]:
            conf = team_data[year][team_name]['conf']
            # Calculate average adj_net for conference
            conf_teams = [v['adj_net'] for k, v in team_data[year].items() if v['conf'] == conf]
            if conf_teams:
                return sum(conf_teams) / len(conf_teams)
        return 0.0
    
    features_df['current_team_quality'] = features_df.apply(
        lambda row: get_team_quality(row['current_team'], row['current_year']), axis=1
    )
    features_df['next_team_quality'] = features_df.apply(
        lambda row: get_team_quality(row['next_team'], row['next_year']), axis=1
    )
    features_df['current_conf_strength'] = features_df.apply(
        lambda row: get_conference_strength(row['current_team'], row['current_year']), axis=1
    )
    features_df['next_conf_strength'] = features_df.apply(
        lambda row: get_conference_strength(row['next_team'], row['next_year']), axis=1
    )
    
    # Calculate team quality change
    features_df['team_quality_change'] = features_df['next_team_quality'] - features_df['current_team_quality']
    features_df['conf_strength_change'] = features_df['next_conf_strength'] - features_df['current_conf_strength']
    
    return features_df

def main():
    """Build the player development dataset."""
    print("="*60)
    print("Building Player Development Dataset")
    print("="*60)
    
    # Load roster data for physical attributes
    roster_data = load_roster_data()
    
    # Load all years
    df = load_all_years()
    
    # Link players across years
    careers_df = link_players_across_years(df, roster_data)
    
    # Create year-over-year features
    features_df = create_year_over_year_features(careers_df)
    
    # Add team context features
    features_df = add_team_context_features(features_df)
    
    # Save dataset
    output_file = os.path.join(os.path.dirname(__file__), "data", "players", "player_development_dataset.csv")
    features_df.to_csv(output_file, index=False)
    
    print(f"\nSaved development dataset to {output_file}")
    print(f"Total observations: {len(features_df)}")
    
    # Print statistics
    print(f"\nDataset Statistics:")
    print(f"  BPM change range: {features_df['bpm_change'].min():.2f} to {features_df['bpm_change'].max():.2f}")
    print(f"  BPM change mean: {features_df['bpm_change'].mean():.2f}")
    print(f"  Team change rate: {features_df['team_changed'].mean():.2%}")
    print(f"  Conference change rate: {features_df['conference_changed'].mean():.2%}")
    
    # Year index distribution
    print(f"\nYear Index Distribution:")
    print(features_df['year_index'].value_counts().sort_index())

if __name__ == "__main__":
    main()

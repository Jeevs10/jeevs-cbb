"""Create RAPM-like metric using game data.

This script creates a RAPM-like metric by combining game-level BPM with
team performance adjustments and opponent quality factors.
"""

import pandas as pd
import os
import json
from collections import defaultdict

def calculate_rapm_for_year(year):
    """Calculate RAPM-like metric for a specific year."""
    # Load game data
    game_file = os.path.join(os.path.dirname(__file__), "data", "games", f"{year}_player_game_data.json")
    
    if not os.path.exists(game_file):
        print(f"Game data file not found for year {year}")
        return None
    
    with open(game_file, 'r', encoding='utf-8') as f:
        games = json.load(f)
    
    print(f"Loaded {len(games)} games for year {year}")
    
    # Aggregate by player
    player_data = defaultdict(lambda: {
        'games': [],
        'bpm_values': [],
        'obpm_values': [],
        'dbpm_values': [],
        'wins': 0,
        'losses': 0,
        'points': [],
        'opp_points': [],
        'quality': [],
        'possessions': [],
        'minutes': []
    })
    
    for game in games:
        ncaa_id = game.get('ncaa_id')
        if not ncaa_id:
            continue
        
        player_data[ncaa_id]['games'].append(game)
        
        # Collect BPM values
        if game.get('bpm') is not None:
            player_data[ncaa_id]['bpm_values'].append(game['bpm'])
        if game.get('Obpm') is not None:
            player_data[ncaa_id]['obpm_values'].append(game['Obpm'])
        if game.get('Dbpm') is not None:
            player_data[ncaa_id]['dbpm_values'].append(game['Dbpm'])
        
        # Track wins/losses
        if game.get('win1') == 1 or game.get('win2') == 1:
            player_data[ncaa_id]['wins'] += 1
        else:
            player_data[ncaa_id]['losses'] += 1
        
        # Collect performance data
        if game.get('pts') is not None:
            player_data[ncaa_id]['points'].append(game['pts'])
        if game.get('quality') is not None:
            player_data[ncaa_id]['quality'].append(game['quality'])
        if game.get('possessions') is not None:
            player_data[ncaa_id]['possessions'].append(game['possessions'])
        if game.get('Min_per') is not None:
            player_data[ncaa_id]['minutes'].append(game['Min_per'])
    
    # Calculate RAPM-like metric for each player
    rapm_data = {}
    for ncaa_id, data in player_data.items():
        if not data['bpm_values'] or len(data['bpm_values']) < 10:
            continue
        
        # Base BPM (weighted by minutes)
        if data['minutes']:
            total_minutes = sum(data['minutes'])
            if total_minutes > 0:
                base_bpm = sum(bpm * min_ for bpm, min_ in zip(data['bpm_values'], data['minutes'])) / total_minutes
                base_obpm = sum(obpm * min_ for obpm, min_ in zip(data['obpm_values'], data['minutes'])) / total_minutes if data['obpm_values'] else None
                base_dbpm = sum(dbpm * min_ for dbpm, min_ in zip(data['dbpm_values'], data['minutes'])) / total_minutes if data['dbpm_values'] else None
            else:
                base_bpm = sum(data['bpm_values']) / len(data['bpm_values'])
                base_obpm = sum(data['obpm_values']) / len(data['obpm_values']) if data['obpm_values'] else None
                base_dbpm = sum(data['dbpm_values']) / len(data['dbpm_values']) if data['dbpm_values'] else None
        else:
            base_bpm = sum(data['bpm_values']) / len(data['bpm_values'])
            base_obpm = sum(data['obpm_values']) / len(data['obpm_values']) if data['obpm_values'] else None
            base_dbpm = sum(data['dbpm_values']) / len(data['dbpm_values']) if data['dbpm_values'] else None
        
        # Win rate adjustment
        total_games = data['wins'] + data['losses']
        win_rate = data['wins'] / total_games if total_games > 0 else 0.5
        win_adjustment = (win_rate - 0.5) * 5  # Scale factor
        
        # Quality adjustment (average opponent quality)
        if data['quality']:
            avg_quality = sum(data['quality']) / len(data['quality'])
            quality_adjustment = (avg_quality - 0.5) * 3  # Scale factor
        else:
            quality_adjustment = 0
        
        # RAPM = Base BPM + Win Adjustment + Quality Adjustment
        rapm = base_bpm + win_adjustment + quality_adjustment
        
        # Offensive RAPM
        if base_obpm is not None:
            off_rapm = base_obpm + win_adjustment * 0.5 + quality_adjustment * 0.3
        else:
            off_rapm = None
        
        # Defensive RAPM
        if base_dbpm is not None:
            def_rapm = base_dbpm + win_adjustment * 0.5 + quality_adjustment * 0.3
        else:
            def_rapm = None
        
        rapm_data[ncaa_id] = {
            'ncaa_id': ncaa_id,
            'year': year,
            'rapm': round(rapm, 2),
            'off_rapm': round(off_rapm, 2) if off_rapm else None,
            'def_rapm': round(def_rapm, 2) if def_rapm else None,
            'base_bpm': round(base_bpm, 2),
            'win_rate': round(win_rate, 3),
            'games_played': len(data['games']),
            'total_minutes': sum(data['minutes']) if data['minutes'] else 0,
        }
    
    return rapm_data

def main():
    """Calculate RAPM for all years."""
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    
    all_rapm = []
    
    for year in years:
        print(f"\nProcessing year {year}...")
        rapm_data = calculate_rapm_for_year(year)
        
        if rapm_data:
            all_rapm.extend(rapm_data.values())
            print(f"  {len(rapm_data)} players with RAPM data")
    
    # Convert to DataFrame
    df = pd.DataFrame(all_rapm)
    
    # Save to CSV
    output_file = os.path.join(os.path.dirname(__file__), "data", "players", "aggregated_rapm.csv")
    df.to_csv(output_file, index=False)
    
    print(f"\nSaved RAPM data to {output_file}")
    print(f"Total records: {len(df)}")
    print(f"Years covered: {df['year'].unique().tolist()}")
    print(f"\nRAPM statistics:")
    print(df['rapm'].describe())
    
    # Merge into player CSV files
    print(f"\nMerging RAPM into player CSV files...")
    for year in years:
        player_file = os.path.join(os.path.dirname(__file__), "data", "players", f"{year}-players_basic.csv")
        if not os.path.exists(player_file):
            continue
        
        df_players = pd.read_csv(player_file)
        
        # Filter RAPM data for this year
        year_rapm = df[df['year'] == year].copy()
        
        # Create mapping
        year_rapm['ncaa_id_str'] = year_rapm['ncaa_id'].astype(str)
        rapm_map = year_rapm.set_index('ncaa_id_str')['rapm'].to_dict()
        off_rapm_map = year_rapm.set_index('ncaa_id_str')['off_rapm'].to_dict()
        def_rapm_map = year_rapm.set_index('ncaa_id_str')['def_rapm'].to_dict()
        
        # Add RAPM to player dataframe
        df_players['ncaa_id_str'] = df_players['AthleteSourceId'].astype(str).str.replace('.0', '', regex=False)
        df_players['RAPM'] = df_players['ncaa_id_str'].map(rapm_map)
        df_players['off_RAPM'] = df_players['ncaa_id_str'].map(off_rapm_map)
        df_players['def_RAPM'] = df_players['ncaa_id_str'].map(def_rapm_map)
        
        # Drop temporary column
        df_players = df_players.drop('ncaa_id_str', axis=1)
        
        # Save
        df_players.to_csv(player_file, index=False)
        print(f"  Updated {year}-players_basic.csv with RAPM values")

if __name__ == "__main__":
    main()

"""Optimize usage allocation at the team level."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

DATA_DIR = Path(__file__).parent / "data"

def analyze_team_usage_distribution():
    """Analyze usage distribution patterns and their relationship to team success."""
    print("Analyzing team usage distribution patterns...")
    
    # Load optimal usage data
    optimal_usage = pd.read_csv(DATA_DIR / "players" / "2026_optimal_usage.csv")
    print(f"Loaded optimal usage for {len(optimal_usage)} players")
    
    # Filter to rotation players (at least 10 games and 10%+ usage)
    optimal_usage = optimal_usage[(optimal_usage['games_analyzed'] >= 10) & (optimal_usage['current_usage'] >= 10)]
    print(f"Filtered to {len(optimal_usage)} rotation players (10+ games, 10%+ usage)")
    
    # Group by team
    team_data = {}
    for _, row in optimal_usage.iterrows():
        team = row['Team']
        if team not in team_data:
            team_data[team] = []
        team_data[team].append({
            'ncaa_id': row['ncaa_id'],
            'Name': row['Name'],
            'current_usage': row['current_usage'],
            'optimal_usage': row['optimal_usage'],
            'usage_gap': row['usage_gap'],
            'current_bpm': row['current_bpm'],
            'optimal_bpm': row['optimal_bpm'],
            'games_analyzed': row['games_analyzed']
        })
    
    print(f"Found {len(team_data)} teams with rotation players")
    
    # Analyze each team's usage distribution
    team_analysis = []
    
    for team, players in team_data.items():
        if len(players) < 5:
            continue
        
        # Sort players by current usage
        players_sorted = sorted(players, key=lambda x: x['current_usage'], reverse=True)
        
        # Calculate distribution metrics
        total_current_usage = sum(p['current_usage'] for p in players)
        total_optimal_usage = sum(p['optimal_usage'] for p in players)
        
        # Calculate usage concentration (Gini coefficient-like measure)
        # How concentrated is usage among top players?
        top_2_usage = sum(p['current_usage'] for p in players_sorted[:2])
        top_3_usage = sum(p['current_usage'] for p in players_sorted[:3])
        usage_concentration = top_2_usage / total_current_usage if total_current_usage > 0 else 0
        
        # Calculate weighted team BPM (usage-weighted)
        weighted_team_bpm = sum(p['current_bpm'] * (p['current_usage'] / total_current_usage) 
                                 for p in players if total_current_usage > 0)
        
        # Calculate potential improvement if players moved to optimal usage
        potential_team_bpm = sum(p['optimal_bpm'] * (p['optimal_usage'] / total_optimal_usage) 
                                for p in players if total_optimal_usage > 0)
        
        # Identify misused players
        overutilized = [p for p in players if p['usage_gap'] > 5]
        underutilized = [p for p in players if p['usage_gap'] < -5]
        
        team_analysis.append({
            'team': team,
            'num_players': len(players),
            'total_current_usage': total_current_usage,
            'total_optimal_usage': total_optimal_usage,
            'usage_concentration': usage_concentration,
            'top_2_usage': top_2_usage,
            'top_3_usage': top_3_usage,
            'weighted_team_bpm': weighted_team_bpm,
            'potential_team_bpm': potential_team_bpm,
            'bpm_improvement_potential': potential_team_bpm - weighted_team_bpm,
            'overutilized_count': len(overutilized),
            'underutilized_count': len(underutilized),
            'top_players': players_sorted[:3],
            'overutilized_players': overutilized[:3],
            'underutilized_players': underutilized[:3],
            'all_players': players
        })
    
    # Create DataFrame
    analysis_df = pd.DataFrame(team_analysis)
    print(f"Analyzed {len(analysis_df)} teams")
    
    # Save summary
    output_file = DATA_DIR / "team_usage_analysis.csv"
    analysis_df[['team', 'num_players', 'total_current_usage', 'total_optimal_usage', 
                  'usage_concentration', 'top_2_usage', 'top_3_usage', 'weighted_team_bpm',
                  'potential_team_bpm', 'bpm_improvement_potential', 
                  'overutilized_count', 'underutilized_count']].to_csv(output_file, index=False)
    print(f"Saved team analysis to {output_file}")
    
    # Show statistics
    print(f"\n=== Team Usage Distribution Statistics ===")
    print(f"Average total team usage: {analysis_df['total_current_usage'].mean():.1f}%")
    print(f"Average usage concentration (top 2 players): {analysis_df['usage_concentration'].mean():.2f}")
    print(f"Average weighted team BPM: {analysis_df['weighted_team_bpm'].mean():.2f}")
    print(f"Average potential BPM improvement: {analysis_df['bpm_improvement_potential'].mean():.2f}")
    
    # Analyze relationship between usage concentration and team BPM
    print(f"\n=== Usage Concentration vs Team BPM ===")
    high_concentration = analysis_df[analysis_df['usage_concentration'] > 0.5]
    low_concentration = analysis_df[analysis_df['usage_concentration'] <= 0.5]
    print(f"High concentration teams (top 2 > 50%): {len(high_concentration)}")
    print(f"  Average weighted BPM: {high_concentration['weighted_team_bpm'].mean():.2f}")
    print(f"Low concentration teams (top 2 <= 50%): {len(low_concentration)}")
    print(f"  Average weighted BPM: {low_concentration['weighted_team_bpm'].mean():.2f}")
    
    # Show examples
    print(f"\n=== Top 5 Teams by BPM Improvement Potential ===")
    top_improvement = analysis_df.nlargest(5, 'bpm_improvement_potential')
    for _, row in top_improvement.iterrows():
        print(f"\n{row['team']}: +{row['bpm_improvement_potential']:.2f} BPM potential")
        print(f"  Current weighted BPM: {row['weighted_team_bpm']:.2f} → Potential: {row['potential_team_bpm']:.2f}")
        print(f"  Usage concentration: {row['usage_concentration']:.2f} (top 2: {row['top_2_usage']:.1f}%)")
        print(f"  Overutilized: {row['overutilized_count']}, Underutilized: {row['underutilized_count']}")
    
    # Save detailed analysis as JSON
    import json
    detailed_output = DATA_DIR / "team_usage_analysis_detailed.json"
    with open(detailed_output, 'w') as f:
        json.dump(team_analysis, f, indent=2)
    print(f"\nSaved detailed analysis to {detailed_output}")
    
    return team_analysis

if __name__ == "__main__":
    analyze_team_usage_distribution()

"""Analyze correlation between usage distribution and team success."""

import pandas as pd
import numpy as np
from pathlib import Path
import json

DATA_DIR = Path(__file__).parent / "data"

def analyze_usage_success_correlation():
    """Analyze how usage distribution correlates with team success metrics."""
    print("Analyzing usage distribution vs team success correlation...")
    
    # Load team usage analysis
    usage_analysis = pd.read_csv(DATA_DIR / "team_usage_analysis.csv")
    print(f"Loaded usage analysis for {len(usage_analysis)} teams")
    
    # Load team success data
    team_data = pd.read_csv(DATA_DIR / "teams" / "2026-hoop-explorer-teams.csv")
    print(f"Loaded team data for {len(team_data)} teams")
    
    # Normalize team names for matching
    usage_analysis['team_normalized'] = usage_analysis['team'].str.lower().str.strip()
    team_data['team_normalized'] = team_data['team_name'].str.lower().str.strip()
    
    # Merge on normalized team names
    merged = usage_analysis.merge(team_data, on='team_normalized', how='inner')
    print(f"Merged {len(merged)} teams")
    
    # Select key success metrics
    success_metrics = ['wins', 'losses', 'adj_net', 'off_adj_ppp', 'def_adj_ppp', 'tempo', 'wab', 'power']
    available_metrics = [m for m in success_metrics if m in merged.columns]
    print(f"Available success metrics: {available_metrics}")
    
    # Calculate correlations
    usage_vars = ['total_current_usage', 'usage_concentration', 'top_2_usage', 'top_3_usage',
                  'weighted_team_bpm', 'overutilized_count', 'underutilized_count']
    
    print(f"\n=== Correlation Analysis ===")
    correlations = {}
    for usage_var in usage_vars:
        for success_metric in available_metrics:
            if usage_var in merged.columns and success_metric in merged.columns:
                corr = merged[usage_var].corr(merged[success_metric])
                correlations[f"{usage_var} vs {success_metric}"] = corr
                print(f"{usage_var:30s} vs {success_metric:20s}: {corr:.3f}")
    
    # Analyze by usage concentration quartiles
    merged['concentration_quartile'] = pd.qcut(merged['usage_concentration'], 4, labels=['Q1 (Low)', 'Q2', 'Q3', 'Q4 (High)'])
    
    print(f"\n=== Team Success by Usage Concentration Quartile ===")
    for quartile in ['Q1 (Low)', 'Q2', 'Q3', 'Q4 (High)']:
        quartile_data = merged[merged['concentration_quartile'] == quartile]
        if len(quartile_data) > 0 and 'adj_net' in quartile_data.columns:
            print(f"\n{quartile} (n={len(quartile_data)}):")
            print(f"  Average Adj Net: {quartile_data['adj_net'].mean():.2f}")
            if 'wins' in quartile_data.columns:
                print(f"  Average Wins: {quartile_data['wins'].mean():.1f}")
            print(f"  Average Usage Concentration: {quartile_data['usage_concentration'].mean():.3f}")
    
    # Identify successful teams with optimal usage patterns
    if 'adj_net' in merged.columns:
        high_adj_net_threshold = merged['adj_net'].quantile(0.75)
        successful_teams = merged[merged['adj_net'] >= high_adj_net_threshold]
        
        print(f"\n=== Successful Teams (Top 25% Adj Net) ===")
        print(f"Count: {len(successful_teams)}")
        print(f"Average usage concentration: {successful_teams['usage_concentration'].mean():.3f}")
        print(f"Average overutilized count: {successful_teams['overutilized_count'].mean():.1f}")
        print(f"Average underutilized count: {successful_teams['underutilized_count'].mean():.1f}")
        
        # Show top successful teams
        print(f"\n=== Top 10 Successful Teams ===")
        top_successful = successful_teams.nlargest(10, 'adj_net')
        for _, row in top_successful.iterrows():
            print(f"{row['team']}: Adj Net {row['adj_net']:.2f}, Wins {row.get('wins', 'N/A')}, "
                  f"Concentration {row['usage_concentration']:.2f}, "
                  f"Over {row['overutilized_count']}, Under {row['underutilized_count']}")
    
    # Identify teams with high improvement potential
    if 'bpm_improvement_potential' in merged.columns:
        high_potential = merged[merged['bpm_improvement_potential'] > 5]
        print(f"\n=== Teams with High Improvement Potential (>5 BPM) ===")
        print(f"Count: {len(high_potential)}")
        if 'adj_net' in high_potential.columns:
            print(f"Average Adj Net: {high_potential['adj_net'].mean():.2f}")
        
        print(f"\n=== Top 10 Teams by Improvement Potential ===")
        top_potential = merged.nlargest(10, 'bpm_improvement_potential')
        for _, row in top_potential.iterrows():
            print(f"{row['team']}: Potential +{row['bpm_improvement_potential']:.2f} BPM, "
                  f"Current Adj Net {row.get('adj_net', 'N/A'):.2f}, "
                  f"Concentration {row['usage_concentration']:.2f}")
    
    # Save correlation results
    correlation_df = pd.DataFrame(list(correlations.items()), columns=['Comparison', 'Correlation'])
    correlation_df.to_csv(DATA_DIR / "usage_success_correlations.csv", index=False)
    print(f"\nSaved correlation results to {DATA_DIR / 'usage_success_correlations.csv'}")
    
    # Save merged data for further analysis
    merged.to_csv(DATA_DIR / "usage_success_merged.csv", index=False)
    print(f"Saved merged data to {DATA_DIR / 'usage_success_merged.csv'}")
    
    return merged, correlations

if __name__ == "__main__":
    analyze_usage_success_correlation()

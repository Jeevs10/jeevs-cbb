"""Analyze team archetype composition and its impact on team success."""

import pandas as pd
import numpy as np
from pathlib import Path
import json

DATA_DIR = Path(__file__).parent / "data"

# Archetype labels from frontend
ARCHETYPE_LABELS = {
    "PG": "Point Guard",
    "CG": "Combo Guard",
    "WG": "Wing Guard",
    "s-PG": "Scoring Guard",
    "WF": "Wing Forward",
    "S-PF": "Stretch Forward",
    "PF/C": "Hybrid Big",
    "C": "Center",
}

def analyze_archetype_composition():
    """Analyze how team archetype composition correlates with team success, adjusting for minutes."""
    print("Analyzing team archetype composition with minutes adjustment...")
    
    # Load player data with archetypes
    import sys
    sys.path.append('.')
    from app.core.data_loader import df
    
    df_2026 = df[df['year'] == 2026].copy()
    print(f"Loaded {len(df_2026)} players for 2026")
    
    # Filter to players with archetype data and minutes
    df_2026 = df_2026[df_2026['posClass'].notna()]
    df_2026 = df_2026[df_2026['Minutes'].notna()]
    print(f"Filtered to {len(df_2026)} players with archetype and minutes data")
    
    # Group by team and collect archetype data with minutes
    team_data_list = []
    for team in df_2026['Team'].unique():
        team_players = df_2026[df_2026['Team'] == team]
        
        # Calculate minutes-weighted archetype composition
        total_minutes = team_players['Minutes'].sum()
        archetype_minutes = {}
        for archetype in ARCHETYPE_LABELS.keys():
            archetype_players = team_players[team_players['posClass'] == archetype]
            archetype_minutes[archetype] = archetype_players['Minutes'].sum()
        
        # Calculate archetype percentages by minutes
        archetype_pct = {}
        for archetype in ARCHETYPE_LABELS.keys():
            if total_minutes > 0:
                archetype_pct[archetype] = archetype_minutes[archetype] / total_minutes
            else:
                archetype_pct[archetype] = 0
        
        # Calculate weighted team BPM (usage-weighted)
        if team_players['Usage'].sum() > 0:
            weighted_bpm = (team_players['BPM'] * team_players['Usage'] / 100).sum()
        else:
            weighted_bpm = team_players['BPM'].mean()
        
        team_data_list.append({
            'team': team,
            'total_minutes': total_minutes,
            'total_players': len(team_players),
            'weighted_team_bpm': weighted_bpm,
            **{f'minutes_{archetype}': archetype_minutes[archetype] for archetype in ARCHETYPE_LABELS.keys()},
            **{f'pct_minutes_{archetype}': archetype_pct[archetype] for archetype in ARCHETYPE_LABELS.keys()},
        })
    
    team_analysis = pd.DataFrame(team_data_list)
    print(f"Analyzed {len(team_analysis)} teams with archetype data")
    
    # Load team success data
    team_success = pd.read_csv(DATA_DIR / "teams" / "2026-hoop-explorer-teams.csv")
    team_success['team_normalized'] = team_success['team_name'].str.lower().str.strip()
    team_analysis['team_normalized'] = team_analysis['team'].str.lower().str.strip()
    
    # Merge with success data
    merged = team_analysis.merge(team_success, on='team_normalized', how='inner')
    print(f"Merged with success data: {len(merged)} teams")
    
    # Calculate correlations between archetype composition and success
    success_metrics = ['wins', 'adj_net', 'off_adj_ppp', 'def_adj_ppp']
    archetype_cols = [f'pct_minutes_{archetype}' for archetype in ARCHETYPE_LABELS.keys()]
    
    print(f"\n=== Archetype Composition (Minutes-Weighted) vs Team Success Correlations ===")
    correlations = {}
    for arch_col in archetype_cols:
        arch_name = arch_col.replace('pct_minutes_', '')
        for metric in success_metrics:
            if metric in merged.columns:
                corr = merged[arch_col].corr(merged[metric])
                correlations[f"{arch_name} vs {metric}"] = corr
                if abs(corr) > 0.1:  # Only show meaningful correlations
                    print(f"{ARCHETYPE_LABELS.get(arch_name, arch_name):20s} vs {metric:15s}: {corr:.3f}")
    
    # Analyze successful teams' archetype composition
    if 'adj_net' in merged.columns:
        high_adj_net_threshold = merged['adj_net'].quantile(0.75)
        successful_teams = merged[merged['adj_net'] >= high_adj_net_threshold]
        
        print(f"\n=== Successful Teams (Top 25% Adj Net) Archetype Composition (Minutes-Weighted) ===")
        print(f"Count: {len(successful_teams)}")
        for archetype in ARCHETYPE_LABELS.keys():
            avg_pct = successful_teams[f'pct_minutes_{archetype}'].mean()
            print(f"{ARCHETYPE_LABELS[archetype]:20s}: {avg_pct:.2%}")
    
    # Identify optimal archetype combinations
    print(f"\n=== Top 10 Teams by Adj Net with Archetype Breakdown (Minutes-Weighted) ===")
    top_teams = merged.nlargest(10, 'adj_net')
    for _, row in top_teams.iterrows():
        print(f"\n{row['team_name']}: Adj Net {row['adj_net']:.2f}, Wins {row.get('wins', 'N/A')}")
        for archetype in ARCHETYPE_LABELS.keys():
            pct = row[f'pct_minutes_{archetype}']
            if pct > 0.01:  # Only show if >1% of minutes
                print(f"  {ARCHETYPE_LABELS[archetype]}: {pct:.1%}")
    
    # Find optimal composition patterns
    print(f"\n=== Optimal Composition Patterns ===")
    
    # Group by top performers and find common patterns
    top_quartile = merged[merged['adj_net'] >= merged['adj_net'].quantile(0.75)]
    bottom_quartile = merged[merged['adj_net'] <= merged['adj_net'].quantile(0.25)]
    
    print(f"\nTop Quartile vs Bottom Quartile Comparison:")
    for archetype in ARCHETYPE_LABELS.keys():
        top_avg = top_quartile[f'pct_minutes_{archetype}'].mean()
        bottom_avg = bottom_quartile[f'pct_minutes_{archetype}'].mean()
        diff = top_avg - bottom_avg
        if abs(diff) > 0.05:  # Only show meaningful differences
            print(f"{ARCHETYPE_LABELS[archetype]:20s}: Top {top_avg:.1%} vs Bottom {bottom_avg:.1%} (diff: {diff:+.1%})")
    
    # Save correlation results
    correlation_df = pd.DataFrame(list(correlations.items()), columns=['Comparison', 'Correlation'])
    correlation_df.to_csv(DATA_DIR / "archetype_success_correlations.csv", index=False)
    print(f"\nSaved correlation results to {DATA_DIR / 'archetype_success_correlations.csv'}")
    
    # Save merged data
    merged.to_csv(DATA_DIR / "archetype_team_analysis.csv", index=False)
    print(f"Saved merged data to {DATA_DIR / 'archetype_team_analysis.csv'}")
    
    return merged, correlations

if __name__ == "__main__":
    analyze_archetype_composition()

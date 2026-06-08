"""
BPM Change Analysis Script

This script analyzes BPM changes for players across their available years,
identifies factors that correlate with high BPM, and prepares data for
predictive modeling.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import json

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent))

from app.core.data_loader import df

def analyze_bpm_data():
    """Analyze the BPM data structure and availability."""
    print("=" * 60)
    print("BPM DATA ANALYSIS")
    print("=" * 60)
    
    # Check if BPM columns exist
    bpm_cols = ['BPM', 'OBPM', 'DBPM']
    for col in bpm_cols:
        if col in df.columns:
            non_null_count = df[col].notna().sum()
            total_count = len(df)
            print(f"{col}: {non_null_count}/{total_count} non-null values ({non_null_count/total_count*100:.1f}%)")
        else:
            print(f"{col}: Column not found")
    
    # Analyze by year
    print("\n--- BPM Availability by Year ---")
    for year in sorted(df['year'].unique()):
        year_df = df[df['year'] == year]
        if 'BPM' in year_df.columns:
            bpm_count = year_df['BPM'].notna().sum()
            print(f"Year {year}: {bpm_count}/{len(year_df)} players with BPM ({bpm_count/len(year_df)*100:.1f}%)")
    
    # Analyze players with multiple years
    print("\n--- Players with Multiple Years ---")
    player_year_counts = df.groupby('player_key')['year'].nunique()
    multi_year_players = player_year_counts[player_year_counts > 1]
    print(f"Players with 2+ years: {len(multi_year_players)}")
    print(f"Players with 3+ years: {len(player_year_counts[player_year_counts > 2])}")
    print(f"Players with 4+ years: {len(player_year_counts[player_year_counts > 3])}")
    
    return df

def calculate_bpm_change(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate BPM change for players across consecutive years."""
    print("\n" + "=" * 60)
    print("CALCULATING BPM CHANGES")
    print("=" * 60)
    
    # Filter to players with BPM data
    if 'BPM' not in df.columns:
        print("BPM column not found in dataframe")
        return pd.DataFrame()
    
    bpm_df = df[df['BPM'].notna()].copy()
    
    # Filter out extreme BPM values based on sample size (GP)
    # For players with low GP (<10), center extreme BPM values toward mean
    # For players with sufficient GP, filter out truly extreme values
    print(f"Before filtering: {len(bpm_df)} players with BPM data")
    print(f"BPM range: {bpm_df['BPM'].min():.2f} to {bpm_df['BPM'].max():.2f}")
    
    # Check if GP column exists
    if 'GP' in bpm_df.columns:
        print(f"GP column found with range: {bpm_df['GP'].min()} to {bpm_df['GP'].max()}")
        # For low sample size players (<10 GP), center extreme BPM values
        low_gp_mask = bpm_df['GP'] < 10
        extreme_bpm_mask = (bpm_df['BPM'] < -15) | (bpm_df['BPM'] > 20)
        
        # Center extreme values for low GP players
        bpm_mean = bpm_df['BPM'].mean()
        bpm_df.loc[low_gp_mask & extreme_bpm_mask, 'BPM'] = bpm_mean
        
        print(f"Centered {sum(low_gp_mask & extreme_bpm_mask)} extreme BPM values for low GP players")
        
        # Filter remaining extreme values for high GP players
        high_gp_mask = ~low_gp_mask
        bpm_df = bpm_df[~(high_gp_mask & ((bpm_df['BPM'] < -20) | (bpm_df['BPM'] > 25)))]
    else:
        print("GP column not found, using simple filtering")
        # If no GP column, just filter extreme values
        bpm_df = bpm_df[(bpm_df['BPM'] >= -20) & (bpm_df['BPM'] <= 25)]
    
    print(f"After filtering: {len(bpm_df)} players")
    print(f"Filtered BPM range: {bpm_df['BPM'].min():.2f} to {bpm_df['BPM'].max():.2f}")
    
    # Sort by player and year
    bpm_df = bpm_df.sort_values(['player_key', 'year'])
    
    # Calculate year-over-year BPM changes
    bpm_changes = []
    
    for player_key, player_df in bpm_df.groupby('player_key'):
        player_df = player_df.sort_values('year')
        
        if len(player_df) < 2:
            continue
        
        for i in range(len(player_df) - 1):
            current_row = player_df.iloc[i]
            next_row = player_df.iloc[i + 1]
            
            change = {
                'player_key': player_key,
                'player_name': current_row.get('player_name', ''),
                'team': current_row.get('team', ''),
                'year_from': current_row['year'],
                'year_to': next_row['year'],
                'bpm_from': current_row['BPM'],
                'bpm_to': next_row['BPM'],
                'bpm_change': next_row['BPM'] - current_row['BPM'],
                'obpm_from': current_row.get('OBPM'),
                'obpm_to': next_row.get('OBPM'),
                'obpm_change': next_row.get('OBPM') - current_row.get('OBPM') if pd.notna(current_row.get('OBPM')) and pd.notna(next_row.get('OBPM')) else None,
                'dbpm_from': current_row.get('DBPM'),
                'dbpm_to': next_row.get('DBPM'),
                'dbpm_change': next_row.get('DBPM') - current_row.get('DBPM') if pd.notna(current_row.get('DBPM')) and pd.notna(next_row.get('DBPM')) else None,
            }
            
            # Add basic stats that might be useful for prediction
            basic_stat_cols = ['PPG', 'APG', 'RPG', 'SPG', 'BPG', 'MPG', 'Usage', 'off_rtg', 'def_rtg', 'off_usage']
            for col in basic_stat_cols:
                if col in player_df.columns:
                    change[f'{col}_from'] = current_row[col]
                    change[f'{col}_to'] = next_row[col]
                    change[f'{col}_change'] = next_row[col] - current_row[col] if pd.notna(current_row[col]) and pd.notna(next_row[col]) else None
            
            # Add Torvik stats if available
            torvik_stat_cols = [
                'Min_per', 'ORtg', 'usgG1', 'eFG', 'TS_per',
                'ORB_per', 'DRB_per', 'AST_per', 'TO_per',
                'FT_per', 'twoP_per', 'TP_per', 'blk_per', 'stl_per',
                'ftr', 'porpag', 'adjoe', 'pfr', 'drtg', 'adrtg',
                'dporpag', 'stops', 'oreb', 'dreb', 'treb',
                'ast', 'stl', 'blk', 'pts'
            ]
            for col in torvik_stat_cols:
                if col in player_df.columns:
                    change[f'{col}_from'] = current_row[col]
                    change[f'{col}_to'] = next_row[col]
                    change[f'{col}_change'] = next_row[col] - current_row[col] if pd.notna(current_row[col]) and pd.notna(next_row[col]) else None
            
            # Add class/year information for age-based improvement analysis
            change['class_from'] = current_row.get('roster.year_class')
            change['class_to'] = next_row.get('roster.year_class')
            change['year_from'] = current_row['year']
            change['year_to'] = next_row['year']
            
            bpm_changes.append(change)
    
    bpm_change_df = pd.DataFrame(bpm_changes)
    
    # Filter out extreme BPM changes (likely data errors)
    # Normal year-over-year BPM change should be within -15 to +15
    print(f"\nBefore filtering BPM changes: {len(bpm_change_df)} transitions")
    print(f"BPM change range: {bpm_change_df['bpm_change'].min():.2f} to {bpm_change_df['bpm_change'].max():.2f}")
    
    bpm_change_df = bpm_change_df[(bpm_change_df['bpm_change'] >= -15) & (bpm_change_df['bpm_change'] <= 15)]
    
    print(f"After filtering extreme changes: {len(bpm_change_df)} transitions")
    print(f"Filtered BPM change range: {bpm_change_df['bpm_change'].min():.2f} to {bpm_change_df['bpm_change'].max():.2f}")
    
    print(f"Average BPM change: {bpm_change_df['bpm_change'].mean():.3f}")
    print(f"Std dev BPM change: {bpm_change_df['bpm_change'].std():.3f}")
    print(f"Median BPM change: {bpm_change_df['bpm_change'].median():.3f}")
    
    return bpm_change_df

def analyze_bpm_factors(df: pd.DataFrame, bpm_change_df: pd.DataFrame):
    """Analyze factors that correlate with high BPM and BPM changes."""
    print("\n" + "=" * 60)
    print("ANALYZING BPM FACTORS")
    print("=" * 60)
    
    # Correlation with BPM
    if 'BPM' in df.columns:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        correlations = {}
        
        for col in numeric_cols:
            if col != 'BPM' and col != 'OBPM' and col != 'DBPM':
                corr = df[col].corr(df['BPM'])
                if not np.isnan(corr):
                    correlations[col] = abs(corr)
        
        # Sort by correlation strength
        sorted_correlations = sorted(correlations.items(), key=lambda x: x[1], reverse=True)
        
        print("\n--- Top 15 Features Correlated with BPM ---")
        for col, corr in sorted_correlations[:15]:
            print(f"{col}: {corr:.3f}")
    
    # Correlation with BPM change
    if len(bpm_change_df) > 0:
        numeric_cols = bpm_change_df.select_dtypes(include=[np.number]).columns
        change_correlations = {}
        
        for col in numeric_cols:
            if col != 'bpm_change' and 'change' not in col:
                corr = bpm_change_df[col].corr(bpm_change_df['bpm_change'])
                if not np.isnan(corr):
                    change_correlations[col] = abs(corr)
        
        sorted_change_correlations = sorted(change_correlations.items(), key=lambda x: x[1], reverse=True)
        
        print("\n--- Top 15 Features Correlated with BPM Change ---")
        for col, corr in sorted_change_correlations[:15]:
            print(f"{col}: {corr:.3f}")
    
    return sorted_correlations, sorted_change_correlations

def prepare_modeling_data(bpm_change_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """Prepare data for BPM prediction modeling using Torvik and basic player stats."""
    print("\n" + "=" * 60)
    print("PREPARING MODELING DATA")
    print("=" * 60)
    
    # Select features from Torvik and basic player data (excluding BPM-related features)
    # These are the actual performance metrics that should predict BPM change
    feature_cols = [
        # Basic stats
        'PPG_from', 'APG_from', 'RPG_from', 'SPG_from', 'BPG_from', 'MPG_from',
        'Usage_from', 'off_rtg_from', 'def_rtg_from', 'off_usage_from',
        # Torvik stats (if available)
        'Min_per_from', 'ORtg_from', 'usgG1_from', 'eFG_from', 'TS_per_from',
        'ORB_per_from', 'DRB_per_from', 'AST_per_from', 'TO_per_from',
        'FT_per_from', 'twoP_per_from', 'TP_per_from', 'blk_per_from', 'stl_per_from',
        'ftr_from', 'porpag_from', 'adjoe_from', 'pfr_from', 'drtg_from', 'adrtg_from',
        'dporpag_from', 'stops_from', 'oreb_from', 'dreb_from', 'treb_from',
        'ast_from', 'stl_from', 'blk_from', 'pts_from'
    ]
    
    # Filter to available columns
    available_features = [col for col in feature_cols if col in bpm_change_df.columns]
    
    # Add class features (encode as dummy variables)
    if 'class_from' in bpm_change_df.columns:
        print("Adding class features...")
        # Create class dummy variables
        class_dummies = pd.get_dummies(bpm_change_df['class_from'], prefix='class_from')
        bpm_change_df = pd.concat([bpm_change_df, class_dummies], axis=1)
        class_features = [col for col in bpm_change_df.columns if col.startswith('class_from_')]
        available_features.extend(class_features)
        print(f"Added {len(class_features)} class features")
    
    modeling_df = bpm_change_df[available_features + ['bpm_change', 'player_key', 'year_from', 'year_to']].copy()
    
    # Drop rows with missing target
    modeling_df = modeling_df.dropna(subset=['bpm_change'])
    
    # Drop rows with all missing features
    modeling_df = modeling_df.dropna(subset=available_features, how='all')
    
    print(f"Modeling dataset: {len(modeling_df)} samples")
    print(f"Features: {available_features}")
    
    # Save for future use
    output_path = Path(__file__).parent / "data" / "bpm_change_modeling_data.csv"
    output_path.parent.mkdir(exist_ok=True)
    modeling_df.to_csv(output_path, index=False)
    print(f"Saved modeling data to {output_path}")
    
    # Save feature list
    feature_info = {
        'features': available_features,
        'target': 'bpm_change',
        'sample_count': len(modeling_df),
        'years': sorted(modeling_df['year_from'].unique().tolist())
    }
    
    feature_path = Path(__file__).parent / "data" / "bpm_change_features.json"
    with open(feature_path, 'w') as f:
        json.dump(feature_info, f, indent=2)
    print(f"Saved feature info to {feature_path}")
    
    return modeling_df, feature_info

def main():
    """Main analysis pipeline."""
    # Analyze BPM data structure
    df_analyzed = analyze_bpm_data()
    
    # Calculate BPM changes
    bpm_change_df = calculate_bpm_change(df_analyzed)
    
    if len(bpm_change_df) > 0:
        # Analyze factors
        bpm_correlations, change_correlations = analyze_bpm_factors(df_analyzed, bpm_change_df)
        
        # Prepare modeling data
        modeling_df, feature_info = prepare_modeling_data(bpm_change_df)
        
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print(f"Total players analyzed: {df_analyzed['player_key'].nunique()}")
        print(f"Total year-over-year transitions: {len(bpm_change_df)}")
        print(f"Modeling samples: {len(modeling_df)}")
    else:
        print("\nNo BPM change data available for analysis")

if __name__ == "__main__":
    main()

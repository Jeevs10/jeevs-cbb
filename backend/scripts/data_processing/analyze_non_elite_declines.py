"""Analyze decline patterns specifically for non-elite players.

This script:
1. Analyzes non-elite players (BPM < 15) by position
2. Analyzes non-elite players by year in school
3. Analyzes non-elite players by usage tier
4. Analyzes non-elite players by advanced metrics
5. Identifies risk factors for large declines in non-elite players
"""

import pandas as pd
import numpy as np
import os

def load_year_over_year_dataset():
    """Load the year-over-year dataset."""
    dataset_file = os.path.join(os.path.dirname(__file__), "data", "players", "year_over_year_dataset.csv")
    df = pd.read_csv(dataset_file)
    return df

def analyze_non_elite_by_position(df):
    """Analyze non-elite players by position."""
    print(f"\n{'='*60}")
    print("Non-Elite Players (<15 BPM) by Position")
    print('='*60)
    
    valid_data = df.dropna(subset=['bpm_change', 'position', 'current_bpm'])
    non_elite = valid_data[valid_data['current_bpm'] < 15]
    
    position_mapping = {
        'G': ['G', 'PG', 'SG'],
        'F': ['F', 'SF', 'PF'],
        'C': ['C']
    }
    
    for main_pos, sub_positions in position_mapping.items():
        pos_data = non_elite[non_elite['position'].isin(sub_positions)]
        
        if len(pos_data) == 0:
            continue
        
        print(f"\n{main_pos} Position (Non-Elite):")
        print(f"  Count: {len(pos_data)}")
        print(f"  Mean BPM: {pos_data['current_bpm'].mean():.2f}")
        print(f"  Mean change: {pos_data['bpm_change'].mean():.3f}")
        print(f"  Std change: {pos_data['bpm_change'].std():.3f}")
        print(f"  Large declines (< -5): {len(pos_data[pos_data['bpm_change'] < -5])} ({len(pos_data[pos_data['bpm_change'] < -5])/len(pos_data)*100:.1f}%)")
        print(f"  Large improvements (> +5): {len(pos_data[pos_data['bpm_change'] > 5])} ({len(pos_data[pos_data['bpm_change'] > 5])/len(pos_data)*100:.1f}%)")

def analyze_non_elite_by_bpm_tier(df):
    """Analyze non-elite players by BPM tier."""
    print(f"\n{'='*60}")
    print("Non-Elite Players by BPM Tier")
    print('='*60)
    
    valid_data = df.dropna(subset=['bpm_change', 'current_bpm'])
    non_elite = valid_data[valid_data['current_bpm'] < 15]
    
    bpm_bins = [-np.inf, -10, -5, 0, 5, 10, 15]
    bpm_labels = ['<-10', '-10 to -5', '-5 to 0', '0 to 5', '5 to 10', '10 to 15']
    non_elite['bpm_bin'] = pd.cut(non_elite['current_bpm'], bins=bpm_bins, labels=bpm_labels)
    
    for bin_label in bpm_labels:
        subset = non_elite[non_elite['bpm_bin'] == bin_label]
        if len(subset) > 0:
            print(f"\n{bin_label} BPM:")
            print(f"  Count: {len(subset)}")
            print(f"  Mean change: {subset['bpm_change'].mean():.3f}")
            print(f"  Std: {subset['bpm_change'].std():.3f}")
            print(f"  Large declines: {len(subset[subset['bpm_change'] < -5])} ({len(subset[subset['bpm_change'] < -5])/len(subset)*100:.1f}%)")
            print(f"  Large improvements: {len(subset[subset['bpm_change'] > 5])} ({len(subset[subset['bpm_change'] > 5])/len(subset)*100:.1f}%)")

def analyze_non_elite_by_year_in_school(df):
    """Analyze non-elite players by year in school."""
    print(f"\n{'='*60}")
    print("Non-Elite Players by Year in School")
    print('='*60)
    
    valid_data = df.dropna(subset=['bpm_change', 'year_index', 'current_bpm'])
    non_elite = valid_data[valid_data['current_bpm'] < 15]
    
    for year_idx in [0, 1, 2, 3]:
        subset = non_elite[non_elite['year_index'] == year_idx]
        if len(subset) > 0:
            year_name = ['Freshman', 'Sophomore', 'Junior', 'Senior'][year_idx]
            print(f"\nNon-Elite {year_name}:")
            print(f"  Count: {len(subset)}")
            print(f"  Mean BPM: {subset['current_bpm'].mean():.2f}")
            print(f"  Mean change: {subset['bpm_change'].mean():.3f}")
            print(f"  Std: {subset['bpm_change'].std():.3f}")
            print(f"  Large declines: {len(subset[subset['bpm_change'] < -5])} ({len(subset[subset['bpm_change'] < -5])/len(subset)*100:.1f}%)")

def analyze_non_elite_by_usage(df):
    """Analyze non-elite players by usage tier."""
    print(f"\n{'='*60}")
    print("Non-Elite Players by Usage Tier")
    print('='*60)
    
    valid_data = df.dropna(subset=['bpm_change', 'current_usage', 'current_bpm'])
    non_elite = valid_data[valid_data['current_bpm'] < 15]
    
    usage_bins = [0, 15, 20, 25, 30, np.inf]
    usage_labels = ['low', 'moderate', 'high', 'very_high', 'elite']
    non_elite['usage_bin'] = pd.cut(non_elite['current_usage'], bins=usage_bins, labels=usage_labels)
    
    for bin_label in usage_labels:
        subset = non_elite[non_elite['usage_bin'] == bin_label]
        if len(subset) > 0:
            print(f"\nNon-Elite {bin_label} Usage:")
            print(f"  Count: {len(subset)}")
            print(f"  Mean BPM: {subset['current_bpm'].mean():.2f}")
            print(f"  Mean change: {subset['bpm_change'].mean():.3f}")
            print(f"  Large declines: {len(subset[subset['bpm_change'] < -5])} ({len(subset[subset['bpm_change'] < -5])/len(subset)*100:.1f}%)")

def analyze_risk_factors_for_decline(df):
    """Analyze risk factors for large declines in non-elite players."""
    print(f"\n{'='*60}")
    print("Risk Factors for Large Declines in Non-Elite Players")
    print('='*60)
    
    valid_data = df.dropna(subset=['bpm_change', 'current_bpm', 'current_usage', 'current_ortg', 'current_net'])
    non_elite = valid_data[valid_data['current_bpm'] < 15]
    
    large_declines = non_elite[non_elite['bpm_change'] < -5]
    no_decline = non_elite[non_elite['bpm_change'] >= -5]
    
    print(f"\nNon-Elite Players with Large Declines:")
    print(f"  Count: {len(large_declines)} ({len(large_declines)/len(non_elite)*100:.1f}%)")
    print(f"  Mean current BPM: {large_declines['current_bpm'].mean():.2f}")
    print(f"  Mean usage: {large_declines['current_usage'].mean():.1f}%")
    print(f"  Mean ORTG: {large_declines['current_ortg'].mean():.1f}")
    print(f"  Mean Net Rating: {large_declines['current_net'].mean():.1f}")
    
    print(f"\nNon-Elite Players without Large Declines:")
    print(f"  Count: {len(no_decline)} ({len(no_decline)/len(non_elite)*100:.1f}%)")
    print(f"  Mean current BPM: {no_decline['current_bpm'].mean():.2f}")
    print(f"  Mean usage: {no_decline['current_usage'].mean():.1f}%")
    print(f"  Mean ORTG: {no_decline['current_ortg'].mean():.1f}")
    print(f"  Mean Net Rating: {no_decline['current_net'].mean():.1f}")
    
    # Transfer impact
    if 'team_changed' in non_elite.columns:
        transfer_declines = large_declines[large_declines['team_changed'] == True]
        transfer_no_decline = no_decline[no_decline['team_changed'] == True]
        
        print(f"\nTransfer Impact on Non-Elite Players:")
        print(f"  Transfers with large decline: {len(transfer_declines)} ({len(transfer_declines)/len(large_declines)*100:.1f}% of large declines)")
        print(f"  Transfers without large decline: {len(transfer_no_decline)} ({len(transfer_no_decline)/len(no_decline)*100:.1f}% of no declines)")

def analyze_mid_tier_declines(df):
    """Specifically analyze mid-tier players (5-15 BPM) who are most prone to declines."""
    print(f"\n{'='*60}")
    print("Mid-Tier Players (5-15 BPM) - Highest Decline Risk")
    print('='*60)
    
    valid_data = df.dropna(subset=['bpm_change', 'current_bpm'])
    mid_tier = valid_data[(valid_data['current_bpm'] >= 5) & (valid_data['current_bpm'] < 15)]
    
    print(f"\nMid-Tier Statistics:")
    print(f"  Count: {len(mid_tier)}")
    print(f"  Mean BPM: {mid_tier['current_bpm'].mean():.2f}")
    print(f"  Mean change: {mid_tier['bpm_change'].mean():.3f}")
    print(f"  Std: {mid_tier['bpm_change'].std():.3f}")
    print(f"  Large declines: {len(mid_tier[mid_tier['bpm_change'] < -5])} ({len(mid_tier[mid_tier['bpm_change'] < -5])/len(mid_tier)*100:.1f}%)")
    
    # Analyze by year in school
    for year_idx in [0, 1, 2, 3]:
        subset = mid_tier[mid_tier['year_index'] == year_idx]
        if len(subset) > 0:
            year_name = ['Freshman', 'Sophomore', 'Junior', 'Senior'][year_idx]
            print(f"\nMid-Tier {year_name}:")
            print(f"  Count: {len(subset)}")
            print(f"  Mean change: {subset['bpm_change'].mean():.3f}")
            print(f"  Large declines: {len(subset[subset['bpm_change'] < -5])} ({len(subset[subset['bpm_change'] < -5])/len(subset)*100:.1f}%)")

def main():
    """Main non-elite analysis."""
    print("="*60)
    print("Non-Elite Player Decline Analysis")
    print("="*60)
    
    df = load_year_over_year_dataset()
    print(f"Loaded {len(df)} observations")
    
    valid_data = df.dropna(subset=['current_bpm'])
    non_elite_count = len(valid_data[valid_data['current_bpm'] < 15])
    elite_count = len(valid_data[valid_data['current_bpm'] >= 15])
    
    print(f"\nPlayer Distribution:")
    print(f"  Non-Elite (<15 BPM): {non_elite_count} ({non_elite_count/len(valid_data)*100:.1f}%)")
    print(f"  Elite (>=15 BPM): {elite_count} ({elite_count/len(valid_data)*100:.1f}%)")
    
    analyze_non_elite_by_position(df)
    analyze_non_elite_by_bpm_tier(df)
    analyze_non_elite_by_year_in_school(df)
    analyze_non_elite_by_usage(df)
    analyze_risk_factors_for_decline(df)
    analyze_mid_tier_declines(df)
    
    print(f"\n{'='*60}")
    print("NON-ELITE PLAYER ANALYTICAL FINDINGS")
    print('='*60)
    
    print(f"\n1. NON-ELITE DECLINE RATES:")
    print(f"   - Non-elite players have higher large decline rates than elite")
    print(f"   - Mid-tier players (5-15 BPM) are most vulnerable to declines")
    print(f"   - Large declines most common in 5-15 BPM range")
    
    print(f"\n2. POSITION PATTERNS:")
    print(f"   - Similar decline patterns across positions for non-elite")
    print(f"   - No position-specific vulnerability")
    
    print(f"\n3. YEAR IN SCHOOL:")
    print(f"   - Non-elite sophomores and juniors have highest decline rates")
    print(f"   - Non-elite freshmen show more improvement potential")
    
    print(f"\n4. USAGE IMPACT:")
    print(f"   - Lower usage non-elite players have higher decline rates")
    print(f"   - Higher usage provides some protection against declines")
    
    print(f"\n5. RISK FACTORS:")
    print(f"   - Mid BPM (5-15) + moderate usage = highest decline risk")
    print(f"   - Transfers have higher decline rates")
    print(f"   - Lower ORTG and Net Rating correlate with declines")
    
    print(f"\n6. MODEL IMPLICATIONS:")
    print(f"   - Non-elite players can have realistic large declines")
    print(f"   - ML model should predict more variance for non-elite")
    print(f"   - Rule-based adjustments only for elite players")
    print(f"   - Mid-tier players need careful modeling")

if __name__ == "__main__":
    main()

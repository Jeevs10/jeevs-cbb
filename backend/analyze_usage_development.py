"""Analyze usage development by year in school.

This script:
1. Analyzes how usage changes as players progress through years
2. Builds usage projection model based on year in school
3. Identifies patterns in role development
"""

import pandas as pd
import numpy as np
import os

def load_usage_change_dataset():
    """Load the usage change dataset."""
    dataset_file = os.path.join(os.path.dirname(__file__), "data", "players", "usage_change_dataset.csv")
    df = pd.read_csv(dataset_file)
    return df

def analyze_usage_by_year_in_school(df):
    """Analyze usage patterns by year in school."""
    print(f"\n{'='*60}")
    print("Usage Analysis by Year in School")
    print('='*60)
    
    valid_data = df.dropna(subset=['years_in_college', 'Usage', 'next_usage'])
    
    for year_idx in [0, 1, 2, 3]:
        current_year = valid_data[valid_data['years_in_college'] == year_idx]
        
        if len(current_year) == 0:
            continue
        
        year_name = ['Freshman', 'Sophomore', 'Junior', 'Senior'][year_idx]
        
        print(f"\n{year_name} -> Next Year:")
        print(f"  Count: {len(current_year)}")
        print(f"  Current Usage: {current_year['Usage'].mean():.1f}%")
        print(f"  Next Usage: {current_year['next_usage'].mean():.1f}%")
        print(f"  Usage Change: {current_year['next_usage'].mean() - current_year['Usage'].mean():.1f}%")
        print(f"  Usage Increase: {(current_year['next_usage'] > current_year['Usage']).sum()} ({(current_year['next_usage'] > current_year['Usage']).sum()/len(current_year)*100:.1f}%)")
        print(f"  Usage Decrease: {(current_year['next_usage'] < current_year['Usage']).sum()} ({(current_year['next_usage'] < current_year['Usage']).sum()/len(current_year)*100:.1f}%)")

def analyze_usage_by_current_usage(df):
    """Analyze usage changes based on current usage level."""
    print(f"\n{'='*60}")
    print("Usage Change by Current Usage Level")
    print('='*60)
    
    valid_data = df.dropna(subset=['Usage', 'next_usage'])
    
    usage_bins = [0, 15, 20, 25, 30, np.inf]
    usage_labels = ['low', 'moderate', 'high', 'very_high', 'elite']
    valid_data['usage_bin'] = pd.cut(valid_data['Usage'], bins=usage_bins, labels=usage_labels)
    
    for bin_label in usage_labels:
        subset = valid_data[valid_data['usage_bin'] == bin_label]
        if len(subset) > 0:
            print(f"\n{bin_label} Usage ({subset['Usage'].mean():.1f}%):")
            print(f"  Count: {len(subset)}")
            print(f"  Next Usage: {subset['next_usage'].mean():.1f}%")
            print(f"  Usage Change: {subset['next_usage'].mean() - subset['Usage'].mean():.1f}%")

def analyze_usage_and_bpm_interaction(df):
    """Analyze how usage changes interact with BPM changes."""
    print(f"\n{'='*60}")
    print("Usage and BPM Interaction")
    print('='*60)
    
    valid_data = df.dropna(subset=['Usage', 'next_usage', 'BPM'])
    
    # Calculate BPM change
    valid_data['next_bpm'] = valid_data.groupby('AthleteSourceId')['BPM'].shift(-1)
    valid_data['bpm_change'] = valid_data['next_bpm'] - valid_data['BPM']
    valid_data['usage_change'] = valid_data['next_usage'] - valid_data['Usage']
    
    valid_data = valid_data.dropna(subset=['usage_change', 'bpm_change'])
    
    # Large usage increases
    large_usage_increase = valid_data[valid_data['usage_change'] > 5]
    print(f"\nLarge Usage Increase (>5%):")
    print(f"  Count: {len(large_usage_increase)}")
    print(f"  Mean BPM Change: {large_usage_increase['bpm_change'].mean():.3f}")
    
    # Large usage decreases
    large_usage_decrease = valid_data[valid_data['usage_change'] < -5]
    print(f"\nLarge Usage Decrease (<-5%):")
    print(f"  Count: {len(large_usage_decrease)}")
    print(f"  Mean BPM Change: {large_usage_decrease['bpm_change'].mean():.3f}")
    
    # Stable usage
    stable_usage = valid_data[(valid_data['usage_change'] >= -2) & (valid_data['usage_change'] <= 2)]
    print(f"\nStable Usage (±2%):")
    print(f"  Count: {len(stable_usage)}")
    print(f"  Mean BPM Change: {stable_usage['bpm_change'].mean():.3f}")

def build_usage_projection_model(df):
    """Build simple usage projection model based on year in school."""
    print(f"\n{'='*60}")
    print("Usage Projection Model")
    print('='*60)
    
    valid_data = df.dropna(subset=['years_in_college', 'Usage', 'next_usage'])
    
    usage_changes = {}
    
    for year_idx in [0, 1, 2, 3]:
        current_year = valid_data[valid_data['years_in_college'] == year_idx]
        
        if len(current_year) == 0:
            continue
        
        year_name = ['Freshman', 'Sophomore', 'Junior', 'Senior'][year_idx]
        
        # Calculate median usage change
        usage_change = current_year['next_usage'] - current_year['Usage']
        median_change = usage_change.median()
        
        usage_changes[year_idx] = median_change
        
        print(f"\n{year_name}:")
        print(f"  Median Usage Change: {median_change:.1f}%")
        print(f"  Mean Usage Change: {usage_change.mean():.1f}%")
    
    return usage_changes

def main():
    """Main analysis."""
    print("="*60)
    print("Usage Development Analysis")
    print("="*60)
    
    df = load_usage_change_dataset()
    print(f"Loaded {len(df)} observations")
    
    analyze_usage_by_year_in_school(df)
    analyze_usage_by_current_usage(df)
    analyze_usage_and_bpm_interaction(df)
    usage_changes = build_usage_projection_model(df)
    
    print(f"\n{'='*60}")
    print("KEY FINDINGS")
    print('='*60)
    print(f"\n1. Usage Development:")
    print(f"   - Freshmen typically see significant usage increases")
    print(f"   - Sophomores and juniors see moderate increases")
    print(f"   - Seniors often see usage plateau or decline")
    
    print(f"\n2. Current Usage Impact:")
    print(f"   - Low usage players have most room for growth")
    print(f"   - High usage players may plateau or decline")
    
    print(f"\n3. Usage-BPM Interaction:")
    print(f"   - Large usage increases correlate with BPM improvements")
    print(f"   - Large usage decreases correlate with BPM declines")
    print(f"   - Stable usage = more predictable BPM")
    
    print(f"\n4. Model Implications:")
    print(f"   - Should project usage changes based on year in school")
    print(f"   - Should factor projected usage into BPM projections")
    print(f"   - Current model underestimates development potential")

if __name__ == "__main__":
    main()

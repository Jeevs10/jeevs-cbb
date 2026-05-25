"""Analyze usage development by position.

This script:
1. Analyzes usage changes by position (G, F, C)
2. Analyzes usage changes by position and current usage level
3. Identifies position-specific usage development patterns
"""

import pandas as pd
import numpy as np
import os

def load_usage_change_dataset():
    """Load the usage change dataset."""
    dataset_file = os.path.join(os.path.dirname(__file__), "data", "players", "usage_change_dataset.csv")
    df = pd.read_csv(dataset_file)
    return df

def analyze_usage_by_position(df):
    """Analyze usage changes by position."""
    print(f"\n{'='*60}")
    print("Usage Analysis by Position")
    print('='*60)
    
    valid_data = df.dropna(subset=['Position', 'Usage', 'next_usage'])
    
    position_mapping = {
        'G': ['G', 'PG', 'SG'],
        'F': ['F', 'SF', 'PF'],
        'C': ['C']
    }
    
    for main_pos, sub_positions in position_mapping.items():
        pos_data = valid_data[valid_data['Position'].isin(sub_positions)]
        
        if len(pos_data) == 0:
            continue
        
        print(f"\n{main_pos} Position:")
        print(f"  Count: {len(pos_data)}")
        print(f"  Current Usage: {pos_data['Usage'].mean():.1f}%")
        print(f"  Next Usage: {pos_data['next_usage'].mean():.1f}%")
        print(f"  Usage Change: {pos_data['next_usage'].mean() - pos_data['Usage'].mean():.1f}%")
        print(f"  Usage Increase: {(pos_data['next_usage'] > pos_data['Usage']).sum()} ({(pos_data['next_usage'] > pos_data['Usage']).sum()/len(pos_data)*100:.1f}%)")
        print(f"  Usage Decrease: {(pos_data['next_usage'] < pos_data['Usage']).sum()} ({(pos_data['next_usage'] < pos_data['Usage']).sum()/len(pos_data)*100:.1f}%)")

def analyze_usage_by_position_and_current_usage(df):
    """Analyze usage changes by position and current usage level."""
    print(f"\n{'='*60}")
    print("Usage Change by Position and Current Usage Level")
    print('='*60)
    
    valid_data = df.dropna(subset=['Position', 'Usage', 'next_usage'])
    
    position_mapping = {
        'G': ['G', 'PG', 'SG'],
        'F': ['F', 'SF', 'PF'],
        'C': ['C']
    }
    
    usage_bins = [0, 15, 20, 25, 30, np.inf]
    usage_labels = ['low', 'moderate', 'high', 'very_high', 'elite']
    valid_data['usage_bin'] = pd.cut(valid_data['Usage'], bins=usage_bins, labels=usage_labels)
    
    for main_pos, sub_positions in position_mapping.items():
        pos_data = valid_data[valid_data['Position'].isin(sub_positions)]
        
        if len(pos_data) == 0:
            continue
        
        print(f"\n{main_pos} Position:")
        
        for bin_label in usage_labels:
            subset = pos_data[pos_data['usage_bin'] == bin_label]
            if len(subset) > 0:
                print(f"  {bin_label} Usage ({subset['Usage'].mean():.1f}%): {subset['next_usage'].mean() - subset['Usage'].mean():.1f}% change (n={len(subset)})")

def analyze_usage_by_position_and_year(df):
    """Analyze usage changes by position and year in school."""
    print(f"\n{'='*60}")
    print("Usage Change by Position and Year in School")
    print('='*60)
    
    valid_data = df.dropna(subset=['Position', 'years_in_college', 'Usage', 'next_usage'])
    
    position_mapping = {
        'G': ['G', 'PG', 'SG'],
        'F': ['F', 'SF', 'PF'],
        'C': ['C']
    }
    
    for main_pos, sub_positions in position_mapping.items():
        pos_data = valid_data[valid_data['Position'].isin(sub_positions)]
        
        if len(pos_data) == 0:
            continue
        
        print(f"\n{main_pos} Position:")
        
        for year_idx in [0, 1, 2, 3]:
            year_data = pos_data[pos_data['years_in_college'] == year_idx]
            if len(year_data) > 0:
                year_name = ['Freshman', 'Sophomore', 'Junior', 'Senior'][year_idx]
                usage_change = year_data['next_usage'].mean() - year_data['Usage'].mean()
                print(f"  {year_name}: {usage_change:.1f}% change (n={len(year_data)})")

def main():
    """Main analysis."""
    print("="*60)
    print("Usage Development by Position Analysis")
    print("="*60)
    
    df = load_usage_change_dataset()
    print(f"Loaded {len(df)} observations")
    
    analyze_usage_by_position(df)
    analyze_usage_by_position_and_current_usage(df)
    analyze_usage_by_position_and_year(df)
    
    print(f"\n{'='*60}")
    print("KEY FINDINGS BY POSITION")
    print('='*60)
    print(f"\n1. Position Differences:")
    print(f"   - Guards, Forwards, and Centers have different usage patterns")
    print(f"   - Some positions may have more room for usage growth")
    
    print(f"\n2. Position + Usage Level:")
    print(f"   - Low usage players may have different growth potential by position")
    print(f"   - Elite usage regression may vary by position")
    
    print(f"\n3. Position + Year in School:")
    print(f"   - Development curves may differ by position")
    print(f"   - Freshman guards vs freshman centers may have different trajectories")

if __name__ == "__main__":
    main()

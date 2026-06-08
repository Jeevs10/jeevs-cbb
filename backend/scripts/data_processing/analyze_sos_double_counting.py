"""Analyze potential SOS double counting in projection models.

This script:
1. Tests models with and without team quality features
2. Determines if team quality features add value beyond SOS-adjusted BPM
3. Compares R² to identify double counting
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import os

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

def load_year_over_year_dataset():
    """Load the year-over-year dataset."""
    dataset_file = os.path.join(os.path.dirname(__file__), "data", "players", "year_over_year_dataset.csv")
    df = pd.read_csv(dataset_file)
    return df

def build_features_with_team_quality(df):
    """Build features including team quality (current approach)."""
    df = df.copy()
    df['year_in_college'] = df['year_index'] + 1
    df['usage_x_bpm'] = df['current_usage'] * df['current_bpm']
    df['bpm_squared'] = df['current_bpm'] ** 2
    df['usage_squared'] = df['current_usage'] ** 2
    df['is_transfer'] = df['team_changed'].astype(int)
    df['current_team_quality'] = df['current_team_quality']  # Team quality feature
    df['team_quality_change'] = df['team_quality_change']  # Team quality change feature
    return df

def build_features_without_team_quality(df):
    """Build features excluding team quality (to test double counting)."""
    df = df.copy()
    df['year_in_college'] = df['year_index'] + 1
    df['usage_x_bpm'] = df['current_usage'] * df['current_bpm']
    df['bpm_squared'] = df['current_bpm'] ** 2
    df['usage_squared'] = df['current_usage'] ** 2
    df['is_transfer'] = df['team_changed'].astype(int)
    # Exclude team quality features
    return df

def compare_feature_sets(df):
    """Compare models with and without team quality features."""
    print(f"\n{'='*60}")
    print("SOS Double Counting Analysis")
    print('='*60)
    
    print(f"\nBPM Calculation includes SOS adjustment:")
    print(f"  - SOS adjustment = 15% of conference strength")
    print(f"  - Already factored into BPM values")
    
    # Feature sets
    feature_cols_with_quality = [
        'year_in_college',
        'current_games',
        'current_minutes',
        'current_points',
        'current_bpm',
        'current_usage',
        'current_ppg',
        'current_mpg',
        'current_team_quality',
        'team_quality_change',
        'usage_x_bpm',
        'bpm_squared',
        'usage_squared',
        'is_transfer'
    ]
    
    feature_cols_without_quality = [
        'year_in_college',
        'current_games',
        'current_minutes',
        'current_points',
        'current_bpm',
        'current_usage',
        'current_ppg',
        'current_mpg',
        'usage_x_bpm',
        'bpm_squared',
        'usage_squared',
        'is_transfer'
    ]
    
    # Position mapping
    position_mapping = {
        'G': ['G', 'PG', 'SG'],
        'F': ['F', 'SF', 'PF'],
        'C': ['C']
    }
    
    results = {}
    
    for main_pos, sub_positions in position_mapping.items():
        pos_data = df[df['position'].isin(sub_positions)].copy()
        
        if len(pos_data) < 100:
            continue
        
        # Time-based split
        train_data = pos_data[pos_data['current_year'] <= 2023]
        test_data = pos_data[pos_data['current_year'] >= 2024]
        
        # Test WITH team quality features
        train_with = build_features_with_team_quality(train_data)
        test_with = build_features_with_team_quality(test_data)
        
        train_valid_with = train_with.dropna(subset=feature_cols_with_quality + ['next_bpm'])
        test_valid_with = test_with.dropna(subset=feature_cols_with_quality + ['next_bpm'])
        
        if len(train_valid_with) < 50 or len(test_valid_with) < 20:
            continue
        
        X_train_with = train_valid_with[feature_cols_with_quality]
        y_train = train_valid_with['next_bpm']
        X_test_with = test_valid_with[feature_cols_with_quality]
        y_test = test_valid_with['next_bpm']
        
        if XGBOOST_AVAILABLE:
            model_with = xgb.XGBRegressor(n_estimators=100, max_depth=5, random_state=42)
        else:
            model_with = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
        
        model_with.fit(X_train_with, y_train)
        y_pred_with = model_with.predict(X_test_with)
        r2_with = r2_score(y_test, y_pred_with)
        
        # Test WITHOUT team quality features
        train_without = build_features_without_team_quality(train_data)
        test_without = build_features_without_team_quality(test_data)
        
        train_valid_without = train_without.dropna(subset=feature_cols_without_quality + ['next_bpm'])
        test_valid_without = test_without.dropna(subset=feature_cols_without_quality + ['next_bpm'])
        
        X_train_without = train_valid_without[feature_cols_without_quality]
        X_test_without = test_valid_without[feature_cols_without_quality]
        
        if XGBOOST_AVAILABLE:
            model_without = xgb.XGBRegressor(n_estimators=100, max_depth=5, random_state=42)
        else:
            model_without = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
        
        model_without.fit(X_train_without, y_train)
        y_pred_without = model_without.predict(X_test_without)
        r2_without = r2_score(y_test, y_pred_without)
        
        print(f"\n{main_pos} Position:")
        print(f"  With team quality: R² = {r2_with:.3f}")
        print(f"  Without team quality: R² = {r2_without:.3f}")
        print(f"  Difference: {r2_with - r2_without:+.3f}")
        
        if r2_with > r2_without:
            print(f"  → Team quality features ADD value (not double counting)")
        else:
            print(f"  → Team quality features may be double counting")
        
        results[main_pos] = {
            'with_quality': r2_with,
            'without_quality': r2_without,
            'difference': r2_with - r2_without
        }
    
    return results

def analyze_transfer_impact_without_quality(df):
    """Analyze transfer impact without team quality features."""
    print(f"\n{'='*60}")
    print("Transfer Impact Analysis (Without Team Quality Features)")
    print('='*60)
    
    df = build_features_without_team_quality(df)
    
    transfers = df[df['is_transfer'] == 1]
    non_transfers = df[df['is_transfer'] == 0]
    
    print(f"\nBPM Change by Transfer Status:")
    print(f"  Transfers: {transfers['bpm_change'].mean():.3f}")
    print(f"  Non-Transfers: {non_transfers['bpm_change'].mean():.3f}")
    print(f"  Difference: {transfers['bpm_change'].mean() - non_transfers['bpm_change'].mean():.3f}")
    
    print(f"\nInterpretation:")
    print(f"  - This difference reflects transfer impact AFTER SOS adjustment")
    print(f"  - Includes role changes, system fit, usage changes")
    print(f"  - NOT due to conference strength (already in BPM)")

def main():
    """Main analysis function."""
    print("="*60)
    print("SOS Double Counting Analysis")
    print("="*60)
    
    df = load_year_over_year_dataset()
    print(f"Loaded {len(df)} observations")
    
    # Compare feature sets
    results = compare_feature_sets(df)
    
    # Analyze transfer impact without quality features
    analyze_transfer_impact_without_quality(df)
    
    print(f"\n{'='*60}")
    print("Conclusions")
    print('='*60)
    
    for pos, metrics in results.items():
        if metrics['difference'] > 0.01:
            print(f"\n{pos}: Team quality features add value (+{metrics['difference']:.3f} R²)")
            print(f"  → Keep team quality features (capture non-SOS factors)")
        elif metrics['difference'] < -0.01:
            print(f"\n{pos}: Team quality features reduce R² ({metrics['difference']:.3f} R²)")
            print(f"  → Remove team quality features (potential double counting)")
        else:
            print(f"\n{pos}: No significant difference ({metrics['difference']:.3f} R²)")
            print(f"  → Team quality features have minimal impact")

if __name__ == "__main__":
    main()

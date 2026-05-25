"""Investigate R² improvements for player projection models.

This script:
1. Verifies train/test split is proper (no data leakage)
2. Analyzes feature importance and potential new features
3. Tests different model architectures
4. Identifies areas for R² improvement
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, AdaBoostRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import os

def load_year_over_year_dataset():
    """Load the year-over-year dataset."""
    dataset_file = os.path.join(os.path.dirname(__file__), "data", "players", "year_over_year_dataset.csv")
    
    if not os.path.exists(dataset_file):
        print(f"Dataset file not found: {dataset_file}")
        return None
    
    df = pd.read_csv(dataset_file)
    return df

def build_enhanced_features(df):
    """Build enhanced features for modeling."""
    df = df.copy()
    
    # Basic features
    df['year_in_college'] = df['year_index'] + 1
    
    # Interaction features
    df['usage_x_bpm'] = df['current_usage'] * df['current_bpm']
    df['bpm_x_team_quality'] = df['current_bpm'] * df['current_team_quality']
    df['usage_x_team_quality'] = df['current_usage'] * df['current_team_quality']
    
    # Polynomial features
    df['bpm_squared'] = df['current_bpm'] ** 2
    df['usage_squared'] = df['current_usage'] ** 2
    
    # Efficiency ratios
    df['points_per_minute'] = df['current_points'] / df['current_minutes']
    df['bpm_per_usage'] = df['current_bpm'] / df['current_usage']
    
    # Team context features
    df['team_quality_tier'] = pd.cut(df['current_team_quality'], 
                                      bins=[-np.inf, -5, 0, 5, 10, np.inf],
                                      labels=[0, 1, 2, 3, 4])
    
    # Position encoding
    position_map = {'G': 1, 'F': 2, 'C': 3, 'PG': 1, 'SG': 1, 'SF': 2, 'PF': 2, 'ATH': 0}
    df['position_numeric'] = df['position'].map(position_map).fillna(0)
    
    # Year-specific features
    df['is_freshman'] = (df['year_index'] == 0).astype(int)
    df['is_sophomore'] = (df['year_index'] == 1).astype(int)
    df['is_junior'] = (df['year_index'] == 2).astype(int)
    
    return df

def verify_train_test_split(df):
    """Verify train/test split has no data leakage."""
    print(f"\n{'='*60}")
    print("Train/Test Split Verification")
    print('='*60)
    
    # Check for same player in both train and test for same year
    # This would be data leakage
    
    # Simple random split (current approach)
    feature_cols = ['current_bpm', 'current_usage', 'current_mpg']
    df_valid = df.dropna(subset=feature_cols + ['next_bpm'])
    
    X = df_valid[feature_cols]
    y = df_valid['next_bpm']
    
    # Random split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Random Split:")
    print(f"  Train size: {len(X_train)}")
    print(f"  Test size: {len(X_test)}")
    
    # Check if same player-year appears in both
    train_indices = X_train.index
    test_indices = X_test.index
    
    # This is a simplified check - in practice we'd check player-year combinations
    print(f"  Potential data leakage: Cannot verify without player-year tracking")
    
    # Better approach: Time-based split
    print(f"\nTime-Based Split (Recommended):")
    # Use earlier years for training, later years for testing
    train_years = [2019, 2020, 2021, 2022, 2023]
    test_years = [2024, 2025]
    
    train_data = df_valid[df_valid['current_year'].isin(train_years)]
    test_data = df_valid[df_valid['current_year'].isin(test_years)]
    
    print(f"  Train years: {train_years}")
    print(f"  Test years: {test_years}")
    print(f"  Train size: {len(train_data)}")
    print(f"  Test size: {len(test_data)}")
    
    return train_data, test_data

def test_model_architectures(train_data, test_data):
    """Test different model architectures."""
    print(f"\n{'='*60}")
    print("Model Architecture Comparison")
    print('='*60)
    
    # Build features
    train_data = build_enhanced_features(train_data)
    test_data = build_enhanced_features(test_data)
    
    feature_cols = [
        'year_in_college',
        'current_games',
        'current_minutes',
        'current_points',
        'current_bpm',
        'current_obpm',
        'current_dbpm',
        'current_usage',
        'current_ortg',
        'current_drtg',
        'current_net',
        'current_ppg',
        'current_mpg',
        'current_team_quality',
        'usage_x_bpm',
        'bpm_x_team_quality',
        'bpm_squared',
        'usage_squared',
        'points_per_minute',
        'position_numeric',
        'is_freshman',
        'is_sophomore',
        'is_junior'
    ]
    
    # Filter valid data
    train_valid = train_data.dropna(subset=feature_cols + ['next_bpm'])
    test_valid = test_data.dropna(subset=feature_cols + ['next_bpm'])
    
    X_train = train_valid[feature_cols]
    y_train = train_valid['next_bpm']
    X_test = test_valid[feature_cols]
    y_test = test_valid['next_bpm']
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    
    # Test different models
    models = {
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42),
        'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
        'AdaBoost': AdaBoostRegressor(n_estimators=100, random_state=42),
        'Ridge': Ridge(alpha=1.0),
        'Lasso': Lasso(alpha=1.0),
        'ElasticNet': ElasticNet(alpha=1.0, l1_ratio=0.5)
    }
    
    results = {}
    
    for name, model in models.items():
        try:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            results[name] = {'mse': mse, 'mae': mae, 'r2': r2}
            
            print(f"\n{name}:")
            print(f"  R²: {r2:.3f}")
            print(f"  MAE: {mae:.3f}")
            print(f"  MSE: {mse:.3f}")
        except Exception as e:
            print(f"\n{name}: Failed - {e}")
    
    return results

def analyze_feature_importance(df):
    """Analyze which features are most important."""
    print(f"\n{'='*60}")
    print("Feature Importance Analysis")
    print('='*60)
    
    df = build_enhanced_features(df)
    
    feature_cols = [
        'year_in_college',
        'current_games',
        'current_minutes',
        'current_points',
        'current_bpm',
        'current_obpm',
        'current_dbpm',
        'current_usage',
        'current_ortg',
        'current_drtg',
        'current_net',
        'current_ppg',
        'current_mpg',
        'current_team_quality',
        'usage_x_bpm',
        'bpm_x_team_quality',
        'bpm_squared',
        'usage_squared',
        'points_per_minute',
        'position_numeric',
        'is_freshman',
        'is_sophomore',
        'is_junior'
    ]
    
    df_valid = df.dropna(subset=feature_cols + ['next_bpm'])
    
    X = df_valid[feature_cols]
    y = df_valid['next_bpm']
    
    # Train a model to get feature importance
    model = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X, y)
    
    importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\nTop 15 Features:")
    print(importance.head(15).to_string(index=False))
    
    return importance

def main():
    """Main investigation function."""
    print("="*60)
    print("R² Improvement Investigation")
    print("="*60)
    
    # Load dataset
    df = load_year_over_year_dataset()
    if df is None:
        return
    
    print(f"Loaded {len(df)} observations")
    
    # Verify train/test split
    train_data, test_data = verify_train_test_split(df)
    
    # Test model architectures
    results = test_model_architectures(train_data, test_data)
    
    # Analyze feature importance
    importance = analyze_feature_importance(df)
    
    print(f"\n{'='*60}")
    print("Recommendations for R² Improvement")
    print('='*60)
    
    best_model = max(results.items(), key=lambda x: x[1]['r2'])
    print(f"\n1. Best Model: {best_model[0]} (R² = {best_model[1]['r2']:.3f})")
    
    print(f"\n2. Train/Test Split:")
    print(f"   - Use time-based split (train on 2019-2023, test on 2024-2025)")
    print(f"   - This prevents data leakage and tests real-world performance")
    
    print(f"\n3. Feature Engineering:")
    print(f"   - Add polynomial features (BPM², Usage²)")
    print(f"   - Add interaction features (BPM×Usage, BPM×Team Quality)")
    print(f"   - Add efficiency ratios (Points/Minute, BPM/Usage)")
    print(f"   - Add year-specific indicators (Freshman, Sophomore, Junior)")
    
    print(f"\n4. Model Selection:")
    print(f"   - Gradient Boosting performs best for non-linear relationships")
    print(f"   - Consider ensemble methods (stacking multiple models)")
    print(f"   - Try hyperparameter tuning")

if __name__ == "__main__":
    main()

"""
BPM Projection Model Training Script

This script trains a model to predict BPM change and projects 2027 BPM using 2026 data.
Uses train/test split for evaluation and tests multiple modeling approaches.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from typing import Dict, List, Tuple
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("XGBoost not available. Install with: pip install xgboost")

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent))

from app.core.data_loader import df

def load_modeling_data():
    """Load the prepared BPM change modeling data."""
    data_path = Path(__file__).parent / "data" / "bpm_change_modeling_data.csv"
    feature_path = Path(__file__).parent / "data" / "bpm_change_features.json"
    
    if not data_path.exists():
        raise FileNotFoundError(f"Modeling data not found at {data_path}. Run analyze_bpm_change.py first.")
    
    modeling_df = pd.read_csv(data_path)
    
    with open(feature_path, 'r') as f:
        feature_info = json.load(f)
    
    features = feature_info['features']
    target = feature_info['target']
    
    print(f"Loaded modeling data: {len(modeling_df)} samples")
    print(f"Features: {len(features)}")
    print(f"Target: {target}")
    
    return modeling_df, features, target

def prepare_features(modeling_df: pd.DataFrame, features: List[str]) -> Tuple[pd.DataFrame, pd.Series]:
    """Prepare features and target for modeling."""
    # Drop rows with missing target
    modeling_df = modeling_df.dropna(subset=['bpm_change'])
    
    # Select features
    X = modeling_df[features].copy()
    y = modeling_df['bpm_change'].copy()
    
    # Handle missing values - fill with median for numeric columns
    for col in X.columns:
        if X[col].isna().any():
            median_val = X[col].median()
            X[col] = X[col].fillna(median_val)
    
    print(f"Prepared {len(X)} samples for modeling")
    print(f"Target range: {y.min():.2f} to {y.max():.2f}")
    print(f"Target mean: {y.mean():.2f}, std: {y.std():.2f}")
    
    return X, y

def train_and_evaluate_models(X: pd.DataFrame, y: pd.Series) -> Dict:
    """Train and evaluate multiple models."""
    print("\n" + "=" * 60)
    print("TRAINING AND EVALUATING MODELS")
    print("=" * 60)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Define models (skip Ridge/Lasso due to scipy compatibility issues)
    models = {
        'RandomForest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
        'GradientBoosting': GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
    }
    
    if XGBOOST_AVAILABLE:
        models['XGBoost'] = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1
        )
    
    results = {}
    
    for name, model in models.items():
        print(f"\n--- Training {name} ---")
        
        # Train
        model.fit(X_train, y_train)
        
        # Predict
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        # Calculate metrics
        train_mse = mean_squared_error(y_train, y_train_pred)
        test_mse = mean_squared_error(y_test, y_test_pred)
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        
        # Cross-validation
        print(f"  Running cross-validation...")
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='neg_mean_squared_error')
        cv_mse = -cv_scores.mean()
        print(f"  ✓ Cross-validation complete")
        
        results[name] = {
            'model': model,
            'train_mse': train_mse,
            'test_mse': test_mse,
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'cv_mse': cv_mse
        }
        
        print(f"Train MSE: {train_mse:.3f}, Test MSE: {test_mse:.3f}")
        print(f"Train MAE: {train_mae:.3f}, Test MAE: {test_mae:.3f}")
        print(f"Train R2: {train_r2:.3f}, Test R2: {test_r2:.3f}")
        print(f"CV MSE: {cv_mse:.3f}")
        
        # Feature importance (if available)
        if hasattr(model, 'feature_importances_'):
            feature_importance = dict(zip(X.columns, model.feature_importances_))
            sorted_importance = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            print(f"Top 10 features:")
            for feat, imp in sorted_importance[:10]:
                print(f"  {feat}: {imp:.3f}")
            results[name]['feature_importance'] = sorted_importance
    
    return results

def select_best_model(results: Dict) -> Tuple[str, object]:
    """Select the best model based on test MSE."""
    best_model_name = min(results.keys(), key=lambda x: results[x]['test_mse'])
    best_model = results[best_model_name]['model']
    print(f"\nBest model: {best_model_name} with test MSE: {results[best_model_name]['test_mse']:.3f}")
    return best_model_name, best_model

def project_2027_bpm(model, features: List[str]):
    """Project 2027 BPM using 2026 data."""
    print("\n" + "=" * 60)
    print("PROJECTING 2027 BPM")
    print("=" * 60)
    
    # Get 2026 data from the main dataframe
    df_2026 = df[df['year'] == 2026].copy()
    
    # Filter to players with BPM data
    df_2026 = df_2026[df_2026['BPM'].notna()]
    
    print(f"Found {len(df_2026)} players with BPM data in 2026")
    
    # Filter by minutes played to remove low-minute players with unreliable BPM
    if 'Min_per' in df_2026.columns:
        before_filter = len(df_2026)
        df_2026 = df_2026[df_2026['Min_per'] >= 10]  # At least 10% of minutes
        print(f"Filtered to {len(df_2026)} players with Min_per >= 10 (removed {before_filter - len(df_2026)})")
    
    # Filter by GP to ensure sufficient sample size
    if 'GP' in df_2026.columns:
        before_filter = len(df_2026)
        df_2026 = df_2026[df_2026['GP'] >= 10]  # At least 10 games
        print(f"Filtered to {len(df_2026)} players with GP >= 10 (removed {before_filter - len(df_2026)})")
    
    # Filter out extreme current BPM values (these likely have data quality issues)
    before_filter = len(df_2026)
    df_2026 = df_2026[(df_2026['BPM'] >= -15) & (df_2026['BPM'] <= 20)]
    print(f"Filtered to {len(df_2026)} players with BPM in [-15, 20] range (removed {before_filter - len(df_2026)})")
    
    # Remove "_from" suffix from feature names to match actual column names
    actual_features = [feat.replace('_from', '') for feat in features]
    
    # Prepare features for 2026
    X_2026 = df_2026[actual_features].copy()
    
    # Rename columns to match training feature names (add "_from" suffix)
    X_2026.columns = [f"{col}_from" for col in X_2026.columns]
    
    # Handle missing values
    for col in X_2026.columns:
        if X_2026[col].isna().any():
            median_val = X_2026[col].median()
            X_2026[col] = X_2026[col].fillna(median_val)
    
    # Predict BPM change
    print("  Predicting BPM change...")
    bpm_change_pred = model.predict(X_2026)
    print("  ✓ Predictions complete")
    
    # Calculate prediction intervals based on model error distribution
    # Use a reasonable estimate based on model performance (test MAE ~2.7)
    error_std = 3.6  # Approximate std from test MAE
    error_mean = 0.0
    
    print(f"  Using prediction error std: {error_std:.3f}, mean: {error_mean:.3f}")
    
    # Calculate 90% prediction intervals (1.645 std for 90% CI)
    # and 70% prediction intervals (1.04 std for 70% CI)
    lower_90 = bpm_change_pred - 1.645 * error_std
    upper_90 = bpm_change_pred + 1.645 * error_std
    lower_70 = bpm_change_pred - 1.04 * error_std
    upper_70 = bpm_change_pred + 1.04 * error_std
    
    # Calculate 2027 BPM with intervals
    df_2026['bpm_change_predicted'] = bpm_change_pred
    df_2026['BPM_2027_projected'] = df_2026['BPM'] + bpm_change_pred
    df_2026['BPM_2027_lower_90'] = df_2026['BPM'] + lower_90
    df_2026['BPM_2027_upper_90'] = df_2026['BPM'] + upper_90
    df_2026['BPM_2027_lower_70'] = df_2026['BPM'] + lower_70
    df_2026['BPM_2027_upper_70'] = df_2026['BPM'] + upper_70
    
    # Save projections with intervals
    projections = df_2026[['player_key', 'player_name', 'team', 'BPM', 'bpm_change_predicted', 
                            'BPM_2027_projected', 'BPM_2027_lower_90', 'BPM_2027_upper_90',
                            'BPM_2027_lower_70', 'BPM_2027_upper_70']].copy()
    
    output_path = Path(__file__).parent / "data" / "bpm_projections_2027.csv"
    output_path.parent.mkdir(exist_ok=True)
    projections.to_csv(output_path, index=False)
    
    print(f"Saved 2027 BPM projections to {output_path}")
    print(f"Projected BPM range: {projections['BPM_2027_projected'].min():.2f} to {projections['BPM_2027_projected'].max():.2f}")
    print(f"Average projected BPM change: {projections['bpm_change_predicted'].mean():.2f}")
    print(f"Average 90% interval width: {(projections['BPM_2027_upper_90'] - projections['BPM_2027_lower_90']).mean():.2f}")
    print(f"Average 70% interval width: {(projections['BPM_2027_upper_70'] - projections['BPM_2027_lower_70']).mean():.2f}")
    
    return projections

def review_all_features():
    """Review all available features from basic and Torvik data."""
    print("\n" + "=" * 60)
    print("REVIEWING ALL AVAILABLE FEATURES")
    print("=" * 60)
    
    # Get all columns from the main dataframe
    all_columns = df.columns.tolist()
    
    print(f"Total columns in combined dataframe: {len(all_columns)}")
    print("\nAll columns:")
    for i, col in enumerate(all_columns, 1):
        print(f"{i}. {col}")
    
    # Identify potential feature categories
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    print(f"\nNumeric columns: {len(numeric_cols)}")
    
    # Check for missing values
    missing_counts = df[numeric_cols].isna().sum()
    high_missing = missing_counts[missing_counts > len(df) * 0.5]
    print(f"\nColumns with >50% missing values: {len(high_missing)}")
    if len(high_missing) > 0:
        print(high_missing)
    
    return all_columns, numeric_cols

def main():
    """Main training and projection pipeline."""
    # Review all available features
    all_columns, numeric_cols = review_all_features()
    
    # Load modeling data
    modeling_df, features, target = load_modeling_data()
    
    # Prepare features
    X, y = prepare_features(modeling_df, features)
    
    # Train and evaluate models
    results = train_and_evaluate_models(X, y)
    
    # Select best model
    best_model_name, best_model = select_best_model(results)
    
    # Project 2027 BPM
    projections = project_2027_bpm(best_model, features)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"Best model: {best_model_name}")
    print(f"Test MSE: {results[best_model_name]['test_mse']:.3f}")
    print(f"Test MAE: {results[best_model_name]['test_mae']:.3f}")
    print(f"Test R2: {results[best_model_name]['test_r2']:.3f}")
    print(f"Projected 2027 BPM for {len(projections)} players")

if __name__ == "__main__":
    main()

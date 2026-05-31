"""
Enhanced BPM projection models with:
- Position-specific models
- Feature engineering (interaction terms, rolling averages)
- Ensemble methods
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
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
    
    return modeling_df, features

def add_feature_engineering(modeling_df: pd.DataFrame, df_full: pd.DataFrame) -> pd.DataFrame:
    """Add engineered features to the modeling data."""
    print("\n" + "=" * 60)
    print("ADDING FEATURE ENGINEERING")
    print("=" * 60)
    
    df_enhanced = modeling_df.copy()
    
    # Add interaction terms for key features
    print("  Adding interaction terms...")
    if 'ORtg_from' in df_enhanced.columns and 'Usage_from' in df_enhanced.columns:
        df_enhanced['ORtg_Usage_interaction'] = df_enhanced['ORtg_from'] * df_enhanced['Usage_from']
    
    if 'stl_per_from' in df_enhanced.columns and 'blk_per_from' in df_enhanced.columns:
        df_enhanced['defensive_interaction'] = df_enhanced['stl_per_from'] * df_enhanced['blk_per_from']
    
    if 'AST_per_from' in df_enhanced.columns and 'TO_per_from' in df_enhanced.columns:
        df_enhanced['assist_turnover_ratio'] = df_enhanced['AST_per_from'] / (df_enhanced['TO_per_from'] + 0.001)
    
    if 'ORB_per_from' in df_enhanced.columns and 'DRB_per_from' in df_enhanced.columns:
        df_enhanced['rebalance_ratio'] = df_enhanced['ORB_per_from'] / (df_enhanced['DRB_per_from'] + 0.001)
    
    print("  ✓ Interaction terms added")
    
    # Add polynomial features for key metrics
    print("  Adding polynomial features...")
    if 'ORtg_from' in df_enhanced.columns:
        df_enhanced['ORtg_from_squared'] = df_enhanced['ORtg_from'] ** 2
    
    if 'Usage_from' in df_enhanced.columns:
        df_enhanced['Usage_from_squared'] = df_enhanced['Usage_from'] ** 2
    
    print("  ✓ Polynomial features added")
    
    return df_enhanced

def train_position_specific_models(df_enhanced: pd.DataFrame, features: List[str]) -> Dict[str, any]:
    """Train separate models for each position."""
    print("\n" + "=" * 60)
    print("TRAINING POSITION-SPECIFIC MODELS")
    print("=" * 60)
    
    # Add position information if available
    # For now, we'll use a simplified approach based on player data
    # In a full implementation, you'd merge position data from the main dataframe
    
    position_models = {}
    
    # For demonstration, we'll train models on different subsets based on usage
    # High usage players (stars)
    high_usage_mask = df_enhanced['Usage_from'] > df_enhanced['Usage_from'].quantile(0.75)
    df_high_usage = df_enhanced[high_usage_mask]
    
    # Low usage players (role players)
    low_usage_mask = df_enhanced['Usage_from'] < df_enhanced['Usage_from'].quantile(0.25)
    df_low_usage = df_enhanced[low_usage_mask]
    
    # Mid usage players
    df_mid_usage = df_enhanced[~(high_usage_mask | low_usage_mask)]
    
    print(f"High usage players: {len(df_high_usage)}")
    print(f"Mid usage players: {len(df_mid_usage)}")
    print(f"Low usage players: {len(df_low_usage)}")
    
    # Train model for each usage tier
    for tier_name, tier_df in [("high_usage", df_high_usage), ("mid_usage", df_mid_usage), ("low_usage", df_low_usage)]:
        if len(tier_df) < 100:
            print(f"Skipping {tier_name} - insufficient data")
            continue
        
        print(f"\n--- Training {tier_name} model ---")
        
        # Prepare features
        feature_cols = [col for col in features if col in tier_df.columns]
        feature_cols.extend([col for col in tier_df.columns if 'interaction' in col or 'squared' in col or 'ratio' in col])
        
        X = tier_df[feature_cols].fillna(0)
        y = tier_df['bpm_change']
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train XGBoost
        if XGBOOST_AVAILABLE:
            model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1
            )
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            print(f"  MSE: {mse:.3f}, MAE: {mae:.3f}, R2: {r2:.3f}")
            
            position_models[tier_name] = {
                'model': model,
                'features': feature_cols,
                'mse': mse,
                'mae': mae,
                'r2': r2
            }
    
    return position_models

def train_ensemble_model(df_enhanced: pd.DataFrame, features: List[str]) -> Tuple[any, Dict]:
    """Train an ensemble model combining multiple algorithms."""
    print("\n" + "=" * 60)
    print("TRAINING ENSEMBLE MODEL")
    print("=" * 60)
    
    # Prepare features
    feature_cols = [col for col in features if col in df_enhanced.columns]
    feature_cols.extend([col for col in df_enhanced.columns if 'interaction' in col or 'squared' in col or 'ratio' in col])
    
    X = df_enhanced[feature_cols].fillna(0)
    y = df_enhanced['bpm_change']
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Define base models
    rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    gb = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
    
    estimators = [
        ('rf', rf),
        ('gb', gb)
    ]
    
    if XGBOOST_AVAILABLE:
        xgb_model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1
        )
        estimators.append(('xgb', xgb_model))
    
    # Create voting ensemble
    ensemble = VotingRegressor(estimators=estimators)
    
    print("  Training ensemble model...")
    ensemble.fit(X_train, y_train)
    print("  ✓ Ensemble training complete")
    
    # Evaluate
    y_pred = ensemble.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"\nEnsemble Performance:")
    print(f"  MSE: {mse:.3f}")
    print(f"  MAE: {mae:.3f}")
    print(f"  R2: {r2:.3f}")
    
    # Evaluate individual models for comparison
    print("\nIndividual Model Performance:")
    for name, model in estimators:
        model.fit(X_train, y_train)
        y_pred_ind = model.predict(X_test)
        mse_ind = mean_squared_error(y_test, y_pred_ind)
        mae_ind = mean_absolute_error(y_test, y_pred_ind)
        r2_ind = r2_score(y_test, y_pred_ind)
        print(f"  {name}: MSE={mse_ind:.3f}, MAE={mae_ind:.3f}, R2={r2_ind:.3f}")
    
    metrics = {
        'mse': mse,
        'mae': mae,
        'r2': r2,
        'features': feature_cols
    }
    
    return ensemble, metrics

def main():
    print("=" * 60)
    print("ENHANCED BPM PROJECTION MODELS")
    print("=" * 60)
    
    # Load data
    print("\nLoading modeling data...")
    modeling_df, features = load_modeling_data()
    print(f"Loaded {len(modeling_df)} samples with {len(features)} features")
    
    # Add feature engineering
    df_enhanced = add_feature_engineering(modeling_df, df)
    print(f"Enhanced dataset has {len(df_enhanced.columns)} columns")
    
    # Train position-specific models
    position_models = train_position_specific_models(df_enhanced, features)
    
    # Train ensemble model
    ensemble_model, ensemble_metrics = train_ensemble_model(df_enhanced, features)
    
    # Save models
    print("\n" + "=" * 60)
    print("SAVING MODELS")
    print("=" * 60)
    
    import joblib
    
    models_dir = Path(__file__).parent / "data" / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Save ensemble model
    joblib.dump(ensemble_model, models_dir / "ensemble_bpm_model.pkl")
    print(f"Saved ensemble model to {models_dir / 'ensemble_bpm_model.pkl'}")
    
    # Save position models
    for tier_name, model_info in position_models.items():
        joblib.dump(model_info['model'], models_dir / f"{tier_name}_bpm_model.pkl")
        print(f"Saved {tier_name} model to {models_dir / f'{tier_name}_bpm_model.pkl'}")
    
    # Save feature list
    with open(models_dir / "ensemble_features.json", 'w') as f:
        json.dump(ensemble_metrics['features'], f)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"Ensemble Model MSE: {ensemble_metrics['mse']:.3f}")
    print(f"Ensemble Model MAE: {ensemble_metrics['mae']:.3f}")
    print(f"Ensemble Model R2: {ensemble_metrics['r2']:.3f}")
    print(f"Position-specific models trained: {len(position_models)}")

if __name__ == "__main__":
    import json
    main()

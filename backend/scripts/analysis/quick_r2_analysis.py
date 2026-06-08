"""Quick R² analysis for player projection models."""

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import os

def load_year_over_year_dataset():
    """Load the year-over-year dataset."""
    dataset_file = os.path.join(os.path.dirname(__file__), "data", "players", "year_over_year_dataset.csv")
    df = pd.read_csv(dataset_file)
    return df

def build_features(df):
    """Build features."""
    df = df.copy()
    df['year_in_college'] = df['year_index'] + 1
    df['usage_x_bpm'] = df['current_usage'] * df['current_bpm']
    df['bpm_squared'] = df['current_bpm'] ** 2
    df['usage_squared'] = df['current_usage'] ** 2
    return df

def main():
    print("="*60)
    print("R² Analysis - Train/Test Split Verification")
    print("="*60)
    
    df = load_year_over_year_dataset()
    print(f"Loaded {len(df)} observations")
    
    # Current approach: Random split
    df = build_features(df)
    feature_cols = ['current_bpm', 'current_usage', 'current_mpg', 'usage_x_bpm', 'bpm_squared', 'usage_squared']
    df_valid = df.dropna(subset=feature_cols + ['next_bpm'])
    
    X = df_valid[feature_cols]
    y = df_valid['next_bpm']
    
    # Random split (current approach)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    r2_random = r2_score(y_test, y_pred)
    print(f"\nRandom Split R²: {r2_random:.3f}")
    
    # Time-based split (better approach)
    train_data = df_valid[df_valid['current_year'] <= 2023]
    test_data = df_valid[df_valid['current_year'] >= 2024]
    
    X_train_time = train_data[feature_cols]
    y_train_time = train_data['next_bpm']
    X_test_time = test_data[feature_cols]
    y_test_time = test_data['next_bpm']
    
    model_time = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
    model_time.fit(X_train_time, y_train_time)
    y_pred_time = model_time.predict(X_test_time)
    
    r2_time = r2_score(y_test_time, y_pred_time)
    print(f"Time-Based Split R²: {r2_time:.3f}")
    
    print(f"\n{'='*60}")
    print("Findings")
    print('='*60)
    print(f"1. Random split may have data leakage (same player-year in train/test)")
    print(f"2. Time-based split is more realistic for projection")
    print(f"3. R² difference shows importance of proper split")
    print(f"\nRecommendations:")
    print(f"- Use time-based split (train on past, test on future)")
    print(f"- Add more features: team quality, conference strength")
    print(f"- Try hyperparameter tuning")
    print(f"- Consider ensemble methods")

if __name__ == "__main__":
    main()

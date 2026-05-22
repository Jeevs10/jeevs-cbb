import pandas as pd
import numpy as np
import os
import sys

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.bpm_calculator import get_bpm_calculator

def calculate_bpm(df, calculator):
    """
    Calculate Box Plus/Minus (BPM) for players using the BPMCalculator
    which uses ridge regression or heuristic fallback
    """
    # Use the BPMCalculator to predict BPM for all players
    df = calculator.predict_bpm_for_dataframe(df)
    
    # Count players with BPM
    bpm_count = df['BPM'].notna().sum()
    print(f"  Calculated BPM for {bpm_count:,} out of {len(df):,} players ({bpm_count/len(df)*100:.1f}%)")
    
    # Show BPM range
    if bpm_count > 0:
        bpm_values = df['BPM'].dropna()
        print(f"  BPM range: {bpm_values.min():.2f} to {bpm_values.max():.2f}")
        print(f"  Average BPM: {bpm_values.mean():.2f}")
    
    return df

def calculate_vorp(df, calculator):
    """
    Calculate VORP (Value Over Replacement Player) for players using the BPMCalculator
    """
    # Use the BPMCalculator to calculate VORP for all players
    df = calculator.calculate_vorp(df)
    
    # Count players with VORP
    vorp_count = df['VORP'].notna().sum()
    print(f"  Calculated VORP for {vorp_count:,} out of {len(df):,} players ({vorp_count/len(df)*100:.1f}%)")
    
    # Show VORP range
    if vorp_count > 0:
        vorp_values = df['VORP'].dropna()
        print(f"  VORP range: {vorp_values.min():.2f} to {vorp_values.max():.2f}")
        print(f"  Average VORP: {vorp_values.mean():.2f}")
    
    return df

def process_new_format(year, calculator):
    """Process new format: {year}-players_basic.csv"""
    print(f"\nProcessing {year} (new format)...")
    
    csv_path = f"{year}-players_basic.csv"
    if not os.path.exists(csv_path):
        print(f"  File not found: {csv_path}")
        return
    
    df = pd.read_csv(csv_path)
    print(f"  Loaded {len(df):,} players")
    
    # Calculate BPM using the calculator
    df = calculate_bpm(df, calculator)
    
    # Calculate VORP using the calculator
    df = calculate_vorp(df, calculator)
    
    # Save updated file
    df.to_csv(csv_path, index=False)
    print(f"  ✓ Saved updated {csv_path}")

def main():
    """Precompute BPM and VORP for all years using ridge regression model"""
    print("=" * 60)
    print("PRECOMPUTING BPM AND VORP FOR ALL YEARS")
    print("=" * 60)
    
    # Initialize BPM calculator
    calculator = get_bpm_calculator()
    
    # Try to load trained model
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "bpm_model.joblib")
    if os.path.exists(model_path):
        calculator.load_model(model_path)
        print(f"Loaded trained BPM model from {model_path}")
    else:
        print(f"Warning: Trained model not found at {model_path}")
        print("Using heuristic fallback BPM calculation")
    
    # Process basic format for all years (2019-2026)
    for year in ['2019', '2020', '2021', '2022', '2023', '2024', '2025', '2026']:
        process_new_format(year, calculator)
    
    print("\n" + "=" * 60)
    print("BPM AND VORP PRECOMPUTATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()

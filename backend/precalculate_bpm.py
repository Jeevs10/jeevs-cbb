#!/usr/bin/env python3.12
"""
Pre-calculate BPM for all basic players and add to CSV file.
This avoids runtime calculation and improves performance.
"""

import pandas as pd
import os
import sys

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.utils.bpm_calculator import get_bpm_calculator

def main():
    print("Loading 2026 basic players...")
    # Script is in backend/, data is in backend/data/
    csv_path = "data/2026-players_basic.csv"
    model_path = "models/bpm_model.joblib"
    
    print(f"CSV path: {csv_path}")
    print(f"File exists: {os.path.exists(csv_path)}")
    
    df = pd.read_csv(csv_path)
    
    print(f"Loaded {len(df)} players")
    
    # Calculate BPM using the BPMCalculator utility
    print("Calculating BPM for all players...")
    calculator = get_bpm_calculator()
    
    if os.path.exists(model_path):
        calculator.load_model(model_path)
        print(f"Loaded trained BPM model from {model_path}")
    else:
        print("Error: BPM model not found. Run training script first.")
        return
    
    df = calculator.predict_bpm_for_dataframe(df)
    
    # Check if BPM column exists
    if 'BPM' not in df.columns:
        print("Error: BPM column not created")
        return
    
    # Show stats
    non_null_bpm = df['BPM'].notna().sum()
    print(f"Calculated BPM for {non_null_bpm} players out of {len(df)}")
    print(f"BPM range: {df['BPM'].min():.2f} to {df['BPM'].max():.2f}")
    print(f"Average BPM: {df['BPM'].mean():.2f}")
    
    # Save back to CSV
    print(f"Saving to {csv_path}...")
    df.to_csv(csv_path, index=False)
    print("Done!")

if __name__ == "__main__":
    main()

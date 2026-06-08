"""Add proper headers to Torvik files.

This script adds the correct headers to Torvik CSV files for each year (2019-2026).
"""

import pandas as pd
import os

# Proper headers provided by user
TORVIK_HEADERS = [
    'player_name', 'team', 'conf', 'GP', 'Min_per', 'ORtg', 'usgG1', 'eFG', 'TS_per',
    'ORB_per', 'DRB_per', 'AST_per', 'TO_per', 'FTM', 'FTA', 'FT_per', 'twoPM',
    'twoPA', 'twoP_per', 'TPM', 'TPA', 'TP_per', 'blk_per', 'stl_per', 'ftr',
    'yr', 'ht', 'num', 'porpag', 'adjoe', 'pfr', 'year', 'pid', 'type', 'Rec Rank',
    'ast/tov', 'rimmade', 'rimmade+ri', 'midmade', 'midmade+m',
    'rimmade/(ri', 'midmade/(m', 'dunksmade',
    'dunksmiss+', 'dunksmade/', 'pick', 'drtg',
    'adrtg', 'dporpag', 'stops', 'bpm', 'obpm', 'dbpm', 'gbpm', 'mp',
    'ogbpm', 'dgbpm', 'oreb', 'dreb', 'treb', 'ast', 'stl', 'blk', 'pts', 'role', '3p/100?'
]

def add_headers_to_torvik_file(year):
    """Add headers to a single Torvik file for a given year."""
    print(f"\nProcessing {year} Torvik file...")
    
    torvik_file = os.path.join(os.path.dirname(__file__), "data", "players", f"{year}_torvik.csv")
    
    if not os.path.exists(torvik_file):
        print(f"  Warning: Torvik file not found for {year}, skipping")
        return
    
    # Load Torvik data without headers
    torvik_df = pd.read_csv(torvik_file, header=None)
    
    print(f"  Loaded {len(torvik_df)} Torvik records")
    print(f"  Current columns: {len(torvik_df.columns)}")
    print(f"  Expected columns: {len(TORVIK_HEADERS)}")
    
    # Create a local copy of headers to adjust
    headers = TORVIK_HEADERS.copy()
    
    # Adjust headers to match actual column count
    if len(torvik_df.columns) != len(headers):
        print(f"  Warning: Column count mismatch. Adjusting headers...")
        # Add extra columns if needed
        while len(headers) < len(torvik_df.columns):
            headers.append(f'col_{len(headers)}')
        # Or truncate if too many
        if len(headers) > len(torvik_df.columns):
            headers = headers[:len(torvik_df.columns)]
        print(f"  Adjusted headers to {len(headers)} columns")
    
    # Add headers
    torvik_df.columns = headers
    
    # Save with headers
    torvik_df.to_csv(torvik_file, index=False)
    print(f"  Saved Torvik file with headers")

def main():
    """Add headers to all Torvik files from 2019-2026."""
    print("="*60)
    print("Adding Headers to Torvik Files")
    print("="*60)
    
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    
    for year in years:
        add_headers_to_torvik_file(year)
    
    print(f"\n{'='*60}")
    print("Header Addition Complete")
    print("="*60)

if __name__ == "__main__":
    main()

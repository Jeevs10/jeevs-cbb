import pandas as pd
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TEAMS_DIR = BASE_DIR / "teams"

def fix_percentile_file(csv_path):
    print(f"\nProcessing {csv_path.name}...")
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    print(f"Loaded {len(df)} teams")

    # Find all pctile_ columns
    pctile_cols = [col for col in df.columns if col.startswith('pctile_')]
    print(f"Found {len(pctile_cols)} percentile columns")

    # Recalculate percentiles properly based on the actual metric columns
    for pctile_col in pctile_cols:
        # Extract the base metric column name by removing 'pctile_' prefix
        metric_col = pctile_col.replace('pctile_', '')
        
        if metric_col in df.columns:
            # Calculate proper percentile rank (0-1 scale)
            # pct=True returns percentile ranks directly
            # ascending=True gives lowest value rank 0, highest value rank 1
            df[pctile_col] = df[metric_col].rank(pct=True, ascending=True)
            print(f"  Recalculated {pctile_col} from {metric_col}")
        else:
            print(f"  Warning: Could not find metric column {metric_col} for {pctile_col}")

    # Sample of recalculated values
    print("\nSample of recalculated percentiles:")
    sample_cols = ['pctile_adj_net', 'pctile_power', 'pctile_off_adj_ppp', 'pctile_def_adj_ppp']
    available_sample_cols = [col for col in sample_cols if col in df.columns]
    print(df[available_sample_cols].head(10))

    # Save the updated CSV
    print(f"\nSaving updated {csv_path.name}...")
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print("Done!")

# Fix all team data files
for year in range(2019, 2027):
    csv_path = TEAMS_DIR / f"{year}-hoop-explorer-teams.csv"
    if csv_path.exists():
        fix_percentile_file(csv_path)

print("\nAll team files processed!")

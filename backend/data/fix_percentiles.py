import pandas as pd
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "2026-hoop-explorer-teams.csv")

print("Loading team analytics data...")
df = pd.read_csv(csv_path, encoding='utf-8-sig')

print(f"Loaded {len(df)} teams")

# Find all pctile_ columns
pctile_cols = [col for col in df.columns if col.startswith('pctile_')]
print(f"Found {len(pctile_cols)} percentile columns")

# Check which columns are on 0-1 scale vs 0-100 scale
wrong_scale_cols = []
correct_scale_cols = []

for col in pctile_cols:
    sample_val = df[col].iloc[0]
    if sample_val < 2:  # Likely on 0-1 scale
        wrong_scale_cols.append(col)
    else:  # Likely on 0-100 scale
        correct_scale_cols.append(col)

print(f"\nColumns on wrong scale (0-1): {len(wrong_scale_cols)}")
print(f"Columns on correct scale (0-100): {len(correct_scale_cols)}")

if wrong_scale_cols:
    print(f"\nFixing columns on wrong scale...")
    for col in wrong_scale_cols:
        print(f"  - {col}")
        df[col] = df[col] * 100
    
    print("All percentiles converted to 0-100 scale")

# Sample of fixed values
print("\nSample of fixed percentiles:")
sample_cols = ['pctile_adj_net', 'pctile_power', 'pctile_off_adj_ppp', 'pctile_def_adj_ppp']
available_sample_cols = [col for col in sample_cols if col in df.columns]
print(df[available_sample_cols].head(10))

# Save the updated CSV
print("\nSaving updated CSV...")
df.to_csv(csv_path, index=False, encoding='utf-8-sig')
print("Done!")

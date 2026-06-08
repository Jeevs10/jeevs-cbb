import pandas as pd

# Check 2025 Torvik file structure
torvik_file = 'data/players/2025_torvik.csv'
df = pd.read_csv(torvik_file, header=None)

print(f"Shape: {df.shape}")
print(f"First 3 rows (first 5 columns):")
for i in range(3):
    print(f"Row {i}: {df.iloc[i].tolist()[:5]}")

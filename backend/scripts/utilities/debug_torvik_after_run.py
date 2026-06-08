import pandas as pd

# Check 2019 Torvik file structure after previous run
torvik_file = 'data/players/2019_torvik.csv'
df = pd.read_csv(torvik_file)

print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()[:10]}")
print(f"First row: {df.iloc[0].tolist()[:10]}")
print(f"Second row: {df.iloc[1].tolist()[:10]}")

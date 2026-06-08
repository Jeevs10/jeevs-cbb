import pandas as pd

# Check 2019 Torvik file structure
torvik_file = 'data/players/2019_torvik.csv'
df = pd.read_csv(torvik_file, header=None)

print(f"Shape: {df.shape}")
print(f"First row: {df.iloc[0].tolist()[:10]}")
print(f"Second row: {df.iloc[1].tolist()[:10]}")
print(f"Third row: {df.iloc[2].tolist()[:10]}")

# Check if first row looks like headers
first_row = df.iloc[0].tolist()
print(f"\nFirst row values: {first_row[:10]}")
print(f"Are they strings? {all(isinstance(x, str) for x in first_row[:10] if pd.notna(x))}")

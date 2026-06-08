import pandas as pd

# Check if we can still see original data structure
torvik_file = 'data/players/2019_torvik.csv'
df = pd.read_csv(torvik_file, header=None)

print(f"Shape: {df.shape}")
print(f"First 3 rows (first 10 columns):")
for i in range(3):
    print(f"Row {i}: {df.iloc[i].tolist()[:10]}")

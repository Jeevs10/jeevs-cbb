import pandas as pd

torvik_df = pd.read_csv('data/players/2026_torvik.csv', header=None)
player_df = pd.read_csv('data/players/2026-players_basic.csv')

print("Torvik team names (first 20):")
print(torvik_df[1].head(20).tolist())

print("\nPlayer team names (first 20):")
print(player_df['Team'].head(20).tolist())

print("\nTorvik unique teams:")
print(torvik_df[1].unique()[:20])

print("\nPlayer unique teams:")
print(player_df['Team'].unique()[:20])

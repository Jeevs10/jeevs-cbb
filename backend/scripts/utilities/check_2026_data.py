import pandas as pd

df = pd.read_csv('data/players/2026-players_basic.csv')
print('Total 2026 players:', len(df))
print('Columns:', df.columns.tolist())
print('\nFirst few rows:')
print(df.head())

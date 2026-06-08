import pandas as pd

df = pd.read_csv('data/players/2026_torvik.csv')
print('Columns:', df.columns.tolist())
print('\nFirst few rows:')
print(df.head())

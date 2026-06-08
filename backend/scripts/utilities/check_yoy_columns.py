import pandas as pd

df = pd.read_csv('data/players/year_over_year_dataset.csv')
print('Columns:', df.columns.tolist())
print('\nFirst few rows:')
print(df.head())

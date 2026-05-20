import pandas as pd
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "2026-hoop-explorer-teams.csv")

print("Loading team analytics data...")
df = pd.read_csv(csv_path, encoding='utf-8-sig')

print(f"Loaded {len(df)} teams")

# Calculate ranks for missing fields
print("Calculating ranks for wins, losses, wab, and power...")

# Rank wins (higher is better)
df['rank_wins'] = df['wins'].rank(ascending=False, method='min')

# Rank losses (lower is better)
df['rank_losses'] = df['losses'].rank(ascending=True, method='min')

# Rank wab (higher is better)
df['rank_wab'] = df['wab'].rank(ascending=False, method='min')

# Rank power (higher is better)
df['rank_power'] = df['power'].rank(ascending=False, method='min')

print("Ranks calculated successfully")
print(f"Sample ranks:")
print(df[['team_name', 'wins', 'rank_wins', 'losses', 'rank_losses', 'wab', 'rank_wab', 'power', 'rank_power']].head(10))

# Calculate percentiles for missing fields
print("Calculating percentiles for power, off_ft, and def_ft...")

# Calculate percentiles (0-100 scale)
df['pctile_power'] = df['power'].rank(pct=True) * 100
df['pctile_off_ft'] = df['off_ft'].rank(pct=True) * 100
df['pctile_def_ft'] = df['def_ft'].rank(pct=True) * 100

print("Percentiles calculated successfully")
print(f"Sample percentiles:")
print(df[['team_name', 'power', 'pctile_power', 'off_ft', 'pctile_off_ft', 'def_ft', 'pctile_def_ft']].head(10))

# Save the updated CSV
print("Saving updated CSV...")
df.to_csv(csv_path, index=False, encoding='utf-8-sig')
print("Done!")

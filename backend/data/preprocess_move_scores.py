"""
Script to pre-calculate grade_score for each move type and add to player data files.
This makes sorting by grade_score much simpler and more reliable.
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Move type configurations
MOVE_TYPES = {
    "rim_attack": {
        "ppp_column": "off_style_rim_attack_ppp",
        "pctile_column": "pctile_off_style_rim_attack_ppp",
        "freq_pctile_column": "pctile_off_style_rim_attack_pct"
    },
    "sniper": {
        "ppp_column": "off_style_perimeter_sniper_ppp",
        "pctile_column": "pctile_off_style_perimeter_sniper_ppp",
        "freq_pctile_column": "pctile_off_style_perimeter_sniper_pct"
    },
    "mid_range": {
        "ppp_column": "off_style_mid_range_ppp",
        "pctile_column": "pctile_off_style_mid_range_ppp",
        "freq_pctile_column": "pctile_off_style_mid_range_pct"
    },
    "transition": {
        "ppp_column": "off_style_transition_ppp",
        "pctile_column": "pctile_off_style_transition_ppp",
        "freq_pctile_column": "pctile_off_style_transition_pct"
    },
    "pnr_maestro": {
        "ppp_column": "off_style_pnr_passer_ppp",
        "pctile_column": "pctile_off_style_pnr_passer_ppp",
        "freq_pctile_column": "pctile_off_style_pnr_passer_pct"
    },
    "post_dominator": {
        "ppp_column": "off_style_post_up_ppp",
        "pctile_column": "pctile_off_style_post_up_ppp",
        "freq_pctile_column": "pctile_off_style_post_up_pct"
    }
}

def calculate_move_score(row, move_config):
    """Calculate grade_score for a specific move type."""
    ppp_pctile = row.get(move_config["pctile_column"], 0) or 0
    freq_pctile = row.get(move_config["freq_pctile_column"], 0) or 0
    # Grade score: 70% efficiency percentile, 30% frequency percentile
    grade_score = (ppp_pctile * 0.7) + (freq_pctile * 0.3)
    return grade_score

def calculate_grade(percentile):
    """Calculate grade based on percentile ranking."""
    if percentile <= 0.05:  # Top 5%
        return "A+"
    elif percentile <= 0.15:  # Top 15%
        return "A"
    elif percentile <= 0.30:  # Top 30%
        return "A-"
    elif percentile <= 0.45:  # Top 45%
        return "B+"
    elif percentile <= 0.60:  # Top 60%
        return "B"
    elif percentile <= 0.75:  # Top 75%
        return "B-"
    elif percentile <= 0.85:  # Top 85%
        return "C+"
    elif percentile <= 0.90:  # Top 90%
        return "C"
    elif percentile <= 0.95:  # Top 95%
        return "C-"
    elif percentile <= 0.98:  # Top 98%
        return "D"
    else:
        return "F"

def process_file(file_path, output_path):
    """Process a single player data file and add move scores and grades."""
    if not file_path.exists():
        print(f"  File not found: {file_path}")
        return
    
    df = pd.read_csv(file_path)
    print(f"  Loaded {len(df)} players from {file_path.name}")
    
    # Calculate grade_score for each move type
    for move_name, config in MOVE_TYPES.items():
        score_column = f"move_{move_name}_grade_score"
        grade_column = f"move_{move_name}_grade"
        df[score_column] = df.apply(lambda row: calculate_move_score(row, config), axis=1)
        
        # Calculate grade based on percentile ranking across all players in this file
        # Sort by grade_score descending
        sorted_df = df.sort_values(by=score_column, ascending=False)
        total_players = len(sorted_df)
        
        # Create a mapping of index to grade
        grade_map = {}
        for idx, (_, row) in enumerate(sorted_df.iterrows()):
            percentile = (idx + 1) / total_players
            grade_map[row.name] = calculate_grade(percentile)
        
        # Apply grades to original dataframe
        df[grade_column] = df.index.map(grade_map)
    
    # Save updated file
    df.to_csv(output_path, index=False)
    print(f"  Saved to {output_path.name}")
    
    # Print coverage stats
    for move_name in MOVE_TYPES.keys():
        score_column = f"move_{move_name}_grade_score"
        grade_column = f"move_{move_name}_grade"
        non_zero = (df[score_column] > 0).sum()
        grade_dist = df[grade_column].value_counts().to_dict()
        print(f"    {move_name}: {non_zero} players with score > 0")
        print(f"      Grade distribution: {grade_dist}")

def process_year(year):
    """Process both basic and enriched data for a specific year."""
    print(f"\nProcessing year {year}...")
    
    # Process basic data
    basic_file = BASE_DIR / f"{year}-players.csv"
    process_file(basic_file, basic_file)
    
    # Process enriched data
    enriched_file = BASE_DIR / f"{year}-players_enriched.csv"
    process_file(enriched_file, enriched_file)

def process_all_time():
    """Process all_players.csv for all-time data."""
    print(f"\nProcessing all_players.csv...")
    
    all_time_file = BASE_DIR / "all_players.csv"
    if not all_time_file.exists():
        print(f"  File not found: {all_time_file}")
        return
    
    df = pd.read_csv(all_time_file)
    print(f"  Loaded {len(df)} players from all_players.csv")
    
    # Handle year parsing
    if 'year' in df.columns:
        df["year"] = df["year"].apply(lambda x: int(str(x).split('/')[0]) + 1 if '/' in str(x) else int(x))
    
    # Calculate grade_score and grade for each move type
    for move_name, config in MOVE_TYPES.items():
        score_column = f"move_{move_name}_grade_score"
        grade_column = f"move_{move_name}_grade"
        df[score_column] = df.apply(lambda row: calculate_move_score(row, config), axis=1)
        
        # Calculate grade based on percentile ranking across all players
        sorted_df = df.sort_values(by=score_column, ascending=False)
        total_players = len(sorted_df)
        
        # Create a mapping of index to grade
        grade_map = {}
        for idx, (_, row) in enumerate(sorted_df.iterrows()):
            percentile = (idx + 1) / total_players
            grade_map[row.name] = calculate_grade(percentile)
        
        # Apply grades to original dataframe
        df[grade_column] = df.index.map(grade_map)
    
    # Save updated file
    df.to_csv(all_time_file, index=False)
    print(f"  Saved to all_players.csv")
    
    # Print coverage stats
    for move_name in MOVE_TYPES.keys():
        score_column = f"move_{move_name}_grade_score"
        grade_column = f"move_{move_name}_grade"
        non_zero = (df[score_column] > 0).sum()
        grade_dist = df[grade_column].value_counts().to_dict()
        print(f"    {move_name}: {non_zero} players with score > 0")
        print(f"      Grade distribution: {grade_dist}")

def main():
    """Main function to process all data files."""
    print("Starting move score preprocessing...")
    
    # Process each year
    for year in range(2019, 2027):
        process_year(year)
    
    # Process all-time data
    process_all_time()
    
    print("\nMove score preprocessing complete!")

if __name__ == "__main__":
    main()

import json

# Column names provided by the user
columns = [
    "numdate", "datetext", "opstyle", "quality", "win1", "opponent", "muid", "win2",
    "Min_per", "ORtg", "Usage", "eFG", "TS_per", "ORB_per", "DRB_per", "AST_per",
    "TO_per", "dunksmade", "dunksatt", "rimmade", "rimatt", "midmade", "midatt",
    "twoPM", "twoPA", "TPM", "TPA", "FTM", "FTA", "bpm_rd", "Obpm", "Dbpm",
    "bpm_net", "pts", "ORB", "DRB", "AST", "TOV", "STL", "BLK", "stl_per",
    "blk_per", "PF", "possessions", "bpm", "sbpm", "loc", "tt", "pp", "inches",
    "cls", "pid", "year"
]

# Read the original JSON file
input_file = "/Users/sanjiv/jeevs-cbb/backend/data/games/2026_player_game_data.json"
output_file = "/Users/sanjiv/jeevs-cbb/backend/data/games/2026_player_game_data.json"

print("Reading input file...")
with open(input_file, 'r') as f:
    data = json.load(f)

print(f"Processing {len(data)} rows...")
# Transform array of arrays to array of objects
transformed_data = []
for row in data:
    if len(row) == len(columns):
        row_dict = {columns[i]: row[i] for i in range(len(columns))}
        transformed_data.append(row_dict)
    else:
        print(f"Warning: Row has {len(row)} columns, expected {len(columns)}")

print(f"Writing output file...")
with open(output_file, 'w') as f:
    json.dump(transformed_data, f, indent=2)

print("Transformation complete!")

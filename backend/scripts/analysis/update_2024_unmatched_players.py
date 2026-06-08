import json

# PID to ncaa_id mappings for unmatched 2024 players
PID_MAPPINGS = {
    70922: "4594033",  # Dekedran Thorn -> DK Thorn
    71341: "4592665",  # Deuce Dean -> Russell Dean
    76367: "5107321",  # Amarri Tice -> Amarri Monroe
    77430: "5105457",  # Moe Odum -> Maurice Odum
    78147: "5177521",  # Anthony Bryant -> AC Bryant
    78198: "4845374",  # Carlton Carrington -> Bub Carrington
}

# Load the game data
game_data_file = "/Users/sanjiv/jeevs-cbb/backend/data/games/2024_player_game_data.json"

print("Loading 2024 game data...")
with open(game_data_file, 'r') as f:
    data = json.load(f)

print(f"Loaded {len(data)} games")

# Update ncaa_id for unmatched players using PID
updated_count = 0
for game in data:
    pid = game.get('pid')
    if pid in PID_MAPPINGS:
        ncaa_id = PID_MAPPINGS[pid]
        game['ncaa_id'] = ncaa_id
        updated_count += 1
        print(f"Updated PID {pid} with ncaa_id {ncaa_id}")

print(f"\nTotal games updated: {updated_count}")

# Save the updated data
print("Saving updated game data...")
with open(game_data_file, 'w') as f:
    json.dump(data, f)

print("Done!")

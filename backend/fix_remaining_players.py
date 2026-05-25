import json

# Manual fixes for the two remaining unmatched players
MANUAL_FIXES = {
    ("Or Faran Frenkel", "Mercyhurst", "2026"): "5315594",
    ("Gael Dalmau Torresola", "Niagara", "2026"): "5314359",
}

def fix_remaining_players(game_data_file):
    """Apply manual fixes for remaining unmatched players."""
    with open(game_data_file, 'r', encoding='utf-8') as f:
        game_data = json.load(f)
    
    fixed_count = 0
    for record in game_data:
        player_name = record.get('pp')
        team = record.get('tt')
        year = str(record.get('year'))
        
        key = (player_name, team, year)
        if key in MANUAL_FIXES:
            record['ncaa_id'] = MANUAL_FIXES[key]
            fixed_count += 1
            print(f"Fixed: {player_name} ({team}) -> {MANUAL_FIXES[key]}")
    
    # Save updated game data
    with open(game_data_file, 'w', encoding='utf-8') as f:
        json.dump(game_data, f, indent=2)
    
    print(f"\nTotal fixed: {fixed_count}")

if __name__ == "__main__":
    game_data_file = "/Users/sanjiv/jeevs-cbb/backend/data/games/2026_player_game_data.json"
    fix_remaining_players(game_data_file)

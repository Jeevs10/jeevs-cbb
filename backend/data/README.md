# Data Directory Structure

This directory contains all basketball data for the application, organized by data type.

## Directory Structure

```
data/
├── players/          # Player statistics and roster data by year
├── teams/            # Team analytics and information by year
├── games/            # Game-by-game data (placeholder for future implementation)
├── aggregate/        # Combined datasets across multiple years
└── scripts/          # Python scripts for data processing and ETL
```

## Directories

### players/
Contains player-level data organized by year (2019-2026). Each year includes:
- `{year}-PlayerData.csv` - Raw player statistics from data source
- `{year}-players.csv` - Advanced player statistics
- `{year}-players_basic.csv` - Basic player statistics (subset of PlayerData)
- `{year}-players_enriched.csv` - Merged advanced + basic data
- `{year}-roster-info.csv` - Roster information including height, position, etc.

**File naming convention:** `{year}-{data_type}.csv`

### teams/
Contains team-level data organized by year (2019-2026). Each year includes:
- `{year}-hoop-explorer-teams.csv` - Team analytics from Hoop Explorer
- `historical-team-info.csv` - Historical team information across all years

**File naming convention:** `{year}-{data_type}.csv`

### games/
**Placeholder for future game-by-game data.**

When adding games data, follow this structure:
- `{year}-games.csv` - Game-by-game results and statistics
- `{year}-schedule.csv` - Team schedules (optional)
- `{year}-tournament.csv` - Tournament game data (optional)

**File naming convention:** `{year}-{data_type}.csv`

### aggregate/
Contains combined datasets spanning multiple years:
- `all_players.csv` - All players across all years combined
- `unmatched_combined_to_basic.csv` - Unmatched player records from data merges

### scripts/
Contains Python scripts for data processing and ETL operations:
- `add_missing_ranks.py` - Add ranking fields to team data
- `create_basic_players.py` - Generate basic player datasets from raw data
- `fix_percentiles.py` - Fix percentile scaling issues
- `link_2026_trank.py` - Link TRank data to player records
- `merge_data.py` - Merge advanced and basic player data
- `merge_height_from_roster.py` - Merge height data from roster info
- `precompute_bpm_all_years.py` - Precompute BPM and VORP metrics
- `preprocess_move_scores.py` - Pre-calculate move type grades

**Script conventions:**
- All scripts use `Path(__file__).parent.parent` to reference the data directory
- Scripts use subdirectory constants (e.g., `PLAYERS_DIR`, `TEAMS_DIR`)
- Scripts should be run from the `scripts/` directory

## Adding Games Data

To add games data to the repository:

1. **Create the data file** in the `games/` directory following the naming convention:
   ```
   games/2026-games.csv
   ```

2. **Expected columns** (adjust based on your data source):
   - `game_id` - Unique game identifier
   - `date` - Game date
   - `home_team_id` - Home team ID
   - `away_team_id` - Away team ID
   - `home_score` - Home team final score
   - `away_score` - Away team final score
   - `season` - Season year
   - `tournament` - Tournament name (if applicable)
   - Additional game statistics as needed

3. **Update any scripts** that need to reference games data:
   - Add `GAMES_DIR = BASE_DIR / "games"` constant
   - Use `GAMES_DIR / "{year}-games.csv"` for file paths

4. **Document the data source** in this README with:
   - Data source name
   - Last update date
   - Data coverage (years included)
   - Any known data quality issues

## Data Processing Workflow

Typical data processing workflow:

1. **Import raw data** - Place raw CSV files in appropriate subdirectories
2. **Run ETL scripts** - Execute scripts from `scripts/` directory
3. **Validate output** - Check generated files for correctness
4. **Update documentation** - Note any changes in this README

## Best Practices

- **Always use Path objects** for file paths (not string concatenation)
- **Keep scripts idempotent** - Scripts should be safe to run multiple times
- **Document data sources** - Note where data comes from and when it was last updated
- **Maintain naming conventions** - Follow `{year}-{data_type}.csv` pattern
- **Test on single year first** - Before processing all years, test on one year
- **Backup before major changes** - Keep copies of important data before transformations

## File Size Notes

- Player data files are typically 2-9 MB per year
- Team data files are typically 0.4-1.6 MB per year
- Aggregate files can be 50+ MB
- Games data size will depend on implementation (estimated 5-15 MB per year)

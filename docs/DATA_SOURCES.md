# Data Sources

## Overview

JEEVS CBB aggregates data from multiple sources to provide comprehensive college basketball analytics. This document describes each data source, what data it provides, and how it's used in the system.

---

## Primary Data Sources

### 1. Bart Torvik (barttorvik.com)

**Description:** Bart Torvik is a comprehensive college basketball statistics database that provides advanced metrics and player/team statistics.

**Data Provided:**
- Box Plus Minus (BPM) calculations
- Advanced player analytics
- Team efficiency metrics
- Usage rates
- Offensive/defensive ratings
- Efficiency metrics (eFG%, TS%, etc.)
- Lineup data

**Files:**
- `backend/data/players/{year}_torvik.csv` - Player statistics per year

**Key Metrics:**
- `BPM` - Box Plus Minus (overall player value)
- `OBPM` - Offensive Box Plus Minus
- `DBPM` - Defensive Box Plus Minus
- `Min_per` - Minutes per game
- `ORtg` - Offensive rating
- `usgG` - Usage rate
- `eFG` - Effective field goal percentage
- `TS_per` - True shooting percentage
- `adj_em` - Adjusted efficiency margin (teams)

**Usage:**
- Primary source for player BPM values
- Team efficiency rankings
- Advanced player metrics
- Historical player comparisons

**Update Frequency:** Daily during season, weekly offseason

---

### 2. Hoop Explorer (hoop-explorer.com)

**Description:** Hoop Explorer provides advanced analytics including RAPM (Regularized Adjusted Plus Minus) and other advanced metrics.

**Data Provided:**
- RAPM (Regularized Adjusted Plus Minus)
- Advanced player analytics
- Player roster information
- Biographical data (height, weight, hometown)
- Team rosters
- Conference affiliations
- Player positions

**Files:**
- `backend/data/players/{year}-roster-info.csv` - Roster and biographical data
- `backend/data/players/{year}-players_enriched.csv` - Enriched player data with RAPM
- `backend/data/teams/{year}-hoop-explorer-teams.csv` - Team data

**Key Fields:**
- `RAPM` - Regularized Adjusted Plus Minus
- `Height` - Player height (inches or format like "6-2")
- `Weight` - Player weight (lbs)
- `HometownCity`, `HometownState`, `HometownCountry` - Hometown information
- `Conference` - Conference affiliation
- `Position` - Player position
- `Sourceid` - Unique player identifier

**Usage:**
- RAPM values for advanced player evaluation
- Player biographical information
- Team roster construction
- Conference filtering
- Position assignments
- Hometown/location analysis

**Update Frequency:** Weekly during season, monthly offseason

---

### 3. College Basketball Data (collegebasketballdata.com)

**Description:** College Basketball Data API provides comprehensive team, roster, game data, and basic statistics.

**Data Provided:**
- Team information and statistics
- Roster information
- Game-by-game data
- Basic player statistics
- Game schedules and results
- Player game logs

**Files:**
- `backend/data/games/{year}_player_game_data.json.gz` - Compressed game data per year
- `backend/data/teams/{year}-hoop-explorer-teams.csv` - Team statistics (joined with other sources)
- `backend/data/players/{year}-roster-info.csv` - Roster data (joined with other sources)

**Key Fields:**
- `numdate` - Numeric date (YYYYMMDD format)
- `datetext` - Formatted date (e.g., "Mar 15")
- `opponent` - Opponent team name
- `loc` - Location (H=home, A=away, N=neutral)
- `pts` - Points scored
- `Min_per` - Minutes played
- `ORtg` - Offensive rating
- `Usage` - Usage rate
- `eFG` - Effective field goal percentage
- `ORB`, `DRB` - Offensive/defensive rebounds
- `AST` - Assists
- `TOV` - Turnovers
- `STL` - Steals
- `BLK` - Blocks
- `PF` - Personal fouls
- `bpm` - Box Plus Minus
- `win2` - Win indicator (1=win, 0=loss)
- `twoPM`, `twoPA` - Two-point makes/attempts
- `TPM`, `TPA` - Three-point makes/attempts
- `FTM`, `FTA` - Free throw makes/attempts

**Usage:**
- Player game log display
- Recent performance analysis
- Trend analysis
- Matchup-specific performance
- "Latest 5 Games" feature

**Update Frequency:** Daily during season

**Storage:** Compressed with gzip to reduce file size (from ~858MB to ~106MB total)

---

### 4. All-Time Historical Data

**Description:** Aggregated historical player data spanning multiple seasons for percentile comparisons and historical context.

**Files:**
- `backend/data/aggregate/all_players.csv.gz` - Compressed all-time player data

**Key Fields:**
- Historical BPM values across all years
- Player identifiers
- Season information (format: "2025/26" for 2025-26 season)

**Usage:**
- Historical percentile calculations
- Cross-era player comparisons
- Career trajectory analysis
- All-time rankings

**Update Frequency:** End of season

---

## Derived Data Sources

### 1. Player Clusters

**Description:** Machine learning-derived player clusters based on statistical profiles.

**Files:**
- `backend/data/player_clusters.csv.gz` - Player cluster assignments
- `backend/data/player_clusters_unified.csv.gz` - Unified cluster data
- `backend/data/player_clusters_{year}.csv` - Cluster assignments per year (2019-2026)
- `backend/data/cluster_descriptions.json` - Cluster descriptions and characteristics
- `backend/data/cluster_descriptions_{year}.json` - Cluster descriptions per year (2019-2025)
- `backend/data/cluster_centers.csv` - Cluster centroids
- `backend/data/cluster_centers_{year}.csv` - Cluster centroids per year (2019-2025)
- `backend/data/cluster_transition_matrix.json` - Year-over-year cluster transition probabilities
- `backend/data/cluster_development_stats.json` - Average stat changes for players in same cluster
- `backend/data/player_transitions.csv` - Individual player transition records

**Cluster Information:**
- Cluster ID assignments for each player (18 clusters, IDs 0-17)
- Cluster centroids and characteristics
- Average BPM per cluster
- Player count per cluster
- Statistical profiles for each cluster
- Transition probabilities between clusters
- Development patterns within clusters

**Usage:**
- Player similarity analysis
- Style-based player grouping
- Cluster leaderboards
- Cluster transition analysis
- Projection model improvements

**Generation Method:** K-means clustering on normalized player statistics

**Update Frequency:** End of season

---

### 2. BPM Projections

**Description:** Machine learning projections for future season BPM values.

**Files:**
- `backend/data/bpm_projections_2027.csv.gz` - 2027 season projections
- `backend/data/bpm_change_modeling_data.csv.gz` - Training data for projection models
- `backend/data/bpm_change_features.json` - Feature definitions for projection model
- `backend/data/projection_leaderboard_2027.csv` - Projection leaderboard data

**Projection Method:**
- Features: Previous season BPM, age, usage rate, efficiency metrics, team context
- Model: Random Forest regression
- Validation: Historical backtesting with R² metrics
- Cluster transition integration: Blends similarity-weighted averages with cluster development patterns

**Usage:**
- 2027 season projections
- Projection leaderboards
- Player development tracking
- Transfer impact analysis

**Update Frequency:** Pre-season (before 2027 season)

---

### 3. Similarity Vectors

**Description:** Precomputed similarity vectors for efficient nearest-neighbor searches.

**Files:**
- `backend/app/cache/player_vectors_cache.pkl` - Cached similarity vectors
- `backend/app/cache/player_vectors_cache_metadata.json` - Cache metadata
- `backend/data/similarity_positions.csv` - Precomputed 3D positions for similarity map

**Vector Components:**
- Normalized statistical profile
- Style metrics (scoring, playmaking, rebounding, defense)
- Efficiency metrics
- Usage patterns

**Usage:**
- Similarity search
- "Similar Players" feature
- Similarity Map visualization
- Player comparison tool

**Update Frequency:** Weekly during season

---

### 4. Utilization Analysis

**Description:** Analysis of team usage patterns and their correlation with team success.

**Files:**
- `backend/data/usage_success_correlations.csv` - Correlation between usage and team success
- `backend/data/usage_success_merged.csv` - Merged usage and success data
- `backend/data/team_usage_analysis.csv` - Team-level usage analysis
- `backend/data/team_usage_analysis_detailed.json` - Detailed team usage analysis

**Key Metrics:**
- Usage rate distributions
- Correlation with win percentage
- Correlation with adjusted efficiency margin

**Usage:**
- Success correlation analysis
- Team strategy insights

**Update Frequency:** Weekly during season

---

### 6. Archetype Analysis

**Description:** Analysis of team archetype composition and its correlation with team success.

**Files:**
- `backend/data/archetype_success_correlations.csv` - Correlation between archetype composition and success
- `backend/data/archetype_team_analysis.csv` - Team-level archetype composition
- `backend/data/optimal_compositions.json` - Optimal archetype compositions

**Key Metrics:**
- Archetype distribution per team
- Correlation with team success metrics
- Optimal archetype combinations

**Usage:**
- Team composition analysis
- Archetype-based team comparison
- Team building insights

**Update Frequency:** Weekly during season

---

## Data Processing Pipeline

### 1. Data Ingestion

**Scripts:** `backend/scripts/data_processing/`

**Process:**
1. Download raw data from source APIs
2. Standardize field names and formats
3. Handle missing values
4. Normalize identifiers (player IDs, team names)
5. Validate data quality

**Key Scripts:**
- `link_player_ids.py` - Links player IDs across different sources
- `add_athlete_source_id_to_torvik.py` - Adds consistent player IDs to Torvik data

---

### 2. Data Cleanup Process

#### Bart Torvik Data Cleanup

**Steps:**
1. **Column Standardization:** Rename columns to consistent naming convention (snake_case)
2. **Team Name Normalization:** Standardize team names across all years (e.g., "UNC" → "North Carolina")
3. **Missing Value Handling:**
   - Fill missing BPM with 0 (replacement level)
   - Fill missing usage rates with team average
   - Drop rows with missing essential fields (player name, team)
4. **Data Type Conversion:** Convert numeric fields from strings to proper types
5. **Outlier Detection:** Remove statistical outliers (e.g., usage > 100%, negative minutes)
6. **Year Standardization:** Ensure year format is consistent (e.g., "2026" for 2025-26 season)

**Key Cleanups:**
- `BPM` → numeric, fill NaN with 0
- `Min_per` → numeric, cap at 40
- `usgG` → numeric, cap at 100
- Team names → standardized lookup table

#### Hoop Explorer Data Cleanup

**Steps:**
1. **Column Standardization:** Rename columns to match Torvik naming convention
2. **Player ID Mapping:** Create `AthleteSourceId` as primary identifier
3. **Height/Weight Normalization:**
   - Convert height from "6-2" format to inches (74)
   - Convert weight to numeric (lbs)
4. **Hometown Parsing:** Split `Hometown` into City, State, Country fields
5. **Position Standardization:** Map various position formats to standard (PG, SG, SF, PF, C)
6. **RAPM Handling:** Ensure RAPM values are numeric, handle missing values

**Key Cleanups:**
- `Height` → convert to inches
- `Weight` → numeric
- `Position` → standard 5 positions
- `Sourceid` → rename to `AthleteSourceId`
- `RAPM` → numeric, fill NaN with 0

#### College Basketball Data Cleanup

**Steps:**
1. **Game Data Parsing:** Parse JSON game data into structured format
2. **Date Standardization:** Convert various date formats to YYYYMMDD
3. **Team Name Matching:** Map team names to standardized names
4. **Player ID Linking:** Link game data to player IDs from other sources
5. **Statistical Validation:** Ensure game stats are within reasonable ranges
6. **Compression:** Compress JSON files with gzip to reduce storage

**Key Cleanups:**
- `numdate` → YYYYMMDD format
- `opponent` → standardized team name
- Player matching by name + team + year
- Compression to `.json.gz`

---

### 3. Data Joining Process

#### Player Data Join

**Join Strategy:** Left join on player identifier

**Primary Key:** `AthleteSourceId` (from Hoop Explorer)

**Join Process:**
1. **Start with Hoop Explorer roster data** as base (contains biographical info)
2. **Join Bart Torvik data** on:
   - `AthleteSourceId` (primary match)
   - Fallback: Player name + team + year (if ID missing)
3. **Join College Basketball Data** on:
   - `AthleteSourceId` (primary match)
   - Fallback: Player name + team + year (if ID missing)

**Join Logic:**
```python
# Primary join on AthleteSourceId
merged = hoop_explorer.merge(
    torvik,
    on='AthleteSourceId',
    how='left',
    suffixes=('', '_torvik')
)

# Fallback join for unmatched players
unmatched = merged[merged['BPM'].isna()]
for _, row in unmatched.iterrows():
    match = torvik[
        (torvik['Name'] == row['Name']) &
        (torvik['Team'] == row['Team']) &
        (torvik['year'] == row['year'])
    ]
    if not match.empty:
        # Fill in data from name match
        merged.loc[row.index, 'BPM'] = match.iloc[0]['BPM']
```

**Resulting Dataset Fields:**
- From Hoop Explorer: `AthleteSourceId`, `Name`, `Height`, `Weight`, `Hometown`, `Position`, `RAPM`
- From Bart Torvik: `BPM`, `OBPM`, `DBPM`, `Min_per`, `ORtg`, `usgG`, `eFG`, `TS_per`
- From College Basketball Data: Game-by-game stats (linked separately)

#### Team Data Join

**Join Strategy:** Inner join on team name + year

**Primary Key:** Team name + year

**Join Process:**
1. **Start with Hoop Explorer team data** as base
2. **Join Bart Torvik team data** on team name + year
3. **Join College Basketball team data** on team name + year

**Join Logic:**
```python
# Standardize team names first
team_lookup = {
    'UNC': 'North Carolina',
    'UCLA': 'UCLA',
    # ... full mapping
}

# Join on standardized names
merged_teams = hoop_teams.merge(
    torvik_teams,
    left_on=['standardized_name', 'year'],
    right_on=['standardized_name', 'year'],
    how='inner'
)
```

**Resulting Dataset Fields:**
- Team identifiers (name, conference)
- Efficiency metrics (adj_em, adj_o, adj_d)
- Roster information
- Game results

#### Game Data Join

**Join Strategy:** Separate lookup, not joined to main player dataset

**Process:**
1. Game data stored separately as JSON files
2. Linked dynamically via API endpoint using `ncaa_id` + `year`
3. Player game data accessed through `/api/v1/players/{ncaa_id}/games`

**Rationale:** Game data is too large to join with main player dataset; accessed on-demand

---

### 4. Data Quality Validation

**Validation Checks:**
1. **Completeness:** Ensure no missing critical fields (player ID, name, team, year)
2. **Consistency:** Verify team names match across sources
3. **Range Validation:** Check numeric values are within reasonable ranges
4. **Duplicate Detection:** Remove duplicate player entries
5. **Cross-Source Validation:** Compare overlapping metrics between sources

**Quality Metrics:**
- Player match rate: ~95% (most players have data from all sources)
- Team match rate: ~100% (all teams standardized)
- Missing BPM: <5% (filled with 0 for replacement level)
- Missing RAPM: ~60% (not all players have RAPM data)

---

### 5. Data Compression

**Process:**
1. Compress large CSV and JSON files using gzip
2. Update data loader to read compressed files
3. Maintain uncompressed copies for local development
4. Update .gitignore to exclude uncompressed files

**Key Scripts:**
- `compress_data.py` - Compresses CSV files
- `compress_game_data.py` - Compresses game JSON files

**Compression Ratios:**
- CSV files: ~70-80% reduction
- JSON game files: ~85% reduction

---

## Data Quality

### Validation

**Checks Performed:**
- Missing value detection
- Outlier identification (e.g., BPM > 20 or < -10)
- Duplicate record detection
- ID consistency across sources
- Season year validation
- Conference affiliation verification

**Error Handling:**
- Invalid records are logged and excluded
- Missing values are filled with defaults or marked as null
- Outliers are flagged for manual review

---

### Data Freshness

**Current Data Coverage:**
- Years: 2019-2026 (8 seasons)
- Players: ~15,000+ unique players
- Teams: 350+ D1 teams
- Games: ~50,000+ game records

**Update Schedule:**
- **Daily:** Game data, current season player stats
- **Weekly:** Similarity vectors, roster updates
- **Monthly:** Team efficiency updates
- **End of Season:** Historical data, clusters, projections

---

## Design Choices

### 1. Primary Player Identifier: AthleteSourceId

**Choice:** Use `AthleteSourceId` from Hoop Explorer as the primary player identifier across all data sources.

**Rationale:**
- Hoop Explorer provides consistent, unique identifiers across seasons
- More reliable than name-based matching (players can have same name)
- Allows tracking players across transfers and team changes
- IDs are stable over time, unlike some other sources

**Trade-off:**
- Requires joining other sources to this ID
- Some players may not have this ID in certain sources (handled with fallback matching)

---

### 2. Left Join Strategy for Player Data

**Choice:** Use Hoop Explorer roster data as the base and left join other sources (Bart Torvik, College Basketball Data).

**Rationale:**
- Hoop Explorer has the most complete roster information
- Ensures all players in the system have biographical data
- Allows graceful handling of missing data from other sources
- Prioritizes roster completeness over statistical completeness

**Trade-off:**
- Some players may have missing BPM or RAPM if not in Torvik
- Requires fallback matching for unmatched records

---

### 3. Fallback Matching by Name + Team + Year

**Choice:** When `AthleteSourceId` matching fails, fallback to matching by player name, team, and year.

**Rationale:**
- Handles cases where player IDs are missing or inconsistent
- Increases data coverage (catches ~5% more players)
- Provides robustness against source data quality issues
- Allows data from sources without consistent IDs

**Trade-off:**
- Risk of false positives (players with same name on same team in different years)
- Requires additional validation logic
- Slightly slower than ID-only matching

---

### 4. Separate Storage for Game Data

**Choice:** Store game-by-game data separately as compressed JSON files, not joined to main player dataset.

**Rationale:**
- Game data is voluminous (~50,000+ games × multiple players per game)
- Joining would create an extremely large player dataset
- Game data is accessed infrequently (only when viewing specific player's game log)
- On-demand loading via API is more efficient for this use case
- Allows easy updates to game data without rebuilding entire dataset

**Trade-off:**
- Requires separate API endpoint for game data
- Cannot query game data alongside player stats in single query
- Slightly higher latency for game data access

---

### 5. Gzip Compression for Storage

**Choice:** Compress all CSV and JSON data files using gzip (.csv.gz, .json.gz).

**Rationale:**
- 70-85% reduction in file size
- Critical for deployment (platforms have disk limits)
- Pandas and standard libraries can read compressed files directly
- Minimal performance impact (decompression is fast)
- Allows keeping more historical data

**Trade-off:**
- Slightly slower initial load time (decompression overhead)
- Cannot inspect files directly without decompression
- Requires custom data loader to handle both compressed and uncompressed

---

### 6. Missing BPM Filled with 0 (Replacement Level)

**Choice:** Fill missing BPM values with 0 rather than dropping records or using null.

**Rationale:**
- BPM of 0 represents "replacement level" player
- Preserves player records even if advanced metrics are missing
- Allows ranking and filtering without special null handling
- Consistent with basketball analytics conventions
- Prevents bias from dropping low-usage players

**Trade-off:**
- May underestimate true value of some players
- Could affect percentile calculations
- Requires clear documentation of this convention

---

### 7. Team Name Standardization

**Choice:** Maintain a lookup table mapping all team name variations to standardized names.

**Rationale:**
- Different sources use different team names (e.g., "UNC" vs "North Carolina")
- Essential for accurate data joining across sources
- Enables consistent team-based queries and aggregations
- Prevents duplicate team records

**Trade-off:**
- Requires manual maintenance of lookup table
- New teams or name changes require updates
- Some edge cases may be missed

---

### 8. 18 Clusters for Player Clustering

**Choice:** Use K-means clustering with 18 clusters (IDs 0-17) for player archetype classification.

**Rationale:**
- Provides granular player type differentiation
- Captures nuanced playing styles (e.g., different types of guards, forwards, centers)
- Balances specificity with interpretability
- Allows meaningful cluster transition analysis
- Determined via elbow method and silhouette analysis

**Trade-off:**
- More clusters than simpler systems (some use 5-8)
- Requires cluster descriptions for user interpretability
- May overfit to specific season data


---

### 9. Year Format: Single Year (e.g., "2026" for 2025-26 season)

**Choice:** Use single year integer to represent seasons (e.g., "2026" for 2025-26 season).

**Rationale:**
- Simpler than year ranges (e.g., "2025-26")
- Easier to sort and query
- Consistent with common basketball analytics conventions
- Reduces storage space

**Trade-off:**
- Less intuitive for users unfamiliar with convention
- Requires documentation to clarify mapping

---

## Data Schema

### Player Schema

**Basic Tier:**
```json
{
  "player_key": "string",
  "player_name": "string",
  "team": "string",
  "year": "int",
  "Position": "string",
  "BPM": "float",
  "PPG": "float",
  "RPG": "float",
  "APG": "float",
  "Usage": "float",
  "ORtg": "float",
  "data_tier": "basic"
}
```

**Enriched Tier:**
```json
{
  "player_key": "string",
  "player_name": "string",
  "team": "string",
  "year": "int",
  "Position": "string",
  "Height": "string",
  "Weight": "int",
  "BPM": "float",
  "off_usage": "float",
  "off_assist": "float",
  "off_to": "float",
  "def_orb": "float",
  "def_stl": "float",
  "def_blk": "float",
  "data_tier": "enriched"
}
```

### Team Schema

```json
{
  "Team": "string",
  "Conference": "string",
  "year": "int",
  "adj_em": "float",
  "adj_o": "float",
  "adj_d": "float",
  "W": "int",
  "L": "int"
}
```

### Game Schema

```json
{
  "ncaa_id": "string",
  "numdate": "string",
  "datetext": "string",
  "opponent": "string",
  "loc": "string",
  "pts": "int",
  "Min_per": "float",
  "ORtg": "float",
  "Usage": "float",
  "eFG": "float",
  "bpm": "float",
  "win2": "int"
}
```

---

## Data Access

### Backend Data Loading

**File:** `backend/app/core/data_loader.py`

**Functions:**
- `read_csv_with_compression()` - Reads CSV files, handles gzip automatically
- `load_enriched_players()` - Loads enriched player data
- `load_basic_players()` - Loads basic player data
- `load_all_players()` - Combines basic and enriched data
- `load_torvik_players()` - Loads Torvik-specific data

**Caching:**
- Player data loaded at startup and cached in memory
- Game data cached on first load per year
- Similarity vectors cached in pickle format

---

## Data Limitations

### Known Limitations

1. **Historical Data:** Limited to 2019-present due to data availability
2. **D2/D3 Teams:** Only D1 teams are fully tracked
3. **Tracking Data:** Enriched tier only available for subset of players
4. **Real-time Updates:** 24-48 hour delay for game data processing
5. **Transfer Portal:** Portal movement data may be incomplete

### Missing Data Handling

- **Missing Games:** Players with < 5 games in a season may have incomplete stats
- **Missing Biographical Data:** Height/weight not available for all players
- **Missing Tracking Data:** Enriched metrics only for players with tracking coverage
- **Early Season Data:** First few weeks of season may have limited sample size

---

## Data Licensing

**Bart Torvik:** Public data, attribution required
**Hoop Explorer:** Public data, attribution required
**Game Data:** Compiled from public box scores

**Attribution:** All data sources are publicly available and used for analytical purposes. Credit is given to original data providers where applicable.

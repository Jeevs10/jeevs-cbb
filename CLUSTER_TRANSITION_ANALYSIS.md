# Cluster Transition Analysis & Projection Model Improvements

## Overview

This document describes the cluster transition analysis conducted on historical player data (2019-2025) and how it has been integrated into the BPM projection model to improve prediction accuracy.

## Background

The projection model uses KMeans clustering to group players into 18 archetypes based on their playing style and performance metrics. Historically, the model only considered how similar players developed within the same cluster. This analysis adds two new dimensions:

1. **Cluster Transitions**: How players move between clusters year-over-year
2. **Cluster Development Patterns**: How players within the same cluster develop over time

## Methodology

### Data Sources

- **Historical Player Data**: Basic player statistics for 2019-2025 (57,274 players total)
- **Cluster Assignments**: Generated for each year using KMeans with 18 clusters
- **Features Used**: PPG, RPG, APG, Usage, eFG%, TS%, offensive/defensive ratings

### Analysis Scripts

#### 1. `cluster_historical_players.py`
Generates cluster assignments for historical players using basic features available across all years.

```bash
python cluster_historical_players.py
```

**Output**: 
- `player_clusters_{year}.csv` for each year (2019-2025)
- `cluster_descriptions_{year}.json` with cluster metadata

#### 2. `analyze_cluster_transitions.py`
Analyzes player movements between clusters and development patterns within clusters.

```bash
python analyze_cluster_transitions.py
```

**Output**:
- `cluster_transition_matrix.json` - Probability of moving from one cluster to another
- `cluster_development_stats.json` - Average stat changes for players staying in same cluster
- `player_transitions.csv` - Individual player transition records

## Key Findings

### Cluster Transition Matrix

The transition matrix shows the probability of a player moving from one cluster to another year-over-year. Key insights:

**Most players change clusters**: Only 4-7% of players stay in the same cluster year-over-year. This indicates significant player development and role changes.

**Example transitions from Cluster 0**:
- → Cluster 17: 13.76% (most common destination)
- → Cluster 3: 12.34%
- → Cluster 7: 9.29%
- → Cluster 5: 9.15%
- → Cluster 0: 4.20% (staying in same cluster)

**High-mobility clusters**: Some clusters have very low retention rates (<5%), suggesting they represent transitional player types (e.g., freshmen adjusting to college basketball).

**Stable clusters**: A few clusters have higher retention rates (>10%), possibly representing established player archetypes (e.g., senior role players).

### Cluster Development Patterns

For players who stay in the same cluster, we analyzed their year-over-year development in key statistics:

**Cluster 1 (Developing scorers)**:
- Mean PPG change: +2.28
- Mean RPG change: +0.46
- Mean APG change: +0.86
- Mean Usage change: +2.28%
- Sample size: 59 players

**Cluster 17 (High-usage stars)**:
- Mean PPG change: +3.31
- Mean RPG change: +1.79
- Mean APG change: +0.40
- Mean Usage change: +1.89%
- Sample size: 139 players

**Cluster 10 (Declining players)**:
- Mean PPG change: -3.12
- Mean RPG change: -0.59
- Mean Usage change: -1.57%
- Sample size: 31 players

## Integration into Projection Model

### Model Changes

The projection service (`projection_service.py`) was updated to incorporate:

1. **Cluster Transition Matrix**: Loaded from `cluster_transition_matrix.json`
2. **Cluster Development Stats**: Loaded from `cluster_development_stats.json`
3. **Blended Projection Approach**: Combines similarity-weighted averages with cluster development patterns

### Projection Formula

The new projection formula blends three components:

```
blended_change = 0.7 * similarity_weighted_avg + 0.3 * cluster_development_pattern
```

**Similarity-weighted average (70%)**: Based on how similar historical players developed, weighted by feature similarity (Usage, PPG, RPG, APG, shooting efficiency).

**Cluster development pattern (30%)**: Based on how players in the same cluster typically develop (using PPG change as a proxy for BPM change when BPM data is limited).

**Cluster transition adjustment**: If a player has a low probability of staying in their current cluster (<50%), the projection is made more conservative (10% reduction) and the confidence interval is widened (20% increase) to account for uncertainty.

### Example: Keaton Wagler (Cluster 12)

**Before integration**:
- Projected 2027 BPM: 18.34
- Based solely on similar players

**After integration**:
- Projected 2027 BPM: 15.95
- Blended approach: 70% similarity + 30% cluster development
- Cluster 12 development: +0.98 PPG average change
- Conservative adjustment applied due to low cluster retention

## Similar Players Display

### Career Trajectory View

The similar players display was updated to show career trajectories instead of individual year transitions. This provides better context for how similar players developed over their entire careers.

**Before**: Showed duplicate entries for the same player across different years
- Tramon Mark (Texas) 2021→2022: +4.06 BPM
- Tramon Mark (Texas) 2022→2023: -1.97 BPM
- Tramon Mark (Texas) 2023→2024: -1.32 BPM

**After**: Groups by player and shows full career trajectory
- Tramon Mark (Texas) - Similarity: 0.589
  - 2021→2022: +4.06 BPM
  - 2022→2023: -1.97 BPM
  - 2023→2024: -1.32 BPM
  - 2024→2025: -0.67 BPM

### Career BPM Graph

A new visualization component (`SimilarPlayersCareerGraph.tsx`) displays:
- Line chart showing year-over-year BPM changes for similar players
- Color-coded lines for different years
- Detailed table with all career trajectory data

## Performance Considerations

### Data Loading

The projection service now loads additional data files:
- `cluster_transition_matrix.json` (~50KB)
- `cluster_development_stats.json` (~30KB)
- Historical player data for name mapping (~7 years × ~8KB each)

Total additional load time: <100ms

### Similar Players Grouping

The similar players calculation now:
1. Groups by `player_key` to identify unique players
2. Calculates average similarity across all years for each player
3. Returns top 5 unique players with full career trajectories
4. Filters out invalid player keys (empty, 'nan')

## Future Improvements

### Potential Enhancements

1. **BPM-based development patterns**: Use actual BPM changes instead of PPG as proxy when data becomes available
2. **Multi-year projections**: Extend transition analysis to 2-3 year projections
3. **Position-specific transitions**: Analyze transitions within position groups
4. **Team context**: Factor in team quality and role changes
5. **Age/Year-in-school**: Incorporate class year (freshman, sophomore, etc.) into transition probabilities

### Data Gaps

- Historical data before 2019 is limited
- BPM data not consistently available in older datasets
- Transfer portal effects not captured (players changing teams may have different development patterns)

## Technical Details

### File Structure

```
backend/
├── data/
│   ├── cluster_transition_matrix.json
│   ├── cluster_development_stats.json
│   ├── player_transitions.csv
│   ├── player_clusters_2019.csv
│   ├── player_clusters_2020.csv
│   ├── ...
│   ├── cluster_descriptions_2019.json
│   ├── cluster_descriptions_2020.json
│   └── ...
├── cluster_historical_players.py
├── analyze_cluster_transitions.py
└── app/services/
    └── projection_service.py (updated)

frontend/
└── components/player/
    └── SimilarPlayersCareerGraph.tsx (new)
```

### API Endpoints

The projection API remains unchanged:
```
GET /api/v1/players/{player_id}/projections?current_year=2026&years_ahead=1&min_samples=10
```

Response now includes:
- `similar_players` array with career trajectories
- Same projection structure but with blended calculations

## Conclusion

The cluster transition analysis provides valuable context for player projections by:

1. **Accounting for cluster mobility**: Recognizing that most players change clusters year-over-year
2. **Incorporating development patterns**: Using historical cluster development as a baseline
3. **Improving uncertainty estimates**: Widening confidence intervals when cluster transitions are likely
4. **Better similar players display**: Showing career trajectories instead of individual years

These improvements make the projection model more robust and provide users with better context for understanding player development potential.

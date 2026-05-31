# Cluster-Based Player Projections API

## Overview

This API provides cluster-based BPM (Box Plus/Minus) projections for college basketball players. It uses historical year-over-year BPM changes from players in the same cluster to predict a target player's growth, weighted by feature similarity.

## Methodology

### Core Concept
The projection methodology is based on the principle that players with similar playing styles and physical attributes tend to follow similar development trajectories. By analyzing how historically similar players have progressed year-over-year, we can make data-driven projections for current players.

### Algorithm Steps

1. **Cluster Identification**: The target player is assigned to a cluster based on their playing style, physical attributes, and performance metrics. Clusters are pre-computed using PCA and clustering algorithms on player feature vectors.

2. **Historical Pool Construction**: We filter the historical BPM change dataset (`bpm_change_modeling_data.csv`) to include only players from the same cluster. This creates a pool of comparable players with known year-over-year trajectories.

3. **Feature Similarity Calculation**: For each historical player in the pool, we calculate a similarity score to the target player using weighted Euclidean distance on key features:
   - Usage rate (25% weight)
   - Current BPM (20% weight)
   - Height (15% weight)
   - Offensive rating (10% weight)
   - Defensive rating (10% weight)
   - Effective field goal percentage (10% weight)
   - True shooting percentage (10% weight)

4. **Weighted Projection**: Historical BPM changes are weighted by their similarity scores. More similar players have greater influence on the projection.

5. **Confidence Intervals**: We calculate weighted standard deviations to provide 95% confidence intervals for projections.

6. **Multi-Year Projections**: The algorithm can project 1-3 years ahead, with diminishing returns for longer time horizons.

### Data Sources

- **player_clusters.csv**: Contains cluster assignments for 2,903+ players across 18 clusters
- **cluster_descriptions.json**: Metadata for each cluster including average characteristics and top players
- **bpm_change_modeling_data.csv**: 22,442 historical year-over-year BPM changes with 40+ features

## API Endpoints

### Get Player Projections

```http
GET /api/v1/players/{ncaa_id}/projections
```

**Query Parameters:**
- `ncaa_id` (path): Player NCAA ID
- `current_year` (query): Current year for the player (default: 2026, range: 2019-2030)
- `years_ahead` (query): Number of years to project (default: 1, range: 1-3)
- `min_samples` (query): Minimum historical samples required (default: 10, range: 5-100)

**Response Example:**
```json
{
  "success": true,
  "player_id": "123456",
  "current_year": 2026,
  "cluster_id": 4,
  "cluster_description": {
    "cluster_id": 4,
    "count": 193,
    "avg_height": 77.92,
    "avg_usage": 21.65,
    "avg_rim_freq": 0.485,
    "avg_3pt_pct": 32.9,
    "avg_bpm": 3.04,
    "top_players": [...]
  },
  "historical_samples": 245,
  "projections": [
    {
      "year": 2027,
      "projected_bpm": 7.2,
      "bpm_change": 2.1,
      "confidence_interval": [5.8, 8.6],
      "percentile_rank": 0.75,
      "sample_size": 245
    }
  ],
  "similar_players": [
    {
      "player_key": "3906520",
      "year_from": 2019,
      "year_to": 2020,
      "bpm_change": 2.55,
      "similarity": 0.85
    }
  ],
  "methodology": "cluster_weighted_average"
}
```

### Get Cluster Projections Summary

```http
GET /api/v1/clusters/{cluster_id}/projections-summary
```

**Query Parameters:**
- `cluster_id` (path): Cluster ID to analyze
- `limit` (query): Number of top players to return (default: 10, range: 1-50)

**Response Example:**
```json
{
  "cluster_id": 4,
  "total_samples": 245,
  "valid_bpm_changes": 230,
  "avg_bpm_change": 1.5,
  "median_bpm_change": 1.2,
  "std_bpm_change": 3.2,
  "positive_changes": 140,
  "negative_changes": 90,
  "top_improvements": [...],
  "top_declines": [...]
}
```

## Usage Examples

### Python

```python
import requests

# Get projections for a player
response = requests.get(
    "http://localhost:8000/api/v1/players/123456/projections",
    params={
        "current_year": 2026,
        "years_ahead": 2,
        "min_samples": 15
    }
)

projections = response.json()
print(f"Projected 2027 BPM: {projections['projections'][0]['projected_bpm']}")
```

### JavaScript/TypeScript

```typescript
// Get projections for a player
const response = await fetch(
  'http://localhost:8000/api/v1/players/123456/projections?current_year=2026&years_ahead=2'
);
const projections = await response.json();

console.log(`Projected 2027 BPM: ${projections.projections[0].projected_bpm}`);
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `404`: Player not found or insufficient data
- `400`: Invalid query parameters
- `500`: Internal server error

Error response format:
```json
{
  "detail": "Error message describing the issue"
}
```

## Caching

Projections are cached for 10 minutes to improve performance. Cache keys are based on:
- Player NCAA ID
- Current year
- Years ahead
- Minimum samples

## Performance Considerations

- The service loads cluster and BPM change data at startup
- Similarity calculations are O(n) where n is the number of historical samples
- Caching reduces repeated calculations for the same player
- Minimum sample requirements ensure statistical significance

## Limitations

1. **Data Availability**: Projections are only available for players in the cluster dataset
2. **Sample Size**: Clusters with fewer than `min_samples` historical records cannot generate projections
3. **Assumption of Similarity**: The methodology assumes that similar players follow similar trajectories, which may not always hold true
4. **External Factors**: The model does not account for injuries, transfers, coaching changes, or other external factors

## Future Enhancements

Potential improvements to the projection system:

1. **Machine Learning Models**: Train regression models on historical data for more accurate predictions
2. **Feature Engineering**: Add more sophisticated features (team quality, conference strength, etc.)
3. **Time Decay**: Weight more recent historical data more heavily
4. **Cross-Cluster Analysis**: Include players from similar clusters when sample size is low
5. **Position-Specific Models**: Develop separate models for different positions
6. **Transfer Portal Impact**: Account for transfer portal effects on player development

## Testing

Run the projection service tests:

```bash
cd backend
python -m pytest tests/test_projections.py -v
```

## Support

For questions or issues, please refer to the main project README or contact the development team.

# API Documentation

## Overview

The JEEVS CBB API provides endpoints for accessing college basketball player and team statistics, analytics, and projections. The API is built with FastAPI and follows RESTful conventions.

**Base URL:** `http://localhost:8000` (development) or your deployed URL

**API Version:** v1

**All endpoints are prefixed with `/api/v1`**

---

## Authentication

Currently, the API does not require authentication. Rate limiting is applied to prevent abuse.

---

## Rate Limiting

- **Default:** 100 requests per minute per IP address
- **Health Check:** 100 requests per minute

---

## Response Format

All responses return JSON. Standard error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

---

## Endpoints

### Players

#### Get All Players
```http
GET /api/v1/players
```

**Query Parameters:**
- `limit` (int, default: 50, max: 5000) - Number of results to return
- `offset` (int, default: 0) - Number of results to skip
- `sort` (string, default: "adj_rapm_margin") - Field to sort by
- `order` (string, default: "desc") - Sort order ("asc" or "desc")
- `year` (string, optional) - Filter by year (e.g., "2026" or "career")
- `conf` (string, optional) - Filter by conference
- `search` (string, optional) - Search by player name
- `dataTier` (string, optional) - Filter by data tier ("basic" or "enriched")
- `d1Only` (boolean, default: false) - Filter to D1 players only
- `highMajorOnly` (boolean, default: false) - Filter to high major players only

**Response:**
```json
{
  "results": [
    {
      "player_key": "123456",
      "player_name": "John Doe",
      "team": "Duke",
      "year": 2026,
      "BPM": 5.2,
      "PPG": 18.5,
      "RPG": 6.3,
      "APG": 4.1,
      ...
    }
  ],
  "total": 5000,
  "limit": 50,
  "offset": 0
}
```

#### Get Player by ID
```http
GET /api/v1/players/{ncaa_id}
```

**Path Parameters:**
- `ncaa_id` (string) - Player's NCAA ID

**Query Parameters:**
- `year` (string, optional) - Filter by year

**Response:**
```json
{
  "player_key": "123456",
  "player_name": "John Doe",
  "team": "Duke",
  "year": 2026,
  "Position": "PG",
  "Height": "6-2",
  "Weight": 185,
  "BPM": 5.2,
  "PPG": 18.5,
  "RPG": 6.3,
  "APG": 4.1,
  ...
}
```

#### Get Player Games
```http
GET /api/v1/players/{ncaa_id}/games
```

**Path Parameters:**
- `ncaa_id` (string) - Player's NCAA ID

**Query Parameters:**
- `year` (string, optional) - Filter by year (default: "2026")
- `limit` (int, default: 5, max: 1000) - Number of games to return

**Response:**
```json
{
  "player_id": "123456",
  "year": "2026",
  "total_games": 35,
  "games": [
    {
      "numdate": "20260315",
      "datetext": "Mar 15",
      "opponent": "North Carolina",
      "loc": "N",
      "pts": 22,
      "Min_per": 35.2,
      "ORtg": 118.5,
      "Usage": 24.3,
      "eFG": 0.582,
      "bpm": 6.1,
      "win2": 1,
      ...
    }
  ]
}
```

#### Get Player Moves
```http
GET /api/v1/players/{ncaa_id}/moves
```

**Path Parameters:**
- `ncaa_id` (string) - Player's NCAA ID

**Query Parameters:**
- `year` (string, optional) - Filter by year

**Response:**
```json
{
  "player_id": "123456",
  "moves": [
    {
      "season": 2025,
      "from_team": "Duke",
      "to_team": "Kentucky",
      "transfer_type": "portal"
    }
  ]
}
```

#### Get Player Badges
```http
GET /api/v1/players/{ncaa_id}/badges
```

**Path Parameters:**
- `ncaa_id` (string) - Player's NCAA ID

**Query Parameters:**
- `year` (string, optional) - Filter by year

**Response:**
```json
{
  "player_id": "123456",
  "badges": [
    {
      "name": "Elite Scorer",
      "description": "Top 10% in PPG",
      "tier": "gold"
    }
  ]
}
```

#### Get Similar Players
```http
GET /api/v1/players/{ncaa_id}/similar
```

**Path Parameters:**
- `ncaa_id` (string) - Player's NCAA ID

**Query Parameters:**
- `style_weight` (float, default: 0.7) - Weight for style similarity (0-1)
- `year` (string, optional) - Filter by year

**Response:**
```json
{
  "player_id": "123456",
  "similar_players": [
    {
      "player_key": "789012",
      "player_name": "Jane Smith",
      "similarity_score": 0.92,
      "style_similarity": 0.88,
      "production_similarity": 0.95
    }
  ]
}
```

#### Get Player Radar
```http
GET /api/v1/players/{ncaa_id}/radar
```

**Path Parameters:**
- `ncaa_id` (string) - Player's NCAA ID

**Query Parameters:**
- `year` (string, optional) - Filter by year
- `preset` (string, optional) - Radar preset name
- `custom_fields` (array, optional) - Custom field names

**Response:**
```json
{
  "player_id": "123456",
  "radar_data": {
    "scoring": 85,
    "playmaking": 72,
    "rebounding": 65,
    "defense": 78,
    "efficiency": 82
  }
}
```

#### Get Player Evolution
```http
GET /api/v1/players/{ncaa_id}/evolution
```

**Path Parameters:**
- `ncaa_id` (string) - Player's NCAA ID

**Query Parameters:**
- `year` (string, optional) - Filter by year
- `metric` (string, optional) - Specific metric to track

**Response:**
```json
{
  "player_id": "123456",
  "evolution": [
    {
      "year": 2024,
      "BPM": 3.2,
      "PPG": 12.5
    },
    {
      "year": 2025,
      "BPM": 4.8,
      "PPG": 16.2
    }
  ]
}
```

#### Get Player History
```http
GET /api/v1/players/{ncaa_id}/history
```

**Path Parameters:**
- `ncaa_id` (string) - Player's NCAA ID

**Response:**
```json
{
  "player_id": "123456",
  "history": [
    {
      "year": 2024,
      "team": "Duke",
      "BPM": 3.2
    },
    {
      "year": 2025,
      "team": "Kentucky",
      "BPM": 4.8
    }
  ]
}
```

#### Get Player Historical BPM
```http
GET /api/v1/players/{ncaa_id}/historical-bpm
```

**Path Parameters:**
- `ncaa_id` (string) - Player's NCAA ID

**Response:**
```json
{
  "player_id": "123456",
  "historical_bpm": [
    {
      "year": 2019,
      "BPM": 2.1,
      "Name": "John Doe",
      "Team": "Duke"
    }
  ]
}
```

---

### Teams

#### Get All Teams
```http
GET /api/v1/teams
```

**Query Parameters:**
- `year` (string, optional) - Filter by year

**Response:**
```json
{
  "teams": [
    {
      "Team": "Duke",
      "Conference": "ACC",
      "year": 2026,
      "adj_em": 25.3,
      "adj_o": 118.5,
      "adj_d": 93.2
    }
  ]
}
```

#### Get Team by ID
```http
GET /api/v1/teams/{team_id}
```

**Path Parameters:**
- `team_id` (string) - Team ID or name

**Query Parameters:**
- `year` (string, optional) - Filter by year

**Response:**
```json
{
  "Team": "Duke",
  "Conference": "ACC",
  "year": 2026,
  "adj_em": 25.3,
  "adj_o": 118.5,
  "adj_d": 93.2,
  "players": [...]
}
```

---

### Projections

#### Get 2027 Projections
```http
GET /api/v1/projections/2027
```

**Response:**
```json
[
  {
    "player_key": "123456",
    "player_name": "John Doe",
    "projected_bpm": 6.5,
    "confidence": 0.82
  }
]
```

#### Get Projection Leaderboard
```http
GET /api/v1/projections/leaderboard
```

**Query Parameters:**
- `limit` (int, default: 50) - Number of results

**Response:**
```json
{
  "results": [
    {
      "player_key": "123456",
      "player_name": "John Doe",
      "projected_bpm": 8.2,
      "current_bpm": 5.5,
      "improvement": 2.7
    }
  ]
}
```

---

### Clusters

#### Get Cluster Analysis
```http
GET /api/v1/clusters
```

**Response:**
```json
{
  "clusters": [
    {
      "cluster_id": 1,
      "name": "Elite Scorers",
      "count": 150,
      "avg_bpm": 7.5,
      "description": "High-volume scorers with elite efficiency"
    }
  ]
}
```

#### Get Cluster Leaderboard
```http
GET /api/v1/clusters/leaderboard
```

**Response:**
```json
{
  "results": [
    {
      "cluster_id": 1,
      "name": "Elite Scorers",
      "avg_bpm": 7.5,
      "count": 150
    }
  ]
}
```

#### Get Cluster BPM Distribution
```http
GET /api/v1/clusters/{cluster_id}/bpm-distribution
```

**Path Parameters:**
- `cluster_id` (int) - Cluster ID

**Response:**
```json
{
  "cluster_id": 1,
  "avg_bpm": 7.5,
  "count": 150,
  "distribution": [8.2, 7.5, 6.8, ...],
  "percentiles": {
    "p10": 5.2,
    "p25": 6.1,
    "p50": 7.5,
    "p75": 8.9,
    "p90": 10.2
  }
}
```

---

### Similarity

#### Get All Vectors
```http
GET /api/v1/similarity/vectors
```

**Response:**
```json
{
  "vectors": [
    {
      "player_key": "123456",
      "vector": [0.5, 0.3, 0.8, ...]
    }
  ]
}
```

#### Get Precomputed Positions
```http
GET /api/v1/similarity/positions
```

**Response:**
```json
{
  "positions": [
    {
      "player_key": "123456",
      "x": 0.5,
      "y": 0.3
    }
  ]
}
```

#### Get Nearest Neighbors
```http
GET /api/v1/similarity/nearest/{ncaa_id}
```

**Path Parameters:**
- `ncaa_id` (string) - Player's NCAA ID

**Query Parameters:**
- `limit` (int, default: 20) - Number of neighbors to return

**Response:**
```json
{
  "player_id": "123456",
  "neighbors": [
    {
      "player_key": "789012",
      "distance": 0.15,
      "player_name": "Jane Smith"
    }
  ]
}
```

---

### Years

#### Get Available Years
```http
GET /api/v1/years
```

**Response:**
```json
{
  "years": [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
}
```

---

### Game (PORTALMANIA)

#### Get Random Pair
```http
GET /api/v1/game/random-pair
```

**Query Parameters:**
- `min_distance` (int, default: 3) - Minimum degree of separation
- `max_distance` (int, default: 6) - Maximum degree of separation

**Response:**
```json
{
  "start_player": {
    "id": "123456",
    "name": "John Doe",
    "team": "Duke"
  },
  "end_player": {
    "id": "789012",
    "name": "Jane Smith",
    "team": "Kentucky"
  },
  "distance": 4
}
```

#### Get Game Player Info
```http
GET /api/v1/game/player/{player_id}
```

**Path Parameters:**
- `player_id` (string) - Player ID

**Response:**
```json
{
  "id": "123456",
  "name": "John Doe",
  "team": "Duke",
  "years": [2024, 2025],
  "teams": ["Duke", "Kentucky"],
  "Position": "PG"
}
```

#### Check Teammates
```http
POST /api/v1/game/check-teammates
```

**Request Body:**
```json
{
  "player_id1": "123456",
  "player_id2": "789012"
}
```

**Response:**
```json
{
  "are_teammates": true,
  "teammate_info": {
    "team": "Duke",
    "year": 2025
  }
}
```

#### Get Shortest Path
```http
POST /api/v1/game/shortest-path
```

**Request Body:**
```json
{
  "player_id1": "123456",
  "player_id2": "789012"
}
```

**Response:**
```json
{
  "path": [
    {"id": "123456", "name": "John Doe"},
    {"id": "345678", "name": "Bob Johnson"},
    {"id": "789012", "name": "Jane Smith"}
  ]
}
```

---

### NIL Valuation

#### Get Player NIL Valuation
```http
GET /api/v1/nil/players/{ncaa_id}
```

**Path Parameters:**
- `ncaa_id` (string) - Player's NCAA ID

**Query Parameters:**
- `year` (string, optional) - Filter by year

**Response:**
```json
{
  "player_id": "123456",
  "nil_score": 85.5,
  "market_value": 250000,
  "factors": {
    "performance": 0.6,
    "market": 0.3,
    "social": 0.1
  }
}
```

#### Get Team NIL Valuations
```http
GET /api/v1/nil/teams/{team_id}
```

**Path Parameters:**
- `team_id` (string) - Team ID

**Query Parameters:**
- `year` (string, optional) - Filter by year

**Response:**
```json
{
  "team_id": "duke",
  "total_nil_value": 2500000,
  "players": [
    {
      "player_id": "123456",
      "player_name": "John Doe",
      "nil_score": 85.5
    }
  ]
}
```

#### Get All NIL Valuations
```http
GET /api/v1/nil/players
```

**Query Parameters:**
- `limit` (int, default: 50, max: 100) - Number of results
- `offset` (int, default: 0) - Pagination offset
- `sort` (string, default: "nil_score") - Sort field
- `order` (string, default: "desc") - Sort order

**Response:**
```json
{
  "results": [...],
  "total": 5000,
  "limit": 50,
  "offset": 0
}
```

---

### Additional Projections

#### Get Player Projections
```http
GET /api/v1/players/{ncaa_id}/projections
```

**Path Parameters:**
- `ncaa_id` (string) - Player's NCAA ID

**Query Parameters:**
- `current_year` (int, default: 2026) - Current year for the player
- `years_ahead` (int, default: 1, max: 3) - Number of years to project
- `min_samples` (int, default: 10) - Minimum historical samples required

**Response:**
```json
{
  "player_id": "123456",
  "current_bpm": 5.5,
  "projected_bpm": 6.8,
  "confidence": 0.75,
  "years_ahead": 1
}
```

#### Get Cluster Projections Summary
```http
GET /api/v1/clusters/{cluster_id}/projections-summary
```

**Path Parameters:**
- `cluster_id` (int) - Cluster ID

**Query Parameters:**
- `limit` (int, default: 10, max: 50) - Number of players to return

**Response:**
```json
{
  "cluster_id": 1,
  "avg_projected_bpm": 6.5,
  "top_players": [...]
}
```

---

### Additional Clusters

#### Get Cluster Descriptions
```http
GET /api/v1/clusters/descriptions
```

**Query Parameters:**
- `year` (string, optional) - Filter by year

**Response:**
```json
{
  "clusters": [
    {
      "cluster_id": 0,
      "name": "Elite Scorers",
      "description": "High-volume scorers with elite efficiency",
      "avg_bpm": 7.5,
      "count": 150
    }
  ]
}
```

#### Get Cluster Rankings
```http
GET /api/v1/clusters/rankings
```

**Query Parameters:**
- `cluster_id` (int, required) - Cluster ID (0-17)
- `year` (string, optional) - Filter by year
- `limit` (int, default: 50, max: 100) - Number of results
- `offset` (int, default: 0) - Pagination offset
- `sort_by` (string, default: "BPM") - Sort field
- `sort_order` (string, default: "desc") - Sort order

**Response:**
```json
{
  "results": [...],
  "count": 5000,
  "filtered_count": 150,
  "cluster_info": {...},
  "success": true
}
```

#### Get Cluster Players
```http
GET /api/v1/clusters/players
```

**Response:**
```json
{
  "players": [
    {
      "player_key": "123456",
      "cluster": 1,
      "year": 2026
    }
  ]
}
```

#### Get Cluster Teams
```http
GET /api/v1/clusters/teams
```

**Response:**
```json
{
  "teams": [
    {
      "team": "Duke",
      "cluster_composition": {...}
    }
  ]
}
```

---

### Utilization & Archetype

#### Get Utilization Correlations
```http
GET /api/v1/utilization/correlations
```

**Response:**
```json
{
  "correlations": {
    "usage_vs_win_pct": 0.35,
    "usage_vs_adj_em": 0.42
  }
}
```

#### Get Utilization Teams
```http
GET /api/v1/utilization/teams
```

**Response:**
```json
{
  "teams": [
    {
      "team": "Duke",
      "avg_usage": 22.5,
      "success_metrics": {...}
    }
  ]
}
```

#### Get Utilization Summary
```http
GET /api/v1/utilization/summary
```

**Response:**
```json
{
  "summary": {
    "avg_usage": 20.3,
    "std_usage": 5.2,
    "correlation_with_success": 0.35
  }
}
```

#### Get Archetype Teams
```http
GET /api/v1/archetype/teams
```

**Response:**
```json
{
  "teams": [
    {
      "team": "Duke",
      "archetype_composition": {...}
    }
  ]
}
```

#### Get Archetype Correlations
```http
GET /api/v1/archetype/correlations
```

**Response:**
```json
{
  "correlations": {
    "archetype_vs_win_pct": 0.28
  }
}
```

#### Get Archetype Summary
```http
GET /api/v1/archetype/summary
```

**Response:**
```json
{
  "summary": {
    "total_teams": 350,
    "archetype_distribution": {...}
  }
}
```

---

### Team Matchups

#### Get Team Matchups
```http
GET /api/v1/teams/{team_id}/matchups
```

**Path Parameters:**
- `team_id` (string) - Team ID

**Query Parameters:**
- `threshold` (float, default: 0.05) - Score threshold for matchups
- `filter_type` (string, default: "all") - Filter type: all, conference, quartile

**Response:**
```json
{
  "team_id": "duke",
  "matchups": [
    {
      "opponent": "North Carolina",
      "score": 0.85,
      "style_compatibility": 0.92
    }
  ]
}
```

#### Get Team Analytics Debug
```http
GET /api/v1/teams/{team_id}/analytics-debug
```

**Path Parameters:**
- `team_id` (string) - Team ID

**Response:**
```json
{
  "team_id": "duke",
  "debug_info": {
    "style_vector": [...],
    "impact_vector": [...]
  }
}
```

#### Get Team vs Opponent Matchup
```http
GET /api/v1/teams/{team_id}/matchup/{opponent_id}
```

**Path Parameters:**
- `team_id` (string) - Team ID
- `opponent_id` (string) - Opponent team ID

**Response:**
```json
{
  "team_id": "duke",
  "opponent_id": "unc",
  "matchup_score": 0.85,
  "style_matchup": 0.92,
  "impact_matchup": 0.78
}
```

#### Get Similar Teams
```http
GET /api/v1/teams/{team_id}/similar
```

**Path Parameters:**
- `team_id` (string) - Team ID

**Query Parameters:**
- `style_weight` (float, default: 0.5) - Weight for style vector (0-1)
- `limit` (int, default: 10) - Maximum number of similar teams

**Response:**
```json
{
  "team_id": "duke",
  "similar_teams": [
    {
      "team": "North Carolina",
      "similarity_score": 0.88
    }
  ]
}
```

---

### Additional Game Endpoints

#### Reload Graph
```http
POST /api/v1/game/reload-graph
```

**Request Body:**
```json
{
  "conferences": ["ACC", "SEC"],
  "years": [2024, 2025, 2026]
}
```

**Response:**
```json
{
  "message": "Graph reloaded successfully",
  "nodes": 15000,
  "edges": 45000
}
```

---

### Moves Rankings

#### Get Move Rankings
```http
GET /api/v1/moves/rankings
```

**Query Parameters:**
- `move_type` (string, required) - Move type (rim_attack, sniper, mid_range, transition, pnr_maestro, post_dominator)
- `year` (string, optional) - Filter by year
- `limit` (int, default: 50, max: 100) - Number of results
- `offset` (int, default: 0) - Pagination offset

**Response:**
```json
{
  "results": [
    {
      "player_key": "123456",
      "player_name": "John Doe",
      "move_type": "rim_attack",
      "ppp": 1.25,
      "usage": 0.35
    }
  ],
  "total": 5000,
  "limit": 50,
  "offset": 0
}
```

---

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-06-08T17:00:00.000000"
}
```

---

## Error Codes

- `400` - Bad Request (invalid parameters)
- `404` - Not Found (resource doesn't exist)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

---

## Data Tiers

The API provides two data tiers:

### Basic Tier
- All players across all years
- Basic statistics (points, rebounds, assists, etc.)
- Standard advanced metrics (BPM, usage rate, etc.)

### Enriched Tier
- Subset of players with detailed tracking data
- Advanced tracking metrics (offensive/defensive breakdowns)
- Granular efficiency metrics
- Additional contextual statistics

---

## Common Fields

### Player Fields
- `player_key` - Unique player identifier
- `player_name` - Player's full name
- `team` - Current team
- `year` - Season year
- `Position` - Player position (PG, SG, SF, PF, C)
- `BPM` - Box Plus Minus
- `PPG` - Points Per Game
- `RPG` - Rebounds Per Game
- `APG` - Assists Per Game
- `Usage` - Usage rate percentage
- `ORtg` - Offensive rating
- `eFG` - Effective field goal percentage

### Team Fields
- `Team` - Team name
- `Conference` - Conference affiliation
- `year` - Season year
- `adj_em` - Adjusted efficiency margin
- `adj_o` - Adjusted offensive efficiency
- `adj_d` - Adjusted defensive efficiency

# Analytics and Model Calculations

## Overview

This document provides in-depth explanations of the analytics, metrics, and machine learning models used in JEEVS CBB. It covers the mathematical derivations, methodologies, and implementation details for each calculation.

---

## Table of Contents

1. [Box Plus Minus (BPM)](#box-plus-minus-bpm)
2. [Player Clustering](#player-clustering)
3. [Similarity Scoring](#similarity-scoring)
4. [BPM Projections](#bpm-projections)
5. [Usage Rate Analysis](#usage-rate-analysis)
6. [Player Development Tracking](#player-development-tracking)
7. [NIL Valuation Model](#nil-valuation-model)
8. [Badge System](#badge-system)
9. [Cluster Transitions](#cluster-transitions)

---

## Box Plus Minus (BPM)

### Definition

Box Plus Minus (BPM) is an advanced basketball metric that estimates a player's contribution to their team's performance per 100 possessions, measured in points above or below an average player.

### Source

BPM values are sourced from Bart Torvik, which calculates BPM using a regression-based approach on box score statistics.

### Calculation Method

The BPM calculation uses a linear regression model with the following components:

**Offensive BPM (OBPM):**
```
OBPM = w1 * (PPG) + w2 * (AST) + w3 * (ORB) + w4 * (TOV) + w5 * (eFG%) + w6 * (FT%) + intercept
```

**Defensive BPM (DBPM):**
```
DBPM = w1 * (DRB) + w2 * (STL) + w3 * (BLK) + w4 * (PF) + w5 * (DRTG) + intercept
```

**Total BPM:**
```
BPM = OBPM + DBPM
```

### Weights and Coefficients

The exact weights are proprietary to Bart Torvik, but the general approach:

- **Scoring:** Points per game, weighted by efficiency
- **Playmaking:** Assists, weighted by turnover rate
- **Rebounding:** Offensive and defensive rebounds
- **Defense:** Steals, blocks, personal fouls
- **Efficiency:** eFG%, FT%, usage rate

### Interpretation

- **BPM > 10:** Elite player (All-American level)
- **BPM 5-10:** Above average starter
- **BPM 0-5:** Rotation player
- **BPM < 0:** Below average
- **BPM < -5:** Replacement level

### Usage in JEEVS CBB

- Primary sorting metric for leaderboards
- Used in similarity calculations
- Key feature in projection models
- Basis for cluster analysis

---

## Player Clustering

### Overview

Player clustering groups players with similar statistical profiles using unsupervised machine learning. This enables style-based player comparisons and analysis.

### Methodology

**Algorithm:** K-Means Clustering

**Number of Clusters:** 18 (cluster IDs 0-17)

**Features Used:**
1. BPM (overall value)
2. Usage rate (role)
3. eFG% (scoring efficiency)
4. AST% (playmaking)
5. ORB% (offensive rebounding)
6. DRB% (defensive rebounding)
7. STL% (stealing)
8. BLK% (shot blocking)
9. TOV% (turnover rate)
10. FTR (free throw rate)

### Preprocessing

1. **Normalization:**
   - All features standardized to mean=0, std=1
   - Ensures equal weighting across features
   - Formula: `z = (x - μ) / σ`

2. **Feature Selection:**
   - Remove highly correlated features (|r| > 0.8)
   - Retain most representative metrics
   - Focus on rate statistics rather than totals

3. **Outlier Handling:**
   - Cap extreme values at 99th percentile
   - Prevents outliers from dominating clusters
   - Maintains cluster stability

### Cluster Determination

**Optimal Cluster Count:** 18 clusters (IDs 0-17)

**Process:**
1. Run K-means clustering on normalized player statistics
2. Determine optimal k using the Elbow Method
3. Validate cluster quality using silhouette score
4. Assign cluster labels to all players

**Cluster Descriptions:**
Cluster descriptions are loaded from `cluster_descriptions.json` and provide detailed information about each cluster's characteristics, average BPM, and player count. Use the `/api/v1/clusters/descriptions` endpoint to retrieve cluster information.

### Implementation

**File:** `backend/scripts/modeling/cluster_players.py`

**Key Steps:**
```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Normalize features
scaler = StandardScaler()
X_normalized = scaler.fit_transform(X)

# Fit K-means
kmeans = KMeans(n_clusters=8, random_state=42)
clusters = kmeans.fit_predict(X_normalized)

# Assign cluster labels
df['cluster'] = clusters
```

### Validation

**Silhouette Score:** ~0.45 (moderate clustering quality)

**Cluster Stability:**
- Re-run clustering with different random seeds
- Compare cluster assignments
- >85% consistency across runs

**Interpretability:**
- Each cluster has distinct statistical profile
- Clusters align with basketball positions/roles
- Meaningful for player comparisons

---

## Similarity Scoring

### Overview

Similarity scoring quantifies how similar two players are based on their statistical profiles. It's used for the "Similar Players" feature and Similarity Map visualization.

### Methodology

**Algorithm:** Cosine Similarity on normalized feature vectors

### Feature Vector Construction

**Components:**
1. **Style Metrics (weight: 0.7):**
   - Usage rate
   - Assist rate
   - Rebound rate (ORB% + DRB%)
   - Scoring efficiency (eFG%)
   - Turnover rate
   - Free throw rate

2. **Production Metrics (weight: 0.3):**
   - BPM
   - PPG
   - RPG
   - APG

**Normalization:**
- Each feature normalized to [0, 1] range
- Min-max scaling: `x_norm = (x - min) / (max - min)`
- Ensures features contribute equally

### Similarity Calculation

**Cosine Similarity:**
```
similarity(A, B) = (A · B) / (||A|| * ||B||)
```

Where:
- `A · B` = dot product of vectors
- `||A||` = magnitude of vector A
- `||B||` = magnitude of vector B

**Range:** [-1, 1], where 1 = identical, 0 = orthogonal, -1 = opposite

**Weighted Similarity:**
```
final_similarity = 0.7 * style_similarity + 0.3 * production_similarity
```

### Implementation

**File:** `backend/app/services/similarity_service.py`

**Caching:**
- Precompute similarity vectors for all players
- Cache in pickle format for fast loading
- Update weekly during season

**Nearest Neighbor Search:**
```python
from sklearn.neighbors import NearestNeighbors

# Fit nearest neighbors model
nn = NearestNeighbors(n_neighbors=20, metric='cosine')
nn.fit(vectors)

# Find neighbors
distances, indices = nn.kneighbors([query_vector])
```

### Performance Optimization

**Vector Precomputation:**
- Compute feature vectors for all players at startup
- Store in memory for O(1) access
- Reduces computation time from O(n) to O(1)

**Dimensionality Reduction (Optional):**
- PCA to reduce from 10D to 3D for visualization
- Maintains ~80% variance explained
- Used for Similarity Map 2D projection

### Interpretation

**Similarity Score Ranges:**
- **0.9-1.0:** Nearly identical profiles
- **0.8-0.9:** Very similar
- **0.7-0.8:** Similar
- **0.6-0.7:** Moderately similar
- **0.5-0.6:** Somewhat similar
- **<0.5:** Not similar

---

## BPM Projections

### Overview

BPM projections estimate a player's future BPM based on historical performance, age, and contextual factors. Used for 2027 season projections.

### Methodology

**Algorithm:** Random Forest Regression

### Features

**Player Performance Features:**
1. Previous season BPM
2. BPM change from prior season (ΔBPM)
3. Age
4. Usage rate
5. eFG%
6. AST%
7. ORB% + DRB%
8. STL% + BLK%
9. TOV%
10. Minutes per game

**Contextual Features:**
1. Team efficiency margin (adj_em)
2. Conference strength
3. Transfer status (portal transfer?)
4. Year in school (FR, SO, JR, SR)
5. Recruiting ranking (if available)

### Feature Engineering

**Age-Adjusted Performance:**
```
age_adj_bpm = BPM + (age - 22) * 0.5
```
Adjusts BPM based on typical age curve (players peak at ~22-23)

**Usage-Efficiency Interaction:**
```
usage_eff = usage_rate * eFG%
```
Captures players who maintain efficiency at high usage

**Team Context:**
```
team_adj = BPM * (team_adj_em / league_avg_adj_em)
```
Adjusts for team quality

### Model Training

**Training Data:**
- Historical player data (2019-2025)
- Year-over-year BPM changes
- ~10,000 player-season observations

**Validation:**
- 5-fold cross-validation
- Holdout test set (20%)
- Time-series split (train on past, test on future)

**Hyperparameters:**
```python
n_estimators = 100
max_depth = 10
min_samples_split = 5
min_samples_leaf = 2
random_state = 42
```

### Model Performance

**Metrics:**
- **R²:** 0.45 (explains 45% of variance)
- **RMSE:** 1.8 BPM
- **MAE:** 1.4 BPM

**Feature Importance:**
1. Previous season BPM (35%)
2. Age (20%)
3. Usage rate (15%)
4. BPM change (10%)
5. Team context (8%)
6. Other features (12%)

### Projection Formula

**Base Projection:**
```
projected_bpm = model.predict(features)
```

**Confidence Interval:**
```
ci = 1.96 * rmse * sqrt(1 + 1/n)
```
Where n = sample size for similar players

**Age Adjustment:**
```
final_bpm = projected_bpm + age_curve(age)
```

**Age Curve:**
- Age 18-20: +0.5 BPM per year (development)
- Age 21-23: +0.2 BPM per year (peak)
- Age 24+: -0.3 BPM per year (decline)

### Implementation

**File:** `backend/scripts/modeling/train_bpm_projection_model.py`

**Usage:**
```python
from app.services.projection_service import get_projection_service

service = get_projection_service()
projections = service.get_2027_projections()
```

### Validation

**Backtesting:**
- Train on 2019-2024, test on 2025
- Compare projected vs actual BPM
- R² = 0.42 on holdout set

**Calibration:**
- Check if projections are unbiased
- Mean error ≈ 0
- Errors normally distributed

---

## Usage Rate Analysis

### Definition

Usage rate estimates the percentage of team possessions a player uses while on the court, either through shots, free throws, or turnovers.

### Calculation

**Formula (from basketball-reference):**
```
Usage = (FGA + 0.44 * FTA + AST + TOV) / (Team FGA + 0.44 * Team FTA + Team AST)
```

**Components:**
- FGA: Field goal attempts
- FTA: Free throw attempts
- AST: Assists
- TOV: Turnovers
- Team totals: Sum for team while player is on court

### Interpretation

**Usage Ranges:**
- **>30%:** Alpha scorer, primary option
- **25-30%:** High usage, secondary option
- **20-25%:** Above average, role player
- **15-20%:** Average usage
- **<15%:** Low usage, role player

### Usage Efficiency

**Usage-Efficiency Curve:**
```
efficiency = eFG% - (usage_rate - 20) * 0.005
```
Adjusts efficiency based on usage (higher usage typically lower efficiency)

### Implementation

**File:** `backend/app/services/utilization_service.py`

**Features:**
- Calculate usage rate for each player
- Track usage changes over time
- Identify usage outliers

---

## Player Development Tracking

### Overview

Player development tracking analyzes how players improve or decline over time, identifying trends and factors affecting development.

### Metrics Tracked

**Year-Over-Year Changes:**
1. ΔBPM (BPM change)
2. ΔUsage (usage rate change)
3. ΔeFG% (efficiency change)
4. ΔAST% (playmaking change)
5. ΔREB% (rebounding change)

### Development Classifications

**Breakout Players:**
- ΔBPM > +3
- Significant improvement in multiple metrics
- Often younger players (FR/SO)

**Steady Improvers:**
- ΔBPM +1 to +3
- Consistent improvement
- Reliable development

**Plateaued:**
- ΔBPM -1 to +1
- Little change
- Often older players (SR)

**Declining:**
- ΔBPM < -1
- Performance drop
- Age-related or injury-related

### Factors Affecting Development

**Age:**
- Younger players show more improvement
- Peak age: 22-23
- Decline starts at 24+

**Usage:**
- Increased usage often leads to efficiency drop
- Usage management important for development

**Team Context:**
- Better teams develop players better
- Coaching quality affects development
- Role clarity important

**Transfer Impact:**
- Portal transfers show mixed results
- Some improve, some decline
- Context change is key factor

### Implementation

**File:** `backend/scripts/analysis/analyze_bpm_change.py`

**Analysis:**
```python
# Calculate year-over-year changes
df['bpm_change'] = df.groupby('player_key')['BPM'].diff()

# Classify development
def classify_development(row):
    if row['bpm_change'] > 3:
        return 'breakout'
    elif row['bpm_change'] > 1:
        return 'improver'
    elif row['bpm_change'] > -1:
        return 'plateaued'
    else:
        return 'declining'
```

---

## NIL Valuation Model

### Overview

NIL (Name, Image, Likeness) valuation estimates a player's market value based on performance, market size, and social media presence.

### Methodology

**Algorithm:** Weighted scoring model with percentile-based normalization

### Components

**NIL Score Weights:**
- Position Rank (within cluster): 25%
- Win Shares Percentile: 20%
- BPM Percentile: 15%
- Team Success: 10%
- Conference Prestige: 10%
- Cluster Quality: 20%

### Features

**Performance Features:**
1. **Position Rank:** BPM percentile within player's cluster (18 clusters, IDs 0-17)
2. **Win Shares:** Total Win Shares percentile vs all players with meaningful minutes (MPG > 5)
3. **BPM:** Box Plus Minus percentile vs all players with meaningful minutes and BPM data
4. **Cluster Quality:** Quality score based on cluster's average BPM (0.15 to 1.0)

**Context Features:**
1. **Team Success:** Based on adjusted net rating (adj_net), normalized to 0-100 scale
2. **Conference Prestige:** Conference tier multiplier (High Major: 1.0, Mid Major: 0.7, Low Major: 0.4)

### Cluster Quality Mapping

Clusters are ranked by average BPM:
- **Cluster 2** (Elite Bigs): 1.0 (BPM 5.04)
- **Cluster 0** (High-Usage Guards): 0.95 (BPM 4.79)
- **Cluster 6** (3PT Wings): 0.9 (BPM 2.52)
- **Cluster 11** (Stretch Bigs): 0.85 (BPM 2.41)
- **Cluster 13** (Versatile Forwards): 0.8 (BPM 2.37)
- **Cluster 9** (High-Usage Guards): 0.75 (BPM 2.16)
- **Cluster 12** (Playmakers): 0.7 (BPM 1.95)
- **Cluster 15** (Rim Protectors): 0.65 (BPM 0.02)
- **Cluster 3** (Wings): 0.6 (BPM -0.29)
- **Cluster 14** (Low BPM Guards): 0.55 (BPM -0.41)
- **Cluster 8** (3PT Specialists): 0.5 (BPM -0.80)
- **Cluster 1** (Low BPM Forwards): 0.45 (BPM -2.10)
- **Cluster 17** (Low BPM Bigs): 0.4 (BPM -2.49)
- **Cluster 5** (Traditional Bigs): 0.35 (BPM -3.21)
- **Cluster 16** (High-Usage Low BPM): 0.3 (BPM -3.22)
- **Cluster 10** (Empty Calorie): 0.25 (BPM -3.44)
- **Cluster 7** (Low BPM Wings): 0.2 (BPM -3.89)
- **Cluster 4** (Very Low BPM): 0.15 (BPM -6.45)

### Conference Prestige Mapping

**High Major (1.0):**
- ACC, Big 12, Big Ten, SEC, Big East, Pac 12, West Coast Conference

**Mid Major (0.7):**
- AAC, A-10, Mountain West, MVC, WCC, Big West, Conference USA

**Low Major (0.4):**
- All other conferences

### Calculation

**NIL Score Formula:**
```
nil_score = (position_rank * 0.25) +
            (win_shares_percentile * 0.20) +
            (bpm_percentile * 0.15) +
            (team_success * 0.10) +
            (conference_prestige * 100 * 0.10) +
            (cluster_quality * 100 * 0.20)
```

**VORP Calculation:**
```
vorp = (BPM - (-2.0)) * (MPG / 40.0) * (Games / 33.0)
```

### Dollar Conversion

**Score to Dollar Ranges:**
- **95-100 score:** $2M - $5M (elite players)
- **90-95 score:** $1M - $2M (star players)
- **70-90 score:** $100K - $500K (good players)
- **50-70 score:** $10K - $100K (average players)
- **0-50 score:** $0 - $10K (below average)

### Implementation

**File:** `backend/app/services/nil_service.py`

**Key Methods:**
- `calculate_player_nil()` - Calculate NIL valuation for a specific player
- `calculate_team_nil()` - Calculate NIL valuations for all players on a team
- `get_all_nil_valuations()` - Get NIL valuations with filtering and sorting

**Data Sources:**
- Player data from main dataframe
- Cluster assignments from `player_clusters_unified.csv`
- Team data from hoop-explorer teams CSV

**Limitations:**
- Social media data not included
- Market estimates are approximate
- NIL market is rapidly evolving
- Local deals not captured
- Conference name variations handled with case-insensitive matching

---

## Player Evolution

### Overview

Player evolution tracks how players develop over multiple seasons, showing changes in key metrics and performance tiers.

### Methodology

**Algorithm:** Historical data aggregation with percentile-based tiering

### Features

**Metrics Tracked:**
- BPM (Box Plus Minus)
- RAPM (Regularized Adjusted Plus Minus)
- VORP (Value Over Replacement Player)
- Combined score

**Tiering System:**
Players are assigned tiers based on their percentile performance:
- **Elite:** Top 10%
- **Star:** 10-25%
- **Starter:** 25-50%
- **Bench:** 50-75%
- **Replacement:** Bottom 25%

### Implementation

**File:** `backend/app/services/evolution_service.py`

**API Endpoint:** `GET /api/v1/players/{ncaa_id}/evolution`

**Data Sources:**
- Historical player data across all years
- Percentile calculations for tiering

---

## Radar Charts

### Overview

Radar charts provide a visual representation of a player's strengths across multiple dimensions, allowing for quick comparison of player profiles.

### Methodology

**Algorithm:** Normalized feature scaling across multiple dimensions

### Dimensions

**Common Presets:**
- **Overview:** Scoring, playmaking, rebounding, defense, efficiency
- **Offensive:** Scoring, playmaking, efficiency, usage, shooting
- **Defensive:** Rim protection, perimeter defense, rebounding, steals, blocks
- **Complete:** All available metrics

### Calculation

Each dimension is normalized to a 0-100 scale based on percentile performance relative to all players in the same year with meaningful minutes.

### Implementation

**File:** `backend/app/features/radar.py`

**API Endpoint:** `GET /api/v1/players/{ncaa_id}/radar`

**Parameters:**
- `preset` - Radar preset name (overview, offensive, defensive, complete)
- `custom_fields` - Array of custom field names for custom radar

---

## Feature Vectors

### Overview

Feature vectors are high-dimensional representations of player statistical profiles used for similarity calculations and machine learning tasks.

### Methodology

**Algorithm:** Normalized feature extraction and vectorization

### Vector Components

**Style Features:**
- Scoring profile (PPG, eFG%, usage rate)
- Playmaking (AST%, assist rate)
- Rebounding (ORB%, DRB%, TRB%)
- Defense (STL%, BLK%, DBPM)
- Efficiency (TS%, ORtg)

**Production Features:**
- BPM, VORP
- Minutes played
- Team context

### Normalization

All features are normalized to [0, 1] range using min-max scaling to ensure equal contribution to similarity calculations.

### Implementation

**File:** `backend/app/features/vectors.py`

**Usage:**
- Similarity search
- Clustering
- Machine learning model inputs

---

## Moves Analysis

### Overview

Moves analysis evaluates player efficiency by offensive move type, providing insights into scoring efficiency and usage patterns.

### Move Types

**Primary Move Types:**
- **Rim Attack:** Finishing at the basket
- **Sniper:** Three-point shooting
- **Mid Range:** Mid-range jump shots
- **Transition:** Fast break scoring
- **PnR Maestro:** Pick-and-roll playmaking
- **Post Dominator:** Post-up scoring

### Metrics

**Key Metrics:**
- **PPP (Points Per Possession):** Efficiency metric for each move type
- **Usage Rate:** Percentage of possessions using each move type
- **Volume:** Number of attempts per game

### Calculation

```
move_score = usage * ppp
```

Players are ranked by their efficiency (PPP) and volume (usage) for each move type.

### Implementation

**File:** `backend/app/features/moves.py`

**API Endpoints:**
- `GET /api/v1/players/{ncaa_id}/moves` - Get player move data
- `GET /api/v1/moves/rankings` - Get rankings by move type

**Data Sources:**
- Synergy-style tracking data
- Shot location data
- Play-by-play data

---

## Badge System

### Overview

Badges are awarded to players based on achieving specific statistical thresholds or performance criteria. They provide quick visual indicators of player strengths.

### Badge Categories

**Scoring Badges:**
- Deadeye
- True Sniper
- Microwave Scorer
- Movement Shooter
- Shot Architect
- Midrange Magician
- Rim Attacker
- Fastbreak Phenom

**Big Man Badges:**
- Lob Threat
- Paint Punisher
- Pick & Pop

**Playmaking Badges:**
- PnR Maestro
- Drive & Dish Dynamo
- Floor General
- Tempo Controller

**IQ Badges:**
- Backdoor Bandit
- Off-Ball Savant

**Defense Badges:**
- Rim Protector
- Pickpocket
- Perimeter Lock
- Interior Anchor

**Hustle Badges:**
- Glass Cleaner
- Second Chance King

**Role Badges:**
- Offensive Engine
- Elite Finisher
- Primary Creator
- Iron Man

**Rare Badges:**
- Unicorn
- Two-Way Star
- Chaos Agent

### Badge Levels

Badges are assigned levels 0-5 based on percentile performance:

- **Level 5:** > 97th percentile (elite)
- **Level 4:** > 95th percentile (excellent)
- **Level 3:** > 90th percentile (very good)
- **Level 2:** > 85th percentile (good)
- **Level 1:** > 80th percentile (above average)
- **Level 0:** ≤ 80th percentile (not awarded)

### Badge Calculation

Most badges use a usage-filtered score that combines:
- Usage rate (minimum 30% usage required)
- Points per possession (PPP)
- Percentile performance in specific play types

Special badges have custom calculations:
- **True Sniper:** Requires 100+ 3PA, dynamic efficiency thresholds based on volume
- **Microwave Scorer:** Combines scoring load, usage, and true shooting
- **Iron Man:** Based on minutes played, games played, and start rate

### Implementation

**File:** `backend/app/features/badges.py`

**Badge Assignment:**
```python
def assign_badges(player_stats):
    badges = []
    
    # Check scoring badges
    if player_stats['PPG'] > 20 and player_stats['eFG'] > 0.55:
        badges.append({'name': 'Elite Scorer', 'tier': 'gold'})
    
    # Check playmaking badges
    if player_stats['AST%'] > 30 and player_stats['TOV%'] < 15:
        badges.append({'name': 'Elite Playmaker', 'tier': 'gold'})
    
    # ... (continue for all badges)
    
    return badges
```

---

## Cluster Transitions

### Overview

Cluster transition analysis tracks how players move between statistical clusters over time, identifying development patterns and archetype changes.

### Transition Matrix

**Matrix Structure:**
- Rows: Starting cluster (year N)
- Columns: Ending cluster (year N+1)
- Values: Probability of transition

**Example:**
```
          C1    C2    C3    C4    C5    C6    C7    C8
C1      0.60  0.15  0.10  0.05  0.05  0.03  0.01  0.01
C2      0.10  0.50  0.20  0.05  0.08  0.05  0.01  0.01
...
```

### Common Transition Patterns

**Development Paths:**
1. **Specialist → Role Player → Starter:**
   - C7 → C6 → C4/C5
   - Typical development for young players

2. **Role Player → Elite:**
   - C6 → C3 → C1
   - Breakout development

3. **Elite → Elite:**
   - C1 → C1
   - Sustained excellence

4. **Decline Paths:**
   - C1 → C3 → C6
   - Age-related decline
   - C2 → C7
   - Loss of role

### Factors Influencing Transitions

**Age:**
- Younger players more likely to move up clusters
- Older players more likely to move down

**Usage Changes:**
- Increased usage often leads to cluster changes
- Role changes affect statistical profile

**Team Context:**
- Better teams enable better development
- Role clarity affects cluster stability

**Transfers:**
- Portal transfers often lead to cluster changes
- New system = new role = new cluster

### Implementation

**File:** `backend/scripts/analysis/analyze_cluster_transitions.py`

**Analysis:**
```python
# Build transition matrix
transition_matrix = np.zeros((8, 8))

for player in players:
    for year in range(2019, 2026):
        current_cluster = get_cluster(player, year)
        next_cluster = get_cluster(player, year + 1)
        transition_matrix[current_cluster][next_cluster] += 1

# Normalize to probabilities
transition_matrix = transition_matrix / transition_matrix.sum(axis=1, keepdims=True)
```

---

## Statistical Validation

### Cross-Validation

All models use k-fold cross-validation (k=5) to ensure robustness and prevent overfitting.

### Backtesting

Historical data is used to validate model predictions:
- Train on 2019-2024 data
- Test on 2025 data
- Compare predicted vs actual
- Calculate R², RMSE, MAE

### Model Comparison

Multiple models are compared:
- Linear regression
- Random forest
- Gradient boosting
- Neural networks

Best model selected based on:
- Predictive accuracy (R²)
- Interpretability
- Computational efficiency

### Continuous Improvement

Models are retrained:
- End of each season
- When new data becomes available
- If performance degrades

---

## References

1. **Bart Torvik** - BPM calculation methodology
2. **Basketball Reference** - Advanced metrics definitions
3. **Kubatko et al.** - Basketball analytics research
4. **Scikit-learn Documentation** - Machine learning algorithms
5. **NBA Analytics** - Similarity and clustering approaches

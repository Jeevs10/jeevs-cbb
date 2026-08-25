# Technical Architecture & Implementation

## Executive Summary

JEEVS CBB is a full-stack college basketball analytics platform built with a Python FastAPI backend and Next.js TypeScript frontend. The system aggregates data from multiple sources, applies machine learning models for player analysis, and provides interactive visualizations. This document focuses on the backend architecture, data processing pipeline, and technical implementation details.

---

## Backend Technology Stack

### Core Framework

**FastAPI** - Modern, fast web framework for building APIs
- Async/await support for high performance
- Automatic API documentation (Swagger/ReDoc)
- Pydantic integration for data validation
- Built-in type hints and IDE support

**Uvicorn** - ASGI server
- Lightning-fast ASGI implementation
- Hot reload in development
- Production-ready with proper configuration

### Data Processing

**Pandas** - Data manipulation and analysis
- DataFrame operations for player/team statistics
- CSV/JSON data loading with compression support
- Data joining across multiple sources
- Statistical calculations and aggregations

**NumPy** - Numerical computing
- Vector operations for similarity calculations
- Array manipulations for ML features
- Statistical computations

### Machine Learning

**Scikit-learn** - Machine learning library
- KMeans clustering for player archetypes
- RandomForest regression for BPM projections
- StandardScaler for feature normalization
- NearestNeighbors for similarity search

**NetworkX** - Graph algorithms
- Player teammate relationship graph
- Shortest path calculations (PORTALMANIA game)
- BFS for efficient graph traversal

### Data Validation & Configuration

**Pydantic** - Data validation using Python type annotations
- Request/response schema validation
- Configuration management with pydantic-settings
- Automatic type conversion and error handling

**python-dotenv** - Environment variable management
- Load configuration from .env files
- Separate dev/prod configurations

### Caching & Performance

**Pickle** - Python object serialization
- Cache precomputed similarity vectors
- Store player feature vectors for fast lookup
- Cache invalidation based on file modification times

**Gzip** - Data compression
- Compress CSV files (70-80% reduction)
- Compress JSON game data (85% reduction)
- Pandas native support for reading compressed files

### API Features

**Slowapi** - Rate limiting
- Prevent API abuse
- Configurable rate limits per endpoint
- Redis-compatible (for distributed systems)

---

## Frontend Technology Stack

### Core Framework

**Next.js 14** - React framework for production applications
- Server-side rendering (SSR) for improved SEO and performance
- Static site generation (SSG) for optimized page loads
- File-based routing for intuitive navigation
- API routes for backend integration
- Built-in optimization and code splitting

**React 18** - UI library
- Component-based architecture
- Hooks for state management and side effects
- Virtual DOM for efficient rendering
- Context API for global state (YearContext)

**TypeScript** - Type-safe JavaScript
- Static type checking for fewer runtime errors
- Enhanced IDE support with autocomplete
- Interface definitions for API responses
- Type-safe component props

### Styling & UI

**Tailwind CSS** - Utility-first CSS framework
- Rapid UI development with pre-built classes
- Consistent design system across components
- Responsive design utilities
- Custom color palette matching brand identity

**clsx** - Conditional className utility
- Dynamic class name construction
- Conditional styling based on component state
- Lightweight alternative to classnames

**Lucide React** - Icon library
- Consistent icon set throughout application
- Tree-shakeable for minimal bundle size
- Customizable stroke and fill properties

### Data Visualization

**Recharts** - Charting library
- Player progression charts (BPM over time)
- Cluster distribution visualizations
- Radar charts for player comparison
- Responsive and customizable components

**React Simple Maps** - Geographic visualization
- Player origin/hometown mapping
- Team location visualization
- Custom SVG map components
- Lightweight compared to full mapping libraries

**Leaflet & React Leaflet** - Interactive maps
- Team location panels
- Player hometown visualization
- Interactive map controls
- Custom markers and popups

### 3D Graphics

**Three.js** - 3D graphics library
- WebGL rendering for 3D visualizations
- Performance-optimized graphics
- Extensive 3D capabilities

**React Three Fiber** - React renderer for Three.js
- Declarative 3D components in React
- Integration with React ecosystem
- Reusable 3D scene components

**React Three Drei** - Helpers for React Three Fiber
- Pre-built 3D components (controls, loaders)
- Camera controls and orbit helpers
- Environment and lighting utilities

### Animations & Interactions

**Framer Motion** - Animation library
- Smooth page transitions
- Component animations on mount/unmount
- Gesture-based interactions
- Performance-optimized animations

### Utilities

**dom-to-image / html2canvas / modern-screenshot** - Screenshot utilities
- Export player reports as images
- Capture visualizations for sharing
- Multiple screenshot implementations for compatibility

### Development & Testing

**Jest** - JavaScript testing framework
- Unit testing for components and hooks
- Snapshot testing for UI consistency
- Mock capabilities for API calls

**Testing Library** - React component testing
- User-centric testing approach
- Accessible component queries
- Integration with Jest

**ESLint & Prettier** - Code quality tools
- Linting for code consistency
- Automatic code formatting
- TypeScript-specific rules

---

## Architecture Overview

### Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                    │
│  - Route handlers (/api/v1/players, /api/v1/teams, etc) │
│  - Request validation (Pydantic schemas)                 │
│  - Response formatting                                   │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                  Service Layer                            │
│  - Business logic (PlayerService, TeamService, etc)       │
│  - Data transformation                                    │
│  - Feature calculations                                   │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                  Core Layer                              │
│  - Data loading (data_loader.py)                         │
│  - Player/team resolvers                                 │
│  - Graph operations (player_graph.py)                    │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                  Feature Layer                            │
│  - Vector building (vectors.py)                          │
│  - Badge calculations (badges.py)                        │
│  - Radar chart data (radar.py)                           │
│  - Moves analysis (moves.py)                             │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                  Cache Layer                             │
│  - Player vectors cache (player_vectors.py)              │
│  - Pickle serialization                                  │
│  - Cache invalidation logic                              │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                  Data Layer                              │
│  - CSV files (compressed with gzip)                      │
│  - JSON game data (compressed)                           │
│  - Cluster assignments                                   │
│  - Projection data                                       │
└─────────────────────────────────────────────────────────┘
```

---

## Data Pipeline Architecture

### 1. Data Ingestion

**Sources:**
- **Bart Torvik** (barttorvik.com): BPM, advanced metrics, team efficiency
- **Hoop Explorer** (hoop-explorer.com): RAPM, roster info, biographical data
- **College Basketball Data** (collegebasketballdata.com): Game-by-game data, schedules

**Processing Scripts:** `backend/scripts/data_processing/`

**Key Scripts:**
- `link_player_ids.py` - Links player IDs across sources
- `process_*_game_data.py` - Processes game data for each year
- `build_year_over_year_dataset.py` - Creates YoY change datasets
- `analyze_bpm_change.py` - Analyzes BPM changes for projections

### 2. Data Loading Strategy

**File:** `backend/app/core/data_loader.py`

**Three-Tier Data Loading:**

```python
# Tier 1: Basic Players (complete coverage, ~15,000 players)
def load_basic_players():
    # Loads {year}-players_basic.csv
    # Fields: Name, Team, Conference, Position, basic stats
    # Coverage: All D1 players, all years (2019-2026)

# Tier 2: Enriched Players (subset, advanced metrics)
def load_enriched_players():
    # Loads {year}-players_enriched.csv
    # Fields: RAPM, tracking data, advanced efficiency metrics
    # Coverage: ~60% of players with tracking data

# Tier 3: Torvik Data (BPM and advanced stats)
def load_torvik_players():
    # Loads {year}_torvik.csv
    # Fields: BPM, OBPM, DBPM, usage rates, efficiency metrics
    # Coverage: Most players, all years
```

**Data Joining Strategy:**

```python
def load_all_players():
    # 1. Load basic players as base (complete coverage)
    basic_df = load_basic_players()
    
    # 2. Join roster info (height, weight, hometown)
    roster_df = load_roster_info()
    basic_df = merge(basic_df, roster_df, on='AthleteSourceId')
    
    # 3. Join enriched data (advanced metrics)
    enriched_df = load_enriched_players()
    # Enriched data takes precedence where available
    
    # 4. Join Torvik data (BPM, advanced stats)
    torvik_df = load_torvik_players()
    # Merge BPM and Torvik-specific metrics
    
    # 5. Combine with deduplication
    combined = concat_and_deduplicate(basic_df, enriched_df)
    combined = merge(combined, torvik_df)
    
    return combined
```

**Compression Handling:**

```python
def read_csv_with_compression(csv_path: Path) -> pd.DataFrame:
    # Automatically detects and reads .csv.gz files
    gz_path = csv_path.with_suffix('.csv.gz')
    
    if gz_path.exists():
        return pd.read_csv(gz_path, compression='gzip')
    elif csv_path.exists():
        return pd.read_csv(csv_path)
    else:
        return pd.DataFrame()
```

### 3. Caching Strategy

**File:** `backend/app/cache/player_vectors.py`

**Two-Pass Cache Building:**

```python
def build_cache():
    # Pass 1: Collect all metric values for percentile calculations
    for row in df.iterrows():
        collect_rapm_values(row)
        collect_bpm_values(row)
        collect_vorp_values(row)
    
    # Pass 2: Build vectors with percentile normalization
    for row in df.iterrows():
        style_vec = build_style_vector(row)
        impact_vec = build_impact_vector(row)
        
        # Calculate percentiles using collected values
        rapm_pct = percentile_rank(row['rapm'], ALL_RAPM_VALUES)
        bpm_pct = percentile_rank(row['bpm'], ALL_BPM_VALUES)
        
        PLAYER_VECTORS[ncaa_id][year] = {
            'style': style_vec,
            'impact': impact_vec,
            'rapm_pct': rapm_pct,
            'bpm_pct': bpm_pct,
            # ...
        }
    
    # Save to disk with metadata
    save_cache()
```

**Cache Invalidation:**

```python
def is_cache_valid():
    # Compare data file modification times
    cached_mod_times = load_metadata()
    current_mod_times = get_file_mod_times()
    
    for file_path, cached_time in cached_mod_times.items():
        if current_mod_times[file_path] > cached_time:
            return False  # Data changed, rebuild cache
    
    return True
```

**Cache Validity Rules:**

**Current Implementation:**
- File modification time-based invalidation
- Tracks 11 specific data files
- Rebuilds entire cache if any tracked file changes
- No time-based expiration (cache persists indefinitely if data unchanged)

**Tradeoffs:**
- **Pros:** Simple to implement, ensures data consistency, no stale data
- **Cons:** Coarse-grained invalidation (rebuilds entire cache for single file change), no partial cache updates, no time-based refresh for slowly changing data

**Improvements:**
1. **Granular Cache Invalidation:**
   - Split cache into independent modules (player vectors, cluster data, projection data)
   - Track dependencies between cache modules
   - Only rebuild affected modules when data changes
   - Example: If only 2026 player data changes, only rebuild 2026 vectors

2. **Time-Based Expiration:**
   - Add TTL (time-to-live) for different cache types
   - Player vectors: 7 days (stats change weekly)
   - Cluster data: 30 days (stable archetypes)
   - Projection data: 90 days (pre-season calculations)
   - Allows periodic refreshes even without data changes

3. **Version-Based Invalidation:**
   - Add data version hash to cache metadata
   - Compute hash from data file contents (not just modification time)
   - Detects data changes even if modification time is reset
   - More reliable than file timestamps

4. **Partial Cache Updates:**
   - Implement incremental cache updates
   - Only recompute vectors for changed players
   - Maintain cache index for fast lookups
   - Reduces rebuild time from O(n) to O(Δn)

5. **Distributed Caching:**
   - Move from local pickle to Redis
   - Share cache across multiple API instances
   - Implement cache warming on startup
   - Add cache metrics (hit rate, miss rate, size)

**Preloading vs Real-Time Computation Decisions:**

**Preloaded Data (Loaded at Startup):**
- **Player vectors:** All players, all years
  - **Rationale:** Used frequently (similarity search, radar charts), expensive to compute (percentile calculations across all players)
  - **Size:** ~50MB in memory
  - **Access pattern:** O(1) lookups, high frequency

- **Cluster assignments:** All players, current year
  - **Rationale:** Used for NIL valuation, projections, player comparisons
  - **Size:** ~5MB in memory
  - **Access pattern:** O(1) lookups, medium frequency

- **Player graph:** All players, all years
  - **Rationale:** Used for PORTALMANIA game, teammate relationships
  - **Size:** ~100MB in memory
  - **Access pattern:** Graph traversals, medium frequency

**Real-Time Computed Data (Loaded on Demand):**
- **Game data:** Per year, per player
  - **Rationale:** Large dataset (~50,000 games), accessed infrequently (only when viewing specific player's game log)
  - **Size:** ~100MB compressed per year
  - **Access pattern:** Sequential reads, low frequency per player

- **Projection data:** 2027 projections
  - **Rationale:** Computed pre-season, changes rarely, only accessed on projection leaderboard
  - **Size:** ~1MB
  - **Access pattern:** Bulk reads, low frequency

- **NIL valuations:** All players
  - **Rationale:** Computed on-demand, depends on multiple data sources, accessed on NIL leaderboard
  - **Size:** Computed in real-time
  - **Access pattern:** Bulk reads, low frequency

**Decision Framework:**

```python
def should_preload(data_type):
    """
    Decision matrix for preloading vs real-time computation:
    
    Factors:
    1. Access frequency: High → Preload
    2. Computation cost: High → Preload
    3. Data size: Small → Preload
    4. Change frequency: Low → Preload
    5. Access pattern: Random → Preload, Sequential → Real-time
    """
    
    if access_frequency > threshold_high:
        return True
    
    if computation_cost > threshold_high and data_size < threshold_memory:
        return True
    
    if change_frequency < threshold_low and access_frequency > threshold_medium:
        return True
    
    return False
```

**Improvements:**
1. **Adaptive Preloading:**
   - Monitor access patterns at runtime
   - Dynamically preload frequently accessed data
   - Implement LRU cache for real-time computed data
   - Cache eviction based on access patterns

2. **Lazy Loading with Prefetching:**
   - Load data on first access
   - Prefetch related data (e.g., load game data for player's teammates)
   - Predictive prefetching based on user behavior
   - Background loading to avoid blocking requests

3. **Hybrid Approach:**
   - Preload hot data (frequently accessed)
   - Real-time compute cold data (infrequently accessed)
   - Promote cold to hot based on access patterns
   - Demote hot to cold based on memory pressure


---

## Key Backend Components

### 1. Player Service

**File:** `backend/app/services/player_service.py`

**Responsibilities:**
- Player data retrieval with filtering/sorting/pagination
- Derived stat calculations (PPG, APG, RPG, etc.)
- Data tier handling (basic vs enriched)
- Field mapping and normalization

**Key Methods:**

```python
class PlayerService:
    def get_players(params: PlayerQueryParams) -> PlayerListResponse:
        # 1. Apply filters (year, conference, search, etc.)
        filtered_data = _apply_filters(df, params, year)
        
        # 2. Apply sorting (handle derived stats)
        if params.sort in ['PPG', 'APG', 'RPG']:
            data = _calculate_derived_stats(data)
        data = _apply_sorting(data, params.sort, params.order)
        
        # 3. Apply pagination (before expensive transformations)
        paginated_data = _apply_pagination(data, params.limit, params.offset)
        
        # 4. Transform paginated data only
        paginated_data = _clean_numeric_data(paginated_data)
        paginated_data = _convert_percentages(paginated_data)
        paginated_data = _calculate_derived_stats(paginated_data)
        
        return PlayerListResponse(results=paginated_data.to_dict())
    
    def _calculate_derived_stats(data: pd.DataFrame) -> pd.DataFrame:
        # Calculate per-game stats
        new_columns = {
            'PPG': data['Points'] / data['Games'],
            'APG': data['Assists'] / data['Games'],
            'RPG': data['Rebounds Total'] / data['Games'],
            'SPG': data['Steals'] / data['Games'],
            'BPG': data['Blocks'] / data['Games'],
            'MPG': data['Minutes'] / data['Games'],
        }
        return data.assign(**new_columns)
```

**Optimization Techniques:**
- Filter before copying (reduce memory usage)
- Paginate before expensive transformations
- Calculate derived stats only when needed for sorting
- Use vectorized pandas operations

**Pagination Strategy:**

**Current Implementation:**
```python
def _apply_pagination(data: pd.DataFrame, limit: int, offset: int) -> pd.DataFrame:
    return data.iloc[offset:offset + limit]
```

**Tradeoffs:**
- **Pros:** Simple implementation, works with pandas DataFrames, memory-efficient (only loads needed rows)
- **Cons:** No cursor-based pagination (inefficient for deep pagination), offset-based can skip many rows, no total count optimization

**Pagination Performance Issues:**
- Offset-based pagination requires scanning and skipping `offset` rows
- For large datasets (e.g., offset=10000), this is inefficient
- Total count requires scanning entire filtered dataset
- No support for cursor-based pagination (better for infinite scroll)

**Improvements:**
1. **Cursor-Based Pagination:**
   ```python
   def get_players_cursor(cursor: str = None, limit: int = 50):
       if cursor:
           # Decode cursor to get last seen values
           last_values = decode_cursor(cursor)
           # Filter where all sort columns > last_values
           data = df[(df['BPM'] > last_values['BPM']) |
                    ((df['BPM'] == last_values['BPM']) &
                     (df['player_name'] > last_values['player_name']))]
       else:
           data = df
       
       paginated = data.head(limit)
       next_cursor = encode_cursor(paginated.iloc[-1])
       return paginated, next_cursor
   ```
   - Efficient for deep pagination (no offset scanning)
   - Supports infinite scroll
   - Consistent results even if data changes between requests

2. **Total Count Optimization:**
   ```python
   def get_players_with_count(params):
       # Use approximate count for large datasets
       if filtered_count > 10000:
           total_count = df.shape[0]  # Approximate
       else:
           total_count = len(filtered_data)  # Exact
       
       return results, total_count
   ```
   - Use approximate counts for large datasets
   - Cache total counts per filter combination
   - Separate endpoint for count-only queries

3. **Keyset Pagination:**
   - Use unique keys (player_key, year) for pagination
   - More efficient than offset-based
   - Better for real-time data (handles inserts/deletes)

4. **Pagination Metadata:**
   ```python
   return {
       'results': results,
       'pagination': {
           'limit': limit,
           'offset': offset,
           'total': total_count,
           'has_next': offset + limit < total_count,
           'has_prev': offset > 0,
           'next_cursor': next_cursor,
           'prev_cursor': prev_cursor
       }
   }
   ```

---

## Data Storage Architecture

### Current Approach: File-Based Storage

**Implementation:**
- CSV files compressed with gzip
- JSON files for game data
- Pickle files for cached computations
- No database layer

**Tradeoffs:**

**Pros:**
- **Simplicity:** No database setup, maintenance, or schema migrations
- **Portability:** Easy to move data between environments (copy files)
- **Version Control:** Can track data changes in Git (for small datasets)
- **Cost:** No database hosting costs
- **Development:** Fast iteration, no schema changes needed

**Cons:**
- **Scalability:** Limited to single-server deployment (no horizontal scaling)
- **Concurrency:** No built-in concurrency control (file locking issues)
- **Query Performance:** No indexes, full scans for all queries
- **Data Integrity:** No ACID guarantees, no foreign key constraints
- **Real-time Updates:** Difficult to update individual records (must rewrite entire file)
- **Complex Queries:** No joins, aggregations, or complex filtering at data layer
- **Memory Usage:** Must load entire dataset into memory (pandas)
- **Transaction Support:** No rollback capability for failed operations

**Why Not SQL/Database?**

**Decision Factors:**
1. **Dataset Size:** ~15,000 players × 8 years = ~120,000 records (fits in memory)
2. **Query Patterns:** Simple filtering/sorting (no complex joins)
3. **Update Frequency:** Data updates weekly (not real-time)
4. **Team Size:** Single developer (database overhead not justified)
5. **Deployment:** Railway (limited resources, database adds complexity)
6. **Development Speed:** File-based allows faster iteration

**When to Migrate to Database:**

**Triggers for Migration:**
1. **Dataset Size:** > 1M records or > 10GB in memory
2. **Concurrent Users:** > 100 simultaneous users
3. **Real-time Updates:** Need sub-second data updates
4. **Complex Queries:** Need joins across multiple tables
5. **Horizontal Scaling:** Need multiple API instances
6. **Data Integrity:** Need ACID guarantees for transactions
7. **Advanced Features:** Need full-text search, geospatial queries, etc.

**Database Migration Strategy:**

**Recommended Database:** PostgreSQL

**Schema Design:**
```sql
-- Players table
CREATE TABLE players (
    player_key VARCHAR(50) PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    team VARCHAR(100),
    conference VARCHAR(50),
    position VARCHAR(10),
    year INT NOT NULL,
    bpm FLOAT,
    usage FLOAT,
    efg FLOAT,
    -- ... other stats
    data_tier VARCHAR(20),
    INDEX idx_year (year),
    INDEX idx_team (team),
    INDEX idx_conference (conference),
    INDEX idx_bpm (bpm),
    INDEX idx_composite (year, conference, bpm)
);

-- Game data table
CREATE TABLE game_stats (
    id SERIAL PRIMARY KEY,
    player_key VARCHAR(50) REFERENCES players(player_key),
    game_date DATE,
    opponent VARCHAR(100),
    points INT,
    rebounds INT,
    assists INT,
    -- ... other game stats
    INDEX idx_player_date (player_key, game_date)
);

-- Clusters table
CREATE TABLE player_clusters (
    player_key VARCHAR(50) REFERENCES players(player_key),
    year INT,
    cluster_id INT,
    PRIMARY KEY (player_key, year),
    INDEX idx_cluster (cluster_id)
);
```

**Migration Benefits:**
1. **Query Performance:** Indexes for fast filtering/sorting
2. **Scalability:** Horizontal scaling with read replicas
3. **Concurrency:** Built-in connection pooling and transaction support
4. **Data Integrity:** Foreign keys, constraints, ACID guarantees
5. **Real-time Updates:** Update individual records without rewriting entire dataset
6. **Complex Queries:** JOINs, subqueries, window functions
7. **Full-Text Search:** PostgreSQL's built-in full-text search
8. **JSON Support:** Store flexible data (roster info, biographical data)

**Migration Challenges:**
1. **Schema Design:** Need to design normalized schema vs denormalized
2. **Data Migration:** ETL process to move CSV data to database
3. **Code Changes:** Rewrite data_loader.py to use SQLAlchemy/psycopg2
4. **Deployment:** Set up database hosting (Railway Postgres, RDS, etc.)
5. **Cost:** Database hosting costs ($5-50/month depending on size)
6. **Backup:** Need database backup strategy
7. **Monitoring:** Database performance monitoring

**Alternative: Hybrid Approach**

**Keep File-Based For:**
- Static reference data (conference mappings, cluster descriptions)
- Historical data that rarely changes (pre-2020 seasons)
- Large analytical datasets (all-time player data)

**Move to Database For:**
- Current season player data (frequent updates)
- Game data (real-time updates during season)
- User-generated data (if added in future)
- Session/cache data

**Implementation:**
```python
# Hybrid data loader
class HybridDataLoader:
    def __init__(self):
        self.db_engine = create_engine(DATABASE_URL)
        self.csv_loader = CSVDataLoader()
    
    def get_current_players(self, year):
        # Use database for current data
        query = f"SELECT * FROM players WHERE year = {year}"
        return pd.read_sql(query, self.db_engine)
    
    def get_historical_players(self, year):
        # Use CSV for historical data
        return self.csv_loader.load_players(year)
```

---

## API/Frontend/Backend Separation

### Current Architecture

**Separation Strategy:**
- **Frontend:** Next.js (React) - UI layer, state management, user interactions
- **Backend:** FastAPI (Python) - API layer, business logic, data processing
- **Communication:** REST API over HTTP (JSON)

**API Layer (Backend):**
```python
# Route handlers in backend/app/api/
@app.get("/api/v1/players")
async def get_players(params: PlayerQueryParams):
    # 1. Validate request (Pydantic)
    # 2. Call service layer
    results = PlayerService.get_players(params)
    # 3. Return JSON response
    return results
```

**Frontend API Client:**
```typescript
// lib/api.ts
export async function getPlayers(params: PlayerQueryParams) {
  const response = await fetch(`${API_URL}/api/v1/players?${queryParams}`);
  return response.json();
}
```

**Separation Benefits:**
- **Independent Development:** Frontend and backend can be developed separately
- **Technology Flexibility:** Different languages/frameworks for each layer
- **Scalability:** Can scale frontend and backend independently
- **Reusability:** Backend API can be used by multiple clients (web, mobile, third-party)
- **Testing:** Can test frontend with mocked API, test backend independently

**Separation Challenges:**
- **Integration Complexity:** Need to maintain API contract between layers
- **Type Safety:** TypeScript types may not match Python schemas
- **Latency:** Network overhead for API calls
- **State Management:** Need to manage client-side state vs server-side state

### Security Features

**Current Security Implementation:**

**1. CORS (Cross-Origin Resource Sharing):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Whitelisted origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
- **Purpose:** Prevent unauthorized cross-origin requests
- **Tradeoff:** Currently allows all methods/headers (could be more restrictive)
- **Improvement:** Restrict to specific methods (GET, POST) and headers needed

**2. Rate Limiting:**
```python
limiter = Limiter(key_func=get_remote_address)
@app.get("/health")
@limiter.limit("100/minute")
async def health_check(request: Request):
    return {"status": "healthy"}
```
- **Purpose:** Prevent API abuse and DDoS attacks
- **Current:** IP-based rate limiting (100 requests/minute for health endpoint)
- **Tradeoff:** IP-based can be bypassed with proxies, no per-user limits
- **Improvement:** 
  - Implement per-endpoint rate limits
  - Add API key authentication for higher limits
  - Use Redis-backed rate limiting for distributed systems
  - Add rate limit headers to responses

**3. Input Validation:**
```python
class PlayerQueryParams(BaseModel):
    year: Optional[Union[int, str]] = None
    conf: Optional[str] = None
    search: Optional[str] = None
    limit: int = Field(default=50, le=100)  # Max 100
    offset: int = Field(default=0, ge=0)     # Min 0
```
- **Purpose:** Prevent injection attacks and invalid inputs
- **Current:** Pydantic schema validation with type checking
- **Tradeoff:** No custom validation beyond type checking
- **Improvement:**
  - Add custom validators (e.g., conference name validation)
  - Sanitize search inputs to prevent injection
  - Add length limits on string inputs
  - Validate enum values (conference, position)

**4. Error Handling:**
```python
class ErrorHandlerMiddleware:
    async def __call__(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"}
            )
```
- **Purpose:** Prevent information leakage in error messages
- **Current:** Generic error messages, logging for debugging
- **Tradeoff:** Generic errors make debugging harder for legitimate users
- **Improvement:**
  - Add error codes for different error types
  - Include request ID in error response for debugging
  - Add detailed error messages in debug mode only
  - Implement error monitoring (Sentry, etc.)

**5. Environment Configuration:**
```python
class Settings(BaseSettings):
    debug: bool = False
    cors_origins: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
```
- **Purpose:** Separate dev/prod configurations
- **Current:** Environment variables, .env file
- **Tradeoff:** No secrets management (API keys in .env)
- **Improvement:**
  - Use secrets manager (Railway secrets, AWS Secrets Manager)
  - Never commit .env files to version control
  - Rotate secrets regularly
  - Add secrets validation on startup

**Missing Security Features:**

**1. Authentication/Authorization:**
- **Current:** No authentication (public API)
- **Risk:** Anyone can access API, no rate limiting per user
- **Improvement:**
  - Add API key authentication for write operations
  - Implement OAuth2 for user authentication
  - Add role-based access control (admin vs user)
  - Rate limit per API key/user

**2. HTTPS/TLS:**
- **Current:** Depends on deployment (Railway provides HTTPS)
- **Risk:** Man-in-the-middle attacks if not using HTTPS
- **Improvement:**
  - Enforce HTTPS in production (redirect HTTP to HTTPS)
  - Add HSTS headers
  - Use secure cookies for authentication

**3. SQL Injection Prevention:**
- **Current:** Not applicable (file-based storage)
- **Risk:** N/A currently, but critical if migrating to database
- **Improvement (if migrating):**
  - Use parameterized queries (SQLAlchemy ORM)
  - Never concatenate user input into SQL queries
  - Validate all inputs before database queries

**4. XSS (Cross-Site Scripting) Prevention:**
- **Current:** Backend returns JSON (no HTML rendering)
- **Risk:** Frontend must sanitize user-generated content
- **Improvement:**
  - Add Content-Security-Policy headers
  - Sanitize user inputs in frontend
  - Escape HTML entities in responses

**5. CSRF (Cross-Site Request Forgery) Prevention:**
- **Current:** Not implemented (stateless API)
- **Risk:** Unauthorized actions on behalf of authenticated users
- **Improvement:**
  - Add CSRF tokens for state-changing operations
  - Verify Origin and Referer headers
  - Use SameSite cookie attribute

**Security Improvements Priority:**

**High Priority:**
1. Add API key authentication for write operations
2. Implement per-endpoint rate limiting
3. Add input sanitization for search fields
4. Enforce HTTPS in production

**Medium Priority:**
5. Add error monitoring (Sentry)
6. Implement secrets management
7. Add request logging for audit trail
8. Add API versioning for backward compatibility

**Low Priority:**
9. Add OAuth2 for user authentication
10. Implement role-based access control
11. Add CSRF protection
12. Add API analytics/monitoring

### 2. Similarity Service

**File:** `backend/app/services/similarity_service.py`

**Algorithm:** Cosine Similarity on normalized feature vectors

**Vector Construction:**

```python
# Style Vector (9 dimensions)
STYLE_FEATURES = [
    "3PT Volume",      # 3-point shooting tendency
    "Rim Pressure",    # Finishing at basket
    "Midrange",        # Mid-range shooting
    "Playmaking",      # Assist rate
    "Off-Ball",        # Off-ball movement
    "Turnovers",       # Turnover rate (inverted)
]

# Impact Vector (7 dimensions)
IMPACT_FEATURES = [
    "Scoring Impact",  # RAPM scoring contribution
    "Assist Impact",   # RAPM playmaking contribution
    "Rebounding Impact", # RAPM rebounding contribution
    "Defense Impact",  # RAPM defensive contribution
    "Efficiency",      # Overall efficiency
]
```

**Similarity Calculation:**

```python
def get_similar_players(ncaa_id, year=None, top_k=10, style_weight=0.7):
    # 1. Get target player's vector
    target = get_vector(PLAYER_VECTORS[ncaa_id], year)
    style_a = normalize(target['style'])
    impact_a = normalize(target['impact'])
    
    # 2. Compare with all other players
    for other_id, other_data in PLAYER_VECTORS.items():
        if other_id == ncaa_id:
            continue
        
        style_b = normalize(other_data[year]['style'])
        impact_b = normalize(other_data[year]['impact'])
        
        # 3. Calculate cosine similarity
        style_sim = cosine_similarity(style_a, style_b)
        impact_sim = cosine_similarity(impact_a, impact_b)
        
        # 4. Weighted combination
        combined_sim = style_weight * style_sim + (1 - style_weight) * impact_sim
        
        # 5. Extract reasons for similarity/differences
        reasons = extract_reasons(style_a, style_b, STYLE_FEATURES)
        differences = extract_reasons(style_a, style_b, STYLE_FEATURES, similar=False)
    
    return sorted(results, key=lambda x: -x['similarity'])[:top_k]
```

**Reason Extraction:**

```python
def extract_reasons(a, b, labels, top_n=3, similar=True):
    # Calculate absolute differences
    diffs = np.abs(a - b)
    
    # Normalize by spread (prevents everything looking "small")
    spread = np.std(np.concatenate([a, b])) + 1e-8
    diffs = diffs / spread
    
    # Rank by difference
    idxs = np.argsort(diffs)
    
    if similar:
        # Return smallest differences (most similar)
        return [(labels[i], diffs[i]) for i in idxs[:top_n]]
    else:
        # Return largest differences (most different)
        return [(labels[i], diffs[i]) for i in idxs[-top_n:]]
```

**Vector Feature Selection:**

**Current Approach:**
- Features selected based on domain knowledge and basketball analytics conventions
- Style vector: 9 dimensions (usage, assist rate, turnover rate, shooting profile, etc.)
- Impact vector: 7 dimensions (RAPM components, efficiency metrics)
- No systematic feature importance analysis
- Arbitrary weight assignment (style_weight=0.7, impact_weight=0.3)

**Tradeoffs:**
- **Pros:** Domain-informed features, interpretable, fast to implement
- **Cons:** Subjective selection, may miss important features, weights are arbitrary, no validation

**Improvements with Feature Importance Analysis:**

**1. SHAP (SHapley Additive exPlanations) Values:**
```python
import shap
from sklearn.ensemble import RandomForestRegressor

# Train a model to predict a target (e.g., BPM)
X = player_data[all_potential_features]
y = player_data['BPM']

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Calculate SHAP values
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

# Feature importance ranking
feature_importance = np.abs(shap_values).mean(axis=0)
ranked_features = sorted(zip(X.columns, feature_importance), 
                         key=lambda x: -x[1])

# Select top N features for similarity vectors
top_features = [f[0] for f in ranked_features[:15]]
```

**Benefits:**
- Data-driven feature selection
- Quantifies each feature's contribution to predictions
- Identifies non-linear relationships
- Handles feature interactions

**2. Recursive Feature Elimination (RFE):**
```python
from sklearn.feature_selection import RFE
from sklearn.linear_model import LinearRegression

# Use RFE to select optimal number of features
estimator = LinearRegression()
selector = RFE(estimator, n_features_to_select=10, step=1)
selector = selector.fit(X, y)

# Get selected features
selected_features = X.columns[selector.support_]
```

**Benefits:**
- Systematic feature selection
- Cross-validation for robustness
- Automatically determines optimal feature count

**3. Correlation Analysis:**
```python
# Remove highly correlated features
correlation_matrix = X.corr().abs()
upper_triangle = correlation_matrix.where(
    np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)
)

# Find features with correlation > 0.8
high_corr_features = [column for column in upper_triangle.columns 
                      if any(upper_triangle[column] > 0.8)]

# Remove one of each correlated pair
selected_features = [f for f in X.columns if f not in high_corr_features]
```

**Benefits:**
- Reduces redundancy
- Improves model stability
- Reduces multicollinearity

**4. PCA (Principal Component Analysis):**
```python
from sklearn.decomposition import PCA

# Use PCA to reduce dimensionality
pca = PCA(n_components=10)
X_pca = pca.fit_transform(X_scaled)

# Explained variance ratio
explained_variance = pca.explained_variance_ratio_
cumulative_variance = np.cumsum(explained_variance)

# Use principal components as features
```

**Benefits:**
- Automatic dimensionality reduction
- Captures maximum variance with fewer features
- Uncovers latent patterns

**Tradeoffs:**
- Loss of interpretability (components are linear combinations)
- Harder to explain to users

**5. Automated Feature Selection Pipeline:**
```python
def select_optimal_features(X, y, max_features=15):
    """
    Automated feature selection combining multiple methods:
    1. Remove low-variance features
    2. Remove highly correlated features
    3. Use SHAP for importance ranking
    4. Use RFE for final selection
    """
    # Step 1: Remove low-variance features
    variance_threshold = VarianceThreshold(threshold=0.01)
    X_var = variance_threshold.fit_transform(X)
    
    # Step 2: Remove correlated features
    X_corr = remove_correlated_features(X_var, threshold=0.8)
    
    # Step 3: SHAP importance ranking
    shap_ranking = get_shap_importance(X_corr, y)
    
    # Step 4: RFE for final selection
    rfe_selector = RFE(estimator, n_features_to_select=max_features)
    selected = rfe_selector.fit_transform(X_corr, y)
    
    return selected
```

**Modular Feature Selection:**
```python
# Configurable feature sets
FEATURE_SETS = {
    'minimal': ['BPM', 'Usage', 'eFG%', 'AST%'],
    'standard': ['BPM', 'Usage', 'eFG%', 'AST%', 'ORB%', 'DRB%', 'STL%', 'BLK%'],
    'comprehensive': ['BPM', 'Usage', 'eFG%', 'AST%', 'ORB%', 'DRB%', 'STL%', 'BLK%', 
                     'TOV%', 'FTR', '3P%', '2P%', 'FT%', 'Height', 'Weight'],
    'ml_optimized': None  # Dynamically selected using SHAP/RFE
}

def get_feature_vectors(player, feature_set='standard'):
    if feature_set == 'ml_optimized':
        features = select_optimal_features(player_data)
    else:
        features = FEATURE_SETS[feature_set]
    
    return build_vector(player, features)
```

**Cosine Similarity Explained:**

**Mathematical Definition:**
```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)
```

Where:
- `A · B` = dot product of vectors A and B
- `||A||` = magnitude (length) of vector A
- `||B||` = magnitude (length) of vector B

**Intuition:**
- Measures the cosine of the angle between two vectors
- Range: [-1, 1]
  - 1 = identical direction (perfect similarity)
  - 0 = orthogonal (no similarity)
  - -1 = opposite direction (completely different)
- Focuses on direction, not magnitude

**Why Cosine Similarity for Player Comparison?**

**Advantages:**
1. **Magnitude Independence:**
   - Players with different usage rates but similar playing styles can be similar
   - Example: High-usage star vs low-usage role player with same efficiency profile
   - Captures "style" similarity, not "production" similarity

2. **Normalized Vectors:**
   - After normalization, cosine similarity = dot product
   - Computationally efficient (O(n) for n-dimensional vectors)
   - Fast for large-scale similarity search

3. **Interpretability:**
   - Easy to understand: angle between vectors
   - Well-established in recommendation systems
   - Standard approach in ML literature

**Disadvantages:**
1. **Ignores Magnitude:**
   - Two players with identical direction but different magnitudes are considered similar
   - May miss important differences in production level
   - Example: Elite player vs average player with same style

2. **Sensitive to Feature Scaling:**
   - Requires proper normalization
   - Different scales can skew results
   - Outliers can disproportionately affect similarity

3. **Curse of Dimensionality:**
   - In high-dimensional spaces, most vectors are nearly orthogonal
   - Similarity scores tend to cluster around 0
   - Requires dimensionality reduction for meaningful results

**Alternatives to Cosine Similarity:**

**1. Euclidean Distance:**
```
euclidean_distance(A, B) = sqrt(Σ(Ai - Bi)²)
```
- **Pros:** Captures both direction and magnitude, intuitive
- **Cons:** Sensitive to scale, requires normalization, less interpretable for high-dimensional data

**2. Manhattan Distance:**
```
manhattan_distance(A, B) = Σ|Ai - Bi|
```
- **Pros:** Robust to outliers, works well with high-dimensional data
- **Cons:** Less intuitive than Euclidean, sensitive to scale

**3. Pearson Correlation:**
```
pearson_correlation(A, B) = covariance(A, B) / (std(A) × std(B))
```
- **Pros:** Measures linear relationship, scale-invariant
- **Cons:** Only captures linear relationships, sensitive to outliers

**4. Jaccard Similarity:**
```
jaccard_similarity(A, B) = |A ∩ B| / |A ∪ B|
```
- **Pros:** Good for binary/categorical data
- **Cons:** Not suitable for continuous data

**5. Mahalanobis Distance:**
```
mahalanobis_distance(A, B) = sqrt((A - B)ᵀ × Σ⁻¹ × (A - B))
```
- **Pros:** Accounts for feature correlations, scale-invariant
- **Cons:** Requires covariance matrix, computationally expensive

**Hybrid Approach:**
```python
def hybrid_similarity(player_a, player_b):
    # Combine cosine similarity (style) with Euclidean distance (production)
    style_sim = cosine_similarity(player_a['style_vector'], player_b['style_vector'])
    prod_dist = euclidean_distance(player_a['production_vector'], player_b['production_vector'])
    
    # Normalize production distance to [0, 1]
    prod_sim = 1 / (1 + prod_dist)
    
    # Weighted combination
    final_sim = 0.6 * style_sim + 0.4 * prod_sim
    
    return final_sim
```

**Differences Feature Improvements:**

**Current Issues:**
- Differences are based on normalized absolute differences
- May not capture meaningful differences in context
- No statistical significance testing
- Arbitrary threshold (0.1) for including differences

**Improvements:**

**1. Statistical Significance Testing:**
```python
from scipy import stats

def extract_significant_differences(a, b, labels, top_n=3):
    # Calculate z-scores for differences
    diffs = np.abs(a - b)
    
    # Calculate population statistics for each feature
    population_means = get_population_means()
    population_stds = get_population_stds()
    
    # Calculate z-scores
    z_scores = (diffs - population_means) / population_stds
    
    # Calculate p-values
    p_values = 2 * (1 - stats.norm.cdf(np.abs(z_scores)))
    
    # Filter for statistically significant differences (p < 0.05)
    significant_mask = p_values < 0.05
    significant_diffs = diffs[significant_mask]
    significant_labels = [labels[i] for i in range(len(labels)) if significant_mask[i]]
    
    # Return top N significant differences
    idxs = np.argsort(significant_diffs)[-top_n:]
    return [(significant_labels[i], significant_diffs[i]) for i in idxs]
```

**2. Percentile-Based Differences:**
```python
def extract_percentile_differences(a, b, labels, top_n=3):
    # Calculate percentile ranks for each feature
    a_percentiles = [get_percentile_rank(val, feature) for val, feature in zip(a, labels)]
    b_percentiles = [get_percentile_rank(val, feature) for val, feature in zip(b, labels)]
    
    # Calculate percentile differences
    percentile_diffs = np.abs(np.array(a_percentiles) - np.array(b_percentiles))
    
    # Return features with largest percentile differences
    idxs = np.argsort(percentile_diffs)[-top_n:]
    return [(labels[i], percentile_diffs[i]) for i in idxs]
```

**3. Context-Aware Differences:**
```python
def extract_context_aware_differences(a, b, labels, context):
    # Adjust difference importance based on context
    # Example: For guards, 3PT shooting is more important than rebounding
    
    context_weights = {
        'PG': {'3PT Volume': 1.5, 'Playmaking': 1.5, 'Rebounding': 0.5},
        'SG': {'3PT Volume': 1.3, 'Scoring': 1.3, 'Playmaking': 1.0},
        'SF': {'Scoring': 1.2, '3PT Volume': 1.2, 'Rebounding': 1.0},
        'PF': {'Rebounding': 1.5, 'Scoring': 1.2, '3PT Volume': 0.8},
        'C': {'Rebounding': 1.5, 'Rim Protection': 1.5, '3PT Volume': 0.5}
    }
    
    diffs = np.abs(a - b)
    weights = np.array([context_weights.get(context, {}).get(label, 1.0) for label in labels])
    weighted_diffs = diffs * weights
    
    idxs = np.argsort(weighted_diffs)[-top_n:]
    return [(labels[i], weighted_diffs[i]) for i in idxs]
```

**4. Directional Differences:**
```python
def extract_directional_differences(a, b, labels, top_n=3):
    # Capture direction of difference (a > b or a < b)
    diffs = a - b
    
    # Categorize differences
    categories = []
    for diff, label in zip(diffs, labels):
        if diff > 0.1:
            categories.append((label, 'higher', diff))
        elif diff < -0.1:
            categories.append((label, 'lower', abs(diff)))
        else:
            categories.append((label, 'similar', abs(diff)))
    
    # Sort by magnitude
    categories.sort(key=lambda x: -x[2])
    
    return categories[:top_n]
```

**5. Clustering-Based Differences:**
```python
def extract_cluster_based_differences(a, b, labels, cluster_id):
    # Compare differences relative to cluster averages
    cluster_means = get_cluster_means(cluster_id)
    
    diffs = np.abs(a - b)
    cluster_diffs = np.abs(a - cluster_means) + np.abs(b - cluster_means)
    
    # Weight differences by how far both are from cluster mean
    weighted_diffs = diffs * cluster_diffs
    
    idxs = np.argsort(weighted_diffs)[-top_n:]
    return [(labels[i], weighted_diffs[i]) for i in idxs]
```

### 3. Projection Service

**File:** `backend/app/services/projection_service.py`

**Methodology:** Cluster-based projection with similarity weighting

**Algorithm:**

```python
class ProjectionService:
    def get_2027_projections(self):
        # 1. Load player clusters (18 clusters, IDs 0-17)
        clusters_df = load_clusters()
        
        # 2. Load BPM change modeling data
        bpm_change_df = load_bpm_change_data()
        
        # 3. For each player, find similar players in same cluster
        for player in players_2026:
            cluster = player['cluster']
            similar_players = find_similar_in_cluster(
                player, 
                cluster, 
                features=['Usage', 'BPM', 'Height', 'off_rtg', 'def_rtg']
            )
            
            # 4. Weight historical BPM changes by similarity
            weighted_changes = []
            for similar in similar_players:
                similarity = calculate_similarity(player, similar)
                bpm_change = similar['bpm_change']
                weighted_changes.append(similarity * bpm_change)
            
            # 5. Project 2027 BPM
            projected_change = sum(weighted_changes) / len(weighted_changes)
            projected_bpm_2027 = player['BPM_2026'] + projected_change
            
            # 6. Apply age adjustment
            age_adjustment = get_age_curve(player['age'])
            final_bpm = projected_bpm_2027 + age_adjustment
        
        return projections
```

**Feature Weights:**

```python
FEATURE_WEIGHTS = {
    'Usage_from': 0.25,    # Usage rate is most predictive
    'BPM_from': 0.20,     # Current BPM predicts future
    'Height': 0.15,       # Physical profile matters
    'off_rtg_from': 0.10, # Offensive rating
    'def_rtg_from': 0.10, # Defensive rating
    'eFG_from': 0.10,     # Efficiency
    'TS_per_from': 0.10,  # True shooting
}
```

**Weight Determination:**
- Current weights are based on domain knowledge and basketball analytics conventions
- No systematic validation or optimization
- Arbitrary assignment without testing

**Improvements for Weight Determination:**

**1. Grid Search for Optimal Weights:**
```python
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor

# Define weight combinations to test
weight_combinations = [
    {'Usage_from': 0.3, 'BPM_from': 0.25, 'Height': 0.15, 'off_rtg_from': 0.1, 'def_rtg_from': 0.1, 'eFG_from': 0.05, 'TS_per_from': 0.05},
    {'Usage_from': 0.25, 'BPM_from': 0.2, 'Height': 0.2, 'off_rtg_from': 0.1, 'def_rtg_from': 0.1, 'eFG_from': 0.1, 'TS_per_from': 0.05},
    # ... more combinations
]

best_score = -float('inf')
best_weights = None

for weights in weight_combinations:
    # Calculate weighted features
    X_weighted = calculate_weighted_features(X, weights)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    scores = cross_val_score(model, X_weighted, y, cv=5, scoring='neg_mean_squared_error')
    
    if scores.mean() > best_score:
        best_score = scores.mean()
        best_weights = weights

print(f"Best weights: {best_weights}")
print(f"Best CV score: {best_score}")
```

**2. Bayesian Optimization for Weights:**
```python
from skopt import gp_minimize
from skopt.space import Real

# Define search space (weights must sum to 1)
space = [
    Real(0.0, 0.5, name='usage_weight'),
    Real(0.0, 0.5, name='bpm_weight'),
    Real(0.0, 0.3, name='height_weight'),
    Real(0.0, 0.2, name='off_rtg_weight'),
    Real(0.0, 0.2, name='def_rtg_weight'),
    Real(0.0, 0.2, name='efg_weight'),
    Real(0.0, 0.2, name='ts_weight'),
]

def objective(weights):
    # Normalize weights to sum to 1
    weights = np.array(weights)
    weights = weights / weights.sum()
    
    # Calculate weighted features
    X_weighted = calculate_weighted_features(X, weights)
    
    # Train and evaluate
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    scores = cross_val_score(model, X_weighted, y, cv=5, scoring='neg_mean_squared_error')
    
    return -scores.mean()  # Minimize negative MSE

# Optimize
result = gp_minimize(objective, space, n_calls=50, random_state=42)
optimal_weights = result.x / result.x.sum()
```

**3. Learnable Weights (Neural Network):**
```python
import tensorflow as tf

# Build neural network with attention mechanism
inputs = tf.keras.Input(shape=(n_features,))
attention = tf.keras.layers.Dense(n_features, activation='softmax')(inputs)
weighted_features = inputs * attention
output = tf.keras.layers.Dense(1)(weighted_features)

model = tf.keras.Model(inputs=inputs, outputs=output)
model.compile(optimizer='adam', loss='mse')

# Train to learn optimal weights
model.fit(X_train, y_train, epochs=100, validation_split=0.2)

# Extract learned weights
attention_weights = model.get_layer('dense').get_weights()[0]
```

**Additional Features for Cluster-Based Projection:**

**Current Features:**
- Usage, BPM, Height, offensive rating, defensive rating, eFG%, true shooting

**Potential Additional Features:**

**1. Team Context Features:**
- Team adjusted efficiency margin (adj_em)
- Team offensive/defensive efficiency
- Team pace
- Team strength of schedule (SOS)
- Conference strength
- Coaching quality (if available)

**2. Player Role Features:**
- Position (PG, SG, SF, PF, C)
- Minutes per game
- Usage rate percentile within team
- Shot distribution (2P%, 3P%, FT%)
- Assist rate
- Turnover rate

**3. Historical Features:**
- Career BPM trend (3-year average)
- Year-over-year BPM change (ΔBPM)
- Consistency (standard deviation of BPM over seasons)
- Peak BPM (career best)
- Age at peak

**4. Transfer Portal Features:**
- Transfer status (yes/no)
- Number of transfers
- Change in team quality (adj_em difference)
- Change in conference strength
- Time since transfer

**5. Physical Features:**
- Height
- Weight
- Wingspan (if available)
- Body mass index (BMI)
- Age

**6. Advanced Metrics:**
- RAPM (Regularized Adjusted Plus Minus)
- VORP (Value Over Replacement Player)
- Win Shares
- Box Plus Minus components (OBPM, DBPM)
- Player Efficiency Rating (PER)

**Modular Projection System:**

**Current Implementation:**
- Monolithic projection service
- Hardcoded features and weights
- Single projection method (cluster-based)

**Modular Design:**

```python
# Feature modules
class FeatureModule:
    """Base class for feature extraction modules"""
    def extract(self, player_data):
        raise NotImplementedError

class TeamContextModule(FeatureModule):
    def extract(self, player_data):
        return {
            'team_adj_em': player_data['team_adj_em'],
            'team_sos': player_data['team_sos'],
            'conference_strength': get_conference_strength(player_data['conf'])
        }

class HistoricalModule(FeatureModule):
    def extract(self, player_data):
        career_history = get_career_history(player_data['player_key'])
        return {
            'career_bpm_avg': career_history['BPM'].mean(),
            'bpm_trend': calculate_trend(career_history['BPM']),
            'peak_bpm': career_history['BPM'].max()
        }

# Projection modules
class ProjectionModule:
    """Base class for projection methods"""
    def project(self, player, features):
        raise NotImplementedError

class ClusterProjectionModule(ProjectionModule):
    def project(self, player, features):
        # Current cluster-based projection
        return cluster_based_projection(player, features)

class MLProjectionModule(ProjectionModule):
    def project(self, player, features):
        # Machine learning projection
        return ml_model.predict(features)

class EnsembleProjectionModule(ProjectionModule):
    def __init__(self, modules, weights):
        self.modules = modules
        self.weights = weights
    
    def project(self, player, features):
        projections = [module.project(player, features) for module in self.modules]
        return sum(p * w for p, w in zip(projections, self.weights))

# Modular projection service
class ModularProjectionService:
    def __init__(self):
        self.feature_modules = [
            TeamContextModule(),
            HistoricalModule(),
            # ... more modules
        ]
        self.projection_module = EnsembleProjectionModule(
            modules=[ClusterProjectionModule(), MLProjectionModule()],
            weights=[0.6, 0.4]
        )
    
    def get_projection(self, player):
        # Extract features from all modules
        features = {}
        for module in self.feature_modules:
            features.update(module.extract(player))
        
        # Project using projection module
        return self.projection_module.project(player, features)
```

**Benefits of Modular Design:**
- Easy to add new features without modifying core logic
- Can test different projection methods independently
- Supports ensemble methods (combine multiple approaches)
- Easier to maintain and debug
- Configurable feature sets per use case

---

## Player Projection Methodologies

### Current Methodology: Cluster-Based Projection

**Approach:**
- Find similar players in same cluster
- Weight historical BPM changes by similarity
- Apply age adjustment
- Simple, interpretable, but limited accuracy

**Performance:**
- R² = 0.45 (explains 45% of variance)
- RMSE = 1.8 BPM
- MAE = 1.4 BPM

### Alternative Projection Methodologies

**1. Time Series Forecasting:**

**ARIMA (AutoRegressive Integrated Moving Average):**
```python
from statsmodels.tsa.arima.model import ARIMA

def project_arima(player_history):
    # Fit ARIMA model to player's BPM history
    model = ARIMA(player_history['BPM'], order=(1, 1, 1))
    model_fit = model.fit()
    
    # Forecast next season
    forecast = model_fit.forecast(steps=1)
    return forecast[0]
```
- **Pros:** Captures temporal patterns, handles trends and seasonality
- **Cons:** Requires sufficient historical data (3+ seasons), assumes stationarity

**2. Prophet (Facebook's Time Series Library):**
```python
from prophet import Prophet

def project_prophet(player_history):
    # Prepare data for Prophet
    df = pd.DataFrame({
        'ds': player_history['year'],
        'y': player_history['BPM']
    })
    
    # Fit Prophet model
    model = Prophet()
    model.fit(df)
    
    # Make future dataframe
    future = model.make_future_dataframe(periods=1)
    forecast = model.predict(future)
    
    return forecast.iloc[-1]['yhat']
```
- **Pros:** Handles missing data, captures seasonality, interpretable components
- **Cons:** Overkill for single-season projection, requires regular time intervals

**3. Gradient Boosting (XGBoost/LightGBM):**

**XGBoost:**
```python
import xgboost as xgb

def project_xgboost(player_features):
    # Train XGBoost model
    model = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Project
    return model.predict(player_features)
```
- **Pros:** Handles non-linear relationships, feature importance, robust to outliers
- **Cons:** Requires careful hyperparameter tuning, less interpretable than linear models

**4. Neural Networks (LSTM/Transformer):**

**LSTM (Long Short-Term Memory):**
```python
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

def project_lstm(player_history):
    # Build LSTM model
    model = Sequential([
        LSTM(50, activation='relu', input_shape=(n_timesteps, n_features)),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    
    # Train on player history
    model.fit(X_train, y_train, epochs=100, batch_size=32)
    
    # Project
    return model.predict(player_history)
```
- **Pros:** Captures complex temporal patterns, handles long-term dependencies
- **Cons:** Requires large dataset, computationally expensive, black box

**5. Ensemble Methods:**

**Stacking Ensemble:**
```python
from sklearn.ensemble import StackingRegressor
from sklearn.linear_model import LinearRegression

# Base models
base_models = [
    ('rf', RandomForestRegressor(n_estimators=100)),
    ('xgb', xgb.XGBRegressor(n_estimators=100)),
    ('lgb', lgb.LGBMRegressor(n_estimators=100))
]

# Meta model
meta_model = LinearRegression()

# Stacking ensemble
ensemble = StackingRegressor(
    estimators=base_models,
    final_estimator=meta_model,
    cv=5
)

ensemble.fit(X_train, y_train)
```
- **Pros:** Combines strengths of multiple models, often improves accuracy
- **Cons:** More complex, harder to interpret, longer training time

**6. Bayesian Methods:**

**Bayesian Ridge Regression:**
```python
from sklearn.linear_model import BayesianRidge

def project_bayesian(player_features):
    model = BayesianRidge()
    model.fit(X_train, y_train)
    
    # Get prediction with uncertainty
    prediction, std = model.predict(player_features, return_std=True)
    return prediction, std
```
- **Pros:** Provides uncertainty estimates, regularizes automatically
- **Cons:** Assumes linear relationship, computationally expensive for large datasets

### Model Accuracy Assessment

**Current Assessment:**
- 5-fold cross-validation
- Holdout test set (20%)
- Time-series split (train on past, test on future)
- Metrics: R², RMSE, MAE

**Improved Assessment Framework:**

**1. Cross-Validation Strategies:**

**Time Series Split:**
```python
from sklearn.model_selection import TimeSeriesSplit

# Time-series cross-validation (train on past, test on future)
tscv = TimeSeriesSplit(n_splits=5)
scores = cross_val_score(model, X, y, cv=tscv, scoring='neg_mean_squared_error')
```

**Group K-Fold:**
```python
from sklearn.model_selection import GroupKFold

# Group by player to prevent data leakage
gkf = GroupKFold(n_splits=5)
scores = cross_val_score(model, X, y, groups=player_ids, cv=gkf, scoring='neg_mean_squared_error')
```

**2. Additional Metrics:**

**Mean Absolute Percentage Error (MAPE):**
```python
from sklearn.metrics import mean_absolute_percentage_error

mape = mean_absolute_percentage_error(y_test, y_pred)
```

**Symmetric Mean Absolute Percentage Error (SMAPE):**
```python
def smape(y_true, y_pred):
    return np.mean(2 * np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred)))
```

**Directional Accuracy:**
```python
def directional_accuracy(y_true, y_pred):
    """Percentage of correct directional predictions"""
    correct_direction = np.sign(y_pred - y_true) == np.sign(y_true - y_true.shift(1))
    return correct_direction.mean()
```

**3. Calibration Assessment:**

**Calibration Curve:**
```python
from sklearn.calibration import calibration_curve

# Check if predictions are well-calibrated
prob_true, prob_pred = calibration_curve(y_test > threshold, y_pred, n_bins=10)
```

**Reliability Diagram:**
- Visualize predicted vs actual values
- Check for systematic biases (over/under-prediction)

**4. Residual Analysis:**

**Residual Plots:**
```python
import matplotlib.pyplot as plt

residuals = y_test - y_pred
plt.scatter(y_pred, residuals)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted BPM')
plt.ylabel('Residuals')
plt.show()
```

**Q-Q Plot:**
```python
from scipy import stats
stats.probplot(residuals, dist="norm", plot=plt)
plt.show()
```

**5. Feature Importance Analysis:**

**Permutation Importance:**
```python
from sklearn.inspection import permutation_importance

result = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=42)
```

**SHAP Values:**
```python
import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)
shap.summary_plot(shap_values, X_test)
```

**6. Backtesting:**

**Historical Backtesting:**
```python
def backtest_model(model, start_year, end_year):
    results = []
    for year in range(start_year, end_year):
        # Train on data before year
        train_data = data[data['year'] < year]
        test_data = data[data['year'] == year]
        
        model.fit(train_data[features], train_data['BPM_change'])
        predictions = model.predict(test_data[features])
        
        # Calculate accuracy
        actual = test_data['BPM_change']
        accuracy = calculate_accuracy(actual, predictions)
        results.append({'year': year, 'accuracy': accuracy})
    
    return pd.DataFrame(results)
```

**Walk-Forward Validation:**
```python
def walk_forward_validation(data, window_size=3):
    results = []
    for i in range(window_size, len(data)):
        # Train on window of previous years
        train_data = data.iloc[i-window_size:i]
        test_data = data.iloc[i]
        
        model.fit(train_data[features], train_data['BPM_change'])
        prediction = model.predict(test_data[features].reshape(1, -1))
        
        results.append({
            'year': test_data['year'],
            'actual': test_data['BPM_change'],
            'predicted': prediction[0]
        })
    
    return pd.DataFrame(results)
```

**7. Benchmark Comparison:**

**Naive Benchmarks:**
```python
# Benchmark 1: No change (BPM stays same)
naive_pred = data['BPM_from']
naive_mse = mean_squared_error(data['BPM_change'], 0)

# Benchmark 2: Average change
avg_change = data['BPM_change'].mean()
avg_pred = data['BPM_from'] + avg_change
avg_mse = mean_squared_error(data['BPM_change'], avg_change)

# Compare model to benchmarks
model_mse = mean_squared_error(y_test, y_pred)
improvement_over_naive = (naive_mse - model_mse) / naive_mse
improvement_over_avg = (avg_mse - model_mse) / avg_mse
```

**Age Curve:**

```python
def get_age_curve(age):
    # Players peak at 22-23
    if age <= 20:
        return 0.5  # Development phase
    elif age <= 23:
        return 0.2  # Peak phase
    else:
        return -0.3  # Decline phase
```

**Age Curve Improvements:**

**Current Issues:**
- Piecewise linear approximation (too simple)
- Same curve for all players (doesn't account for position, usage, etc.)
- No uncertainty estimates
- Based on general basketball wisdom, not data-driven

**Improvements:**

**1. Data-Driven Age Curves:**
```python
# Fit age curves separately for each position
age_curves = {}
for position in ['PG', 'SG', 'SF', 'PF', 'C']:
    pos_data = data[data['Position'] == position]
    # Fit polynomial to BPM vs age
    coeffs = np.polyfit(pos_data['age'], pos_data['BPM'], degree=2)
    age_curves[position] = np.poly1d(coeffs)

def get_age_curve(age, position):
    return age_curves[position](age) - age_curves[position](22)  # Relative to peak age
```

**2. Hierarchical Age Curves:**
```python
# Fit hierarchical model: position-level and player-level adjustments
import statsmodels.api as sm
import statsmodels.formula.api as smf

model = smf.mixedlm("BPM ~ age + I(age**2) + position", 
                    data, 
                    groups=data["player_key"])
result = model.fit()

def get_age_curve(age, position, player_id=None):
    if player_id:
        # Use player-specific random effects
        player_effect = result.random_effects.get(player_id, 0)
    else:
        player_effect = 0
    
    # Fixed effects
    fixed_pred = result.predict({'age': age, 'position': position})
    return fixed_pred + player_effect
```

**3. Bayesian Age Curves:**
```python
import pymc3 as pm

with pm.Model() as age_model:
    # Priors for age curve parameters
    intercept = pm.Normal('intercept', mu=0, sigma=1)
    linear_coef = pm.Normal('linear_coef', mu=0, sigma=1)
    quadratic_coef = pm.Normal('quadratic_coef', mu=-0.1, sigma=0.5)
    
    # Position-specific adjustments
    position_effect = pm.Normal('position_effect', mu=0, sigma=0.5, shape=5)
    
    # Likelihood
    mu = intercept + linear_coef * data['age'] + quadratic_coef * data['age']**2 + position_effect[data['position_code']]
    sigma = pm.HalfNormal('sigma', sigma=1)
    pm.Normal('BPM', mu=mu, sigma=sigma, observed=data['BPM'])
    
    trace = pm.sample(2000, tune=1000)
```

---

## NIL Service Analysis

### Current Implementation

**Valuation Model:** Weighted percentile-based scoring

**Components:**
- Position rank within cluster (25%)
- Win shares percentile (20%)
- BPM percentile (15%)
- Team success (10%)
- Conference prestige (10%)
- Cluster quality (20%)

**Weight Determination:**
- Current weights are arbitrary
- Based on intuition about NIL market factors
- No validation against actual NIL deals
- No market data to calibrate weights

### Shortcomings

**1. Arbitrary Weight Assignment:**
- Weights chosen without empirical validation
- No sensitivity analysis on weight changes
- May not reflect actual NIL market dynamics

**2. Limited Feature Set:**
- Missing key NIL drivers:
  - Social media following
  - Local market size
  - Personal brand (charisma, story)
  - Academic performance
  - Off-court behavior
  - Media coverage
  - Endorsement history

**3. No Market Calibration:**
- Not calibrated against actual NIL deal values
- No training data from real NIL contracts
- Dollar ranges are estimates, not predictions

**4. Static Model:**
- Doesn't account for NIL market evolution
- No time-based adjustments (market changes rapidly)
- No position-specific NIL patterns

**5. No Uncertainty Estimates:**
- Single point estimate
- No confidence intervals
- No risk assessment

**6. Conference Prestige Simplification:**
- Binary classification (high/mid/low major)
- Doesn't capture nuance within tiers
- No regional market differences

### Improvements

**1. Data-Driven Weight Optimization:**

**If NIL Deal Data Available:**
```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score

# Assume we have historical NIL deal data
X = nil_deal_data[['position_rank', 'win_shares_pct', 'bpm_pct', 
                    'team_success', 'conference_prestige', 'cluster_quality']]
y = nil_deal_data['actual_dollar_value']

# Learn optimal weights
model = LinearRegression(fit_intercept=False)
model.fit(X, y)

# Normalize weights to sum to 1
learned_weights = model.coef_ / model.coef_.sum()

print("Learned weights:")
for feature, weight in zip(X.columns, learned_weights):
    print(f"{feature}: {weight:.2f}")
```

**2. Feature Expansion:**

**Additional Features to Consider:**
```python
NIL_FEATURES = {
    # Performance features (current)
    'position_rank': 0.25,
    'win_shares_pct': 0.20,
    'bpm_pct': 0.15,
    
    # Market features (new)
    'social_media_followers': 0.10,      # Instagram/Twitter followers
    'local_market_size': 0.08,            # DMA market size
    'media_coverage': 0.05,               # Media mentions count
    'google_trends': 0.05,                # Search popularity
    
    # Personal brand features (new)
    'story_score': 0.05,                  # Narrative appeal (underdog, etc.)
    'academic_performance': 0.03,         # GPA, academic awards
    'community_engagement': 0.03,         # Community service
    
    # Team context (current)
    'team_success': 0.10,
    'conference_prestige': 0.10,
    'cluster_quality': 0.20
}
```

**3. Machine Learning Approach:**

**Random Forest for NIL Valuation:**
```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Assume we have NIL deal data
X = nil_data[all_features]
y = nil_data['dollar_value']

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Feature importance
importance = model.feature_importances_
for feature, imp in zip(X.columns, importance):
    print(f"{feature}: {imp:.3f}")

# Predict with uncertainty (using quantile regression)
from sklearn.ensemble import GradientBoostingRegressor

lower_model = GradientBoostingRegressor(loss="quantile", alpha=0.05)
upper_model = GradientBoostingRegressor(loss="quantile", alpha=0.95)
mid_model = GradientBoostingRegressor(loss="quantile", alpha=0.5)

lower_model.fit(X_train, y_train)
upper_model.fit(X_train, y_train)
mid_model.fit(X_train, y_train)

# Get prediction interval
lower_bound = lower_model.predict(X_test)
upper_bound = upper_model.predict(X_test)
median_pred = mid_model.predict(X_test)
```

**4. Market Segmentation:**

**Position-Specific Models:**
```python
# Train separate models for each position
position_models = {}
for position in ['PG', 'SG', 'SF', 'PF', 'C']:
    pos_data = nil_data[nil_data['position'] == position]
    X_pos = pos_data[features]
    y_pos = pos_data['dollar_value']
    
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X_pos, y_pos)
    position_models[position] = model

def predict_nil(player, position):
    return position_models[position].predict(player[features])
```

**5. Time-Series Adjustment:**

**Market Trend Adjustment:**
```python
# Fit NIL market growth trend
market_data = nil_data.groupby('year')['dollar_value'].mean()
market_growth = market_data.pct_change().mean()

def adjust_for_market_trend(base_value, year):
    years_from_baseline = year - baseline_year
    adjusted_value = base_value * (1 + market_growth) ** years_from_baseline
    return adjusted_value
```

**6. Bayesian NIL Valuation:**

**Probabilistic Valuation:**
```python
import pymc3 as pm

with pm.Model() as nil_model:
    # Priors for feature weights
    weights = pm.Dirichlet('weights', a=np.ones(6))
    
    # Linear combination
    mu = pm.math.dot(X, weights)
    
    # Likelihood
    sigma = pm.HalfNormal('sigma', sigma=10000)
    pm.Normal('value', mu=mu, sigma=sigma, observed=y)
    
    trace = pm.sample(2000)

# Get posterior distribution of weights
weight_samples = trace['weights']
weight_mean = weight_samples.mean(axis=0)
weight_ci = np.percentile(weight_samples, [2.5, 97.5], axis=0)
```

**7. Calibration with Real Data:**

**If NIL Deal Data Becomes Available:**
```python
# Collect actual NIL deal data
# Features: player stats, position, team, conference, social media, etc.
# Target: actual deal value

# Train model
from xgboost import XGBRegressor
model = XGBRegressor(n_estimators=200, max_depth=6)
model.fit(X_train, y_train)

# Evaluate
from sklearn.metrics import mean_absolute_error, r2_score
mae = mean_absolute_error(y_test, model.predict(X_test))
r2 = r2_score(y_test, model.predict(X_test))

print(f"MAE: ${mae:,.0f}")
print(f"R²: {r2:.3f}")
```

**8. Ensemble Approach:**

**Combine Multiple Models:**
```python
# Model 1: Weighted scoring (current)
score_valuation = calculate_weighted_score(player)

# Model 2: Machine learning
ml_valuation = ml_model.predict(player_features)

# Model 3: Market comparable
comparable_valuation = find_comparable_deals(player)

# Ensemble
final_valuation = 0.3 * score_valuation + 0.5 * ml_valuation + 0.2 * comparable_valuation
```

---

## Machine Learning: Clustering Deep Dive

### Elbow Method Explained

**Purpose:** Determine optimal number of clusters (k) for K-means clustering

**Algorithm:**
1. Run K-means for different values of k (e.g., k=2 to k=20)
2. Calculate inertia (within-cluster sum of squares) for each k
3. Plot inertia vs k
4. Identify "elbow" point where rate of decrease slows

**Mathematical Definition:**
```
Inertia = Σ Σ ||x - μ||²
        i=1 x∈Ci
```
Where:
- Ci = cluster i
- μ = centroid of cluster i
- x = data point in cluster i

**Implementation:**
```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Normalize data
scaler = StandardScaler()
X_normalized = scaler.fit_transform(player_data[CLUSTER_FEATURES])

# Calculate inertia for different k values
inertias = []
k_range = range(2, 25)

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_normalized)
    inertias.append(kmeans.inertia_)

# Plot elbow curve
plt.figure(figsize=(10, 6))
plt.plot(k_range, inertias, 'bo-')
plt.xlabel('Number of clusters (k)')
plt.ylabel('Inertia')
plt.title('Elbow Method for Optimal k')
plt.grid(True)
plt.show()
```

**Elbow Detection:**
```python
import numpy as np
from kneed import KneeLocator

# Automatic elbow detection
kneedle = KneeLocator(k_range, inertias, curve='convex', direction='decreasing')
optimal_k = kneed.elbow

print(f"Optimal k: {optimal_k}")
```

**Tradeoffs:**
- **Pros:** Simple, visual, intuitive
- **Cons:** Subjective (elbow not always clear), doesn't work for all datasets

**Current Implementation:**
- k=18 selected based on elbow method
- No quantitative validation of elbow point
- May not be truly optimal

### Silhouette Score

**Purpose:** Measure how similar an object is to its own cluster compared to other clusters

**Range:** [-1, 1]
- 1 = well-clustered
- 0 = on cluster boundary
- -1 = misclustered

**Calculation:**
```python
from sklearn.metrics import silhouette_score

silhouette_scores = []
k_range = range(2, 25)

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_normalized)
    score = silhouette_score(X_normalized, labels)
    silhouette_scores.append(score)

# Plot silhouette scores
plt.figure(figsize=(10, 6))
plt.plot(k_range, silhouette_scores, 'bo-')
plt.xlabel('Number of clusters (k)')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Score for Optimal k')
plt.grid(True)
plt.show()

# Optimal k is where silhouette score is maximized
optimal_k = k_range[np.argmax(silhouette_scores)]
```

**Tradeoffs:**
- **Pros:** Quantitative, objective, works well with compact clusters
- **Cons:** Computationally expensive for large datasets, favors convex clusters

### Gap Statistic

**Purpose:** Compare within-cluster dispersion to expected dispersion under null reference distribution

**Advantages:**
- More robust than elbow method
- Statistical framework for cluster selection
- Works well with non-convex clusters

**Implementation:**
```python
from gap_statistic import OptimalK

optimalK = OptimalK(n_refs=5, cluster_array=np.array(X_normalized))
n_clusters = optimalK.run_through()
print(f"Optimal k: {n_clusters}")
```

### Alternative Clustering Algorithms

**1. DBSCAN (Density-Based Spatial Clustering of Applications with Noise):**

**Advantages:**
- Doesn't require specifying k
- Handles outliers well
- Can find arbitrarily shaped clusters
- Robust to noise

**Disadvantages:**
- Sensitive to epsilon and min_samples parameters
- Struggles with varying density clusters
- Doesn't work well with high-dimensional data

**Implementation:**
```python
from sklearn.cluster import DBSCAN

dbscan = DBSCAN(eps=0.5, min_samples=5)
labels = dbscan.fit_predict(X_normalized)

# Number of clusters (excluding noise)
n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
```

**2. Hierarchical Clustering:**

**Advantages:**
- Dendrogram visualization
- No need to specify k upfront
- Captures nested cluster structure
- Works well with small datasets

**Disadvantages:**
- O(n²) time complexity (slow for large datasets)
- Once merged, cannot split
- Sensitive to noise and outliers

**Implementation:**
```python
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage

# Hierarchical clustering
hierarchical = AgglomerativeClustering(n_clusters=18, linkage='ward')
labels = hierarchical.fit_predict(X_normalized)

# Dendrogram
linkage_matrix = linkage(X_normalized, method='ward')
plt.figure(figsize=(12, 8))
dendrogram(linkage_matrix)
plt.title('Hierarchical Clustering Dendrogram')
plt.show()
```

**3. Gaussian Mixture Models (GMM):**

**Advantages:**
- Probabilistic clustering (soft assignments)
- Can model different cluster shapes (ellipsoidal)
- Provides uncertainty estimates
- EM algorithm for parameter estimation

**Disadvantages:**
- Assumes Gaussian distribution (may not hold)
- Requires specifying number of components
- Can converge to local optima
- Sensitive to initialization

**Implementation:**
```python
from sklearn.mixture import GaussianMixture

gmm = GaussianMixture(n_components=18, random_state=42)
labels = gmm.fit_predict(X_normalized)

# Get probabilities (soft assignments)
probabilities = gmm.predict_proba(X_normalized)

# Get uncertainty
uncertainty = 1 - probabilities.max(axis=1)
```

**4. Spectral Clustering:**

**Advantages:**
- Works well with non-convex clusters
- Uses graph Laplacian for clustering
- Can capture complex cluster structures
- Good for image segmentation

**Disadvantages:**
- Computationally expensive (O(n³))
- Requires specifying k
- Sensitive to similarity graph construction
- Memory intensive for large datasets

**Implementation:**
```python
from sklearn.cluster import SpectralClustering

spectral = SpectralClustering(n_clusters=18, affinity='rbf', random_state=42)
labels = spectral.fit_predict(X_normalized)
```

**5. Affinity Propagation:**

**Advantages:**
- Doesn't require specifying k
- Identifies exemplars (representative points)
- Works well with small to medium datasets
- Can find clusters of varying sizes

**Disadvantages:**
- O(n²) time complexity
- Sensitive to damping parameter
- Can be slow for large datasets
- May produce many small clusters

**Implementation:**
```python
from sklearn.cluster import AffinityPropagation

affinity = AffinityPropagation(damping=0.5, random_state=42)
labels = affinity.fit_predict(X_normalized)
n_clusters = len(set(labels))
```

### Cluster Validation

**Current Validation:**
- Silhouette score: ~0.45 (moderate clustering quality)
- Cluster stability: >85% consistency across runs
- Interpretability: Clusters align with basketball positions

**Improved Validation Framework:**

**1. Stability Analysis:**
```python
from sklearn.utils import resample

def cluster_stability(X, n_clusters=18, n_bootstraps=10):
    stability_scores = []
    
    for i in range(n_bootstraps):
        # Bootstrap sample
        X_sample = resample(X, n_samples=len(X), random_state=i)
        
        # Cluster original and sample
        kmeans_original = KMeans(n_clusters=n_clusters, random_state=42)
        labels_original = kmeans_original.fit_predict(X)
        
        kmeans_sample = KMeans(n_clusters=n_clusters, random_state=42)
        labels_sample = kmeans_sample.fit_predict(X_sample)
        
        # Calculate Adjusted Rand Index
        from sklearn.metrics import adjusted_rand_score
        ari = adjusted_rand_score(labels_original, labels_sample)
        stability_scores.append(ari)
    
    return np.mean(stability_scores), np.std(stability_scores)

mean_stability, std_stability = cluster_stability(X_normalized)
print(f"Cluster stability: {mean_stability:.3f} ± {std_stability:.3f}")
```

**2. Davies-Bouldin Index:**
```python
from sklearn.metrics import davies_bouldin_score

db_score = davies_bouldin_score(X_normalized, labels)
print(f"Davies-Bouldin Index: {db_score:.3f}")
# Lower is better (0 = optimal)
```

**3. Calinski-Harabasz Index:**
```python
from sklearn.metrics import calinski_harabasz_score

ch_score = calinski_harabasz_score(X_normalized, labels)
print(f"Calinski-Harabasz Index: {ch_score:.3f}")
# Higher is better
```

**4. Cluster Separation:**
```python
from scipy.spatial.distance import cdist

centroids = kmeans.cluster_centers_
inter_cluster_dist = cdist(centroids, centroids, metric='euclidean')
avg_inter_cluster_dist = inter_cluster_dist[np.triu_indices_from(inter_cluster_dist, k=1)].mean()

print(f"Average inter-cluster distance: {avg_inter_cluster_dist:.3f}")
```

**5. Cluster Compactness:**
```python
intra_cluster_distances = []
for i in range(n_clusters):
    cluster_points = X_normalized[labels == i]
    centroid = centroids[i]
    distances = np.linalg.norm(cluster_points - centroid, axis=1)
    intra_cluster_distances.append(distances.mean())

avg_intra_cluster_dist = np.mean(intra_cluster_distances)
print(f"Average intra-cluster distance: {avg_intra_cluster_dist:.3f}")
```

### Cluster Interpretability

**Current Approach:**
- Qualitative descriptions based on average stats
- Manual inspection of cluster characteristics
- No systematic interpretability analysis

**Improvements:**

**1. Cluster Profiling:**
```python
def profile_cluster(cluster_id, data, labels):
    cluster_data = data[labels == cluster_id]
    overall_data = data
    
    profile = {}
    for feature in CLUSTER_FEATURES:
        cluster_mean = cluster_data[feature].mean()
        overall_mean = overall_data[feature].mean()
        overall_std = overall_data[feature].std()
        
        # Z-score relative to overall population
        z_score = (cluster_mean - overall_mean) / overall_std
        profile[feature] = {
            'cluster_mean': cluster_mean,
            'overall_mean': overall_mean,
            'z_score': z_score,
            'interpretation': interpret_z_score(z_score)
        }
    
    return profile

def interpret_z_score(z):
    if z > 1.5:
        return "Very High"
    elif z > 0.5:
        return "High"
    elif z > -0.5:
        return "Average"
    elif z > -1.5:
        return "Low"
    else:
        return "Very Low"
```

**2. Decision Tree for Cluster Rules:**
```python
from sklearn.tree import DecisionTreeClassifier, export_text

# Train decision tree to predict cluster
tree = DecisionTreeClassifier(max_depth=3, random_state=42)
tree.fit(X_normalized, labels)

# Extract rules
rules = export_text(tree, feature_names=CLUSTER_FEATURES)
print("Cluster decision rules:")
print(rules)
```

**3. SHAP for Cluster Interpretation:**
```python
import shap

# Train a classifier to predict cluster membership
from sklearn.ensemble import RandomForestClassifier
classifier = RandomForestClassifier(n_estimators=100, random_state=42)
classifier.fit(X_normalized, labels)

# SHAP analysis
explainer = shap.TreeExplainer(classifier)
shap_values = explainer.shap_values(X_normalized)

# Summary plot for each cluster
for cluster_id in range(n_clusters):
    cluster_mask = labels == cluster_id
    shap.summary_plot(shap_values[cluster_id], X_normalized[cluster_mask], 
                     feature_names=CLUSTER_FEATURES, 
                     title=f"Cluster {cluster_id} Feature Importance")
```

### Optimal Cluster Count Selection

**Current Selection:**
- k=18 based on elbow method
- No quantitative validation
- May not be truly optimal

**Improved Selection Framework:**

**1. Multiple Metrics Comparison:**
```python
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score

results = []
k_range = range(5, 30)

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_normalized)
    
    sil_score = silhouette_score(X_normalized, labels)
    db_score = davies_bouldin_score(X_normalized, labels)
    ch_score = calinski_harabasz_score(X_normalized, labels)
    
    results.append({
        'k': k,
        'silhouette': sil_score,
        'davies_bouldin': db_score,
        'calinski_harabasz': ch_score
    })

results_df = pd.DataFrame(results)

# Plot all metrics
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

axes[0].plot(results_df['k'], results_df['silhouette'], 'bo-')
axes[0].set_xlabel('k')
axes[0].set_ylabel('Silhouette Score')
axes[0].set_title('Silhouette Score (higher is better)')

axes[1].plot(results_df['k'], results_df['davies_bouldin'], 'ro-')
axes[1].set_xlabel('k')
axes[1].set_ylabel('Davies-Bouldin Index')
axes[1].set_title('Davies-Bouldin Index (lower is better)')

axes[2].plot(results_df['k'], results_df['calinski_harabasz'], 'go-')
axes[2].set_xlabel('k')
axes[2].set_ylabel('Calinski-Harabasz Index')
axes[2].set_title('Calinski-Harabasz Index (higher is better)')

plt.tight_layout()
plt.show()
```

**2. Consensus Clustering:**
```python
# Run multiple clustering algorithms and find consensus
from sklearn.cluster import KMeans, AgglomerativeClustering, SpectralClustering

algorithms = [
    ('KMeans', KMeans(n_clusters=18, random_state=42)),
    ('Agglomerative', AgglomerativeClustering(n_clusters=18)),
    ('Spectral', SpectralClustering(n_clusters=18, affinity='rbf'))
]

clusterings = []
for name, algorithm in algorithms:
    labels = algorithm.fit_predict(X_normalized)
    clusterings.append(labels)

# Calculate consensus using majority voting
from scipy.stats import mode
consensus_labels = mode(clusterings, axis=0)[0][0]
```

**3. Domain-Driven Cluster Count:**

**Basketball-Specific Considerations:**
- Number of positions: 5 (PG, SG, SF, PF, C)
- Number of hybrid positions: ~5-10 (combo guards, stretch 4s, etc.)
- Number of roles: ~10-15 (starter, sixth man, specialist, etc.)
- Total: 18-30 clusters reasonable

**Recommendation:**
- Start with k=18 (current)
- Validate with multiple metrics
- Adjust based on interpretability
- Consider business needs (not too granular, not too broad)

### 4. Player Graph (PORTALMANIA Game)

**File:** `backend/app/core/player_graph.py`

**Technology:** NetworkX graph library

**Graph Construction:**

```python
class PlayerGraph:
    def load_from_roster_data(self, conferences=None, years=None):
        # 1. Load roster data for all years
        roster_df = load_roster_data(conferences, years)
        
        # 2. Group by team and year
        grouped = roster_df.groupby(['Team', 'year'])
        
        # 3. For each team/year, connect all players
        for (team, year), group in grouped:
            player_ids = group['Sourceid'].tolist()
            
            # Create complete graph (all players connected)
            for i in range(len(player_ids)):
                for j in range(i + 1, len(player_ids)):
                    self.graph.add_edge(player_ids[i], player_ids[j])
        
        # 4. Store player info
        for player_id, info in player_data.items():
            self.player_info[player_id] = {
                'name': info['name'],
                'teams': list(info['teams']),
                'years': sorted(info['years']),
                'position': info['position'],
                # ...
            }
```

**Shortest Path Algorithm:**

```python
def get_shortest_path(self, player_id1, player_id2):
    # Use NetworkX's built-in shortest path (BFS)
    try:
        path = nx.shortest_path(self.graph, player_id1, player_id2)
        
        # Convert to player info
        path_info = []
        for pid in path:
            info = self.player_info.get(pid, {'id': pid, 'name': 'Unknown'})
            path_info.append(info)
        
        return path_info
    except nx.NetworkXNoPath:
        return None  # No connection exists
```

**Random Pair Generation (Optimized):**

```python
def get_random_reachable_pair(self, min_distance=3, max_distance=6):
    # Optimization: Use BFS instead of checking all pairs
    for _ in range(max_attempts):
        start_id = random.choice(list(self.graph.nodes()))
        
        # BFS to find nodes within distance range
        lengths = nx.single_source_shortest_path_length(
            self.graph, start_id, cutoff=max_distance
        )
        
        # Filter nodes in desired range
        nodes_in_range = [
            (node_id, length) 
            for node_id, length in lengths.items() 
            if min_distance <= length <= max_distance
        ]
        
        if nodes_in_range:
            target_id, distance = random.choice(nodes_in_range)
            return {
                'start_player': self.player_info[start_id],
                'end_player': self.player_info[target_id],
                'distance': distance
            }
```

### 5. NIL Service

**File:** `backend/app/services/nil_service.py`

**Valuation Model:** Weighted percentile-based scoring

**Components:**

```python
NIL_SCORE_WEIGHTS = {
    'position_rank': 0.25,      # Rank within cluster
    'win_shares_pct': 0.20,     # Win shares percentile
    'bpm_pct': 0.15,            # BPM percentile
    'team_success': 0.10,       # Team adjusted net rating
    'conference_prestige': 0.10, # Conference tier
    'cluster_quality': 0.20,     # Cluster average BPM
}
```

**Calculation:**

```python
def calculate_player_nil(player):
    # 1. Get cluster assignment
    cluster = player['cluster']
    
    # 2. Calculate position rank within cluster
    position_rank = get_percentile_rank(
        player['BPM'], 
        get_cluster_bpm_distribution(cluster)
    )
    
    # 3. Get cluster quality (0.15 to 1.0 based on avg BPM)
    cluster_quality = CLUSTER_QUALITY_MAP[cluster]
    
    # 4. Calculate conference prestige multiplier
    conference_prestige = CONFERENCE_PRESTIGE_MAP[player['conf']]
    
    # 5. Calculate team success (0-100 based on adj_net)
    team_success = normalize_team_success(player['team_adj_net'])
    
    # 6. Calculate win shares and BPM percentiles
    win_shares_pct = calculate_win_shares_percentile(player)
    bpm_pct = calculate_bpm_percentile(player)
    
    # 7. Weighted sum
    nil_score = (
        position_rank * 0.25 +
        win_shares_pct * 0.20 +
        bpm_pct * 0.15 +
        team_success * 0.10 +
        conference_prestige * 100 * 0.10 +
        cluster_quality * 100 * 0.20
    )
    
    # 8. Convert to dollar range
    dollar_value = score_to_dollars(nil_score)
    
    return {
        'nil_score': nil_score,
        'dollar_value': dollar_value,
        'components': {
            'position_rank': position_rank,
            'win_shares_pct': win_shares_pct,
            'bpm_pct': bpm_pct,
            'team_success': team_success,
            'conference_prestige': conference_prestige,
            'cluster_quality': cluster_quality,
        }
    }
```

---

## Machine Learning Pipeline

### 1. Player Clustering

**File:** `backend/scripts/modeling/cluster_players.py`

**Algorithm:** K-Means Clustering

**Process:**

```python
# 1. Feature selection
CLUSTER_FEATURES = [
    'Usage', 'BPM', 'eFG%', 'AST%', 'ORB%', 'DRB%',
    'STL%', 'BLK%', 'TOV%', 'FTR'
]

# 2. Normalization
scaler = StandardScaler()
X_normalized = scaler.fit_transform(player_data[CLUSTER_FEATURES])

# 3. Determine optimal k (Elbow Method)
inertias = []
for k in range(5, 25):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X_normalized)
    inertias.append(kmeans.inertia_)

# Optimal k = 18 (based on elbow point)

# 4. Fit final model
kmeans = KMeans(n_clusters=18, random_state=42)
clusters = kmeans.fit_predict(X_normalized)

# 5. Assign cluster labels
player_data['cluster'] = clusters

# 6. Generate cluster descriptions
for cluster_id in range(18):
    cluster_players = player_data[player_data['cluster'] == cluster_id]
    description = {
        'cluster_id': cluster_id,
        'avg_bpm': cluster_players['BPM'].mean(),
        'avg_usage': cluster_players['Usage'].mean(),
        'player_count': len(cluster_players),
        'characteristics': extract_characteristics(cluster_players)
    }
```

**Cluster Descriptions:**
- 18 clusters (IDs 0-17)
- Each cluster has distinct statistical profile
- Descriptions include average BPM, usage, and qualitative characteristics
- Used for player similarity and projections

### 2. BPM Projection Model

**File:** `backend/scripts/modeling/train_bpm_projection_model.py`

**Algorithm:** Random Forest Regression

**Feature Engineering:**

```python
# Base features
BASE_FEATURES = [
    'BPM_from', 'Usage_from', 'eFG_from', 'AST_from',
    'ORB_from', 'DRB_from', 'STL_from', 'BLK_from',
    'age', 'height', 'team_adj_em'
]

# Interaction features
INTERACTION_FEATURES = [
    'usage_efficiency',  # Usage * eFG%
    'age_usage',         # Age * Usage
    'bpm_usage',         # BPM * Usage
]

# Lag features
LAG_FEATURES = [
    'BPM_lag1',  # BPM from previous season
    'BPM_lag2',  # BPM from 2 seasons ago
    'Usage_lag1', # Usage from previous season
]

# Combine all features
ALL_FEATURES = BASE_FEATURES + INTERACTION_FEATURES + LAG_FEATURES
```

**Model Training:**

```python
# 1. Load historical YoY data
modeling_df = pd.read_csv('bpm_change_modeling_data.csv')

# 2. Prepare features and target
X = modeling_df[ALL_FEATURES]
y = modeling_df['bpm_change']  # Target: BPM change from year N to N+1

# 3. Handle missing values
X = X.fillna(X.median())

# 4. Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 5. Train Random Forest
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# 6. Evaluate
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

# Results: R² = 0.45, RMSE = 1.8 BPM
```

**Feature Importance:**
1. Previous season BPM: 35%
2. Age: 20%
3. Usage rate: 15%
4. BPM change: 10%
5. Team context: 8%
6. Other features: 12%

**Projection Generation:**

```python
# 1. Load 2026 player data
players_2026 = load_players(year=2026)

# 2. Prepare features for 2026
X_2026 = prepare_features(players_2026)

# 3. Predict BPM change
bpm_change_pred = model.predict(X_2026)

# 4. Calculate 2027 BPM
players_2026['BPM_2027'] = players_2026['BPM'] + bpm_change_pred

# 5. Apply age adjustment
players_2026['BPM_2027'] += players_2026['age'].apply(get_age_curve)

# 6. Save projections
players_2026.to_csv('bpm_projections_2027.csv.gz', compression='gzip')
```

---

## API Architecture

### Route Structure

**File:** `backend/app/main.py`

**Router Organization:**

```python
# API routers organized by domain
app.include_router(players_router, prefix="/api/v1", tags=["players"])
app.include_router(teams_router, prefix="/api/v1", tags=["teams"])
app.include_router(moves_router, prefix="/api/v1", tags=["moves"])
app.include_router(badges_router, prefix="/api/v1", tags=["badges"])
app.include_router(radar_router, prefix="/api/v1", tags=["radar"])
app.include_router(sim_router, prefix="/api/v1", tags=["similarity"])
app.include_router(years_router, prefix="/api/v1", tags=["years"])
app.include_router(evolution_router, prefix="/api/v1", tags=["evolution"])
app.include_router(history_router, prefix="/api/v1", tags=["history"])
app.include_router(game_router, prefix="/api/v1", tags=["game"])
app.include_router(utilization_router, prefix="/api/v1", tags=["utilization"])
app.include_router(nil_router, prefix="/api/v1", tags=["nil"])
app.include_router(projections_router, prefix="/api/v1", tags=["projections"])
app.include_router(clusters_router, prefix="/api/v1", tags=["clusters"])
```

### Middleware Stack

```python
# 1. Error handling middleware
app.add_middleware(ErrorHandlerMiddleware)

# 2. Logging middleware
app.add_middleware(LoggingMiddleware)

# 3. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### Lifecycle Management

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Build cache
    build_cache()
    
    yield
    
    # Shutdown: Cleanup (if needed)
    pass

app = FastAPI(
    title="Jeevs CBB API",
    description="College Basketball Analytics API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)
```

---

## Performance Optimizations

### 1. Data Loading Optimizations

**Lazy Loading:**
- Player vectors loaded on startup (cached)
- Game data loaded on-demand (per year)
- Projection data loaded when first accessed

**Compression:**
- CSV files compressed with gzip (70-80% reduction)
- JSON game data compressed (85% reduction)
- Pandas reads compressed files natively

**Caching:**
- Player vectors cached in pickle format
- Cache invalidation based on file modification times
- Metadata tracking for cache validity

### 2. Query Optimizations

**Filter Before Transform:**
```python
# Bad: Transform all data, then filter
data = transform_all(df)
filtered = data[data['year'] == 2026]

# Good: Filter first, then transform
filtered = df[df['year'] == 2026]
data = transform(filtered)
```

**Pagination Before Expensive Operations:**
```python
# Apply pagination BEFORE derived stat calculations
paginated_data = data.iloc[offset:offset + limit]
paginated_data = _calculate_derived_stats(paginated_data)
```

**Vectorized Operations:**
```python
# Use pandas vectorized operations instead of loops
# Bad:
for idx, row in df.iterrows():
    df.loc[idx, 'PPG'] = row['Points'] / row['Games']

# Good:
df['PPG'] = df['Points'] / df['Games']
```

### 3. Similarity Search Optimizations

**Precomputed Vectors:**
- All player vectors computed at startup
- Stored in memory for O(1) access
- Avoids recomputation on each request

**Normalized Vectors:**
- Vectors normalized once during cache building
- Cosine similarity becomes simple dot product
- Faster similarity calculations

**Efficient Neighbor Search:**
```python
# Use sklearn's NearestNeighbors for O(log n) search
nn = NearestNeighbors(n_neighbors=20, metric='cosine')
nn.fit(vectors)
distances, indices = nn.kneighbors([query_vector])
```

### 4. Graph Optimizations

**BFS for Shortest Path:**
- NetworkX uses efficient BFS algorithm
- O(V + E) complexity
- Early termination with distance cutoff

**Random Pair Generation:**
- Use BFS from random start instead of checking all pairs
- Reduces from O(n²) to O(n) average case
- Cutoff at max_distance for early termination

---

## Data Models & Schemas

### Pydantic Schemas

**File:** `backend/app/models/schemas.py`

**Query Parameters:**

```python
class PlayerQueryParams(BaseModel):
    year: Optional[Union[int, str]] = None
    conf: Optional[str] = None
    search: Optional[str] = None
    dataTier: Optional[str] = None
    d1Only: bool = False
    highMajorOnly: bool = False
    sort: str = "BPM"
    order: str = "desc"
    limit: int = 50
    offset: int = 0
```

**Response Models:**

```python
class PlayerResponse(BaseModel):
    player: Dict[str, Any]
    available_years: List[int]

class PlayerListResponse(BaseModel):
    count: int
    filtered_count: int
    results: List[Dict[str, Any]]
```

### Data Tiers

**Basic Tier:**
- Complete coverage (~15,000 players)
- Basic stats (PPG, RPG, APG, BPM)
- Roster info (height, weight, hometown)
- No tracking data

**Enriched Tier:**
- Subset of players (~60%)
- Advanced metrics (RAPM, tracking data)
- Efficiency breakdowns
- Shot location data

---

## Deployment Architecture

### Environment Configuration

**File:** `backend/app/core/config.py`

```python
class Settings(BaseSettings):
    # API Configuration
    api_title: str = "Jeevs CBB API"
    api_version: str = "1.0.0"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # Data Configuration
    data_dir: str = "data"
    
    # Pagination Defaults
    default_limit: int = 50
    max_limit: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

### Railway Deployment

**File:** `backend/railway.toml`

```toml
[build]
builder = "NIXPACKS"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
```

**Deployment Process:**
1. Code pushed to GitHub
2. Railway detects changes
3. Builds Docker image using Nixpacks
4. Deploys to container
5. Health check on `/health` endpoint
6. Auto-restart on failure

---

## Key Technical Decisions

### 1. Why FastAPI?

**Chosen for:**
- Native async/await support (high performance)
- Automatic API documentation (Swagger/ReDoc)
- Pydantic integration (type safety)
- Modern Python standards
- Easy testing and validation

**Alternatives considered:**
- Flask: Less performant, no native async
- Django: Overkill for API-only, heavier footprint

### 2. Why Pandas for Data?

**Chosen for:**
- Efficient DataFrame operations
- Built-in CSV/JSON handling
- Vectorized computations (fast)
- Easy data joining and aggregation
- Large ecosystem of data tools

**Trade-offs:**
- Memory-intensive for large datasets
- Not ideal for real-time streaming
- Mitigated by compression and caching

### 3. Why K-Means for Clustering?

**Chosen for:**
- Simple and interpretable
- Fast for large datasets
- Scales well with data size
- Easy to implement with scikit-learn

**Alternatives considered:**
- DBSCAN: Better for arbitrary shapes, but harder to parameterize
- Hierarchical: More interpretable, but slower
- Gaussian Mixture: More flexible, but overkill

### 4. Why Cosine Similarity?

**Chosen for:**
- Captures similarity in direction, not magnitude
- Works well with normalized vectors
- Fast computation (dot product)
- Standard approach for recommendation systems

**Alternatives considered:**
- Euclidean distance: Sensitive to magnitude
- Manhattan distance: Less intuitive for high-dimensional data
- Jaccard similarity: Better for binary/categorical data

### 5. Why NetworkX for Graph?

**Chosen for:**
- Easy-to-use Python API
- Efficient graph algorithms
- Built-in shortest path (BFS)
- Good documentation

**Alternatives considered:**
- Custom implementation: More control, but more work
- Neo4j: Overkill for this use case
- igraph: Faster, but harder to install

### 6. Why Gzip Compression?

**Chosen for:**
- 70-85% file size reduction
- Pandas native support
- Fast decompression
- No external dependencies

**Trade-offs:**
- Slightly slower initial load
- Cannot inspect files directly
- Mitigated by caching

### 7. Why Pickle for Caching?

**Chosen for:**
- Python native serialization
- Fast serialization/deserialization
- Preserves Python objects
- Easy to implement

**Trade-offs:**
- Not language-agnostic
- Security concerns (untrusted data)
- Mitigated by only caching internal data

---

## Monitoring & Logging

### Logging Configuration

**File:** `backend/app/utils/logger.py`

```python
import logging

def setup_logging():
    logging.basicConfig(
        level=settings.log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            # Add file handler in production
        ]
    )
```

### Health Check Endpoint

```python
@app.get("/health")
@limiter.limit("100/minute")
async def health_check(request: Request):
    return {
        "status": "healthy",
        "version": settings.api_version,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Error Handling

**Middleware:** `backend/app/middleware/error_handler.py`

```python
class ErrorHandlerMiddleware:
    async def __call__(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"}
            )
```

---

## Testing Strategy

### Backend Tests

**File:** `backend/tests/`

**Test Types:**
- Unit tests for service methods
- Integration tests for API endpoints
- Data validation tests

**Example Test:**

```python
def test_get_players():
    params = PlayerQueryParams(year=2026, limit=10)
    response = PlayerService.get_players(params)
    
    assert response.count > 0
    assert len(response.results) <= 10
    assert all('player_name' in p for p in response.results)
```

---

## Future Improvements

### Potential Enhancements

1. **Database Migration:**
   - Move from CSV files to PostgreSQL
   - Enable complex queries and joins
   - Improve data consistency

2. **Real-time Updates:**
   - WebSocket support for live updates
   - Push notifications for game data
   - Real-time leaderboards

3. **Advanced ML:**
   - Deep learning for projections
   - Neural networks for similarity
   - Reinforcement learning for strategy

4. **Distributed Caching:**
   - Redis for distributed cache
   - Improved cache invalidation
   - Better scalability

5. **API Versioning:**
   - Formal versioning strategy
   - Backward compatibility
   - Deprecation policy

---

## Summary

JEEVS CBB's backend architecture is built on:

- **FastAPI** for high-performance API serving
- **Pandas** for efficient data processing
- **Scikit-learn** for machine learning models
- **NetworkX** for graph algorithms
- **Pydantic** for data validation
- **Gzip** for data compression
- **Pickle** for caching

The system processes data from multiple sources, applies ML models for player analysis, and serves results through a RESTful API. Key optimizations include compression, caching, vectorized operations, and efficient algorithms for similarity search and graph traversal.

The architecture is modular, scalable, and maintainable, with clear separation of concerns across layers (API, service, core, feature, cache, data).

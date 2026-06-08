# System Architecture

## Overview

JEEVS CBB is a full-stack web application for college basketball analytics. The system consists of a FastAPI backend, Next.js frontend, and data processing pipeline for handling large-scale basketball statistics.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Pages       │  │  Components  │  │  Hooks       │         │
│  │  (Routes)    │  │  (UI)        │  │  (Data)      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│                    ┌───────▼───────┐                            │
│                    │  API Client   │                            │
│                    │  (lib/api.ts) │                            │
│                    └───────┬───────┘                            │
└────────────────────────────┼────────────────────────────────────┘
                             │ HTTP/REST
┌────────────────────────────▼────────────────────────────────────┐
│                         Backend (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  API Routes  │  │  Services    │  │  Core        │         │
│  │  (Endpoints) │  │  (Business)  │  │  (Data)      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│                    ┌───────▼───────┐                            │
│                    │  Data Loader  │                            │
│                    │  (CSV/JSON)   │                            │
│                    └───────┬───────┘                            │
└────────────────────────────┼────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                         Data Storage                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  CSV Files   │  │  JSON Files  │  │  Cache       │         │
│  │  (Players)   │  │  (Games)     │  │  (Vectors)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Frontend

**Framework:** Next.js 14 (React)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** React Hooks
- **Data Fetching:** Native fetch API
- **Charts:** Victory
- **Maps:** React Simple Maps
- **Icons:** Lucide React

**Key Libraries:**
- `next` - React framework
- `react` - UI library
- `typescript` - Type safety
- `tailwindcss` - Utility-first CSS
- `victory` - Charting library
- `react-simple-maps` - Map visualization

---

### Backend

**Framework:** FastAPI (Python 3.11+)
- **Language:** Python
- **Data Processing:** Pandas, NumPy
- **API Documentation:** OpenAPI/Swagger (auto-generated)
- **Rate Limiting:** SlowAPI
- **CORS:** FastAPI CORS middleware

**Key Libraries:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `scikit-learn` - Machine learning (clustering, projections)
- `slowapi` - Rate limiting
- `pydantic` - Data validation

---

### Data Storage

**File-based Storage:**
- **CSV Files:** Player and team statistics (compressed with gzip)
- **JSON Files:** Game-by-game data (compressed with gzip)
- **Pickle Files:** Cached similarity vectors
- **JSON Files:** Cluster descriptions and metadata

**Why File-based?**
- Simplicity for current scale
- No database overhead
- Easy version control with git
- Sufficient for read-heavy workload
- Compression reduces storage needs

**Future Considerations:**
- PostgreSQL for production scaling
- Redis for caching layer
- S3 for data file storage

---

## Project Structure

### Backend Structure

```
backend/
├── app/
│   ├── api/              # API route handlers
│   │   ├── players.py    # Player endpoints
│   │   ├── teams.py      # Team endpoints
│   │   ├── projections.py # Projection endpoints
│   │   ├── clusters.py   # Cluster endpoints
│   │   ├── similarity.py # Similarity endpoints
│   │   ├── moves.py      # Transfer/moves endpoints
│   │   ├── badges.py     # Badge endpoints
│   │   ├── radar.py      # Radar chart endpoints
│   │   ├── evolution.py  # Player evolution endpoints
│   │   ├── history.py    # Player history endpoints
│   │   ├── game.py       # Game (PORTALMANIA) endpoints
│   │   ├── utilization.py # Usage analysis endpoints
│   │   ├── nil.py        # NIL valuation endpoints
│   │   └── years.py      # Years endpoint
│   ├── services/         # Business logic layer
│   │   ├── player_service.py
│   │   ├── team_service.py
│   │   ├── projection_service.py
│   │   ├── similarity_service.py
│   │   ├── evolution_service.py
│   │   └── nil_service.py
│   ├── core/             # Core functionality
│   │   ├── data_loader.py      # Data loading logic
│   │   ├── player_resolver.py  # Player ID resolution
│   │   ├── team_resolver.py    # Team resolution
│   │   ├── player_graph.py      # Player graph for game
│   │   ├── team_data_loader.py  # Team data loading
│   │   ├── config.py           # Configuration
│   │   └── year_utils.py        # Year utilities
│   ├── cache/            # Caching layer
│   │   └── player_vectors.py   # Similarity vector cache
│   ├── features/         # Feature calculations
│   │   ├── badges.py
│   │   ├── moves.py
│   │   └── vectors.py
│   ├── models/           # Data models
│   │   ├── schemas.py
│   │   └── similarity.py
│   ├── middleware/       # Custom middleware
│   │   └── error_handler.py
│   ├── utils/            # Utilities
│   │   ├── logger.py
│   │   └── bpm_calculator.py
│   └── main.py           # Application entry point
├── data/                 # Data files
│   ├── players/          # Player CSV files
│   ├── teams/            # Team CSV files
│   ├── games/            # Game JSON files
│   └── aggregate/        # Aggregated data
├── scripts/              # Data processing scripts
│   ├── data_processing/  # Data ingestion/enrichment
│   ├── analysis/         # Analysis scripts
│   ├── modeling/         # ML model training
│   └── utilities/        # Utility scripts
├── tests/                # Backend tests
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variables template
```

---

### Frontend Structure

```
frontend/
├── app/                  # Next.js app directory
│   ├── layout.tsx        # Root layout
│   ├── page.tsx          # Home page
│   ├── player/           # Player pages
│   │   ├── [id]/         # Player detail page
│   │   │   ├── page.tsx
│   │   │   └── games/    # Player games page
│   ├── team/             # Team pages
│   │   ├── [id]/         # Team detail page
│   ├── clusters/         # Cluster pages
│   │   ├── page.tsx
│   │   └── leaderboard/  # Cluster leaderboard
│   ├── game/             # Game (PORTALMANIA) page
│   ├── leaderboard/      # Leaderboard pages
│   ├── moves/            # Moves rankings
│   ├── similarity/       # Similarity map
│   ├── teams/            # Team catalog
│   ├── team-rankings/    # Team rankings
│   ├── projections/      # Projections pages
│   └── docs/             # Documentation pages
├── components/           # React components
│   ├── player/           # Player-related components
│   ├── team/             # Team-related components
│   └── ui/               # Reusable UI components
├── hooks/                # Custom React hooks
│   ├── usePlayers.ts
│   ├── useYears.ts
│   ├── useProjections.ts
│   ├── useHistoricalBpm.ts
│   ├── useMovesRankings.ts
│   └── useClusterBpmDistribution.ts
├── lib/                  # Utility libraries
│   ├── api.ts            # API client
│   ├── api-client.ts     # Alternative API client
│   ├── utils.ts          # Utility functions
│   ├── config.ts         # Configuration
│   ├── cityCoordinates.ts # City coordinates for maps
│   ├── badgeIcons.ts     # Badge icon mappings
│   ├── positionLabels.ts # Position label mappings
│   └── yearClassMap.ts   # Year/class mappings
├── types/                # TypeScript type definitions
├── __tests__/            # Frontend tests
├── .env.example          # Environment variables template
├── next.config.js        # Next.js configuration
├── tailwind.config.js    # Tailwind configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Node dependencies
```

---

## Data Flow

### 1. API Request Flow

```
User Action
    ↓
Frontend Component
    ↓
API Client (lib/api.ts)
    ↓
HTTP Request (GET/POST)
    ↓
FastAPI Route Handler
    ↓
Service Layer (Business Logic)
    ↓
Data Loader (Data Access)
    ↓
File System (CSV/JSON)
    ↓
Response Processing
    ↓
Frontend Display
```

---

### 2. Data Loading Flow

**Startup:**
1. FastAPI application starts
2. `lifespan()` function runs
3. `build_cache()` loads similarity vectors
4. `data_loader.py` loads player data into memory
5. Application ready to serve requests

**Request:**
1. API endpoint receives request
2. Service layer processes request
3. Data loader checks cache
4. If cache miss, load from file (with gzip decompression)
5. Return data to service layer
6. Service layer applies business logic
7. Return response to API layer
8. API layer serializes and returns JSON

---

### 3. Similarity Search Flow

```
Request: /api/v1/similarity/nearest/{player_id}
    ↓
Check cache for player vectors
    ↓
If cached, use cached vectors
    ↓
If not cached, compute similarity
    ↓
Calculate cosine similarity between vectors
    ↓
Sort by similarity score
    ↓
Return top N similar players
```

---

## Key Components

### 1. Data Loader (`app/core/data_loader.py`)

**Responsibilities:**
- Load player data from CSV files
- Handle gzip compression automatically
- Merge basic and enriched data tiers
- Create lookup dictionaries for efficient queries
- Calculate derived statistics (PPG, RPG, APG)

**Key Functions:**
- `read_csv_with_compression()` - Smart CSV reading with gzip support
- `load_all_players()` - Combines all player data sources
- `load_enriched_players()` - Loads enriched tier data
- `load_basic_players()` - Loads basic tier data
- `load_torvik_players()` - Loads Torvik-specific data

**Caching Strategy:**
- Data loaded once at startup
- Stored in module-level variables
- No expiration (historical data doesn't change)
- Memory footprint: ~500MB for full dataset

---

### 2. Service Layer

**Player Service (`services/player_service.py`):**
- Player filtering and sorting
- Pagination
- Data tier selection
- Derived stat calculation
- Search functionality

**Team Service (`services/team_service.py`):**
- Team data retrieval
- Team filtering
- Roster construction
- Team statistics aggregation

**Projection Service (`services/projection_service.py`):**
- BPM projection loading
- Projection leaderboard generation
- Cluster-based projections
- Confidence interval calculation

**Similarity Service (`services/similarity_service.py`):**
- Similarity vector management
- Nearest neighbor search
- Position precomputation
- Similarity scoring

---

### 3. API Layer

**Route Handlers:**
- Request validation using Pydantic
- Query parameter parsing
- Error handling
- Response serialization
- Rate limiting

**Middleware:**
- Error handling middleware
- Logging middleware
- CORS middleware
- Rate limiting middleware

---

### 4. Frontend API Client

**Location:** `frontend/lib/api.ts`

**Responsibilities:**
- Centralized API communication
- Error handling
- Type-safe requests
- Base URL configuration
- Request/response transformation

**Key Functions:**
- `fetchPlayer()` - Get player data
- `fetchAllPlayers()` - Get player list with filters
- `fetchPlayerGames()` - Get player game log
- `fetchPlayerSimilar()` - Get similar players
- `fetchTeam()` - Get team data
- `fetchProjections()` - Get projections

---

## Performance Optimization

### Backend Optimizations

1. **In-Memory Caching:**
   - Player data loaded at startup
   - Similarity vectors cached
   - Game data cached per year
   - Reduces file I/O by 90%+

2. **Data Compression:**
   - CSV files compressed with gzip (70-80% reduction)
   - JSON game files compressed (85% reduction)
   - Automatic decompression on read
   - Faster network transfer for deployments

3. **Efficient Data Structures:**
   - Pandas DataFrames for vectorized operations
   - Dictionary lookups for O(1) access
   - Precomputed indexes for common queries
   - Sorted data for binary search

4. **Lazy Loading:**
   - Game data loaded on first request per year
   - Historical data loaded only when needed
   - Cluster data loaded on demand
   - Projection data loaded on demand

---

### Frontend Optimizations

1. **Code Splitting:**
   - Next.js automatic code splitting
   - Route-based splitting
   - Dynamic imports for heavy components

2. **Memoization:**
   - React.memo for component optimization
   - useMemo for expensive calculations
   - useCallback for function stability

3. **Data Fetching:**
   - Client-side fetching for user interactions
   - Server components for initial data
   - Optimistic UI updates

4. **Bundle Optimization:**
   - Tree shaking
   - Minification
   - Image optimization

---

## Security

### Current Security Measures

1. **CORS Configuration:**
   - Configured allowed origins
   - Credentials handling
   - Method restrictions

2. **Rate Limiting:**
   - 100 requests/minute per IP
   - Prevents abuse
   - Configurable per endpoint

3. **Input Validation:**
   - Pydantic models for request validation
   - Type checking
   - Pattern validation

4. **Error Handling:**
   - Generic error messages
   - No stack traces in production
   - Proper HTTP status codes

### Future Security Enhancements

1. **Authentication:**
   - JWT tokens for API access
   - OAuth integration
   - User accounts

2. **API Keys:**
   - Rate limiting per API key
   - Usage tracking
   - Access control

3. **HTTPS:**
   - SSL/TLS encryption
   - Secure cookies
   - HSTS headers

4. **Input Sanitization:**
   - SQL injection prevention (if database added)
   - XSS prevention
   - CSRF protection

---

## Deployment Architecture

### Development Environment

**Frontend:**
- Runs on `localhost:3000`
- Hot reload enabled
- API proxy to backend

**Backend:**
- Runs on `localhost:8000`
- Auto-reload with uvicorn
- Debug mode enabled
- API docs at `/docs`

---

### Production Deployment

**Current Setup:**
- Frontend: Vercel (or similar)
- Backend: Railway (or similar)
- Data: Included in deployment (compressed files)

**Recommended Architecture:**

```
┌─────────────────┐
│   CDN (Vercel)  │
│   Frontend      │
└────────┬────────┘
         │
         │ HTTPS
         │
┌────────▼────────┐
│   Load Balancer │
└────────┬────────┘
         │
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│ App 1 │ │ App 2 │
│ (API) │ │ (API) │
└───┬───┘ └──┬────┘
    │         │
    └────┬────┘
         │
┌────────▼────────┐
│   Data Storage  │
│   (Files/S3)    │
└─────────────────┘
```

**Scaling Considerations:**
- Horizontal scaling for API
- CDN for static assets
- Caching layer (Redis)
- Database for persistent storage

---

## Monitoring and Logging

### Current Logging

**Backend:**
- Structured logging with custom logger
- Request/response logging
- Error logging
- Performance metrics

**Frontend:**
- Console logging in development
- Error boundary for crashes
- Network error handling

### Future Monitoring

1. **Application Performance Monitoring (APM):**
   - Response time tracking
   - Error rate monitoring
   - Request volume tracking

2. **Uptime Monitoring:**
   - Health check endpoints
   - Automated alerts
   - Status page

3. **Analytics:**
   - User behavior tracking
   - Feature usage
   - Performance metrics

---

## Development Workflow

### Local Development

1. **Backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Data Updates

1. **Download Data:**
   - Run data ingestion scripts
   - Scripts in `backend/scripts/data_processing/`

2. **Process Data:**
   - Run enrichment scripts
   - Generate clusters
   - Train projection models

3. **Compress Data:**
   ```bash
   cd backend
   python compress_data.py
   python compress_game_data.py
   ```

4. **Deploy:**
   - Commit changes
   - Push to repository
   - Trigger deployment

---

## Testing Strategy

### Backend Testing

**Unit Tests:**
- Service layer logic
- Data loading functions
- Utility functions

**Integration Tests:**
- API endpoints
- Data flow
- Error handling

**Test Framework:** pytest

---

### Frontend Testing

**Unit Tests:**
- Component rendering
- Hook behavior
- Utility functions

**Integration Tests:**
- User flows
- API interactions
- Navigation

**Test Framework:** Jest + React Testing Library

---

## Future Enhancements

### Short Term

1. **Database Migration:**
   - Move from file-based to PostgreSQL
   - Improve query performance
   - Enable complex queries

2. **Caching Layer:**
   - Add Redis for distributed caching
   - Improve cache invalidation
   - Reduce memory footprint

3. **API Authentication:**
   - Add user authentication
   - API key management
   - Rate limiting per user

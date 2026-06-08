# JEEVS CBB - College Basketball Analytics

A comprehensive full-stack application for college basketball analytics, featuring advanced player statistics, machine learning models, and interactive visualizations.

**GitHub Repository:** [https://github.com/Jeevs10/jeevs-cbb](https://github.com/Jeevs10/jeevs-cbb)

## 🏀 Features

- **Player Analytics**: Advanced statistics including BPM, usage rates, efficiency metrics
- **Player Clustering**: ML-derived player archetypes (18 clusters based on statistical profiles)
- **Similarity Analysis**: Find similar players using cosine similarity on feature vectors
- **BPM Projections**: Machine learning projections for future season performance
- **Interactive Leaderboards**: Sortable, searchable, paginated player and team rankings
- **Player Profiles**: Detailed cards with badges, radar charts, evolution data, and game logs
- **Cluster Analysis**: Explore player archetypes and cluster transitions
- **PORTALMANIA Game**: Interactive game connecting players through teammate relationships
- **Modern UI**: Clean, responsive design with Tailwind CSS
- **Type Safety**: Full TypeScript implementation
- **Clean Architecture**: Modular components and service-oriented backend

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+

### Development Setup

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd jeevs-cbb
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cp .env.example .env.local
   ```

4. **Start Development Servers**
   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

Access the application at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📊 API Documentation

For complete API documentation, see [docs/API_DOCUMENTATION.md](./docs/API_DOCUMENTATION.md)

### Main Endpoints

**Players:**
- `GET /api/v1/players` - List players with filtering and pagination
- `GET /api/v1/players/{ncaa_id}` - Get specific player details
- `GET /api/v1/players/{ncaa_id}/games` - Get player game log
- `GET /api/v1/players/{ncaa_id}/badges` - Player achievement badges
- `GET /api/v1/players/{ncaa_id}/radar` - Player radar chart data
- `GET /api/v1/players/{ncaa_id}/evolution` - Player career evolution
- `GET /api/v1/players/{ncaa_id}/history` - Player history
- `GET /api/v1/players/{ncaa_id}/similar` - Similar players
- `GET /api/v1/players/{ncaa_id}/moves` - Transfer/moves data

**Teams:**
- `GET /api/v1/teams` - List teams
- `GET /api/v1/teams/{team_id}` - Get specific team details

**Analytics:**
- `GET /api/v1/clusters` - Get cluster analysis
- `GET /api/v1/clusters/{cluster_id}/bpm-distribution` - Get cluster BPM distribution
- `GET /api/v1/similarity/nearest/{ncaa_id}` - Get nearest neighbors
- `GET /api/v1/projections/2027` - Get 2027 BPM projections
- `GET /api/v1/years` - Available years

**Game (PORTALMANIA):**
- `GET /api/v1/game/random-pair` - Get random player pair
- `GET /api/v1/game/player/{player_id}` - Get game player info
- `POST /api/v1/game/check-teammates` - Check if players were teammates
- `POST /api/v1/game/shortest-path` - Get shortest path between players

**System:**
- `GET /health` - Health check

### Interactive API Docs

When running in development mode:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Development Tools

### Code Quality

```bash
# Frontend
npm run lint          # Check code style
npm run format        # Fix formatting
npm run type-check    # TypeScript validation

# Backend
pytest tests/ -v       # Run tests
```

### Testing (Optional)

```bash
# Frontend
npm run test              # Run tests
npm run test:watch        # Watch mode

# Backend
pytest tests/ -v --cov=app
```

## 🏗️ Project Architecture

### Frontend Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── context/            # React context providers
│   ├── player/             # Player pages
│   ├── globals.css         # Global styles
│   ├── layout.tsx          # Root layout
│   └── page.tsx            # Home page
├── components/             # Reusable components
│   ├── player/            # Player-specific components
│   └── ui/               # UI components
├── hooks/                 # Custom React hooks
├── lib/                   # Utilities and API client
├── types/                 # TypeScript type definitions
└── __tests__/             # Test files
```

### Backend Structure

```
backend/
├── app/
│   ├── api/               # API route handlers
│   ├── services/          # Business logic layer
│   ├── core/              # Core functionality (data loading, resolvers)
│   ├── features/          # Feature calculations (badges, moves, vectors)
│   ├── models/            # Data models and schemas
│   ├── cache/             # Caching layer
│   ├── middleware/       # Custom middleware
│   ├── utils/             # Utility functions
│   └── main.py            # Application entry point
├── data/                 # Data files (CSV, JSON)
│   ├── players/           # Player statistics
│   ├── teams/             # Team statistics
│   ├── games/             # Game-by-game data
│   └── aggregate/         # Aggregated historical data
├── scripts/              # Data processing scripts
│   ├── data_processing/   # Data ingestion and enrichment
│   ├── analysis/          # Analysis scripts
│   ├── modeling/          # ML model training
│   └── utilities/         # Utility scripts
├── tests/                # Test files
└── requirements.txt       # Python dependencies
```

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (default: false)
- `CORS_ORIGINS`: Allowed CORS origins
- `LOG_LEVEL`: Logging level (default: INFO)

**Frontend (.env.local):**
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_ENABLE_ANALYTICS`: Feature flag for analytics

---

## 📖 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[API Documentation](./docs/API_DOCUMENTATION.md)** - Complete API reference with all endpoints, parameters, and response formats
- **[Data Sources](./docs/DATA_SOURCES.md)** - Information about data providers, data processing, and data quality
- **[System Architecture](./docs/SYSTEM_ARCHITECTURE.md)** - Technical architecture, technology stack, and system design
- **[Analytics and Models](./docs/ANALYTICS_AND_MODELS.md)** - In-depth explanations of analytics, metrics, and machine learning models
- **[Technology Stack](./docs/TECH_STACK.md)** - Complete list of technologies, packages, and tools used

### In-App Documentation

Documentation is also available in the application at `/docs` with pages for:
- API Documentation
- Data Sources
- System Architecture
- Analytics and Models

## 📖 Additional Guides

- **[DEVELOPMENT.md](./DEVELOPMENT.md)** - Detailed setup and debugging tips
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Deployment guide for production
- **[DESIGN.md](./DESIGN.md)** - Design principles and decisions
- **[PRODUCT.md](./PRODUCT.md)** - Product vision and features

## 📊 Data Coverage

- **Years:** 2019-2026 (8 seasons)
- **Players:** ~15,000+ unique players
- **Teams:** 350+ D1 teams
- **Games:** ~50,000+ game records

## 🔬 Analytics & Models

### Key Metrics
- **Box Plus Minus (BPM):** Estimates player contribution per 100 possessions
- **Usage Rate:** Percentage of team possessions used by a player
- **eFG%:** Effective field goal percentage
- **Player Clusters:** 18 ML-derived player archetypes

### Machine Learning Models
- **Player Clustering:** K-means clustering (18 clusters)
- **BPM Projections:** Random Forest regression (R² = 0.45, RMSE = 1.8 BPM)
- **Similarity Scoring:** Cosine similarity on normalized feature vectors
- **NIL Valuation:** Multiple linear regression for market value estimation

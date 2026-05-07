# JEEVS-CBB: College Basketball Analytics Platform

A comprehensive college basketball analytics platform built with FastAPI backend and Next.js frontend, featuring advanced player statistics, similarity analysis, and performance metrics.

## 🏀 Overview

This platform provides:
- **Player Analytics**: Advanced statistics and performance metrics
- **Similarity Analysis**: Find players with similar playing styles
- **Career Tracking**: Multi-year player development analysis
- **Statistical Leaders**: Rankings across various metrics
- **Search & Discovery**: Powerful player search capabilities

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CSV Files    │───▶│   Data Layer    │───▶│  Repository     │───▶│      API        │
│                 │    │                 │    │                 │    │                 │
│ • 2024-2026   │    │ • Loader        │    │ • Player Repo   │    │ • Players       │
│ • Enriched data │    │ • Cleaner       │    │ • Search Repo   │    │ • Search        │
│                 │    │ • Merger        │    │ • Stats Repo    │    │ • Stats         │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                                                │
                                                                ▼
                                                       ┌─────────────────┐
                                                       │   Frontend     │
                                                       │                 │
                                                       │ • Next.js      │
                                                       │ • TypeScript    │
                                                       │ • Tailwind CSS  │
                                                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- pip (Python package manager)
- npm (Node.js package manager)

### Backend Setup

1. **Clone and navigate to backend**
```bash
cd backend
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Start the FastAPI server**
```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Clone and navigate to frontend**
```bash
cd frontend
```

2. **Install Node.js dependencies**
```bash
npm install
```

3. **Start the development server**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📊 Data Structure

### Primary Keys
- **`player_id`**: Unique identifier (derived from `roster.ncaa_id`)
- **`year`**: Season year (2024, 2025, 2026, or "career")

### Data Flow
1. **Raw CSV Files**: Annual player data with advanced metrics
2. **Data Layer**: Cleaning, validation, and standardization
3. **Repository Layer**: Abstracted data access with caching
4. **API Layer**: RESTful endpoints with proper separation of concerns
5. **Frontend**: Type-safe client with React components

## 🔧 Development

### Backend Development

#### Key Components
- **`app/data/`**: Data processing layer
  - `loader.py`: Raw data loading
  - `cleaner.py`: Data validation and normalization
  - `merger.py`: Dataset joining and player records
  - `schema.py`: Data contract definitions

- **`app/repositories/`**: Repository pattern implementation
  - `player.py`: Player data access with caching
  - `base.py`: Abstract base repository class

- **`app/core/utils/`**: Shared utilities
  - `ids.py`: Player ID handling and conversion
  - `years.py`: Year normalization and validation
  - `filters.py`: Data filtering and pandas operations

- **`app/api/`**: RESTful API endpoints
  - `players.py`: Player listing and individual data
  - `search.py`: Dedicated search functionality
  - `stats.py`: Statistical endpoints
  - `performance.py`: System monitoring

#### Adding New Features

1. **Data Layer**: Add to appropriate module in `app/data/`
2. **Repository**: Implement in `app/repositories/` following the pattern
3. **API**: Create new router in `app/api/`
4. **Frontend**: Add TypeScript types in `lib/api.ts`

### Frontend Development

#### Key Components
- **`lib/api.ts`**: Type-safe API client
- **`components/player/`**: Player-specific UI components
- **`app/`**: Next.js pages and layouts

#### Adding New Features

1. **API Client**: Add functions to `lib/api.ts` with proper types
2. **Components**: Create reusable components in `components/`
3. **Pages**: Add new pages in `app/`

## 📡 API Documentation

### Core Endpoints

#### Players
- `GET /players` - List players with filtering and pagination
- `GET /players/{id}` - Get individual player data
- `GET /players/{id}/badges` - Player achievement badges
- `GET /players/{id}/radar` - Player performance radar
- `GET /players/{id}/similar` - Similar players analysis
- `GET /players/{id}/moves` - Player movement history
- `GET /players/{id}/evolution` - Player development analysis

#### Search
- `GET /search` - Advanced player search
- `GET /search/suggestions` - Autocomplete suggestions

#### Statistics
- `GET /stats/summary` - Dataset overview
- `GET /stats/leaders` - Statistical leaders by metric
- `GET /stats/distributions` - Data distributions for visualization
- `GET /stats/conferences` - Conference-level statistics

#### System
- `GET /years` - Available years
- `GET /performance/stats` - System performance metrics
- `POST /performance/cache/clear` - Clear system cache
- `GET /performance/health` - Health check

### API Usage Examples

```bash
# List players (paginated)
curl "http://localhost:8000/players?limit=10&offset=0&year=2024"

# Search players
curl "http://localhost:8000/search?q=john&limit=5"

# Get specific player
curl "http://localhost:8000/players/123456?year=2024"

# Get statistical leaders
curl "http://localhost:8000/stats/leaders?stat=adj_rapm_margin&year=2024&limit=10"
```

## 🔍 Testing

### Backend Testing
```bash
# Run all tests (if implemented)
python -m pytest

# Run specific test file
python -m pytest tests/test_players.py
```

### Frontend Testing
```bash
# Run test suite
npm test

# Run tests in watch mode
npm run test:watch
```

## 🚀 Performance

### Caching
- **Repository Layer**: 10-minute TTL for player data
- **Search Results**: 30-minute TTL for search queries
- **Statistical Data**: 5-minute TTL for aggregated stats

### Optimization Features
- **Memory Optimization**: Automatic data type optimization
- **Indexing**: Pre-built indexes for common queries
- **Lazy Loading**: On-demand data loading for large datasets

### Monitoring
- **Cache Hit Rates**: Track performance improvements
- **Memory Usage**: Monitor system resources
- **Response Times**: API performance metrics

## 🔧 Configuration

### Environment Variables
```bash
# Backend (optional)
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export LOG_LEVEL=INFO

# Frontend (optional)
export NEXT_PUBLIC_API_URL=http://localhost:8000
export NODE_ENV=development
```

### Data Configuration
- **Data Location**: `backend/data/`
- **Supported Years**: 2024, 2025, 2026
- **Required Columns**: Enforced by data contract validation

## 🐛 Troubleshooting

### Common Issues

#### Backend
- **Import Errors**: Ensure all dependencies installed via `pip install -r requirements.txt`
- **Data Loading**: Verify CSV files exist in `backend/data/`
- **Port Conflicts**: Change port in `app/main.py` if 8000 is in use

#### Frontend
- **Build Errors**: Run `npm install` after pulling changes
- **API Connection**: Ensure backend is running on `http://localhost:8000`
- **Type Errors**: Check TypeScript types in `lib/api.ts`

### Debug Mode
```bash
# Backend with debug logging
export LOG_LEVEL=DEBUG
python -m app.main

# Frontend with detailed errors
npm run dev
```

## 📈 Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:8000/performance/health

# System performance
curl http://localhost:8000/performance/stats
```

### Logs
- **Backend**: Console output with structured logging
- **Frontend**: Browser console and terminal output

## 🔮 Future Enhancements

### Planned Features
- **Database Migration**: Repository layer enables easy switch to PostgreSQL/MySQL
- **Real-time Updates**: WebSocket integration for live data
- **Advanced Analytics**: Machine learning models for player predictions
- **Mobile App**: React Native companion application
- **API Versioning**: Versioned API endpoints for backward compatibility

### Scalability
- **Horizontal Scaling**: Repository pattern supports multiple data sources
- **Caching Layer**: Redis integration for distributed caching
- **Load Balancing**: API designed for horizontal scaling
- **Database Sharding**: Support for multi-tenant architecture

## 📝 Contributing

### Code Style
- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Strict mode, proper interface definitions
- **React**: Functional components with hooks
- **CSS**: Tailwind utility classes

### Git Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m "Add feature description"`
4. Push branch: `git push origin feature-name`
5. Create pull request

### Development Guidelines
- **Small Commits**: Atomic changes with clear messages
- **Test Coverage**: Add tests for new features
- **Documentation**: Update README and API docs
- **Performance**: Consider caching and optimization impact

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For questions, issues, or contributions:
- **Issues**: Create GitHub issue with detailed description
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers for security issues

---

**Built with ❤️ for college basketball analytics**
# Jeevs CBB - College Basketball Analytics

A clean, modern full-stack application for college basketball player analytics, built with React/Next.js frontend and FastAPI backend.

## 🏀 Features

- **Player Analytics**: Advanced statistics including RAPM, offensive/defensive ratings
- **Interactive Tables**: Sortable, searchable, paginated player leaderboards
- **Player Profiles**: Detailed player cards with badges, radar charts, and evolution data
- **Modern UI**: Clean, responsive design with Tailwind CSS
- **Type Safety**: Full TypeScript implementation across frontend and backend
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

### Main Endpoints

- `GET /api/v1/players` - List players with filtering and pagination
- `GET /api/v1/players/{ncaa_id}` - Get specific player details
- `GET /api/v1/players/{ncaa_id}/badges` - Player achievement badges
- `GET /api/v1/players/{ncaa_id}/radar` - Player radar chart data
- `GET /api/v1/players/{ncaa_id}/evolution` - Player career evolution
- `GET /api/v1/years` - Available years
- `GET /health` - Health check

### Query Parameters

**Players List:**
- `limit` (int): Number of results (default: 50, max: 100)
- `offset` (int): Pagination offset (default: 0)
- `sort` (string): Sort column (default: adj_rapm_margin)
- `order` (string): Sort order "asc" or "desc" (default: desc)
- `year` (int|string): Filter by year or "career"
- `search` (string): Search players/teams
- `conf` (string): Filter by conference

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
│   ├── core/              # Core business logic
│   ├── features/          # Feature-specific logic
│   ├── models/            # Data models and schemas
│   ├── services/          # Service layer
│   └── utils/             # Utility functions
├── data/                 # Data files
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

## 🎯 Key Improvements Made

### ✅ Frontend Refactoring
- **Broke down monolithic components**: 354-line page split into focused pieces
- **Added custom hooks**: Extracted data fetching logic into reusable hooks
- **Improved error handling**: Added error boundaries and proper error states
- **Type safety**: Comprehensive TypeScript with strict mode
- **Performance**: Debounced search, memoization, proper state management

### ✅ Backend Refactoring
- **Service layer**: Separated business logic from API routes
- **Input validation**: Added Pydantic schemas for all endpoints
- **Error handling**: Structured error responses and logging
- **Configuration**: Environment-based settings
- **Clean architecture**: Organized into logical modules

### ✅ Code Quality
- **Linting**: ESLint and Prettier configuration
- **TypeScript**: Strict mode, no `any` types
- **Testing**: Jest and pytest setup with examples
- **Documentation**: Comprehensive README and API docs

## 📝 Development Workflow

1. **Make changes** to components or services
2. **Run linting**: `npm run lint` + type checking
3. **Test manually**: Open app and verify functionality
4. **Format code**: `npm run format` before commits
5. **Focus on**: Clean code, good structure, maintainability

---

## 📖 Detailed Development Guide

See [DEVELOPMENT.md](./DEVELOPMENT.md) for detailed setup and debugging tips.

Built with ❤️ for college basketball analytics
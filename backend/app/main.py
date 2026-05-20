from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.utils.logger import setup_logging
from app.middleware.error_handler import ErrorHandlerMiddleware, LoggingMiddleware

# API routers
from app.api.players import router as players_router
from app.api.moves import router as moves_router
from app.api.badges import router as badges_router
from app.api.radar import router as radar_router
from app.api.similarity import router as sim_router
from app.api.years import router as years_router
from app.api.evolution import router as evolution_router
from app.api.history import router as history_router

# Cache
from app.cache.player_vectors import build_cache

# Setup logging
setup_logging()

# -------------------------
# LIFESPAN HANDLER
# -------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🚀 startup
    build_cache()
    print("✅ Player vector cache built")
    print(f"🚀 Server starting on {settings.host}:{settings.port}")

    yield

    # 🧹 shutdown
    print("👋 Shutting down backend")

# -------------------------
# APP INITIALIZATION
# -------------------------
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# -------------------------
# MIDDLEWARE
# -------------------------
# Error handling middleware (should be first)
app.add_middleware(ErrorHandlerMiddleware)

# Logging middleware
app.add_middleware(LoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# -------------------------
# ROUTES
# -------------------------
app.include_router(players_router, prefix="/api/v1", tags=["players"])
app.include_router(moves_router, prefix="/api/v1", tags=["moves"])
app.include_router(badges_router, prefix="/api/v1", tags=["badges"])
app.include_router(radar_router, prefix="/api/v1", tags=["radar"])
app.include_router(sim_router, prefix="/api/v1", tags=["similarity"])
app.include_router(years_router, prefix="/api/v1", tags=["years"])
app.include_router(evolution_router, prefix="/api/v1", tags=["evolution"])
app.include_router(history_router, prefix="/api/v1", tags=["history"])

# -------------------------
# HEALTH CHECK
# -------------------------
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from datetime import datetime
    
    return {
        "status": "healthy",
        "version": settings.api_version,
        "timestamp": datetime.utcnow().isoformat()
    }
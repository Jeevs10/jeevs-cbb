from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.utils.logger import setup_logging
from app.middleware.error_handler import ErrorHandlerMiddleware, LoggingMiddleware

# API routers
from app.api.players import router as players_router
from app.api.teams import router as teams_router
from app.api.moves import router as moves_router
from app.api.badges import router as badges_router
from app.api.radar import router as radar_router
from app.api.similarity import router as sim_router
from app.api.years import router as years_router
from app.api.evolution import router as evolution_router
from app.api.history import router as history_router
from app.api.game import router as game_router
from app.api.utilization import router as utilization_router
from app.api.nil import router as nil_router
from app.api.projections import router as projections_router
from app.api.clusters import router as clusters_router

# Cache
from app.cache.player_vectors import build_cache

# Setup logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    build_cache()
    yield

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)
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
@app.get("/health")
@limiter.limit("100/minute")
async def health_check(request: Request):
    from datetime import datetime
    return {
        "status": "healthy",
        "version": settings.api_version,
        "timestamp": datetime.utcnow().isoformat()
    }
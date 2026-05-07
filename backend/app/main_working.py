"""
Working version of main.py with minimal dependencies and proper imports.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import only what we need for basic functionality
from app.api.players import router as players_router
from app.api.search import router as search_router
from app.api.stats import router as stats_router

# Minimal years endpoint
from app.data.loader import get_available_years

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for startup/shutdown."""
    print("🚀 Starting JEEVS-CBB API...")
    yield
    print("👋 Shutting down JEEVS-CBB API")

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(players_router)
app.include_router(search_router)
app.include_router(stats_router)

# Basic years endpoint
@app.get("/years")
def get_years():
    """Get available years."""
    try:
        years = get_available_years()
        return {"years": years}
    except Exception as e:
        return {"error": f"Failed to load years: {str(e)}", "years": []}

# Health check
@app.get("/health")
def health_check():
    """Basic health check."""
    return {"status": "healthy", "message": "JEEVS-CBB API is running"}

if __name__ == "__main__":
    import uvicorn
    print("🌐 Starting server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)

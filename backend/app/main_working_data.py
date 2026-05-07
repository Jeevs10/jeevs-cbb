"""
Working main.py that uses actual data layer instead of hardcoded data.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import working API routers
from app.api.players import router as players_router
from app.api.search import router as search_router
from app.api.stats import router as stats_router

# Import data layer functions
from app.data.loader import get_available_years
from app.data.merger import get_conferences

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for startup/shutdown."""
    print("🚀 Starting JEEVS-CBB API with data layer...")
    try:
        # Test data layer on startup
        years = get_available_years()
        print(f"📊 Available years: {years}")
        
        conferences = get_conferences(None)  # Will work with actual data
        print(f"🏀 Conferences found: {len(conferences)}")
        
        yield
        print("👋 Shutting down JEEVS-CBB API")
    except Exception as e:
        print(f"❌ Data layer error: {e}")
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

# Working years endpoint
@app.get("/years")
def get_years():
    """Get available years from actual data."""
    try:
        years = get_available_years()
        return {"years": years}
    except Exception as e:
        return {"error": f"Failed to load years: {str(e)}", "years": []}

# Working conferences endpoint
@app.get("/conferences")
def get_conferences():
    """Get conferences from actual data."""
    try:
        conferences = get_conferences(None)
        return {"conferences": conferences}
    except Exception as e:
        return {"error": f"Failed to load conferences: {str(e)}", "conferences": []}

# Health check
@app.get("/health")
def health_check():
    """Basic health check."""
    return {"status": "healthy", "message": "JEEVS-CBB API is running"}

if __name__ == "__main__":
    import uvicorn
    print("🌐 Starting server on http://localhost:8000")
    print("📊 Using real data layer")
    uvicorn.run(app, host="0.0.0.0", port=8000)

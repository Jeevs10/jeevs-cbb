from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.players import router as players_router
from app.api.moves import router as moves_router
from app.api.badges import router as badges_router
from app.api.radar import router as radar_router
from app.api.similarity import router as sim_router
from app.api.years import router as years_router
from app.cache.player_vectors import build_cache


# -------------------------
# LIFESPAN HANDLER
# -------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🚀 startup
    build_cache()
    print("✅ Player vector cache built")

    yield

    # 🧹 shutdown (optional cleanup later)
    print("👋 Shutting down backend")


app = FastAPI(lifespan=lifespan)


# -------------------------
# MIDDLEWARE
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# ROUTES
# -------------------------
app.include_router(players_router)
app.include_router(moves_router)
app.include_router(badges_router)
app.include_router(radar_router)
app.include_router(sim_router)
app.include_router(years_router)
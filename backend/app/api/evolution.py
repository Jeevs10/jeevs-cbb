from typing import Union, Optional
from fastapi import APIRouter, Query
from app.services.evolution_service import get_player_evolution
from functools import lru_cache
import hashlib
import time

router = APIRouter()

# Simple in-memory cache with TTL
_evolution_cache = {}
_evolution_cache_ttl = 300  # 5 minutes

def get_cache_key(ncaa_id, year, metric):
    key_str = f"{ncaa_id}_{year}_{metric}"
    return hashlib.md5(key_str.encode()).hexdigest()

@router.get("/players/{ncaa_id}/evolution")
def player_evolution(
    ncaa_id: str, 
    year: Union[int, str, None] = None,
    metric: Optional[str] = Query("rapm", description="Metric to use for tiering: rapm, bpm, vorp, or combined")
):
    # Check cache
    cache_key = get_cache_key(ncaa_id, year, metric)
    cached_data, cached_time = _evolution_cache.get(cache_key, (None, 0))
    
    if cached_data and (time.time() - cached_time) < _evolution_cache_ttl:
        return cached_data
    
    result = get_player_evolution(float(ncaa_id), year, metric=metric)

    # -------------------------
    # SAFETY NORMALIZATION
    # -------------------------
    if not result:
        return {
            "player_tier": None,
            "metric": "rapm",
            "bench_unit": [],
            "rotation_piece": [],
            "starter": [],
            "all_conference": [],
            "all_american": []
        }

    # ensure all keys exist even if service omits something
    normalized = {
        "player_tier": result.get("player_tier"),
        "metric": result.get("metric", "rapm"),
        "bench_unit": result.get("bench_unit", []),
        "rotation_piece": result.get("rotation_piece", []),
        "starter": result.get("starter", []),
        "all_conference": result.get("all_conference", []),
        "all_american": result.get("all_american", []),
    }

    # Store in cache
    _evolution_cache[cache_key] = (normalized, time.time())

    return normalized
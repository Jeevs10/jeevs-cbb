from typing import Union
from fastapi import APIRouter
from app.services.similarity_service import get_similar_players
from app.core.data_loader import PLAYER_LOOKUP
from app.core.year_utils import normalize_year
import hashlib
import time

router = APIRouter()

# Simple in-memory cache with TTL
_similarity_cache = {}
_similarity_cache_ttl = 300  # 5 minutes

def get_cache_key(ncaa_id, year, top_k, style_weight):
    key_str = f"{ncaa_id}_{year}_{top_k}_{style_weight}"
    return hashlib.md5(key_str.encode()).hexdigest()


def enrich(results):
    def format_list(lst):
        out = []

        for item in lst:
            # Normalize the ID to match player_key format (remove .0 suffix)
            code = str(item["AthleteSourceId"]).replace('.0', '')
            meta = PLAYER_LOOKUP.get(code, {})

            out.append({
                "AthleteSourceId": code,
                "player_name": meta.get("player_name"),
                "team": meta.get("team"),
                "pos": meta.get("Position", meta.get("posClass")),

                # IMPORTANT: snapshot year used in comparison
                "year": item.get("year"),

                "similarity": item.get("similarity", 0),
                "reasons": item.get("reasons", []),
            })

        return out

    return {
        "style": format_list(results["style"]),
        "impact": format_list(results["impact"]),
        "combined": format_list(results["combined"]),
    }


@router.get("/players/{ncaa_id}/similar")
def similar_players(
    ncaa_id: str,
    year: Union[int, str, None] = None,
    top_k: int = 10,
    style_weight: float = 0.7
):
    # Check cache
    cache_key = get_cache_key(ncaa_id, year, top_k, style_weight)
    cached_data, cached_time = _similarity_cache.get(cache_key, (None, 0))
    
    if cached_data and (time.time() - cached_time) < _similarity_cache_ttl:
        return cached_data

    year = normalize_year(year)

    results = get_similar_players(
        float(ncaa_id),
        year=year,
        top_k=top_k,
        style_weight=style_weight
    )

    enriched = enrich(results)
    
    # Store in cache
    _similarity_cache[cache_key] = (enriched, time.time())

    return enriched
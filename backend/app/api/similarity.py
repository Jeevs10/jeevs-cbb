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


@router.get("/similarity/vectors")
def get_all_vectors():
    """Get all player vectors for similarity mapping"""
    from app.cache.player_vectors import PLAYER_VECTORS
    import numpy as np
    
    vectors = []
    for ncaa_id, year_map in PLAYER_VECTORS.items():
        # Get latest year vector
        latest_year = max(year_map.keys(), key=lambda x: int(x))
        vec = year_map[latest_year]
        
        vectors.append({
            "ncaa_id": ncaa_id,
            "year": latest_year,
            "style": np.array(vec["style"]).tolist(),
            "impact": np.array(vec["impact"]).tolist(),
        })
    
    return {"vectors": vectors}


@router.get("/similarity/positions")
def get_precomputed_positions():
    """Get precomputed 3D positions for similarity map"""
    import pandas as pd
    import os
    
    # Go up from app/api/similarity.py to backend directory
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "similarity_positions.csv")
    
    print(f"[DEBUG] Looking for positions file at: {csv_path}")
    print(f"[DEBUG] File exists: {os.path.exists(csv_path)}")
    
    if not os.path.exists(csv_path):
        return {"positions": [], "error": "Positions file not found. Run precompute_similarity_positions.py"}
    
    df = pd.read_csv(csv_path)
    print(f"[DEBUG] Loaded {len(df)} positions from CSV")
    
    # Fill numeric columns with 0, string columns with empty string
    numeric_cols = ['ncaa_id', 'year', 'x', 'y', 'z']
    string_cols = ['player_name', 'team']
    df[numeric_cols] = df[numeric_cols].fillna(0)
    df[string_cols] = df[string_cols].fillna('')
    
    positions = []
    for _, row in df.iterrows():
        positions.append({
            "ncaa_id": str(int(row["ncaa_id"])),
            "year": str(int(row["year"])),
            "x": float(row["x"]),
            "y": float(row["y"]),
            "z": float(row["z"]),
            "player_name": row.get("player_name") if row.get("player_name") != 0 else None,
            "team": row.get("team") if row.get("team") != 0 else None,
        })
    
    print(f"[DEBUG] Returning {len(positions)} positions")
    return {"positions": positions}


@router.get("/similarity/nearest/{ncaa_id}")
def get_nearest_neighbors(ncaa_id: str, limit: int = 20):
    """Get nearest neighbors based on feature vector cosine similarity"""
    from app.cache.player_vectors import PLAYER_VECTORS
    from app.core.data_loader import PLAYER_LOOKUP
    import numpy as np
    
    # Convert ncaa_id to float for matching with PLAYER_VECTORS keys
    ncaa_id_float = float(ncaa_id)
    
    # Find the target player's vectors (could have multiple years)
    if ncaa_id_float not in PLAYER_VECTORS:
        return {"neighbors": [], "error": "Player not found in vectors"}
    
    target_year_map = PLAYER_VECTORS[ncaa_id_float]
    
    # Use the most recent year's vector as the target
    if not target_year_map:
        return {"neighbors": [], "error": "No vectors found for player"}
    
    # Get the most recent year
    target_year = max(target_year_map.keys())
    target_vector_dict = target_year_map[target_year]
    
    # Concatenate style and impact vectors into a single feature vector
    target_vector = np.concatenate([
        target_vector_dict["style"],
        target_vector_dict["impact"]
    ])
    
    # Calculate cosine similarity with all other player-year vectors
    neighbors = []
    for other_ncaa_id, year_map in PLAYER_VECTORS.items():
        if other_ncaa_id == ncaa_id_float:
            continue
        
        for yr, vec_dict in year_map.items():
            # Concatenate style and impact vectors
            vec = np.concatenate([
                vec_dict["style"],
                vec_dict["impact"]
            ])
            
            # Calculate cosine similarity
            similarity = np.dot(target_vector, vec) / (np.linalg.norm(target_vector) * np.linalg.norm(vec))
            
            # Get player name and team
            ncaa_id_str = str(other_ncaa_id).replace('.0', '')
            torvik_key = f"{ncaa_id_str}_{yr}"
            
            # Try PLAYER_LOOKUP first
            meta = PLAYER_LOOKUP.get(ncaa_id_str, {})
            player_name = meta.get('player_name')
            team = meta.get('team')
            
            neighbors.append({
                "ncaa_id": ncaa_id_str,
                "year": yr,
                "distance": 1 - similarity,  # Convert similarity to distance
                "similarity": similarity,
                "player_name": player_name,
                "team": team
            })
    
    # Sort by similarity (highest first) and return top N
    neighbors.sort(key=lambda x: x["similarity"], reverse=True)
    neighbors = neighbors[:limit]
    
    return {"neighbors": neighbors}
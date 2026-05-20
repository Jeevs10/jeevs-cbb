import numpy as np
import logging

from app.cache.player_vectors import PLAYER_VECTORS, PLAYER_INFO
from app.models.similarity import cosine_similarity
from app.services.similarity_service import get_vector

logger = logging.getLogger("evolution")

DEBUG = True

def log(level, msg):
    if DEBUG:
        getattr(logger, level)(msg)


# -------------------------
# META
# -------------------------
def get_player_name(ncaa_id):
    info = PLAYER_INFO.get(ncaa_id, {})
    name = info.get("player_name")
    return name if name and str(name).strip() else ncaa_id


def get_player_meta(ncaa_id):
    info = PLAYER_INFO.get(ncaa_id, {})
    return info.get("team"), (info.get("pos") or info.get("position"))


# -------------------------
# POOL
# -------------------------
def build_pool(year=None):
    pool = []

    for ncaa_id, year_map in PLAYER_VECTORS.items():
        vec, used_year = get_vector(year_map, year)
        if not vec:
            continue

        pool.append({
            "ncaa_id": ncaa_id,
            "player_name": get_player_name(ncaa_id),
            "team": get_player_meta(ncaa_id)[0],
            "pos": get_player_meta(ncaa_id)[1],
            "year": used_year,
            "style": vec["style"],

            # CLEAN SIGNALS
            "rapm": vec.get("rapm", 0.0),
            "rapm_pct": vec.get("rapm_pct", 0.0),
        })

    return pool


# -------------------------
# 5-TIER SYSTEM
# -------------------------
def assign_tier(p):
    if p < 0.15:
        return "bench_unit"
    elif p < 0.40:
        return "rotation_piece"
    elif p < 0.70:
        return "starter"
    elif p < 0.95:
        return "all_conference"
    else:
        return "all_american"


# -------------------------
# EVOLUTION ENGINE
# -------------------------
def get_player_evolution(ncaa_id, year=None, top_k=3):

    if ncaa_id not in PLAYER_VECTORS:
        return empty()

    target_vec, _ = get_vector(PLAYER_VECTORS[ncaa_id], year)
    if not target_vec:
        return empty()

    target_style = target_vec["style"]
    target_pct = target_vec.get("rapm_pct", 0.0)

    pool = [
        p for p in build_pool(None)
        if p["ncaa_id"] != ncaa_id
    ]

    # -------------------------
    # TIERING (GLOBAL PERCENTILE — NO NOISE)
    # -------------------------
    for p in pool:
        p["tier"] = assign_tier(p["rapm_pct"])

    # -------------------------
    # SIMILARITY WITH TIER BALANCING
    # -------------------------
    for p in pool:
        p["sim"] = cosine_similarity(target_style, p["style"])

    # Ensure we have players from all tiers by sampling from each tier
    tier_samples = {
        "bench_unit": [],
        "rotation_piece": [],
        "starter": [],
        "all_conference": [],
        "all_american": []
    }
    
    # Sample up to 20 players from each tier, sorted by similarity
    for tier in tier_samples:
        tier_players = [p for p in pool if p["tier"] == tier]
        tier_players.sort(key=lambda x: -x["sim"])
        tier_samples[tier] = tier_players[:20]
    
    # Combine samples from all tiers
    balanced_pool = []
    for tier_players in tier_samples.values():
        balanced_pool.extend(tier_players)
    
    # Use the balanced pool instead of the top 100 most similar
    pool = balanced_pool

    player_tier = assign_tier(target_pct)

    # -------------------------
    # BUCKETS
    # -------------------------
    buckets = {
        "bench_unit": [],
        "rotation_piece": [],
        "starter": [],
        "all_conference": [],
        "all_american": []
    }

    for p in pool:
        buckets[p["tier"]].append({
            "AthleteSourceId": p["ncaa_id"],
            "player_name": p["player_name"],
            "team": p["team"],
            "pos": p["pos"],
            "year": p["year"],
            "similarity": float(p["sim"]),
            "rapm_pct": float(p["rapm_pct"]),
        })

    for k in buckets:
        buckets[k] = sorted(buckets[k], key=lambda x: -x["similarity"])[:top_k]

    return {
        "player_tier": player_tier,
        **buckets
    }


def empty():
    return {
        "player_tier": None,
        "bench_unit": [],
        "rotation_piece": [],
        "starter": [],
        "all_conference": [],
        "all_american": []
    }
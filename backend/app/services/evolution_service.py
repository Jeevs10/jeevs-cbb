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
def get_player_name(code):
    info = PLAYER_INFO.get(code, {})
    name = info.get("player_name")
    return name if name and str(name).strip() else code


def get_player_meta(code):
    info = PLAYER_INFO.get(code, {})
    return info.get("team"), (info.get("pos") or info.get("position"))


# -------------------------
# POOL
# -------------------------
def build_pool(year=None):
    pool = []

    for code, year_map in PLAYER_VECTORS.items():
        vec, used_year = get_vector(year_map, year)
        if not vec:
            continue

        pool.append({
            "player_code": code,
            "player_name": get_player_name(code),
            "team": get_player_meta(code)[0],
            "pos": get_player_meta(code)[1],
            "year": used_year,
            "style": vec["style"],

            # 🔥 CLEAN SIGNALS
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
def get_player_evolution(player_code, year=None, top_k=3):

    if player_code not in PLAYER_VECTORS:
        return empty()

    target_vec, _ = get_vector(PLAYER_VECTORS[player_code], year)
    if not target_vec:
        return empty()

    target_style = target_vec["style"]
    target_pct = target_vec.get("rapm_pct", 0.0)

    pool = [
        p for p in build_pool(None)
        if p["player_code"] != player_code
    ]

    # -------------------------
    # SIMILARITY
    # -------------------------
    for p in pool:
        p["sim"] = cosine_similarity(target_style, p["style"])

    pool = sorted(pool, key=lambda x: -x["sim"])[:100]

    # -------------------------
    # TIERING (GLOBAL PERCENTILE — NO NOISE)
    # -------------------------
    for p in pool:
        p["tier"] = assign_tier(p["rapm_pct"])

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
            "player_code": p["player_code"],
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
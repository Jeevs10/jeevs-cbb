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


def get_player_name(ncaa_id):
    info = PLAYER_INFO.get(ncaa_id, {})
    name = info.get("player_name")
    return name if name and str(name).strip() else ncaa_id


def get_player_meta(ncaa_id):
    info = PLAYER_INFO.get(ncaa_id, {})
    return info.get("team"), (info.get("pos") or info.get("position"))


def build_pool(year=None, metric="rapm"):
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

            "rapm": vec.get("rapm", 0.0),
            "rapm_pct": vec.get("rapm_pct", 0.0),
            "bpm": vec.get("bpm", 0.0),
            "bpm_pct": vec.get("bpm_pct", 0.0),
            "vorp": vec.get("vorp", 0.0),
            "vorp_pct": vec.get("vorp_pct", 0.0),
        })

    return pool


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


def get_player_evolution(ncaa_id, year=None, top_k=3, metric="rapm"):

    if ncaa_id not in PLAYER_VECTORS:
        return empty()

    target_vec, _ = get_vector(PLAYER_VECTORS[ncaa_id], year)
    if not target_vec:
        return empty()

    target_style = target_vec["style"]

    if metric == "bpm":
        target_pct = target_vec.get("bpm_pct", 0.0)
    elif metric == "vorp":
        target_pct = target_vec.get("vorp_pct", 0.0)
    elif metric == "combined":
        rapm_pct = target_vec.get("rapm_pct", 0.0)
        bpm_pct = target_vec.get("bpm_pct", 0.0)
        vorp_pct = target_vec.get("vorp_pct", 0.0)
        target_pct = (rapm_pct + bpm_pct + vorp_pct) / 3
    else:
        target_pct = target_vec.get("rapm_pct", 0.0)

    pool = [
        p for p in build_pool(None, metric)
        if p["ncaa_id"] != ncaa_id
    ]

    for p in pool:
        if metric == "bpm":
            p["tier"] = assign_tier(p["bpm_pct"])
        elif metric == "vorp":
            p["tier"] = assign_tier(p["vorp_pct"])
        elif metric == "combined":
            combined_pct = (p["rapm_pct"] + p["bpm_pct"] + p["vorp_pct"]) / 3
            p["tier"] = assign_tier(combined_pct)
        else:
            p["tier"] = assign_tier(p["rapm_pct"])

    for p in pool:
        p["sim"] = cosine_similarity(target_style, p["style"])

    tier_samples = {
        "bench_unit": [],
        "rotation_piece": [],
        "starter": [],
        "all_conference": [],
        "all_american": []
    }

    for tier in tier_samples:
        tier_players = [p for p in pool if p["tier"] == tier]
        tier_players.sort(key=lambda x: -x["sim"])
        tier_samples[tier] = tier_players[:20]

    balanced_pool = []
    for tier_players in tier_samples.values():
        balanced_pool.extend(tier_players)

    pool = balanced_pool

    player_tier = assign_tier(target_pct)

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
            "bpm_pct": float(p["bpm_pct"]),
            "vorp_pct": float(p["vorp_pct"]),
        })

    for k in buckets:
        buckets[k] = sorted(buckets[k], key=lambda x: -x["similarity"])[:top_k]

    return {
        "player_tier": player_tier,
        "metric": metric,
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
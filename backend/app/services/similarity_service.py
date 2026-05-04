from app.cache.player_vectors import PLAYER_VECTORS
from app.models.similarity import cosine_similarity
import numpy as np

# -------------------------
# SAFE YEAR
# -------------------------

def safe_year(y):
    try:
        if y is None:
            return None
        return int(str(y))
    except:
        return None


def get_latest_year(year_map):
    if not year_map:
        return None
    return max(year_map.keys(), key=lambda x: int(x))


# -------------------------
# NORMALIZATION
# -------------------------

def normalize(v):
    n = np.linalg.norm(v)
    if n < 1e-8:
        return v
    return v / n


def build_style(vec):
    return np.array(vec["style"], dtype=float)


def build_impact(vec):
    return np.array(vec["impact"], dtype=float)


# -------------------------
# CAREER VECTOR
# -------------------------

def build_career_vector(year_map):
    """Aggregate all seasons into one career vector"""
    if not year_map:
        return None, None

    style_list = []
    impact_list = []

    for _, vec in year_map.items():
        style_list.append(vec["style"])
        impact_list.append(vec["impact"])

    style = np.mean(style_list, axis=0)
    impact = np.mean(impact_list, axis=0)

    return {
        "style": style,
        "impact": impact
    }, "career"


# -------------------------
# VECTOR SELECTOR (CRITICAL FIX)
# -------------------------

def get_vector(year_map, year=None):
    """
    Returns:
    - (vector, label)
    where label is either:
      - year (int)
      - "career"
    """

    if not year_map:
        return None, None

    # -------------------------
    # CAREER MODE
    # -------------------------
    if year == "career":
        return build_career_vector(year_map)

    latest = get_latest_year(year_map)

    # Latest mode (default)
    if year is None:
        return year_map[latest], latest

    year = safe_year(year)

    # Specific season
    if year in year_map:
        return year_map[year], year

    # fallback
    return year_map[latest], latest


# -------------------------
# MAIN SIMILARITY
# -------------------------

def get_similar_players(player_code, year=None, top_k=10, style_weight=0.7):

    if player_code not in PLAYER_VECTORS:
        return {"style": [], "impact": [], "combined": []}

    player_data = PLAYER_VECTORS[player_code]

    target, target_label = get_vector(player_data, year)
    if target is None:
        return {"style": [], "impact": [], "combined": []}

    style_a = normalize(build_style(target))
    impact_a = normalize(build_impact(target))

    style_scores = []
    impact_scores = []
    combined_scores = []

    # -------------------------
    # COMPARE ALL PLAYERS
    # -------------------------

    for code, year_map in PLAYER_VECTORS.items():
        if code == player_code:
            continue

        vec, used_label = get_vector(year_map, year)

        if vec is None:
            continue

        style_b = normalize(build_style(vec))
        impact_b = normalize(build_impact(vec))

        style_sim = cosine_similarity(style_a, style_b)
        impact_sim = cosine_similarity(impact_a, impact_b)

        combined_sim = (
            style_weight * style_sim +
            (1 - style_weight) * impact_sim
        )

        base = {
            "player_code": code,
            "year": used_label,   # can be int OR "career"
        }

        style_scores.append({
            **base,
            "similarity": float(style_sim),
            "reasons": []
        })

        impact_scores.append({
            **base,
            "similarity": float(impact_sim),
            "reasons": []
        })

        combined_scores.append({
            **base,
            "similarity": float(combined_sim),
            "reasons": []
        })

    if not combined_scores:
        return {"style": [], "impact": [], "combined": []}

    return {
        "style": sorted(style_scores, key=lambda x: -x["similarity"])[:top_k],
        "impact": sorted(impact_scores, key=lambda x: -x["similarity"])[:top_k],
        "combined": sorted(combined_scores, key=lambda x: -x["similarity"])[:top_k],
    }
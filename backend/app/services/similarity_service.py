from app.cache.player_vectors import PLAYER_VECTORS
from app.models.similarity import cosine_similarity
import numpy as np

# -------------------------
# FEATURE LABELS
# -------------------------

STYLE_FEATURES = [
    "3PT Volume",
    "Rim Pressure",
    "Midrange",
    "Playmaking",
    "Off-Ball",
    "Turnovers",
]

IMPACT_FEATURES = [
    "Scoring Impact",
    "Assist Impact",
    "Rebounding Impact",
    "Defense Impact",
    "Efficiency",
]

# -------------------------
# 🔥 FIXED: RELATIVE DIFFERENCE SCORING
# -------------------------

def extract_reasons(a, b, labels, top_n=3, similar=True, scale=1.0):
    """
    similarity mode → smallest relative gaps
    difference mode → largest relative gaps
    """

    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)

    diffs = np.abs(a - b)

    n = min(len(diffs), len(labels))
    if n == 0:
        return []

    diffs = diffs[:n]
    labels = labels[:n]

    # -------------------------
    # 🔥 KEY FIX: normalize per-vector spread
    # (prevents everything looking "small")
    # -------------------------
    spread = np.std(np.concatenate([a[:n], b[:n]])) + 1e-8
    diffs = diffs / spread

    # rank
    idxs = np.argsort(diffs)

    if not similar:
        idxs = idxs[::-1]

    results = []
    for i in idxs[:top_n]:
        # Only include if the difference is meaningful
        if diffs[i] > 0.1 or not similar:  # For differences, include even small ones if they're the largest
            results.append({
                "feature": labels[i],
                "delta": float(diffs[i] * scale)
            })

    # If we don't have enough results, add more even if they're small
    if len(results) < top_n:
        for i in idxs[top_n:]:
            if len(results) >= top_n:
                break
            results.append({
                "feature": labels[i],
                "delta": float(diffs[i] * scale)
            })

    return results


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
# NORMALIZATION (SIMILARITY ONLY)
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
# VECTOR SELECTOR
# -------------------------

def get_vector(year_map, year=None):

    if not year_map:
        return None, None

    if year == "career":
        return build_career_vector(year_map)

    latest = get_latest_year(year_map)

    if year is None:
        return year_map[latest], latest

    year = safe_year(year)

    if year in year_map:
        return year_map[year], year

    return year_map[latest], latest


# -------------------------
# MAIN SIMILARITY
# -------------------------

def get_similar_players(ncaa_id, year=None, top_k=10, style_weight=0.7, require_yoy_data=False):

    if ncaa_id not in PLAYER_VECTORS:
        return {"style": [], "impact": [], "combined": []}

    player_data = PLAYER_VECTORS[ncaa_id]

    target, _ = get_vector(player_data, year)
    if not target:
        return {"style": [], "impact": [], "combined": []}

    style_raw_a = build_style(target)
    impact_raw_a = build_impact(target)

    style_a = normalize(style_raw_a)
    impact_a = normalize(impact_raw_a)

    style_scores = []
    impact_scores = []
    combined_scores = []

    for ncaa_id_check, year_map in PLAYER_VECTORS.items():
        if ncaa_id_check == ncaa_id:
            continue

        # Filter for players with year-over-year data if requested
        if require_yoy_data and len(year_map) < 2:
            continue

        vec, used_label = get_vector(year_map, year)
        if vec is None:
            continue

        style_raw_b = build_style(vec)
        impact_raw_b = build_impact(vec)

        style_b = normalize(style_raw_b)
        impact_b = normalize(impact_raw_b)

        style_sim = cosine_similarity(style_a, style_b)
        impact_sim = cosine_similarity(impact_a, impact_b)

        combined_sim = (
            style_weight * style_sim +
            (1 - style_weight) * impact_sim
        )

        # -------------------------
        # 🔥 SAME STRUCTURE FOR BOTH
        # -------------------------

        style_reasons = extract_reasons(style_raw_a, style_raw_b, STYLE_FEATURES, similar=True)
        impact_reasons = extract_reasons(impact_raw_a, impact_raw_b, IMPACT_FEATURES, similar=True)

        style_diffs = extract_reasons(style_raw_a, style_raw_b, STYLE_FEATURES, similar=False, scale=2.0)
        impact_diffs = extract_reasons(impact_raw_a, impact_raw_b, IMPACT_FEATURES, similar=False, scale=2.0)

        combined_reasons = style_reasons[:2] + impact_reasons[:1]
        combined_diffs = style_diffs[:3] + impact_diffs[:2]

        base = {
            "AthleteSourceId": ncaa_id_check,
            "year": used_label,
        }

        style_scores.append({
            **base,
            "similarity": float(style_sim),
            "reasons": style_reasons,
            "differences": style_diffs
        })

        impact_scores.append({
            **base,
            "similarity": float(impact_sim),
            "reasons": impact_reasons,
            "differences": impact_diffs
        })

        combined_scores.append({
            **base,
            "similarity": float(combined_sim),
            "reasons": combined_reasons,
            "differences": combined_diffs
        })

    return {
        "style": sorted(style_scores, key=lambda x: -x["similarity"])[:top_k],
        "impact": sorted(impact_scores, key=lambda x: -x["similarity"])[:top_k],
        "combined": sorted(combined_scores, key=lambda x: -x["similarity"])[:top_k],
    }
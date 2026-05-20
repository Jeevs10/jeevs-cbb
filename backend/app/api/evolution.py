from typing import Union
from fastapi import APIRouter
from app.services.evolution_service import get_player_evolution

router = APIRouter()

@router.get("/players/{ncaa_id}/evolution")
def player_evolution(ncaa_id: str, year: Union[int, str, None] = None):

    result = get_player_evolution(float(ncaa_id), year)

    # -------------------------
    # SAFETY NORMALIZATION
    # -------------------------
    if not result:
        return {
            "player_tier": None,
            "bench_unit": [],
            "rotation_piece": [],
            "starter": [],
            "all_conference": [],
            "all_american": []
        }

    # ensure all keys exist even if service omits something
    normalized = {
        "player_tier": result.get("player_tier"),
        "bench_unit": result.get("bench_unit", []),
        "rotation_piece": result.get("rotation_piece", []),
        "starter": result.get("starter", []),
        "all_conference": result.get("all_conference", []),
        "all_american": result.get("all_american", []),
    }

    return normalized
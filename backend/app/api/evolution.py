from fastapi import APIRouter
from app.services.evolution_service import get_player_evolution

router = APIRouter()

@router.get("/players/{player_identifier}/evolution")
def player_evolution(player_identifier: str, year: int | str | None = None):
    """
    Get player evolution data by either player_id or player_code.
    
    Args:
        player_identifier: Either player_id (preferred) or player_code (legacy)
        year: Year to get data for, or "career" for career stats
    """

    result = get_player_evolution(player_identifier, year)

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
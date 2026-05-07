from fastapi import APIRouter
from app.core.player_resolver import get_player_snapshot
from app.features.badges import get_player_badges
from app.core.year_utils import normalize_year

router = APIRouter()


@router.get("/players/{player_identifier}/badges")
def player_badges(player_identifier: str, year: int | str | None = None):
    """
    Get player badges by either player_id or player_code.
    
    Args:
        player_identifier: Either player_id (preferred) or player_code (legacy)
        year: Year to get data for, or "career" for career stats
    """

    year = normalize_year(year)

    player = get_player_snapshot(player_identifier, year)

    if not player:
        return {"error": "Player not found"}

    return get_player_badges(player)
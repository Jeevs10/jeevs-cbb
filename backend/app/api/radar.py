from fastapi import APIRouter
from app.core.player_resolver import get_player_snapshot
from app.features.radar import compute_player_radar
from app.core.year_utils import normalize_year

router = APIRouter()


@router.get("/players/{player_identifier}/radar")
def player_radar(
    player_identifier: str,
    year: int | str | None = None
):
    """
    Get player radar data by either player_id or player_code.
    
    Args:
        player_identifier: Either player_id (preferred) or player_code (legacy)
        year: Year to get data for, or "career" for career stats
    """

    year = normalize_year(year)

    player = get_player_snapshot(player_identifier, year)

    if not player:
        return {"error": "Player not found"}

    return compute_player_radar(player)
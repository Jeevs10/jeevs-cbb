from fastapi import APIRouter
from app.core.player_resolver import get_player_snapshot
from app.features.badges import get_player_badges
from app.core.year_utils import normalize_year

router = APIRouter()


@router.get("/players/{player_code}/badges")
def player_badges(player_code: str, year: int | str | None = None):

    year = normalize_year(year)

    player = get_player_snapshot(player_code, year)

    if not player:
        return {"error": "Player not found"}

    return get_player_badges(player)
from typing import Union
from fastapi import APIRouter
from app.core.player_resolver import get_player_snapshot
from app.features.badges import get_player_badges
from app.core.year_utils import normalize_year

router = APIRouter()


@router.get("/players/{ncaa_id}/badges")
def player_badges(ncaa_id: str, year: Union[int, str, None] = None):
    year = normalize_year(year)
    player = get_player_snapshot(ncaa_id, year)

    if not player:
        return {"error": "Player not found"}

    return get_player_badges(player)
from typing import Union
from fastapi import APIRouter
from app.core.player_resolver import get_player_snapshot
from app.features.moves import get_player_moves
from app.core.year_utils import normalize_year

router = APIRouter()


@router.get("/players/{ncaa_id}/moves")
def player_moves(ncaa_id: str, year: Union[int, str, None] = None):
    year = normalize_year(year)
    player = get_player_snapshot(ncaa_id, year)

    if not player:
        return {"error": "Player not found"}

    return get_player_moves(player)
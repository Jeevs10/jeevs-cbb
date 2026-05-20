from typing import Union, Optional, List
from fastapi import APIRouter, Query
from app.core.player_resolver import get_player_snapshot
from app.features.radar import compute_player_radar
from app.core.year_utils import normalize_year

router = APIRouter()


@router.get("/players/{ncaa_id}/radar")
def player_radar(
    ncaa_id: str,
    year: Union[int, str, None] = None,
    preset: Optional[str] = "overview",
    custom_fields: Optional[List[str]] = Query(None)
):
    year = normalize_year(year)
    player = get_player_snapshot(ncaa_id, year)

    if not player:
        return {"error": "Player not found"}

    return compute_player_radar(player, preset, custom_fields)
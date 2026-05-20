from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.services.player_service import PlayerService
from app.models.schemas import PlayerQueryParams, PlayerListResponse, PlayerResponse
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/players", response_model=PlayerListResponse)
def get_players(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort: str = Query(default="adj_rapm_margin"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    year: Optional[str] = Query(default=None),
    conf: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    dataTier: Optional[str] = Query(default=None, pattern="^(basic|enriched)$"),
    d1Only: Optional[bool] = Query(default=False),
    highMajorOnly: Optional[bool] = Query(default=False),
):
    """Get players with filtering, sorting, and pagination."""
    try:
        params = PlayerQueryParams(
            limit=limit,
            offset=offset,
            sort=sort,
            order=order,
            year=year,
            conf=conf,
            search=search,
            dataTier=dataTier,
            d1Only=d1Only,
            highMajorOnly=highMajorOnly
        )
        
        return PlayerService.get_players(params)
        
    except ValueError as e:
        logger.warning(f"Validation error in players endpoint: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in players endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/players/{ncaa_id}", response_model=PlayerResponse)
def get_player(
    ncaa_id: str,
    year: Optional[str] = Query(default=None)
):
    """Get a specific player by NCAA ID."""
    try:
        return PlayerService.get_player_by_id(ncaa_id, year)
        
    except ValueError as e:
        if "Player not found" in str(e):
            logger.warning(f"Player not found: {ncaa_id}")
            raise HTTPException(status_code=404, detail="Player not found")
        logger.warning(f"Validation error in player endpoint: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in player endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
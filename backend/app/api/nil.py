"""API endpoints for NIL valuation."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.services.nil_service import NilService
from app.models.schemas import NilValuationResponse, TeamNilResponse, NilListResponse
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/nil/players/{ncaa_id}", response_model=NilValuationResponse)
def get_player_nil(
    ncaa_id: str,
    year: Optional[str] = Query(default=None)
):
    """Get NIL valuation for a specific player."""
    try:
        valuation = NilService.calculate_player_nil(ncaa_id, year)
        return NilValuationResponse(
            success=True,
            valuation=valuation
        )
    except ValueError as e:
        if "Player not found" in str(e):
            logger.warning(f"Player not found: {ncaa_id}")
            raise HTTPException(status_code=404, detail="Player not found")
        logger.warning(f"Validation error in NIL endpoint: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in NIL endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/nil/teams/{team_id}", response_model=TeamNilResponse)
def get_team_nil(
    team_id: str,
    year: Optional[str] = Query(default=None)
):
    """Get NIL valuations for all players on a team."""
    try:
        team_valuations = NilService.calculate_team_nil(team_id, year)
        return TeamNilResponse(
            success=True,
            team_id=team_valuations["team_id"],
            team_name=team_valuations["team_name"],
            year=team_valuations["year"],
            total_team_value=team_valuations["total_team_value"],
            valuations=team_valuations["valuations"]
        )
    except ValueError as e:
        if "No roster found" in str(e):
            logger.warning(f"No roster found for team: {team_id}")
            raise HTTPException(status_code=404, detail="No roster found for this team")
        logger.warning(f"Validation error in team NIL endpoint: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in team NIL endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/nil/players", response_model=NilListResponse)
def get_all_nil(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort: str = Query(default="nil_score"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    year: Optional[str] = Query(default=None),
    conf: Optional[str] = Query(default=None)
):
    """Get NIL valuations with filtering and sorting."""
    try:
        valuations = NilService.get_all_nil_valuations(
            limit=limit,
            offset=offset,
            sort=sort,
            order=order,
            year=year,
            conf=conf
        )
        return NilListResponse(
            success=True,
            count=valuations["count"],
            filtered_count=valuations["filtered_count"],
            results=valuations["results"]
        )
    except Exception as e:
        logger.error(f"Unexpected error in NIL list endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Union, List, Dict, Any

from app.services.team_service import TeamService
from app.models.schemas import TeamListResponse, TeamResponse
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/teams", response_model=TeamListResponse)
def get_teams(year: Optional[Union[int, str]] = Query(None, description="Year to filter teams (e.g., 2025, 2026)")):
    """Get list of all teams with analytics data."""
    try:
        teams = TeamService.get_all_teams_with_analytics(year=year)
        return TeamListResponse(
            count=len(teams),
            results=teams
        )
    except Exception as e:
        logger.error(f"Unexpected error in teams endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(team_id: str, year: Optional[Union[int, str]] = None):
    """Get a specific team by ID."""
    try:
        team_data = TeamService.get_team_by_id(team_id, year)
        available_years = TeamService.get_available_years_for_team(team_id)
        return {"team": team_data, "available_years": available_years}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting team {team_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/teams/{team_id}/matchups")
async def get_team_matchups(
    team_id: str, 
    threshold: float = Query(0.05, description="Score threshold for matchups"),
    filter_type: str = Query("all", description="Filter type: all, conference, quartile")
):
    """Get matchups for a specific team based on style analytics."""
    try:
        matchups = TeamService.calculate_team_matchups(team_id, threshold, filter_type)
        return {
            "team_id": team_id,
            "matchups": matchups
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating matchups for team {team_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/teams/{team_id}/analytics-debug")
async def get_team_analytics_debug(team_id: str):
    """Get analytics debug info for a specific team."""
    try:
        debug_info = TeamService.get_team_analytics_debug(team_id)
        return debug_info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting analytics debug for team {team_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/teams/{team_id}/matchup/{opponent_id}")
async def get_team_vs_opponent_matchup(team_id: str, opponent_id: str):
    """Get matchup between two specific teams based on style analytics."""
    try:
        matchup = TeamService.calculate_single_matchup(team_id, opponent_id)
        return {
            "team_id": team_id,
            "opponent_id": opponent_id,
            "matchup": matchup
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating matchup between {team_id} and {opponent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/teams/{team_id}/similar")
async def get_similar_teams(
    team_id: str,
    style_weight: float = Query(0.5, description="Weight for style vector (0-1), where 0 = pure impact, 1 = pure style"),
    limit: int = Query(10, description="Maximum number of similar teams to return")
):
    """Get similar teams based on impact and style vectors."""
    try:
        similar_teams = TeamService.calculate_similar_teams(team_id, style_weight, limit)
        return similar_teams
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating similar teams for {team_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

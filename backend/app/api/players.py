from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import json
import os
import pandas as pd
import numpy as np

from app.services.player_service import PlayerService
from app.models.schemas import PlayerQueryParams, PlayerListResponse, PlayerResponse
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

# In-memory cache for game data files (historical data, no expiration needed)
_game_data_cache = {}

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

@router.get("/players/{ncaa_id}/games")
def get_player_games(
    ncaa_id: str,
    year: Optional[str] = Query(default=None),
    limit: int = Query(default=5, ge=1, le=1000)
):
    """Get a player's recent game data."""
    try:
        # Use year from query param or default to 2026
        year_to_load = year if year else "2026"
        
        # Load game data file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        game_data_file = os.path.join(base_dir, "data", "games", f"{year_to_load}_player_game_data.json")
        
        if not os.path.exists(game_data_file):
            raise HTTPException(status_code=404, detail=f"Game data not found for year {year_to_load}")
        
        # Check cache first (historical data, no expiration)
        if year_to_load in _game_data_cache:
            game_data = _game_data_cache[year_to_load]
        else:
            with open(game_data_file, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
            _game_data_cache[year_to_load] = game_data
        
        # Filter games for this player (by ncaa_id)
        player_games = [game for game in game_data if game.get('ncaa_id') == ncaa_id]
        
        if not player_games:
            # Check which years have data for this player
            available_years = []
            for check_year in range(2019, 2027):
                check_file = os.path.join(base_dir, "data", "games", f"{check_year}_player_game_data.json")
                if os.path.exists(check_file):
                    try:
                        with open(check_file, 'r', encoding='utf-8') as f:
                            check_data = json.load(f)
                        if any(g.get('ncaa_id') == ncaa_id for g in check_data):
                            available_years.append(check_year)
                    except:
                        pass
            
            if available_years:
                raise HTTPException(
                    status_code=404, 
                    detail=f"No games found for player {ncaa_id} in year {year_to_load}. Available years: {available_years}"
                )
            else:
                raise HTTPException(status_code=404, detail="No games found for this player")
        
        # Sort by date (numdate) descending and take the most recent
        player_games.sort(key=lambda x: x.get('numdate', ''), reverse=True)
        recent_games = player_games[:limit]
        
        return {
            "player_id": ncaa_id,
            "year": year_to_load,
            "total_games": len(player_games),
            "games": recent_games
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in player games endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
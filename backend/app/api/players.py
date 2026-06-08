from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import json
import os
import gzip
import pandas as pd
import numpy as np
from pathlib import Path

from app.services.player_service import PlayerService
from app.models.schemas import PlayerQueryParams, PlayerListResponse, PlayerResponse
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

# In-memory cache for game data files (historical data, no expiration needed)
_game_data_cache = {}

@router.get("/players", response_model=PlayerListResponse)
def get_players(
    limit: int = Query(default=50, ge=1, le=5000),
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

@router.get("/projections/2027")
def get_2027_projections():
    """Get 2027 BPM projections."""
    try:
        projections_path = Path(__file__).parent.parent.parent / "data" / "bpm_projections_2027.csv"
        
        if not projections_path.exists():
            raise HTTPException(status_code=404, detail="Projections file not found")
        
        df = pd.read_csv(projections_path)
        
        # Replace NaN values with None for JSON compatibility
        df = df.replace({float('nan'): None})
        
        # Convert to list of dicts
        projections = df.to_dict(orient="records")
        
        return projections
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading projections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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

        # Load game data file (try compressed first)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        game_data_file = os.path.join(base_dir, "data", "games", f"{year_to_load}_player_game_data.json")
        game_data_file_gz = os.path.join(base_dir, "data", "games", f"{year_to_load}_player_game_data.json.gz")

        # Check cache first (historical data, no expiration)
        if year_to_load in _game_data_cache:
            game_data = _game_data_cache[year_to_load]
        else:
            # Try compressed file first
            if os.path.exists(game_data_file_gz):
                with gzip.open(game_data_file_gz, 'rt', encoding='utf-8') as f:
                    game_data = json.load(f)
            elif os.path.exists(game_data_file):
                with open(game_data_file, 'r', encoding='utf-8') as f:
                    game_data = json.load(f)
            else:
                raise HTTPException(status_code=404, detail=f"Game data not found for year {year_to_load}")
            _game_data_cache[year_to_load] = game_data

        # Filter games for this player (by ncaa_id)
        player_games = [game for game in game_data if game.get('ncaa_id') == ncaa_id]

        if not player_games:
            # Check which years have data for this player
            available_years = []
            for check_year in range(2019, 2027):
                check_file = os.path.join(base_dir, "data", "games", f"{check_year}_player_game_data.json")
                check_file_gz = os.path.join(base_dir, "data", "games", f"{check_year}_player_game_data.json.gz")
                
                # Try compressed file first
                if os.path.exists(check_file_gz):
                    try:
                        with gzip.open(check_file_gz, 'rt', encoding='utf-8') as f:
                            check_data = json.load(f)
                        if any(g.get('ncaa_id') == ncaa_id for g in check_data):
                            available_years.append(check_year)
                    except:
                        pass
                elif os.path.exists(check_file):
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


@router.get("/players/{ncaa_id}/historical-bpm")
def get_player_historical_bpm(ncaa_id: str):
    """Get a player's historical BPM data across all available years."""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        historical_bpm = []

        # Clean the ncaa_id - remove .0 suffix if present
        ncaa_id_clean = str(ncaa_id).replace('.0', '')

        # Check each year from 2019 to 2026
        for year in range(2019, 2027):
            players_file = os.path.join(base_dir, "data", "players", f"{year}-players_basic.csv")
            if not os.path.exists(players_file):
                continue

            try:
                df = pd.read_csv(players_file)
                # Clean AthleteSourceId in dataframe for comparison
                if 'AthleteSourceId' in df.columns:
                    df['AthleteSourceId_clean'] = df['AthleteSourceId'].astype(str).str.replace('.0', '')
                else:
                    df['AthleteSourceId_clean'] = None

                # Try to find player by AthleteSourceId (cleaned) or AthleteId
                player_row = df[
                    (df['AthleteSourceId_clean'] == ncaa_id_clean) |
                    (df['AthleteId'].astype(str) == ncaa_id_clean)
                ]

                if not player_row.empty:
                    player_data = player_row.iloc[0]
                    historical_bpm.append({
                        'year': year,
                        'BPM': player_data.get('BPM'),
                        'Name': player_data.get('Name'),
                        'Team': player_data.get('Team')
                    })
                    logger.info(f"Found player {ncaa_id_clean} in year {year}: BPM={player_data.get('BPM')}")
            except Exception as e:
                logger.warning(f"Error reading {year} player data: {e}")
                continue

        if not historical_bpm:
            logger.warning(f"No historical BPM data found for player {ncaa_id_clean}")
            raise HTTPException(status_code=404, detail="No historical BPM data found for this player")

        # Sort by year
        historical_bpm.sort(key=lambda x: x['year'])
        logger.info(f"Returning {len(historical_bpm)} historical BPM records for player {ncaa_id_clean}")

        return {
            "player_id": ncaa_id,
            "historical_bpm": historical_bpm
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in historical BPM endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/clusters/{cluster_id}/bpm-distribution")
def get_cluster_bpm_distribution(cluster_id: int):
    """Get BPM distribution for a specific cluster."""
    try:
        from app.services.projection_service import get_projection_service

        service = get_projection_service()
        service._ensure_data_loaded()
        
        if service._clusters_df is None:
            raise HTTPException(status_code=404, detail="Cluster data not loaded")
        
        # Get cluster description from cluster_descriptions.json
        cluster_desc_data = service._cluster_descriptions.get(str(cluster_id))
        
        if cluster_desc_data is None:
            raise HTTPException(status_code=404, detail="Cluster not found")
        
        avg_bpm = cluster_desc_data.get('avg_bpm', 0)
        count = cluster_desc_data.get('count', 0)
        
        if service._players_df is None:
            raise HTTPException(status_code=404, detail="Player data not loaded")
        
        # Get players in this cluster from clusters data
        # Convert cluster_id to match the type in the dataframe
        cluster_players = service._clusters_df[
            service._clusters_df['cluster'].astype(str) == str(cluster_id)
        ].copy()
        
        logger.info(f"Found {len(cluster_players)} players in cluster {cluster_id}")
        
        # Extract BPM values directly from cluster data
        bpm_column = 'BPM' if 'BPM' in cluster_players.columns else 'bpm'
        logger.info(f"Using BPM column: {bpm_column}")
        bpm_values = cluster_players[bpm_column].dropna().tolist()
        
        logger.info(f"Found {len(bpm_values)} BPM values for cluster {cluster_id}")
        
        if len(bpm_values) == 0:
            # Fallback to simulated distribution if no current data
            try:
                std_dev = 5.0 / np.sqrt(count) if count > 0 else 2.0
                distribution = np.random.normal(avg_bpm, std_dev, 100).tolist()
            except Exception as e:
                logger.error(f"Error generating fallback distribution: {e}")
                distribution = [avg_bpm] * 100
        else:
            distribution = bpm_values

        try:
            percentiles = {
                "p25": float(np.percentile(distribution, 25)),
                "p50": float(np.percentile(distribution, 50)),
                "p75": float(np.percentile(distribution, 75)),
                "p90": float(np.percentile(distribution, 90)),
                "p10": float(np.percentile(distribution, 10)),
            }
        except Exception as e:
            logger.error(f"Error calculating percentiles: {e}")
            percentiles = {
                "p25": 0,
                "p50": 0,
                "p75": 0,
                "p90": 0,
                "p10": 0,
            }

        return {
            "cluster_id": cluster_id,
            "avg_bpm": avg_bpm,
            "count": count,
            "distribution": sorted(distribution),
            "percentiles": percentiles,
            "sample_size": len(distribution)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in cluster BPM distribution endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
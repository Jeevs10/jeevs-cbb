from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Union
from app.core.player_graph import player_graph

router = APIRouter()


class PlayerInfo(BaseModel):
    id: str
    name: str
    team: Optional[str] = None
    year: Optional[int] = None
    teams: Optional[List[str]] = None
    years: Optional[List[int]] = None
    Position: Optional[str] = None
    roster_height: Optional[Union[str, float]] = None
    hometown: Optional[str] = None
    conf: Optional[str] = None


class GamePairResponse(BaseModel):
    start_player: PlayerInfo
    end_player: PlayerInfo
    distance: int


class TeammateCheckRequest(BaseModel):
    player_id1: str
    player_id2: str


class TeammateCheckResponse(BaseModel):
    are_teammates: bool
    teammate_info: Optional[dict] = None


class ShortestPathRequest(BaseModel):
    player_id1: str
    player_id2: str


class ReloadGraphRequest(BaseModel):
    conferences: Optional[List[str]] = None
    years: Optional[List[int]] = None


@router.get("/game/random-pair", response_model=GamePairResponse)
def get_random_pair(
    min_distance: int = Query(3, ge=1),
    max_distance: int = Query(6, ge=1)
):
    """Get a random pair of connected players for the game"""
    try:
        pair = player_graph.get_random_reachable_pair(min_distance, max_distance)
        return GamePairResponse(
            start_player=PlayerInfo(**pair['start_player']),
            end_player=PlayerInfo(**pair['end_player']),
            distance=pair['distance']
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/game/reload-graph")
def reload_graph(request: ReloadGraphRequest):
    """Reload the player graph with new conference and year filters"""
    try:
        player_graph.reload_with_filters(conferences=request.conferences, years=request.years)
        return {"message": "Graph reloaded successfully", "nodes": player_graph.graph.number_of_nodes(), "edges": player_graph.graph.number_of_edges()}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to reload graph: {str(e)}")


@router.get("/game/player/{player_id}")
def get_game_player_info(player_id: str):
    """Get player info from the player graph (includes all teams and years)"""
    try:
        player_info = player_graph.get_player_info(player_id)
        if not player_info:
            raise HTTPException(status_code=404, detail="Player not found in graph")
        return player_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/game/check-teammates", response_model=TeammateCheckResponse)
def check_teammates(request: TeammateCheckRequest):
    """Check if two players were teammates"""
    try:
        are_teammates = player_graph.are_teammates(request.player_id1, request.player_id2)
        teammate_info = None
        
        if are_teammates:
            teammate_info = player_graph.get_teammate_info(request.player_id1, request.player_id2)
        
        return TeammateCheckResponse(
            are_teammates=are_teammates,
            teammate_info=teammate_info
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/game/shortest-path")
def get_shortest_path(request: ShortestPathRequest):
    """Get shortest path between two players"""
    try:
        path = player_graph.get_shortest_path(request.player_id1, request.player_id2)
        
        if path is None:
            raise HTTPException(status_code=404, detail="No path found between players")
        
        return {"path": path}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

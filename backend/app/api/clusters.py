from typing import Union, List
from fastapi import APIRouter, Query
import pandas as pd
from pathlib import Path
import json
from app.core.data_loader import df
from app.services.player_service import PlayerService
from app.models.schemas import PlayerQueryParams

router = APIRouter()

DATA_DIR = Path(__file__).parent.parent.parent / "data"

@router.get("/clusters/descriptions")
def get_cluster_descriptions(year: Union[str, None] = Query(default=None)):
    """Get cluster descriptions for a specific year or all-time."""
    if year:
        cluster_file = DATA_DIR / f"cluster_descriptions_{year}.json"
    else:
        cluster_file = DATA_DIR / "cluster_descriptions.json"
    
    if cluster_file.exists():
        with open(cluster_file, 'r') as f:
            return json.load(f)
    else:
        return {"error": f"Cluster descriptions not found for year {year}"}

@router.get("/clusters/rankings")
def cluster_rankings(
    cluster_id: int = Query(..., description="Cluster ID (0-17)"),
    year: Union[str, None] = Query(default=None, description="Year filter"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    sort_by: Union[str, None] = Query(default="BPM", description="Sort by field"),
    sort_order: Union[str, None] = Query(default="desc", description="Sort order (asc/desc)"),
):
    """Get rankings of players within a specific cluster."""
    try:
        # Load cluster descriptions to get cluster info
        cluster_file = DATA_DIR / "cluster_descriptions.json"
        if cluster_file.exists():
            with open(cluster_file, 'r') as f:
                cluster_descriptions = json.load(f)
        else:
            return {"error": "Cluster descriptions not found", "success": False}
        
        # Validate cluster_id
        if cluster_id < 0 or cluster_id >= len(cluster_descriptions):
            return {"error": f"Invalid cluster_id. Must be between 0 and {len(cluster_descriptions) - 1}", "success": False}
        
        # Load cluster assignments from player_clusters.csv
        clusters_csv = DATA_DIR / "player_clusters.csv"
        if not clusters_csv.exists():
            return {"error": "Cluster data file not found", "success": False}
        
        cluster_df = pd.read_csv(clusters_csv)
        
        # Filter by year if specified
        if year:
            cluster_df = cluster_df[cluster_df['year'] == int(year)]
        else:
            # Use latest year if no year specified
            latest_year = cluster_df['year'].max()
            cluster_df = cluster_df[cluster_df['year'] == latest_year]
        
        # Filter to players in the specified cluster
        cluster_df = cluster_df[cluster_df['cluster'] == cluster_id]
        
        if cluster_df.empty:
            return {
                "results": [],
                "count": 0,
                "filtered_count": 0,
                "cluster_info": cluster_descriptions[cluster_id],
                "success": True
            }
        
        # Get AthleteSourceIds for players in this cluster
        cluster_ids = cluster_df['AthleteSourceId'].astype(str).tolist()
        
        # Filter main player dataframe to these players
        if year:
            df_filtered = df[df['year'] == int(year)].copy()
        else:
            latest_year = df['year'].max()
            df_filtered = df[df['year'] == latest_year].copy()
        
        # Normalize player keys for matching
        df_filtered['player_key'] = df_filtered['player_key'].astype(str)
        
        # Filter to players in the cluster
        cluster_players = df_filtered[df_filtered['player_key'].isin(cluster_ids)]
        
        if cluster_players.empty:
            return {
                "results": [],
                "count": len(df_filtered),
                "filtered_count": 0,
                "cluster_info": cluster_descriptions[cluster_id],
                "success": True
            }
        
        # Sort by specified column
        if sort_by in cluster_players.columns:
            reverse = sort_order != "asc"
            cluster_players = cluster_players.sort_values(by=sort_by, ascending=not reverse)
        else:
            # Fallback to BPM if sort column doesn't exist
            cluster_players = cluster_players.sort_values(by='BPM', ascending=False)
        
        # Add ranking before pagination
        cluster_players = cluster_players.reset_index(drop=True)
        cluster_players['rank'] = cluster_players.index + 1
        
        # Apply pagination
        total_filtered = len(cluster_players)
        cluster_players = cluster_players.iloc[offset:offset + limit]
        
        # Convert to dictionaries
        players_list = []
        for _, player in cluster_players.iterrows():
            player_dict = player.to_dict()
            player_dict['rank'] = int(player['rank'])
            # Replace NaN values with None
            player_dict = {k: (None if pd.isna(v) else v) for k, v in player_dict.items()}
            players_list.append(player_dict)
        
        return {
            "results": players_list,
            "count": len(df_filtered),
            "filtered_count": total_filtered,
            "cluster_info": cluster_descriptions[cluster_id],
            "success": True
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e), "success": False}

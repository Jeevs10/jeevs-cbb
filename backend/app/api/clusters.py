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
        if year and year != "all":
            cluster_df = cluster_df[cluster_df['year'] == int(year)]
        elif year == "all":
            # Include all years
            pass
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
        # Clean IDs - remove .0 suffix if present
        cluster_ids = [id.replace('.0', '') for id in cluster_ids]
        
        # Filter main player dataframe to these players
        if year and year != "all":
            df_filtered = df[df['year'] == int(year)].copy()
        elif year == "all":
            # Include all years
            df_filtered = df.copy()
        else:
            latest_year = df['year'].max()
            df_filtered = df[df['year'] == latest_year].copy()
        
        
        # Normalize AthleteSourceId for matching
        df_filtered['AthleteSourceId'] = df_filtered['AthleteSourceId'].astype(str)
        
        # Filter to players in the cluster
        cluster_players = df_filtered[df_filtered['AthleteSourceId'].isin(cluster_ids)]
        
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
            
            # Calculate basic stats if not present
            if 'SPG' not in player_dict or pd.isna(player_dict['SPG']):
                if 'Steals' in player_dict and 'Games' in player_dict and player_dict['Games'] > 0:
                    player_dict['SPG'] = round(player_dict['Steals'] / player_dict['Games'], 1)
                else:
                    player_dict['SPG'] = 0
            
            if 'BPG' not in player_dict or pd.isna(player_dict['BPG']):
                if 'Blocks' in player_dict and 'Games' in player_dict and player_dict['Games'] > 0:
                    player_dict['BPG'] = round(player_dict['Blocks'] / player_dict['Games'], 1)
                else:
                    player_dict['BPG'] = 0
            
            if 'MPG' not in player_dict or pd.isna(player_dict['MPG']):
                if 'Minutes' in player_dict and 'Games' in player_dict and player_dict['Games'] > 0:
                    player_dict['MPG'] = round(player_dict['Minutes'] / player_dict['Games'], 1)
                else:
                    player_dict['MPG'] = 0
            
            # Calculate PPG, APG, RPG if not present
            if 'PPG' not in player_dict or pd.isna(player_dict['PPG']):
                if 'Points' in player_dict and 'Games' in player_dict and player_dict['Games'] > 0:
                    player_dict['PPG'] = round(player_dict['Points'] / player_dict['Games'], 1)
                else:
                    player_dict['PPG'] = 0
            
            if 'APG' not in player_dict or pd.isna(player_dict['APG']):
                if 'Assists' in player_dict and 'Games' in player_dict and player_dict['Games'] > 0:
                    player_dict['APG'] = round(player_dict['Assists'] / player_dict['Games'], 1)
                else:
                    player_dict['APG'] = 0
            
            if 'RPG' not in player_dict or pd.isna(player_dict['RPG']):
                if 'Rebounds' in player_dict and 'Games' in player_dict and player_dict['Games'] > 0:
                    player_dict['RPG'] = round(player_dict['Rebounds'] / player_dict['Games'], 1)
                else:
                    player_dict['RPG'] = 0
            
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

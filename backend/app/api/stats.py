"""
Stats API Routes
Handles statistical endpoints and aggregated data.
"""

from fastapi import APIRouter, Query
from app.core.data_loader import df
from app.core.year_utils import normalize_year
from app.data import get_available_years
from app.data.merger import DataMerger
from app.data.cleaner import prepare_for_display
import numpy as np
import pandas as pd

router = APIRouter()

PCT_COLS = [
    "off_usage",
    "off_assist",
    "off_to",
    "off_orb",
    "def_orb",
    "off_ftr",
    "def_stl",
    "def_blk",
    "off_threepr"
]

@router.get("/stats/summary")
def get_stats_summary(
    year: int | str | None = Query(None, description="Filter by year"),
    conf: str | None = Query(None, description="Filter by conference")
):
    """
    Get statistical summary of the dataset.
    
    Returns aggregation statistics for the current filters.
    """
    year = normalize_year(year)
    data = df.copy()
    
    # Apply filters
    if isinstance(year, int):
        data = data[data["year"] == year]
    
    if conf:
        data = data[data["conf"] == conf]
    
    # Calculate summary statistics
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    
    summary = {}
    
    # Basic counts
    summary["total_players"] = len(data)
    summary["unique_players"] = data["player_id"].nunique() if "player_id" in data.columns else 0
    summary["years"] = get_available_years()
    summary["conferences"] = DataMerger.get_conferences(data)
    
    # Statistical aggregations for key metrics
    key_metrics = [
        "adj_rapm_margin", "off_rtg", "def_rtg", "off_usage", 
        "off_assist", "def_stl", "def_blk"
    ]
    
    for metric in key_metrics:
        if metric in data.columns:
            col_data = data[metric].dropna()
            if not col_data.empty:
                summary[metric] = {
                    "mean": float(col_data.mean()),
                    "median": float(col_data.median()),
                    "std": float(col_data.std()),
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "q25": float(col_data.quantile(0.25)),
                    "q75": float(col_data.quantile(0.75))
                }
    
    return summary


@router.get("/stats/leaders")
def get_stat_leaders(
    stat: str = Query(..., description="Stat to rank players by"),
    year: int | str | None = Query(None, description="Filter by year"),
    conf: str | None = Query(None, description="Filter by conference"),
    limit: int = Query(10, ge=1, le=100, description="Number of leaders to return"),
    minimum_possessions: int = Query(200, ge=0, description="Minimum possessions to qualify")
):
    """
    Get statistical leaders for a specific metric.
    
    Returns top players ranked by the specified statistic.
    """
    year = normalize_year(year)
    data = df.copy()
    
    # Apply filters
    if isinstance(year, int):
        data = data[data["year"] == year]
    
    if conf:
        data = data[data["conf"] == conf]
    
    # Filter by minimum possessions if the column exists
    if "off_poss" in data.columns:
        data = data[data["off_poss"] >= minimum_possessions]
    
    # Check if stat exists
    if stat not in data.columns:
        return {"error": f"Stat '{stat}' not found"}
    
    # Get leaders
    leaders = data.nlargest(limit, stat)
    
    # Prepare for display
    leaders = prepare_for_display(leaders)
    
    return {
        "stat": stat,
        "filters": {
            "year": year,
            "conf": conf,
            "minimum_possessions": minimum_possessions
        },
        "leaders": leaders[[
            "player_id", "player_code", "player_name", "team", "conf", 
            "year", stat
        ]].to_dict(orient="records")
    }


@router.get("/stats/distributions")
def get_stat_distributions(
    stats: list[str] = Query(["adj_rapm_margin", "off_usage"], description="Stats to analyze"),
    year: int | str | None = Query(None, description="Filter by year"),
    conf: str | None = Query(None, description="Filter by conference"),
    bins: int = Query(20, ge=5, le=100, description="Number of histogram bins")
):
    """
    Get distribution data for specified statistics.
    
    Returns histogram data for visualization.
    """
    year = normalize_year(year)
    data = df.copy()
    
    # Apply filters
    if isinstance(year, int):
        data = data[data["year"] == year]
    
    if conf:
        data = data[data["conf"] == conf]
    
    distributions = {}
    
    for stat in stats:
        if stat in data.columns:
            col_data = data[stat].dropna()
            if not col_data.empty:
                hist, bin_edges = np.histogram(col_data, bins=bins)
                
                distributions[stat] = {
                    "histogram": hist.tolist(),
                    "bin_edges": bin_edges.tolist(),
                    "mean": float(col_data.mean()),
                    "std": float(col_data.std()),
                    "count": len(col_data)
                }
    
    return {
        "filters": {
            "year": year,
            "conf": conf,
            "bins": bins
        },
        "distributions": distributions
    }


@router.get("/stats/conferences")
def get_conference_stats(
    year: int | str | None = Query(None, description="Filter by year")
):
    """
    Get conference-level statistics.
    
    Returns aggregated stats for each conference.
    """
    year = normalize_year(year)
    data = df.copy()
    
    # Apply year filter
    if isinstance(year, int):
        data = data[data["year"] == year]
    
    if "conf" not in data.columns:
        return {"error": "Conference data not available"}
    
    # Group by conference and calculate stats
    conf_stats = []
    
    for conf_name in data["conf"].dropna().unique():
        conf_data = data[data["conf"] == conf_name]
        
        if not conf_data.empty:
            stat_summary = {}
            
            # Calculate key metrics
            for metric in ["adj_rapm_margin", "off_rtg", "def_rtg"]:
                if metric in conf_data.columns:
                    col_data = conf_data[metric].dropna()
                    if not col_data.empty:
                        stat_summary[metric] = {
                            "mean": float(col_data.mean()),
                            "median": float(col_data.median()),
                            "count": len(col_data)
                        }
            
            conf_stats.append({
                "conference": conf_name,
                "player_count": len(conf_data),
                "team_count": conf_data["team"].nunique() if "team" in conf_data.columns else 0,
                "stats": stat_summary
            })
    
    # Sort by player count
    conf_stats.sort(key=lambda x: x["player_count"], reverse=True)
    
    return {
        "year": year,
        "conferences": conf_stats
    }

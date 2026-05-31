"""API endpoints for utilization analysis."""

from fastapi import APIRouter, HTTPException
from pathlib import Path
import pandas as pd
import json

router = APIRouter()

@router.get("/utilization/correlations")
def get_utilization_correlations():
    """Get correlation data between utilization and team success."""
    try:
        correlations_path = Path(__file__).parent.parent.parent / "data" / "usage_success_correlations.csv"
        
        if not correlations_path.exists():
            raise HTTPException(status_code=404, detail="Correlations file not found")
        
        df = pd.read_csv(correlations_path)
        
        # Filter to utilization-related correlations
        utilization_correlations = df[df['Comparison'].str.contains('overutilized|underutilized', case=False, na=False)]
        
        return utilization_correlations.to_dict(orient="records")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/utilization/teams")
def get_utilization_teams():
    """Get team-level utilization analysis with success metrics."""
    try:
        merged_path = Path(__file__).parent.parent.parent / "data" / "usage_success_merged.csv"
        
        if not merged_path.exists():
            raise HTTPException(status_code=404, detail="Merged data file not found")
        
        df = pd.read_csv(merged_path)
        
        # Select relevant columns
        cols = ['team', 'team_name', 'num_players', 'total_current_usage', 'usage_concentration',
                'top_2_usage', 'top_3_usage', 'weighted_team_bpm', 'bpm_improvement_potential',
                'overutilized_count', 'underutilized_count', 'wins', 'losses', 'adj_net',
                'off_adj_ppp', 'def_adj_ppp', 'wab', 'power']
        
        available_cols = [col for col in cols if col in df.columns]
        result_df = df[available_cols].copy()
        
        # Replace NaN with None for JSON compatibility
        result_df = result_df.replace({float('nan'): None})
        
        return result_df.to_dict(orient="records")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/utilization/summary")
def get_utilization_summary():
    """Get summary statistics for utilization analysis."""
    try:
        merged_path = Path(__file__).parent.parent.parent / "data" / "usage_success_merged.csv"
        
        if not merged_path.exists():
            raise HTTPException(status_code=404, detail="Merged data file not found")
        
        df = pd.read_csv(merged_path)
        
        # Calculate summary statistics
        summary = {
            "total_teams": len(df),
            "avg_usage_concentration": float(df['usage_concentration'].mean()),
            "avg_overutilized_count": float(df['overutilized_count'].mean()),
            "avg_underutilized_count": float(df['underutilized_count'].mean()),
            "avg_weighted_team_bpm": float(df['weighted_team_bpm'].mean()),
            "avg_adj_net": float(df['adj_net'].mean()) if 'adj_net' in df.columns else None,
            "avg_wins": float(df['wins'].mean()) if 'wins' in df.columns else None,
            "avg_bpm_improvement_potential": float(df['bpm_improvement_potential'].mean()),
        }
        
        # Calculate correlations
        correlations = {
            "overutilized_vs_adj_net": float(df['overutilized_count'].corr(df['adj_net'])) if 'adj_net' in df.columns else None,
            "underutilized_vs_adj_net": float(df['underutilized_count'].corr(df['adj_net'])) if 'adj_net' in df.columns else None,
            "overutilized_vs_wins": float(df['overutilized_count'].corr(df['wins'])) if 'wins' in df.columns else None,
            "underutilized_vs_wins": float(df['underutilized_count'].corr(df['wins'])) if 'wins' in df.columns else None,
        }
        
        return {
            "summary": summary,
            "correlations": correlations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/archetype/teams")
def get_archetype_teams():
    """Get team-level archetype composition data."""
    try:
        archetype_path = Path(__file__).parent.parent.parent / "data" / "archetype_team_analysis.csv"
        
        if not archetype_path.exists():
            raise HTTPException(status_code=404, detail="Archetype data file not found")
        
        df = pd.read_csv(archetype_path)
        
        # Select relevant columns
        cols = ['team', 'team_name', 'total_minutes', 'total_players', 'weighted_team_bpm',
                'wins', 'losses', 'adj_net', 'off_adj_ppp', 'def_adj_ppp']
        
        # Add archetype percentage columns
        archetype_cols = [f'pct_minutes_{arch}' for arch in ['PG', 'CG', 'WG', 's-PG', 'WF', 'S-PF', 'PF/C', 'C']]
        available_cols = [col for col in cols + archetype_cols if col in df.columns]
        result_df = df[available_cols].copy()
        
        # Replace NaN with None for JSON compatibility
        result_df = result_df.replace({float('nan'): None})
        
        return result_df.to_dict(orient="records")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/archetype/correlations")
def get_archetype_correlations():
    """Get archetype composition correlations with team success."""
    try:
        correlations_path = Path(__file__).parent.parent.parent / "data" / "archetype_success_correlations.csv"
        
        if not correlations_path.exists():
            raise HTTPException(status_code=404, detail="Correlations file not found")
        
        df = pd.read_csv(correlations_path)
        
        return df.to_dict(orient="records")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/archetype/summary")
def get_archetype_summary():
    """Get summary statistics for archetype analysis."""
    try:
        archetype_path = Path(__file__).parent.parent.parent / "data" / "archetype_team_analysis.csv"
        
        if not archetype_path.exists():
            raise HTTPException(status_code=404, detail="Archetype data file not found")
        
        df = pd.read_csv(archetype_path)
        
        # Calculate quartiles
        top_quartile = df[df['adj_net'] >= df['adj_net'].quantile(0.75)]
        bottom_quartile = df[df['adj_net'] <= df['adj_net'].quantile(0.25)]
        
        archetype_cols = [f'pct_minutes_{arch}' for arch in ['PG', 'CG', 'WG', 's-PG', 'WF', 'S-PF', 'PF/C', 'C']]
        
        # Calculate average composition for top and bottom quartiles
        top_composition = {}
        bottom_composition = {}
        differences = {}
        
        for col in archetype_cols:
            if col in df.columns:
                arch_name = col.replace('pct_minutes_', '')
                top_composition[arch_name] = float(top_quartile[col].mean())
                bottom_composition[arch_name] = float(bottom_quartile[col].mean())
                differences[arch_name] = float(top_composition[arch_name] - bottom_composition[arch_name])
        
        return {
            "total_teams": len(df),
            "top_quartile_count": len(top_quartile),
            "bottom_quartile_count": len(bottom_quartile),
            "top_composition": top_composition,
            "bottom_composition": bottom_composition,
            "differences": differences
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clusters/players")
def get_cluster_players():
    """Get player clustering data."""
    try:
        clusters_path = Path(__file__).parent.parent.parent / "data" / "player_clusters.csv"
        
        if not clusters_path.exists():
            raise HTTPException(status_code=404, detail="Clusters file not found")
        
        df = pd.read_csv(clusters_path)
        
        # Replace NaN with None for JSON compatibility
        df = df.replace({float('nan'): None})
        
        return df.to_dict(orient="records")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clusters/descriptions")
def get_cluster_descriptions():
    """Get cluster descriptions and statistics."""
    try:
        descriptions_path = Path(__file__).parent.parent.parent / "data" / "cluster_descriptions.json"
        
        if not descriptions_path.exists():
            raise HTTPException(status_code=404, detail="Cluster descriptions file not found")
        
        with open(descriptions_path, 'r') as f:
            data = json.load(f)
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clusters/teams")
def get_cluster_teams():
    """Get team-level cluster composition data."""
    try:
        clusters_path = Path(__file__).parent.parent.parent / "data" / "player_clusters.csv"
        
        if not clusters_path.exists():
            raise HTTPException(status_code=404, detail="Clusters file not found")
        
        df = pd.read_csv(clusters_path)
        
        # Group by team and calculate cluster composition
        team_clusters = df.groupby('Team').apply(
            lambda x: {
                'team': x['Team'].iloc[0],
                'total_players': len(x),
                'clusters': x['cluster'].value_counts().to_dict(),
                'cluster_pcts': (x['cluster'].value_counts() / len(x)).to_dict()
            }
        ).reset_index(drop=True)
        
        # Convert to list of dicts
        team_data = []
        for _, row in team_clusters.items():
            team_data.append(row)
        
        return team_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/team-clusters")
def get_team_clusters():
    """Get team clustering data."""
    try:
        clusters_path = Path(__file__).parent.parent.parent / "data" / "team_clusters.csv"
        
        if not clusters_path.exists():
            raise HTTPException(status_code=404, detail="Team clusters file not found")
        
        df = pd.read_csv(clusters_path)
        
        # Replace NaN with None for JSON compatibility
        df = df.replace({float('nan'): None})
        
        return df.to_dict(orient="records")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/team-clusters/descriptions")
def get_team_cluster_descriptions():
    """Get team cluster descriptions and statistics."""
    try:
        descriptions_path = Path(__file__).parent.parent.parent / "data" / "team_cluster_descriptions.json"
        
        if not descriptions_path.exists():
            raise HTTPException(status_code=404, detail="Team cluster descriptions file not found")
        
        with open(descriptions_path, 'r') as f:
            descriptions = json.load(f)
        
        return descriptions
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

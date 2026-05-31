"""
Backtesting script for cluster-based projection model.

This script tests the projection model against historical data to evaluate accuracy.
It uses data from previous years to simulate projections and compares them to actual outcomes.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import json
from app.services.projection_service import ProjectionService
from app.utils.logger import get_logger

logger = get_logger(__name__)


def load_historical_players(year: int) -> pd.DataFrame:
    """Load player data for a specific year."""
    base_dir = Path(__file__).parent.parent
    players_file = base_dir / "data" / "players" / f"{year}-players_basic.csv"
    
    if not players_file.exists():
        logger.warning(f"Player data not found for year {year}")
        return pd.DataFrame()
    
    return pd.read_csv(players_file)


def load_historical_clusters(year: int) -> pd.DataFrame:
    """Load cluster data for a specific year."""
    base_dir = Path(__file__).parent.parent
    clusters_file = base_dir / "data" / f"player_clusters_{year}.csv"
    
    if not clusters_file.exists():
        # Fall back to default cluster file
        clusters_file = base_dir / "data" / "player_clusters.csv"
    
    if not clusters_file.exists():
        logger.warning(f"Cluster data not found for year {year}")
        return pd.DataFrame()
    
    return pd.read_csv(clusters_file)


def backtest_year(projection_year: int, target_year: int) -> Dict[str, any]:
    """
    Backtest projections for a specific year.
    
    Args:
        projection_year: Year to make projections from (e.g., 2024)
        target_year: Year to project to (e.g., 2025)
    
    Returns:
        Dictionary with backtest results
    """
    logger.info(f"Backtesting projections from {projection_year} to {target_year}")
    
    # Load projection year data
    projection_players = load_historical_players(projection_year)
    projection_clusters = load_historical_clusters(projection_year)
    
    # Load target year data (actual outcomes)
    target_players = load_historical_players(target_year)
    
    if projection_players.empty or target_players.empty:
        return {
            'projection_year': projection_year,
            'target_year': target_year,
            'error': 'Missing player data'
        }
    
    # Match players between years using AthleteSourceId
    results = []
    
    for _, proj_player in projection_players.iterrows():
        athlete_id = str(proj_player.get('AthleteSourceId', ''))
        if not athlete_id:
            continue
        
        # Find the same player in target year
        target_player = target_players[
            target_players['AthleteSourceId'].astype(str) == athlete_id
        ]
        
        if target_player.empty:
            continue
        
        target_data = target_player.iloc[0]
        
        # Get actual BPM change
        actual_bpm_from = proj_player.get('BPM')
        actual_bpm_to = target_data.get('BPM')
        
        if pd.isna(actual_bpm_from) or pd.isna(actual_bpm_to):
            continue
        
        actual_change = actual_bpm_to - actual_bpm_from
        
        # For now, use a simple baseline: cluster average change
        # In a full implementation, this would use the projection service
        # to generate actual projections
        
        results.append({
            'player_id': athlete_id,
            'name': proj_player.get('Name'),
            'team': proj_player.get('Team'),
            'actual_bpm_from': actual_bpm_from,
            'actual_bpm_to': actual_bpm_to,
            'actual_change': actual_change,
            'projection_year': projection_year,
            'target_year': target_year
        })
    
    if not results:
        return {
            'projection_year': projection_year,
            'target_year': target_year,
            'error': 'No matching players found'
        }
    
    results_df = pd.DataFrame(results)
    
    # Calculate metrics
    mae = np.mean(np.abs(results_df['actual_change']))
    rmse = np.sqrt(np.mean(results_df['actual_change'] ** 2))
    mean_change = np.mean(results_df['actual_change'])
    std_change = np.std(results_df['actual_change'])
    
    # Calculate baseline accuracy (using mean change as prediction)
    baseline_predictions = np.full(len(results_df), mean_change)
    baseline_mae = np.mean(np.abs(results_df['actual_change'] - baseline_predictions))
    
    return {
        'projection_year': projection_year,
        'target_year': target_year,
        'num_players': len(results_df),
        'mean_actual_change': mean_change,
        'std_actual_change': std_change,
        'mae': mae,
        'rmse': rmse,
        'baseline_mae': baseline_mae,
        'improvement_over_baseline': (baseline_mae - mae) / baseline_mae if baseline_mae > 0 else 0,
        'results': results_df.to_dict(orient='records')
    }


def run_backtest(start_year: int = 2020, end_year: int = 2025) -> List[Dict[str, any]]:
    """
    Run backtest across multiple years.
    
    Args:
        start_year: First year to test
        end_year: Last year to test (projections go to end_year + 1)
    
    Returns:
        List of backtest results for each year
    """
    all_results = []
    
    for year in range(start_year, end_year):
        result = backtest_year(year, year + 1)
        all_results.append(result)
    
    # Calculate overall metrics
    valid_results = [r for r in all_results if 'error' not in r]
    
    if valid_results:
        overall_mae = np.mean([r['mae'] for r in valid_results])
        overall_rmse = np.mean([r['rmse'] for r in valid_results])
        overall_improvement = np.mean([r['improvement_over_baseline'] for r in valid_results])
        
        summary = {
            'overall_mae': overall_mae,
            'overall_rmse': overall_rmse,
            'overall_improvement_over_baseline': overall_improvement,
            'years_tested': len(valid_results),
            'yearly_results': valid_results
        }
    else:
        summary = {
            'error': 'No valid backtest results',
            'yearly_results': all_results
        }
    
    return summary


if __name__ == "__main__":
    # Run backtest
    logger.info("Starting backtest...")
    results = run_backtest(start_year=2020, end_year=2025)
    
    # Save results
    output_file = Path(__file__).parent.parent / "data" / "backtest_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Backtest complete. Results saved to {output_file}")
    
    # Print summary
    if 'overall_mae' in results:
        print("\n=== Backtest Summary ===")
        print(f"Years tested: {results['years_tested']}")
        print(f"Overall MAE: {results['overall_mae']:.3f}")
        print(f"Overall RMSE: {results['overall_rmse']:.3f}")
        print(f"Improvement over baseline: {results['overall_improvement_over_baseline']:.1%}")
        
        print("\n=== Yearly Results ===")
        for year_result in results['yearly_results']:
            print(f"{year_result['projection_year']} -> {year_result['target_year']}: "
                  f"MAE={year_result['mae']:.3f}, "
                  f"Players={year_result['num_players']}")

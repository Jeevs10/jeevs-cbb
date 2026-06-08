"""
Script to pre-calculate 2027 BPM projections for all 2026 players.
This generates a CSV file that can be used by the leaderboard API.
"""

import pandas as pd
from pathlib import Path
import sys
import logging
from multiprocessing import Pool, cpu_count
from functools import partial

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.projection_service import ProjectionService
from app.utils.logger import get_logger

logger = get_logger(__name__)


def normalize_ncaa_id(ncaa_id):
    """Normalize NCAA ID to string format."""
    if pd.isna(ncaa_id):
        return None
    ncaa_id_str = str(ncaa_id).strip()
    if ncaa_id_str == '' or ncaa_id_str == 'nan':
        return None
    return ncaa_id_str


def process_player(player_data, current_year=2026):
    """Process a single player's projection. This runs in a separate process."""
    player_key, player_name, team, idx = player_data
    
    # Initialize service in this process
    service = ProjectionService()
    service._ensure_data_loaded()
    
    # Normalize NCAA ID
    ncaa_id = normalize_ncaa_id(player_key)
    
    if not ncaa_id:
        return {'status': 'skipped', 'reason': 'Invalid NCAA ID', 'player_name': player_name}
    
    try:
        # Check if player exists in cluster data first
        cluster_info = service.get_player_cluster(ncaa_id)
        if cluster_info is None:
            return {'status': 'skipped', 'reason': 'Not found in cluster data', 'player_name': player_name, 'ncaa_id': ncaa_id}
        
        # Calculate projection
        projection = service.calculate_projection(
            ncaa_id=ncaa_id,
            current_year=current_year,
            years_ahead=1,
            min_samples=5
        )
        
        if 'error' in projection:
            return {'status': 'skipped', 'reason': projection['error'], 'player_name': player_name, 'ncaa_id': ncaa_id}
        
        if not projection.get('projections'):
            return {'status': 'skipped', 'reason': 'No projections generated', 'player_name': player_name, 'ncaa_id': ncaa_id}
        
        # Extract projection data
        proj_data = projection['projections'][0]
        
        return {
            'status': 'success',
            'result': {
                'player_key': ncaa_id,
                'player_name': player_name,
                'team': team,
                'current_bpm': projection.get('current_bpm', 0),
                'bpm_change_predicted': proj_data.get('bpm_change', 0),
                'projected_bpm': proj_data.get('projected_bpm', 0),
                'projected_bpm_lower_90': proj_data.get('confidence_interval', [0, 0])[0],
                'projected_bpm_upper_90': proj_data.get('confidence_interval', [0, 0])[1],
                'cluster_id': projection.get('cluster_id'),
                'historical_samples': projection.get('historical_samples', 0)
            }
        }
        
    except Exception as e:
        return {'status': 'error', 'reason': str(e), 'player_name': player_name, 'ncaa_id': ncaa_id}


def generate_projection_leaderboard():
    """Generate a CSV file with 2027 projections for all 2026 players."""
    
    logger.info("Starting projection leaderboard generation...")
    
    # Initialize projection service to get player data
    service = ProjectionService()
    service._ensure_data_loaded()
    
    # Check if players data is loaded
    if service._players_df is None:
        logger.error("Players data not loaded")
        return
    
    logger.info(f"Loaded {len(service._players_df)} players")
    
    # Get current year
    current_year = 2026
    
    # Prepare player data for parallel processing
    player_data_list = []
    for idx, player_row in service._players_df.iterrows():
        player_key = player_row.get('AthleteSourceId', '')
        player_name = player_row.get('Name', 'Unknown')
        team = player_row.get('Team', '')
        player_data_list.append((player_key, player_name, team, idx))
    
    total_players = len(player_data_list)
    logger.info(f"Processing {total_players} players using multiprocessing...")
    
    # Use multiprocessing to process players in parallel
    num_processes = min(cpu_count(), 8)  # Use up to 8 processes
    logger.info(f"Using {num_processes} processes")
    
    results = []
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    try:
        with Pool(processes=num_processes) as pool:
            # Process players in parallel
            for i, result in enumerate(pool.imap_unordered(
                partial(process_player, current_year=current_year),
                player_data_list,
                chunksize=max(1, total_players // (num_processes * 10))
            )):
                if result['status'] == 'success':
                    results.append(result['result'])
                    processed_count += 1
                elif result['status'] == 'skipped':
                    skipped_count += 1
                    if 'ncaa_id' in result:
                        logger.warning(f"Skipping player {result['player_name']} ({result['ncaa_id']}): {result['reason']}")
                    else:
                        logger.warning(f"Skipping player {result['player_name']}: {result['reason']}")
                elif result['status'] == 'error':
                    error_count += 1
                    logger.error(f"Error processing player {result['player_name']} ({result.get('ncaa_id', 'N/A')}): {result['reason']}")
                
                # Log progress every 100 players
                if (processed_count + skipped_count + error_count) % 100 == 0:
                    logger.info(f"Processed {processed_count + skipped_count + error_count}/{total_players} players...")
    
    except Exception as e:
        logger.error(f"Error in multiprocessing: {e}")
        raise
    
    logger.info(f"Finished processing: {processed_count} successful, {skipped_count} skipped, {error_count} errors")
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    if len(df) == 0:
        logger.error("No projections generated")
        return
    
    # Save to CSV
    output_path = Path(__file__).parent / "data" / "projection_leaderboard_2027.csv"
    df.to_csv(output_path, index=False)
    
    logger.info(f"Saved {len(df)} projections to {output_path}")
    logger.info(f"Summary statistics:")
    logger.info(f"  - Average projected BPM: {df['projected_bpm'].mean():.2f}")
    logger.info(f"  - Average BPM change: {df['bpm_change_predicted'].mean():.2f}")
    logger.info(f"  - Max projected BPM: {df['projected_bpm'].max():.2f}")
    logger.info(f"  - Min projected BPM: {df['projected_bpm'].min():.2f}")


if __name__ == "__main__":
    generate_projection_leaderboard()

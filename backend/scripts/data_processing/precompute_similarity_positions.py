"""
Precompute 3D positions for similarity map using UMAP on similarity vectors.
This runs once on the backend and saves results to CSV for fast frontend loading.

Algorithm: UMAP (Uniform Manifold Approximation and Projection)
   - Pros: Fast O(n log n), preserves both local and global structure, deterministic
   - Cons: More parameters to tune
   - Best for: General-purpose dimensionality reduction, similarity visualization
"""
import numpy as np
import pandas as pd
from app.cache.player_vectors import PLAYER_VECTORS
from app.core.data_loader import PLAYER_LOOKUP, load_torvik_players
import json
import logging
import sys
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)

def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors"""
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot / (norm_a * norm_b)

def compute_similarity(v1, v2, style_weight=0.7):
    """Compute combined similarity using style and impact vectors"""
    style_sim = cosine_similarity(v1['style'], v2['style'])
    impact_sim = cosine_similarity(v1['impact'], v2['impact'])
    return style_weight * style_sim + (1 - style_weight) * impact_sim

def umap_layout(vectors_dict, n_neighbors=15, min_dist=0.1, metric='cosine'):
    """
    Run UMAP dimensionality reduction on similarity vectors.
    
    Args:
        vectors_dict: Dict of key -> {style, impact} vectors (key can be "ncaa_id" or "ncaa_id_year")
        n_neighbors: Number of neighbors to consider (higher = more global structure)
        min_dist: Minimum distance between points (lower = tighter clusters)
        metric: Distance metric to use ('cosine' recommended for similarity)
    
    Returns:
        Dict of key -> (x, y, z) positions
    """
    try:
        import umap
    except ImportError:
        logger.error("UMAP not installed. Install with: /Users/sanjiv/opt/anaconda3/bin/python -m pip install umap-learn")
        raise
    
    keys = list(vectors_dict.keys())
    n = len(keys)
    
    logger.info(f"Starting UMAP with {n} nodes")
    logger.info(f"Parameters: n_neighbors={n_neighbors}, min_dist={min_dist}, metric={metric}")
    
    # Combine style and impact vectors into single feature matrix
    feature_matrix = []
    for key in keys:
        vec = vectors_dict[key]
        combined = np.concatenate([vec['style'], vec['impact']])
        feature_matrix.append(combined)
    
    feature_matrix = np.array(feature_matrix)
    logger.info(f"Feature matrix shape: {feature_matrix.shape}")
    
    # Run UMAP
    logger.info("Running UMAP...")
    reducer = umap.UMAP(
        n_components=3,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        metric=metric,
        random_state=42,  # For reproducibility
        spread=10.0,  # Increase spread further for better distribution
    )
    
    embedding = reducer.fit_transform(feature_matrix)
    logger.info("UMAP complete")
    
    # Scale all axes for better separation
    embedding[:, 0] = embedding[:, 0] * 2.0  # Scale X
    embedding[:, 1] = embedding[:, 1] * 2.0  # Scale Y
    embedding[:, 2] = embedding[:, 2] * 3.0  # Scale Z even more
    logger.info("Scaled all axes for better node separation")
    
    # Map back to keys
    positions = {key: embedding[i] for i, key in enumerate(keys)}
    
    return positions

def main(sample_size=None, year=None):
    """
    Main function to precompute similarity positions.
    
    Args:
        sample_size: If provided, only process this many players (for testing)
        year: If provided, only process this specific year (e.g., '2026')
    """
    logger.info("="*60)
    logger.info("Starting similarity position precomputation")
    logger.info(f"Sample size: {sample_size if sample_size else 'All players'}")
    logger.info(f"Year filter: {year if year else 'All years'}")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)
    
    # Build player vectors cache if needed
    from app.cache.player_vectors import build_cache
    logger.info("Building player vectors cache...")
    build_cache(force_rebuild=True)
    
    # Load Torvik data for player names and teams
    logger.info("Loading Torvik data for player names...")
    torvik_df = load_torvik_players()
    logger.info(f"Loaded {len(torvik_df)} Torvik entries")
    
    # Create a dictionary for fast lookup: {ncaa_id_year: {player_name, team}}
    torvik_lookup = {}
    if not torvik_df.empty:
        for _, row in torvik_df.iterrows():
            ncaa_id = str(row.get('AthleteSourceId', '')).replace('.0', '')
            yr = str(int(row.get('year', 0)))
            key = f"{ncaa_id}_{yr}"
            torvik_lookup[key] = {
                'player_name': row.get('player_name'),
                'team': row.get('team')
            }
    logger.info(f"Created Torvik lookup with {len(torvik_lookup)} entries")
    logger.info(f"Sample Torvik keys: {list(torvik_lookup.keys())[:5]}")
    
    logger.info("Loading player vectors...")
    
    # Debug: Check what's in PLAYER_VECTORS
    sample_keys = list(PLAYER_VECTORS.keys())[:5]
    logger.info(f"Sample PLAYER_VECTORS keys: {sample_keys}")
    
    # Count vectors by year
    year_counts = {}
    for ncaa_id, year_map in PLAYER_VECTORS.items():
        for yr in year_map.keys():
            year_counts[yr] = year_counts.get(yr, 0) + 1
    logger.info(f"Year distribution in PLAYER_VECTORS: {year_counts}")
    
    sample_years = []
    for ncaa_id, year_map in list(PLAYER_VECTORS.items())[:3]:
        sample_years.extend(list(year_map.keys()))
    logger.info(f"Sample years from vectors: {sample_years}")
    
    # Get vectors for each player-year combination
    vectors_dict = {}
    player_years = []  # Track (ncaa_id, year) pairs
    
    logger.info(f"Year filter parameter: {year}")
    
    for ncaa_id, year_map in PLAYER_VECTORS.items():
        # Convert ncaa_id to string without .0 for consistent key format
        ncaa_id_str = str(ncaa_id).replace('.0', '')
        for yr, vec in year_map.items():
            if year and str(yr) != str(year):
                continue
            
            # Use composite key: "ncaa_id_year" to handle year-by-year
            key = f"{ncaa_id_str}_{yr}"
            vectors_dict[key] = vec
            player_years.append((ncaa_id_str, yr))
    
    # Apply sample size if specified
    if sample_size and len(vectors_dict) > sample_size:
        logger.info(f"Limiting to sample size of {sample_size} (from {len(vectors_dict)} total)")
        keys = list(vectors_dict.keys())[:sample_size]
        vectors_dict = {k: vectors_dict[k] for k in keys}
        player_years = [(k.split('_')[0], k.split('_')[1]) for k in keys]
    
    logger.info(f"Loaded {len(vectors_dict)} player-year vectors")
    
    # Run UMAP
    positions = umap_layout(
        vectors_dict,
        n_neighbors=15,
        min_dist=0.1,
        metric='cosine'
    )
    
    # Create output dataframe
    output_data = []
    for key, pos in positions.items():
        ncaa_id, yr = key.split('_')
        # Try to get player name and team from Torvik lookup
        torvik_key = f"{ncaa_id}_{yr}"
        torvik_entry = torvik_lookup.get(torvik_key, {})
        player_name = torvik_entry.get('player_name') if torvik_entry else None
        team = torvik_entry.get('team') if torvik_entry else None
        
        # Fallback to PLAYER_LOOKUP if Torvik doesn't have it
        if not player_name or not team:
            meta = PLAYER_LOOKUP.get(ncaa_id, {})
            player_name = player_name or meta.get('player_name')
            team = team or meta.get('team')
        
        output_data.append({
            'ncaa_id': ncaa_id,
            'year': yr,
            'x': pos[0],
            'y': pos[1],
            'z': pos[2],
            'player_name': player_name,
            'team': team,
        })
    
    df = pd.DataFrame(output_data)
    
    # Handle empty dataframe
    if len(df) == 0:
        logger.warning("No player-year vectors found. Output will be empty.")
        # Create empty CSV with correct columns
        df = pd.DataFrame(columns=['ncaa_id', 'year', 'x', 'y', 'z', 'player_name', 'team'])
    
    # Save to CSV
    output_path = '/Users/sanjiv/jeevs-cbb/backend/data/similarity_positions.csv'
    df.to_csv(output_path, index=False)
    logger.info(f"="*60)
    logger.info(f"Saved positions to {output_path}")
    logger.info(f"Total player-years: {len(df)}")
    
    if len(df) > 0:
        logger.info(f"Unique players: {df['ncaa_id'].nunique()}")
        logger.info(f"Years covered: {sorted(df['year'].unique())}")
        logger.info(f"Position ranges:")
        logger.info(f"  X: [{df['x'].min():.2f}, {df['x'].max():.2f}]")
        logger.info(f"  Y: [{df['y'].min():.2f}, {df['y'].max():.2f}]")
        logger.info(f"  Z: [{df['z'].min():.2f}, {df['z'].max():.2f}]")
    
    logger.info(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Precompute similarity positions')
    parser.add_argument('--sample', type=int, help='Sample size for testing (e.g., 100)')
    parser.add_argument('--year', type=str, help='Filter to specific year (e.g., 2026)')
    
    args = parser.parse_args()
    
    main(sample_size=args.sample, year=args.year)

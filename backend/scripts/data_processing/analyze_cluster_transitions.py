"""Analyze cluster transitions and development patterns from historical data."""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from collections import defaultdict
import time

DATA_DIR = Path(__file__).parent / "data"


def load_cluster_data(year: int) -> pd.DataFrame:
    """Load cluster data for a specific year."""
    cluster_file = DATA_DIR / f"player_clusters_{year}.csv"
    if not cluster_file.exists():
        print(f"WARNING: Cluster file not found for year {year}: {cluster_file}")
        return None
    print(f"Loading cluster data for year {year}...")
    df = pd.read_csv(cluster_file)
    print(f"Loaded {len(df)} cluster records for year {year}")
    return df


def load_player_data(year: int) -> pd.DataFrame:
    """Load player data for a specific year."""
    player_file = DATA_DIR / "players" / f"{year}-players_basic.csv"
    if not player_file.exists():
        print(f"WARNING: Player file not found for year {year}: {player_file}")
        return None
    print(f"Loading player data for year {year}...")
    df = pd.read_csv(player_file)
    print(f"Loaded {len(df)} player records for year {year}")
    return df


def build_transition_matrix(start_year: int, end_year: int = 2025) -> dict:
    """
    Build cluster transition matrix from historical data.

    Args:
        start_year: First year to analyze
        end_year: Last year to analyze

    Returns:
        Dictionary with transition matrix and statistics
    """
    print(f"Building transition matrix from {start_year} to {end_year}")
    start_time = time.time()

    transitions = defaultdict(lambda: defaultdict(int))
    transition_counts = defaultdict(int)
    player_transitions = []

    for year in range(start_year, end_year):
        year_start = time.time()
        print(f"Analyzing transitions from {year} to {year + 1}...")

        # Load cluster data for both years
        clusters_from = load_cluster_data(year)
        clusters_to = load_cluster_data(year + 1)

        if clusters_from is None or clusters_to is None:
            print(f"WARNING: Missing cluster data for {year} or {year + 1}")
            continue

        # Load player data to get BPM changes
        players_from = load_player_data(year)
        players_to = load_player_data(year + 1)

        print(f"Building cluster mappings for {year}...")
        # Create mapping from AthleteSourceId to cluster
        cluster_map_from = {}
        for _, row in clusters_from.iterrows():
            athlete_id = str(row.get('AthleteSourceId', ''))
            if athlete_id:
                cluster_map_from[athlete_id] = row['cluster']

        cluster_map_to = {}
        for _, row in clusters_to.iterrows():
            athlete_id = str(row.get('AthleteSourceId', ''))
            if athlete_id:
                cluster_map_to[athlete_id] = row['cluster']

        print(f"Finding common players between {year} and {year + 1}...")
        # Find players who appear in both years
        common_players = set(cluster_map_from.keys()) & set(cluster_map_to.keys())
        print(f"Found {len(common_players)} players in both years")

        print(f"Processing {len(common_players)} player transitions...")
        # Track transitions
        processed_count = 0
        for player_id in common_players:
            cluster_from = cluster_map_from[player_id]
            cluster_to = cluster_map_to[player_id]

            transitions[cluster_from][cluster_to] += 1
            transition_counts[cluster_from] += 1

            # Get BPM change if available
            bpm_from = None
            bpm_to = None
            bpm_change = None

            if players_from is not None:
                player_from = players_from[players_from['AthleteSourceId'].astype(str) == player_id]
                if not player_from.empty:
                    bpm_from = player_from.iloc[0].get('BPM')

            if players_to is not None:
                player_to = players_to[players_to['AthleteSourceId'].astype(str) == player_id]
                if not player_to.empty:
                    bpm_to = player_to.iloc[0].get('BPM')

            if bpm_from is not None and bpm_to is not None:
                bpm_change = bpm_to - bpm_from

            player_transitions.append({
                'year_from': year,
                'year_to': year + 1,
                'player_id': player_id,
                'cluster_from': cluster_from,
                'cluster_to': cluster_to,
                'cluster_changed': cluster_from != cluster_to,
                'bpm_from': bpm_from,
                'bpm_to': bpm_to,
                'bpm_change': bpm_change
            })

            processed_count += 1
            if processed_count % 1000 == 0:
                print(f"  Processed {processed_count}/{len(common_players)} transitions...")

        year_elapsed = time.time() - year_start
        print(f"Completed {year} -> {year + 1} in {year_elapsed:.2f}s")

    print("Building transition probability matrix...")
    # Build transition probability matrix
    transition_matrix = {}
    for cluster_from in transitions:
        total = transition_counts[cluster_from]
        transition_matrix[cluster_from] = {
            cluster_to: count / total for cluster_to, count in transitions[cluster_from].items()
        }

    elapsed = time.time() - start_time
    print(f"Transition matrix built in {elapsed:.2f}s")

    return {
        'transition_matrix': transition_matrix,
        'transition_counts': dict(transitions),
        'player_transitions': player_transitions
    }


def analyze_cluster_development(start_year: int, end_year: int = 2025) -> dict:
    """
    Analyze how players develop within clusters year-over-year.

    Args:
        start_year: First year to analyze
        end_year: Last year to analyze

    Returns:
        Dictionary with cluster development patterns
    """
    print(f"Analyzing cluster development from {start_year} to {end_year}")
    start_time = time.time()

    cluster_development = defaultdict(lambda: defaultdict(list))

    for year in range(start_year, end_year):
        year_start = time.time()
        print(f"Analyzing development from {year} to {year + 1}...")

        # Load cluster and player data
        clusters_from = load_cluster_data(year)
        clusters_to = load_cluster_data(year + 1)
        players_from = load_player_data(year)
        players_to = load_player_data(year + 1)

        if clusters_from is None or clusters_to is None:
            print(f"WARNING: Missing cluster data for {year} or {year + 1}")
            continue

        print(f"Building cluster mappings for development analysis...")
        # Create mappings
        cluster_map_from = {}
        for _, row in clusters_from.iterrows():
            athlete_id = str(row.get('AthleteSourceId', ''))
            if athlete_id:
                cluster_map_from[athlete_id] = row['cluster']

        cluster_map_to = {}
        for _, row in clusters_to.iterrows():
            athlete_id = str(row.get('AthleteSourceId', ''))
            if athlete_id:
                cluster_map_to[athlete_id] = row['cluster']

        # Find players in same cluster both years
        common_players = set(cluster_map_from.keys()) & set(cluster_map_to.keys())
        print(f"Found {len(common_players)} players in both years")

        # Find players who stayed in same cluster
        same_cluster_players = []
        for player_id in common_players:
            if cluster_map_from[player_id] == cluster_map_to[player_id]:
                same_cluster_players.append(player_id)

        print(f"Found {len(same_cluster_players)} players who stayed in same cluster")

        print(f"Processing development patterns for {len(same_cluster_players)} players...")
        processed_count = 0
        for player_id in same_cluster_players:
            cluster_from = cluster_map_from[player_id]

            # Get stat changes (PPG, RPG, APG since BPM may not be available)
            stats_from = {}
            stats_to = {}

            if players_from is not None:
                player_from = players_from[players_from['AthleteSourceId'].astype(str) == player_id]
                if not player_from.empty:
                    stats_from = {
                        'PPG': player_from.iloc[0].get('PPG'),
                        'RPG': player_from.iloc[0].get('RPG'),
                        'APG': player_from.iloc[0].get('APG'),
                        'Usage': player_from.iloc[0].get('Usage'),
                        'BPM': player_from.iloc[0].get('BPM')
                    }

            if players_to is not None:
                player_to = players_to[players_to['AthleteSourceId'].astype(str) == player_id]
                if not player_to.empty:
                    stats_to = {
                        'PPG': player_to.iloc[0].get('PPG'),
                        'RPG': player_to.iloc[0].get('RPG'),
                        'APG': player_to.iloc[0].get('APG'),
                        'Usage': player_to.iloc[0].get('Usage'),
                        'BPM': player_to.iloc[0].get('BPM')
                    }

            # Calculate changes for available stats
            for stat in ['PPG', 'RPG', 'APG', 'Usage', 'BPM']:
                if stats_from.get(stat) is not None and stats_to.get(stat) is not None:
                    change = stats_to[stat] - stats_from[stat]
                    cluster_development[cluster_from][f'{stat}_changes'].append(change)

            processed_count += 1
            if processed_count % 1000 == 0:
                print(f"  Processed {processed_count}/{len(same_cluster_players)} players...")

        year_elapsed = time.time() - year_start
        print(f"Completed {year} -> {year + 1} development analysis in {year_elapsed:.2f}s")

    print("Calculating cluster development statistics...")
    # Calculate statistics for each cluster
    cluster_stats = {}
    for cluster_id in cluster_development:
        stats = {}
        for stat in ['PPG', 'RPG', 'APG', 'Usage', 'BPM']:
            changes = cluster_development[cluster_id].get(f'{stat}_changes', [])
            if changes:
                stats[stat] = {
                    'mean_change': float(np.mean(changes)),
                    'std_change': float(np.std(changes)),
                    'median_change': float(np.median(changes)),
                    'p25_change': float(np.percentile(changes, 25)),
                    'p75_change': float(np.percentile(changes, 75)),
                    'count': len(changes)
                }
        if stats:
            cluster_stats[cluster_id] = stats

    elapsed = time.time() - start_time
    print(f"Cluster development analysis completed in {elapsed:.2f}s")

    return {
        'cluster_development': dict(cluster_development),
        'cluster_stats': cluster_stats
    }


def save_analysis_results(transitions: dict, development: dict):
    """Save analysis results to files."""
    # Save transition matrix
    with open(DATA_DIR / "cluster_transition_matrix.json", 'w') as f:
        json.dump(transitions['transition_matrix'], f, indent=2)
    print(f"Saved transition matrix to {DATA_DIR / 'cluster_transition_matrix.json'}")
    
    # Save cluster development stats
    with open(DATA_DIR / "cluster_development_stats.json", 'w') as f:
        json.dump(development['cluster_stats'], f, indent=2)
    print(f"Saved cluster development stats to {DATA_DIR / 'cluster_development_stats.json'}")
    
    # Save player transitions for detailed analysis
    transitions_df = pd.DataFrame(transitions['player_transitions'])
    transitions_df.to_csv(DATA_DIR / "player_transitions.csv", index=False)
    print(f"Saved player transitions to {DATA_DIR / 'player_transitions.csv'}")
    
    # Print summary
    print("\n=== Transition Matrix Summary ===")
    for cluster_from in sorted(transitions['transition_matrix'].keys()):
        print(f"\nCluster {cluster_from} transitions:")
        for cluster_to, prob in sorted(transitions['transition_matrix'][cluster_from].items(), 
                                       key=lambda x: x[1], reverse=True):
            print(f"  -> Cluster {cluster_to}: {prob:.2%}")
    
    print("\n=== Cluster Development Summary ===")
    for cluster_id in sorted(development['cluster_stats'].keys()):
        stats = development['cluster_stats'][cluster_id]
        print(f"\nCluster {cluster_id}:")
        for stat_name, stat_data in stats.items():
            print(f"  {stat_name} (n={stat_data['count']}):")
            print(f"    Mean change: {stat_data['mean_change']:.3f}")
            print(f"    Std change: {stat_data['std_change']:.3f}")
            print(f"    Median change: {stat_data['median_change']:.3f}")


if __name__ == "__main__":
    import sys
    print("=== Starting Cluster Analysis ===", file=sys.stderr, flush=True)
    print("=== Analyzing Cluster Transitions and Development ===\n", flush=True)

    # Build transition matrix
    transitions = build_transition_matrix(start_year=2019, end_year=2025)

    # Analyze cluster development
    development = analyze_cluster_development(start_year=2019, end_year=2025)

    # Save results
    save_analysis_results(transitions, development)

    print("\n=== Analysis Complete ===", flush=True)

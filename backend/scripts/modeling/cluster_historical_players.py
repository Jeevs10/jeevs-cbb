"""Cluster historical players based on basic player data (2019-2025)."""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import json

DATA_DIR = Path(__file__).parent / "data"

def cluster_players_basic(year: int, n_clusters: int = 18):
    """
    Cluster players for a specific year using basic player data.
    
    Args:
        year: Year to cluster (e.g., 2019, 2020, etc.)
        n_clusters: Number of clusters to use (default 18 to match 2026)
    """
    print(f"Clustering players for {year} using basic data...")
    
    # Load player data
    players_file = DATA_DIR / "players" / f"{year}-players_basic.csv"
    
    if not players_file.exists():
        print(f"Player data not found for year {year}: {players_file}")
        return None, None
    
    df = pd.read_csv(players_file)
    print(f"Loaded {len(df)} players for {year}")
    
    # Select clustering features available in basic data
    clustering_features = [
        'PPG',  # Points per game
        'APG',  # Assists per game
        'RPG',  # Rebounds per game
        'Usage',  # Usage rate
        'EffectiveFieldGoalPct',  # Shooting efficiency
        'TrueShootingPct',  # True shooting percentage
        'OffensiveRating',  # Offensive rating
        'DefensiveRating',  # Defensive rating
        'MPG',  # Minutes per game
    ]
    
    # Filter to available features
    available_features = [f for f in clustering_features if f in df.columns]
    print(f"Using {len(available_features)} features for clustering")
    
    # Filter to players with sufficient data
    df_cluster = df[available_features].copy()
    df_cluster = df_cluster.dropna()
    print(f"Filtered to {len(df_cluster)} players with complete data")
    
    if len(df_cluster) < n_clusters:
        print(f"Not enough players ({len(df_cluster)}) for {n_clusters} clusters")
        return None, None
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_cluster[available_features])
    
    # Use the same number of clusters as 2026 for consistency
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    # Add cluster labels to original data
    df_cluster['cluster'] = clusters
    df_cluster['Name'] = df.loc[df_cluster.index, 'Name']
    df_cluster['Team'] = df.loc[df_cluster.index, 'Team']
    df_cluster['AthleteSourceId'] = df.loc[df_cluster.index, 'AthleteSourceId']
    df_cluster['AthleteId'] = df.loc[df_cluster.index, 'AthleteId']
    # Only add fields that exist in the original data
    if 'BPM' in df.columns:
        df_cluster['BPM'] = df.loc[df_cluster.index, 'BPM']
    if 'Height' in df.columns:
        df_cluster['Height'] = df.loc[df_cluster.index, 'Height']
    if 'Usage' in df.columns:
        df_cluster['Usage'] = df.loc[df_cluster.index, 'Usage']
    
    # PCA for visualization
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    df_cluster['pca_1'] = X_pca[:, 0]
    df_cluster['pca_2'] = X_pca[:, 1]
    
    # Save cluster data
    base_cols = ['Name', 'Team', 'cluster', 'pca_1', 'pca_2', 'AthleteSourceId', 'AthleteId']
    optional_cols = ['BPM', 'Height', 'Usage']
    output_cols = base_cols + [col for col in optional_cols if col in df_cluster.columns] + available_features
    df_cluster[output_cols].to_csv(DATA_DIR / f"player_clusters_{year}.csv", index=False)
    print(f"Saved cluster data to {DATA_DIR / f'player_clusters_{year}.csv'}")
    
    # Save cluster centers
    cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
    cluster_centers_df = pd.DataFrame(cluster_centers, columns=available_features)
    cluster_centers_df.to_csv(DATA_DIR / f"cluster_centers_{year}.csv", index=False)
    print(f"Saved cluster centers to {DATA_DIR / f'cluster_centers_{year}.csv'}")
    
    # Generate cluster descriptions
    cluster_descriptions = []
    for cluster_id in range(n_clusters):
        cluster_data = df_cluster[df_cluster['cluster'] == cluster_id]
        desc = {
            'cluster_id': cluster_id,
            'count': len(cluster_data),
            'avg_height': float(cluster_data['Height'].mean()) if 'Height' in cluster_data.columns else None,
            'avg_usage': float(cluster_data['Usage'].mean()) if 'Usage' in cluster_data.columns else None,
            'avg_bpm': float(cluster_data['BPM'].mean()) if 'BPM' in cluster_data.columns else None,
            'top_players': cluster_data.nlargest(5, 'BPM')[['Name', 'Team', 'BPM']].to_dict('records') if 'BPM' in cluster_data.columns else []
        }
        cluster_descriptions.append(desc)
    
    with open(DATA_DIR / f"cluster_descriptions_{year}.json", 'w') as f:
        json.dump(cluster_descriptions, f, indent=2)
    print(f"Saved cluster descriptions to {DATA_DIR / f'cluster_descriptions_{year}.json'}")
    
    print(f"\n=== Cluster Analysis for {year} (K={n_clusters}) ===")
    for cluster_id in range(n_clusters):
        cluster_data = df_cluster[df_cluster['cluster'] == cluster_id]
        print(f"Cluster {cluster_id} (n={len(cluster_data)}):")
        if 'Height' in cluster_data.columns:
            print(f"  Average Height: {cluster_data['Height'].mean():.1f} inches")
        if 'Usage' in cluster_data.columns:
            print(f"  Average Usage: {cluster_data['Usage'].mean():.1f}%")
        if 'BPM' in cluster_data.columns:
            print(f"  Average BPM: {cluster_data['BPM'].mean():.2f}")
    
    return df_cluster, cluster_descriptions


def cluster_all_historical_years(start_year: int = 2019, end_year: int = 2025):
    """Generate cluster assignments for all historical years."""
    print(f"=== Clustering Historical Players ({start_year}-{end_year}) ===\n")
    
    all_results = {}
    
    for year in range(start_year, end_year + 1):
        df_cluster, cluster_descriptions = cluster_players_basic(year)
        if df_cluster is not None:
            all_results[year] = {
                'df': df_cluster,
                'descriptions': cluster_descriptions
            }
        print()
    
    print(f"=== Summary ===")
    print(f"Successfully clustered {len(all_results)} years")
    for year in all_results:
        print(f"  {year}: {len(all_results[year]['df'])} players")
    
    return all_results


if __name__ == "__main__":
    cluster_all_historical_years(start_year=2019, end_year=2025)

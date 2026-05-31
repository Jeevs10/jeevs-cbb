"""Cluster players using a unified approach across all years for stable cluster assignments."""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import json

DATA_DIR = Path(__file__).parent / "data"

def load_all_years_data():
    """Load player data from all available years using torvik data for better features."""
    all_data = []
    years = []

    for year in range(2019, 2027):
        # Try torvik data first (has ht, bpm, and many other features)
        torvik_file = DATA_DIR / "players" / f"{year}_torvik.csv"
        if torvik_file.exists():
            print(f"Loading torvik player data for year {year}...")
            df = pd.read_csv(torvik_file)
            # Map torvik columns to standard names
            df['Name'] = df['player_name']
            df['Team'] = df['team']
            df['AthleteSourceId'] = df['AthleteSourceId'].astype(str)
            df['year'] = year

            # Map Height from ht column (format: "6-6") to inches
            def height_to_inches(h):
                if pd.isna(h):
                    return None
                if isinstance(h, str) and '-' in h:
                    parts = h.split('-')
                    if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                        try:
                            return int(parts[0]) * 12 + int(parts[1])
                        except ValueError:
                            return None
                return h

            df['Height'] = df['ht'].apply(height_to_inches)
            df['BPM'] = df['bpm']  # Use torvik's BPM directly
            df['OBPM'] = df['obpm']  # Offensive BPM
            df['DBPM'] = df['dbpm']  # Defensive BPM
            df['Usage'] = df['usgG1']  # Usage rate
            df['ThreePointPct'] = df['TP_per'] * 100  # Actual 3-point shooting percentage
            df['ThreePointAttemptRate'] = df['TPA'] / (df['TPA'] + df['twoPA']) * 100  # 3P attempt rate
            df['TwoPointFieldGoals Pct'] = df['twoP_per'] * 100
            df['FreeThrows Pct'] = df['FT_per'] * 100
            df['FTR'] = df['ftr']  # Free throw rate
            df['off_twoprimr'] = df.get('rimmade/(ri', 0) * 100  # Rim frequency proxy

            all_data.append(df)
            years.append(year)
            print(f"  Loaded {len(df)} players for {year}")
        else:
            print(f"  WARNING: No torvik data found for year {year}")

    if not all_data:
        raise ValueError("No player data found for any year")

    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\nCombined data: {len(combined_df)} player-seasons from years {min(years)}-{max(years)}")
    return combined_df

def cluster_players_unified():
    """Cluster all player-seasons together for stable cluster assignments."""
    print("=== Unified Player Clustering ===\n")

    # Load all years data
    df = load_all_years_data()

    # Select playstyle clustering features (using torvik data columns)
    clustering_features = [
        'OBPM',  # Offensive BPM to split offensive players
        'DBPM',  # Defensive BPM to split defensive players
        'Height',
        'Usage',
        'off_twoprimr',
        'ThreePointPct',  # Actual 3-point shooting percentage
        'ThreePointAttemptRate',  # 3-point attempt rate for display
        'TwoPointFieldGoals Pct',
        'FreeThrows Pct',
        'FTR',  # Free throw rate
        'eFG',  # Effective field goal percentage
        'TS_per',  # True shooting percentage
        'ORB_per',  # Offensive rebound percentage
        'DRB_per',  # Defensive rebound percentage
        'AST_per',  # Assist percentage
        'TO_per',  # Turnover percentage
        'blk_per',  # Block percentage
        'stl_per',  # Steal percentage
    ]

    # Filter to available features
    available_features = [f for f in clustering_features if f in df.columns]
    print(f"\nUsing {len(available_features)} playstyle features for clustering: {available_features}")

    # Filter to players with sufficient data (include filter columns and BPM for statistics)
    required_cols = ['year', 'Name', 'Team', 'AthleteSourceId', 'BPM']
    filter_cols = ['Min_per', 'GP']  # Columns for filtering low-volume players
    available_cols = [c for c in required_cols if c in df.columns]
    available_filter_cols = [c for c in filter_cols if c in df.columns]
    df_cluster = df[available_features + available_cols + available_filter_cols].copy()

    # Filter out low-volume players to avoid noise from extreme BPM values
    before_filter = len(df_cluster)

    # Filter by minutes per game
    if 'Min_per' in df_cluster.columns:
        min_minutes_threshold = 15.0  # Minimum minutes per game
        df_cluster = df_cluster[df_cluster['Min_per'] >= min_minutes_threshold]
        print(f"Filtered to {len(df_cluster)} players with >= {min_minutes_threshold} minutes per game")

    # Filter by games played
    if 'GP' in df_cluster.columns:
        min_games = 10  # Minimum games played
        df_cluster = df_cluster[df_cluster['GP'] >= min_games]
        print(f"Filtered to {len(df_cluster)} players with >= {min_games} games played")

    print(f"Total filtered out: {before_filter - len(df_cluster)} low-volume players")

    df_cluster = df_cluster.dropna(subset=available_features)
    print(f"Filtered to {len(df_cluster)} player-seasons with complete playstyle data")

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_cluster[available_features])

    # Use K=18 to separate star guards, wings, and bigs
    n_clusters = 18
    print(f"\nRunning K-means clustering with K={n_clusters}...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)

    # Add cluster labels to data
    df_cluster['cluster'] = clusters

    # Analyze clusters
    print(f"\n=== Cluster Analysis (K={n_clusters}) ===")
    for cluster_id in range(n_clusters):
        cluster_data = df_cluster[df_cluster['cluster'] == cluster_id]
        print(f"\nCluster {cluster_id} (n={len(cluster_data)}):")

        # Print available stats
        if 'Height' in cluster_data.columns:
            print(f"  Average Height: {cluster_data['Height'].mean():.1f} inches")
        if 'Usage' in cluster_data.columns:
            print(f"  Average Usage: {cluster_data['Usage'].mean():.1f}%")
        if 'off_twoprimr' in cluster_data.columns:
            print(f"  Average Rim Frequency: {cluster_data['off_twoprimr'].mean():.1f}%")
        if 'ThreePointFieldGoals Pct' in cluster_data.columns:
            print(f"  Average 3PT%: {cluster_data['ThreePointFieldGoals Pct'].mean():.1f}%")
        if 'BPM' in cluster_data.columns:
            print(f"  Average BPM: {cluster_data['BPM'].mean():.2f}")

        # Show top players in cluster by BPM
        if 'BPM' in cluster_data.columns:
            top_players = cluster_data.nlargest(5, 'BPM')
            print(f"  Top 5 players by BPM:")
            for _, row in top_players.iterrows():
                print(f"    {row['Name']} ({row['Team']}, {row['year']}): BPM {row['BPM']:.2f}")

    # PCA for visualization
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    df_cluster['pca_1'] = X_pca[:, 0]
    df_cluster['pca_2'] = X_pca[:, 1]

    # Save combined cluster data
    output_cols = ['year', 'Name', 'Team', 'cluster', 'pca_1', 'pca_2', 'BPM', 'Height', 'Usage', 'AthleteSourceId'] + available_features
    output_cols = [c for c in output_cols if c in df_cluster.columns]
    df_cluster[output_cols].to_csv(DATA_DIR / "player_clusters_unified.csv", index=False)
    print(f"\nSaved unified cluster data to {DATA_DIR / 'player_clusters_unified.csv'}")

    # Save cluster centers for interpretation
    cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
    cluster_centers_df = pd.DataFrame(cluster_centers, columns=available_features)
    cluster_centers_df.to_csv(DATA_DIR / "cluster_centers_unified.csv", index=False)
    print(f"Saved cluster centers to {DATA_DIR / 'cluster_centers_unified.csv'}")

    # Generate cluster descriptions (using the clustered data directly since it has Height and BPM)
    cluster_descriptions = []
    for cluster_id in range(n_clusters):
        cluster_data = df_cluster[df_cluster['cluster'] == cluster_id]

        desc = {
            'cluster_id': cluster_id,
            'count': len(cluster_data),
            'avg_height': float(cluster_data['Height'].mean()) if 'Height' in cluster_data.columns else 0,
            'avg_usage': float(cluster_data['Usage'].mean()) if 'Usage' in cluster_data.columns else 0,
            'avg_rim_freq': float(cluster_data['off_twoprimr'].mean()) if 'off_twoprimr' in cluster_data.columns else 0,
            'avg_3pt_pct': float(cluster_data['ThreePointAttemptRate'].mean()) if 'ThreePointAttemptRate' in cluster_data.columns else 0,
            'avg_bpm': float(cluster_data['BPM'].mean()) if 'BPM' in cluster_data.columns else 0,
            'top_players': []
        }

        # Get top players from clustered data
        if 'BPM' in cluster_data.columns:
            top_players = cluster_data.nlargest(5, 'BPM')[['Name', 'Team', 'BPM']]
            desc['top_players'] = top_players.to_dict('records')

        cluster_descriptions.append(desc)

    with open(DATA_DIR / "cluster_descriptions_unified.json", 'w') as f:
        json.dump(cluster_descriptions, f, indent=2)
    print(f"Saved cluster descriptions to {DATA_DIR / 'cluster_descriptions_unified.json'}")

    # Split by year for individual year files
    for year in range(2019, 2027):
        year_data = df_cluster[df_cluster['year'] == year]
        if len(year_data) > 0:
            year_cols = ['Name', 'Team', 'cluster', 'BPM', 'Height', 'Usage', 'AthleteSourceId', 'AthleteId']
            year_cols = [c for c in year_cols if c in year_data.columns]
            year_output = year_data[year_cols]
            year_output.to_csv(DATA_DIR / f"player_clusters_{year}.csv", index=False)
            print(f"Saved {len(year_data)} cluster assignments for year {year}")

    return df_cluster, cluster_descriptions

if __name__ == "__main__":
    cluster_players_unified()

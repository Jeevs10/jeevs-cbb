"""Cluster players based on their analytical profile."""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import json

DATA_DIR = Path(__file__).parent / "data"

def cluster_players():
    """Cluster players based on playstyle features (height, rim frequency, usage, etc.)."""
    print("Clustering players based on playstyle profile...")
    
    # Load player data
    import sys
    sys.path.append('.')
    from app.core.data_loader import df
    
    df_2026 = df[df['year'] == 2026].copy()
    print(f"Loaded {len(df_2026)} players for 2026")
    
    # Select playstyle clustering features (only those available in enriched data)
    clustering_features = [
        'BPM',  # Performance metric to separate star players
        'OBPM',  # Offensive BPM to separate offensive specialists
        'DBPM',  # Defensive BPM to separate defensive specialists
        'Height',  # Physical attribute
        'Usage',  # Usage rate
        'off_twoprimr',  # Rim frequency
        'off_ast_rim',  # Assisted rim frequency
        'ThreePointFieldGoals Pct',  # 3PT shooting percentage
        '3p/100?',  # 3PT attempts per 100 possessions (to distinguish actual shooters)
        'TwoPointFieldGoals Pct',  # 2PT shooting
        'FreeThrows Pct',  # FT shooting
        'off_style_rim_attack_pct',  # Rim attack playstyle
        'off_style_rim_attack_usg',  # Rim attack usage
        'off_style_perimeter_sniper_pct',  # 3PT specialist playstyle
        'off_style_dribble_jumper_pct',  # Dribble jumper playstyle
        'off_style_mid_range_pct',  # Mid-range playstyle
        'off_style_hits_cutter_pct',  # Cutter playstyle
        'off_style_perimeter_cut_pct',  # Perimeter cutter playstyle
        'off_style_pnr_passer_pct',  # PnR passer playstyle
        'off_style_big_cut_roll_pct',  # Roll man playstyle
        'off_style_post_up_pct',  # Post-up playstyle
        'off_style_transition_usg',  # Transition usage
    ]
    
    # Filter to available features
    available_features = [f for f in clustering_features if f in df_2026.columns]
    print(f"Using {len(available_features)} playstyle features for clustering")
    
    # Filter to players with sufficient data (enriched players have playstyle data)
    df_cluster = df_2026[available_features].copy()
    df_cluster = df_cluster.dropna()
    print(f"Filtered to {len(df_cluster)} players with complete playstyle data")
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_cluster[available_features])
    
    # Determine optimal number of clusters using elbow method
    inertias = []
    K_range = range(2, 11)
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        inertias.append(kmeans.inertia_)
    
    print(f"\n=== Elbow Method Results ===")
    for k, inertia in zip(K_range, inertias):
        print(f"K={k}: Inertia={inertia:.2f}")
    
    # Use K=18 to separate star guards, wings, and bigs
    n_clusters = 18
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    # Add cluster labels to original data
    df_cluster['cluster'] = clusters
    df_cluster['Name'] = df_2026.loc[df_cluster.index, 'Name']
    df_cluster['Team'] = df_2026.loc[df_cluster.index, 'Team']
    df_cluster['posClass'] = df_2026.loc[df_cluster.index, 'posClass']
    df_cluster['BPM'] = df_2026.loc[df_cluster.index, 'BPM']
    df_cluster['AthleteSourceId'] = df_2026.loc[df_cluster.index, 'AthleteSourceId']
    df_cluster['AthleteId'] = df_2026.loc[df_cluster.index, 'AthleteId']
    
    # Analyze clusters
    print(f"\n=== Cluster Analysis (K={n_clusters}) ===")
    for cluster_id in range(n_clusters):
        cluster_data = df_cluster[df_cluster['cluster'] == cluster_id]
        print(f"\nCluster {cluster_id} (n={len(cluster_data)}):")
        print(f"  Average Height: {cluster_data['Height'].mean():.1f} inches")
        print(f"  Average Usage: {cluster_data['Usage'].mean():.1f}%")
        print(f"  Average Rim Frequency: {cluster_data['off_twoprimr'].mean():.1f}%")
        print(f"  Average 3PT%: {cluster_data['ThreePointFieldGoals Pct'].mean():.1f}%")
        print(f"  Average BPM: {cluster_data['BPM'].mean():.2f}")
        
        # Show top players in cluster by BPM
        top_players = cluster_data.nlargest(5, 'BPM')
        print(f"  Top 5 players by BPM:")
        for _, row in top_players.iterrows():
            print(f"    {row['Name']} ({row['Team']}): BPM {row['BPM']:.2f}")
    
    # PCA for visualization
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    df_cluster['pca_1'] = X_pca[:, 0]
    df_cluster['pca_2'] = X_pca[:, 1]
    
    # Save cluster data
    output_cols = ['Name', 'Team', 'cluster', 'pca_1', 'pca_2', 'BPM', 'Height', 'Usage', 'AthleteSourceId', 'AthleteId'] + available_features
    df_cluster[output_cols].to_csv(DATA_DIR / "player_clusters.csv", index=False)
    print(f"\nSaved cluster data to {DATA_DIR / 'player_clusters.csv'}")
    
    # Save cluster centers for interpretation
    cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
    cluster_centers_df = pd.DataFrame(cluster_centers, columns=available_features)
    cluster_centers_df.to_csv(DATA_DIR / "cluster_centers.csv", index=False)
    print(f"Saved cluster centers to {DATA_DIR / 'cluster_centers.csv'}")
    
    # Generate cluster descriptions
    cluster_descriptions = []
    for cluster_id in range(n_clusters):
        cluster_data = df_cluster[df_cluster['cluster'] == cluster_id]
        desc = {
            'cluster_id': cluster_id,
            'count': len(cluster_data),
            'avg_height': float(cluster_data['Height'].mean()),
            'avg_usage': float(cluster_data['Usage'].mean()),
            'avg_rim_freq': float(cluster_data['off_twoprimr'].mean()),
            'avg_3pt_pct': float(cluster_data['ThreePointFieldGoals Pct'].mean()),
            'avg_bpm': float(cluster_data['BPM'].mean()),
            'top_players': cluster_data.nlargest(5, 'BPM')[['Name', 'Team', 'BPM']].to_dict('records')
        }
        cluster_descriptions.append(desc)
    
    with open(DATA_DIR / "cluster_descriptions.json", 'w') as f:
        json.dump(cluster_descriptions, f, indent=2)
    print(f"Saved cluster descriptions to {DATA_DIR / 'cluster_descriptions.json'}")
    
    return df_cluster, cluster_descriptions

if __name__ == "__main__":
    cluster_players()

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import json
from pathlib import Path

def cluster_teams():
    """Cluster teams based on their archetype composition and performance metrics."""
    
    # Load team archetype data
    archetype_path = Path(__file__).parent / "data" / "archetype_team_analysis.csv"
    
    if not archetype_path.exists():
        print("Team archetype data not found")
        return
    
    df = pd.read_csv(archetype_path)
    
    # Select features for clustering (playstyle metrics)
    feature_columns = [
        'off_adj_ppp', 'def_adj_ppp', 'off_efg', 'def_efg', 
        'off_to', 'def_to', 'off_ftr', 'def_ftr', 'off_orb', 'def_orb',
        'off_assist', 'off_trans_pct', 'off_trans_ppp', 'def_trans_pct',
        'off_scramble_pct', 'off_scramble_ppp', 'def_scramble_pct',
        'tempo', 'off_threep', 'def_threep', 'weighted_team_bpm', 'adj_net'
    ]
    
    # Filter to only columns that exist
    available_features = [col for col in feature_columns if col in df.columns]
    
    if len(available_features) == 0:
        print("No features available for clustering")
        return
    
    # Prepare data for clustering
    X = df[available_features].fillna(0)
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Perform PCA for visualization
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    # Cluster teams (using 6 clusters for team archetypes)
    n_clusters = 6
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    # Add cluster and PCA coordinates to dataframe
    df['team_cluster'] = clusters
    df['pca_1'] = X_pca[:, 0]
    df['pca_2'] = X_pca[:, 1]
    
    # Calculate cluster statistics
    cluster_stats = []
    for cluster_id in range(n_clusters):
        cluster_df = df[df['team_cluster'] == cluster_id]
        
        stats = {
            'cluster_id': cluster_id,
            'count': len(cluster_df),
            'avg_adj_net': cluster_df['adj_net'].mean() if 'adj_net' in cluster_df.columns else 0,
            'avg_weighted_bpm': cluster_df['weighted_team_bpm'].mean() if 'weighted_team_bpm' in cluster_df.columns else 0,
            'avg_wins': cluster_df['wins'].mean() if 'wins' in cluster_df.columns else 0,
            'avg_off_adj_ppp': cluster_df['off_adj_ppp'].mean() if 'off_adj_ppp' in cluster_df.columns else 0,
            'avg_def_adj_ppp': cluster_df['def_adj_ppp'].mean() if 'def_adj_ppp' in cluster_df.columns else 0,
            'avg_off_efg': cluster_df['off_efg'].mean() if 'off_efg' in cluster_df.columns else 0,
            'avg_def_efg': cluster_df['def_efg'].mean() if 'def_efg' in cluster_df.columns else 0,
            'avg_tempo': cluster_df['tempo'].mean() if 'tempo' in cluster_df.columns else 0,
            'avg_off_threep': cluster_df['off_threep'].mean() if 'off_threep' in cluster_df.columns else 0,
            'avg_def_threep': cluster_df['def_threep'].mean() if 'def_threep' in cluster_df.columns else 0,
        }
        cluster_stats.append(stats)
    
    # Save team clusters
    output_path = Path(__file__).parent / "data" / "team_clusters.csv"
    df.to_csv(output_path, index=False)
    print(f"Team clusters saved to {output_path}")
    
    # Save cluster descriptions
    descriptions_path = Path(__file__).parent / "data" / "team_cluster_descriptions.json"
    with open(descriptions_path, 'w') as f:
        json.dump(cluster_stats, f, indent=2)
    print(f"Cluster descriptions saved to {descriptions_path}")
    
    return df, cluster_stats

if __name__ == "__main__":
    cluster_teams()

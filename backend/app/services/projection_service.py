"""
Cluster-based player projection service.

Uses historical year-over-year BPM changes from players in the same cluster
to predict a target player's growth, weighted by feature similarity.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from app.utils.logger import get_logger
from app.services.similarity_service import get_similar_players

logger = get_logger(__name__)


class ProjectionService:
    """Service for cluster-based player projections."""
    
    # Feature weights for similarity calculation
    FEATURE_WEIGHTS = {
        'Usage_from': 0.25,
        'BPM_from': 0.20,
        'Height': 0.15,
        'off_rtg_from': 0.10,
        'def_rtg_from': 0.10,
        'eFG_from': 0.10,
        'TS_per_from': 0.10,
    }
    
    # Alternative features available in BPM change data
    BPM_CHANGE_FEATURES = {
        'Usage_from': 0.25,
        'PPG_from': 0.20,
        'APG_from': 0.15,
        'RPG_from': 0.15,
        'eFG_from': 0.15,
        'TS_per_from': 0.10,
    }
    
    # Key features for clustering
    CLUSTER_FEATURES = [
        'Usage', 'BPM', 'Height', 'off_rtg', 'def_rtg',
        'off_efg', 'TrueShootingPct', 'Usage'
    ]
    
    def __init__(self):
        """Initialize the projection service with lazy data loading."""
        self._clusters_df = None
        self._bpm_change_df = None
        self._cluster_descriptions = None
        self._players_df = None
        self._player_id_to_cluster = {}
        self._player_key_to_name = {}
        self._transition_matrix = None
        self._cluster_development = None
        self._projection_cache = None  # Cache for pre-calculated projections
        self._data_loaded = False
    
    def _ensure_data_loaded(self):
        """Lazy load data only when needed."""
        if self._data_loaded:
            return
        
        try:
            base_dir = Path(__file__).parent.parent.parent

            # Load cluster descriptions first (small JSON file)
            cluster_desc_path = base_dir / "data" / "cluster_descriptions.json"
            if cluster_desc_path.exists():
                import json
                with open(cluster_desc_path, 'r') as f:
                    cluster_desc_array = json.load(f)
                # Convert array to dictionary keyed by cluster_id for easier lookup
                self._cluster_descriptions = {
                    str(desc['cluster_id']): desc for desc in cluster_desc_array
                }
                logger.info(f"Loaded {len(self._cluster_descriptions)} cluster descriptions")
            else:
                logger.warning(f"Cluster descriptions not found: {cluster_desc_path}")

            # Load player clusters
            clusters_path = base_dir / "data" / "player_clusters.csv"
            if clusters_path.exists():
                self._clusters_df = pd.read_csv(clusters_path)
                logger.info(f"Loaded {len(self._clusters_df)} player cluster assignments")
            else:
                logger.warning(f"Clusters file not found: {clusters_path}")

            # Load players data to create ID mapping
            players_path = base_dir / "data" / "players" / "2026-players_basic.csv"
            if players_path.exists():
                self._players_df = pd.read_csv(players_path)
                logger.info(f"Loaded {len(self._players_df)} players for ID mapping")
                self._build_player_id_mapping(base_dir)
            else:
                logger.warning(f"Players file not found: {players_path}")

            # Load BPM change modeling data (largest file, load last)
            bpm_change_path = base_dir / "data" / "bpm_change_modeling_data.csv"
            if bpm_change_path.exists():
                self._bpm_change_df = pd.read_csv(bpm_change_path)
                logger.info(f"Loaded {len(self._bpm_change_df)} historical BPM change records")
            else:
                logger.warning(f"BPM change data not found: {bpm_change_path}")

            # Load cluster transition matrix
            transition_path = base_dir / "data" / "cluster_transition_matrix.json"
            if transition_path.exists():
                import json
                with open(transition_path, 'r') as f:
                    self._transition_matrix = json.load(f)
                logger.info("Loaded cluster transition matrix")
            else:
                logger.warning(f"Cluster transition matrix not found: {transition_path}")

            # Load cluster development stats
            development_path = base_dir / "data" / "cluster_development_stats.json"
            if development_path.exists():
                with open(development_path, 'r') as f:
                    self._cluster_development = json.load(f)
                logger.info("Loaded cluster development stats")
            else:
                logger.warning(f"Cluster development stats not found: {development_path}")

            # Load pre-calculated projection leaderboard for fast lookups
            projection_cache_path = base_dir / "data" / "projection_leaderboard_2027.csv"
            if projection_cache_path.exists():
                self._projection_cache = pd.read_csv(projection_cache_path)
                # Build a dictionary keyed by player_key for O(1) lookups
                self._projection_cache_dict = {}
                for _, row in self._projection_cache.iterrows():
                    player_key = str(row['player_key'])
                    self._projection_cache_dict[player_key] = row.to_dict()
                logger.info(f"Loaded projection cache with {len(self._projection_cache_dict)} players")
            else:
                logger.warning(f"Projection cache not found: {projection_cache_path}")
                self._projection_cache_dict = {}

            self._data_loaded = True
            logger.info("Projection service data loading complete")

        except Exception as e:
            logger.error(f"Error loading projection data: {str(e)}")
            raise
    
    def _build_player_id_mapping(self, base_dir):
        """Build a mapping from player ID to cluster using AthleteSourceId."""
        if self._players_df is None or self._clusters_df is None:
            return
        
        # Build mapping directly from AthleteSourceId in clusters file
        for _, row in self._clusters_df.iterrows():
            athlete_source_id = str(row.get('AthleteSourceId', ''))
            # Remove .0 suffix to match player_key format
            athlete_source_id = athlete_source_id.replace('.0', '')
            
            if athlete_source_id:
                self._player_id_to_cluster[athlete_source_id] = {
                    'cluster_id': row['cluster'],
                    'BPM': row.get('BPM'),
                    'Height': row.get('Height'),
                    'Usage': row.get('Usage'),
                    'off_rtg': row.get('off_rtg'),
                    'def_rtg': row.get('def_rtg'),
                }
        
        logger.info(f"Built mapping for {len(self._player_id_to_cluster)} players to clusters (via AthleteSourceId)")

        # Build mapping from player_key (AthleteSourceId) to name and team for display
        for _, row in self._players_df.iterrows():
            athlete_source_id = str(row.get('AthleteSourceId', ''))
            # Remove .0 suffix to match player_key format
            athlete_source_id = athlete_source_id.replace('.0', '')
            name = row.get('Name', '')
            team = row.get('Team', '')
            if name:
                if athlete_source_id:
                    self._player_key_to_name[athlete_source_id] = f"{name} ({team})"

        # Also load historical players for name mapping
        try:
            for year in range(2019, 2026):
                historical_players_file = base_dir / "data" / "players" / f"{year}-players_basic.csv"
                if historical_players_file.exists():
                    historical_df = pd.read_csv(historical_players_file)
                    for _, row in historical_df.iterrows():
                        athlete_source_id = str(row.get('AthleteSourceId', ''))
                        # Remove .0 suffix to match player_key format
                        athlete_source_id = athlete_source_id.replace('.0', '')
                        name = row.get('Name', '')
                        team = row.get('Team', '')
                        if name:
                            if athlete_source_id:
                                self._player_key_to_name[athlete_source_id] = f"{name} ({team})"
        except Exception as e:
            logger.warning(f"Could not load historical player names: {e}")

        logger.info(f"Built name mapping for {len(self._player_key_to_name)} player keys")

        logger.info(f"Final name mapping has {len(self._player_key_to_name)} player keys")
    
    def get_player_cluster(self, ncaa_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cluster information for a player.

        Args:
            ncaa_id: Player NCAA ID

        Returns:
            Dictionary with cluster_id and description, or None if not found
        """
        self._ensure_data_loaded()
        if self._clusters_df is None:
            return None

        # Remove .0 suffix to match player_key format
        ncaa_id = ncaa_id.replace('.0', '')

        # First try the ID mapping we built from name/team matching
        if ncaa_id in self._player_id_to_cluster:
            cluster_data = self._player_id_to_cluster[ncaa_id]
            cluster_id = cluster_data['cluster_id']

            # Get cluster description
            cluster_desc = None
            if self._cluster_descriptions:
                cluster_desc = self._cluster_descriptions.get(str(cluster_id))

            return {
                'cluster_id': cluster_id,
                'cluster_description': cluster_desc,
                'player_features': {
                    'BPM': cluster_data.get('BPM'),
                    'Height': cluster_data.get('Height'),
                    'Usage': cluster_data.get('Usage'),
                    'off_rtg': cluster_data.get('off_rtg'),
                    'def_rtg': cluster_data.get('def_rtg'),
                }
            }
        
        # Try direct player_key match if it exists in clusters
        if 'player_key' in self._clusters_df.columns:
            player_row = self._clusters_df[
                self._clusters_df['player_key'].astype(str) == str(ncaa_id)
            ]
            if not player_row.empty:
                return self._extract_cluster_info(player_row.iloc[0])
        
        # No matching player found
        logger.warning(f"Player {ncaa_id} not found in cluster data")
        return None
    
    def _extract_cluster_info(self, row: pd.Series) -> Dict[str, Any]:
        """Extract cluster information from a dataframe row."""
        cluster_id = int(row['cluster'])
        
        # Get cluster description
        cluster_desc = None
        if self._cluster_descriptions:
            cluster_desc = self._cluster_descriptions.get(str(cluster_id))
            if cluster_desc:
                # Add a descriptive name based on cluster characteristics
                cluster_desc['name'] = self._generate_cluster_name(cluster_desc)

        return {
            'cluster_id': cluster_id,
            'cluster_description': cluster_desc,
            'player_features': {
                'BPM': row.get('BPM'),
                'Height': row.get('Height'),
                'Usage': row.get('Usage'),
                'off_rtg': row.get('off_rtg'),
                'def_rtg': row.get('def_rtg'),
            }
        }
    
    def _generate_cluster_name(self, cluster_desc: Dict[str, Any]) -> str:
        """Generate a descriptive name for a cluster based on its characteristics."""
        avg_height = cluster_desc.get('avg_height', 74)
        avg_usage = cluster_desc.get('avg_usage', 20)
        avg_rim_freq = cluster_desc.get('avg_rim_freq', 0.3)
        avg_3pt_rate = cluster_desc.get('avg_3pt_pct', 35)  # This is actually attempt rate
        avg_bpm = cluster_desc.get('avg_bpm', 0)
        
        # Height classification
        if avg_height < 74:
            height_desc = "Guard"
        elif avg_height < 78:
            height_desc = "Wing"
        else:
            height_desc = "Big"
        
        # Usage classification
        if avg_usage < 15:
            usage_desc = "Low-Usage"
        elif avg_usage < 25:
            usage_desc = "Mid-Usage"
        else:
            usage_desc = "High-Usage"
        
        # Shooting style - based on 3pt attempt rate (0-100 scale)
        # More granular categories to reduce duplicates
        if avg_3pt_rate > 45 and avg_rim_freq < 25:
            shooting_desc = "Shooter"
        elif avg_rim_freq > 65:
            shooting_desc = "Rim-Attacker"
        elif avg_3pt_rate > 35:
            shooting_desc = "Stretch"
        elif avg_rim_freq > 50:
            shooting_desc = "Paint-Player"
        elif avg_3pt_rate > 25:
            shooting_desc = "Outside-Shooter"
        else:
            shooting_desc = "Balanced"
        
        # Performance
        if avg_bpm > 5:
            perf_desc = "Elite"
        elif avg_bpm > 2:
            perf_desc = "Above-Avg"
        elif avg_bpm > 0:
            perf_desc = "Average"
        else:
            perf_desc = "Below-Avg"
        
        return f"{height_desc} {usage_desc} {shooting_desc} ({perf_desc})"
    
    def get_cluster_historical_data(self, cluster_id: int) -> pd.DataFrame:
        """
        Get historical BPM change data for a specific cluster.

        Args:
            cluster_id: Cluster ID to filter by

        Returns:
            DataFrame with historical BPM changes for the cluster
        """
        self._ensure_data_loaded()
        if self._bpm_change_df is None or self._clusters_df is None:
            return pd.DataFrame()

        # Get players in this cluster with their IDs
        cluster_players = self._clusters_df[
            self._clusters_df['cluster'] == cluster_id
        ][['Name', 'Team', 'AthleteSourceId']].copy()

        # Collect all player IDs from the cluster
        cluster_player_ids = set()
        for _, row in cluster_players.iterrows():
            athlete_source_id = str(row.get('AthleteSourceId', ''))
            # Remove .0 suffix to match player_key format in BPM change data
            athlete_source_id = athlete_source_id.replace('.0', '')
            if athlete_source_id and athlete_source_id != 'nan':
                cluster_player_ids.add(athlete_source_id)

        logger.info(f"Cluster {cluster_id} has {len(cluster_player_ids)} unique player IDs")
        logger.info(f"Sample cluster IDs: {list(cluster_player_ids)[:5]}")

        # Check what IDs are in BPM change data
        if len(self._bpm_change_df) > 0:
            sample_bpm_ids = self._bpm_change_df['player_key'].astype(str).unique()[:5]
            logger.info(f"Sample BPM change player_key IDs: {sample_bpm_ids}")

        # Filter BPM change data for players in this cluster
        historical_data = self._bpm_change_df[
            self._bpm_change_df['player_key'].astype(str).isin(cluster_player_ids)
        ].copy()

        logger.info(f"Found {len(historical_data)} historical records for cluster {cluster_id}")

        # Add a flag for players who may have changed clusters
        if 'year_from' in historical_data.columns and 'year_to' in historical_data.columns:
            historical_data['year_gap'] = historical_data['year_to'] - historical_data['year_from']
            historical_data['potential_cluster_change'] = historical_data['year_gap'] > 1

        return historical_data
    
    def calculate_similarity(
        self,
        target_features: Dict[str, float],
        historical_features: Dict[str, float]
    ) -> float:
        """
        Calculate similarity between target player and historical player.

        Uses weighted Euclidean distance on key features.

        Args:
            target_features: Target player's features
            historical_features: Historical player's features

        Returns:
            Similarity score between 0 and 1
        """
        total_weight = 0.0
        weighted_distance = 0.0

        # Try BPM_CHANGE_FEATURES first (features available in historical data)
        for feature, weight in self.BPM_CHANGE_FEATURES.items():
            target_val = target_features.get(feature)
            hist_val = historical_features.get(feature)

            if target_val is None or hist_val is None:
                continue

            # Normalize by feature range (approximate)
            if feature in ['PPG_from']:
                max_range = 30.0  # PPG range
            elif feature in ['APG_from']:
                max_range = 10.0  # APG range
            elif feature in ['RPG_from']:
                max_range = 15.0  # RPG range
            elif feature in ['Usage_from', 'Usage']:
                max_range = 35.0  # Usage range
            elif feature in ['eFG_from', 'TS_per_from']:
                max_range = 1.0  # Percentage range (0-1)
            else:
                max_range = 50.0  # Default range

            # Calculate normalized distance
            distance = abs(target_val - hist_val) / max_range
            weighted_distance += weight * distance
            total_weight += weight

        if total_weight == 0:
            return 0.5  # Default similarity if no features match

        avg_distance = weighted_distance / total_weight
        similarity = 1.0 - min(avg_distance, 1.0)

        return similarity
    
    def calculate_projection(
        self,
        ncaa_id: str,
        current_year: int = 2026,
        years_ahead: int = 1,
        min_samples: int = 10
    ) -> Dict[str, Any]:
        """
        Calculate cluster-based projection for a player.

        Args:
            ncaa_id: Player NCAA ID
            current_year: Current year for the player
            years_ahead: Number of years to project (1-3)
            min_samples: Minimum historical samples required

        Returns:
            Dictionary with projection results
        """
        # Ensure data is loaded before processing
        self._ensure_data_loaded()

        # Check cache first for 2027 projections (years_ahead=1, current_year=2026)
        if (years_ahead == 1 and current_year == 2026 and 
            hasattr(self, '_projection_cache_dict') and self._projection_cache_dict):
            # Remove .0 suffix to match player_key format
            ncaa_id_clean = ncaa_id.replace('.0', '')
            if ncaa_id_clean in self._projection_cache_dict:
                cached = self._projection_cache_dict[ncaa_id_clean]
                logger.info(f"Cache hit for player {ncaa_id}, returning pre-calculated projection")
                
                # Get cluster description
                cluster_desc = None
                if self._cluster_descriptions:
                    cluster_desc = self._cluster_descriptions.get(str(cached['cluster_id']))
                
                # Calculate percentile using cluster historical data
                cluster_id = int(cached['cluster_id'])
                historical_data = self.get_cluster_historical_data(cluster_id)
                bpm_change = cached['bpm_change_predicted']
                percentile = 0.5  # Default to median
                if len(historical_data) > 0 and 'bpm_change' in historical_data.columns:
                    all_changes = historical_data['bpm_change'].dropna().values
                    if len(all_changes) > 0:
                        percentile = np.sum(all_changes < bpm_change) / len(all_changes)
                        logger.info(f"Percentile calculation: bpm_change={bpm_change}, all_changes_count={len(all_changes)}, changes_less={np.sum(all_changes < bpm_change)}, percentile={percentile}")
                else:
                    logger.warning(f"Could not calculate percentile: historical_data length={len(historical_data)}, has_bpm_change={'bpm_change' in historical_data.columns if len(historical_data) > 0 else 'N/A'}")
                
                # Build projection result from cached data
                return {
                    'player_id': ncaa_id,
                    'current_year': current_year,
                    'cluster_id': cluster_id,
                    'cluster_description': cluster_desc,
                    'current_bpm': cached['current_bpm'],
                    'projections': [{
                        'year': current_year + years_ahead,
                        'projected_bpm': cached['projected_bpm'],
                        'bpm_change': cached['bpm_change_predicted'],
                        'confidence_interval_lower': cached['projected_bpm_lower_90'],
                        'confidence_interval_upper': cached['projected_bpm_upper_90'],
                        'percentile_rank': round(percentile, 3),
                    }],
                    'historical_samples': int(cached['historical_samples']),
                    'methodology': 'cached',
                    'similar_players': [],  # Empty list for cached responses
                    'cluster_transitions': self._get_cluster_transitions(cluster_id),
                }

        # Get player cluster
        cluster_info = self.get_player_cluster(ncaa_id)
        if cluster_info is None:
            return {
                'error': 'Player not found in cluster data',
                'player_id': ncaa_id
            }
        
        cluster_id = cluster_info['cluster_id']
        target_features = cluster_info['player_features']

        # Get player's current stats from players data for similarity calculation
        player_stats = {}
        if self._players_df is not None:
            # Remove .0 suffix to match player_key format
            ncaa_id_clean = ncaa_id.replace('.0', '')
            # Try to find the player by AthleteSourceId (also try with .0 suffix)
            player_row = self._players_df[
                (self._players_df['AthleteSourceId'].astype(str) == str(ncaa_id)) |
                (self._players_df['AthleteSourceId'].astype(str) == ncaa_id_clean)
            ]
            if not player_row.empty:
                player_stats = player_row.iloc[0].to_dict()
                logger.info(f"Found player stats for {ncaa_id}: PPG={player_stats.get('PPG')}, APG={player_stats.get('APG')}, RPG={player_stats.get('RPG')}, Usage={player_stats.get('Usage')}")
            else:
                logger.warning(f"Player {ncaa_id} not found in players data")

        # Map target features to match historical data format
        # Ensure all values are numeric
        usage_val = target_features.get('Usage') or player_stats.get('Usage', 0)
        ppg_val = player_stats.get('PPG', 0)
        apg_val = player_stats.get('APG', 0)
        rpg_val = player_stats.get('RPG', 0)
        efg_val = player_stats.get('EffectiveFieldGoalPct', 50)
        ts_val = player_stats.get('TrueShootingPct', 50)

        target_features_mapped = {
            'Usage_from': float(usage_val) if pd.notna(usage_val) else 0,
            'PPG_from': float(ppg_val) if pd.notna(ppg_val) else 0,
            'APG_from': float(apg_val) if pd.notna(apg_val) else 0,
            'RPG_from': float(rpg_val) if pd.notna(rpg_val) else 0,
            'eFG_from': float(efg_val) / 100 if pd.notna(efg_val) else 0.5,
            'TS_per_from': float(ts_val) / 100 if pd.notna(ts_val) else 0.5,
        }

        logger.info(f"Target features mapped: {target_features_mapped}")

        # Get historical data for this cluster
        historical_data = self.get_cluster_historical_data(cluster_id)

        # Get cluster development patterns
        cluster_dev_stats = self._cluster_development.get(str(cluster_id), {}) if self._cluster_development else {}

        # Get cluster transition probabilities
        cluster_transitions = self._transition_matrix.get(str(cluster_id), {}) if self._transition_matrix else {}

        logger.info(f"Cluster {cluster_id} development stats: {list(cluster_dev_stats.keys())}")
        logger.info(f"Cluster {cluster_id} transitions: {len(cluster_transitions)} possible destinations")

        if len(historical_data) < min_samples:
            return {
                'error': f'Insufficient historical data (found {len(historical_data)}, need {min_samples})',
                'player_id': ncaa_id,
                'cluster_id': cluster_id
            }
        
        # Calculate similarities and weighted projections
        projections = []
        
        for year_offset in range(1, years_ahead + 1):
            weighted_changes = []
            similarities = []
            
            for _, row in historical_data.iterrows():
                # Extract historical features that are available in BPM change data
                hist_features = {
                    'Usage_from': row.get('Usage_from'),
                    'PPG_from': row.get('PPG_from'),
                    'APG_from': row.get('APG_from'),
                    'RPG_from': row.get('RPG_from'),
                    'eFG_from': row.get('eFG_from'),
                    'TS_per_from': row.get('TS_per_from'),
                }

                # Calculate similarity using mapped features
                try:
                    similarity = self.calculate_similarity(target_features_mapped, hist_features)
                except Exception as e:
                    logger.warning(f"Error calculating similarity: {e}")
                    similarity = 0.5
                
                # Get BPM change
                bpm_change = row.get('bpm_change')
                if pd.isna(bpm_change):
                    continue

                # Adjust similarity for potential cluster changes
                # If year gap > 1, the player may have changed clusters, so weight it lower
                if row.get('potential_cluster_change', False):
                    similarity *= 0.5  # Reduce weight by half for potential cluster changers

                weighted_changes.append(bpm_change * similarity)
                similarities.append(similarity)

            if not weighted_changes:
                projections.append({
                    'year': current_year + year_offset,
                    'error': 'No valid historical samples'
                })
                continue
            
            # Calculate weighted average from similar players
            total_weight = sum(similarities)
            weighted_avg = sum(weighted_changes) / total_weight if total_weight > 0 else 0

            # Incorporate cluster transition probabilities into projection
            # Weight projections by probability of staying in current cluster vs moving to destination clusters
            transition_weighted_changes = []
            transition_weights = []

            # Current cluster (stay probability)
            stay_probability = cluster_transitions.get(str(cluster_id), 0) if cluster_transitions else 0.5
            transition_weighted_changes.append(weighted_avg)
            transition_weights.append(stay_probability)

            # Add destination clusters with significant probability (>5%)
            for dest_cluster_id, prob in cluster_transitions.items():
                if float(prob) > 0.05 and dest_cluster_id != str(cluster_id):
                    # Get historical data for destination cluster
                    dest_historical = self.get_cluster_historical_data(int(dest_cluster_id))
                    if len(dest_historical) > 10:  # Only use if sufficient data
                        dest_weighted_changes = []
                        dest_similarities = []

                        for _, row in dest_historical.iterrows():
                            hist_features = {
                                'Usage_from': row.get('Usage_from'),
                                'PPG_from': row.get('PPG_from'),
                                'APG_from': row.get('APG_from'),
                                'RPG_from': row.get('RPG_from'),
                                'eFG_from': row.get('eFG_from'),
                                'TS_per_from': row.get('TS_per_from'),
                            }

                            try:
                                similarity = self.calculate_similarity(target_features_mapped, hist_features)
                            except Exception as e:
                                similarity = 0.5

                            bpm_change = row.get('bpm_change')
                            if pd.isna(bpm_change):
                                continue

                            dest_weighted_changes.append(bpm_change * similarity)
                            dest_similarities.append(similarity)

                        if dest_weighted_changes:
                            dest_total_weight = sum(dest_similarities)
                            dest_weighted_avg = sum(dest_weighted_changes) / dest_total_weight if dest_total_weight > 0 else 0
                            transition_weighted_changes.append(dest_weighted_avg)
                            transition_weights.append(float(prob))

            # Calculate weighted average across all clusters
            total_transition_weight = sum(transition_weights)
            if total_transition_weight > 0:
                blended_change = sum(wc * w for wc, w in zip(transition_weighted_changes, transition_weights)) / total_transition_weight
            else:
                blended_change = weighted_avg

            # Incorporate cluster development patterns as a baseline
            cluster_ppg_change = 0
            if 'PPG' in cluster_dev_stats:
                cluster_ppg_change = cluster_dev_stats['PPG'].get('mean_change', 0)

            # Blend transition-weighted average with cluster development pattern
            # Use cluster development as 20% of the projection, transition-weighted as 80%
            blended_change = 0.8 * blended_change + 0.2 * cluster_ppg_change

            # Calculate confidence interval using only similar players
            # Filter to top similar players to reduce variance
            if len(weighted_changes) > 20:
                # Use top 20 most similar players for CI calculation
                top_indices = np.argsort(similarities)[-20:]
                filtered_changes = np.array(weighted_changes)[top_indices]
                filtered_similarities = np.array(similarities)[top_indices]
            else:
                filtered_changes = np.array(weighted_changes)
                filtered_similarities = np.array(similarities)

            # Calculate weighted variance from similar players only
            if len(filtered_changes) > 0:
                filtered_weights = filtered_similarities / np.sum(filtered_similarities)
                weighted_avg_similar = np.average(filtered_changes, weights=filtered_weights)
                weighted_variance = np.average((filtered_changes - weighted_avg_similar) ** 2, weights=filtered_weights)
                weighted_std = np.sqrt(weighted_variance)
            else:
                weighted_std = 2.0  # Default std dev if no similar players

            # Apply similarity-based reduction - higher average similarity = tighter CI
            avg_similarity = np.mean(similarities) if similarities else 0.5
            similarity_reduction = 0.5 + (avg_similarity * 0.5)  # Range: 0.5 to 1.0
            weighted_std *= similarity_reduction

            # Increase confidence interval if cluster transition is likely (low stay probability)
            if stay_probability < 0.5:
                weighted_std *= 1.1  # Smaller increase than before

            # Current BPM
            current_bpm = target_features.get('BPM', 0)
            projected_bpm = current_bpm + blended_change
            
            # Confidence interval (80% - tighter)
            ci_lower = projected_bpm - 1.28 * weighted_std
            ci_upper = projected_bpm + 1.28 * weighted_std
            
            # Calculate percentile rank (how good is this projection?)
            all_changes = historical_data['bpm_change'].dropna().values
            percentile = (np.sum(all_changes < weighted_avg) / len(all_changes)) if len(all_changes) > 0 else 0.5
            
            projections.append({
                'year': current_year + year_offset,
                'projected_bpm': round(projected_bpm, 2),
                'bpm_change': round(blended_change, 2),
                'confidence_interval': [round(ci_lower, 2), round(ci_upper, 2)],
                'percentile_rank': round(percentile, 3),
                'sample_size': len(weighted_changes)
            })
        
        # Get similar players for context
        try:
            logger.info(f"Getting similar players with {len(historical_data)} historical records")
            similar_players = self._get_similar_players(
                target_features_mapped,
                historical_data,
                limit=5,
                ncaa_id=ncaa_id
            )
            logger.info(f"Got {len(similar_players)} similar players")
        except Exception as e:
            logger.error(f"Error getting similar players: {e}")
            similar_players = []
        
        return {
            'player_id': ncaa_id,
            'current_year': current_year,
            'current_bpm': current_bpm,
            'cluster_id': cluster_id,
            'cluster_description': cluster_info['cluster_description'],
            'historical_samples': len(historical_data),
            'projections': projections,
            'similar_players': similar_players,
            'cluster_transitions': self._get_cluster_transitions(cluster_id),
            'methodology': 'cluster_weighted_average'
        }

    def _get_cluster_transitions(self, cluster_id: int) -> Dict[str, Any]:
        """
        Get cluster transition probabilities for a given cluster.

        Args:
            cluster_id: Current cluster ID

        Returns:
            Dictionary with transition probabilities and destination clusters
        """
        logger.info(f"Getting cluster transitions for cluster {cluster_id}")

        if self._transition_matrix is None:
            logger.warning("Transition matrix not loaded")
            return {'error': 'Transition matrix not loaded'}

        cluster_key = str(cluster_id)
        if cluster_key not in self._transition_matrix:
            logger.warning(f"Cluster {cluster_id} not found in transition matrix")
            return {'error': f'Cluster {cluster_id} not found in transition matrix'}

        transitions = self._transition_matrix[cluster_key]
        logger.info(f"Found {len(transitions)} transition options for cluster {cluster_id}")

        # Sort by probability and get top destinations
        sorted_transitions = sorted(
            transitions.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Get cluster descriptions for destination clusters
        destination_clusters = []
        for dest_cluster_id, probability in sorted_transitions:
            if dest_cluster_id in self._cluster_descriptions:
                dest_desc = self._cluster_descriptions[dest_cluster_id]
                destination_clusters.append({
                    'cluster_id': int(dest_cluster_id),
                    'probability': round(probability, 3),
                    'name': dest_desc.get('name', f'Cluster {dest_cluster_id}'),
                    'avg_bpm': dest_desc.get('avg_bpm', 0),
                    'avg_usage': dest_desc.get('avg_usage', 0),
                    'avg_height': dest_desc.get('avg_height', 0)
                })

        result = {
            'current_cluster_id': cluster_id,
            'stay_probability': round(transitions.get(cluster_key, 0), 3),
            'destinations': destination_clusters[:10]  # Top 10 destinations
        }

        logger.info(f"Returning cluster transitions with {len(result['destinations'])} destinations")
        return result
    
    def _get_similar_players(
        self,
        target_features: Dict[str, float],
        historical_data: pd.DataFrame,
        limit: int = 5,
        ncaa_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get most similar historical players for context.

        Returns individual records sorted by similarity.

        Args:
            target_features: Target player's features
            historical_data: Historical player data
            limit: Number of similar players to return
            ncaa_id: Target player's ID for checking if enriched

        Returns:
            List of similar player dictionaries
        """
        if historical_data is None or len(historical_data) == 0:
            logger.warning("No historical data available for similar players")
            return []

        logger.info(f"Processing {len(historical_data)} historical records for similar players")

        # Check if player is enriched (has vectors) and use similarity API
        if ncaa_id:
            from app.cache.player_vectors import PLAYER_VECTORS

            ncaa_id_clean = ncaa_id.replace('.0', '')
            logger.info(f"Looking for player {ncaa_id} (cleaned: {ncaa_id_clean}) in PLAYER_VECTORS")

            # PLAYER_VECTORS keys are floats (from roster.ncaa_id), need to check both string and float
            found = False
            if ncaa_id_clean in PLAYER_VECTORS:
                found = True
                search_key = ncaa_id_clean
            else:
                # Try as float
                try:
                    ncaa_id_float = float(ncaa_id_clean)
                    if ncaa_id_float in PLAYER_VECTORS:
                        found = True
                        search_key = ncaa_id_float
                except ValueError:
                    pass

            if found:
                logger.info(f"Player {ncaa_id} is enriched, using similarity API")
                return self._get_similar_players_enriched(search_key, limit)
            else:
                logger.info(f"Player {ncaa_id} not found in PLAYER_VECTORS (size: {len(PLAYER_VECTORS)})")

        # Fallback to basic similarity calculation
        logger.info(f"Player {ncaa_id} is not enriched, using basic similarity")
        return self._get_similar_players_basic(target_features, historical_data, limit)

    def _get_similar_players_enriched(
        self,
        ncaa_id,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get similar players using the vector-based similarity API for enriched players.

        Args:
            ncaa_id: Target player's ID (can be string or float)
            limit: Number of similar players to return

        Returns:
            List of similar player dictionaries
        """
        try:
            from app.cache.player_vectors import PLAYER_VECTORS

            # Convert to float for similarity API
            ncaa_id_float = float(ncaa_id) if isinstance(ncaa_id, str) else ncaa_id

            # Use combined similarity (style + impact) with default weight
            # Only include players with year-over-year data for career trajectory
            results = get_similar_players(
                ncaa_id_float,
                year=None,  # Use latest year
                top_k=limit,
                style_weight=0.7,  # Default blend
                require_yoy_data=True  # Only players with multiple years of data
            )

            similar_players = []
            for player in results.get('combined', []):
                player_key = str(player['AthleteSourceId']).replace('.0', '')
                player_name = self._player_key_to_name.get(player_key, f"Player {player_key}")

                # Get career BPM trajectory from PLAYER_VECTORS
                # PLAYER_VECTORS keys are floats, need to check both string and float
                career_bpm = []
                year_data = None

                if player_key in PLAYER_VECTORS:
                    year_data = PLAYER_VECTORS[player_key]
                else:
                    # Try as float
                    try:
                        player_key_float = float(player_key)
                        if player_key_float in PLAYER_VECTORS:
                            year_data = PLAYER_VECTORS[player_key_float]
                    except ValueError:
                        pass

                if year_data:
                    for year, data in sorted(year_data.items()):
                        bpm = data.get('bpm')
                        if bpm is not None:
                            career_bpm.append({
                                'year': int(year),
                                'bpm': float(bpm)
                            })

                similar_players.append({
                    'player_key': player_key,
                    'player_name': player_name,
                    'similarity': player['similarity'],
                    'year': player.get('year'),
                    'reasons': player.get('reasons', []),
                    'career_bpm': career_bpm
                })

            logger.info(f"Found {len(similar_players)} similar players using enriched similarity")
            return similar_players

        except Exception as e:
            logger.error(f"Error getting enriched similar players: {e}")
            return []

    def _get_similar_players_basic(
        self,
        target_features: Dict[str, float],
        historical_data: pd.DataFrame,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get similar players using basic feature similarity for non-enriched players.

        Args:
            target_features: Target player's features
            historical_data: Historical player data
            limit: Number of similar players to return

        Returns:
            List of similar player dictionaries
        """
        similarities = []

        for _, row in historical_data.iterrows():
            hist_features = {
                'Usage_from': row.get('Usage_from'),
                'PPG_from': row.get('PPG_from'),
                'APG_from': row.get('APG_from'),
                'RPG_from': row.get('RPG_from'),
                'eFG_from': row.get('eFG_from'),
                'TS_per_from': row.get('TS_per_from'),
            }

            similarity = self.calculate_similarity(target_features, hist_features)
            player_key = str(row.get('player_key', ''))

            if not player_key or player_key == 'nan':
                continue

            player_name = self._player_key_to_name.get(player_key, f"Player {player_key}")

            similarities.append({
                'player_key': player_key,
                'player_name': player_name,
                'year_from': int(row.get('year_from', 0)) if pd.notna(row.get('year_from')) else None,
                'year_to': int(row.get('year_to', 0)) if pd.notna(row.get('year_to')) else None,
                'bpm_change': float(row.get('bpm_change', 0)) if pd.notna(row.get('bpm_change')) else None,
                'similarity': round(similarity, 3)
            })

        # Sort by similarity and return top N
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        logger.info(f"Returning {len(similarities[:limit])} similar players")
        return similarities[:limit]


# Singleton instance
_projection_service = None


def get_projection_service() -> ProjectionService:
    """Get the singleton projection service instance."""
    global _projection_service
    if _projection_service is None:
        _projection_service = ProjectionService()
    return _projection_service

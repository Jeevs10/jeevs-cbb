"""Service layer for NIL valuation calculations."""

from typing import List, Optional, Dict, Any, Union
import pandas as pd
import numpy as np
import os

from app.core.data_loader import df
from app.core.player_resolver import get_player_snapshot
from app.core.team_resolver import TEAM_LOOKUP
from app.core.year_utils import normalize_year
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Conference prestige mapping
CONFERENCE_PRESTIGE = {
    # High Major
    "ACC": 1.0,
    "Atlantic Coast Conference": 1.0,
    "Big 12": 1.0,
    "Big 12 Conference": 1.0,
    "Big Ten": 1.0,
    "Big 10": 1.0,
    "B1G": 1.0,
    "Big Ten Conference": 1.0,
    "SEC": 1.0,
    "Southeastern Conference": 1.0,
    "Big East": 1.0,
    "Big East Conference": 1.0,
    "Pac 12": 1.0,
    "Pac 12 Conference": 1.0,
    "West Coast Conference": 1.0,
    # Mid Major
    "AAC": 0.7,
    "American": 0.7,
    "American Athletic Conference": 0.7,
    "A-10": 0.7,
    "Atlantic 10": 0.7,
    "Atlantic 10 Conference": 0.7,
    "Mountain West": 0.7,
    "Mountain West Conference": 0.7,
    "MVC": 0.7,
    "Missouri Valley": 0.7,
    "Missouri Valley Conference": 0.7,
    "WCC": 0.7,
    "West Coast": 0.7,
    "Big West": 0.7,
    "Big West Conference": 0.7,
    "Conference USA": 0.7,
    "CUSA": 0.7,
    # Low Major (default)
    "default": 0.4,
}

# Position mapping for consistent grouping
POSITION_GROUPS = {
    "PG": "Guard",
    "CG": "Guard",
    "WG": "Guard",
    "s-PG": "Guard",
    "WF": "Forward",
    "S-PF": "Forward",
    "PF/C": "Big",
    "C": "Big",
    "F": "Forward",
    "G": "Guard",
}

# Cluster quality mapping based on average BPM per cluster (18 clusters with BPM, OBPM, DBPM, 3p/100 features)
# Updated based on actual cluster averages from player_clusters_unified.csv
CLUSTER_QUALITY = {
    # Star clusters (high BPM) - give these the highest boosts
    2: 1.0,  # Elite Bigs (BPM 5.04) - highest BPM cluster
    0: 0.95,  # High-Usage Guards (BPM 4.79) - second highest
    6: 0.9,  # 3PT Wings (BPM 2.52) - strong shooters
    11: 0.85,  # Stretch Bigs (BPM 2.41) - versatile bigs
    13: 0.8,  # Versatile Forwards (BPM 2.37) - well-rounded forwards
    9: 0.75,  # High-Usage Guards (BPM 2.16) - high usage guards
    12: 0.7,  # Playmakers (BPM 1.95) - playmaking guards
    15: 0.65,  # Rim Protectors (BPM 0.02) - defensive specialists
    3: 0.6,  # Wings (BPM -0.29) - average wings
    14: 0.55,  # Low BPM Guards (BPM -0.41) - below average guards
    8: 0.5,  # 3PT Specialists (BPM -0.80) - specialists
    1: 0.45,  # Low BPM Forwards (BPM -2.10) - role player forwards
    17: 0.4,  # Low BPM Bigs (BPM -2.49) - role player bigs
    5: 0.35,  # Traditional Bigs (BPM -3.21) - low impact bigs
    16: 0.3,  # High-Usage Low BPM (BPM -3.22) - inefficient high usage
    10: 0.25,  # Empty Calorie (BPM -3.44) - low efficiency
    7: 0.2,  # Low BPM Wings (BPM -3.89) - below replacement wings
    4: 0.15,  # Very Low BPM (BPM -6.45) - lowest BPM cluster
    "default": 0.5,
}

# Cluster description mapping based on cluster_descriptions.json
CLUSTER_DESCRIPTIONS = {
    0: "Elite Rim-Protecting Bigs",
    1: "High-Usage Shooting Guards",
    2: "Elite Two-Way High-Usage Bigs",
    3: "Versatile Stretch Wings",
    4: "Low-Impact 3pt Wings",
    5: "Mid-Usage Point Guards",
    6: "Two-Way Wings",
    7: "Low-Impact Stretch Bigs",
    8: "High-Usage Low-Impact Bigs",
    9: "High-Usage Offensive Point Guards",
    10: "High-Volume 3pt Shooters",
    11: "Offensive Scoring Guards",
    12: "Offensive Stretch Fours",
    13: "Low-Usage Two-Way Bigs",
    14: "Offensive 3pt Wings",
    15: "Defensive Rim-Protecting Bigs",
    16: "Low-Usage Defensive Bigs",
    17: "Low-Impact 3pt Wings",
    "default": "Unknown",
}

# NIL valuation weights
NIL_WEIGHTS = {
    "position_rank": 0.25,
    "win_shares": 0.20,
    "bpm_percentile": 0.15,
    "team_success": 0.10,
    "conference_prestige": 0.10,
    "cluster_quality": 0.20,
}

class NilService:
    """Service layer for NIL valuation operations."""
    
    @staticmethod
    def calculate_player_nil(ncaa_id: str, year: Optional[Union[int, str]] = None) -> Dict[str, Any]:
        """Calculate NIL valuation for a specific player."""
        try:
            year = normalize_year(year)
            record = get_player_snapshot(ncaa_id, year)

            if record is None:
                # Check if player exists at all in the dataframe
                from app.core.player_resolver import df
                player_exists = df[df["player_key"] == str(ncaa_id)]
                if player_exists.empty:
                    logger.warning(f"Player not found: {ncaa_id}")
                    raise ValueError("Player not found")
                else:
                    # Player exists but has no data for the requested year
                    # Use default valuation with player info from their most recent year
                    most_recent = player_exists.sort_values("year").iloc[-1]
                    player_name = most_recent.get('player_name') or most_recent.get('Name', 'Unknown')
                    team = most_recent.get('team') or most_recent.get('Team', 'Unknown')
                    position = most_recent.get('Position', 'Unknown')
                    logger.info(f"Player {player_name} has no data for year {year}, using default valuation")
                    return NilService._create_default_valuation(player_name, team, position, ncaa_id, year)

            player_dict = record if isinstance(record, dict) else record.to_dict()

            # Get player data
            player_name = player_dict.get('player_name') or player_dict.get('Name', 'Unknown')
            team = player_dict.get('team') or player_dict.get('Team', 'Unknown')
            position = player_dict.get('Position', 'Unknown')
            conf = player_dict.get('conf') or player_dict.get('Conference') or player_dict.get('conference', '')
            
            # If no conference in player data, try to get it from team data
            if not conf and team != 'Unknown':
                try:
                    from app.core.team_resolver import get_team_snapshot
                    from app.core.team_data_loader import TEAM_LOOKUP
                    
                    # First try by team name
                    conf_found = False
                    for team_id, team_info in TEAM_LOOKUP.items():
                        if team_info.get('School') == team or team_info.get('DisplayName') == team:
                            conf = team_info.get('Conference', '')
                            logger.info(f"Found conference via TEAM_LOOKUP for {team}: {conf}")
                            conf_found = True
                            break
                    
                    # If not found by name, try team_id lookup
                    if not conf_found:
                        team_data = get_team_snapshot(team, year)
                        if team_data:
                            conf = team_data.get('conference') or team_data.get('conf', '')
                            logger.info(f"Found conference via get_team_snapshot for {team}: {conf}")
                except Exception as e:
                    logger.warning(f"Could not get conference from team data for {team}: {str(e)}")
            
            # Get metrics - prioritize Torvik BPM if available
            win_shares = NilService._safe_float(player_dict.get('WinShares Total'))
            bpm = NilService._safe_float(player_dict.get('BPM'))
            # Log BPM source for debugging
            if bpm:
                logger.info(f"Player {player_name}: BPM from 'BPM' field = {bpm}")
            # Try lowercase 'bpm' from Torvik if main BPM is missing or zero
            if not bpm or bpm == 0:
                bpm_torvik = NilService._safe_float(player_dict.get('bpm'))
                if bpm_torvik:
                    logger.info(f"Player {player_name}: BPM from 'bpm' (Torvik) field = {bpm_torvik}")
                    bpm = bpm_torvik
            usage_rate = NilService._safe_float(player_dict.get('Usage') or player_dict.get('usgG1'))
            mpg = NilService._safe_float(player_dict.get('MPG') or player_dict.get('Min_per'))
            games = NilService._safe_float(player_dict.get('Games') or player_dict.get('GP'))
            # Recalculate VORP using formula: [BPM - (-2.0)] * (% possessions) * (team games/33)
            # Calculate % of possessions played using % of total minutes
            # Assume 40 min per game, so % of game = mpg / 40
            possessions_pct = mpg / 40.0 if mpg > 0 else 0
            # Calculate team games (default to 33 if not available)
            team_games = games if games > 0 else 33
            # Recalculate VORP
            vorp = (bpm - (-2.0)) * possessions_pct * (team_games / 33.0)
            
            # Calculate position rank (BPM percentile within archetype cluster)
            position_rank = NilService._calculate_position_rank(player_name, bpm, year)
            
            # Get player's cluster for quality scoring
            player_cluster = NilService._get_player_cluster(player_name)
            cluster_quality = CLUSTER_QUALITY.get(player_cluster, CLUSTER_QUALITY.get("default", 0.5))
            cluster_description = CLUSTER_DESCRIPTIONS.get(player_cluster, CLUSTER_DESCRIPTIONS.get("default", "Unknown"))
            
            # Calculate team success
            team_success = NilService._calculate_team_success(team, year)
            
            # Calculate conference prestige (handle case variations)
            conf_normalized = conf.strip() if conf else ''
            conference_prestige = CONFERENCE_PRESTIGE.get(conf_normalized, CONFERENCE_PRESTIGE.get("default", 0.4))
            # Also try case-insensitive match
            if conference_prestige == 0.4:
                for key, value in CONFERENCE_PRESTIGE.items():
                    if key.lower() == conf_normalized.lower() and key != "default":
                        conference_prestige = value
                        break
            
            # Normalize metrics to 0-100 scale
            win_shares_percentile = NilService._calculate_win_shares_percentile(win_shares, year)
            bpm_percentile = NilService._calculate_bpm_percentile(bpm, year)
            normalized_team_success = team_success  # Already 0-100
            normalized_cluster_quality = cluster_quality * 100  # Convert to 0-100
            
            # Calculate NIL score
            nil_score = (
                (position_rank * NIL_WEIGHTS['position_rank']) +
                (win_shares_percentile * NIL_WEIGHTS['win_shares']) +
                (bpm_percentile * NIL_WEIGHTS['bpm_percentile']) +
                (normalized_team_success * NIL_WEIGHTS['team_success']) +
                (conference_prestige * 100 * NIL_WEIGHTS['conference_prestige']) +
                (normalized_cluster_quality * NIL_WEIGHTS['cluster_quality'])
            )
            
            # Calculate percentiles
            percentile_all = NilService._calculate_percentile_all(nil_score, year)
            percentile_position = NilService._calculate_percentile_position(nil_score, position, year)
            
            # Convert to dollar estimate (rough approximation)
            estimated_value_low, estimated_value_high = NilService._score_to_dollars(nil_score)
            
            # Build breakdown
            breakdown = {
                "position_rank": round(position_rank, 2),
                "win_shares": round(win_shares_percentile, 2),
                "bpm_percentile": round(bpm_percentile, 2),
                "team_success": round(normalized_team_success, 2),
                "conference_prestige": round(conference_prestige * 100, 2),
                "cluster_quality": round(normalized_cluster_quality, 2),
                "total_score": round(nil_score, 2),
            }
            
            valuation = {
                "ncaa_id": str(ncaa_id),
                "player_name": player_name,
                "team": team,
                "position": position,
                "year": str(year),
                "nil_score": round(nil_score, 2),
                "estimated_value_low": estimated_value_low,
                "estimated_value_high": estimated_value_high,
                "percentile_all": round(percentile_all, 2),
                "percentile_position": round(percentile_position, 2),
                "cluster_id": player_cluster,
                "cluster_description": cluster_description,
                "breakdown": breakdown,
            }
            
            logger.info(f"Calculated NIL valuation for {player_name}: ${estimated_value_low:,} - ${estimated_value_high:,}")
            return valuation
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error calculating NIL valuation for {ncaa_id}: {str(e)}")
            raise
    
    @staticmethod
    def calculate_team_nil(team_id: str, year: Optional[Union[int, str]] = None) -> Dict[str, Any]:
        """Calculate NIL valuations for all players on a team."""
        try:
            year = normalize_year(year)
            year_int = int(year) if year else 2026
            
            # Get team roster
            from app.core.team_resolver import get_team_roster
            roster = get_team_roster(team_id, year)
            
            if not roster:
                logger.warning(f"No roster found for team {team_id}")
                raise ValueError("No roster found for this team")
            
            # Get team name
            team_name = roster[0].get('Team', 'Unknown') if roster else 'Unknown'
            
            # Calculate NIL for each player
            valuations = []
            total_team_value = 0
            
            for player in roster:
                # Try AthleteSourceId first (from joined data), then Sourceid (from roster), then Id
                ncaa_id = player.get('AthleteSourceId') or player.get('Sourceid') or player.get('Id')
                player_name = player.get('Name') or f"{player.get('FirstName', '')} {player.get('LastName', '')}"
                player_team = player.get('Team', team_name)
                player_position = player.get('Position', 'Unknown')
                
                if ncaa_id and pd.notna(ncaa_id):
                    try:
                        valuation = NilService.calculate_player_nil(str(ncaa_id), year)
                        valuations.append(valuation)
                        if valuation.get('estimated_value_high'):
                            total_team_value += valuation['estimated_value_high']
                    except Exception as e:
                        # If ID lookup fails, try name matching as fallback
                        year_data = df[df["year"].astype(int) == year_int]
                        matching_players = year_data[
                            (year_data["player_name"].str.lower() == player_name.lower()) |
                            (year_data["Name"].str.lower() == player_name.lower())
                        ]
                        
                        if not matching_players.empty:
                            matching_players = matching_players[
                                (matching_players["team"].str.contains(player_team, case=False, na=False)) |
                                (matching_players["Team"].str.contains(player_team, case=False, na=False))
                            ]
                        
                        if not matching_players.empty:
                            match = matching_players.iloc[0]
                            match_id = match.get('AthleteSourceId')
                            if match_id and pd.notna(match_id):
                                try:
                                    valuation = NilService.calculate_player_nil(str(match_id), year)
                                    valuations.append(valuation)
                                    if valuation.get('estimated_value_high'):
                                        total_team_value += valuation['estimated_value_high']
                                except Exception as e2:
                                    logger.warning(f"Could not calculate NIL for player {player_name} (name match failed): {str(e2)}")
                                    # Add $0 default valuation
                                    valuations.append(NilService._create_default_valuation(player_name, player_team, player_position, str(ncaa_id), year))
                            else:
                                # No match found - add $0 default
                                logger.info(f"No stats data for player {player_name} - using $0 default")
                                valuations.append(NilService._create_default_valuation(player_name, player_team, player_position, str(ncaa_id), year))
                        else:
                            # No match found - add $0 default
                            logger.info(f"No stats data for player {player_name} - using $0 default")
                            valuations.append(NilService._create_default_valuation(player_name, player_team, player_position, str(ncaa_id), year))
                else:
                    # No valid ID - add $0 default
                    logger.info(f"No valid ID for player {player_name} - using $0 default")
                    valuations.append(NilService._create_default_valuation(player_name, player_team, player_position, "unknown", year))
            
            # Sort by NIL score
            valuations.sort(key=lambda x: x.get('nil_score', 0), reverse=True)
            
            return {
                "team_id": str(team_id),
                "team_name": team_name,
                "year": str(year),
                "total_team_value": total_team_value,
                "valuations": valuations,
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error calculating team NIL for {team_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_all_nil_valuations(
        limit: int = 50,
        offset: int = 0,
        sort: str = "nil_score",
        order: str = "desc",
        year: Optional[Union[int, str]] = None,
        conf: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get NIL valuations with filtering and sorting."""
        try:
            year = normalize_year(year)
            
            # Filter data by year
            year_int = int(year) if year else 2026
            data = df[df["year"].astype(int) == year_int].copy()
            
            # Filter by conference
            if conf:
                conference_variations = [conf]
                if conf == "Big 10" or conf == "Big Ten":
                    conference_variations = ["Big 10", "Big Ten"]
                data = data[data["conf"].isin(conference_variations)]
            
            # Calculate NIL for filtered players
            valuations = []
            for _, row in data.iterrows():
                ncaa_id = row.get('AthleteSourceId')
                if ncaa_id and pd.notna(ncaa_id):
                    try:
                        valuation = NilService.calculate_player_nil(str(ncaa_id), year)
                        valuations.append(valuation)
                    except Exception as e:
                        continue
            
            # Sort
            reverse = order == "desc"
            if sort in ["nil_score", "estimated_value_high", "percentile_all"]:
                valuations.sort(key=lambda x: x.get(sort, 0), reverse=reverse)
            
            # Paginate
            total_count = len(valuations)
            filtered_count = len(valuations)
            paginated_valuations = valuations[offset:offset + limit]
            
            return {
                "count": total_count,
                "filtered_count": filtered_count,
                "results": paginated_valuations,
            }
            
        except Exception as e:
            logger.error(f"Error getting NIL valuations: {str(e)}")
            raise
    
    @staticmethod
    def _safe_float(value: Any) -> float:
        """Safely convert a value to float, returning 0 if invalid."""
        try:
            if pd.isna(value):
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def _normalize_metric(value: float, min_val: float, max_val: float) -> float:
        """Normalize a metric to 0-100 scale."""
        if max_val == min_val:
            return 0.0
        normalized = ((value - min_val) / (max_val - min_val)) * 100
        return max(0.0, min(100.0, normalized))
    
    @staticmethod
    def _get_player_cluster(player_name: str) -> int:
        """Get player's cluster ID from player_clusters_unified.csv."""
        try:
            csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'player_clusters_unified.csv')
            if not os.path.exists(csv_path):
                logger.warning(f"Cluster file not found at {csv_path}")
                return "default"
            
            clusters_df = pd.read_csv(csv_path)
            
            # Find player's cluster by name
            player_cluster_row = clusters_df[clusters_df['Name'] == player_name]
            if not player_cluster_row.empty:
                logger.info(f"Found cluster for {player_name}: {int(player_cluster_row.iloc[0]['cluster'])}")
                return int(player_cluster_row.iloc[0]['cluster'])
            
            # Try partial match
            player_cluster_row = clusters_df[clusters_df['Name'].str.contains(player_name, case=False, na=False)]
            if not player_cluster_row.empty:
                logger.info(f"Found cluster for {player_name} via partial match: {int(player_cluster_row.iloc[0]['cluster'])}")
                return int(player_cluster_row.iloc[0]['cluster'])
            
            # Try reversing the name format (Last, First -> First Last)
            if ', ' in player_name:
                parts = player_name.split(', ')
                reversed_name = f"{parts[1]} {parts[0]}"
                player_cluster_row = clusters_df[clusters_df['Name'] == reversed_name]
                if not player_cluster_row.empty:
                    logger.info(f"Found cluster for {player_name} via reversed name {reversed_name}: {int(player_cluster_row.iloc[0]['cluster'])}")
                    return int(player_cluster_row.iloc[0]['cluster'])
                
                # Try partial match on reversed name
                player_cluster_row = clusters_df[clusters_df['Name'].str.contains(reversed_name, case=False, na=False)]
                if not player_cluster_row.empty:
                    logger.info(f"Found cluster for {player_name} via partial reversed name {reversed_name}: {int(player_cluster_row.iloc[0]['cluster'])}")
                    return int(player_cluster_row.iloc[0]['cluster'])
            
            logger.warning(f"Could not find cluster for player {player_name}")
            return "default"
            
        except Exception as e:
            logger.warning(f"Error getting player cluster for {player_name}: {str(e)}")
            return "default"
    
    @staticmethod
    def _calculate_position_rank(player_name: str, bpm: float, year: Union[int, str]) -> float:
        """Calculate player's percentile rank vs same archetype cluster using BPM."""
        try:
            year_int = int(year) if year else 2026
            
            # Load player clusters from unified file
            csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'player_clusters_unified.csv')
            if not os.path.exists(csv_path):
                logger.warning("Player clusters file not found, falling back to position groups")
                return NilService._calculate_position_rank_by_group(bpm, year)
            
            clusters_df = pd.read_csv(csv_path)
            
            # Find player's cluster by name
            player_cluster_row = clusters_df[clusters_df['Name'] == player_name]
            if player_cluster_row.empty:
                # Try partial match (handles "Mara, Aday" vs "Aday Mara")
                player_cluster_row = clusters_df[clusters_df['Name'].str.contains(player_name, case=False, na=False)]
                if player_cluster_row.empty:
                    # Try reversing the name format (if input is "Last, First", try "First Last")
                    if ', ' in player_name:
                        parts = player_name.split(', ')
                        reversed_name = f"{parts[1]} {parts[0]}"
                        player_cluster_row = clusters_df[clusters_df['Name'] == reversed_name]
                    if player_cluster_row.empty:
                        logger.warning(f"Could not find cluster for player {player_name}, falling back to position groups")
                        return NilService._calculate_position_rank_by_group(bpm, year)
            
            player_cluster = player_cluster_row.iloc[0]['cluster']
            
            # Get all players in the same cluster
            cluster_data = clusters_df[clusters_df['cluster'] == player_cluster]
            
            if cluster_data.empty or len(cluster_data) < 5:
                logger.warning(f"Cluster {player_cluster} too small, falling back to position groups")
                return NilService._calculate_position_rank_by_group(bpm, year)
            
            # If player has no BPM data, return 0 percentile
            if bpm == 0:
                return 0.0
            
            # Calculate BPM percentile within cluster
            percentile = (cluster_data['BPM'] < bpm).sum() / len(cluster_data) * 100
            return round(percentile, 2)
            
        except Exception as e:
            logger.warning(f"Error calculating position rank: {str(e)}")
            return NilService._calculate_position_rank_by_group(bpm, year)
    
    @staticmethod
    def _calculate_win_shares_percentile(win_shares: float, year: Union[int, str]) -> float:
        """Calculate player's WinShares percentile vs all players in the same year."""
        try:
            year_int = int(year) if year else 2026
            data = df[df["year"].astype(int) == year_int].copy()
            
            # Filter by meaningful minutes (MPG > 5)
            data = data[data['MPG'].fillna(0) > 5]
            
            if data.empty:
                return 50.0
            
            # If player has no WinShares data, return 0 percentile
            if win_shares == 0 or pd.isna(win_shares):
                return 0.0
            
            # Calculate WinShares percentile vs all players with meaningful minutes
            percentile = (data['WinShares Total'] < win_shares).sum() / len(data) * 100
            return round(percentile, 2)
            
        except Exception as e:
            logger.warning(f"Error calculating WinShares percentile: {str(e)}")
            return 50.0
    
    @staticmethod
    def _calculate_bpm_percentile(bpm: float, year: Union[int, str]) -> float:
        """Calculate player's BPM percentile vs all players in the same year."""
        try:
            year_int = int(year) if year else 2026
            data = df[df["year"].astype(int) == year_int].copy()
            
            # Filter by meaningful minutes (MPG > 5 or Min_per > 5)
            mpg_filter = (data['MPG'].fillna(0) > 5) | (data['Min_per'].fillna(0) > 5)
            data = data[mpg_filter]
            
            if data.empty:
                return 50.0
            
            # If player has no BPM data, return 0 percentile
            if pd.isna(bpm):
                return 0.0
            
            # Filter to only players with BPM data for percentile calculation
            data_with_bpm = data[data['BPM'].notna()]
            
            if data_with_bpm.empty:
                logger.warning(f"No players with BPM data for year {year_int}")
                return 50.0
            
            # Calculate BPM percentile vs all players with meaningful minutes and BPM data
            percentile = (data_with_bpm['BPM'] < bpm).sum() / len(data_with_bpm) * 100
            
            logger.info(f"BPM percentile calculation: BPM={bpm}, percentile={percentile}, total players with BPM={len(data_with_bpm)}")
            
            return round(percentile, 2)
            
        except Exception as e:
            logger.warning(f"Error calculating BPM percentile: {str(e)}")
            return 50.0
    
    @staticmethod
    def _calculate_position_rank_by_group(bpm: float, year: Union[int, str]) -> float:
        """Fallback: Calculate player's percentile rank vs same position group using BPM."""
        try:
            year_int = int(year) if year else 2026
            data = df[df["year"].astype(int) == year_int].copy()
            
            # Filter by meaningful minutes (MPG > 5)
            data = data[data['MPG'].fillna(0) > 5]
            
            if data.empty:
                return 50.0
            
            # If player has no BPM data, return 0 percentile
            if bpm == 0:
                return 0.0
            
            # Calculate BPM percentile vs all players with meaningful minutes
            percentile = (data['BPM'] < bpm).sum() / len(data) * 100
            return round(percentile, 2)
            
        except Exception as e:
            logger.warning(f"Error calculating position rank by group: {str(e)}")
            return 50.0
    
    @staticmethod
    def _calculate_team_success(team: str, year: Union[int, str]) -> float:
        """Calculate team success score (0-100)."""
        try:
            year_int = int(year) if year else 2026
            csv_filename = f"{year_int}-hoop-explorer-teams.csv"
            csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'teams', csv_filename)
            
            if not os.path.exists(csv_path):
                return 50.0  # Default to average
            
            # Load team analytics
            team_df = pd.read_csv(csv_path)
            
            # Find team by name
            team_row = team_df[team_df['team_name'].str.contains(team, case=False, na=False)]
            
            if team_row.empty:
                return 50.0
            
            team_row = team_row.iloc[0]
            
            # Calculate success score based on adj_net only
            adj_net = NilService._safe_float(team_row.get('adj_net'))
            
            # Normalize to 0-100 using adj_net range
            success_score = NilService._normalize_metric(adj_net, -20, 30)
            
            return round(success_score, 2)
            
        except Exception as e:
            logger.warning(f"Error calculating team success: {str(e)}")
            return 50.0
    
    @staticmethod
    def _calculate_percentile_all(nil_score: float, year: Union[int, str]) -> float:
        """Calculate percentile vs all players."""
        try:
            year_int = int(year) if year else 2026
            data = df[df["year"].astype(int) == year_int]
            
            # Rough approximation based on BPM distribution
            # This is a simplified calculation - in production, pre-calculate all NIL scores
            avg_bpm = data['BPM'].mean()
            std_bpm = data['BPM'].std()
            
            # Map NIL score to approximate percentile
            # Assuming NIL score roughly correlates with BPM
            percentile = 50 + (nil_score - 50) * 0.8
            return max(0.0, min(100.0, percentile))
            
        except Exception as e:
            logger.warning(f"Error calculating percentile all: {str(e)}")
            return 50.0
    
    @staticmethod
    def _calculate_percentile_position(nil_score: float, position: str, year: Union[int, str]) -> float:
        """Calculate percentile vs same position."""
        # Simplified - same as all for now
        return NilService._calculate_percentile_all(nil_score, year)
    
    @staticmethod
    def _score_to_dollars(nil_score: float) -> tuple[float, float]:
        """Convert NIL score to dollar estimate range."""
        # Rough approximation based on NIL market data
        # Elite players (95-100 score): $2M - $5M
        # Star players (90-95 score): $1M - $2M
        # Good players (70-90): $100K - $500K
        # Average players (50-70): $10K - $100K
        # Below average (0-50): $0 - $10K
        
        if nil_score >= 95:
            low = 2000000
            high = 2000000 + (nil_score - 95) * 600000  # $600K per point above 95, max $5M at 100
        elif nil_score >= 90:
            low = 1000000
            high = 1000000 + (nil_score - 90) * 200000  # $200K per point above 90, max $2M at 95
        elif nil_score >= 70:
            low = 100000
            high = 500000
        elif nil_score >= 50:
            low = 10000
            high = 100000
        else:
            low = 0
            high = 10000
        
        # Scale by score within range
        factor = nil_score / 100
        low = low * factor
        high = high * factor
        
        return round(low, 0), round(high, 0)
    
    @staticmethod
    def _create_default_valuation(player_name: str, team: str, position: str, ncaa_id: str, year: Union[int, str]) -> Dict[str, Any]:
        """Create a default $0 valuation for players without stats data."""
        return {
            "ncaa_id": str(ncaa_id),
            "player_name": player_name,
            "team": team,
            "position": position,
            "year": str(year),
            "nil_score": 0.0,
            "estimated_value_low": 0,
            "estimated_value_high": 0,
            "percentile_all": 0.0,
            "percentile_position": 0.0,
            "cluster_id": None,
            "cluster_description": "No Data",
            "breakdown": {
                "position_rank": 0.0,
                "win_shares": 0.0,
                "bpm_percentile": 0.0,
                "team_success": 0.0,
                "conference_prestige": 0.0,
                "cluster_quality": 0.0,
                "total_score": 0.0,
            },
        }

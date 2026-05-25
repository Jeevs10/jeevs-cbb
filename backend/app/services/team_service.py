from typing import List, Optional, Dict, Any, Union
import pandas as pd
import numpy as np
import os
import csv

from app.core.team_resolver import get_team_snapshot, get_all_teams, get_team_roster, TEAM_LOOKUP
from app.utils.logger import get_logger

logger = get_logger(__name__)

class TeamService:
    """Service layer for team-related operations."""
    
    @staticmethod
    def get_all_teams_with_analytics(year: Optional[Union[int, str]] = None) -> List[Dict[str, Any]]:
        """Get list of all teams with analytics data.
        
        Args:
            year: Optional year parameter to load specific year's data (e.g., 2025, 2026)
                  Defaults to 2026 if not provided.
        """
        try:
            logger.info(f"Attempting to get all teams with analytics for year: {year or 2026}...")
            teams = get_all_teams()
            
            # Determine which CSV file to load based on year
            year_to_load = int(year) if year and str(year).isdigit() else 2026
            csv_filename = f"{year_to_load}-hoop-explorer-teams.csv"
            csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'teams', csv_filename)
            
            # Fallback to 2026 if the specified year's file doesn't exist
            if not os.path.exists(csv_path):
                logger.warning(f"CSV file for year {year_to_load} not found, falling back to 2026")
                csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'teams', '2026-hoop-explorer-teams.csv')
            
            analytics_map = {}
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    team_id = str(row.get('_id', '')).strip()
                    if not team_id:
                        continue
                    
                    try:
                        analytics_data = {
                            'team_id': team_id,
                            'team_name': row.get('team_name', ''),
                            'conf': row.get('conf', ''),
                            'conf_nick': row.get('conf_nick', ''),
                            'year': int(str(row.get('year', '2026')).split('/')[0]) if '/' in str(row.get('year', '')) else int(row.get('year', '2026')),
                            'wins': float(row.get('wins', 0) or 0),
                            'losses': float(row.get('losses', 0) or 0),
                            'adj_net': float(row.get('adj_net', 0) or 0),
                            'power': float(row.get('power', 0) or 0),
                            'off_adj_ppp': float(row.get('off_adj_ppp', 0) or 0),
                            'def_adj_ppp': float(row.get('def_adj_ppp', 0) or 0),
                            'wab': float(row.get('wab', 0) or 0),
                        }
                        
                        # Add all style columns if they exist
                        # Load all off_style and def_style columns
                        for key in row.keys():
                            if key.startswith('off_style_') or key.startswith('def_style_') or key.startswith('pctile_') or key.startswith('rank_'):
                                if row[key]:
                                    try:
                                        analytics_data[key] = float(row[key])
                                    except (ValueError, TypeError):
                                        pass
                        
                        analytics_map[team_id] = analytics_data
                    except Exception as e:
                        logger.warning(f"Error processing team {team_id}: {str(e)}")
                        continue
            
            # Add analytics data to each team using SourceId mapping
            teams_with_analytics = []
            teams_with_analytics_count = 0
            
            # Calculate power quartiles (include all power values, not just positive)
            power_values = [analytics.get('power', 0) for analytics in analytics_map.values() if analytics.get('power', 0) != 0]
            if power_values:
                power_values_sorted = sorted(power_values)
                n = len(power_values_sorted)
                q1_idx = int(n * 0.25)
                q2_idx = int(n * 0.5)
                q3_idx = int(n * 0.75)
                power_quartiles = {
                    1: power_values_sorted[q1_idx] if q1_idx < n else 0,
                    2: power_values_sorted[q2_idx] if q2_idx < n else 0,
                    3: power_values_sorted[q3_idx] if q3_idx < n else 0,
                    4: power_values_sorted[-1] if n > 0 else 0
                }
                
                # Assign quartile to each team
                for analytics in analytics_map.values():
                    power = analytics.get('power', 0)
                    if power <= power_quartiles[1]:
                        analytics['power_quartile'] = 1
                    elif power <= power_quartiles[2]:
                        analytics['power_quartile'] = 2
                    elif power <= power_quartiles[3]:
                        analytics['power_quartile'] = 3
                    else:
                        analytics['power_quartile'] = 4
            else:
                power_quartiles = {1: 0, 2: 0, 3: 0, 4: 0}
                for analytics in analytics_map.values():
                    analytics['power_quartile'] = 0
            
            for team in teams:
                team_id = team.get('id')
                
                # Get SourceId from TEAM_LOOKUP to match with CSV _id
                source_id = None
                if team_id in TEAM_LOOKUP:
                    source_id = TEAM_LOOKUP[team_id].get('SourceId')
                    if source_id is not None and not pd.isna(source_id):
                        source_id = str(source_id)
                
                if source_id and source_id in analytics_map:
                    # Create a copy of the analytics to avoid reference sharing
                    team['analytics'] = analytics_map[source_id].copy()
                    teams_with_analytics_count += 1
                else:
                    team['analytics'] = None
                teams_with_analytics.append(team)
            
            logger.info(f"Retrieved {len(teams_with_analytics)} teams total, {teams_with_analytics_count} with analytics attached")
            return teams_with_analytics
        except Exception as e:
            logger.error(f"Error retrieving teams with analytics: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def get_all_teams() -> List[Dict[str, Any]]:
        """Get list of all teams with basic info."""
        try:
            logger.info("Attempting to get all teams...")
            teams = get_all_teams()
            logger.info(f"Retrieved {len(teams)} teams")
            return teams
        except Exception as e:
            logger.error(f"Error retrieving teams: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def get_team_by_id(team_id: str, year: Optional[Union[int, str]] = None) -> Dict[str, Any]:
        """Get a specific team by ID."""
        try:
            record = get_team_snapshot(team_id, year)
            
            if record is None:
                logger.warning(f"Team not found: {team_id}")
                raise ValueError("Team not found")
            
            logger.info(f"Retrieved team: {team_id}")
            return record
        except Exception as e:
            logger.error(f"Error retrieving team: {str(e)}")
            raise

    @staticmethod
    def get_available_years_for_team(team_id: str) -> List[int]:
        """Get available years for a specific team."""
        try:
            from app.core.team_data_loader import team_analytics_df
            
            # Convert to string for consistent lookup
            team_id_str = str(team_id)
            
            # Get historical team info to find SourceId
            historical_info = TEAM_LOOKUP.get(team_id_str)
            if not historical_info:
                return []
            
            # Get SourceId for analytics lookup
            source_id = historical_info.get("SourceId")
            if source_id is None or pd.isna(source_id):
                return []
            
            source_id_str = str(source_id)
            
            # Get all years for this team from analytics data
            team_data = team_analytics_df[team_analytics_df["_id"] == source_id_str]
            
            if team_data.empty:
                return []
            
            # Extract unique years
            years = sorted(
                team_data["year"]
                .dropna()
                .astype(int)
                .unique()
                .tolist()
            )
            
            return years
        except Exception as e:
            logger.error(f"Error getting available years for team {team_id}: {str(e)}")
            return []
    
    @staticmethod
    def get_team_roster(team_id: str, year: Optional[Union[int, str]] = None) -> List[Dict[str, Any]]:
        """Get roster for a team."""
        try:
            roster = get_team_roster(team_id, year)
            logger.info(f"Retrieved roster for team {team_id}: {len(roster)} players")
            return roster
        except Exception as e:
            logger.error(f"Error retrieving team roster: {str(e)}")
            raise
    
    @staticmethod
    def calculate_offensive_matchup(current_analytics: Dict[str, Any], opponent_analytics: Dict[str, Any]) -> tuple[float, list[str]]:
        """Calculate offensive matchup score and reasons.
        
        Returns:
            tuple: (score, list of descriptive reasons)
            - Positive score: Our offense exploits their defensive weaknesses
            - Negative score: Their defense neutralizes our offensive strengths
        """
        score = 0.0
        reasons = []
        if not current_analytics or not opponent_analytics:
            return score, reasons
        
        try:
            # Rim attack: our strength vs their weakness (weighted by frequency)
            our_rim_ppp = current_analytics.get('off_style_rim_attack_ppp', 0)
            our_rim_freq = current_analytics.get('off_style_rim_attack_pct', 0) * 100  # Convert decimal to percentage
            their_rim_def_ppp = opponent_analytics.get('def_style_rim_attack_ppp', 0)
            
            if our_rim_ppp > 1.0 and their_rim_def_ppp > 1.0:
                # Weight by frequency - more frequent plays get more weight
                freq_weight = min(our_rim_freq / 20.0, 1.5)  # Cap at 1.5x weight
                rim_score = 0.12 * freq_weight
                score += rim_score
                reasons.append(f"Rim attack ({our_rim_ppp:.2f} PPP, {our_rim_freq:.1f}%) vs rim defense ({their_rim_def_ppp:.2f} PPP allowed)")
            elif our_rim_ppp > 0.8 and their_rim_def_ppp < 0.9:
                freq_weight = min(our_rim_freq / 20.0, 1.5)
                rim_score = -0.12 * freq_weight
                score += rim_score
                reasons.append(f"Rim attack ({our_rim_ppp:.2f} PPP, {our_rim_freq:.1f}%) vs strong rim defense ({their_rim_def_ppp:.2f} PPP allowed)")
            
            # Transition: our strength vs their weakness (weighted by frequency)
            our_trans_ppp = current_analytics.get('off_style_transition_ppp', 0)
            our_trans_freq = current_analytics.get('off_style_transition_pct', 0) * 100  # Convert decimal to percentage
            their_trans_def_ppp = opponent_analytics.get('def_style_transition_ppp', 0)
            
            if our_trans_ppp > 1.1 and their_trans_def_ppp > 1.0:
                freq_weight = min(our_trans_freq / 15.0, 1.5)
                trans_score = 0.1 * freq_weight
                score += trans_score
                reasons.append(f"Strong transition offense ({our_trans_ppp:.2f} PPP, {our_trans_freq:.1f}%) vs weak transition defense ({their_trans_def_ppp:.2f} PPP allowed)")
            elif our_trans_ppp > 0.9 and their_trans_def_ppp < 1.15:
                freq_weight = min(our_trans_freq / 15.0, 1.5)
                trans_score = -0.1 * freq_weight
                score += trans_score
                reasons.append(f"Transition offense ({our_trans_ppp:.2f} PPP, {our_trans_freq:.1f}%) stopped by transition defense ({their_trans_def_ppp:.2f} PPP allowed)")
            
            # Mid range: our strength vs their weakness (weighted by frequency)
            our_mid_ppp = current_analytics.get('off_style_mid_range_ppp', 0)
            our_mid_freq = current_analytics.get('off_style_mid_range_pct', 0) * 100  # Convert decimal to percentage
            their_mid_def_ppp = opponent_analytics.get('def_style_mid_range_ppp', 0)
            
            if our_mid_ppp > 0.8 and their_mid_def_ppp > 0.8:
                freq_weight = min(our_mid_freq / 15.0, 1.5)
                mid_score = 0.08 * freq_weight
                score += mid_score
                reasons.append(f"Mid-range offense ({our_mid_ppp:.2f} PPP, {our_mid_freq:.1f}%) vs mid-range defense ({their_mid_def_ppp:.2f} PPP allowed)")
            elif our_mid_ppp > 0.6 and their_mid_def_ppp < 0.7:
                freq_weight = min(our_mid_freq / 15.0, 1.5)
                mid_score = -0.08 * freq_weight
                score += mid_score
                reasons.append(f"Mid-range offense ({our_mid_ppp:.2f} PPP, {our_mid_freq:.1f}%) vs mid-range defense ({their_mid_def_ppp:.2f} PPP allowed)")
            
            # Turnovers: our turnover rate vs their defensive turnover creation
            our_to_rate = current_analytics.get('off_to', 0) * 100  # Convert decimal to percentage
            their_def_to_rate = opponent_analytics.get('def_to', 0) * 100  # Convert decimal to percentage
            
            # Low offensive TO rate + high defensive TO creation by opponent = bad for us
            if our_to_rate < 15.0 and their_def_to_rate > 18.0:
                score -= 0.06
                reasons.append(f"Careful offense ({our_to_rate:.1f}% TO) vs turnover-forcing defense ({their_def_to_rate:.1f}% TO created)")
            elif our_to_rate > 18.0 and their_def_to_rate < 15.0:
                score += 0.06
                reasons.append(f"Turnover-prone offense ({our_to_rate:.1f}% TO) vs passive defense ({their_def_to_rate:.1f}% TO created)")
            
            # Rebounding: offensive rebounding vs defensive rebounding
            our_oreb_ppp = current_analytics.get('off_style_reb_scramble_ppp', 0)
            our_oreb_freq = current_analytics.get('off_style_reb_scramble_pct', 0) * 100  # Convert decimal to percentage
            their_dreb_ppp = opponent_analytics.get('def_style_reb_scramble_ppp', 0)
            
            if our_oreb_ppp > 1.1 and their_dreb_ppp > 1.1:
                freq_weight = min(our_oreb_freq / 10.0, 1.5)
                reb_score = 0.07 * freq_weight
                score += reb_score
                reasons.append(f"Strong offensive rebounding ({our_oreb_ppp:.2f} PPP, {our_oreb_freq:.1f}%) vs weak defensive rebounding ({their_dreb_ppp:.2f} PPP allowed)")
            elif our_oreb_ppp < 0.9 and their_dreb_ppp < 0.9:
                freq_weight = min(our_oreb_freq / 10.0, 1.5)
                reb_score = -0.07 * freq_weight
                score += reb_score
                reasons.append(f"Weak offensive rebounding ({our_oreb_ppp:.2f} PPP, {our_oreb_freq:.1f}%) vs strong defensive rebounding ({their_dreb_ppp:.2f} PPP allowed)")
                
        except Exception as e:
            logger.warning(f"Error calculating offensive matchup: {str(e)}")
        
        return score, reasons
    
    @staticmethod
    def calculate_defensive_matchup(current_analytics: Dict[str, Any], opponent_analytics: Dict[str, Any]) -> tuple[float, list[str]]:
        """Calculate defensive matchup score and reasons.
        
        Returns:
            tuple: (score, list of descriptive reasons)
            - Positive score: Our defense exploits their offensive weaknesses
            - Negative score: Their offense exploits our defensive weaknesses
        """
        score = 0.0
        reasons = []
        if not current_analytics or not opponent_analytics:
            return score, reasons
        
        try:
            # Rim defense: our strength vs their weakness (weighted by opponent frequency)
            our_rim_def_ppp = current_analytics.get('def_style_rim_attack_ppp', 0)
            their_rim_off_ppp = opponent_analytics.get('off_style_rim_attack_ppp', 0)
            their_rim_freq = opponent_analytics.get('off_style_rim_attack_pct', 0) * 100  # Convert decimal to percentage
            
            if our_rim_def_ppp < 0.9 and their_rim_off_ppp > 1.0:
                # Weight by how frequently opponent runs rim plays
                freq_weight = min(their_rim_freq / 20.0, 1.5)
                rim_score = 0.12 * freq_weight
                score += rim_score
                reasons.append(f"Strong rim defense ({our_rim_def_ppp:.2f} PPP allowed) vs rim-heavy offense ({their_rim_off_ppp:.2f} PPP, {their_rim_freq:.1f}%)")
            elif our_rim_def_ppp > 1.0 and their_rim_off_ppp > 0.9:
                freq_weight = min(their_rim_freq / 20.0, 1.5)
                rim_score = -0.12 * freq_weight
                score += rim_score
                reasons.append(f"Rim defense ({our_rim_def_ppp:.2f} PPP allowed) vs rim attack ({their_rim_off_ppp:.2f} PPP, {their_rim_freq:.1f}%)")
            
            # Transition defense: our strength vs their weakness (weighted by opponent frequency)
            our_trans_def_ppp = current_analytics.get('def_style_transition_ppp', 0)
            their_trans_off_ppp = opponent_analytics.get('off_style_transition_ppp', 0)
            their_trans_freq = opponent_analytics.get('off_style_transition_pct', 0) * 100  # Convert decimal to percentage
            
            if our_trans_def_ppp < 1.15 and their_trans_off_ppp > 1.15:
                freq_weight = min(their_trans_freq / 15.0, 1.5)
                trans_score = 0.1 * freq_weight
                score += trans_score
                reasons.append(f"Strong transition defense ({our_trans_def_ppp:.2f} PPP allowed) vs fast offense ({their_trans_off_ppp:.2f} PPP, {their_trans_freq:.1f}%)")
            elif our_trans_def_ppp > 1.15 and their_trans_off_ppp > 1.05:
                freq_weight = min(their_trans_freq / 15.0, 1.5)
                trans_score = -0.1 * freq_weight
                score += trans_score
                reasons.append(f"Weak transition defense ({our_trans_def_ppp:.2f} PPP allowed) hurt by transition offense ({their_trans_off_ppp:.2f} PPP, {their_trans_freq:.1f}%)")
            
            # Mid range defense: our strength vs their weakness (weighted by opponent frequency)
            our_mid_def_ppp = current_analytics.get('def_style_mid_range_ppp', 0)
            their_mid_off_ppp = opponent_analytics.get('off_style_mid_range_ppp', 0)
            their_mid_freq = opponent_analytics.get('off_style_mid_range_pct', 0) * 100  # Convert decimal to percentage
            
            if our_mid_def_ppp < 0.8 and their_mid_off_ppp > 0.8:
                freq_weight = min(their_mid_freq / 15.0, 1.5)
                mid_score = 0.08 * freq_weight
                score += mid_score
                reasons.append(f"Mid-range defense ({our_mid_def_ppp:.2f} PPP allowed) vs mid-range offense ({their_mid_off_ppp:.2f} PPP, {their_mid_freq:.1f}%)")
            elif our_mid_def_ppp > 0.85 and their_mid_off_ppp > 0.75:
                freq_weight = min(their_mid_freq / 15.0, 1.5)
                mid_score = -0.08 * freq_weight
                score += mid_score
                reasons.append(f"Mid-range defense ({our_mid_def_ppp:.2f} PPP allowed) vs mid-range offense ({their_mid_off_ppp:.2f} PPP, {their_mid_freq:.1f}%)")
            
            # Turnovers: our defensive turnover creation vs their offensive turnover rate
            our_def_to_rate = current_analytics.get('def_to', 0) * 100  # Convert decimal to percentage
            their_off_to_rate = opponent_analytics.get('off_to', 0) * 100  # Convert decimal to percentage
            
            # High defensive TO creation + low offensive TO rate by opponent = good for us
            if our_def_to_rate > 18.0 and their_off_to_rate < 15.0:
                score += 0.06
                reasons.append(f"Turnover-forcing defense ({our_def_to_rate:.1f}% TO created) vs careful offense ({their_off_to_rate:.1f}% TO)")
            elif our_def_to_rate < 15.0 and their_off_to_rate > 18.0:
                score -= 0.06
                reasons.append(f"Passive defense ({our_def_to_rate:.1f}% TO created) vs turnover-prone offense ({their_off_to_rate:.1f}% TO)")
            
            # Rebounding: defensive rebounding vs offensive rebounding
            our_dreb_ppp = current_analytics.get('def_style_reb_scramble_ppp', 0)
            their_oreb_ppp = opponent_analytics.get('off_style_reb_scramble_ppp', 0)
            their_oreb_freq = opponent_analytics.get('off_style_reb_scramble_pct', 0) * 100  # Convert decimal to percentage
            
            if our_dreb_ppp < 0.9 and their_oreb_ppp > 1.1:
                freq_weight = min(their_oreb_freq / 10.0, 1.5)
                reb_score = 0.07 * freq_weight
                score += reb_score
                reasons.append(f"Strong defensive rebounding ({our_dreb_ppp:.2f} PPP allowed) vs offensive rebounding ({their_oreb_ppp:.2f} PPP, {their_oreb_freq:.1f}%)")
            elif our_dreb_ppp > 1.1 and their_oreb_ppp < 0.9:
                freq_weight = min(their_oreb_freq / 10.0, 1.5)
                reb_score = -0.07 * freq_weight
                score += reb_score
                reasons.append(f"Weak defensive rebounding ({our_dreb_ppp:.2f} PPP allowed) vs limited offensive rebounding ({their_oreb_ppp:.2f} PPP, {their_oreb_freq:.1f}%)")
                
        except Exception as e:
            logger.warning(f"Error calculating defensive matchup: {str(e)}")
        
        return score, reasons
    
    @staticmethod
    def calculate_similar_teams(team_id: str, style_weight: float = 0.5, limit: int = 10) -> Dict[str, Any]:
        """Calculate similar teams based on impact and style vectors.
        
        Args:
            team_id: The ID of the team to find similar teams for
            style_weight: Weight for style vector (0-1), where 0 = pure impact, 1 = pure style
            limit: Maximum number of similar teams to return
        
        Returns:
            Dict containing similar teams with similarity scores and reasons
        """
        try:
            logger.info(f"Calculating similar teams for {team_id} with style_weight {style_weight}...")
            
            # Get all teams with analytics
            all_teams = TeamService.get_all_teams_with_analytics()
            
            # Find current team
            current_team = None
            for team in all_teams:
                if str(team.get('id')) == str(team_id):
                    current_team = team
                    break
            
            if not current_team:
                logger.warning(f"Team {team_id} not found")
                raise ValueError(f"Team {team_id} not found")
            
            current_analytics = current_team.get('analytics')
            if not current_analytics:
                logger.warning(f"Team {team_id} has no analytics data")
                return {
                    "current_team": current_team.get('school', 'Unknown'),
                    "similar_teams": [],
                    "message": "No analytics data available for this team"
                }
            
            # Define impact vector fields using percentiles (NetRtg, Power, ORtg, DRTG, SOS)
            impact_fields = [
                'pctile_adj_net',           # Net Rating - most important
                'pctile_power',              # Power rating
                'pctile_off_adj_ppp',        # Offensive efficiency
                'pctile_def_adj_ppp',        # Defensive efficiency
                'pctile_off_adj_opp',        # Offensive strength of schedule
                'pctile_def_adj_opp'         # Defensive strength of schedule
            ]

            # Define style vector fields focusing on shot type frequencies using percentiles
            # Offensive shot type frequencies have weight 3, defensive have weight 2, foul metrics weight 2, other factors weight 1
            # Using frequency (pct) fields, not efficiency (ppp) fields
            # Removed tempo and TO to prevent them from dominating similarity results
            style_fields_with_weights = [
                # Offensive shot type frequencies (how teams play) - highest weight
                ('pctile_off_style_rim_attack_pct', 3),
                ('pctile_off_style_transition_pct', 3),
                ('pctile_off_style_mid_range_pct', 3),
                ('pctile_off_style_post_up_pct', 3),
                ('pctile_off_style_perimeter_cut_pct', 3),
                ('pctile_off_style_big_cut_roll_pct', 3),
                ('pctile_off_style_pick_pop_pct', 3),
                ('pctile_off_style_dribble_jumper_pct', 3),
                ('pctile_off_style_attack_kick_pct', 3),
                ('pctile_off_style_high_low_pct', 3),
                # Defensive shot type frequencies (how opponents play against them) - medium weight
                ('pctile_def_style_rim_attack_pct', 2),
                ('pctile_def_style_transition_pct', 2),
                ('pctile_def_style_mid_range_pct', 2),
                ('pctile_def_style_post_up_pct', 2),
                ('pctile_def_style_perimeter_cut_pct', 2),
                ('pctile_def_style_big_cut_roll_pct', 2),
                ('pctile_def_style_pick_pop_pct', 2),
                ('pctile_def_style_dribble_jumper_pct', 2),
                ('pctile_def_style_attack_kick_pct', 2),
                ('pctile_def_style_high_low_pct', 2),
                # Foul metrics - medium weight
                ('pctile_off_ftr', 2), ('pctile_def_ftr', 2),
                ('pctile_off_ft', 2), ('pctile_def_ft', 2),
                ('pctile_off_scramble_ftr', 2), ('pctile_def_scramble_ftr', 2),
                ('pctile_off_trans_ftr', 2), ('pctile_def_trans_ftr', 2),
                # Rebounding - low weight
                ('pctile_off_orb', 1), ('pctile_def_orb', 1),
                # Efficiency - low weight
                ('pctile_off_efg', 1), ('pctile_def_efg', 1)
            ]

            # Extract field names and weights separately
            style_fields = [field for field, weight in style_fields_with_weights]
            style_weights = [weight for field, weight in style_fields_with_weights]

            # Extract current team's vectors
            current_impact_vector = [current_analytics.get(field, 0) for field in impact_fields]
            # Apply weights to style vector by repeating fields based on weight
            current_style_vector = []
            for field, weight in style_fields_with_weights:
                value = current_analytics.get(field, 0)
                # Add the value 'weight' times to give it more influence
                for _ in range(weight):
                    current_style_vector.append(value)
            
            # Calculate similarity for each other team
            similarities = []
            for team in all_teams:
                if str(team.get('id')) == str(team_id):
                    continue
                
                team_analytics = team.get('analytics')
                if not team_analytics:
                    continue
                
                # Extract team's vectors
                team_impact_vector = [team_analytics.get(field, 0) for field in impact_fields]
                # Apply weights to style vector by repeating fields based on weight
                team_style_vector = []
                for field, weight in style_fields_with_weights:
                    value = team_analytics.get(field, 0)
                    # Add the value 'weight' times to give it more influence
                    for _ in range(weight):
                        team_style_vector.append(value)
                
                # Calculate impact similarity (using Euclidean distance - better for magnitude differences)
                impact_sim = TeamService._euclidean_similarity(current_impact_vector, team_impact_vector)
                
                # Calculate style similarity (using cosine similarity)
                style_sim = TeamService._cosine_similarity(current_style_vector, team_style_vector)
                
                # Combined similarity based on weight
                impact_weight = 1 - style_weight
                combined_sim = (impact_sim * impact_weight) + (style_sim * style_weight)
                
                # Find key similar features and differences - separate for impact and style
                impact_similar_features = []
                impact_differences = []
                style_similar_features = []
                style_differences = []
                
                # Compare impact fields for top similar/different features (using percentiles 0-100)
                for field in impact_fields:
                    current_val = current_analytics.get(field, 0)
                    team_val = team_analytics.get(field, 0)
                    delta = abs(current_val - team_val)
                    
                    if delta < 10.0:  # Very similar for impact percentiles (within 10 percentile points)
                        impact_similar_features.append({"feature": field, "delta": delta})
                    elif delta > 30.0:  # Quite different for impact percentiles (more than 30 percentile points)
                        impact_differences.append({"feature": field, "delta": delta})
                
                # Compare style fields for top similar/different features (using percentiles 0-100)
                for field in style_fields:
                    current_val = current_analytics.get(field, 0)
                    team_val = team_analytics.get(field, 0)
                    delta = abs(current_val - team_val)
                    
                    if delta < 10.0:  # Very similar for style percentiles (within 10 percentile points)
                        style_similar_features.append({"feature": field, "delta": delta})
                    elif delta > 30.0:  # Quite different for style percentiles (more than 30 percentile points)
                        style_differences.append({"feature": field, "delta": delta})
                
                # Sort by delta and take top 3
                impact_similar_features.sort(key=lambda x: x["delta"])
                impact_differences.sort(key=lambda x: x["delta"], reverse=True)
                style_similar_features.sort(key=lambda x: x["delta"])
                style_differences.sort(key=lambda x: x["delta"], reverse=True)
                
                similarities.append({
                    "team": team.get('school', 'Unknown'),
                    "team_id": team.get('id'),
                    "similarity": combined_sim,
                    "impact_similarity": impact_sim,
                    "style_similarity": style_sim,
                    "impact_reasons": impact_similar_features[:3],
                    "impact_differences": impact_differences[:3],
                    "style_reasons": style_similar_features[:3],
                    "style_differences": style_differences[:3]
                })
            
            # Sort by similarity and take top results
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            similarities = similarities[:limit]
            
            return {
                "current_team": current_team.get('school', 'Unknown'),
                "similar_teams": similarities,
                "style_weight": style_weight
            }
        except Exception as e:
            logger.error(f"Error calculating similar teams: {str(e)}")
            raise
    
    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            import numpy as np
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception:
            # Fallback to simple Euclidean distance if numpy fails
            try:
                import math
                dot_product = sum(a * b for a, b in zip(vec1, vec2))
                norm1 = math.sqrt(sum(a * a for a in vec1))
                norm2 = math.sqrt(sum(b * b for b in vec2))
                
                if norm1 == 0 or norm2 == 0:
                    return 0.0
                
                return dot_product / (norm1 * norm2)
            except Exception:
                return 0.0
    
    @staticmethod
    def _euclidean_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate similarity using Euclidean distance (converted to similarity score)."""
        try:
            import numpy as np
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            # Calculate Euclidean distance
            distance = np.linalg.norm(vec1 - vec2)
            
            # Convert distance to similarity (closer = more similar)
            # Max possible distance for 6 dimensions with values 0-100 is sqrt(6 * 100^2) ≈ 245
            max_distance = 245
            similarity = 1 - (distance / max_distance)
            
            return max(0.0, similarity)
        except Exception:
            # Fallback to simple calculation
            try:
                import math
                distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))
                max_distance = 245
                similarity = 1 - (distance / max_distance)
                return max(0.0, similarity)
            except Exception:
                return 0.0

    @staticmethod
    def calculate_single_matchup(team_id: str, opponent_id: str) -> Dict[str, Any]:
        """Calculate matchup between two specific teams.
        
        Args:
            team_id: The ID of the team to calculate matchup for
            opponent_id: The ID of the opponent team
        
        Returns:
            Dict containing matchup details
        """
        try:
            logger.info(f"Calculating matchup between {team_id} and {opponent_id}...")
            
            # Get all teams with analytics
            all_teams = TeamService.get_all_teams_with_analytics()
            
            # Find current team
            current_team = None
            for team in all_teams:
                if str(team.get('id')) == str(team_id):
                    current_team = team
                    break
            
            if not current_team:
                logger.warning(f"Team {team_id} not found")
                raise ValueError(f"Team {team_id} not found")
            
            # Find opponent team
            opponent_team = None
            for team in all_teams:
                if str(team.get('id')) == str(opponent_id):
                    opponent_team = team
                    break
            
            if not opponent_team:
                logger.warning(f"Opponent team {opponent_id} not found")
                raise ValueError(f"Opponent team {opponent_id} not found")
            
            current_analytics = current_team.get('analytics')
            opponent_analytics = opponent_team.get('analytics')
            
            if not current_analytics or not opponent_analytics:
                logger.warning(f"Missing analytics data for matchup calculation")
                raise ValueError("Missing analytics data for matchup calculation")
            
            # Calculate offensive and defensive matchups
            offensive_score, offensive_reasons = TeamService.calculate_offensive_matchup(
                current_analytics, opponent_analytics
            )
            defensive_score, defensive_reasons = TeamService.calculate_defensive_matchup(
                current_analytics, opponent_analytics
            )
            
            overall_score = offensive_score + defensive_score
            
            return {
                "team": opponent_team.get('school', 'Unknown'),
                "team_id": opponent_id,
                "overall_score": overall_score,
                "offensive_score": offensive_score,
                "defensive_score": defensive_score,
                "offensive_reasons": offensive_reasons,
                "defensive_reasons": defensive_reasons
            }
        except Exception as e:
            logger.error(f"Error calculating single matchup: {str(e)}")
            raise

    @staticmethod
    def calculate_team_matchups(team_id: str, threshold: float = 0.05, filter_type: str = "all") -> Dict[str, Any]:
        """Calculate matchups for a team based on style analytics.
        
        Args:
            team_id: The ID of the team to calculate matchups for
            threshold: Score threshold for including matchups
            filter_type: Filter type for matchups - 'all', 'conference', 'quartile'
        
        Returns two categories:
        - most_effective_against: Teams we match up well against (positive overall score)
        - least_effective_against: Teams we match up poorly against (negative overall score)
        
        Each matchup includes:
        - overall_score: Combined offensive and defensive advantage
        - offensive_score: How well our offense matches their defense
        - defensive_score: How well our defense matches their offense
        - offensive_reasons: Detailed explanation of offensive matchup
        - defensive_reasons: Detailed explanation of defensive matchup
        """
        try:
            logger.info(f"Calculating matchups for team {team_id} with threshold {threshold}...")
            
            # Get all teams with analytics
            all_teams = TeamService.get_all_teams_with_analytics()
            
            # Find current team
            current_team = None
            for team in all_teams:
                if str(team.get('id')) == str(team_id):
                    current_team = team
                    break
            
            if not current_team:
                logger.warning(f"Team {team_id} not found")
                raise ValueError(f"Team {team_id} not found")
            
            current_analytics = current_team.get('analytics')
            if not current_analytics:
                logger.warning(f"Team {team_id} has no analytics data")
                return {
                    "current_team": current_team.get('school', 'Unknown'),
                    "most_effective_against": [],
                    "least_effective_against": [],
                    "filter_type": filter_type,
                    "message": "No analytics data available for this team"
                }
            
            # Get filter criteria based on filter_type
            current_conf = current_analytics.get('conf', '')
            current_quartile = current_analytics.get('power_quartile', 0)
            
            logger.info(f"Filter type: {filter_type}, Conference: {current_conf}, Quartile: {current_quartile}")
            
            # Calculate matchups
            most_effective = []
            least_effective = []
            teams_with_analytics = 0
            teams_evaluated = 0
            score_distribution = []
            
            for team in all_teams:
                if str(team.get('id')) == str(team_id):
                    continue
                
                opponent_analytics = team.get('analytics')
                if not opponent_analytics:
                    continue
                
                # Apply filter based on filter_type
                if filter_type == "conference":
                    opponent_conf = opponent_analytics.get('conf', '')
                    if opponent_conf != current_conf:
                        continue
                elif filter_type == "quartile":
                    opponent_quartile = opponent_analytics.get('power_quartile', 0)
                    if opponent_quartile != current_quartile:
                        continue
                # 'all' includes all teams
                
                teams_with_analytics += 1
                teams_evaluated += 1
                
                offense_score, offense_reasons = TeamService.calculate_offensive_matchup(current_analytics, opponent_analytics)
                defense_score, defense_reasons = TeamService.calculate_defensive_matchup(current_analytics, opponent_analytics)
                total_score = offense_score + defense_score
                
                score_distribution.append(total_score)
                
                matchup_data = {
                    "team": team.get('school', 'Unknown'),
                    "team_id": team.get('id'),
                    "overall_score": total_score,
                    "offensive_score": offense_score,
                    "defensive_score": defense_score,
                    "offensive_reasons": offense_reasons,
                    "defensive_reasons": defense_reasons
                }
                
                if total_score > threshold:
                    most_effective.append(matchup_data)
                elif total_score < -threshold:
                    least_effective.append(matchup_data)
            
            if score_distribution:
                logger.info(f"Score distribution - Min: {min(score_distribution):.3f}, Max: {max(score_distribution):.3f}, Avg: {sum(score_distribution)/len(score_distribution):.3f}")
                logger.info(f"Scores > {threshold}: {len([s for s in score_distribution if s > threshold])}, Scores < -{threshold}: {len([s for s in score_distribution if s < -threshold])}")
            
            # Sort by overall score and get top 5 of each type
            most_effective = sorted(most_effective, key=lambda x: x['overall_score'], reverse=True)[:5]
            least_effective = sorted(least_effective, key=lambda x: x['overall_score'])[:5]  # Most negative first
            
            logger.info(f"Calculated matchups for {current_team.get('school', 'Unknown')} (filter: {filter_type}): {len(most_effective)} most effective, {len(least_effective)} least effective (evaluated {teams_evaluated} teams)")
            
            return {
                "current_team": current_team.get('school', 'Unknown'),
                "current_team_id": current_team.get('id'),
                "teams_with_analytics": teams_with_analytics,
                "teams_evaluated": teams_evaluated,
                "filter_type": filter_type,
                "threshold": threshold,
                "most_effective_against": most_effective,
                "least_effective_against": least_effective
            }
        except Exception as e:
            logger.error(f"Error calculating matchups: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def get_team_analytics_debug(team_id: str) -> Dict[str, Any]:
        """Get analytics debug info for a team."""
        try:
            all_teams = TeamService.get_all_teams_with_analytics()
            
            current_team = None
            for team in all_teams:
                if str(team.get('id')) == str(team_id):
                    current_team = team
                    break
            
            if not current_team:
                raise ValueError(f"Team {team_id} not found")
            
            analytics = current_team.get('analytics')
            
            # Get sample analytics from another team for comparison
            sample_analytics = None
            for team in all_teams:
                if str(team.get('id')) != str(team_id) and team.get('analytics'):
                    sample_analytics = team.get('analytics')
                    sample_team = team.get('school', 'Unknown')
                    break
            
            return {
                "team_id": team_id,
                "school": current_team.get('school', 'Unknown'),
                "has_analytics": analytics is not None,
                "analytics": analytics if analytics else None,
                "sample_comparison": {
                    "team": sample_team if sample_analytics else None,
                    "analytics": sample_analytics
                } if sample_analytics else None
            }
        except Exception as e:
            logger.error(f"Error getting analytics debug: {str(e)}", exc_info=True)
            raise

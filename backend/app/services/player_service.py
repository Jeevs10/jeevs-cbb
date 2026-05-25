from typing import List, Optional, Dict, Any, Union
import pandas as pd
import numpy as np
import os

from app.core.data_loader import df
from app.core.player_resolver import get_player_snapshot, get_player_history
from app.core.year_utils import normalize_year
from app.models.schemas import PlayerQueryParams, PlayerListResponse, PlayerResponse
from app.utils.logger import get_logger
from app.utils.bpm_calculator import get_bpm_calculator

logger = get_logger(__name__)

# Percentage columns that need to be converted
PCT_COLS = [
    "off_usage",
    "off_assist", 
    "off_to",
    "off_orb",
    "def_orb",
    "off_ftr",
    "def_stl",
    "def_blk",
    "off_threepr"
]

# Sortable columns set
SORTABLE_COLUMNS = set(df.columns) | {"PPG", "APG", "RPG", "SPG", "BPG", "MPG", "BPM"}

class PlayerService:
    """Service layer for player-related operations."""
    
    @staticmethod
    def get_players(params: PlayerQueryParams) -> PlayerListResponse:
        """Get players with filtering, sorting, and pagination."""
        try:
            year = normalize_year(params.year)

            # Apply filters first to reduce dataset size before copying
            filtered_data = PlayerService._apply_filters(df, params, year)

            # Only copy the filtered data (much smaller than full dataset)
            data = filtered_data.copy()

            # Calculate filtered count before any transformations
            total_filtered = len(data)

            # Check if sorting by a derived stat - if so, calculate it before sorting
            derived_stats = ["PPG", "APG", "RPG", "SPG", "BPG", "MPG", "BPM"]
            if params.sort in derived_stats:
                # Only clean and calculate the specific derived stat needed for sorting
                data = PlayerService._clean_numeric_data(data)
                data = PlayerService._map_basic_fields(data)
                data = PlayerService._calculate_derived_stats(data)

            # Apply sorting
            data = PlayerService._apply_sorting(data, params.sort, params.order)

            # Apply pagination BEFORE expensive transformations
            paginated_data = PlayerService._apply_pagination(data, params.limit, params.offset)

            # Only do remaining transformations on paginated data if not already done
            if params.sort not in derived_stats:
                paginated_data = PlayerService._clean_numeric_data(paginated_data)
                paginated_data = PlayerService._convert_percentages(paginated_data)
                paginated_data = PlayerService._map_basic_fields(paginated_data)
                paginated_data = PlayerService._calculate_derived_stats(paginated_data)
            else:
                # Still need to convert percentages if not done
                paginated_data = PlayerService._convert_percentages(paginated_data)

            # Convert to dict and handle NaN values, ensuring required fields are not None
            results = paginated_data.replace({np.nan: None}).to_dict(orient="records")

            # Ensure required fields are not None for basic players
            for result in results:
                if result.get('data_tier') == 'basic':
                    # For basic players, ensure player_name and team are not None
                    if not result.get('player_name'):
                        result['player_name'] = result.get('Name') or f"Player {result.get('AthleteSourceId')}"
                    if not result.get('team'):
                        result['team'] = result.get('Team') or "Unknown Team"

            logger.info(f"Retrieved {len(results)} players (filtered from {total_filtered} of {len(df)} total)")

            return PlayerListResponse(
                count=len(df),
                filtered_count=total_filtered,
                results=results
            )

        except Exception as e:
            logger.error(f"Error retrieving players: {str(e)}")
            raise
    
    @staticmethod
    def get_player_by_id(ncaa_id: str, year: Optional[Union[int, str]] = None) -> PlayerResponse:
        """Get a specific player by ID."""
        try:
            year = normalize_year(year)
            record = get_player_snapshot(ncaa_id, year)
            history = get_player_history(ncaa_id)
            
            if record is None:
                logger.warning(f"Player not found: {ncaa_id}")
                raise ValueError("Player not found")
            
            # Get available years
            years = sorted(
                history["year"]
                .dropna()
                .astype(int)
                .unique()
                .tolist()
            )
            
            # Convert player data to dict and ensure correct field names
            player_dict = record if isinstance(record, dict) else record.to_dict()
            
            # Add data tier information for frontend
            data_tier = player_dict.get('data_tier', 'basic')
            player_dict['data_tier'] = data_tier
            
            # Map basic player fields to expected API field names
            if data_tier == 'basic':
                import numpy as np
                # Handle player_name mapping
                player_name_val = player_dict.get('player_name')
                if player_name_val is None or (isinstance(player_name_val, float) and np.isnan(player_name_val)):
                    if player_dict.get('Name') is not None:
                        player_dict['player_name'] = player_dict['Name']
                
                # Handle team mapping
                team_val = player_dict.get('team')
                if team_val is None or (isinstance(team_val, float) and np.isnan(team_val)):
                    if player_dict.get('Team') is not None:
                        player_dict['team'] = player_dict['Team']
                
                # Handle Position mapping - ensure Position is preserved
                if 'Position' in player_dict:
                    position_val = player_dict.get('Position')
                    if isinstance(position_val, float) and np.isnan(position_val):
                        player_dict['Position'] = None
                elif 'Position' not in player_dict and 'Position' in record if hasattr(record, 'to_dict') else {}:
                    player_dict['Position'] = record.get('Position') if hasattr(record, 'get') else record['Position']
            
            # For basic data, add missing advanced fields as None for frontend consistency
            if data_tier == 'basic':
                basic_to_enriched_fields = [
                    'adj_rapm_margin', 'off_efg', 'off_usage', 'off_assist',
                    'def_stl', 'def_blk', 'off_ftr', 'off_threepr',
                    'off_twoprimr', 'off_twopmidr', 'off_orb', 'def_orb',
                    'off_reb', 'def_reb', 'off_style_rim_attack_pct',
                    'off_style_perimeter_sniper_pct', 'off_style_dribble_jumper_pct'
                ]
                for field in basic_to_enriched_fields:
                    if field not in player_dict:
                        player_dict[field] = None
            
            # BPM is pre-calculated in CSV for basic players
            # For enriched players, BPM is not calculated due to missing feature columns
            
            logger.info(f"Before nesting - roster keys: {[k for k in player_dict.keys() if 'roster' in k]}")
            # Apply nesting for fields with dot notation
            player_dict = PlayerService._nest_player_data(player_dict)
            logger.info(f"After nesting - roster object present: {'roster' in player_dict}")
            
            logger.info(f"Retrieved player: {ncaa_id} for year: {year} (data tier: {data_tier})")
            
            return PlayerResponse(
                player=player_dict,
                available_years=years
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving player {ncaa_id}: {str(e)}")
            raise
    
    @staticmethod
    def _calculate_derived_stats(data: pd.DataFrame) -> pd.DataFrame:
        """Calculate derived stats (PPG, APG, RPG, SPG, BPG, MPG, BPM) for all players."""
        # Calculate derived stats for all players (both basic and enriched)
        games = pd.to_numeric(data['Games'], errors='coerce')
        games_safe = games.where(games > 0, np.nan)
        
        # Calculate all derived stats at once to avoid DataFrame fragmentation
        new_columns = {}
        
        # PPG = Points / Games
        if 'Points' in data.columns:
            points = pd.to_numeric(data['Points'], errors='coerce')
            new_columns['PPG'] = points / games_safe
        
        # APG = Assists / Games
        if 'Assists' in data.columns:
            assists = pd.to_numeric(data['Assists'], errors='coerce')
            new_columns['APG'] = assists / games_safe
        
        # RPG = Rebounds Total / Games
        if 'Rebounds Total' in data.columns:
            rebounds = pd.to_numeric(data['Rebounds Total'], errors='coerce')
            new_columns['RPG'] = rebounds / games_safe
        
        # SPG = Steals / Games
        if 'Steals' in data.columns:
            steals = pd.to_numeric(data['Steals'], errors='coerce')
            new_columns['SPG'] = steals / games_safe
        
        # BPG = Blocks / Games
        if 'Blocks' in data.columns:
            blocks = pd.to_numeric(data['Blocks'], errors='coerce')
            new_columns['BPG'] = blocks / games_safe
        
        # MPG = Minutes / Games
        if 'Minutes' in data.columns:
            minutes = pd.to_numeric(data['Minutes'], errors='coerce')
            new_columns['MPG'] = minutes / games_safe
        
        # Add all columns at once using assign to avoid fragmentation
        if new_columns:
            data = data.assign(**new_columns)
        
        # BPM is now pre-calculated and stored in the CSV file
        # No runtime calculation needed for performance
        
        return data
    
    @staticmethod
    def _calculate_bpm(data: pd.DataFrame) -> pd.DataFrame:
        """Calculate BPM for all players in the DataFrame using ridge regression."""
        try:
            # Try to load trained model
            calculator = get_bpm_calculator()
            model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'bpm_model.joblib')
            
            if os.path.exists(model_path) and not calculator.is_trained:
                calculator.load_model(model_path)
                logger.info(f"Loaded trained BPM model from {model_path}")
            
            # Calculate BPM using the BPMCalculator utility
            data = calculator.predict_bpm_for_dataframe(data)
            logger.info(f"Calculated BPM for {len(data)} players")
        except Exception as e:
            logger.error(f"Error calculating BPM: {str(e)}")
            # Add BPM column with None values if calculation fails
            data['BPM'] = None
        return data
    
    @staticmethod
    def _map_basic_fields(data: pd.DataFrame) -> pd.DataFrame:
        """Map basic player fields to match API field names."""
        # For basic players, map Name->player_name and Team->team
        basic_mask = data['data_tier'] == 'basic'
        if basic_mask.any():
            data.loc[basic_mask, 'player_name'] = data.loc[basic_mask, 'Name']
            data.loc[basic_mask, 'team'] = data.loc[basic_mask, 'Team']
            data.loc[basic_mask, 'Position'] = data.loc[basic_mask, 'Position']
        
        return data
    
    @staticmethod
    def _apply_filters(data: pd.DataFrame, params: PlayerQueryParams, year: Optional[Union[int, str]]) -> pd.DataFrame:
        """Apply filters to the dataset."""
        # Year filter - ensure year column is numeric before comparison
        if isinstance(year, int):
            data = data[data["year"].astype(int) == year]
        
        # Data tier filter
        if params.dataTier:
            data = data[data["data_tier"] == params.dataTier]
        
        # Conference filter with name normalization
        if params.conf:
            # Map conference name variations to standard names
            conference_mapping = {
                "Big 10": ["Big 10", "Big Ten"],
                "Big Ten": ["Big 10", "Big Ten"],
                "Big 12": ["Big 12"],
                "SEC": ["SEC"],
                "ACC": ["ACC"],
                "Big East": ["Big East"],
                "AAC": ["AAC", "American"],
                "American": ["AAC", "American"],
                "A-10": ["A-10", "Atlantic 10"],
                "Atlantic 10": ["A-10", "Atlantic 10"],
                "Mountain West": ["Mountain West"],
                "MVC": ["MVC", "Missouri Valley"],
                "Missouri Valley": ["MVC", "Missouri Valley"],
                "WCC": ["WCC", "West Coast"],
                "West Coast": ["WCC", "West Coast"],
                "Pac-12": ["Pac-12", "Pac 12"],
                "Pac 12": ["Pac-12", "Pac 12"],
                "Conference USA": ["Conference USA", "CUSA"],
                "CUSA": ["Conference USA", "CUSA"],
                "MAC": ["MAC"],
                "Big Sky": ["Big Sky"],
                "WAC": ["WAC"],
                "Horizon": ["Horizon"],
                "Ivy": ["Ivy"],
                "America East": ["America East"],
                "CAA": ["CAA"],
                "Summit": ["Summit"],
                "Ohio Valley": ["Ohio Valley"],
                "Southern": ["Southern"],
                "Sun Belt": ["Sun Belt"],
                "SWAC": ["SWAC"],
                "MEAC": ["MEAC"],
                "Northeast": ["Northeast"],
            }
            
            # Get all variations for the selected conference
            conference_variations = conference_mapping.get(params.conf, [params.conf])
            data = data[data["conf"].isin(conference_variations)]
        
        # D1 only filter - only show players with Conference field populated
        if params.d1Only:
            data = data[data["conf"].notna() & (data["conf"] != "")]
        
        # High Major only filter - only show players from Big 12, SEC, ACC, Big 10, Big East
        if params.highMajorOnly:
            high_major_conferences = ["Big 12", "Big Ten", "Big 10", "B1G", "SEC", "ACC", "Big East"]
            data = data[data["conf"].isin(high_major_conferences)]
        
        # Search filter
        if params.search and params.search.strip():
            q = params.search.strip().lower()
            
            # Remove commas and extra spaces
            q_clean = q.replace(',', ' ').strip()
            
            # Split into parts for name matching
            parts = [p for p in q_clean.split() if p]
            
            # Use pre-computed lowercase columns for efficient search
            if '_player_name_lc' in data.columns:
                # Try exact match first
                mask = (
                    data["_player_name_lc"].str.contains(q_clean, na=False) |
                    data["_team_lc"].str.contains(q_clean, na=False) |
                    data["_ncaa_id_lc"].str.contains(q_clean, na=False)
                )
                
                # If no results and we have name parts, try different orderings
                if not mask.any() and len(parts) >= 2:
                    # Try "Last First" format (database format)
                    last_first = f"{parts[-1]} {parts[0]}"
                    mask = (
                        data["_player_name_lc"].str.contains(last_first, na=False) |
                        data["_player_name_lc"].str.contains(q_clean, na=False)
                    )
                    
                    # Try matching individual parts
                    if not mask.any():
                        part_masks = []
                        for part in parts:
                            part_masks.append(data["_player_name_lc"].str.contains(part, na=False))
                        mask = part_masks[0]
                        for part_mask in part_masks[1:]:
                            mask = mask & part_mask
            else:
                # Fallback: compute lowercase on the fly
                mask = (
                    data["player_name"].str.lower().str.contains(q_clean, na=False) |
                    data["team"].str.lower().str.contains(q_clean, na=False) |
                    data["player_key"].str.lower().str.contains(q_clean, na=False)
                )
                
                # If no results and we have name parts, try different orderings
                if not mask.any() and len(parts) >= 2:
                    # Try "Last First" format (database format)
                    last_first = f"{parts[-1]} {parts[0]}"
                    mask = (
                        data["player_name"].str.lower().str.contains(last_first, na=False) |
                        data["player_name"].str.lower().str.contains(q_clean, na=False)
                    )
                    
                    # Try matching individual parts
                    if not mask.any():
                        part_masks = []
                        for part in parts:
                            part_masks.append(data["player_name"].str.lower().str.contains(part, na=False))
                        mask = part_masks[0]
                        for part_mask in part_masks[1:]:
                            mask = mask & part_mask
            
            data = data[mask]
        
        return data
    
    @staticmethod
    def _clean_numeric_data(data: pd.DataFrame) -> pd.DataFrame:
        """Clean numeric data columns."""
        # Only convert columns that are actually numeric to avoid unnecessary processing
        # Use errors='coerce' to convert non-numeric values to NaN
        for col in data.columns:
            if col not in ["player_name", "roster.ncaa_id", "team", "conf", "Position"]:
                data[col] = pd.to_numeric(data[col], errors="coerce")

        return data
    
    @staticmethod
    def _convert_percentages(data: pd.DataFrame) -> pd.DataFrame:
        """Convert percentage columns to percentages."""
        for col in PCT_COLS:
            if col in data.columns:
                data[col] = data[col] * 100
        
        return data
    
    @staticmethod
    def _apply_sorting(data: pd.DataFrame, sort_col: str, order: str) -> pd.DataFrame:
        """Apply sorting to the dataset."""
        if sort_col in SORTABLE_COLUMNS:
            data = data.sort_values(
                by=[sort_col, "player_name"],
                ascending=(order == "asc")
            )
        
        return data
    
    @staticmethod
    def _apply_pagination(data: pd.DataFrame, limit: int, offset: int) -> pd.DataFrame:
        """Apply pagination to the dataset."""
        return data.iloc[offset:offset + limit]
    
    @staticmethod
    def _nest_player_data(row: Dict[str, Any]) -> Dict[str, Any]:
        """Nest player data with dot notation."""
        out = {}
        
        for k, v in row.items():
            if "." in k:
                parent, child = k.split(".", 1)
                out.setdefault(parent, {})
                out[parent][child] = None if pd.isna(v) else v
            else:
                out[k] = None if pd.isna(v) else v
        
        return out
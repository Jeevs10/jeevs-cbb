"""
Data Contract Schema
Defines the standardized data structure and validation rules for the CBB dataset.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import pandas as pd


@dataclass
class DataContract:
    """
    Defines the data contract for player statistics.
    
    Primary Keys:
    - player_id: roster.ncaa_id (unique identifier across all years)
    - year: Season year (integer)
    
    All joins and operations must use (player_id, year) as the composite key.
    """
    
    # PRIMARY KEYS
    player_id: str  # roster.ncaa_id cleaned
    year: int      # Season year (2024, 2025, 2026)
    
    # PLAYER IDENTITY FIELDS
    player_name: str
    player_code: str  # Legacy field, kept for compatibility
    team: str
    conf: str
    posClass: str
    
    # ROSTER FIELDS
    roster_number: Optional[str] = None
    roster_height: Optional[str] = None
    roster_year_class: Optional[str] = None
    roster_pos: Optional[str] = None
    roster_origin: Optional[str] = None
    
    # PERFORMANCE METRICS
    # Offensive
    off_adj_opp: Optional[float] = None
    off_poss: Optional[float] = None
    off_team_poss_pct: Optional[float] = None
    off_efg: Optional[float] = None
    off_to: Optional[float] = None
    off_ftr: Optional[float] = None
    adj_rtg_margin: Optional[float] = None
    adj_prod_margin: Optional[float] = None
    adj_rapm_margin: Optional[float] = None
    adj_rapm_prod_margin: Optional[float] = None
    off_rtg: Optional[float] = None
    off_adj_rtg: Optional[float] = None
    off_adj_prod: Optional[float] = None
    off_adj_rapm: Optional[float] = None
    off_adj_rapm_prod: Optional[float] = None
    off_usage: Optional[float] = None
    off_assist: Optional[float] = None
    
    # Defensive
    def_rtg: Optional[float] = None
    def_adj_rtg: Optional[float] = None
    def_adj_prod: Optional[float] = None
    def_adj_rapm: Optional[float] = None
    def_adj_prod_rapm: Optional[float] = None
    def_poss: Optional[float] = None
    def_team_poss_pct: Optional[float] = None
    def_orb: Optional[float] = None
    def_reb: Optional[float] = None
    def_stl: Optional[float] = None
    def_blk: Optional[float] = None
    def_fc: Optional[float] = None
    
    # Tier and Transfer Info
    tier: Optional[str] = None
    transfer_src: Optional[str] = None
    transfer_dest: Optional[str] = None


class SchemaValidator:
    """
    Validates data against the data contract.
    """
    
    @staticmethod
    def validate_primary_keys(df: pd.DataFrame) -> List[str]:
        """
        Validates that (player_id, year) pairs are unique and non-null.
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check for null player_id
        null_player_ids = df[df['player_id'].isna()]
        if not null_player_ids.empty:
            errors.append(f"Found {len(null_player_ids)} rows with null player_id")
        
        # Check for null year
        null_years = df[df['year'].isna()]
        if not null_years.empty:
            errors.append(f"Found {len(null_years)} rows with null year")
        
        # Check for duplicate (player_id, year) pairs
        duplicates = df.duplicated(subset=['player_id', 'year'], keep=False)
        if duplicates.any():
            dup_count = duplicates.sum()
            errors.append(f"Found {dup_count} duplicate (player_id, year) pairs")
        
        return errors
    
    @staticmethod
    def validate_schema_consistency(df: pd.DataFrame) -> List[str]:
        """
        Validates that required columns exist and have correct types.
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Required columns
        required_columns = [
            'player_id', 'year', 'player_name', 'player_code', 
            'team', 'conf', 'posClass'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")
        
        # Type validation
        if 'year' in df.columns:
            if not pd.api.types.is_numeric_dtype(df['year']):
                errors.append("year column must be numeric")
        
        return errors
    
    @staticmethod
    def validate_data_integrity(df: pd.DataFrame) -> List[str]:
        """
        Validates data integrity rules.
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check year ranges
        if 'year' in df.columns:
            invalid_years = df[~df['year'].isin([2024, 2025, 2026])]
            if not invalid_years.empty:
                errors.append(f"Found {len(invalid_years)} rows with invalid years")
        
        # Check for empty player names
        if 'player_name' in df.columns:
            empty_names = df[df['player_name'].isna() | (df['player_name'] == '')]
            if not empty_names.empty:
                errors.append(f"Found {len(empty_names)} rows with empty player names")
        
        return errors


# COLUMN MAPPINGS FOR LEGACY COMPATIBILITY
COLUMN_MAPPINGS = {
    # Legacy -> Standard
    'roster.ncaa_id': 'player_id',
    'roster.number': 'roster_number',
    'roster.height': 'roster_height',
    'roster.year_class': 'roster_year_class',
    'roster.pos': 'roster_pos',
    'roster.origin': 'roster_origin',
}

# PERCENTAGE COLUMNS (multiply by 100 for display)
PERCENTAGE_COLUMNS = [
    'off_usage',
    'off_assist', 
    'off_to',
    'off_orb',
    'def_orb',
    'off_ftr',
    'def_stl',
    'def_blk',
    'off_threepr'
]

# CATEGORICAL FIELDS (never aggregate these)
CATEGORICAL_FIELDS = {
    'player_name',
    'player_code',
    'player_id',
    'team',
    'conf',
    'posClass',
    'roster_number',
    'roster_height',
    'roster_year_class',
    'roster_pos',
    'roster_origin',
}

# EXCLUDE FROM CAREER AGGREGATION
EXCLUDE_FROM_CAREER_AGG = {
    'year',
}

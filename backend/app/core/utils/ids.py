"""
ID Utilities Module
Centralized ID handling and conversion functions.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any


def clean_player_id(x: Any) -> Optional[str]:
    """
    Clean player ID (roster.ncaa_id) to ensure consistency.
    
    Args:
        x: Raw player ID value
        
    Returns:
        Cleaned player ID as string, or None if invalid
    """
    if pd.isna(x):
        return None
    
    # Convert to string and clean
    cleaned = str(x).replace(".0", "").strip()
    
    # Return None if empty after cleaning
    if not cleaned:
        return None
    
    return cleaned


def clean_year(x: Any) -> Optional[int]:
    """
    Clean year values to ensure consistency.
    
    Args:
        x: Raw year value
        
    Returns:
        Cleaned year as integer, or None if invalid
    """
    if pd.isna(x):
        return None
    
    try:
        x = str(x)
        
        # Handle format like "2023/2024" -> 2024
        if "/" in x:
            return int(x.split("/")[-1]) + 2000
        
        # Handle numeric strings
        return int(float(x))
        
    except (ValueError, TypeError):
        return None


def resolve_player_identifier(identifier: str, player_lookup: Dict[str, Dict], 
                         player_code_lookup: Dict[str, Dict]) -> Optional[str]:
    """
    Resolve player identifier to standardized player_id.
    
    Args:
        identifier: Either player_id or player_code
        player_lookup: Dictionary mapping player_id to player data
        player_code_lookup: Dictionary mapping player_code to player data
        
    Returns:
        Resolved player_id, or None if not found
    """
    if not identifier:
        return None
    
    # First try as player_id directly
    if identifier in player_lookup:
        return identifier
    
    # Then try as player_code
    player_data = player_code_lookup.get(identifier)
    if player_data and 'player_id' in player_data:
        return player_data['player_id']
    
    return None


def validate_player_id_format(player_id: str) -> bool:
    """
    Validate player ID format.
    
    Args:
        player_id: Player ID to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not player_id or not isinstance(player_id, str):
        return False
    
    # Basic validation: non-empty string after cleaning
    cleaned = clean_player_id(player_id)
    return cleaned is not None and len(cleaned) > 0


def create_id_mapping(df: pd.DataFrame) -> Dict[str, str]:
    """
    Create mapping between player_code and player_id.
    
    Args:
        df: DataFrame with player data
        
    Returns:
        Dictionary mapping player_code to player_id
    """
    if 'player_code' not in df.columns or 'player_id' not in df.columns:
        return {}
    
    # Get unique mappings (player_code should map to single player_id)
    mapping = df.drop_duplicates(subset=['player_code', 'player_id'])
    
    return dict(zip(mapping['player_code'], mapping['player_id']))


def get_player_id_from_code(player_code: str, id_mapping: Dict[str, str]) -> Optional[str]:
    """
    Convert player_code to player_id using mapping.
    
    Args:
        player_code: Legacy player code
        id_mapping: Mapping from player_code to player_id
        
    Returns:
        Corresponding player_id, or None if not found
    """
    return id_mapping.get(player_code)


def get_player_code_from_id(player_id: str, id_mapping: Dict[str, str]) -> Optional[str]:
    """
    Convert player_id to player_code using mapping.
    
    Args:
        player_id: New player ID
        id_mapping: Mapping from player_code to player_id
        
    Returns:
        Corresponding player_code, or None if not found
    """
    # Reverse lookup
    for code, pid in id_mapping.items():
        if pid == player_id:
            return code
    
    return None

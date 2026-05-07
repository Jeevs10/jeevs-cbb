import os
import pandas as pd

# Import new data layer
from app.data import load_clean_data, create_player_lookup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def load_players():
    """
    Legacy function - now uses new data layer.
    Returns cleaned DataFrame with standardized schema.
    """
    return load_clean_data()

# Load the cleaned dataset using new data layer
df = load_players()

# Apply performance optimizations
from app.core.performance import optimize_dataframe_memory, get_indexed_dataframe
df = optimize_dataframe_memory(df)

# -------------------------
# PLAYER ID MIGRATION
# -------------------------
# Create lookup dictionaries for both player_id (new) and player_code (legacy)
players_df_by_id = (
    df.sort_values(["player_id", "year"])
      .groupby("player_id")
      .tail(1)
)

players_df_by_code = (
    df.sort_values(["player_code", "year"])
      .groupby("player_code")
      .tail(1)
)

# Primary lookup using player_id (new standard)
PLAYER_LOOKUP = players_df_by_id.set_index("player_id").to_dict("index")

# Legacy lookup using player_code (for backward compatibility)
PLAYER_LOOKUP_BY_CODE = players_df_by_code.set_index("player_code").to_dict("index")

# Initialize indexed DataFrame for fast lookups
get_indexed_dataframe(df)

# -------------------------
# ID MAPPING FUNCTIONS
# -------------------------
def get_player_id_from_code(player_code: str) -> str:
    """
    Convert player_code to player_id.
    
    Args:
        player_code: Legacy player code
        
    Returns:
        Corresponding player_id, or None if not found
    """
    player_data = PLAYER_LOOKUP_BY_CODE.get(player_code)
    return player_data.get('player_id') if player_data else None

def get_player_code_from_id(player_id: str) -> str:
    """
    Convert player_id to player_code.
    
    Args:
        player_id: New player ID
        
    Returns:
        Corresponding player_code, or None if not found
    """
    player_data = PLAYER_LOOKUP.get(player_id)
    return player_data.get('player_code') if player_data else None

def resolve_player_id(identifier: str) -> str:
    """
    Resolve player identifier to player_id.
    Accepts either player_id or player_code.
    
    Args:
        identifier: Either player_id or player_code
        
    Returns:
        Resolved player_id, or None if not found
    """
    # First try as player_id directly
    if identifier in PLAYER_LOOKUP:
        return identifier
    
    # Then try as player_code
    return get_player_id_from_code(identifier)
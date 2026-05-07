"""
Data Layer Module
Provides unified access to player data with standardized schema and validation.

This module implements the data contract and provides:
- Loading: Raw data file access
- Cleaning: Data normalization and validation
- Merging: Dataset joining and player record creation
- Schema: Data contract definitions and validation rules

Usage:
    from app.data import load_clean_data, get_player_snapshot, search_players
    
    # Load and clean all data
    df = load_clean_data()
    
    # Get player data
    player = get_player_snapshot(df, "123456", 2024)
    
    # Search players
    results = search_players(df, "john")
"""

from .loader import load_players, get_available_years, validate_data_files
from .cleaner import clean_data, validate_data, prepare_for_display
from .merger import (
    create_player_lookup,
    get_player_snapshot,
    get_player_history,
    search_players
)
from .schema import DataContract, SchemaValidator, COLUMN_MAPPINGS


def load_clean_data(years=None):
    """
    Load and clean player data in one step.
    
    Args:
        years: List of years to load (default: all available)
        
    Returns:
        Cleaned DataFrame ready for use
    """
    # Load raw data
    df = load_players(years)
    
    # Clean and normalize
    df_clean = clean_data(df)
    
    # Validate and report
    validation = validate_data(df_clean)
    
    if not validation['is_valid']:
        print(f"⚠️  Data validation warnings:")
        for error in validation['errors']:
            print(f"   - {error}")
    
    print(f"✅ Loaded {validation['row_count']} rows for {validation['unique_players']} unique players")
    
    return df_clean


def get_data_summary(df):
    """
    Get a summary of the loaded data.
    
    Args:
        df: DataFrame to summarize
        
    Returns:
        Dictionary with data summary
    """
    validation = validate_data(df)
    
    return {
        'total_rows': validation['row_count'],
        'unique_players': validation['unique_players'],
        'year_range': validation['year_range'],
        'available_years': get_data_years(df),
        'conferences': get_conferences(df),
        'validation_errors': validation['errors'],
        'is_valid': validation['is_valid']
    }

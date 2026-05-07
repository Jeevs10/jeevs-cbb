"""
Year Utilities Module
Centralized year handling and normalization functions.
"""

import pandas as pd
import numpy as np
from typing import Optional, Union, List, Dict


def normalize_year(year: Union[str, int, None]) -> Union[int, str, None]:
    """
    Normalize year input to consistent format.
    
    Args:
        year: Year value as string, integer, or None
        
    Returns:
        Normalized year (int, "career", or None)
    """
    if year is None:
        return None
    
    if isinstance(year, str) and year.lower() == "career":
        return "career"
    
    try:
        return int(year)
    except (ValueError, TypeError):
        return None


def validate_year(year: Union[int, str]) -> bool:
    """
    Validate if year is in acceptable range.
    
    Args:
        year: Year to validate
        
    Returns:
        True if valid year, False otherwise
    """
    if year == "career":
        return True
    
    if isinstance(year, (int, str)):
        try:
            year_int = int(year)
            return 2020 <= year_int <= 2030  # Reasonable range for college basketball
        except (ValueError, TypeError):
            return False
    
    return False


def get_year_range(years: List[int]) -> Dict[str, int]:
    """
    Get min and max year from a list.
    
    Args:
        years: List of years
        
    Returns:
        Dictionary with min_year and max_year
    """
    if not years:
        return {"min_year": None, "max_year": None}
    
    valid_years = [y for y in years if y is not None and isinstance(y, (int, str))]
    
    if not valid_years:
        return {"min_year": None, "max_year": None}
    
    year_ints = [int(y) for y in valid_years if y != "career"]
    
    if not year_ints:
        return {"min_year": None, "max_year": None}
    
    return {
        "min_year": min(year_ints),
        "max_year": max(year_ints)
    }


def filter_by_years(df: pd.DataFrame, years: Union[int, List[int], str, None]) -> pd.DataFrame:
    """
    Filter DataFrame by year(s).
    
    Args:
        df: Input DataFrame
        years: Single year, list of years, "career", or None
        
    Returns:
        Filtered DataFrame
    """
    if years is None:
        return df
    
    if 'year' not in df.columns:
        return df
    
    if years == "career":
        # Return all years for career calculations
        return df
    
    if isinstance(years, int):
        return df[df['year'] == years]
    
    if isinstance(years, list):
        return df[df['year'].isin(years)]
    
    return df


def get_available_years(df: pd.DataFrame) -> List[int]:
    """
    Get list of available years from DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Sorted list of unique years
    """
    if 'year' not in df.columns:
        return []
    
    years = df['year'].dropna().unique()
    
    # Convert to int and filter out invalid years
    valid_years = []
    for year in years:
        try:
            year_int = int(year)
            if validate_year(year_int):
                valid_years.append(year_int)
        except (ValueError, TypeError):
            continue
    
    return sorted(list(set(valid_years)))


def create_year_labels(years: List[int]) -> Dict[str, str]:
    """
    Create human-readable year labels.
    
    Args:
        years: List of years
        
    Returns:
        Dictionary mapping year to label
    """
    labels = {}
    
    for year in years:
        if year == "career":
            labels[year] = "Career"
        else:
            labels[year] = str(year)
    
    return labels


def sort_by_year(df: pd.DataFrame, ascending: bool = True) -> pd.DataFrame:
    """
    Sort DataFrame by year.
    
    Args:
        df: Input DataFrame
        ascending: Sort order
        
    Returns:
        Sorted DataFrame
    """
    if 'year' not in df.columns:
        return df
    
    # Handle "career" years by putting them at the end
    df_copy = df.copy()
    
    # Create sort key: career years get high value
    def sort_key(year):
        if year == "career":
            return 9999 if ascending else -9999
        return int(year) if isinstance(year, (int, str)) else 0
    
    df_copy['_sort_year'] = df_copy['year'].apply(sort_key)
    df_sorted = df_copy.sort_values('_sort_year', ascending=ascending)
    df_sorted = df_sorted.drop('_sort_year', axis=1)
    
    return df_sorted

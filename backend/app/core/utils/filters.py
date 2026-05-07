"""
Filter Utilities Module
Centralized data filtering and pandas operations.
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Union


def apply_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply multiple filters to DataFrame.
    
    Args:
        df: Input DataFrame
        filters: Dictionary of column_name -> filter_value pairs
        
    Returns:
        Filtered DataFrame
    """
    filtered_df = df.copy()
    
    for column, value in filters.items():
        if column not in filtered_df.columns:
            continue
        
        if value is None:
            continue
        
        if isinstance(value, list):
            # Filter for values in list
            filtered_df = filtered_df[filtered_df[column].isin(value)]
        elif isinstance(value, str):
            # String filter (case-insensitive)
            if value.strip():
                filtered_df = filtered_df[
                    filtered_df[column].str.lower().str.contains(value.lower(), na=False)
                ]
        else:
            # Exact match filter
            filtered_df = filtered_df[filtered_df[column] == value]
    
    return filtered_df


def filter_by_numeric_range(df: pd.DataFrame, column: str, 
                         min_val: Optional[float] = None, 
                         max_val: Optional[float] = None) -> pd.DataFrame:
    """
    Filter DataFrame by numeric range.
    
    Args:
        df: Input DataFrame
        column: Column name to filter
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)
        
    Returns:
        Filtered DataFrame
    """
    if column not in df.columns:
        return df
    
    filtered_df = df.copy()
    
    if min_val is not None:
        filtered_df = filtered_df[filtered_df[column] >= min_val]
    
    if max_val is not None:
        filtered_df = filtered_df[filtered_df[column] <= max_val]
    
    return filtered_df


def search_columns(df: pd.DataFrame, query: str, 
                  columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Search for query across multiple columns.
    
    Args:
        df: Input DataFrame
        query: Search query
        columns: Columns to search in (default: text columns)
        
    Returns:
        Filtered DataFrame with matching rows
    """
    if not query or not query.strip():
        return df
    
    query_lower = query.strip().lower()
    
    # Default to string columns if not specified
    if columns is None:
        columns = df.select_dtypes(include=['object']).columns.tolist()
    
    # Filter to only existing columns
    search_columns = [col for col in columns if col in df.columns]
    
    if not search_columns:
        return df
    
    # Create search masks
    masks = []
    for col in search_columns:
        # Create lowercase version for case-insensitive search
        mask = df[col].fillna("").astype(str).str.lower().str.contains(query_lower, na=False)
        masks.append(mask)
    
    # Combine masks with OR logic
    if masks:
        combined_mask = masks[0]
        for mask in masks[1:]:
            combined_mask = combined_mask | mask
        
        return df[combined_mask]
    
    return df


def sort_dataframe(df: pd.DataFrame, sort_columns: Union[str, List[str]], 
                  ascending: Union[bool, List[bool]] = True) -> pd.DataFrame:
    """
    Sort DataFrame by specified columns.
    
    Args:
        df: Input DataFrame
        sort_columns: Column name(s) to sort by
        ascending: Sort direction(s)
        
    Returns:
        Sorted DataFrame
    """
    if isinstance(sort_columns, str):
        sort_columns = [sort_columns]
    
    # Filter to existing columns
    valid_columns = [col for col in sort_columns if col in df.columns]
    
    if not valid_columns:
        return df
    
    return df.sort_values(by=valid_columns, ascending=ascending)


def paginate_dataframe(df: pd.DataFrame, offset: int = 0, limit: int = 50) -> pd.DataFrame:
    """
    Apply pagination to DataFrame.
    
    Args:
        df: Input DataFrame
        offset: Number of rows to skip
        limit: Maximum number of rows to return
        
    Returns:
        Paginated DataFrame
    """
    if offset < 0:
        offset = 0
    
    if limit <= 0:
        return pd.DataFrame()
    
    return df.iloc[offset:offset + limit]


def clean_numeric_columns(df: pd.DataFrame, 
                        exclude_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Convert appropriate columns to numeric, excluding specified columns.
    
    Args:
        df: Input DataFrame
        exclude_columns: Columns to exclude from numeric conversion
        
    Returns:
        DataFrame with cleaned numeric columns
    """
    if exclude_columns is None:
        exclude_columns = []
    
    cleaned_df = df.copy()
    
    for col in cleaned_df.columns:
        if col not in exclude_columns:
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='ignore')
    
    return cleaned_df


def convert_percentages(df: pd.DataFrame, 
                      percentage_columns: List[str], 
                      multiply_by: float = 100.0) -> pd.DataFrame:
    """
    Convert decimal columns to percentages.
    
    Args:
        df: Input DataFrame
        percentage_columns: List of columns to convert
        multiply_by: Factor to multiply by (default 100 for percentages)
        
    Returns:
        DataFrame with converted percentage columns
    """
    converted_df = df.copy()
    
    for col in percentage_columns:
        if col in converted_df.columns:
            converted_df[col] = converted_df[col] * multiply_by
    
    return converted_df


def replace_nan_with_none(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace NaN values with None for JSON serialization.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with NaN replaced by None
    """
    return df.replace({np.nan: None})


def get_unique_values(df: pd.DataFrame, column: str, 
                    sort: bool = True, 
                    exclude_na: bool = True) -> List[Any]:
    """
    Get unique values from a column.
    
    Args:
        df: Input DataFrame
        column: Column name
        sort: Whether to sort the results
        exclude_na: Whether to exclude NaN values
        
    Returns:
        List of unique values
    """
    if column not in df.columns:
        return []
    
    values = df[column].unique()
    
    if exclude_na:
        values = [v for v in values if pd.notna(v)]
    
    if sort:
        try:
            # Try to sort numerically first
            values = sorted(values, key=lambda x: (float('inf') if pd.isna(x) else float(x)))
        except (ValueError, TypeError):
            # Fall back to string sort
            values = sorted([str(v) for v in values])
    
    return values


def create_filter_summary(df: pd.DataFrame, filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create summary of applied filters.
    
    Args:
        df: Original DataFrame
        filters: Applied filters
        
    Returns:
        Dictionary with filter summary
    """
    return {
        "original_count": len(df),
        "applied_filters": {k: v for k, v in filters.items() if v is not None},
        "filter_count": len([v for v in filters.values() if v is not None])
    }

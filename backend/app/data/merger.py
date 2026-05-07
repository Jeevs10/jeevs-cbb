"""
Data Merger Module
Handles joining datasets and creating unified player records.
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Tuple

from .schema import CATEGORICAL_FIELDS, EXCLUDE_FROM_CAREER_AGG


class DataMerger:
    """
    Handles merging and joining of player datasets.
    """
    
    @staticmethod
    def create_player_lookup(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Create a lookup dictionary for player metadata.
        
        Args:
            df: Input DataFrame with player data
            
        Returns:
            Dictionary mapping player_id to player metadata
        """
        # Get the most recent record for each player
        latest_df = (
            df.sort_values(['player_id', 'year'])
              .groupby('player_id')
              .tail(1)
        )
        
        return latest_df.set_index('player_id').to_dict('index')
    
    @staticmethod
    def filter_by_keys(df: pd.DataFrame, player_ids: Optional[List[str]] = None, 
                      years: Optional[List[int]] = None) -> pd.DataFrame:
        """
        Filter DataFrame by player_ids and/or years.
        
        Args:
            df: Input DataFrame
            player_ids: List of player_ids to include (if None, include all)
            years: List of years to include (if None, include all)
            
        Returns:
            Filtered DataFrame
        """
        filtered_df = df.copy()
        
        # Filter by player_ids
        if player_ids is not None:
            filtered_df = filtered_df[filtered_df['player_id'].isin(player_ids)]
        
        # Filter by years
        if years is not None:
            filtered_df = filtered_df[filtered_df['year'].isin(years)]
        
        return filtered_df
    
    @staticmethod
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
                if 2020 <= year_int <= 2030:  # Reasonable range
                    valid_years.append(year_int)
            except (ValueError, TypeError):
                continue
        
        return sorted(list(set(valid_years)))
    
    @staticmethod
    def get_conferences(df: pd.DataFrame) -> List[str]:
        """
        Get list of conferences from DataFrame.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Sorted list of unique conferences
        """
        if 'conf' not in df.columns:
            return []
        
        conferences = df['conf'].dropna().unique()
        return sorted([str(c) for c in conferences if c])
    
    @staticmethod
    def get_player_snapshot(df: pd.DataFrame, player_id: str, 
                           year: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get a single player snapshot for a specific year or career.
        
        Args:
            df: Input DataFrame
            player_id: Player ID to retrieve
            year: Year to retrieve (if None, gets most recent)
            
        Returns:
            Player data as dictionary, or None if not found
        """
        player_data = df[df['player_id'] == player_id]
        
        if player_data.empty:
            return None
        
        # Filter by year if specified
        if year is not None and year != 'career':
            year_data = player_data[player_data['year'] == year]
            if not year_data.empty:
                player_data = year_data
        
        # Sort by year and get the most recent
        player_data = player_data.sort_values('year')
        return player_data.iloc[-1].to_dict()
    
    @staticmethod
    def get_player_history(df: pd.DataFrame, player_id: str) -> pd.DataFrame:
        """
        Get complete player history across all years.
        
        Args:
            df: Input DataFrame
            player_id: Player ID to retrieve
            
        Returns:
            DataFrame with player's historical data
        """
        return df[df['player_id'] == player_id].sort_values('year')
    
    @staticmethod
    def build_career_snapshot(player_df: pd.DataFrame, 
                             weight_column: str = 'off_poss') -> Dict[str, Any]:
        """
        Build a career snapshot by aggregating a player's multi-year data.
        
        Args:
            player_df: DataFrame with player's multi-year data
            weight_column: Column to use for weighted averages
            
        Returns:
            Career snapshot as dictionary
        """
        if player_df.empty:
            return {}
        
        player_df = player_df.copy()
        latest = player_df.sort_values('year').iloc[-1]
        
        out = {}
        
        # Keep categorical fields from latest year
        for col in CATEGORICAL_FIELDS:
            if col in player_df.columns:
                out[col] = latest.get(col)
        
        # Get numeric columns
        numeric_cols = player_df.select_dtypes(include=[np.number]).columns
        
        # Determine weight column
        weight_col = weight_column if weight_column in player_df.columns else None
        
        for col in numeric_cols:
            # Skip categorical and excluded columns
            if col in CATEGORICAL_FIELDS or col in EXCLUDE_FROM_CAREER_AGG:
                continue
            
            values = player_df[col].fillna(0).values
            
            if weight_col and weight_col in player_df.columns:
                weights = player_df[weight_col].fillna(0).values
                if weights.sum() > 0:
                    out[col] = float(np.average(values, weights=weights))
                else:
                    out[col] = float(values.mean())
            else:
                out[col] = float(values.mean())
        
        # Add career metadata
        years = sorted(player_df['year'].dropna().astype(int).unique().tolist())
        
        out['year'] = 'career'
        out['is_career'] = True
        
        if len(years) == 1:
            out['career_year_label'] = str(years[0])
        else:
            out['career_year_label'] = f"{years[0]}–{years[-1]}"
        
        return out
    
    @staticmethod
    def search_players(df: pd.DataFrame, query: str, 
                      search_fields: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Search players by name, team, or player_code.
        
        Args:
            df: Input DataFrame
            query: Search query
            search_fields: Fields to search in (default: player_name, team, player_code)
            
        Returns:
            DataFrame with matching players
        """
        if not query or not query.strip():
            return df
        
        if search_fields is None:
            search_fields = ['player_name', 'team', 'player_code']
        
        # Create lowercase search columns if they don't exist
        df_search = df.copy()
        query_lower = query.strip().lower()
        
        masks = []
        
        for field in search_fields:
            if field in df_search.columns:
                # Create lowercase version for case-insensitive search
                lc_col = f"_{field}_lc"
                df_search[lc_col] = df_search[field].fillna("").astype(str).str.lower()
                mask = df_search[lc_col].str.contains(query_lower, na=False)
                masks.append(mask)
        
        if masks:
            combined_mask = masks[0]
            for mask in masks[1:]:
                combined_mask = combined_mask | mask
            
            return df_search[combined_mask]
        
        return df  # Return empty if no search fields found
    
    @staticmethod
    def get_available_years(df: pd.DataFrame) -> List[int]:
        """
        Get list of years available in the dataset.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Sorted list of available years
        """
        if 'year' not in df.columns:
            return []
        
        return sorted(df['year'].dropna().astype(int).unique().tolist())
    
    @staticmethod
    def get_conferences(df: pd.DataFrame) -> List[str]:
        """
        Get list of conferences available in the dataset.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Sorted list of conferences
        """
        if 'conf' not in df.columns:
            return []
        
        return sorted(df['conf'].dropna().unique().tolist())


# Global merger instance
_merger = DataMerger()


def create_player_lookup(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Convenience function to create player lookup.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Player lookup dictionary
    """
    return _merger.create_player_lookup(df)


def get_player_snapshot(df: pd.DataFrame, player_id: str, 
                       year: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Convenience function to get player snapshot.
    
    Args:
        df: Input DataFrame
        player_id: Player ID
        year: Year (optional)
        
    Returns:
        Player snapshot
    """
    return _merger.get_player_snapshot(df, player_id, year)


def get_player_history(df: pd.DataFrame, player_id: str) -> pd.DataFrame:
    """
    Convenience function to get player history.
    
    Args:
        df: Input DataFrame
        player_id: Player ID
        
    Returns:
        Player history DataFrame
    """
    return _merger.get_player_history(df, player_id)


def search_players(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """
    Convenience function to search players.
    
    Args:
        df: Input DataFrame
        query: Search query
        
    Returns:
        DataFrame with matching players
    """
    return _merger.search_players(df, query)

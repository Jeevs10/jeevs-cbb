"""
Player Repository
Handles player data access using repository pattern.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from .base import CSVRepository
from ..core.performance import cache_result


class PlayerRepository(CSVRepository):
    """
    Repository for player data access.
    
    Provides clean interface for player operations while abstracting
    the underlying data storage mechanism.
    """
    
    def _get_index_columns(self) -> List[str]:
        """Return index columns for player data."""
        return ['player_id', 'year']
    
    @cache_result(ttl_seconds=600)  # 10 minutes cache
    def get_player(self, player_id: str, year: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get player data by ID and year.
        
        Args:
            player_id: Player ID
            year: Year to get data for (if None, gets most recent)
            
        Returns:
            Player data dictionary or None if not found
        """
        # Try cache first
        cache_key = f"get_player:{player_id}:{year}"
        cached = self.get_cached("get_player", player_id=player_id, year=year)
        if cached:
            return cached
        
        # Filter by player_id
        player_data = self.df[self.df['player_id'] == player_id]
        
        if player_data.empty:
            return None
        
        # Filter by year if specified
        if year is not None:
            year_data = player_data[player_data['year'] == year]
            if not year_data.empty:
                player_data = year_data
        
        # Get most recent record
        player_data = player_data.sort_values('year')
        result = player_data.iloc[-1].to_dict()
        
        # Cache result
        self.set_cache("get_player", result, player_id=player_id, year=year)
        
        return result
    
    @cache_result(ttl_seconds=300)  # 5 minutes cache
    def get_player_history(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Get complete player history across all years.
        
        Args:
            player_id: Player ID
            
        Returns:
            List of player data by year
        """
        # Try cache first
        cached = self.get_cached("get_player_history", player_id=player_id)
        if cached:
            return cached
        
        player_data = self.df[self.df['player_id'] == player_id]
        
        if player_data.empty:
            return []
        
        # Sort by year and convert to list of dicts
        result = player_data.sort_values('year').to_dict('records')
        
        # Cache result
        self.set_cache("get_player_history", result, player_id=player_id)
        
        return result
    
    @cache_result(ttl_seconds=1800)  # 30 minutes cache
    def list_players(self, limit: int = 50, offset: int = 0, 
                   sort: str = "adj_rapm_margin", order: str = "desc",
                   year: Optional[int] = None, conf: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List players with filtering and pagination.
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            sort: Sort column
            order: Sort order
            year: Filter by year
            conf: Filter by conference
            
        Returns:
            List of player data
        """
        # Try cache first
        cached = self.get_cached("list_players", limit=limit, offset=offset, 
                              sort=sort, order=order, year=year, conf=conf)
        if cached:
            return cached
        
        # Apply filters
        filters = {}
        if year is not None:
            filters['year'] = year
        if conf is not None:
            filters['conf'] = conf
        
        filtered_df = self._apply_filters(self.df, filters)
        
        # Sort
        filtered_df = self._sort(filtered_df, sort, order)
        
        # Paginate
        result_df = self._paginate(filtered_df, offset, limit)
        
        # Convert to list of dicts and clean
        result = result_df.replace({np.nan: None}).to_dict('records')
        
        # Cache result
        self.set_cache("list_players", result, limit=limit, offset=offset,
                      sort=sort, order=order, year=year, conf=conf)
        
        return result
    
    def count_players(self, year: Optional[int] = None, 
                    conf: Optional[str] = None) -> int:
        """
        Count players with optional filters.
        
        Args:
            year: Filter by year
            conf: Filter by conference
            
        Returns:
            Count of players
        """
        filters = {}
        if year is not None:
            filters['year'] = year
        if conf is not None:
            filters['conf'] = conf
        
        filtered_df = self._apply_filters(self.df, filters)
        return len(filtered_df)
    
    @cache_result(ttl_seconds=1800)  # 30 minutes cache
    def get_top_players(self, metric: str, year: Optional[int] = None, 
                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top players by metric.
        
        Args:
            metric: Metric to rank by
            year: Filter by year
            limit: Number of players to return
            
        Returns:
            List of top players
        """
        # Try cache first
        cached = self.get_cached("get_top_players", metric=metric, year=year, limit=limit)
        if cached:
            return cached
        
        # Apply year filter if specified
        if year is not None:
            filtered_df = self.df[self.df['year'] == year]
        else:
            filtered_df = self.df
        
        # Check if metric exists
        if metric not in filtered_df.columns:
            return []
        
        # Sort by metric and get top players
        top_df = filtered_df.nlargest(limit, metric)
        
        # Convert to list of dicts
        result = top_df.replace({np.nan: None}).to_dict('records')
        
        # Cache result
        self.set_cache("get_top_players", result, metric=metric, year=year, limit=limit)
        
        return result
    
    def get_available_years(self) -> List[int]:
        """
        Get list of available years.
        
        Returns:
            Sorted list of unique years
        """
        if 'year' not in self.df.columns:
            return []
        
        years = self.df['year'].dropna().unique()
        return sorted([int(y) for y in years if y != 'career'])
    
    def get_conferences(self) -> List[str]:
        """
        Get list of available conferences.
        
        Returns:
            Sorted list of unique conferences
        """
        if 'conf' not in self.df.columns:
            return []
        
        conferences = self.df['conf'].dropna().unique()
        return sorted([str(c) for c in conferences if c])
    
    def get_player_by_code(self, player_code: str, year: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get player data by player_code (legacy support).
        
        Args:
            player_code: Legacy player code
            year: Year to get data for
            
        Returns:
            Player data dictionary or None if not found
        """
        # Find player_id for this code
        code_data = self.df[self.df['player_code'] == player_code]
        
        if code_data.empty:
            return None
        
        # Get the player_id from the most recent record
        player_id = code_data.sort_values('year').iloc[-1]['player_id']
        
        # Use the main get_player method
        return self.get_player(player_id, year)
    
    def search_players(self, query: str, limit: int = 50, offset: int = 0,
                      year: Optional[int] = None, conf: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search players by name, team, or player code.
        
        Args:
            query: Search query
            limit: Maximum number of results
            offset: Number of results to skip
            year: Filter by year
            conf: Filter by conference
            
        Returns:
            List of matching players
        """
        # Try cache first
        cached = self.get_cached("search_players", query=query, limit=limit, offset=offset,
                              year=year, conf=conf)
        if cached:
            return cached
        
        # Apply basic filters first
        filters = {}
        if year is not None:
            filters['year'] = year
        if conf is not None:
            filters['conf'] = conf
        
        filtered_df = self._apply_filters(self.df, filters)
        
        # Apply search filter
        if query and query.strip():
            query_lower = query.strip().lower()
            
            # Search in multiple fields
            search_mask = (
                filtered_df['player_name'].str.lower().str.contains(query_lower, na=False) |
                filtered_df['team'].str.lower().str.contains(query_lower, na=False) |
                filtered_df['player_code'].str.lower().str.contains(query_lower, na=False)
            )
            filtered_df = filtered_df[search_mask]
        
        # Sort by relevance (name matches first) and paginate
        filtered_df = filtered_df.sort_values(['player_name', 'year'])
        result_df = self._paginate(filtered_df, offset, limit)
        
        # Convert to list of dicts
        result = result_df.replace({np.nan: None}).to_dict('records')
        
        # Cache result
        self.set_cache("search_players", result, query=query, limit=limit, offset=offset,
                      year=year, conf=conf)
        
        return result
    
    def get_career_stats(self, player_id: str) -> Optional[Dict[str, Any]]:
        """
        Get career statistics for a player.
        
        Args:
            player_id: Player ID
            
        Returns:
            Career stats dictionary or None if not found
        """
        player_history = self.get_player_history(player_id)
        
        if not player_history:
            return None
        
        # Convert to DataFrame for aggregation
        history_df = pd.DataFrame(player_history)
        
        # Get latest categorical data
        latest = history_df.sort_values('year').iloc[-1]
        
        career_stats = {}
        
        # Keep categorical fields
        categorical_fields = [
            'player_id', 'player_code', 'player_name', 'team', 'conf', 'posClass'
        ]
        for field in categorical_fields:
            if field in latest:
                career_stats[field] = latest[field]
        
        # Aggregate numeric fields
        numeric_cols = history_df.select_dtypes(include=[np.number]).columns
        weight_col = 'off_poss' if 'off_poss' in history_df.columns else None
        
        for col in numeric_cols:
            if col in categorical_fields or col == 'year':
                continue
            
            values = history_df[col].fillna(0).values
            
            if weight_col and weight_col in history_df.columns:
                weights = history_df[weight_col].fillna(0).values
                if weights.sum() > 0:
                    career_stats[col] = float(np.average(values, weights=weights))
                else:
                    career_stats[col] = float(values.mean())
            else:
                career_stats[col] = float(values.mean())
        
        # Add career metadata
        years = sorted(history_df['year'].dropna().astype(int).unique().tolist())
        career_stats['year'] = 'career'
        career_stats['is_career'] = True
        
        if len(years) == 1:
            career_stats['career_year_label'] = str(years[0])
        else:
            career_stats['career_year_label'] = f"{years[0]}–{years[-1]}"
        
        return career_stats

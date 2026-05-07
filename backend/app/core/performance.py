"""
Performance Optimization Module
Handles caching, indexing, and performance improvements.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import functools
import time
from collections import defaultdict

# Global cache for frequently accessed data
_CACHE = {}
_CACHE_STATS = defaultdict(int)
_CACHE_TTL = {}  # Time-to-live for cache entries


def cache_result(ttl_seconds: int = 300):
    """
    Decorator to cache function results with TTL.
    
    Args:
        ttl_seconds: Time to live in seconds (default: 5 minutes)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            current_time = time.time()
            
            # Check if cached result exists and is not expired
            if key in _CACHE and key in _CACHE_TTL:
                if current_time - _CACHE_TTL[key] < ttl_seconds:
                    _CACHE_STATS[f"{func.__name__}_hits"] += 1
                    return _CACHE[key]
            
            # Compute result and cache it
            result = func(*args, **kwargs)
            _CACHE[key] = result
            _CACHE_TTL[key] = current_time
            _CACHE_STATS[f"{func.__name__}_misses"] += 1
            
            return result
        
        return wrapper
    return decorator


def clear_cache(pattern: Optional[str] = None):
    """
    Clear cache entries.
    
    Args:
        pattern: If provided, only clear entries matching this pattern
    """
    global _CACHE, _CACHE_TTL
    
    if pattern:
        keys_to_remove = [k for k in _CACHE.keys() if pattern in k]
        for key in keys_to_remove:
            _CACHE.pop(key, None)
            _CACHE_TTL.pop(key, None)
    else:
        _CACHE.clear()
        _CACHE_TTL.clear()


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache performance statistics.
    
    Returns:
        Dictionary with cache statistics
    """
    stats = {}
    
    for key, count in _CACHE_STATS.items():
        if key.endswith('_hits'):
            func_name = key[:-5]
            hits = count
            misses = _CACHE_STATS.get(f"{func_name}_misses", 0)
            total = hits + misses
            
            if total > 0:
                stats[func_name] = {
                    "hits": hits,
                    "misses": misses,
                    "hit_rate": hits / total,
                    "total_calls": total
                }
    
    stats["cache_size"] = len(_CACHE)
    return stats


class IndexedDataFrame:
    """
    Wrapper around DataFrame with pre-built indexes for fast lookups.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.indexes = {}
        self._build_indexes()
    
    def _build_indexes(self):
        """Build indexes for common query patterns."""
        # Primary key index: (player_id, year)
        if 'player_id' in self.df.columns and 'year' in self.df.columns:
            self.indexes['player_year'] = self.df.set_index(['player_id', 'year'])
        
        # Player index: player_id -> list of rows
        if 'player_id' in self.df.columns:
            self.indexes['player'] = defaultdict(list)
            for _, row in self.df.iterrows():
                self.indexes['player'][row['player_id']].append(row)
        
        # Year index: year -> list of rows
        if 'year' in self.df.columns:
            self.indexes['year'] = defaultdict(list)
            for _, row in self.df.iterrows():
                self.indexes['year'][row['year']].append(row)
        
        # Conference index: conf -> list of rows
        if 'conf' in self.df.columns:
            self.indexes['conf'] = defaultdict(list)
            for _, row in self.df.iterrows():
                if pd.notna(row['conf']):
                    self.indexes['conf'][row['conf']].append(row)
        
        # Search indexes for text fields
        text_fields = ['player_name', 'team', 'player_code']
        for field in text_fields:
            if field in self.df.columns:
                self.indexes[f'search_{field}'] = defaultdict(list)
                for _, row in self.df.iterrows():
                    if pd.notna(row[field]):
                        # Lowercase for case-insensitive search
                        text = str(row[field]).lower()
                        self.indexes[f'search_{field}'][text].append(row)
    
    def get_player_snapshot(self, player_id: str, year: Optional[int] = None) -> Optional[Dict]:
        """
        Get player snapshot using indexes.
        
        Args:
            player_id: Player ID
            year: Year to get data for (if None, gets most recent)
            
        Returns:
            Player data or None if not found
        """
        if 'player_year' not in self.indexes:
            return None
        
        try:
            if year is not None:
                # Get specific year
                if (player_id, year) in self.indexes['player_year'].index:
                    return self.indexes['player_year'].loc[(player_id, year)].to_dict()
            else:
                # Get most recent year
                player_data = self.indexes['player'].get(player_id, [])
                if player_data:
                    return max(player_data, key=lambda x: x['year']).to_dict()
        except (KeyError, ValueError):
            pass
        
        return None
    
    def search_players(self, query: str, fields: Optional[List[str]] = None) -> List[Dict]:
        """
        Search players using pre-built search indexes.
        
        Args:
            query: Search query
            fields: Fields to search in (default: player_name, team, player_code)
            
        Returns:
            List of matching player data
        """
        if fields is None:
            fields = ['player_name', 'team', 'player_code']
        
        query_lower = query.lower()
        results = []
        seen_players = set()
        
        for field in fields:
            search_index = self.indexes.get(f'search_{field}')
            if not search_index:
                continue
            
            # Find exact matches first
            if query_lower in search_index:
                for row in search_index[query_lower]:
                    player_id = row['player_id']
                    if player_id not in seen_players:
                        results.append(row.to_dict())
                        seen_players.add(player_id)
            
            # Find partial matches
            for text, rows in search_index.items():
                if query_lower in text and text != query_lower:
                    for row in rows:
                        player_id = row['player_id']
                        if player_id not in seen_players:
                            results.append(row.to_dict())
                            seen_players.add(player_id)
        
        return results
    
    def filter_by_year(self, year: int) -> List[Dict]:
        """
        Filter by year using index.
        
        Args:
            year: Year to filter by
            
        Returns:
            List of player data for the year
        """
        if 'year' not in self.indexes:
            return []
        
        return [row.to_dict() for row in self.indexes['year'].get(year, [])]
    
    def filter_by_conference(self, conf: str) -> List[Dict]:
        """
        Filter by conference using index.
        
        Args:
            conf: Conference to filter by
            
        Returns:
            List of player data for the conference
        """
        if 'conf' not in self.indexes:
            return []
        
        return [row.to_dict() for row in self.indexes['conf'].get(conf.lower(), [])]
    
    def get_dataframe(self) -> pd.DataFrame:
        """Get the original DataFrame."""
        return self.df.copy()


# Global indexed dataframe instance
_INDEXED_DF = None


def get_indexed_dataframe(df: Optional[pd.DataFrame] = None) -> IndexedDataFrame:
    """
    Get or create indexed DataFrame.
    
    Args:
        df: DataFrame to index (if None, uses cached version)
        
    Returns:
        IndexedDataFrame instance
    """
    global _INDEXED_DF
    
    if df is not None:
        _INDEXED_DF = IndexedDataFrame(df)
    elif _INDEXED_DF is None:
        from app.core.data_loader import df
        _INDEXED_DF = IndexedDataFrame(df)
    
    return _INDEXED_DF


@cache_result(ttl_seconds=600)  # 10 minutes cache
def get_top_players(metric: str, year: Optional[int] = None, limit: int = 10) -> List[Dict]:
    """
    Get top players by metric using cached results.
    
    Args:
        metric: Metric to rank by
        year: Year to filter by (optional)
        limit: Number of players to return
        
    Returns:
        List of top players
    """
    indexed_df = get_indexed_dataframe()
    
    if year is not None:
        players = indexed_df.filter_by_year(year)
    else:
        players = indexed_df.get_dataframe().to_dict('records')
    
    # Sort by metric
    try:
        players.sort(key=lambda x: x.get(metric, 0) or 0, reverse=True)
        return players[:limit]
    except (TypeError, ValueError):
        return []


def optimize_dataframe_memory(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize DataFrame memory usage.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Memory-optimized DataFrame
    """
    optimized_df = df.copy()
    
    for col in optimized_df.columns:
        col_type = optimized_df[col].dtype
        
        if col_type != 'object':
            c_min = optimized_df[col].min()
            c_max = optimized_df[col].max()
            
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    optimized_df[col] = optimized_df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    optimized_df[col] = optimized_df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    optimized_df[col] = optimized_df[col].astype(np.int32)
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    optimized_df[col] = optimized_df[col].astype(np.float32)
    
    return optimized_df

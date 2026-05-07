"""
Base Repository Class
Provides common interface and functionality for all repositories.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
    """
    Abstract base class for all repositories.
    
    Provides common interface that can be implemented for different
    storage backends (CSV, SQL, NoSQL, etc.).
    """
    
    def __init__(self, data_source: Any = None):
        """
        Initialize repository with data source.
        
        Args:
            data_source: Data source (DataFrame, connection, etc.)
        """
        self.data_source = data_source
        self._cache = {}
        self._cache_ttl = {}
    
    @abstractmethod
    def get_by_id(self, id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Get entity by ID.
        
        Args:
            id: Entity ID
            **kwargs: Additional parameters
            
        Returns:
            Entity data or None if not found
        """
        pass
    
    @abstractmethod
    def list(self, **filters) -> List[Dict[str, Any]]:
        """
        List entities with optional filters.
        
        Args:
            **filters: Filter parameters
            
        Returns:
            List of entities
        """
        pass
    
    @abstractmethod
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search entities.
        
        Args:
            query: Search query
            **kwargs: Additional search parameters
            
        Returns:
            List of matching entities
        """
        pass
    
    def count(self, **filters) -> int:
        """
        Count entities with optional filters.
        
        Args:
            **filters: Filter parameters
            
        Returns:
            Count of entities
        """
        return len(self.list(**filters))
    
    def exists(self, id: str, **kwargs) -> bool:
        """
        Check if entity exists.
        
        Args:
            id: Entity ID
            **kwargs: Additional parameters
            
        Returns:
            True if entity exists, False otherwise
        """
        return self.get_by_id(id, **kwargs) is not None
    
    def validate_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize filter parameters.
        
        Args:
            filters: Raw filter parameters
            
        Returns:
            Validated filters
        """
        validated = {}
        
        for key, value in filters.items():
            if value is not None:
                validated[key] = value
        
        return validated
    
    def get_cache_key(self, method: str, **kwargs) -> str:
        """
        Generate cache key for method call.
        
        Args:
            method: Method name
            **kwargs: Method arguments
            
        Returns:
            Cache key string
        """
        import time
        
        # Create deterministic key from method and sorted kwargs
        key_parts = [method]
        for k in sorted(kwargs.keys()):
            key_parts.append(f"{k}:{kwargs[k]}")
        
        return "|".join(key_parts)
    
    def get_cached(self, method: str, ttl_seconds: int = 300, **kwargs):
        """
        Get cached result if available and not expired.
        
        Args:
            method: Method name
            ttl_seconds: Time to live in seconds
            **kwargs: Method arguments
            
        Returns:
            Cached result or None
        """
        import time
        
        key = self.get_cache_key(method, **kwargs)
        
        if key in self._cache:
            cached_time = self._cache_ttl.get(key, 0)
            if time.time() - cached_time < ttl_seconds:
                return self._cache[key]
        
        return None
    
    def set_cache(self, method: str, result: Any, ttl_seconds: int = 300, **kwargs):
        """
        Cache method result.
        
        Args:
            method: Method name
            result: Result to cache
            ttl_seconds: Time to live in seconds
            **kwargs: Method arguments
        """
        import time
        
        key = self.get_cache_key(method, **kwargs)
        self._cache[key] = result
        self._cache_ttl[key] = time.time()
    
    def clear_cache(self, pattern: Optional[str] = None):
        """
        Clear repository cache.
        
        Args:
            pattern: If provided, only clear entries matching pattern
        """
        if pattern:
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                self._cache.pop(key, None)
                self._cache_ttl.pop(key, None)
        else:
            self._cache.clear()
            self._cache_ttl.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Cache statistics dictionary
        """
        return {
            "cache_size": len(self._cache),
            "cached_methods": list(set(k.split("|")[0] for k in self._cache.keys()))
        }


class CSVRepository(BaseRepository):
    """
    Base repository for CSV-based data sources.
    """
    
    def __init__(self, dataframe: pd.DataFrame):
        """
        Initialize CSV repository with DataFrame.
        
        Args:
            dataframe: Pandas DataFrame containing data
        """
        super().__init__(dataframe)
        self.df = dataframe
        
        # Build indexes for common queries
        self._build_indexes()
    
    def _build_indexes(self):
        """Build performance indexes."""
        # Primary key index
        if hasattr(self, '_get_index_columns'):
            index_cols = self._get_index_columns()
            if all(col in self.df.columns for col in index_cols):
                self._index = self.df.set_index(index_cols)
            else:
                self._index = None
        else:
            self._index = None
    
    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply filters to DataFrame.
        
        Args:
            df: DataFrame to filter
            filters: Filter dictionary
            
        Returns:
            Filtered DataFrame
        """
        filtered_df = df.copy()
        
        for column, value in filters.items():
            if column not in filtered_df.columns or value is None:
                continue
            
            if isinstance(value, list):
                filtered_df = filtered_df[filtered_df[column].isin(value)]
            elif isinstance(value, str):
                if value.strip():
                    filtered_df = filtered_df[
                        filtered_df[column].str.lower().str.contains(value.lower(), na=False)
                    ]
            else:
                filtered_df = filtered_df[filtered_df[column] == value]
        
        return filtered_df
    
    def _paginate(self, df: pd.DataFrame, offset: int = 0, limit: int = 50) -> pd.DataFrame:
        """
        Apply pagination to DataFrame.
        
        Args:
            df: DataFrame to paginate
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
    
    def _sort(self, df: pd.DataFrame, sort_by: str, order: str = "desc") -> pd.DataFrame:
        """
        Sort DataFrame.
        
        Args:
            df: DataFrame to sort
            sort_by: Column to sort by
            order: Sort order ("asc" or "desc")
            
        Returns:
            Sorted DataFrame
        """
        if sort_by not in df.columns:
            return df
        
        ascending = order == "asc"
        return df.sort_values(by=sort_by, ascending=ascending)

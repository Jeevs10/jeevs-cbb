"""
Repository Layer Package
Provides abstraction layer for data access to enable easier database migration.

This package implements the Repository pattern to separate data access logic
from business logic, making it easier to switch from CSV-based storage
to a proper database system in the future.

Usage:
    from app.repositories import PlayerRepository
    
    repo = PlayerRepository()
    player = repo.get_player("123456", 2024)
    players = repo.search_players("john doe")
"""

from .base import BaseRepository
from .player import PlayerRepository
from .search import SearchRepository
from .stats import StatsRepository

__all__ = [
    'BaseRepository',
    'PlayerRepository', 
    'SearchRepository',
    'StatsRepository'
]

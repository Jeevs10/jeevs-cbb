"""
Performance Monitoring API
Provides endpoints for monitoring system performance and cache statistics.
"""

from fastapi import APIRouter
from app.core.performance import get_cache_stats, clear_cache
import psutil
import time

router = APIRouter()


@router.get("/performance/stats")
def get_performance_stats():
    """
    Get system performance statistics.
    
    Returns information about cache hit rates, memory usage, and system metrics.
    """
    # Get cache statistics
    cache_stats = get_cache_stats()
    
    # Get system metrics
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)
    
    return {
        "timestamp": time.time(),
        "cache": cache_stats,
        "system": {
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent
            },
            "cpu": {
                "percent": cpu_percent
            }
        }
    }


@router.post("/performance/cache/clear")
def clear_performance_cache(pattern: str = None):
    """
    Clear performance cache.
    
    Args:
        pattern: If provided, only clear entries matching this pattern
        
    Returns:
        Cache clearing result
    """
    clear_cache(pattern)
    
    return {
        "message": f"Cache cleared{' for pattern: ' + pattern if pattern else ' completely'}",
        "timestamp": time.time()
    }


@router.get("/performance/health")
def health_check():
    """
    Simple health check endpoint.
    
    Returns basic system health status.
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": time.time() - psutil.boot_time()
    }

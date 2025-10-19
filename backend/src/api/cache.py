"""Cache management API endpoints."""

import sys
from pathlib import Path

from fastapi import APIRouter

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.src.services.cache_service import get_cache

router = APIRouter()


@router.get("/stats")
async def cache_stats():
    """
    Get cache statistics.

    Returns:
        Cache hit rate, size, and other metrics
    """
    cache = get_cache()
    return cache.stats()


@router.post("/clear")
async def clear_cache():
    """
    Clear entire cache.

    Use this endpoint to force-refresh all cached data.
    """
    cache = get_cache()
    cache.clear()
    return {
        "message": "Cache cleared successfully",
        "stats": cache.stats(),
    }


@router.post("/cleanup")
async def cleanup_expired():
    """
    Remove expired cache entries.

    This is called automatically but can be triggered manually.
    """
    cache = get_cache()
    removed = cache.cleanup_expired()
    return {
        "message": f"Removed {removed} expired entries",
        "removed_count": removed,
        "stats": cache.stats(),
    }


@router.post("/invalidate/{pattern}")
async def invalidate_pattern(pattern: str):
    """
    Invalidate cache entries matching pattern.

    Examples:
        - "device_metrics" - clear all device metrics
        - "correlation" - clear all correlation calculations
        - "device_comparison" - clear all comparison data
    """
    cache = get_cache()
    removed = cache.invalidate_pattern(pattern)
    return {
        "message": f"Invalidated {removed} entries matching '{pattern}'",
        "removed_count": removed,
        "stats": cache.stats(),
    }

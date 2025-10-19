"""Caching service for improved API performance."""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Optional


class CacheService:
    """
    Simple in-memory cache with TTL support.

    For production, consider using Redis or Memcached.
    """

    def __init__(self, default_ttl_seconds: int = 300):
        """
        Initialize cache service.

        Args:
            default_ttl_seconds: Default time-to-live in seconds (default: 5 minutes)
        """
        self._cache: dict[str, tuple[Any, datetime]] = {}
        self.default_ttl = default_ttl_seconds
        self.hits = 0
        self.misses = 0

    def _generate_key(self, prefix: str, **kwargs) -> str:
        """
        Generate cache key from prefix and parameters.

        Args:
            prefix: Cache key prefix
            **kwargs: Parameters to include in key

        Returns:
            Cache key string
        """
        # Sort kwargs for consistent key generation
        sorted_params = json.dumps(kwargs, sort_keys=True)
        key_string = f"{prefix}:{sorted_params}"

        # Hash for shorter keys
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key in self._cache:
            value, expires_at = self._cache[key]

            if datetime.utcnow() < expires_at:
                self.hits += 1
                return value
            else:
                # Expired, remove from cache
                del self._cache[key]

        self.misses += 1
        return None

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live in seconds (uses default if None)
        """
        if ttl_seconds is None:
            ttl_seconds = self.default_ttl

        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        self._cache[key] = (value, expires_at)

    def invalidate(self, key: str) -> bool:
        """
        Invalidate cache entry.

        Args:
            key: Cache key

        Returns:
            True if key was found and removed, False otherwise
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern.

        Args:
            pattern: Pattern to match (prefix)

        Returns:
            Number of keys invalidated
        """
        keys_to_remove = [k for k in self._cache.keys() if k.startswith(pattern)]
        for key in keys_to_remove:
            del self._cache[key]
        return len(keys_to_remove)

    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()
        self.hits = 0
        self.misses = 0

    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        now = datetime.utcnow()
        expired_keys = [
            k for k, (_, expires_at) in self._cache.items() if now >= expires_at
        ]

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)

    def stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dict with cache statistics
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests,
        }


# Global cache instance
_cache_instance: Optional[CacheService] = None


def get_cache() -> CacheService:
    """
    Get global cache instance.

    Returns:
        CacheService instance
    """
    global _cache_instance

    if _cache_instance is None:
        # Default TTL: 5 minutes for metrics data
        _cache_instance = CacheService(default_ttl_seconds=300)

    return _cache_instance


def cache_key_for_device_metrics(
    device_id: int, hours: int, metric_type: Optional[str] = None
) -> str:
    """
    Generate cache key for device metrics.

    Args:
        device_id: Device ID
        hours: Hours of history
        metric_type: Optional metric type filter

    Returns:
        Cache key
    """
    cache = get_cache()
    return cache._generate_key(
        "device_metrics",
        device_id=device_id,
        hours=hours,
        metric_type=metric_type or "all",
    )


def cache_key_for_comparison(
    device_ids: list[int], hours: int, metric_types: Optional[list[str]] = None
) -> str:
    """
    Generate cache key for device comparison.

    Args:
        device_ids: List of device IDs
        hours: Hours of history
        metric_types: Optional metric types filter

    Returns:
        Cache key
    """
    cache = get_cache()
    return cache._generate_key(
        "device_comparison",
        device_ids=sorted(device_ids),  # Sort for consistent keys
        hours=hours,
        metric_types=sorted(metric_types) if metric_types else "all",
    )


def cache_key_for_correlation(
    device_id: int, metric_x: str, metric_y: str, hours: int
) -> str:
    """
    Generate cache key for correlation calculation.

    Args:
        device_id: Device ID
        metric_x: First metric
        metric_y: Second metric
        hours: Hours of history

    Returns:
        Cache key
    """
    cache = get_cache()
    # Sort metrics for consistent keys (x,y same as y,x correlation)
    metrics = sorted([metric_x, metric_y])
    return cache._generate_key(
        "correlation",
        device_id=device_id,
        metric_x=metrics[0],
        metric_y=metrics[1],
        hours=hours,
    )

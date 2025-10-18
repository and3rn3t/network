"""
Data collection service for UniFi Network API.

Provides automated polling and storage of host data.
"""

from .config import DEFAULT_CONFIG, CollectorConfig
from .data_collector import DataCollector
from .scheduler import CollectionScheduler, run_collector

__all__ = [
    "CollectorConfig",
    "DEFAULT_CONFIG",
    "DataCollector",
    "CollectionScheduler",
    "run_collector",
]

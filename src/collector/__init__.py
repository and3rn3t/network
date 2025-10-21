"""
Data collection service for UniFi Network API.

Provides automated polling and storage of host data.
"""

from .config import DEFAULT_CONFIG, CollectorConfig
from .data_collector import DataCollector
from .orchestrator import CollectionOrchestrator, create_orchestrator_from_config_file
from .scheduler import CollectionScheduler, run_collector
from .unifi_collector import UniFiCollectorConfig, UniFiDataCollector

__all__ = [
    "CollectorConfig",
    "DEFAULT_CONFIG",
    "DataCollector",
    "CollectionScheduler",
    "run_collector",
    "UniFiCollectorConfig",
    "UniFiDataCollector",
    "CollectionOrchestrator",
    "create_orchestrator_from_config_file",
]

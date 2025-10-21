"""
Unified data collection orchestrator.

Manages both cloud-based UniFi API and local UniFi Controller collections.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from ..database import Database
from .config import CollectorConfig
from .data_collector import DataCollector
from .unifi_collector import UniFiCollectorConfig, UniFiDataCollector

logger = logging.getLogger(__name__)


class CollectionOrchestrator:
    """
    Orchestrates data collection from multiple sources.

    Manages both cloud-based UniFi API and local UniFi Controller
    data collection, coordinating scheduling and resource usage.
    """

    def __init__(self, config: CollectorConfig, database: Optional[Database] = None):
        """
        Initialize collection orchestrator.

        Args:
            config: Collector configuration
            database: Optional shared Database instance
        """
        self.config = config
        self.config.validate()

        # Initialize database (shared across collectors)
        if database:
            self.db = database
        else:
            db_path = config.db_path if config.db_path else "network_monitor.db"
            self.db = Database(db_path)

        # Initialize collectors based on configuration
        self.cloud_collector: Optional[DataCollector] = None
        self.unifi_collector: Optional[UniFiDataCollector] = None

        # Set up logging
        logging.basicConfig(
            level=getattr(logging, config.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        self._initialize_collectors()

        logger.info("CollectionOrchestrator initialized")

    def _initialize_collectors(self) -> None:
        """Initialize configured collectors."""
        # Initialize cloud collector (if API key provided)
        if self.config.api_key and not self.config.unifi_controller_enabled:
            logger.info("Initializing cloud-based data collector")
            try:
                self.cloud_collector = DataCollector(
                    config=self.config, database=self.db
                )
                logger.info("Cloud collector initialized")
            except Exception as e:
                logger.error(f"Failed to initialize cloud collector: {e}")

        # Initialize UniFi Controller collector (if enabled)
        if self.config.unifi_controller_enabled:
            logger.info("Initializing UniFi Controller data collector")
            try:
                unifi_config = UniFiCollectorConfig(
                    controller_url=self.config.unifi_controller_url,
                    username=self.config.unifi_username,
                    password=self.config.unifi_password,
                    site=self.config.unifi_site,
                    verify_ssl=self.config.unifi_verify_ssl,
                    enable_events=self.config.enable_events,
                    enable_metrics=self.config.enable_metrics,
                    status_retention_days=self.config.status_retention_days,
                    event_retention_days=self.config.event_retention_days,
                    metric_retention_days=self.config.metric_retention_days,
                    log_level=self.config.log_level,
                )

                self.unifi_collector = UniFiDataCollector(
                    config=unifi_config, database=self.db
                )
                logger.info("UniFi Controller collector initialized")
            except Exception as e:
                logger.error(f"Failed to initialize UniFi Controller collector: {e}")

    def collect_all(self) -> Dict[str, Any]:
        """
        Run collection from all configured sources.

        Returns:
            Dictionary with combined statistics from all collectors
        """
        start_time = datetime.now()
        logger.info("Starting unified collection cycle")

        combined_stats = {
            "start_time": start_time,
            "cloud_stats": None,
            "unifi_stats": None,
            "total_errors": 0,
            "collectors_run": 0,
            "collectors_failed": 0,
        }

        # Run cloud collector
        if self.cloud_collector:
            try:
                logger.info("Running cloud data collector")
                cloud_stats = self.cloud_collector.collect()
                combined_stats["cloud_stats"] = cloud_stats
                combined_stats["collectors_run"] += 1

                if cloud_stats.get("errors", 0) > 0:
                    combined_stats["total_errors"] += cloud_stats["errors"]
                    combined_stats["collectors_failed"] += 1

                logger.info(
                    f"Cloud collection completed: {cloud_stats.get('hosts_processed', 0)} hosts processed"
                )
            except Exception as e:
                logger.error(f"Cloud collector failed: {e}", exc_info=True)
                combined_stats["collectors_failed"] += 1
                combined_stats["total_errors"] += 1

        # Run UniFi Controller collector
        if self.unifi_collector:
            try:
                logger.info("Running UniFi Controller data collector")
                unifi_stats = self.unifi_collector.collect()
                combined_stats["unifi_stats"] = unifi_stats
                combined_stats["collectors_run"] += 1

                if unifi_stats.get("errors", 0) > 0:
                    combined_stats["total_errors"] += unifi_stats["errors"]
                    combined_stats["collectors_failed"] += 1

                logger.info(
                    f"UniFi collection completed: "
                    f"{unifi_stats.get('devices_processed', 0)} devices, "
                    f"{unifi_stats.get('clients_processed', 0)} clients processed"
                )
            except Exception as e:
                logger.error(f"UniFi Controller collector failed: {e}", exc_info=True)
                combined_stats["collectors_failed"] += 1
                combined_stats["total_errors"] += 1

        # Calculate total duration
        duration = (datetime.now() - start_time).total_seconds()
        combined_stats["duration_seconds"] = duration
        combined_stats["end_time"] = datetime.now()

        logger.info(
            f"Unified collection completed in {duration:.2f}s: "
            f"{combined_stats['collectors_run']} collectors run, "
            f"{combined_stats['collectors_failed']} failed, "
            f"{combined_stats['total_errors']} total errors"
        )

        return combined_stats

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics from all collectors.

        Returns:
            Dictionary with statistics from all configured collectors
        """
        stats = {
            "collectors_configured": 0,
            "cloud_collector": None,
            "unifi_collector": None,
        }

        if self.cloud_collector:
            stats["collectors_configured"] += 1
            stats["cloud_collector"] = self.cloud_collector.get_stats()

        if self.unifi_collector:
            stats["collectors_configured"] += 1
            stats["unifi_collector"] = self.unifi_collector.get_stats()

        return stats

    def close(self) -> None:
        """Close all collectors and database connection."""
        logger.info("Closing collection orchestrator")

        if self.cloud_collector:
            try:
                self.cloud_collector.close()
            except Exception as e:
                logger.warning(f"Error closing cloud collector: {e}")

        if self.unifi_collector:
            try:
                self.unifi_collector.close()
            except Exception as e:
                logger.warning(f"Error closing UniFi collector: {e}")

        # Close database (only if we created it)
        if hasattr(self.db, "close"):
            try:
                self.db.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.warning(f"Error closing database: {e}")


def create_orchestrator_from_config_file(
    config_path: str = "config.py",
) -> CollectionOrchestrator:
    """
    Create a CollectionOrchestrator from a config file.

    Args:
        config_path: Path to config file (default: config.py)

    Returns:
        Initialized CollectionOrchestrator instance
    """
    import importlib.util
    import sys
    from pathlib import Path

    # Load config file
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # Import config module
    spec = importlib.util.spec_from_file_location("user_config", config_file)
    config_module = importlib.util.module_from_spec(spec)
    sys.modules["user_config"] = config_module
    spec.loader.exec_module(config_module)

    # Create CollectorConfig from user config
    config = CollectorConfig(
        log_level=getattr(config_module, "LOG_LEVEL", "INFO"),
        enable_metrics=True,
        enable_events=True,
        status_retention_days=90,
        event_retention_days=365,
        metric_retention_days=30,
    )

    # Determine which API type to use
    api_type = getattr(config_module, "API_TYPE", "cloud").lower()

    if api_type == "local":
        # Configure for local UniFi Controller
        config.unifi_controller_enabled = True
        controller_host = getattr(config_module, "CONTROLLER_HOST", "192.168.1.1")
        controller_port = getattr(config_module, "CONTROLLER_PORT", 443)
        config.unifi_controller_url = f"https://{controller_host}:{controller_port}"
        config.unifi_username = getattr(config_module, "CONTROLLER_USERNAME")
        config.unifi_password = getattr(config_module, "CONTROLLER_PASSWORD")
        config.unifi_site = getattr(config_module, "CONTROLLER_SITE", "default")
        config.unifi_verify_ssl = getattr(config_module, "CONTROLLER_VERIFY_SSL", False)
        logger.info(
            f"Configured for local UniFi Controller at {config.unifi_controller_url}"
        )
    else:
        # Configure for cloud API
        config.unifi_controller_enabled = False
        config.api_base_url = getattr(
            config_module, "BASE_URL", "https://api.ui.com/v1"
        )
        config.api_key = getattr(config_module, "API_KEY")
        logger.info("Configured for cloud-based UniFi API")

    return CollectionOrchestrator(config)

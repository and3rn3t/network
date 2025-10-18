"""
Data collection service for UniFi hosts.

Polls the UniFi API periodically, stores data in the database,
and generates events for status changes.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..database import Database
from ..database.models import CollectionRun, Event, Host, HostStatus, Metric
from ..database.repositories import (
    EventRepository,
    HostRepository,
    MetricRepository,
    StatusRepository,
)
from ..unifi_client import UniFiClient
from .config import CollectorConfig

logger = logging.getLogger(__name__)


class DataCollector:
    """
    Data collector for UniFi network devices.

    Fetches host data from the UniFi API, stores it in the database,
    detects status changes, and generates events.
    """

    def __init__(
        self,
        config: CollectorConfig,
        api_client: Optional[UniFiClient] = None,
        database: Optional[Database] = None,
    ):
        """
        Initialize data collector.

        Args:
            config: Collector configuration
            api_client: Optional UniFi API client (creates one if not provided)
            database: Optional Database instance (creates one if not provided)
        """
        self.config = config
        self.config.validate()

        # Set up logging
        logging.basicConfig(
            level=getattr(logging, config.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        # Initialize API client
        if api_client:
            self.api = api_client
        else:
            self.api = UniFiClient(api_key=config.api_key, base_url=config.api_base_url)

        # Initialize database
        if database:
            self.db = database
        else:
            db_path = (
                Path(config.db_path)
                if config.db_path
                else Path("data/unifi_network.db")
            )
            self.db = Database(db_path)
            self.db.initialize()

        # Initialize repositories
        self.host_repo = HostRepository(self.db)
        self.status_repo = StatusRepository(self.db)
        self.event_repo = EventRepository(self.db)
        self.metric_repo = MetricRepository(self.db)

        # Track collection state
        self._last_collection: Optional[datetime] = None
        self._collection_count = 0
        self._error_count = 0

        logger.info("DataCollector initialized")

    def collect(self) -> Dict[str, Any]:
        """
        Perform single collection cycle.

        Fetches all hosts from the API, updates the database,
        detects changes, and generates events.

        Returns:
            Dictionary with collection statistics
        """
        start_time = datetime.now()
        logger.info("Starting collection cycle")

        stats = {
            "start_time": start_time,
            "hosts_processed": 0,
            "hosts_updated": 0,
            "hosts_created": 0,
            "status_records": 0,
            "events_created": 0,
            "metrics_created": 0,
            "errors": 0,
        }

        try:
            # Fetch all hosts from API
            logger.info("Fetching hosts from API")
            api_hosts = self.api.get_hosts()

            if not api_hosts:
                logger.warning("No hosts returned from API")
                return stats

            logger.info(f"Retrieved {len(api_hosts)} hosts from API")

            # Process each host
            for host_data in api_hosts:
                try:
                    self._process_host(host_data, stats)
                    stats["hosts_processed"] += 1
                except Exception as e:
                    logger.error(
                        f"Error processing host {host_data.get('id', 'unknown')}: {e}"
                    )
                    stats["errors"] += 1
                    self._error_count += 1

            # Clean up old data
            if self.config.status_retention_days > 0:
                deleted = self.status_repo.delete_old_records(
                    self.config.status_retention_days
                )
                logger.info(f"Deleted {deleted} old status records")

            if self.config.event_retention_days > 0:
                deleted = self.event_repo.delete_old_events(
                    self.config.event_retention_days
                )
                logger.info(f"Deleted {deleted} old events")

            if self.config.metric_retention_days > 0:
                deleted = self.metric_repo.delete_old_metrics(
                    self.config.metric_retention_days
                )
                logger.info(f"Deleted {deleted} old metrics")

            # Update collection tracking
            self._last_collection = datetime.now()
            self._collection_count += 1

            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            stats["duration_seconds"] = duration
            stats["end_time"] = datetime.now()

            logger.info(
                f"Collection completed in {duration:.2f}s: "
                f"{stats['hosts_processed']} hosts, "
                f"{stats['status_records']} statuses, "
                f"{stats['events_created']} events, "
                f"{stats['metrics_created']} metrics"
            )

        except Exception as e:
            logger.error(f"Collection cycle failed: {e}", exc_info=True)
            stats["errors"] += 1
            self._error_count += 1
            raise

        return stats

    def _process_host(self, host_data: Dict[str, Any], stats: Dict[str, Any]) -> None:
        """
        Process a single host from API response.

        Args:
            host_data: Raw host data from API
            stats: Statistics dictionary to update
        """
        host_id = host_data.get("id")
        if not host_id:
            logger.warning("Host missing ID, skipping")
            return

        # Create/update host record
        host = Host.from_api_response(host_data)

        # Check if host exists
        existing_host = self.host_repo.get_by_id(host_id)

        if existing_host:
            # Update existing host
            self.host_repo.update(host)
            stats["hosts_updated"] += 1
            logger.debug(f"Updated host {host_id}")
        else:
            # Create new host
            self.host_repo.create(host)
            stats["hosts_created"] += 1
            logger.info(f"Created new host {host_id} ({host.name})")

            # Generate host discovered event
            if self.config.enable_events:
                event = Event(
                    event_type="host_discovered",
                    severity="info",
                    title="New Host Discovered",
                    host_id=host_id,
                    description=f"New host discovered: {host.name} ({host.type})",
                )
                self.event_repo.create(event)
                stats["events_created"] += 1

        # Create status record
        status = HostStatus.from_api_response(host_id, host_data)

        # Check for status change
        if existing_host and self.config.enable_events:
            latest_status = self.status_repo.get_latest_for_host(host_id)

            if latest_status and latest_status.is_online != status.is_online:
                # Status changed - generate event
                old_status = "online" if latest_status.is_online else "offline"
                new_status = "online" if status.is_online else "offline"

                event = Event.create_status_change(
                    host_id=host_id, old_status=old_status, new_status=new_status
                )
                self.event_repo.create(event)
                stats["events_created"] += 1
                logger.info(
                    f"Host {host_id} status changed: {old_status} -> {new_status}"
                )

        # Save status
        self.status_repo.create(status)
        stats["status_records"] += 1

        # Create metrics if enabled
        if self.config.enable_metrics:
            metrics = self._extract_metrics(host_id, host_data)
            if metrics:
                created = self.metric_repo.create_many(metrics)
                stats["metrics_created"] += created
                logger.debug(f"Created {created} metrics for host {host_id}")

    def _extract_metrics(self, host_id: str, host_data: Dict[str, Any]) -> List[Metric]:
        """
        Extract metrics from host data.

        Args:
            host_id: Host identifier
            host_data: Raw host data from API

        Returns:
            List of Metric instances
        """
        metrics = []

        # Check for uptime
        uptime = host_data.get("uptimeSeconds")
        if uptime is not None:
            metrics.append(
                Metric(
                    host_id=host_id,
                    metric_name="uptime",
                    metric_value=float(uptime),
                    unit="seconds",
                )
            )

        # Check for metrics object
        if "metrics" in host_data:
            metric_data = host_data["metrics"]

            # CPU usage
            if "cpu" in metric_data:
                metrics.append(
                    Metric(
                        host_id=host_id,
                        metric_name="cpu_usage",
                        metric_value=float(metric_data["cpu"]),
                        unit="percent",
                    )
                )

            # Memory usage
            if "memory" in metric_data:
                metrics.append(
                    Metric(
                        host_id=host_id,
                        metric_name="memory_usage",
                        metric_value=float(metric_data["memory"]),
                        unit="percent",
                    )
                )

            # Temperature
            if "temperature" in metric_data:
                metrics.append(
                    Metric(
                        host_id=host_id,
                        metric_name="temperature",
                        metric_value=float(metric_data["temperature"]),
                        unit="celsius",
                    )
                )

        return metrics

    def get_stats(self) -> Dict[str, Any]:
        """
        Get collector statistics.

        Returns:
            Dictionary with collector stats
        """
        return {
            "last_collection": (
                self._last_collection.isoformat() if self._last_collection else None
            ),
            "collection_count": self._collection_count,
            "error_count": self._error_count,
            "total_hosts": self.host_repo.count(),
            "total_statuses": self.status_repo.count(),
            "total_events": self.event_repo.count(),
            "total_metrics": self.metric_repo.count(),
        }

    def close(self) -> None:
        """Close database connection."""
        if hasattr(self.db, "close"):
            self.db.close()
            logger.info("Database connection closed")

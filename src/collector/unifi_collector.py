"""
UniFi Controller data collection service.

Polls the UniFi Controller API periodically, stores data in the database,
detects changes, and generates events.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..database import Database
from ..database.models_unifi import (
    UniFiClient,
    UniFiClientStatus,
    UniFiDevice,
    UniFiDeviceStatus,
    UniFiEvent,
)
from ..database.repositories.unifi_repository import (
    UniFiClientRepository,
    UniFiClientStatusRepository,
    UniFiCollectionRunRepository,
    UniFiDeviceRepository,
    UniFiDeviceStatusRepository,
    UniFiEventRepository,
    UniFiMetricsRepository,
)
from ..unifi_controller import UniFiController

logger = logging.getLogger(__name__)


class UniFiCollectorConfig:
    """Configuration for UniFi data collector."""

    def __init__(
        self,
        controller_url: str,
        username: str,
        password: str,
        site: str = "default",
        verify_ssl: bool = True,
        enable_events: bool = True,
        enable_metrics: bool = True,
        status_retention_days: int = 30,
        event_retention_days: int = 90,
        metric_retention_days: int = 30,
        log_level: str = "INFO",
    ):
        """
        Initialize collector configuration.

        Args:
            controller_url: UniFi Controller URL
            username: Controller username
            password: Controller password
            site: Site name (default: "default")
            verify_ssl: Verify SSL certificates
            enable_events: Generate events for changes
            enable_metrics: Store time-series metrics
            status_retention_days: Days to keep status history
            event_retention_days: Days to keep events
            metric_retention_days: Days to keep metrics
            log_level: Logging level
        """
        self.controller_url = controller_url
        self.username = username
        self.password = password
        self.site = site
        self.verify_ssl = verify_ssl
        self.enable_events = enable_events
        self.enable_metrics = enable_metrics
        self.status_retention_days = status_retention_days
        self.event_retention_days = event_retention_days
        self.metric_retention_days = metric_retention_days
        self.log_level = log_level

    def validate(self) -> None:
        """Validate configuration."""
        if not self.controller_url:
            raise ValueError("controller_url is required")
        if not self.username:
            raise ValueError("username is required")
        if not self.password:
            raise ValueError("password is required")


class UniFiDataCollector:
    """
    Data collector for UniFi Controller.

    Fetches device and client data from the UniFi Controller,
    stores it in the database, detects changes, and generates events.
    """

    def __init__(
        self,
        config: UniFiCollectorConfig,
        controller: Optional[UniFiController] = None,
        database: Optional[Database] = None,
    ):
        """
        Initialize UniFi data collector.

        Args:
            config: Collector configuration
            controller: Optional UniFi Controller client
            database: Optional Database instance
        """
        self.config = config
        self.config.validate()

        # Set up logging
        logging.basicConfig(
            level=getattr(logging, config.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        # Initialize UniFi Controller client
        if controller:
            self.controller = controller
        else:
            # Extract host from URL (e.g., "https://192.168.1.1:443" -> "192.168.1.1")
            from urllib.parse import urlparse

            parsed = urlparse(config.controller_url)
            host = (
                parsed.hostname or config.controller_url.split("://")[-1].split(":")[0]
            )
            port = parsed.port or 443

            self.controller = UniFiController(
                host=host,
                username=config.username,
                password=config.password,
                port=port,
                site=config.site,
                verify_ssl=config.verify_ssl,
            )

        # Initialize database
        if database:
            self.db = database
        else:
            self.db = Database("network_monitor.db")

        # Initialize repositories
        self.device_repo = UniFiDeviceRepository(self.db)
        self.device_status_repo = UniFiDeviceStatusRepository(self.db)
        self.client_repo = UniFiClientRepository(self.db)
        self.client_status_repo = UniFiClientStatusRepository(self.db)
        self.event_repo = UniFiEventRepository(self.db)
        self.metrics_repo = UniFiMetricsRepository(self.db)
        self.collection_run_repo = UniFiCollectionRunRepository(self.db)

        # Track collection state
        self._last_collection: Optional[datetime] = None
        self._collection_count = 0
        self._error_count = 0

        logger.info(
            f"UniFiDataCollector initialized for {config.controller_url} (site: {config.site})"
        )

    def collect(self) -> Dict[str, Any]:
        """
        Perform single collection cycle.

        Fetches devices and clients from the controller,
        updates the database, detects changes, and generates events.

        Returns:
            Dictionary with collection statistics
        """
        start_time = datetime.now()
        logger.info("Starting UniFi collection cycle")

        # Create collection run record
        run_id = self.collection_run_repo.create_run(self.config.controller_url)

        stats = {
            "run_id": run_id,
            "start_time": start_time,
            "devices_processed": 0,
            "devices_created": 0,
            "devices_updated": 0,
            "clients_processed": 0,
            "clients_created": 0,
            "clients_updated": 0,
            "status_records": 0,
            "events_created": 0,
            "metrics_created": 0,
            "errors": 0,
        }

        try:
            # Authenticate to controller
            logger.info("Authenticating to UniFi Controller")
            self.controller.login()

            # Collect devices
            self._collect_devices(stats)

            # Collect clients
            self._collect_clients(stats)

            # Clean up old data
            self._cleanup_old_data()

            # Update collection tracking
            self._last_collection = datetime.now()
            self._collection_count += 1

            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            stats["duration_seconds"] = duration
            stats["end_time"] = datetime.now()

            # Mark collection run as completed
            self.collection_run_repo.complete_run(
                run_id=run_id,
                devices_collected=stats["devices_processed"],
                clients_collected=stats["clients_processed"],
                errors_encountered=stats["errors"],
            )

            logger.info(
                f"Collection completed in {duration:.2f}s: "
                f"{stats['devices_processed']} devices, "
                f"{stats['clients_processed']} clients, "
                f"{stats['events_created']} events, "
                f"{stats['metrics_created']} metrics"
            )

        except Exception as e:
            logger.error(f"Collection cycle failed: {e}", exc_info=True)
            stats["errors"] += 1
            self._error_count += 1

            # Mark collection run as failed
            self.collection_run_repo.fail_run(run_id, str(e))

            raise
        finally:
            # Always logout
            try:
                self.controller.logout()
            except Exception as e:
                logger.warning(f"Logout failed: {e}")

        return stats

    def _collect_devices(self, stats: Dict[str, Any]) -> None:
        """
        Collect device data from controller.

        Args:
            stats: Statistics dictionary to update
        """
        try:
            logger.info(f"Fetching devices from site '{self.config.site}'")
            api_devices = self.controller.get_devices()

            if not api_devices:
                logger.warning("No devices returned from controller")
                return

            logger.info(f"Retrieved {len(api_devices)} devices from controller")

            # Process each device
            for device_data in api_devices:
                try:
                    self._process_device(device_data, stats)
                    stats["devices_processed"] += 1
                except Exception as e:
                    logger.error(
                        f"Error processing device {device_data.get('mac', 'unknown')}: {e}"
                    )
                    stats["errors"] += 1
                    self._error_count += 1

        except Exception as e:
            logger.error(f"Failed to fetch devices: {e}")
            stats["errors"] += 1
            self._error_count += 1
            raise

    def _process_device(
        self, device_data: Dict[str, Any], stats: Dict[str, Any]
    ) -> None:
        """
        Process a single device from API response.

        Args:
            device_data: Raw device data from API
            stats: Statistics dictionary to update
        """
        mac = device_data.get("mac")
        if not mac:
            logger.warning("Device missing MAC address, skipping")
            return

        # Create device model from API response
        device = UniFiDevice.from_controller_response(
            device_data, site=self.config.site
        )

        # Check if device exists
        existing_device = self.device_repo.get_by_mac(mac)

        if existing_device:
            # Check for changes
            if self.config.enable_events:
                self._check_device_changes(existing_device, device, stats)

            # Update existing device
            self.device_repo.update(device)
            stats["devices_updated"] += 1
            logger.debug(f"Updated device {mac} ({device.name})")
        else:
            # Create new device
            self.device_repo.create(device)
            stats["devices_created"] += 1
            logger.info(f"Created new device {mac} ({device.name})")

            # Generate device discovered event
            if self.config.enable_events:
                event = UniFiEvent(
                    event_type="device_discovered",
                    severity="info",
                    title="New Device Discovered",
                    description=f"New {device.type} device: {device.name} ({device.model})",
                    device_mac=mac,
                    metadata=json.dumps(
                        {"device_type": device.type, "model": device.model}
                    ),
                )
                self.event_repo.create(event)
                stats["events_created"] += 1

        # Create device status record
        status = UniFiDeviceStatus.from_controller_response(mac, device_data)
        self.device_status_repo.create(status)
        stats["status_records"] += 1

        # Create metrics if enabled
        if self.config.enable_metrics:
            self._create_device_metrics(mac, device_data, stats)

    def _check_device_changes(
        self, old_device: UniFiDevice, new_device: UniFiDevice, stats: Dict[str, Any]
    ) -> None:
        """
        Check for device changes and generate events.

        Args:
            old_device: Previous device state
            new_device: New device state
            stats: Statistics dictionary to update
        """
        # Check for state change (online/offline)
        if old_device.state != new_device.state:
            old_state = "online" if old_device.state == 1 else "offline"
            new_state = "online" if new_device.state == 1 else "offline"

            severity = "critical" if new_state == "offline" else "info"

            event = UniFiEvent(
                event_type="device_status_change",
                severity=severity,
                title=f"Device {new_state.title()}",
                description=f"Device {new_device.name} is now {new_state}",
                device_mac=new_device.mac,
                previous_value=old_state,
                new_value=new_state,
            )
            self.event_repo.create(event)
            stats["events_created"] += 1
            logger.info(
                f"Device {new_device.mac} state changed: {old_state} -> {new_state}"
            )

        # Check for adoption status change
        if old_device.adopted != new_device.adopted:
            if new_device.adopted:
                event = UniFiEvent(
                    event_type="device_adopted",
                    severity="info",
                    title="Device Adopted",
                    description=f"Device {new_device.name} has been adopted",
                    device_mac=new_device.mac,
                )
                self.event_repo.create(event)
                stats["events_created"] += 1

        # Check for firmware upgrade
        if old_device.version != new_device.version and new_device.version:
            event = UniFiEvent(
                event_type="firmware_upgrade",
                severity="info",
                title="Firmware Upgraded",
                description=f"Device {new_device.name} upgraded to {new_device.version}",
                device_mac=new_device.mac,
                previous_value=old_device.version,
                new_value=new_device.version,
            )
            self.event_repo.create(event)
            stats["events_created"] += 1

    def _create_device_metrics(
        self, mac: str, device_data: Dict[str, Any], stats: Dict[str, Any]
    ) -> None:
        """
        Extract and store device metrics.

        Args:
            mac: Device MAC address
            device_data: Raw device data from API
            stats: Statistics dictionary to update
        """
        # Uptime
        if "uptime" in device_data:
            self.metrics_repo.create_device_metric(
                device_mac=mac,
                metric_name="uptime",
                metric_value=float(device_data["uptime"]),
                unit="seconds",
            )
            stats["metrics_created"] += 1

        # System stats (if available)
        if "system-stats" in device_data:
            sys_stats = device_data["system-stats"]

            # CPU usage
            if "cpu" in sys_stats:
                self.metrics_repo.create_device_metric(
                    device_mac=mac,
                    metric_name="cpu_usage",
                    metric_value=float(sys_stats["cpu"]),
                    unit="percent",
                )
                stats["metrics_created"] += 1

            # Memory usage
            if "mem" in sys_stats:
                self.metrics_repo.create_device_metric(
                    device_mac=mac,
                    metric_name="memory_usage",
                    metric_value=float(sys_stats["mem"]),
                    unit="percent",
                )
                stats["metrics_created"] += 1

        # Temperature
        if "general_temperature" in device_data:
            self.metrics_repo.create_device_metric(
                device_mac=mac,
                metric_name="temperature",
                metric_value=float(device_data["general_temperature"]),
                unit="celsius",
            )
            stats["metrics_created"] += 1

        # Satisfaction
        if "satisfaction" in device_data:
            self.metrics_repo.create_device_metric(
                device_mac=mac,
                metric_name="satisfaction",
                metric_value=float(device_data["satisfaction"]),
                unit="score",
            )
            stats["metrics_created"] += 1

        # Number of clients (for APs)
        if "num_sta" in device_data:
            self.metrics_repo.create_device_metric(
                device_mac=mac,
                metric_name="connected_clients",
                metric_value=float(device_data["num_sta"]),
                unit="count",
            )
            stats["metrics_created"] += 1

    def _collect_clients(self, stats: Dict[str, Any]) -> None:
        """
        Collect client data from controller.

        Args:
            stats: Statistics dictionary to update
        """
        try:
            logger.info(f"Fetching clients from site '{self.config.site}'")
            api_clients = self.controller.get_clients()

            if not api_clients:
                logger.info("No clients currently connected")
                return

            logger.info(f"Retrieved {len(api_clients)} clients from controller")

            # Process each client
            for client_data in api_clients:
                try:
                    self._process_client(client_data, stats)
                    stats["clients_processed"] += 1
                except Exception as e:
                    logger.error(
                        f"Error processing client {client_data.get('mac', 'unknown')}: {e}"
                    )
                    stats["errors"] += 1
                    self._error_count += 1

        except Exception as e:
            logger.error(f"Failed to fetch clients: {e}")
            stats["errors"] += 1
            self._error_count += 1
            # Don't raise - clients are optional

    def _process_client(
        self, client_data: Dict[str, Any], stats: Dict[str, Any]
    ) -> None:
        """
        Process a single client from API response.

        Args:
            client_data: Raw client data from API
            stats: Statistics dictionary to update
        """
        mac = client_data.get("mac")
        if not mac:
            logger.warning("Client missing MAC address, skipping")
            return

        # Create client model from API response
        client = UniFiClient.from_controller_response(
            client_data, site=self.config.site
        )

        # Check if client exists
        existing_client = self.client_repo.get_by_mac(mac)

        if existing_client:
            # Check for changes
            if self.config.enable_events:
                self._check_client_changes(existing_client, client, stats)

            # Update existing client
            self.client_repo.update(client)
            stats["clients_updated"] += 1
            logger.debug(f"Updated client {mac} ({client.hostname})")
        else:
            # Create new client
            self.client_repo.create(client)
            stats["clients_created"] += 1
            logger.info(f"Created new client {mac} ({client.hostname})")

            # Generate client connected event
            if self.config.enable_events:
                conn_type = "wired" if client.is_wired else "wireless"
                event = UniFiEvent(
                    event_type="client_connected",
                    severity="info",
                    title="Client Connected",
                    description=f"New {conn_type} client: {client.hostname or client.mac}",
                    client_mac=mac,
                    metadata=json.dumps(
                        {
                            "connection_type": conn_type,
                            "ap_mac": client.ap_mac,
                            "sw_mac": client.sw_mac,
                        }
                    ),
                )
                self.event_repo.create(event)
                stats["events_created"] += 1

        # Create client status record
        status = UniFiClientStatus.from_controller_response(mac, client_data)
        self.client_status_repo.create(status)
        stats["status_records"] += 1

        # Create metrics if enabled
        if self.config.enable_metrics:
            self._create_client_metrics(mac, client_data, stats)

    def _check_client_changes(
        self, old_client: UniFiClient, new_client: UniFiClient, stats: Dict[str, Any]
    ) -> None:
        """
        Check for client changes and generate events.

        Args:
            old_client: Previous client state
            new_client: New client state
            stats: Statistics dictionary to update
        """
        # Check for AP change (roaming)
        if not old_client.is_wired and not new_client.is_wired:
            if old_client.ap_mac != new_client.ap_mac:
                event = UniFiEvent(
                    event_type="client_roaming",
                    severity="info",
                    title="Client Roamed",
                    description=f"Client {new_client.hostname or new_client.mac} roamed to {new_client.ap_name}",
                    client_mac=new_client.mac,
                    previous_value=old_client.ap_name,
                    new_value=new_client.ap_name,
                )
                self.event_repo.create(event)
                stats["events_created"] += 1
                logger.info(
                    f"Client {new_client.mac} roamed: {old_client.ap_name} -> {new_client.ap_name}"
                )

        # Check for blocked status change
        if old_client.blocked != new_client.blocked:
            if new_client.blocked:
                event = UniFiEvent(
                    event_type="client_blocked",
                    severity="warning",
                    title="Client Blocked",
                    description=f"Client {new_client.hostname or new_client.mac} has been blocked",
                    client_mac=new_client.mac,
                )
                self.event_repo.create(event)
                stats["events_created"] += 1

    def _create_client_metrics(
        self, mac: str, client_data: Dict[str, Any], stats: Dict[str, Any]
    ) -> None:
        """
        Extract and store client metrics.

        Args:
            mac: Client MAC address
            client_data: Raw client data from API
            stats: Statistics dictionary to update
        """
        # Signal strength (wireless only)
        if "signal" in client_data:
            self.metrics_repo.create_client_metric(
                client_mac=mac,
                metric_name="signal_strength",
                metric_value=float(client_data["signal"]),
                unit="dbm",
            )
            stats["metrics_created"] += 1

        # RSSI (wireless only)
        if "rssi" in client_data:
            self.metrics_repo.create_client_metric(
                client_mac=mac,
                metric_name="rssi",
                metric_value=float(client_data["rssi"]),
                unit="dbm",
            )
            stats["metrics_created"] += 1

        # TX/RX rates
        if "tx_rate" in client_data:
            self.metrics_repo.create_client_metric(
                client_mac=mac,
                metric_name="tx_rate",
                metric_value=float(client_data["tx_rate"]),
                unit="kbps",
            )
            stats["metrics_created"] += 1

        if "rx_rate" in client_data:
            self.metrics_repo.create_client_metric(
                client_mac=mac,
                metric_name="rx_rate",
                metric_value=float(client_data["rx_rate"]),
                unit="kbps",
            )
            stats["metrics_created"] += 1

        # Satisfaction
        if "satisfaction" in client_data:
            self.metrics_repo.create_client_metric(
                client_mac=mac,
                metric_name="satisfaction",
                metric_value=float(client_data["satisfaction"]),
                unit="score",
            )
            stats["metrics_created"] += 1

        # Data transfer
        if "tx_bytes" in client_data:
            self.metrics_repo.create_client_metric(
                client_mac=mac,
                metric_name="tx_bytes",
                metric_value=float(client_data["tx_bytes"]),
                unit="bytes",
            )
            stats["metrics_created"] += 1

        if "rx_bytes" in client_data:
            self.metrics_repo.create_client_metric(
                client_mac=mac,
                metric_name="rx_bytes",
                metric_value=float(client_data["rx_bytes"]),
                unit="bytes",
            )
            stats["metrics_created"] += 1

    def _cleanup_old_data(self) -> None:
        """Clean up old data based on retention settings."""
        # TODO: Implement retention cleanup
        # This would delete old status records, events, and metrics
        # based on retention_days settings
        pass

    def get_stats(self) -> Dict[str, Any]:
        """
        Get collector statistics.

        Returns:
            Dictionary with collector stats
        """
        return {
            "controller_url": self.config.controller_url,
            "site": self.config.site,
            "last_collection": (
                self._last_collection.isoformat() if self._last_collection else None
            ),
            "collection_count": self._collection_count,
            "error_count": self._error_count,
            "total_devices": self.device_repo.count(),
            "total_clients": self.client_repo.count(),
            "total_events": self.event_repo.count(),
        }

    def close(self) -> None:
        """Close connections."""
        try:
            self.controller.logout()
        except Exception as e:
            logger.warning(f"Logout failed during close: {e}")

        if hasattr(self.db, "close"):
            self.db.close()
            logger.info("Database connection closed")

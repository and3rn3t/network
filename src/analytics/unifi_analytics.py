"""
UniFi Network Analytics Engine

Provides analytics and insights for UniFi network devices and clients.
Includes device health, client experience, network topology, and performance analysis.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import mean, median, stdev
from typing import Dict, List, Optional, Tuple

# Import directly from module to avoid circular import issues
import src.database.repositories.unifi_repository as unifi_repos
from src.database import Database


@dataclass
class DeviceHealthScore:
    """Health score for a UniFi device"""

    device_mac: str
    device_name: str
    device_model: str
    health_score: float  # 0-100
    cpu_score: float
    memory_score: float
    uptime_score: float
    client_score: float  # Based on number of clients vs capacity
    status: str  # 'excellent', 'good', 'fair', 'poor'


@dataclass
class ClientExperience:
    """Client experience metrics"""

    client_mac: str
    client_hostname: Optional[str]
    experience_score: float  # 0-100 (satisfaction score)
    signal_strength: float  # RSSI in dBm
    signal_quality: str  # 'excellent', 'good', 'fair', 'poor'
    avg_latency: Optional[float]
    connection_stability: float  # 0-1 (based on reconnection frequency)
    bandwidth_utilization: float  # Percentage of available bandwidth


@dataclass
class NetworkTopology:
    """Network topology analysis"""

    total_devices: int
    total_clients: int
    devices_by_type: Dict[str, int]  # 'uap', 'usw', 'ugw', etc.
    clients_per_device: Dict[str, int]  # device_mac -> client_count
    busiest_device: Optional[str]  # MAC of device with most clients
    underutilized_devices: List[str]  # MACs of devices with few clients


@dataclass
class SignalQuality:
    """Signal quality analysis for wireless clients"""

    excellent_count: int  # RSSI >= -60 dBm
    good_count: int  # -70 <= RSSI < -60
    fair_count: int  # -80 <= RSSI < -70
    poor_count: int  # RSSI < -80
    avg_rssi: float
    median_rssi: float
    weakest_clients: List[Tuple[str, float]]  # (mac, rssi)


@dataclass
class TrendAnalysis:
    """Trend analysis for UniFi metrics"""

    metric_name: str
    entity_mac: str
    entity_name: str
    direction: str  # 'up', 'down', 'stable'
    slope: float
    change_percent: float
    confidence: float


class UniFiAnalyticsEngine:
    """Analytics engine for UniFi network data"""

    def __init__(self, db: Database):
        """
        Initialize UniFi analytics engine.

        Args:
            db: Database instance
        """
        self.db = db
        self.device_repo = unifi_repos.UniFiDeviceRepository(db)
        self.device_status_repo = unifi_repos.UniFiDeviceStatusRepository(db)
        self.client_repo = unifi_repos.UniFiClientRepository(db)
        self.client_status_repo = unifi_repos.UniFiClientStatusRepository(db)
        self.event_repo = unifi_repos.UniFiEventRepository(db)
        self.metric_repo = unifi_repos.UniFiMetricRepository(db)

    def calculate_device_health(
        self, device_mac: str, hours: int = 24
    ) -> Optional[DeviceHealthScore]:
        """
        Calculate comprehensive health score for a device.

        Args:
            device_mac: Device MAC address
            hours: Number of hours to analyze

        Returns:
            DeviceHealthScore or None if device not found
        """
        device = self.device_repo.get_by_mac(device_mac)
        if not device:
            return None

        # Get recent device status
        start_time = datetime.now() - timedelta(hours=hours)
        statuses = self.device_status_repo.get_by_device(
            device_mac, start_time=start_time, limit=100
        )

        if not statuses:
            return None

        # Calculate CPU score (100 - avg CPU usage)
        cpu_values = [s.cpu_usage for s in statuses if s.cpu_usage is not None]
        cpu_score = 100 - mean(cpu_values) if cpu_values else 100.0

        # Calculate memory score (100 - avg memory usage)
        mem_values = [s.memory_usage for s in statuses if s.memory_usage is not None]
        memory_score = 100 - mean(mem_values) if mem_values else 100.0

        # Calculate uptime score (higher is better, normalize to 0-100)
        # Perfect score if uptime > 30 days
        uptime_seconds = statuses[-1].uptime if statuses else 0
        uptime_days = uptime_seconds / (24 * 3600)
        uptime_score = min(100.0, (uptime_days / 30) * 100)

        # Calculate client score based on load
        # Assume optimal is 20-40 clients per AP, adjust based on device type
        avg_clients = mean([s.num_clients for s in statuses])
        if device.model and "ap" in device.model.lower():
            # Access point - optimal 20-40 clients
            if 20 <= avg_clients <= 40:
                client_score = 100.0
            elif avg_clients < 20:
                client_score = 80.0 + (avg_clients / 20) * 20
            else:
                # Penalize overload
                client_score = max(0, 100 - (avg_clients - 40) * 2)
        else:
            # Switch/Gateway - different scoring
            client_score = 100.0

        # Calculate overall health score (weighted average)
        health_score = (
            cpu_score * 0.3
            + memory_score * 0.3
            + uptime_score * 0.2
            + client_score * 0.2
        )

        # Determine status
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 75:
            status = "good"
        elif health_score >= 60:
            status = "fair"
        else:
            status = "poor"

        return DeviceHealthScore(
            device_mac=device_mac,
            device_name=device.name or "Unknown",
            device_model=device.model or "Unknown",
            health_score=health_score,
            cpu_score=cpu_score,
            memory_score=memory_score,
            uptime_score=uptime_score,
            client_score=client_score,
            status=status,
        )

    def analyze_client_experience(
        self, client_mac: str, hours: int = 24
    ) -> Optional[ClientExperience]:
        """
        Analyze client experience and calculate satisfaction score.

        Args:
            client_mac: Client MAC address
            hours: Number of hours to analyze

        Returns:
            ClientExperience or None if client not found
        """
        client = self.client_repo.get_by_mac(client_mac)
        if not client:
            return None

        # Get recent client status
        start_time = datetime.now() - timedelta(hours=hours)
        statuses = self.client_status_repo.get_by_client(
            client_mac, start_time=start_time, limit=100
        )

        if not statuses:
            return None

        # Calculate signal strength average
        rssi_values = [s.rssi for s in statuses if s.rssi is not None]
        avg_rssi = mean(rssi_values) if rssi_values else -70.0

        # Determine signal quality
        if avg_rssi >= -60:
            signal_quality = "excellent"
            signal_score = 100.0
        elif avg_rssi >= -70:
            signal_quality = "good"
            signal_score = 80.0
        elif avg_rssi >= -80:
            signal_quality = "fair"
            signal_score = 60.0
        else:
            signal_quality = "poor"
            signal_score = 40.0

        # Calculate latency score
        latency_values = [s.latency for s in statuses if s.latency is not None]
        avg_latency = mean(latency_values) if latency_values else None
        if avg_latency:
            # Perfect score if latency < 10ms, decreasing to 0 at 100ms
            latency_score = max(0, 100 - avg_latency)
        else:
            latency_score = 80.0  # Default if no latency data

        # Calculate connection stability
        # Count reconnection events
        reconnect_events = self.event_repo.get_by_client(
            client_mac, start_time=start_time, event_type="client_connected"
        )
        reconnect_count = len(reconnect_events)

        # Perfect stability if <= 1 reconnect per day
        expected_reconnects = hours / 24
        stability = max(0, 1 - (reconnect_count - expected_reconnects) / 10)
        stability_score = stability * 100

        # Calculate bandwidth utilization
        tx_bytes = [s.tx_bytes for s in statuses if s.tx_bytes is not None]
        rx_bytes = [s.rx_bytes for s in statuses if s.rx_bytes is not None]

        if tx_bytes and rx_bytes:
            # Calculate average throughput (bytes per status interval)
            avg_tx = mean(tx_bytes)
            avg_rx = mean(rx_bytes)
            total_bytes = avg_tx + avg_rx

            # Assume 1 Gbps link capacity = 125 MB/s
            capacity_bytes = 125_000_000
            bandwidth_utilization = min(100, (total_bytes / capacity_bytes) * 100)
        else:
            bandwidth_utilization = 0.0

        # Calculate overall experience score (weighted average)
        experience_score = (
            signal_score * 0.4
            + latency_score * 0.3
            + stability_score * 0.2
            + (100 - bandwidth_utilization * 0.5) * 0.1
        )

        return ClientExperience(
            client_mac=client_mac,
            client_hostname=client.hostname,
            experience_score=experience_score,
            signal_strength=avg_rssi,
            signal_quality=signal_quality,
            avg_latency=avg_latency,
            connection_stability=stability,
            bandwidth_utilization=bandwidth_utilization,
        )

    def analyze_network_topology(self) -> NetworkTopology:
        """
        Analyze current network topology.

        Returns:
            NetworkTopology with current network structure
        """
        devices = self.device_repo.get_all()
        clients = self.client_repo.get_active_clients()

        # Count devices by type
        devices_by_type = {}
        for device in devices:
            device_type = device.device_type or "unknown"
            devices_by_type[device_type] = devices_by_type.get(device_type, 0) + 1

        # Count clients per device
        clients_per_device = {}
        for client in clients:
            ap_mac = client.ap_mac
            if ap_mac:
                clients_per_device[ap_mac] = clients_per_device.get(ap_mac, 0) + 1

        # Find busiest device
        busiest_device = None
        max_clients = 0
        for device_mac, client_count in clients_per_device.items():
            if client_count > max_clients:
                max_clients = client_count
                busiest_device = device_mac

        # Find underutilized devices (APs with < 5 clients)
        underutilized = []
        for device in devices:
            if device.device_type == "uap":
                client_count = clients_per_device.get(device.mac, 0)
                if client_count < 5:
                    underutilized.append(device.mac)

        return NetworkTopology(
            total_devices=len(devices),
            total_clients=len(clients),
            devices_by_type=devices_by_type,
            clients_per_device=clients_per_device,
            busiest_device=busiest_device,
            underutilized_devices=underutilized,
        )

    def analyze_signal_quality(self) -> SignalQuality:
        """
        Analyze signal quality across all wireless clients.

        Returns:
            SignalQuality with distribution and statistics
        """
        clients = self.client_repo.get_active_clients()

        # Get RSSI values for wireless clients
        rssi_values = []
        client_rssi = []

        for client in clients:
            # Get latest status
            statuses = self.client_status_repo.get_by_client(client.mac, limit=1)
            if statuses and statuses[0].rssi is not None:
                rssi = statuses[0].rssi
                rssi_values.append(rssi)
                client_rssi.append((client.mac, rssi))

        if not rssi_values:
            return SignalQuality(
                excellent_count=0,
                good_count=0,
                fair_count=0,
                poor_count=0,
                avg_rssi=0.0,
                median_rssi=0.0,
                weakest_clients=[],
            )

        # Categorize by quality
        excellent = sum(1 for rssi in rssi_values if rssi >= -60)
        good = sum(1 for rssi in rssi_values if -70 <= rssi < -60)
        fair = sum(1 for rssi in rssi_values if -80 <= rssi < -70)
        poor = sum(1 for rssi in rssi_values if rssi < -80)

        # Find weakest clients
        client_rssi_sorted = sorted(client_rssi, key=lambda x: x[1])
        weakest = client_rssi_sorted[:5]  # Top 5 weakest

        return SignalQuality(
            excellent_count=excellent,
            good_count=good,
            fair_count=fair,
            poor_count=poor,
            avg_rssi=mean(rssi_values),
            median_rssi=median(rssi_values),
            weakest_clients=weakest,
        )

    def detect_metric_trend(
        self, entity_mac: str, metric_name: str, hours: int = 24
    ) -> Optional[TrendAnalysis]:
        """
        Detect trend in UniFi metrics using linear regression.

        Args:
            entity_mac: Device or client MAC address
            metric_name: Metric name (e.g., 'cpu', 'memory', 'tx_bytes')
            hours: Number of hours to analyze

        Returns:
            TrendAnalysis or None if insufficient data
        """
        start_time = datetime.now() - timedelta(hours=hours)
        metrics = self.metric_repo.get_by_entity(
            entity_mac, metric_name=metric_name, start_time=start_time, limit=1000
        )

        if not metrics or len(metrics) < 3:
            return None

        # Get entity name
        device = self.device_repo.get_by_mac(entity_mac)
        if device:
            entity_name = device.name or "Unknown Device"
        else:
            client = self.client_repo.get_by_mac(entity_mac)
            entity_name = client.hostname if client else "Unknown Client"

        # Extract values and timestamps
        data_points = []
        for m in metrics:
            hours_since_start = (m.timestamp - start_time).total_seconds() / 3600
            data_points.append((hours_since_start, m.value))

        # Simple linear regression
        n = len(data_points)
        x_values = [p[0] for p in data_points]
        y_values = [p[1] for p in data_points]

        x_mean = mean(x_values)
        y_mean = mean(y_values)

        # Calculate slope
        numerator = sum(
            (x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n)
        )
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            slope = 0.0
        else:
            slope = numerator / denominator

        # Calculate R-squared for confidence
        y_pred = [y_mean + slope * (x - x_mean) for x in x_values]
        ss_res = sum((y_values[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((y - y_mean) ** 2 for y in y_values)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Determine trend direction
        # Slope is in units per hour
        if abs(slope) < 0.01:  # Threshold for "stable"
            direction = "stable"
        elif slope > 0:
            direction = "up"
        else:
            direction = "down"

        # Calculate percent change
        if y_values[0] > 0:
            change_percent = ((y_values[-1] - y_values[0]) / y_values[0]) * 100
        else:
            change_percent = 0.0

        return TrendAnalysis(
            metric_name=metric_name,
            entity_mac=entity_mac,
            entity_name=entity_name,
            direction=direction,
            slope=slope,
            change_percent=change_percent,
            confidence=max(0.0, min(1.0, r_squared)),
        )

    def get_network_health_summary(self, hours: int = 24) -> Dict:
        """
        Get comprehensive network health summary.

        Args:
            hours: Number of hours to analyze

        Returns:
            Dictionary with network-wide health metrics
        """
        devices = self.device_repo.get_all()
        active_clients = self.client_repo.get_active_clients()

        # Calculate device health scores
        device_health_scores = []
        unhealthy_devices = []

        for device in devices:
            health = self.calculate_device_health(device.mac, hours=hours)
            if health:
                device_health_scores.append(health.health_score)
                if health.health_score < 75:
                    unhealthy_devices.append(
                        {
                            "mac": device.mac,
                            "name": device.name,
                            "score": health.health_score,
                        }
                    )

        # Calculate client experience scores
        client_experience_scores = []
        poor_experience_clients = []

        # Sample up to 100 clients for performance
        sample_clients = active_clients[:100]
        for client in sample_clients:
            experience = self.analyze_client_experience(client.mac, hours=hours)
            if experience:
                client_experience_scores.append(experience.experience_score)
                if experience.experience_score < 70:
                    poor_experience_clients.append(
                        {
                            "mac": client.mac,
                            "hostname": client.hostname,
                            "score": experience.experience_score,
                        }
                    )

        # Get signal quality
        signal_quality = self.analyze_signal_quality()

        # Get topology
        topology = self.analyze_network_topology()

        # Get event counts
        start_time = datetime.now() - timedelta(hours=hours)
        events = self.event_repo.get_by_time_range(start_time, datetime.now())
        event_counts = {}
        for event in events:
            event_type = event.event_type
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        return {
            "timestamp": datetime.now().isoformat(),
            "analysis_period_hours": hours,
            "devices": {
                "total": len(devices),
                "avg_health_score": (
                    mean(device_health_scores) if device_health_scores else None
                ),
                "unhealthy_count": len(unhealthy_devices),
                "unhealthy_devices": unhealthy_devices,
            },
            "clients": {
                "total_active": len(active_clients),
                "avg_experience_score": (
                    mean(client_experience_scores) if client_experience_scores else None
                ),
                "poor_experience_count": len(poor_experience_clients),
                "poor_experience_clients": poor_experience_clients,
            },
            "signal_quality": {
                "excellent": signal_quality.excellent_count,
                "good": signal_quality.good_count,
                "fair": signal_quality.fair_count,
                "poor": signal_quality.poor_count,
                "avg_rssi": signal_quality.avg_rssi,
            },
            "topology": {
                "devices_by_type": topology.devices_by_type,
                "busiest_device": topology.busiest_device,
                "underutilized_devices": topology.underutilized_devices,
            },
            "events": {
                "total": len(events),
                "by_type": event_counts,
            },
        }

"""
Analytics Engine for UniFi Network Data

Provides statistical analysis, trend detection, anomaly detection,
and capacity planning for network devices.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import mean, median, stdev
from typing import Dict, List, Optional, Tuple

from src.database import Database
from src.database.models import Metric
from src.database.repositories import EventRepository, HostRepository, MetricRepository


@dataclass
class Statistics:
    """Statistical summary of a metric"""

    mean: float
    median: float
    min: float
    max: float
    stddev: float
    count: int


@dataclass
class TrendAnalysis:
    """Trend analysis result"""

    metric_name: str
    direction: str  # 'up', 'down', 'stable'
    slope: float
    confidence: float  # 0.0 to 1.0
    change_percent: float


@dataclass
class Anomaly:
    """Detected anomaly in metrics"""

    timestamp: datetime
    host_id: str
    host_name: str
    metric_name: str
    value: float
    expected_range: Tuple[float, float]
    severity: str  # 'low', 'medium', 'high'
    description: str


@dataclass
class CapacityForecast:
    """Capacity planning forecast"""

    metric_name: str
    current_value: float
    predicted_value: float
    days_until_threshold: Optional[int]
    threshold: float
    confidence: float


class AnalyticsEngine:
    """Main analytics engine for network data analysis"""

    def __init__(self, db: Database):
        self.db = db
        self.host_repo = HostRepository(db)
        self.metric_repo = MetricRepository(db)
        self.event_repo = EventRepository(db)

    def calculate_statistics(
        self, host_id: str, metric_name: str, days: int = 7
    ) -> Optional[Statistics]:
        """
        Calculate statistical summary for a metric.

        Args:
            host_id: Host ID
            metric_name: Name of metric ('cpu', 'memory', 'temperature', 'uptime')
            days: Number of days to analyze

        Returns:
            Statistics object or None if no data
        """
        # Get metrics for time range
        start_time = datetime.now() - timedelta(days=days)
        metrics = self.metric_repo.get_by_time_range(
            host_id=host_id,
            start_time=start_time,
            end_time=datetime.now(),
            metric_name=metric_name,
        )

        if not metrics:
            return None

        # Extract values
        values = [m.metric_value for m in metrics]

        if not values or len(values) < 2:
            return None

        return Statistics(
            mean=mean(values),
            median=median(values),
            min=min(values),
            max=max(values),
            stddev=stdev(values) if len(values) > 1 else 0.0,
            count=len(values),
        )

    def detect_trend(
        self, host_id: str, metric_name: str, days: int = 7
    ) -> Optional[TrendAnalysis]:
        """
        Detect trend in metric data using linear regression.

        Args:
            host_id: Host ID
            metric_name: Name of metric
            days: Number of days to analyze

        Returns:
            TrendAnalysis object or None if insufficient data
        """
        start_time = datetime.now() - timedelta(days=days)
        metrics = self.metric_repo.get_by_time_range(
            host_id=host_id,
            start_time=start_time,
            end_time=datetime.now(),
            metric_name=metric_name,
        )

        if not metrics:
            return None

        # Extract values and timestamps
        data_points = []
        for m in metrics:
            if m.metric_value is not None:
                # Convert timestamp to numeric (hours since start)
                ts = datetime.fromisoformat(m.recorded_at)
                hours = (ts - start_time).total_seconds() / 3600
                data_points.append((hours, m.metric_value))

        if len(data_points) < 3:
            return None

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
        # Slope is in units per hour, so convert to units per day
        daily_slope = slope * 24

        if abs(daily_slope) < 0.1:  # Less than 0.1% change per day
            direction = "stable"
        elif daily_slope > 0:
            direction = "up"
        else:
            direction = "down"

        # Calculate percent change over the period
        if y_values[0] > 0:
            change_percent = ((y_values[-1] - y_values[0]) / y_values[0]) * 100
        else:
            change_percent = 0.0

        return TrendAnalysis(
            metric_name=metric_name,
            direction=direction,
            slope=daily_slope,
            confidence=max(0.0, min(1.0, r_squared)),
            change_percent=change_percent,
        )

    def detect_anomalies(
        self,
        host_id: str,
        metric_name: str,
        days: int = 7,
        threshold_sigma: float = 2.0,
    ) -> List[Anomaly]:
        """
        Detect anomalies using statistical methods (Z-score).

        Args:
            host_id: Host ID
            metric_name: Name of metric
            days: Number of days to analyze
            threshold_sigma: Number of standard deviations for anomaly

        Returns:
            List of detected anomalies
        """
        start_time = datetime.now() - timedelta(days=days)
        metrics = self.metric_repo.get_by_time_range(
            host_id=host_id,
            start_time=start_time,
            end_time=datetime.now(),
            metric_name=metric_name,
        )

        if not metrics:
            return []

        # Extract values
        values = [(m.recorded_at, m.metric_value) for m in metrics]

        if len(values) < 10:  # Need enough data
            return []

        # Calculate mean and standard deviation
        val_list = [v[1] for v in values]
        avg = mean(val_list)
        std = stdev(val_list) if len(val_list) > 1 else 0

        if std == 0:
            return []

        # Find anomalies
        anomalies = []
        host = self.host_repo.get_by_id(host_id)
        host_name = host.name if (host and host.name) else "Unknown"

        expected_min = avg - (threshold_sigma * std)
        expected_max = avg + (threshold_sigma * std)

        for timestamp, value in values:
            if value < expected_min or value > expected_max:
                # Calculate Z-score for severity
                z_score = abs((value - avg) / std)

                if z_score > 3.0:
                    severity = "high"
                elif z_score > 2.5:
                    severity = "medium"
                else:
                    severity = "low"

                if value > expected_max:
                    desc = (
                        f"{metric_name.capitalize()} unusually high: "
                        f"{value:.1f} (expected: {expected_max:.1f})"
                    )
                else:
                    desc = (
                        f"{metric_name.capitalize()} unusually low: "
                        f"{value:.1f} (expected: {expected_min:.1f})"
                    )

                anomalies.append(
                    Anomaly(
                        timestamp=datetime.fromisoformat(timestamp),
                        host_id=host_id,
                        host_name=host_name,
                        metric_name=metric_name,
                        value=value,
                        expected_range=(expected_min, expected_max),
                        severity=severity,
                        description=desc,
                    )
                )

        return anomalies

    def forecast_capacity(
        self,
        host_id: str,
        metric_name: str,
        threshold: float,
        days: int = 30,
    ) -> Optional[CapacityForecast]:
        """
        Forecast when a metric will reach a threshold (capacity planning).

        Args:
            host_id: Host ID
            metric_name: Name of metric
            threshold: Threshold value (e.g., 90 for 90% capacity)
            days: Number of days of historical data to use

        Returns:
            CapacityForecast object or None if insufficient data
        """
        # Get trend analysis
        trend = self.detect_trend(host_id, metric_name, days=days)

        if not trend or trend.direction != "up":
            return None

        # Get current value
        metrics = self.metric_repo.get_by_host_id(host_id, limit=1)
        if not metrics:
            return None

        # Filter for the specific metric name
        current_metrics = [m for m in metrics if m.metric_name == metric_name]
        if not current_metrics:
            return None

        current_value = current_metrics[0].metric_value

        if current_value is None or current_value >= threshold:
            return None

        # Calculate days until threshold
        # slope is in units per day
        if trend.slope <= 0:
            days_until_threshold = None
            predicted_value = current_value
        else:
            days_until_threshold = int((threshold - current_value) / trend.slope)
            predicted_value = current_value + (trend.slope * days_until_threshold)

        return CapacityForecast(
            metric_name=metric_name,
            current_value=current_value,
            predicted_value=min(predicted_value, 100.0),  # Cap at 100%
            days_until_threshold=days_until_threshold,
            threshold=threshold,
            confidence=trend.confidence,
        )

    def get_host_health_score(self, host_id: str, days: int = 7) -> Optional[float]:
        """
        Calculate overall health score for a host (0-100).

        Considers:
        - CPU usage (lower is better)
        - Memory usage (lower is better)
        - Temperature (lower is better)
        - Uptime (higher is better)
        - Number of anomalies (fewer is better)

        Args:
            host_id: Host ID
            days: Number of days to analyze

        Returns:
            Health score (0-100) or None if insufficient data
        """
        scores = []

        # CPU score (100 - avg CPU usage)
        cpu_stats = self.calculate_statistics(host_id, "cpu", days)
        if cpu_stats:
            cpu_score = max(0, 100 - cpu_stats.mean)
            scores.append(cpu_score)

        # Memory score (100 - avg memory usage)
        mem_stats = self.calculate_statistics(host_id, "memory", days)
        if mem_stats:
            mem_score = max(0, 100 - mem_stats.mean)
            scores.append(mem_score)

        # Temperature score (100 if < 50°C, decreasing to 0 at 90°C)
        temp_stats = self.calculate_statistics(host_id, "temperature", days)
        if temp_stats:
            if temp_stats.mean < 50:
                temp_score = 100
            elif temp_stats.mean > 90:
                temp_score = 0
            else:
                temp_score = 100 - ((temp_stats.mean - 50) / 40) * 100
            scores.append(temp_score)

        # Anomaly score (penalize anomalies)
        cpu_anomalies = self.detect_anomalies(host_id, "cpu", days)
        mem_anomalies = self.detect_anomalies(host_id, "memory", days)
        total_anomalies = len(cpu_anomalies) + len(mem_anomalies)

        # Deduct 5 points per anomaly, minimum 0
        anomaly_penalty = min(50, total_anomalies * 5)
        anomaly_score = 100 - anomaly_penalty
        scores.append(anomaly_score)

        if not scores:
            return None

        # Return average of all scores
        return mean(scores)

    def get_network_summary(self, days: int = 7) -> Dict:
        """
        Get comprehensive network analytics summary.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with network-wide statistics
        """
        hosts = self.host_repo.get_all()
        online_hosts = self.host_repo.get_online_hosts()
        offline_hosts = self.host_repo.get_offline_hosts()

        # Calculate health scores for all online hosts
        health_scores = []
        for host in online_hosts:
            score = self.get_host_health_score(host.id, days)
            if score is not None:
                health_scores.append(score)

        # Get event counts
        start_time = datetime.now() - timedelta(days=days)
        event_counts = self.event_repo.get_event_counts(start_time, datetime.now())

        return {
            "total_hosts": len(hosts),
            "active_hosts": len(online_hosts),
            "offline_hosts": len(offline_hosts),
            "avg_health_score": mean(health_scores) if health_scores else None,
            "min_health_score": min(health_scores) if health_scores else None,
            "max_health_score": max(health_scores) if health_scores else None,
            "total_events": sum(event_counts.values()),
            "event_breakdown": event_counts,
            "analysis_period_days": days,
        }

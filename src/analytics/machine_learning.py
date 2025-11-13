"""
Machine Learning Module for Network Analytics

Provides ML-based analysis including:
- Anomaly detection using Isolation Forest
- Device failure prediction
- Client behavior pattern recognition
- Traffic classification
"""

from dataclasses import dataclass
from datetime import datetime
from statistics import mean, stdev
from typing import List, Optional, Tuple

import numpy as np


@dataclass
class Anomaly:
    """Detected anomaly in network data"""

    timestamp: datetime
    entity_id: str
    entity_name: str
    metric_name: str
    value: float
    expected_range: Tuple[float, float]
    anomaly_score: float  # -1 to 1 (higher is more anomalous)
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str


@dataclass
class FailurePrediction:
    """Device failure prediction result"""

    device_id: str
    device_name: str
    failure_probability: float  # 0.0 to 1.0
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    time_to_failure_days: Optional[int]
    contributing_factors: List[str]
    recommendation: str


@dataclass
class ClientPattern:
    """Client behavior pattern"""

    pattern_type: str  # 'heavy_user', 'intermittent', 'stable', 'problematic'
    client_count: int
    avg_bandwidth_mbps: float
    avg_session_duration_hours: float
    typical_hours: List[int]  # Hours of day when active
    characteristics: List[str]


@dataclass
class TrafficClassification:
    """Network traffic classification"""

    classification: str  # 'video', 'gaming', 'browsing', 'file_transfer', 'voip'
    confidence: float
    bandwidth_mbps: float
    packet_pattern: str
    protocol_hints: List[str]


class IsolationForest:
    """
    Simplified Isolation Forest for anomaly detection.

    Uses random partitioning to isolate anomalies.
    """

    def __init__(self, n_trees: int = 100, max_samples: int = 256):
        """
        Initialize isolation forest.

        Args:
            n_trees: Number of isolation trees
            max_samples: Maximum samples per tree
        """
        self.n_trees = n_trees
        self.max_samples = max_samples
        self.trees: List[dict] = []

    def fit(self, data: np.ndarray):
        """
        Train the isolation forest.

        Args:
            data: Training data (n_samples, n_features)
        """
        n_samples = len(data)
        sample_size = min(self.max_samples, n_samples)

        self.trees = []
        for _ in range(self.n_trees):
            # Random sample
            indices = np.random.choice(n_samples, sample_size, replace=False)
            sample_data = data[indices]

            # Build isolation tree (simplified)
            tree = self._build_tree(sample_data, depth=0)
            self.trees.append(tree)

    def _build_tree(self, data: np.ndarray, depth: int, max_depth: int = 10):
        """
        Build an isolation tree recursively.

        Args:
            data: Data to partition
            depth: Current tree depth
            max_depth: Maximum tree depth

        Returns:
            Tree node (dict)
        """
        if depth >= max_depth or len(data) <= 1:
            return {"type": "leaf", "size": len(data)}

        # Random split
        n_features = data.shape[1]
        split_feature = np.random.randint(0, n_features)
        feature_vals = data[:, split_feature]

        if len(np.unique(feature_vals)) <= 1:
            return {"type": "leaf", "size": len(data)}

        split_value = np.random.uniform(feature_vals.min(), feature_vals.max())

        # Partition data
        left_mask = feature_vals < split_value
        right_mask = ~left_mask

        left_data = data[left_mask]
        right_data = data[right_mask]

        if len(left_data) == 0 or len(right_data) == 0:
            return {"type": "leaf", "size": len(data)}

        return {
            "type": "split",
            "feature": split_feature,
            "value": split_value,
            "left": self._build_tree(left_data, depth + 1, max_depth),
            "right": self._build_tree(right_data, depth + 1, max_depth),
        }

    def _path_length(self, point: np.ndarray, tree: dict, depth: int = 0) -> float:
        """
        Calculate path length for a point in a tree.

        Args:
            point: Data point
            tree: Isolation tree
            depth: Current depth

        Returns:
            Path length
        """
        if tree["type"] == "leaf":
            # Average path length of unsuccessful search in BST
            size = tree["size"]
            if size <= 1:
                return depth
            # c(n) = 2H(n-1) - 2(n-1)/n where H(n) is harmonic number
            c_n = 2 * (np.log(size - 1) + 0.5772) - 2 * (size - 1) / size
            return depth + c_n

        feature = tree["feature"]
        value = tree["value"]

        if point[feature] < value:
            return self._path_length(point, tree["left"], depth + 1)
        else:
            return self._path_length(point, tree["right"], depth + 1)

    def predict(self, data: np.ndarray) -> np.ndarray:
        """
        Predict anomaly scores for data.

        Args:
            data: Data to score (n_samples, n_features)

        Returns:
            Anomaly scores (-1 to 1, higher is more anomalous)
        """
        n_samples = len(data)
        scores = np.zeros(n_samples)

        for i, point in enumerate(data):
            # Average path length across all trees
            avg_path = mean([self._path_length(point, tree) for tree in self.trees])

            # Normalize score
            # c(n) for the training sample size
            c_n = (
                2 * (np.log(self.max_samples - 1) + 0.5772)
                - 2 * (self.max_samples - 1) / self.max_samples
            )

            # Anomaly score: 2^(-E(h(x))/c(n))
            # Subtract 0.5 to center around 0, then scale to -1 to 1
            score = 2 ** (-avg_path / c_n)
            scores[i] = (score - 0.5) * 2

        return scores


class AnomalyDetector:
    """
    Anomaly detection for network metrics.

    Uses isolation forest and statistical methods to detect anomalies.
    """

    def __init__(self):
        """Initialize anomaly detector."""
        self.isolation_forest = IsolationForest()
        self.is_fitted = False

    def fit(self, data: List[float]):
        """
        Train anomaly detector on historical data.

        Args:
            data: Historical metric values
        """
        if len(data) < 10:
            return  # Need minimum data to train

        # Convert to numpy array
        data_array = np.array(data).reshape(-1, 1)

        # Train isolation forest
        self.isolation_forest.fit(data_array)
        self.is_fitted = True

    def detect_anomalies(
        self,
        metric_name: str,
        values: List[float],
        timestamps: List[datetime],
        entity_id: str = "",
        entity_name: str = "",
    ) -> List[Anomaly]:
        """
        Detect anomalies in metric data.

        Args:
            metric_name: Name of the metric
            values: Metric values
            timestamps: Timestamps for each value
            entity_id: Entity (device/client) ID
            entity_name: Entity name

        Returns:
            List of detected anomalies
        """
        if len(values) < 10:
            return []

        anomalies = []

        # Calculate statistical baseline
        mean_val = mean(values)
        std_val = stdev(values) if len(values) > 1 else 0

        # Statistical method: values beyond 3 standard deviations
        for i, (val, ts) in enumerate(zip(values, timestamps)):
            z_score = (val - mean_val) / std_val if std_val > 0 else 0

            if abs(z_score) > 3:
                severity = self._classify_severity(abs(z_score))
                anomalies.append(
                    Anomaly(
                        timestamp=ts,
                        entity_id=entity_id,
                        entity_name=entity_name,
                        metric_name=metric_name,
                        value=val,
                        expected_range=(
                            mean_val - 2 * std_val,
                            mean_val + 2 * std_val,
                        ),
                        anomaly_score=min(1.0, abs(z_score) / 5),
                        severity=severity,
                        description=f"{metric_name} value {val:.2f} is {abs(z_score):.1f}σ from mean ({mean_val:.2f})",
                    )
                )

        # ML method: isolation forest
        if self.is_fitted:
            data_array = np.array(values).reshape(-1, 1)
            scores = self.isolation_forest.predict(data_array)

            for i, (val, ts, score) in enumerate(zip(values, timestamps, scores)):
                if score > 0.6:  # High anomaly score threshold
                    # Skip if already detected by statistical method
                    if any(a.timestamp == ts for a in anomalies):
                        continue

                    severity = self._classify_severity_from_score(score)
                    anomalies.append(
                        Anomaly(
                            timestamp=ts,
                            entity_id=entity_id,
                            entity_name=entity_name,
                            metric_name=metric_name,
                            value=val,
                            expected_range=(
                                mean_val - std_val,
                                mean_val + std_val,
                            ),
                            anomaly_score=score,
                            severity=severity,
                            description=f"{metric_name} shows unusual pattern (ML score: {score:.2f})",
                        )
                    )

        return sorted(anomalies, key=lambda x: x.timestamp)

    def _classify_severity(self, z_score: float) -> str:
        """Classify anomaly severity based on z-score."""
        if z_score >= 5:
            return "critical"
        elif z_score >= 4:
            return "high"
        elif z_score >= 3:
            return "medium"
        else:
            return "low"

    def _classify_severity_from_score(self, score: float) -> str:
        """Classify anomaly severity based on ML score."""
        if score >= 0.9:
            return "critical"
        elif score >= 0.8:
            return "high"
        elif score >= 0.7:
            return "medium"
        else:
            return "low"


class FailurePredictor:
    """
    Device failure prediction using multiple indicators.

    Analyzes device health metrics to predict potential failures.
    """

    def predict_failure(
        self,
        device_id: str,
        device_name: str,
        uptime_days: float,
        restart_count: int,
        cpu_history: List[float],
        memory_history: List[float],
        temperature_history: List[float],
    ) -> FailurePrediction:
        """
        Predict device failure probability.

        Args:
            device_id: Device ID
            device_name: Device name
            uptime_days: Current uptime in days
            restart_count: Number of restarts (last 30 days)
            cpu_history: CPU usage history (%)
            memory_history: Memory usage history (%)
            temperature_history: Temperature history (°C)

        Returns:
            FailurePrediction with risk assessment
        """
        risk_factors = []
        failure_score = 0.0

        # Factor 1: Frequent restarts (10-30 points)
        if restart_count > 5:
            risk_factors.append(f"Frequent restarts ({restart_count} in 30 days)")
            failure_score += min(30, restart_count * 3)

        # Factor 2: High CPU usage (0-20 points)
        if cpu_history:
            avg_cpu = mean(cpu_history)
            if avg_cpu > 80:
                risk_factors.append(f"High CPU usage (avg {avg_cpu:.1f}%)")
                failure_score += min(20, (avg_cpu - 80) * 2)

        # Factor 3: High memory usage (0-20 points)
        if memory_history:
            avg_memory = mean(memory_history)
            if avg_memory > 85:
                risk_factors.append(f"High memory usage (avg {avg_memory:.1f}%)")
                failure_score += min(20, (avg_memory - 85) * 2)

        # Factor 4: High temperature (0-30 points)
        if temperature_history:
            avg_temp = mean(temperature_history)
            max_temp = max(temperature_history)
            if avg_temp > 70:
                risk_factors.append(f"High temperature (avg {avg_temp:.1f}°C)")
                failure_score += min(20, (avg_temp - 70) * 2)
            if max_temp > 85:
                risk_factors.append(f"Critical temperature spike ({max_temp:.1f}°C)")
                failure_score += 10

        # Factor 5: Very long uptime without reboot (0-10 points)
        if uptime_days > 365:
            risk_factors.append(f"Extended uptime ({uptime_days:.0f} days)")
            failure_score += 10

        # Calculate failure probability (0-100 scale to 0-1)
        failure_probability = min(1.0, failure_score / 100)

        # Classify risk level
        if failure_probability >= 0.7:
            risk_level = "critical"
            time_to_failure = 7  # days
            recommendation = (
                "⚠️ CRITICAL: Device shows multiple failure indicators. "
                "Schedule immediate maintenance or replacement."
            )
        elif failure_probability >= 0.5:
            risk_level = "high"
            time_to_failure = 30
            recommendation = (
                "⚠️ HIGH RISK: Device health is degraded. Plan maintenance "
                "within 30 days and monitor closely."
            )
        elif failure_probability >= 0.3:
            risk_level = "medium"
            time_to_failure = 90
            recommendation = (
                "Medium risk detected. Monitor device health and plan "
                "maintenance within 90 days."
            )
        else:
            risk_level = "low"
            time_to_failure = None
            recommendation = "Device health is good. Continue routine monitoring."

        return FailurePrediction(
            device_id=device_id,
            device_name=device_name,
            failure_probability=failure_probability,
            risk_level=risk_level,
            time_to_failure_days=time_to_failure,
            contributing_factors=risk_factors,
            recommendation=recommendation,
        )


class ClientBehaviorAnalyzer:
    """
    Analyze client behavior patterns.

    Classifies clients into behavior categories for better network planning.
    """

    def classify_client_pattern(
        self,
        bandwidth_history: List[float],  # Mbps
        session_durations: List[float],  # hours
        connection_times: List[datetime],
    ) -> ClientPattern:
        """
        Classify client behavior pattern.

        Args:
            bandwidth_history: Bandwidth usage history (Mbps)
            session_durations: Session duration history (hours)
            connection_times: Connection timestamps

        Returns:
            ClientPattern classification
        """
        if not bandwidth_history or not session_durations:
            return ClientPattern(
                pattern_type="unknown",
                client_count=1,
                avg_bandwidth_mbps=0,
                avg_session_duration_hours=0,
                typical_hours=[],
                characteristics=["Insufficient data"],
            )

        avg_bandwidth = mean(bandwidth_history)
        avg_duration = mean(session_durations)

        # Determine typical connection hours
        hours = [dt.hour for dt in connection_times]
        hour_counts = {h: hours.count(h) for h in range(24)}
        typical_hours = sorted(hour_counts.keys(), key=lambda h: hour_counts[h], reverse=True)[:8]

        characteristics = []

        # Classify pattern
        if avg_bandwidth > 50:
            pattern_type = "heavy_user"
            characteristics.append("High bandwidth consumption")
        elif avg_duration < 1:
            pattern_type = "intermittent"
            characteristics.append("Short, frequent sessions")
        elif len(bandwidth_history) > 10 and stdev(bandwidth_history) < 5:
            pattern_type = "stable"
            characteristics.append("Consistent usage pattern")
        else:
            pattern_type = "normal"
            characteristics.append("Typical usage")

        # Add more characteristics
        if avg_duration > 8:
            characteristics.append("Long session durations")

        peak_hours = [h for h in typical_hours if 9 <= h <= 17]
        if len(peak_hours) > 4:
            characteristics.append("Business hours usage")
        else:
            characteristics.append("Off-hours usage")

        return ClientPattern(
            pattern_type=pattern_type,
            client_count=1,
            avg_bandwidth_mbps=avg_bandwidth,
            avg_session_duration_hours=avg_duration,
            typical_hours=typical_hours,
            characteristics=characteristics,
        )

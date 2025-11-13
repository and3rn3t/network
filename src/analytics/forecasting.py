"""
Time-Series Forecasting Module

Provides forecasting capabilities for network metrics including:
- Exponential smoothing for short-term predictions
- Linear regression for trend analysis
- Capacity planning predictions
- Resource saturation forecasting
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import mean
from typing import List, Optional, Tuple

import numpy as np


@dataclass
class ForecastPoint:
    """A single point in a forecast"""

    timestamp: datetime
    predicted_value: float
    confidence_lower: float
    confidence_upper: float
    confidence_level: float  # 0.0 to 1.0


@dataclass
class CapacityForecast:
    """Capacity planning forecast result"""

    metric_name: str
    current_value: float
    current_capacity: float
    predicted_value: float
    days_until_threshold: Optional[int]
    threshold_value: float
    utilization_percent: float
    forecast_points: List[ForecastPoint]
    recommendation: str


@dataclass
class TrendForecast:
    """Trend-based forecast result"""

    metric_name: str
    current_value: float
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    daily_change_rate: float
    predicted_7d: float
    predicted_30d: float
    predicted_90d: float
    confidence: float


class ExponentialSmoother:
    """
    Exponential smoothing for time-series forecasting.

    Uses triple exponential smoothing (Holt-Winters) for data with trends.
    """

    def __init__(self, alpha: float = 0.3, beta: float = 0.1):
        """
        Initialize exponential smoother.

        Args:
            alpha: Smoothing factor for level (0.0 to 1.0)
            beta: Smoothing factor for trend (0.0 to 1.0)
        """
        self.alpha = alpha
        self.beta = beta

    def smooth(self, values: List[float]) -> List[float]:
        """
        Apply exponential smoothing to values.

        Args:
            values: Time-series values

        Returns:
            Smoothed values
        """
        if len(values) < 2:
            return values

        smoothed = [values[0]]
        level = values[0]
        trend = values[1] - values[0] if len(values) > 1 else 0

        for i in range(1, len(values)):
            prev_level = level
            level = self.alpha * values[i] + (1 - self.alpha) * (level + trend)
            trend = self.beta * (level - prev_level) + (1 - self.beta) * trend
            smoothed.append(level)

        return smoothed

    def forecast(
        self, values: List[float], periods: int
    ) -> Tuple[List[float], List[float], List[float]]:
        """
        Forecast future values with confidence intervals.

        Args:
            values: Historical time-series values
            periods: Number of periods to forecast

        Returns:
            Tuple of (forecasts, lower_bounds, upper_bounds)
        """
        if len(values) < 3:
            # Not enough data, return simple extrapolation
            avg = mean(values)
            return (
                [avg] * periods,
                [avg * 0.9] * periods,
                [avg * 1.1] * periods,
            )

        # Initialize level and trend
        level = values[0]
        trend = (values[-1] - values[0]) / (len(values) - 1)

        # Apply smoothing to get current level and trend
        for value in values[1:]:
            prev_level = level
            level = self.alpha * value + (1 - self.alpha) * (level + trend)
            trend = self.beta * (level - prev_level) + (1 - self.beta) * trend

        # Generate forecasts
        forecasts = []
        for i in range(periods):
            forecast = level + (i + 1) * trend
            forecasts.append(forecast)

        # Calculate confidence intervals based on historical error
        errors = []
        smoothed = self.smooth(values)
        for i in range(len(values)):
            errors.append(abs(values[i] - smoothed[i]))

        std_error = np.std(errors) if errors else 0.1 * abs(level)

        # Confidence intervals widen with forecast horizon
        lower_bounds = []
        upper_bounds = []
        for i, forecast in enumerate(forecasts):
            margin = std_error * (1 + 0.1 * i)  # Widen with horizon
            lower_bounds.append(max(0, forecast - 1.96 * margin))
            upper_bounds.append(forecast + 1.96 * margin)

        return forecasts, lower_bounds, upper_bounds


class NetworkForecaster:
    """
    Network metrics forecasting engine.

    Provides capacity planning and resource forecasting for network infrastructure.
    """

    def __init__(self):
        """Initialize network forecaster."""
        self.smoother = ExponentialSmoother()

    def forecast_metric(
        self,
        values: List[float],
        timestamps: List[datetime],
        forecast_days: int = 30,
    ) -> List[ForecastPoint]:
        """
        Forecast a metric into the future.

        Args:
            values: Historical metric values
            timestamps: Timestamps for each value
            forecast_days: Number of days to forecast

        Returns:
            List of forecast points
        """
        if len(values) < 3:
            return []

        # Calculate time intervals
        if len(timestamps) > 1:
            avg_interval = (timestamps[-1] - timestamps[0]) / (len(timestamps) - 1)
        else:
            avg_interval = timedelta(hours=1)

        # Determine how many periods to forecast
        periods = int(forecast_days * 24 / (avg_interval.total_seconds() / 3600))

        # Generate forecasts
        forecasts, lower, upper = self.smoother.forecast(values, periods)

        # Create forecast points
        forecast_points = []
        last_timestamp = timestamps[-1] if timestamps else datetime.now()

        for i in range(periods):
            timestamp = last_timestamp + avg_interval * (i + 1)
            # Confidence decreases with forecast horizon
            confidence = max(0.5, 1.0 - (i / periods) * 0.5)

            forecast_points.append(
                ForecastPoint(
                    timestamp=timestamp,
                    predicted_value=forecasts[i],
                    confidence_lower=lower[i],
                    confidence_upper=upper[i],
                    confidence_level=confidence,
                )
            )

        return forecast_points

    def forecast_capacity(
        self,
        metric_name: str,
        current_value: float,
        historical_values: List[float],
        historical_timestamps: List[datetime],
        capacity: float,
        threshold_percent: float = 80.0,
    ) -> CapacityForecast:
        """
        Forecast when a resource will reach capacity threshold.

        Args:
            metric_name: Name of the metric
            current_value: Current metric value
            historical_values: Historical values
            historical_timestamps: Timestamps for historical values
            capacity: Maximum capacity
            threshold_percent: Alert threshold (% of capacity)

        Returns:
            CapacityForecast with predictions and recommendations
        """
        threshold_value = capacity * (threshold_percent / 100)
        utilization = (current_value / capacity * 100) if capacity > 0 else 0

        # Generate forecast
        forecast_points = self.forecast_metric(
            historical_values, historical_timestamps, forecast_days=90
        )

        # Find when threshold will be crossed
        days_until_threshold = None
        for point in forecast_points:
            if point.predicted_value >= threshold_value:
                days_until_threshold = (point.timestamp - datetime.now()).days
                break

        # Generate recommendation
        if days_until_threshold is None:
            recommendation = (
                f"{metric_name} is not expected to reach {threshold_percent}% "
                "capacity within 90 days. Current utilization is healthy."
            )
        elif days_until_threshold <= 7:
            recommendation = (
                f"⚠️ CRITICAL: {metric_name} will reach {threshold_percent}% "
                f"capacity in ~{days_until_threshold} days. Immediate action required!"
            )
        elif days_until_threshold <= 30:
            recommendation = (
                f"⚠️ WARNING: {metric_name} will reach {threshold_percent}% "
                f"capacity in ~{days_until_threshold} days. Plan capacity expansion."
            )
        else:
            recommendation = (
                f"{metric_name} will reach {threshold_percent}% capacity in "
                f"~{days_until_threshold} days. Monitor and plan accordingly."
            )

        # Get predicted value at 30 days
        predicted_30d = forecast_points[min(len(forecast_points) - 1, 30 * 24)]
        predicted_value = predicted_30d.predicted_value

        return CapacityForecast(
            metric_name=metric_name,
            current_value=current_value,
            current_capacity=capacity,
            predicted_value=predicted_value,
            days_until_threshold=days_until_threshold,
            threshold_value=threshold_value,
            utilization_percent=utilization,
            forecast_points=forecast_points[: 30 * 24],  # Return 30 days
            recommendation=recommendation,
        )

    def forecast_trend(
        self,
        metric_name: str,
        values: List[float],
        timestamps: List[datetime],
    ) -> TrendForecast:
        """
        Analyze trend and forecast future values.

        Args:
            metric_name: Name of the metric
            values: Historical values
            timestamps: Timestamps for each value

        Returns:
            TrendForecast with predictions
        """
        if len(values) < 2:
            return TrendForecast(
                metric_name=metric_name,
                current_value=values[0] if values else 0,
                trend_direction="stable",
                daily_change_rate=0,
                predicted_7d=values[0] if values else 0,
                predicted_30d=values[0] if values else 0,
                predicted_90d=values[0] if values else 0,
                confidence=0,
            )

        current_value = values[-1]

        # Calculate daily change rate
        time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 86400  # days
        total_change = values[-1] - values[0]
        daily_change = total_change / time_span if time_span > 0 else 0

        # Determine trend direction
        if abs(daily_change) < 0.01 * current_value:  # Less than 1% per day
            trend_direction = "stable"
        elif daily_change > 0:
            trend_direction = "increasing"
        else:
            trend_direction = "decreasing"

        # Generate forecasts for 7, 30, and 90 days
        forecast_points = self.forecast_metric(values, timestamps, forecast_days=90)

        # Get predictions at specific intervals
        predicted_7d = current_value
        predicted_30d = current_value
        predicted_90d = current_value

        for point in forecast_points:
            days_ahead = (point.timestamp - timestamps[-1]).days
            if days_ahead >= 7 and predicted_7d == current_value:
                predicted_7d = point.predicted_value
            if days_ahead >= 30 and predicted_30d == current_value:
                predicted_30d = point.predicted_value
            if days_ahead >= 90:
                predicted_90d = point.predicted_value
                break

        # Calculate confidence based on data consistency
        if len(values) > 2:
            smoothed = self.smoother.smooth(values)
            errors = [abs(values[i] - smoothed[i]) for i in range(len(values))]
            avg_error = mean(errors)
            confidence = max(0, 1 - (avg_error / current_value if current_value > 0 else 1))
        else:
            confidence = 0.5

        return TrendForecast(
            metric_name=metric_name,
            current_value=current_value,
            trend_direction=trend_direction,
            daily_change_rate=daily_change,
            predicted_7d=predicted_7d,
            predicted_30d=predicted_30d,
            predicted_90d=predicted_90d,
            confidence=min(1.0, confidence),
        )


def calculate_bandwidth_forecast(
    current_usage_mbps: float,
    historical_values: List[float],
    historical_timestamps: List[datetime],
    link_capacity_mbps: float,
) -> CapacityForecast:
    """
    Forecast bandwidth utilization and capacity needs.

    Args:
        current_usage_mbps: Current bandwidth usage in Mbps
        historical_values: Historical bandwidth values
        historical_timestamps: Timestamps for historical values
        link_capacity_mbps: Maximum link capacity in Mbps

    Returns:
        CapacityForecast for bandwidth
    """
    forecaster = NetworkForecaster()
    return forecaster.forecast_capacity(
        metric_name="Bandwidth",
        current_value=current_usage_mbps,
        historical_values=historical_values,
        historical_timestamps=historical_timestamps,
        capacity=link_capacity_mbps,
        threshold_percent=80.0,
    )


def calculate_client_capacity_forecast(
    current_clients: int,
    historical_values: List[float],
    historical_timestamps: List[datetime],
    max_clients: int = 250,
) -> CapacityForecast:
    """
    Forecast when client count will reach capacity.

    Args:
        current_clients: Current number of connected clients
        historical_values: Historical client counts
        historical_timestamps: Timestamps for historical values
        max_clients: Maximum supported clients

    Returns:
        CapacityForecast for client capacity
    """
    forecaster = NetworkForecaster()
    return forecaster.forecast_capacity(
        metric_name="Connected Clients",
        current_value=float(current_clients),
        historical_values=historical_values,
        historical_timestamps=historical_timestamps,
        capacity=float(max_clients),
        threshold_percent=75.0,
    )

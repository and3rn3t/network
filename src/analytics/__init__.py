"""
Analytics module for UniFi Network data analysis.

Provides statistical analysis, trend detection, anomaly detection,
and capacity planning capabilities.
"""

from src.analytics.analytics_engine import (
    AnalyticsEngine,
    Anomaly,
    CapacityForecast,
    Statistics,
    TrendAnalysis,
)
from src.analytics.unifi_analytics import (
    ClientExperience,
    DeviceHealthScore,
    NetworkTopology,
    SignalQuality,
    UniFiAnalyticsEngine,
)

__all__ = [
    # Cloud API analytics
    "AnalyticsEngine",
    "Statistics",
    "TrendAnalysis",
    "Anomaly",
    "CapacityForecast",
    # UniFi Controller analytics
    "UniFiAnalyticsEngine",
    "DeviceHealthScore",
    "ClientExperience",
    "NetworkTopology",
    "SignalQuality",
]

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

__all__ = [
    "AnalyticsEngine",
    "Statistics",
    "TrendAnalysis",
    "Anomaly",
    "CapacityForecast",
]

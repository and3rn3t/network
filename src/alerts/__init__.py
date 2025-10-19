"""
Alert system for UniFi Network Monitor.

This package provides alerting and notification capabilities for monitoring
UniFi network devices.
"""

from .alert_engine import AlertEngine
from .alert_manager import AlertManager
from .models import Alert, AlertMute, AlertRule, NotificationChannel
from .notification_manager import NotificationManager

__all__ = [
    "AlertRule",
    "Alert",
    "NotificationChannel",
    "AlertMute",
    "AlertEngine",
    "AlertManager",
    "NotificationManager",
]

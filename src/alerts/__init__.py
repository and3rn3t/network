"""
Alert system for UniFi Network Monitor.

This package provides alerting and notification capabilities for monitoring
UniFi network devices.
"""

# Only export models to avoid circular imports with repositories
# Import AlertEngine, AlertManager, NotificationManager directly when needed
from .models import Alert, AlertMute, AlertRule, NotificationChannel

__all__ = [
    "AlertRule",
    "Alert",
    "NotificationChannel",
    "AlertMute",
]

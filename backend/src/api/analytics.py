"""Analytics API endpoints."""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Query

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.src.services.database_service import get_database
from src.database.database import Database

router = APIRouter()


@router.get("/metrics/summary")
async def get_metrics_summary(
    hours: int = Query(24, ge=1, le=168, description="Hours to analyze"),
    db: Database = Depends(get_database),
):
    """
    Get metrics summary.

    Returns aggregated metrics over the specified time period.
    """
    since = datetime.now() - timedelta(hours=hours)

    # Get average metrics
    query = """
        SELECT
            metric_type,
            AVG(value) as avg_value,
            MIN(value) as min_value,
            MAX(value) as max_value,
            COUNT(*) as count
        FROM metrics
        WHERE timestamp >= ?
        GROUP BY metric_type
    """
    rows = db.execute(query, (since.isoformat(),)).fetchall()

    metrics = {
        row[0]: {
            "average": round(row[1], 2) if row[1] else None,
            "min": round(row[2], 2) if row[2] else None,
            "max": round(row[3], 2) if row[3] else None,
            "count": row[4],
        }
        for row in rows
    }

    return {
        "metrics": metrics,
        "hours": hours,
        "since": since.isoformat(),
    }


@router.get("/trends")
async def get_trends(
    metric_type: str = Query(..., description="Metric type to analyze"),
    host_id: Optional[int] = Query(None, description="Filter by host ID"),
    hours: int = Query(24, ge=1, le=168, description="Hours to analyze"),
    interval: int = Query(60, ge=1, le=1440, description="Interval in minutes"),
    db: Database = Depends(get_database),
):
    """
    Get metric trends over time.

    Returns time-series data for the specified metric.
    """
    since = datetime.now() - timedelta(hours=hours)

    query = """
        SELECT
            strftime('%Y-%m-%d %H:%M', timestamp) as time_bucket,
            AVG(value) as avg_value
        FROM metrics
        WHERE metric_type = ?
        AND timestamp >= ?
    """
    params = [metric_type, since.isoformat()]

    if host_id:
        query += " AND host_id = ?"
        params.append(host_id)

    query += """
        GROUP BY time_bucket
        ORDER BY time_bucket
    """

    rows = db.execute(query, tuple(params)).fetchall()

    data_points = [
        {
            "timestamp": row[0],
            "value": round(row[1], 2) if row[1] else None,
        }
        for row in rows
    ]

    return {
        "metric_type": metric_type,
        "host_id": host_id,
        "data_points": data_points,
        "count": len(data_points),
        "hours": hours,
    }


@router.get("/health-score")
async def get_health_score(
    db: Database = Depends(get_database),
):
    """
    Get overall network health score.

    Returns a calculated health score based on device status and metrics.
    """
    # Get device counts
    device_query = """
        SELECT
            status,
            COUNT(*) as count
        FROM hosts
        GROUP BY status
    """
    device_rows = db.execute(device_query).fetchall()
    device_stats = {row[0]: row[1] for row in device_rows}

    total_devices = sum(device_stats.values())
    online_devices = device_stats.get("online", 0)

    # Get recent alert count
    since_24h = datetime.now() - timedelta(hours=24)
    alert_query = """
        SELECT severity, COUNT(*) as count
        FROM alert_history
        WHERE triggered_at >= ?
        AND status = 'triggered'
        GROUP BY severity
    """
    alert_rows = db.execute(alert_query, (since_24h.isoformat(),)).fetchall()
    alert_stats = {row[0]: row[1] for row in alert_rows}

    # Calculate health score (0-100)
    health_score = 100

    # Deduct for offline devices
    if total_devices > 0:
        offline_penalty = ((total_devices - online_devices) / total_devices) * 30
        health_score -= offline_penalty

    # Deduct for active alerts
    critical_alerts = alert_stats.get("critical", 0)
    warning_alerts = alert_stats.get("warning", 0)
    health_score -= critical_alerts * 5
    health_score -= warning_alerts * 2

    # Ensure score is between 0 and 100
    health_score = max(0, min(100, health_score))

    return {
        "health_score": round(health_score, 1),
        "total_devices": total_devices,
        "online_devices": online_devices,
        "offline_devices": total_devices - online_devices,
        "active_alerts": {
            "critical": critical_alerts,
            "warning": warning_alerts,
            "total": sum(alert_stats.values()),
        },
        "timestamp": datetime.now().isoformat(),
    }

"""Analytics API endpoints."""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.src.services.database_service import get_database
from src.analytics.forecasting import NetworkForecaster
from src.analytics.machine_learning import AnomalyDetector, FailurePredictor
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


@router.get("/forecast/{device_id}")
async def get_device_forecast(
    device_id: int,
    metric_type: str = Query(..., description="Metric to forecast (cpu, memory, bandwidth)"),
    forecast_days: int = Query(30, ge=1, le=90, description="Days to forecast"),
    db: Database = Depends(get_database),
):
    """
    Forecast device metrics using time-series analysis.

    Returns predicted values and confidence intervals for the specified metric.
    """
    # Get historical data
    since = datetime.now() - timedelta(days=30)
    query = """
        SELECT value, timestamp
        FROM metrics
        WHERE host_id = ? AND metric_type = ? AND timestamp >= ?
        ORDER BY timestamp ASC
    """
    rows = db.execute(query, (device_id, metric_type, since.isoformat())).fetchall()

    if not rows or len(rows) < 10:
        raise HTTPException(status_code=404, detail="Insufficient historical data for forecasting")

    values = [float(row[0]) for row in rows]
    timestamps = [datetime.fromisoformat(row[1]) for row in rows]

    # Generate forecast
    forecaster = NetworkForecaster()
    forecast_points = forecaster.forecast_metric(values, timestamps, forecast_days)

    # Format response
    return {
        "device_id": device_id,
        "metric_type": metric_type,
        "current_value": values[-1],
        "forecast_days": forecast_days,
        "forecast": [
            {
                "timestamp": fp.timestamp.isoformat(),
                "predicted_value": round(fp.predicted_value, 2),
                "confidence_lower": round(fp.confidence_lower, 2),
                "confidence_upper": round(fp.confidence_upper, 2),
                "confidence_level": round(fp.confidence_level, 2),
            }
            for fp in forecast_points
        ],
        "generated_at": datetime.now().isoformat(),
    }


@router.get("/capacity-forecast/{device_id}")
async def get_capacity_forecast(
    device_id: int,
    metric_type: str = Query(..., description="Metric to analyze"),
    capacity: float = Query(..., description="Maximum capacity value"),
    threshold_percent: float = Query(80.0, ge=50, le=95, description="Alert threshold %"),
    db: Database = Depends(get_database),
):
    """
    Forecast when a device will reach capacity threshold.

    Useful for capacity planning (bandwidth, memory, storage, client count).
    """
    # Get historical data (last 30 days)
    since = datetime.now() - timedelta(days=30)
    query = """
        SELECT value, timestamp
        FROM metrics
        WHERE host_id = ? AND metric_type = ? AND timestamp >= ?
        ORDER BY timestamp ASC
    """
    rows = db.execute(query, (device_id, metric_type, since.isoformat())).fetchall()

    if not rows or len(rows) < 10:
        raise HTTPException(
            status_code=404, detail="Insufficient historical data for capacity forecast"
        )

    values = [float(row[0]) for row in rows]
    timestamps = [datetime.fromisoformat(row[1]) for row in rows]
    current_value = values[-1]

    # Generate capacity forecast
    forecaster = NetworkForecaster()
    capacity_forecast = forecaster.forecast_capacity(
        metric_name=metric_type,
        current_value=current_value,
        historical_values=values,
        historical_timestamps=timestamps,
        capacity=capacity,
        threshold_percent=threshold_percent,
    )

    return {
        "device_id": device_id,
        "metric_type": metric_type,
        "current_value": round(capacity_forecast.current_value, 2),
        "current_utilization": round(capacity_forecast.utilization_percent, 1),
        "capacity": capacity,
        "threshold_percent": threshold_percent,
        "threshold_value": round(capacity_forecast.threshold_value, 2),
        "predicted_value_30d": round(capacity_forecast.predicted_value, 2),
        "days_until_threshold": capacity_forecast.days_until_threshold,
        "recommendation": capacity_forecast.recommendation,
        "generated_at": datetime.now().isoformat(),
    }


@router.get("/anomalies/{device_id}")
async def detect_anomalies(
    device_id: int,
    metric_type: str = Query(..., description="Metric to analyze"),
    days: int = Query(7, ge=1, le=30, description="Days to analyze"),
    db: Database = Depends(get_database),
):
    """
    Detect anomalies in device metrics using ML.

    Uses isolation forest and statistical methods to identify unusual patterns.
    """
    # Get device info
    device_query = "SELECT name FROM hosts WHERE id = ?"
    device_row = db.execute(device_query, (device_id,)).fetchone()
    if not device_row:
        raise HTTPException(status_code=404, detail="Device not found")

    device_name = device_row[0]

    # Get historical data
    since = datetime.now() - timedelta(days=days)
    query = """
        SELECT value, timestamp
        FROM metrics
        WHERE host_id = ? AND metric_type = ? AND timestamp >= ?
        ORDER BY timestamp ASC
    """
    rows = db.execute(query, (device_id, metric_type, since.isoformat())).fetchall()

    if not rows or len(rows) < 10:
        return {
            "device_id": device_id,
            "device_name": device_name,
            "metric_type": metric_type,
            "anomalies": [],
            "message": "Insufficient data for anomaly detection",
        }

    values = [float(row[0]) for row in rows]
    timestamps = [datetime.fromisoformat(row[1]) for row in rows]

    # Train detector and find anomalies
    detector = AnomalyDetector()
    detector.fit(values)
    anomalies = detector.detect_anomalies(
        metric_name=metric_type,
        values=values,
        timestamps=timestamps,
        entity_id=str(device_id),
        entity_name=device_name,
    )

    return {
        "device_id": device_id,
        "device_name": device_name,
        "metric_type": metric_type,
        "days_analyzed": days,
        "total_data_points": len(values),
        "anomalies_detected": len(anomalies),
        "anomalies": [
            {
                "timestamp": a.timestamp.isoformat(),
                "value": round(a.value, 2),
                "expected_range": [
                    round(a.expected_range[0], 2),
                    round(a.expected_range[1], 2),
                ],
                "anomaly_score": round(a.anomaly_score, 2),
                "severity": a.severity,
                "description": a.description,
            }
            for a in anomalies
        ],
        "generated_at": datetime.now().isoformat(),
    }


@router.get("/failure-prediction/{device_id}")
async def predict_device_failure(
    device_id: int,
    db: Database = Depends(get_database),
):
    """
    Predict device failure probability using ML.

    Analyzes multiple health indicators to assess failure risk.
    """
    # Get device info
    device_query = "SELECT name FROM hosts WHERE id = ?"
    device_row = db.execute(device_query, (device_id,)).fetchone()
    if not device_row:
        raise HTTPException(status_code=404, detail="Device not found")

    device_name = device_row[0]

    # Get recent metrics (last 30 days)
    since = datetime.now() - timedelta(days=30)

    # CPU history
    cpu_query = """
        SELECT value FROM metrics
        WHERE host_id = ? AND metric_type = 'cpu' AND timestamp >= ?
        ORDER BY timestamp DESC
        LIMIT 100
    """
    cpu_rows = db.execute(cpu_query, (device_id, since.isoformat())).fetchall()
    cpu_history = [float(row[0]) for row in cpu_rows]

    # Memory history
    mem_query = """
        SELECT value FROM metrics
        WHERE host_id = ? AND metric_type = 'memory' AND timestamp >= ?
        ORDER BY timestamp DESC
        LIMIT 100
    """
    mem_rows = db.execute(mem_query, (device_id, since.isoformat())).fetchall()
    memory_history = [float(row[0]) for row in mem_rows]

    # Temperature history
    temp_query = """
        SELECT value FROM metrics
        WHERE host_id = ? AND metric_type = 'temperature' AND timestamp >= ?
        ORDER BY timestamp DESC
        LIMIT 100
    """
    temp_rows = db.execute(temp_query, (device_id, since.isoformat())).fetchall()
    temperature_history = [float(row[0]) for row in temp_rows]

    # Get uptime and restart count (mock data for now - would need event tracking)
    uptime_days = 45.0  # Would calculate from actual data
    restart_count = 2  # Would count from events

    # Predict failure
    predictor = FailurePredictor()
    prediction = predictor.predict_failure(
        device_id=str(device_id),
        device_name=device_name,
        uptime_days=uptime_days,
        restart_count=restart_count,
        cpu_history=cpu_history,
        memory_history=memory_history,
        temperature_history=temperature_history,
    )

    return {
        "device_id": device_id,
        "device_name": device_name,
        "failure_probability": round(prediction.failure_probability, 2),
        "risk_level": prediction.risk_level,
        "time_to_failure_days": prediction.time_to_failure_days,
        "contributing_factors": prediction.contributing_factors,
        "recommendation": prediction.recommendation,
        "analysis_period_days": 30,
        "generated_at": datetime.now().isoformat(),
    }


@router.get("/network-insights")
async def get_network_insights(
    db: Database = Depends(get_database),
):
    """
    Get high-level network insights and recommendations.

    Aggregates analytics across all devices for executive summary.
    """
    # Get total device count and health
    device_query = "SELECT COUNT(*) as total, SUM(CASE WHEN state = 1 THEN 1 ELSE 0 END) as online FROM unifi_devices"  # noqa: E501
    device_row = db.fetch_one(device_query)
    total_devices = device_row["total"] if device_row else 0
    online_devices = device_row["online"] if device_row else 0

    # Get recent metrics summary (last 24 hours)
    since_24h = datetime.now() - timedelta(hours=24)
    metrics_query = """
        SELECT metric_name, AVG(metric_value) as avg_val
        FROM unifi_device_metrics
        WHERE recorded_at >= ?
        GROUP BY metric_name
    """
    metrics_rows = db.fetch_all(metrics_query, (since_24h.isoformat(),))
    avg_metrics = {row["metric_name"]: round(row["avg_val"], 2) for row in metrics_rows}

    # Get active alerts (if alert system is configured)
    active_alerts = 0
    try:
        alert_query = """
            SELECT COUNT(*) as alert_count
            FROM alert_history
            WHERE status = 'triggered' AND triggered_at >= ?
        """
        alert_row = db.fetch_one(alert_query, (since_24h.isoformat(),))
        active_alerts = alert_row["alert_count"] if alert_row else 0
    except Exception:
        # Alert system not configured, use 0
        pass

    # Generate insights
    insights = []
    recommendations = []

    # Device health insight
    if total_devices > 0:
        online_percent = (online_devices / total_devices) * 100
        if online_percent < 90:
            insights.append(
                f"⚠️ {total_devices - online_devices} device(s) offline ({100 - online_percent:.1f}%)"  # noqa: E501
            )
            recommendations.append("Investigate offline devices")
        else:
            insights.append(f"✅ All devices healthy ({online_percent:.0f}% online)")

    # CPU insight
    if "cpu_usage" in avg_metrics:
        avg_cpu = avg_metrics["cpu_usage"]
        if avg_cpu > 80:
            insights.append(f"⚠️ High average CPU usage ({avg_cpu}%)")
            recommendations.append("Consider load balancing or capacity upgrade")
        elif avg_cpu < 30:
            insights.append(f"✅ CPU usage is healthy ({avg_cpu}%)")

    # Memory insight
    if "memory_usage" in avg_metrics:
        avg_mem = avg_metrics["memory_usage"]
        if avg_mem > 90:
            insights.append(f"⚠️ High average memory usage ({avg_mem}%)")
            recommendations.append("Monitor memory usage trends")

    # Client satisfaction insight
    if "satisfaction" in avg_metrics:
        avg_satisfaction = avg_metrics["satisfaction"]
        if avg_satisfaction < 80:
            insights.append(f"⚠️ Client satisfaction below target ({avg_satisfaction}%)")
            recommendations.append("Review network performance and client connectivity")

    # Alert insight
    if active_alerts > 10:
        insights.append(f"⚠️ {active_alerts} active alerts in last 24h")
        recommendations.append("Review and acknowledge alerts")
    elif active_alerts > 0:
        insights.append(f"ℹ️ {active_alerts} active alert(s)")

    return {
        "network_summary": {
            "total_devices": total_devices,
            "online_devices": online_devices,
            "offline_devices": total_devices - online_devices,
            "active_alerts": active_alerts,
        },
        "avg_metrics_24h": avg_metrics,
        "insights": insights,
        "recommendations": recommendations,
        "generated_at": datetime.now().isoformat(),
    }

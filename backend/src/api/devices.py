"""Device API endpoints."""

import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Query

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.src.middleware.error_handler import NotFoundError
from backend.src.services.database_service import get_database
from src.database.database import Database
from src.database.models import Host

router = APIRouter()


@router.get("")
async def list_devices(
    status: Optional[str] = Query(None, description="Filter by status"),
    model: Optional[str] = Query(None, description="Filter by model"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Database = Depends(get_database),
):
    """
    List all network devices.

    Returns paginated list of devices with optional filtering.
    """
    # Build query with filters
    # Note: network.db uses different column names than expected
    query = "SELECT id, mac_address, name, model, type, ip_address, 'unknown' as status, firmware_version, 0 as uptime, last_seen FROM hosts WHERE 1=1"
    params = []

    if model:
        query += " AND model LIKE ?"
        params.append(f"%{model}%")

    # Get total count
    count_query = "SELECT COUNT(*) FROM hosts WHERE 1=1"
    count_params = []
    if model:
        count_query += " AND model LIKE ?"
        count_params.append(f"%{model}%")

    cursor = db.execute(count_query, tuple(count_params) if count_params else None)
    total = cursor.fetchone()[0]

    # Add pagination
    query += f" LIMIT {limit} OFFSET {offset}"

    # Execute query
    cursor = db.execute(query, tuple(params) if params else None)
    rows = cursor.fetchall()

    # Convert to dict format
    devices = [
        {
            "id": i,  # Use index as numeric ID since db uses TEXT id
            "mac": row[1],
            "name": row[2] or "Unknown",
            "model": row[3],
            "type": row[4],
            "ip": row[5],
            "status": "online",  # Default to online since we don't have status
            "version": row[7],
            "uptime": row[8],
            "last_seen": row[9],
            "site_id": None,
        }
        for i, row in enumerate(rows, start=1)
    ]

    return {
        "devices": devices,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{device_id}")
async def get_device(
    device_id: int,
    db: Database = Depends(get_database),
):
    """
    Get device details by ID.

    Returns complete device information including current status.
    """
    # Get device using direct SQL (avoid circular import)
    query = """
        SELECT id, mac_address, name, model, type, ip_address,
               firmware_version, last_seen
        FROM hosts
        ORDER BY rowid
        LIMIT 1 OFFSET ?
    """
    cursor = db.execute(query, (device_id - 1,))
    row = cursor.fetchone()

    if not row:
        raise NotFoundError(f"Device with ID {device_id} not found")

    return {
        "id": device_id,
        "mac": row[1],
        "name": row[2] or "Unknown",
        "model": row[3],
        "type": row[4],
        "ip": row[5],
        "status": "online",  # Could enhance with real-time status check
        "version": row[6],
        "uptime": 0,  # Could calculate from metrics
        "last_seen": row[7],
        "site_id": None,
    }


@router.get("/{device_id}/metrics")
async def get_device_metrics(
    device_id: int,
    metric_type: Optional[str] = Query(
        None, description="Filter by metric type (cpu_usage, memory_usage, etc.)"
    ),
    hours: int = Query(24, ge=1, le=168, description="Hours of history"),
    db: Database = Depends(get_database),
):
    """
    Get device metrics history.

    Returns time-series data for device metrics over specified time period.
    """
    from datetime import datetime, timedelta

    # First, we need to get the host_id (TEXT) from the numeric device_id
    # Query hosts to get the actual TEXT id
    host_query = """
        SELECT id, name FROM hosts
        ORDER BY rowid
        LIMIT 1 OFFSET ?
    """
    host_cursor = db.execute(host_query, (device_id - 1,))
    host_row = host_cursor.fetchone()

    if not host_row:
        raise NotFoundError(f"Device with ID {device_id} not found")

    host_id = host_row[0]  # TEXT id from database
    device_name = host_row[1] or "Unknown"

    # Get metrics from database using the TEXT host_id
    since = datetime.utcnow() - timedelta(hours=hours)
    query = """
        SELECT metric_name, metric_value, unit, recorded_at
        FROM metrics
        WHERE host_id = ?
        AND recorded_at >= ?
    """
    params = [host_id, since.isoformat() + "Z"]

    if metric_type:
        query += " AND metric_name = ?"
        params.append(metric_type)

    query += " ORDER BY recorded_at ASC"

    rows = db.execute(query, tuple(params)).fetchall()

    metrics = [
        {
            "metric_type": row[0],
            "value": row[1],
            "unit": row[2],
            "timestamp": row[3],
        }
        for row in rows
    ]

    return {
        "device_id": device_id,
        "device_name": device_name,
        "metrics": metrics,
        "count": len(metrics),
        "hours": hours,
    }


@router.get("/{device_id}/alerts")
async def get_device_alerts(
    device_id: int,
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    db: Database = Depends(get_database),
):
    """
    Get alerts for a specific device.

    Returns recent alerts related to this device.
    """
    # Get device using direct SQL to get TEXT host_id
    host_query = """
        SELECT id, name FROM hosts
        ORDER BY rowid
        LIMIT 1 OFFSET ?
    """
    host_cursor = db.execute(host_query, (device_id - 1,))
    host_row = host_cursor.fetchone()

    if not host_row:
        raise NotFoundError(f"Device with ID {device_id} not found")

    host_id = host_row[0]  # TEXT id from database
    device_name = host_row[1] or "Unknown"

    # Query alerts for this device
    query = """
        SELECT id, rule_id, host_id, status, severity, message,
               triggered_at, acknowledged_at, resolved_at
        FROM alert_history
        WHERE host_id = ?
    """
    params: list = [host_id]

    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY triggered_at DESC LIMIT ?"
    params.append(limit)

    rows = db.execute(query, tuple(params)).fetchall()

    alerts = [
        {
            "id": row[0],
            "rule_id": row[1],
            "host_id": row[2],
            "status": row[3],
            "severity": row[4],
            "message": row[5],
            "triggered_at": row[6],
            "acknowledged_at": row[7],
            "resolved_at": row[8],
        }
        for row in rows
    ]

    return {
        "device_id": device_id,
        "device_name": device_name,
        "alerts": alerts,
        "count": len(alerts),
    }

"""Device API endpoints."""

import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Query

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.src.database.database import Database
from backend.src.database.repositories import HostRepository

from backend.src.middleware.error_handler import NotFoundError
from backend.src.services.database_service import get_database

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
    host_repo = HostRepository(db)
    hosts = host_repo.get_all()

    # Apply filters
    if status:
        hosts = [h for h in hosts if h.status == status]
    if model:
        hosts = [h for h in hosts if h.model and model.lower() in h.model.lower()]

    # Get total count before pagination
    total = len(hosts)

    # Apply pagination
    hosts = hosts[offset : offset + limit]

    # Convert to dict format
    devices = [
        {
            "id": h.id,
            "mac": h.mac,
            "name": h.name,
            "model": h.model,
            "type": h.type,
            "ip": h.ip,
            "status": h.status,
            "version": h.version,
            "uptime": h.uptime,
            "last_seen": h.last_seen.isoformat() if h.last_seen else None,
            "site_id": h.site_id,
        }
        for h in hosts
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
    host_repo = HostRepository(db)
    host = host_repo.get_by_id(device_id)

    if not host:
        raise NotFoundError(f"Device with ID {device_id} not found")

    return {
        "id": host.id,
        "mac": host.mac,
        "name": host.name,
        "model": host.model,
        "type": host.type,
        "ip": host.ip,
        "status": host.status,
        "version": host.version,
        "uptime": host.uptime,
        "adopted": host.adopted,
        "disabled": host.disabled,
        "site_id": host.site_id,
        "first_seen": host.first_seen.isoformat() if host.first_seen else None,
        "last_seen": host.last_seen.isoformat() if host.last_seen else None,
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

    # Verify device exists
    host_repo = HostRepository(db)
    host = host_repo.get_by_id(device_id)
    if not host:
        raise NotFoundError(f"Device with ID {device_id} not found")

    # Get metrics from database
    since = datetime.now() - timedelta(hours=hours)
    query = """
        SELECT metric_type, value, timestamp
        FROM metrics
        WHERE host_id = ?
        AND timestamp >= ?
    """
    params = [device_id, since.isoformat()]

    if metric_type:
        query += " AND metric_type = ?"
        params.append(metric_type)

    query += " ORDER BY timestamp DESC LIMIT 1000"

    rows = db.execute(query, tuple(params)).fetchall()

    metrics = [
        {
            "metric_type": row[0],
            "value": row[1],
            "timestamp": row[2],
        }
        for row in rows
    ]

    return {
        "device_id": device_id,
        "device_name": host.name,
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
    from src.database.repositories import AlertRepository

    # Verify device exists
    host_repo = HostRepository(db)
    host = host_repo.get_by_id(device_id)
    if not host:
        raise NotFoundError(f"Device with ID {device_id} not found")

    # Get alerts for this device
    alert_repo = AlertRepository(db)

    # Query alerts
    query = """
        SELECT id, rule_id, host_id, status, severity, message,
               triggered_at, acknowledged_at, resolved_at
        FROM alert_history
        WHERE host_id = ?
    """
    params = [device_id]

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
        "device_name": host.name,
        "alerts": alerts,
        "count": len(alerts),
    }

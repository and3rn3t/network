"""Device API endpoints."""

import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, Field

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.src.middleware.error_handler import NotFoundError
from backend.src.services.database_service import get_database
from config import (
    API_TYPE,
    CONTROLLER_HOST,
    CONTROLLER_PASSWORD,
    CONTROLLER_PORT,
    CONTROLLER_SITE,
    CONTROLLER_USERNAME,
    CONTROLLER_VERIFY_SSL,
)
from src.database.database import Database
from src.database.models import Host
from src.unifi_controller import UniFiController

router = APIRouter()


# Pydantic models for request/response validation
class DeviceAction(BaseModel):
    """Base model for device actions."""

    action: str = Field(..., description="Action to perform")
    reason: Optional[str] = Field(None, description="Reason for action (for audit log)")


class DeviceRenameRequest(BaseModel):
    """Request model for renaming a device."""

    name: str = Field(..., min_length=1, max_length=100, description="New device name")


class BulkDeviceAction(BaseModel):
    """Request model for bulk device operations."""

    device_ids: List[int] = Field(
        ..., min_items=1, max_items=50, description="Device IDs"
    )
    action: str = Field(..., description="Action to perform")
    reason: Optional[str] = Field(None, description="Reason for action")


class DeviceActionResponse(BaseModel):
    """Response model for device actions."""

    success: bool
    message: str
    device_id: Optional[int] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# Helper function to get UniFi client
def get_unifi_client() -> UniFiController:
    """Get configured UniFi controller instance."""
    controller = UniFiController(
        host=CONTROLLER_HOST,
        username=CONTROLLER_USERNAME,
        password=CONTROLLER_PASSWORD,
        port=CONTROLLER_PORT,
        site=CONTROLLER_SITE,
        verify_ssl=CONTROLLER_VERIFY_SSL,
    )
    # Login is handled automatically by _ensure_logged_in()
    return controller


@router.get("")
async def list_devices(
    status: Optional[str] = Query(None, description="Filter by status"),
    model: Optional[str] = Query(None, description="Filter by model"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Database = Depends(get_database),
):
    """
    List all network devices from UniFi controller.

    Returns paginated list of devices with optional filtering.
    """
    # Query from unifi_devices table (real data)
    query = """
        SELECT
            d.id,
            d.mac,
            d.name,
            d.model,
            d.type,
            d.ip,
            COALESCE(ds.state, 'unknown') as status,
            d.version,
            COALESCE(ds.uptime, 0) as uptime,
            d.last_seen,
            d.site_name
        FROM unifi_devices d
        LEFT JOIN unifi_device_status ds ON d.mac = ds.device_mac
            AND ds.recorded_at = (
                SELECT MAX(recorded_at) FROM unifi_device_status WHERE device_mac = d.mac
            )
        WHERE 1=1
    """
    params = []

    if model:
        query += " AND d.model LIKE ?"
        params.append(f"%{model}%")

    if status:
        query += " AND ds.state = ?"
        params.append(status)

    # Get total count
    count_query = "SELECT COUNT(*) FROM unifi_devices d WHERE 1=1"
    count_params = []
    if model:
        count_query += " AND d.model LIKE ?"
        count_params.append(f"%{model}%")

    if count_params:
        cursor = db.execute(count_query, tuple(count_params))
    else:
        cursor = db.execute(count_query)
    total = cursor.fetchone()[0]

    # Add pagination
    query += f" LIMIT {limit} OFFSET {offset}"

    # Execute query
    if params:
        cursor = db.execute(query, tuple(params))
    else:
        cursor = db.execute(query)
    rows = cursor.fetchall()

    # Convert to dict format
    devices = [
        {
            "id": row[0],
            "mac": row[1],
            "name": row[2] or "Unknown",
            "model": row[3],
            "type": row[4],
            "ip": row[5],
            "status": row[6] if row[6] in ["online", "offline"] else "online",
            "version": row[7],
            "uptime": row[8],
            "last_seen": row[9],
            "site_name": row[10],
        }
        for row in rows
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


# =============================================================================
# Device Management Endpoints
# =============================================================================


@router.post("/{device_id}/reboot", response_model=DeviceActionResponse)
async def reboot_device(
    device_id: int,
    action: DeviceAction = Body(...),
    db: Database = Depends(get_database),
):
    """
    Reboot a network device.

    ⚠️ **Warning:** This will temporarily disconnect the device and clients.

    Args:
        device_id: Numeric device ID
        action: Action details including reason

    Returns:
        Action response with success status
    """
    # Get device to verify it exists and get MAC address
    host_query = """
        SELECT id, name, mac_address FROM hosts
        ORDER BY rowid
        LIMIT 1 OFFSET ?
    """
    host_cursor = db.execute(host_query, (device_id - 1,))
    host_row = host_cursor.fetchone()

    if not host_row:
        raise NotFoundError(f"Device with ID {device_id} not found")

    host_id = host_row[0]
    device_name = host_row[1] or "Unknown"
    mac_address = host_row[2]

    # Execute reboot via UniFi Controller API
    try:
        controller = get_unifi_client()
        controller.reboot_device(mac_address)

        # Log the action in events table
        db.execute(
            """
            INSERT INTO events (host_id, event_type, event_data, recorded_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (
                host_id,
                "device_reboot",
                f"Rebooted by API. Reason: {action.reason or 'Not specified'}",
            ),
        )
        db.commit()

        return DeviceActionResponse(
            success=True,
            message=f"Reboot command sent to {device_name}",
            device_id=device_id,
        )
    except Exception as e:
        return DeviceActionResponse(
            success=False,
            message=f"Failed to reboot device: {str(e)}",
            device_id=device_id,
        )


@router.post("/{device_id}/locate", response_model=DeviceActionResponse)
async def locate_device(
    device_id: int,
    duration: int = Query(
        30, ge=5, le=300, description="LED blink duration in seconds"
    ),
    db: Database = Depends(get_database),
):
    """
    Make device LED blink for identification.

    Useful for physically locating a device in a large deployment.

    Args:
        device_id: Numeric device ID
        duration: How long to blink (5-300 seconds)

    Returns:
        Action response with success status
    """
    # Get device
    host_query = """
        SELECT id, name, mac_address FROM hosts
        ORDER BY rowid
        LIMIT 1 OFFSET ?
    """
    host_cursor = db.execute(host_query, (device_id - 1,))
    host_row = host_cursor.fetchone()

    if not host_row:
        raise NotFoundError(f"Device with ID {device_id} not found")

    host_id = host_row[0]
    device_name = host_row[1] or "Unknown"
    mac_address = host_row[2]

    try:
        # Turn on locate LED via UniFi Controller
        controller = get_unifi_client()
        controller.locate_device(mac_address, enable=True)

        # Log the request
        db.execute(
            """
            INSERT INTO events (host_id, event_type, event_data, recorded_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (
                host_id,
                "device_locate",
                f"Locate requested for {duration} seconds",
            ),
        )
        db.commit()

        return DeviceActionResponse(
            success=True,
            message=f"Locate LED enabled on {device_name} ({duration}s)",
            device_id=device_id,
        )
    except Exception as e:
        return DeviceActionResponse(
            success=False,
            message=f"Failed to locate device: {str(e)}",
            device_id=device_id,
        )


@router.post("/{device_id}/rename", response_model=DeviceActionResponse)
async def rename_device(
    device_id: int,
    rename_request: DeviceRenameRequest,
    db: Database = Depends(get_database),
):
    """
    Rename a network device.

    Args:
        device_id: Numeric device ID
        rename_request: New name for the device

    Returns:
        Action response with success status
    """
    # Get device
    host_query = """
        SELECT id, name, mac_address FROM hosts
        ORDER BY rowid
        LIMIT 1 OFFSET ?
    """
    host_cursor = db.execute(host_query, (device_id - 1,))
    host_row = host_cursor.fetchone()

    if not host_row:
        raise NotFoundError(f"Device with ID {device_id} not found")

    host_id = host_row[0]
    old_name = host_row[1] or "Unknown"
    mac_address = host_row[2]
    new_name = rename_request.name

    try:
        # Rename via UniFi Controller API
        controller = get_unifi_client()
        controller.rename_device(mac_address, new_name)

        # Update device name in database
        db.execute(
            "UPDATE hosts SET name = ? WHERE id = ?",
            (new_name, host_id),
        )

        # Log the rename event
        db.execute(
            """
            INSERT INTO events (host_id, event_type, event_data, recorded_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (
                host_id,
                "device_rename",
                f"Renamed from '{old_name}' to '{new_name}'",
            ),
        )
        db.commit()

        return DeviceActionResponse(
            success=True,
            message=f"Device renamed from '{old_name}' to '{new_name}'",
            device_id=device_id,
        )
    except Exception as e:
        return DeviceActionResponse(
            success=False,
            message=f"Failed to rename device: {str(e)}",
            device_id=device_id,
        )


@router.post("/{device_id}/restart", response_model=DeviceActionResponse)
async def restart_device(
    device_id: int,
    action: DeviceAction = Body(...),
    db: Database = Depends(get_database),
):
    """
    Soft restart a network device (graceful restart).

    Difference from reboot: restart is gentler, reboot is hard reset.

    Args:
        device_id: Numeric device ID
        action: Action details including reason

    Returns:
        Action response with success status
    """
    # Get device
    host_query = """
        SELECT id, name, mac_address FROM hosts
        ORDER BY rowid
        LIMIT 1 OFFSET ?
    """
    host_cursor = db.execute(host_query, (device_id - 1,))
    host_row = host_cursor.fetchone()

    if not host_row:
        raise NotFoundError(f"Device with ID {device_id} not found")

    host_id = host_row[0]
    device_name = host_row[1] or "Unknown"
    mac_address = host_row[2]

    try:
        # Soft restart via UniFi Controller API
        controller = get_unifi_client()
        controller.restart_device(mac_address)

        # Log the restart
        db.execute(
            """
            INSERT INTO events (host_id, event_type, event_data, recorded_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (
                host_id,
                "device_restart",
                f"Soft restart. Reason: {action.reason or 'Not specified'}",
            ),
        )
        db.commit()

        return DeviceActionResponse(
            success=True,
            message=f"Restart command sent to {device_name}",
            device_id=device_id,
        )
    except Exception as e:
        return DeviceActionResponse(
            success=False,
            message=f"Failed to restart device: {str(e)}",
            device_id=device_id,
        )


@router.get("/{device_id}/info")
async def get_device_info(
    device_id: int,
    db: Database = Depends(get_database),
):
    """
    Get comprehensive device information.

    Returns detailed configuration, status, and statistics from controller.

    Args:
        device_id: Numeric device ID

    Returns:
        Complete device information
    """
    # Get device basic info from database
    host_query = """
        SELECT h.id, h.mac_address, h.name, h.model, h.type, h.ip_address,
               h.firmware_version, h.last_seen,
               hi.manufacturer, hi.product_line, hi.hardware_revision
        FROM hosts h
        LEFT JOIN host_info hi ON h.id = hi.host_id
        ORDER BY h.rowid
        LIMIT 1 OFFSET ?
    """
    cursor = db.execute(host_query, (device_id - 1,))
    row = cursor.fetchone()

    if not row:
        raise NotFoundError(f"Device with ID {device_id} not found")

    host_id = row[0]
    mac_address = row[1]

    # Get real-time device info from controller
    try:
        controller = get_unifi_client()
        device_stats = controller.get_device_statistics(mac_address)
    except Exception as e:
        # Fallback to database if controller unavailable
        device_stats = {}

    # Get latest metrics from database
    metrics_query = """
        SELECT metric_name, metric_value, unit, recorded_at
        FROM metrics
        WHERE host_id = ?
        ORDER BY recorded_at DESC
        LIMIT 20
    """
    metrics_cursor = db.execute(metrics_query, (host_id,))
    metrics_rows = metrics_cursor.fetchall()

    # Get configuration
    config_query = """
        SELECT config_json
        FROM host_config
        WHERE host_id = ?
        ORDER BY updated_at DESC
        LIMIT 1
    """
    config_cursor = db.execute(config_query, (host_id,))
    config_row = config_cursor.fetchone()

    # Get recent events
    events_query = """
        SELECT event_type, event_data, recorded_at
        FROM events
        WHERE host_id = ?
        ORDER BY recorded_at DESC
        LIMIT 10
    """
    events_cursor = db.execute(events_query, (host_id,))
    events_rows = events_cursor.fetchall()

    return {
        "id": device_id,
        "host_id": host_id,
        "mac": row[1],
        "name": row[2] or "Unknown",
        "model": row[3],
        "type": row[4],
        "ip": row[5],
        "firmware_version": row[6],
        "last_seen": row[7],
        "manufacturer": row[8],
        "product_line": row[9],
        "hardware_revision": row[10],
        # Real-time stats from controller
        "live_stats": device_stats,
        # Historical metrics from database
        "metrics": [
            {
                "name": m[0],
                "value": m[1],
                "unit": m[2],
                "timestamp": m[3],
            }
            for m in metrics_rows
        ],
        "configuration": config_row[0] if config_row else None,
        "recent_events": [
            {
                "type": e[0],
                "data": e[1],
                "timestamp": e[2],
            }
            for e in events_rows
        ],
    }


# =============================================================================
# Bulk Operations
# =============================================================================


@router.post("/bulk/reboot", response_model=List[DeviceActionResponse])
async def bulk_reboot_devices(
    bulk_action: BulkDeviceAction,
    db: Database = Depends(get_database),
):
    """
    Reboot multiple devices at once.

    ⚠️ **Warning:** This will disconnect multiple devices simultaneously.

    Args:
        bulk_action: List of device IDs and action details

    Returns:
        List of action responses for each device
    """
    results = []
    controller = get_unifi_client()

    for device_id in bulk_action.device_ids:
        # Get device with MAC address
        host_query = """
            SELECT id, name, mac_address FROM hosts
            ORDER BY rowid
            LIMIT 1 OFFSET ?
        """
        host_cursor = db.execute(host_query, (device_id - 1,))
        host_row = host_cursor.fetchone()

        if not host_row:
            results.append(
                DeviceActionResponse(
                    success=False,
                    message=f"Device ID {device_id} not found",
                    device_id=device_id,
                )
            )
            continue

        host_id = host_row[0]
        device_name = host_row[1] or "Unknown"
        mac_address = host_row[2]

        try:
            # Execute reboot via controller
            controller.reboot_device(mac_address)

            # Log the action
            db.execute(
                """
                INSERT INTO events (host_id, event_type, event_data,
                                   recorded_at)
                VALUES (?, ?, ?, datetime('now'))
                """,
                (
                    host_id,
                    "device_reboot",
                    f"Bulk reboot. Reason: " f"{bulk_action.reason or 'Not specified'}",
                ),
            )

            results.append(
                DeviceActionResponse(
                    success=True,
                    message=f"Reboot command sent to {device_name}",
                    device_id=device_id,
                )
            )
        except Exception as e:
            results.append(
                DeviceActionResponse(
                    success=False,
                    message=f"Failed to reboot {device_name}: {str(e)}",
                    device_id=device_id,
                )
            )

    db.commit()
    return results

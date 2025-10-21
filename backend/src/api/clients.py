"""Client API endpoints for managing network clients."""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, Query
from pydantic import BaseModel, Field

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.src.middleware.error_handler import NotFoundError
from backend.src.services.database_service import get_database
from config import (
    CONTROLLER_HOST,
    CONTROLLER_PASSWORD,
    CONTROLLER_PORT,
    CONTROLLER_SITE,
    CONTROLLER_USERNAME,
    CONTROLLER_VERIFY_SSL,
)
from src.database.database import Database
from src.unifi_controller import UniFiController

router = APIRouter()


# Pydantic models for request/response validation
class ClientBlockRequest(BaseModel):
    """Request model for blocking a client."""

    mac: str = Field(..., description="Client MAC address")
    reason: Optional[str] = Field(None, description="Reason for blocking")
    duration: Optional[int] = Field(
        None,
        ge=1,
        le=86400,
        description="Block duration in seconds (None = permanent)",
    )


class ClientBandwidthLimit(BaseModel):
    """Request model for setting client bandwidth limits."""

    download_limit: Optional[int] = Field(
        None, ge=0, description="Download limit in Kbps (0 = unlimited)"
    )
    upload_limit: Optional[int] = Field(
        None, ge=0, description="Upload limit in Kbps (0 = unlimited)"
    )


class ClientActionResponse(BaseModel):
    """Response model for client actions."""

    success: bool
    message: str
    mac: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class BulkClientAction(BaseModel):
    """Request model for bulk client operations."""

    mac_addresses: List[str] = Field(
        ..., min_items=1, max_items=100, description="Client MAC addresses"
    )
    action: str = Field(..., description="Action to perform")
    reason: Optional[str] = Field(None, description="Reason for action")


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
    return controller


# =============================================================================
# Client Listing & Details
# =============================================================================


@router.get("")
async def list_clients(
    status: Optional[str] = Query(
        None, description="Filter by status (active/blocked)"
    ),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Database = Depends(get_database),
):
    """
    List all network clients with latest WiFi metrics.

    Returns paginated list of clients with signal strength, speed, and channel data.
    """
    # Query unifi_clients with latest status/metrics
    query = """
        SELECT
            c.mac,
            c.hostname,
            c.name,
            c.ip,
            c.blocked,
            c.last_seen,
            c.is_wired,
            c.channel,
            c.essid,
            c.ap_name,
            s.signal,
            s.tx_rate,
            s.rx_rate,
            s.satisfaction,
            s.uptime
        FROM unifi_clients c
        LEFT JOIN unifi_client_status s ON c.mac = s.client_mac
            AND s.recorded_at = (
                SELECT MAX(recorded_at)
                FROM unifi_client_status
                WHERE client_mac = c.mac
            )
        ORDER BY c.last_seen DESC
    """

    # Get total count
    count_query = "SELECT COUNT(DISTINCT mac) FROM unifi_clients"
    cursor = db.execute(count_query)
    total = cursor.fetchone()[0]

    # Add pagination
    query += f" LIMIT {limit} OFFSET {offset}"

    # Execute query
    cursor = db.execute(query)
    rows = cursor.fetchall()

    # Convert to dict format with WiFi metrics
    clients = []
    for row in rows:
        client = {
            "mac": row[0],
            "hostname": row[1],
            "name": row[2],
            "ip": row[3],
            "blocked": bool(row[4]) if row[4] is not None else False,
            "last_seen": row[5],
            "is_wired": bool(row[6]) if row[6] is not None else False,
            "channel": row[7],
            "essid": row[8],
            "ap_name": row[9],
            "signal_strength": row[10],  # Signal in dBm
            "tx_rate": row[11],  # TX rate in Mbps
            "rx_rate": row[12],  # RX rate in Mbps
            "satisfaction": row[13],  # WiFi experience score
            "uptime": row[14],
            "device_type": "wireless" if not row[6] else "wired",
        }

        # Add channel utilization estimate (placeholder - would need separate query)
        client["channel_utilization"] = 0

        clients.append(client)

    return {
        "clients": clients,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{mac}")
async def get_client(
    mac: str,
    db: Database = Depends(get_database),
):
    """
    Get client details by MAC address.

    Returns complete client information including connection history.

    Args:
        mac: Client MAC address (format: 00:11:22:33:44:55 or 001122334455)

    Returns:
        Client details
    """
    # Normalize MAC address
    mac_normalized = mac.replace(":", "").replace("-", "").lower()

    # TODO: Query clients table
    # For now, return structure
    return {
        "mac": mac,
        "name": "Unknown Client",
        "ip": None,
        "hostname": None,
        "connection_status": "unknown",
        "first_seen": None,
        "last_seen": None,
        "blocked": False,
        "message": "Client details require clients table (not yet implemented)",
    }


# =============================================================================
# Client Management Endpoints
# =============================================================================


@router.post("/{mac}/block", response_model=ClientActionResponse)
async def block_client(
    mac: str,
    block_request: ClientBlockRequest = Body(...),
    db: Database = Depends(get_database),
):
    """
    Block a network client.

    Prevents the client from connecting to the network.

    ⚠️ **Warning:** This will immediately disconnect the client.

    Args:
        mac: Client MAC address
        block_request: Block duration and reason

    Returns:
        Action response with success status
    """
    try:
        # Call UniFi Controller API to block client
        controller = get_unifi_client()
        controller.block_client(mac, duration=block_request.duration)

        # Log the action
        duration_msg = (
            f" for {block_request.duration}s" if block_request.duration else ""
        )

        return ClientActionResponse(
            success=True,
            message=f"Client {mac} blocked successfully{duration_msg}",
            mac=mac,
        )
    except Exception as e:
        return ClientActionResponse(
            success=False,
            message=f"Failed to block client: {str(e)}",
            mac=mac,
        )


@router.post("/{mac}/unblock", response_model=ClientActionResponse)
async def unblock_client(
    mac: str,
    reason: Optional[str] = Body(None, embed=True),
    db: Database = Depends(get_database),
):
    """
    Unblock a previously blocked client.

    Allows the client to reconnect to the network.

    Args:
        mac: Client MAC address
        reason: Optional reason for unblocking

    Returns:
        Action response with success status
    """
    try:
        # Call UniFi Controller API to unblock client
        controller = get_unifi_client()
        controller.unblock_client(mac)

        return ClientActionResponse(
            success=True,
            message=f"Client {mac} unblocked successfully",
            mac=mac,
        )
    except Exception as e:
        return ClientActionResponse(
            success=False,
            message=f"Failed to unblock client: {str(e)}",
            mac=mac,
        )


@router.post("/{mac}/reconnect", response_model=ClientActionResponse)
async def reconnect_client(
    mac: str,
    reason: Optional[str] = Body(None, embed=True),
    db: Database = Depends(get_database),
):
    """
    Force client to reconnect (disconnect and re-authenticate).

    Useful for troubleshooting connectivity issues.

    ⚠️ **Warning:** This will temporarily disconnect the client.

    Args:
        mac: Client MAC address
        reason: Optional reason for reconnection

    Returns:
        Action response with success status
    """
    try:
        # Call UniFi Controller API to reconnect client
        controller = get_unifi_client()
        controller.reconnect_client(mac)

        return ClientActionResponse(
            success=True,
            message=f"Client {mac} reconnect command sent",
            mac=mac,
        )
    except Exception as e:
        return ClientActionResponse(
            success=False,
            message=f"Failed to reconnect client: {str(e)}",
            mac=mac,
        )


@router.post("/{mac}/bandwidth", response_model=ClientActionResponse)
async def set_client_bandwidth(
    mac: str,
    limits: ClientBandwidthLimit,
    db: Database = Depends(get_database),
):
    """
    Set bandwidth limits for a client.

    Useful for QoS management or limiting problematic clients.

    Args:
        mac: Client MAC address
        limits: Download and upload limits in Kbps

    Returns:
        Action response with success status
    """
    try:
        # Call UniFi Controller API to set bandwidth limits
        controller = get_unifi_client()

        download_kbps = limits.download_limit or 0
        upload_kbps = limits.upload_limit or 0

        controller.set_client_bandwidth(mac, download_kbps, upload_kbps)

        # Build message
        limit_text = []
        if limits.download_limit is not None:
            limit_text.append(
                f"download: {limits.download_limit} Kbps"
                if limits.download_limit > 0
                else "download: unlimited"
            )
        if limits.upload_limit is not None:
            limit_text.append(
                f"upload: {limits.upload_limit} Kbps"
                if limits.upload_limit > 0
                else "upload: unlimited"
            )

        return ClientActionResponse(
            success=True,
            message=f"Bandwidth limits set for {mac}: {', '.join(limit_text)}",
            mac=mac,
        )
    except Exception as e:
        return ClientActionResponse(
            success=False,
            message=f"Failed to set bandwidth limits: {str(e)}",
            mac=mac,
        )


@router.post("/{mac}/authorize-guest", response_model=ClientActionResponse)
async def authorize_guest(
    mac: str,
    duration: int = Body(..., ge=1, le=86400, embed=True),
    db: Database = Depends(get_database),
):
    """
    Authorize a guest client for limited time.

    Useful for guest networks with portal authentication.

    Args:
        mac: Client MAC address
        duration: Authorization duration in seconds (1-86400)

    Returns:
        Action response with success status
    """
    try:
        # Call UniFi Controller API to authorize guest
        controller = get_unifi_client()
        controller.authorize_guest(mac, duration)

        # Calculate expiration for display
        expires_at = datetime.now() + timedelta(seconds=duration)

        return ClientActionResponse(
            success=True,
            message=f"Guest {mac} authorized for {duration}s "
            f"(until {expires_at.strftime('%H:%M:%S')})",
            mac=mac,
        )
    except Exception as e:
        return ClientActionResponse(
            success=False,
            message=f"Failed to authorize guest: {str(e)}",
            mac=mac,
        )


# =============================================================================
# Client Connection History
# =============================================================================


@router.get("/{mac}/history")
async def get_client_history(
    mac: str,
    hours: int = Query(24, ge=1, le=168, description="Hours of history"),
    db: Database = Depends(get_database),
):
    """
    Get connection history for a client.

    Returns connection/disconnection events and session information.

    Args:
        mac: Client MAC address
        hours: Hours of history to retrieve (1-168)

    Returns:
        Connection history
    """
    try:
        # Try to get real history from UniFi Controller
        controller = get_unifi_client()
        history = controller.get_client_history(mac, hours=hours)

        # Calculate statistics from history
        total_sessions = len(history)
        total_data_gb = sum(
            (session.get("rx_bytes", 0) + session.get("tx_bytes", 0)) / (1024**3)
            for session in history
        )
        avg_duration = (
            sum(session.get("duration", 0) for session in history) / total_sessions
            if total_sessions > 0
            else 0
        )

        return {
            "mac": mac,
            "history": history,
            "sessions": history,  # Alias for compatibility
            "total_sessions": total_sessions,
            "total_data_gb": round(total_data_gb, 2),
            "average_session_duration": round(avg_duration, 0),
        }
    except Exception as e:
        # Fallback if controller unavailable
        return {
            "mac": mac,
            "history": [],
            "sessions": [],
            "total_sessions": 0,
            "total_data_gb": 0.0,
            "average_session_duration": 0,
            "message": f"Could not retrieve history: {str(e)}",
        }


# =============================================================================
# Bulk Client Operations
# =============================================================================


@router.post("/bulk/block", response_model=List[ClientActionResponse])
async def bulk_block_clients(
    bulk_action: BulkClientAction,
    db: Database = Depends(get_database),
):
    """
    Block multiple clients at once.

    ⚠️ **Warning:** This will disconnect multiple clients simultaneously.

    Args:
        bulk_action: List of client MAC addresses and action details

    Returns:
        List of action responses for each client
    """
    results = []
    controller = get_unifi_client()

    for mac in bulk_action.mac_addresses:
        try:
            # Call UniFi Controller API to block client
            controller.block_client(mac)

            results.append(
                ClientActionResponse(
                    success=True,
                    message=f"Client {mac} blocked",
                    mac=mac,
                )
            )
        except Exception as e:
            results.append(
                ClientActionResponse(
                    success=False,
                    message=f"Failed to block {mac}: {str(e)}",
                    mac=mac,
                )
            )

    return results


@router.post("/bulk/unblock", response_model=List[ClientActionResponse])
async def bulk_unblock_clients(
    bulk_action: BulkClientAction,
    db: Database = Depends(get_database),
):
    """
    Unblock multiple clients at once.

    Args:
        bulk_action: List of client MAC addresses and action details

    Returns:
        List of action responses for each client
    """
    results = []
    controller = get_unifi_client()

    for mac in bulk_action.mac_addresses:
        try:
            # Call UniFi Controller API to unblock client
            controller.unblock_client(mac)

            results.append(
                ClientActionResponse(
                    success=True,
                    message=f"Client {mac} unblocked",
                    mac=mac,
                )
            )
        except Exception as e:
            results.append(
                ClientActionResponse(
                    success=False,
                    message=f"Failed to unblock {mac}: {str(e)}",
                    mac=mac,
                )
            )

    return results


@router.post("/bulk/reconnect", response_model=List[ClientActionResponse])
async def bulk_reconnect_clients(
    bulk_action: BulkClientAction,
    db: Database = Depends(get_database),
):
    """
    Force multiple clients to reconnect at once.

    ⚠️ **Warning:** This will temporarily disconnect multiple clients.

    Args:
        bulk_action: List of client MAC addresses and action details

    Returns:
        List of action responses for each client
    """
    results = []
    controller = get_unifi_client()

    for mac in bulk_action.mac_addresses:
        try:
            # Call UniFi Controller API to reconnect client
            controller.reconnect_client(mac)

            results.append(
                ClientActionResponse(
                    success=True,
                    message=f"Client {mac} reconnect command sent",
                    mac=mac,
                )
            )
        except Exception as e:
            results.append(
                ClientActionResponse(
                    success=False,
                    message=f"Failed to reconnect {mac}: {str(e)}",
                    mac=mac,
                )
            )

    return results

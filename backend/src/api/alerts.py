"""Alert API endpoints."""

import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Body, Depends, Query

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.src.middleware.error_handler import NotFoundError
from backend.src.services.database_service import get_database

# Lazy import to avoid circular dependency
def get_alert_repository(db):
    """Get AlertRepository instance."""
    from src.database.repositories import AlertRepository
    return AlertRepository(db)

router = APIRouter()


@router.get("")
async def list_alerts(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    rule_id: Optional[int] = Query(None, description="Filter by rule ID"),
    host_id: Optional[int] = Query(None, description="Filter by host ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Database = Depends(get_database),
):
    """
    List all alerts with filtering and pagination.

    Returns paginated list of alerts matching the specified criteria.
    """
    alert_repo = AlertRepository(db)

    # Build query
    query = """
        SELECT id, rule_id, host_id, status, severity, message,
               metric_value, threshold_value,
               triggered_at, acknowledged_at, acknowledged_by,
               resolved_at, resolved_by, notes
        FROM alert_history
        WHERE 1=1
    """
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)
    if severity:
        query += " AND severity = ?"
        params.append(severity)
    if rule_id:
        query += " AND rule_id = ?"
        params.append(rule_id)
    if host_id:
        query += " AND host_id = ?"
        params.append(host_id)

    # Get total count
    count_query = query.replace(
        "SELECT id, rule_id, host_id, status, severity, message,"
        "               metric_value, threshold_value,"
        "               triggered_at, acknowledged_at, acknowledged_by,"
        "               resolved_at, resolved_by, notes",
        "SELECT COUNT(*)",
    )
    total = db.execute(count_query, tuple(params)).fetchone()[0]

    # Add pagination
    query += " ORDER BY triggered_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = db.execute(query, tuple(params)).fetchall()

    alerts = [
        {
            "id": row[0],
            "rule_id": row[1],
            "host_id": row[2],
            "status": row[3],
            "severity": row[4],
            "message": row[5],
            "metric_value": row[6],
            "threshold_value": row[7],
            "triggered_at": row[8],
            "acknowledged_at": row[9],
            "acknowledged_by": row[10],
            "resolved_at": row[11],
            "resolved_by": row[12],
            "notes": row[13],
        }
        for row in rows
    ]

    return {
        "alerts": alerts,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{alert_id}")
async def get_alert(
    alert_id: int,
    db: Database = Depends(get_database),
):
    """
    Get alert details by ID.

    Returns complete alert information including lifecycle events.
    """
    alert_repo = AlertRepository(db)
    alert = alert_repo.get_by_id(alert_id)

    if not alert:
        raise NotFoundError(f"Alert with ID {alert_id} not found")

    return alert.to_dict()


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    notes: Optional[str] = Body(None, embed=True),
    acknowledged_by: str = Body("api_user", embed=True),
    db: Database = Depends(get_database),
):
    """
    Acknowledge an alert.

    Marks the alert as acknowledged and optionally adds notes.
    """
    alert_repo = AlertRepository(db)
    alert = alert_repo.get_by_id(alert_id)

    if not alert:
        raise NotFoundError(f"Alert with ID {alert_id} not found")

    # Update alert status
    alert.status = "acknowledged"
    alert.acknowledged_by = acknowledged_by
    if notes:
        alert.notes = notes

    from datetime import datetime

    alert.acknowledged_at = datetime.now()

    alert_repo.update(alert)

    return {
        "success": True,
        "alert_id": alert_id,
        "status": "acknowledged",
    }


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    notes: Optional[str] = Body(None, embed=True),
    resolved_by: str = Body("api_user", embed=True),
    db: Database = Depends(get_database),
):
    """
    Resolve an alert.

    Marks the alert as resolved and optionally adds notes.
    """
    alert_repo = AlertRepository(db)
    alert = alert_repo.get_by_id(alert_id)

    if not alert:
        raise NotFoundError(f"Alert with ID {alert_id} not found")

    # Update alert status
    alert.status = "resolved"
    alert.resolved_by = resolved_by
    if notes:
        alert.notes = notes if not alert.notes else f"{alert.notes}\n{notes}"

    from datetime import datetime

    alert.resolved_at = datetime.now()

    alert_repo.update(alert)

    return {
        "success": True,
        "alert_id": alert_id,
        "status": "resolved",
    }


@router.get("/stats/summary")
async def get_alert_stats(
    hours: int = Query(24, ge=1, le=168, description="Hours to analyze"),
    db: Database = Depends(get_database),
):
    """
    Get alert statistics summary.

    Returns aggregated statistics about alerts over time period.
    """
    from datetime import datetime, timedelta

    since = datetime.now() - timedelta(hours=hours)

    # Get stats by severity
    severity_query = """
        SELECT severity, COUNT(*) as count
        FROM alert_history
        WHERE triggered_at >= ?
        GROUP BY severity
    """
    severity_rows = db.execute(severity_query, (since.isoformat(),)).fetchall()
    by_severity = {row[0]: row[1] for row in severity_rows}

    # Get stats by status
    status_query = """
        SELECT status, COUNT(*) as count
        FROM alert_history
        WHERE triggered_at >= ?
        GROUP BY status
    """
    status_rows = db.execute(status_query, (since.isoformat(),)).fetchall()
    by_status = {row[0]: row[1] for row in status_rows}

    # Get total count
    total_query = """
        SELECT COUNT(*) FROM alert_history WHERE triggered_at >= ?
    """
    total = db.execute(total_query, (since.isoformat(),)).fetchone()[0]

    return {
        "total": total,
        "by_severity": by_severity,
        "by_status": by_status,
        "hours": hours,
        "since": since.isoformat(),
    }

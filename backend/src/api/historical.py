"""Historical data API endpoints for performance trends analysis."""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.src.services.database_service import get_database
from src.database.database import Database

router = APIRouter()


# CLIENT METRICS ENDPOINTS (Primary Focus)


@router.get(
    "/clients/{client_mac}/metrics",
    response_model=DeviceMetricsResponse,
    summary="Get historical client metrics",
)
async def get_client_historical_metrics(
    client_mac: str = Field(..., description="Client MAC address"),
    days: int = Query(7, ge=1, le=90, description="Number of days to query"),
    metrics: Optional[str] = Query(
        None,
        description="Comma-separated metric names (e.g., 'signal_strength,tx_rate')",
    ),
    aggregate: bool = Query(True, description="Auto-aggregate for long ranges"),
    db: Database = Depends(get_database),
):
    """
    Get historical metrics for a client device (laptop, phone, IoT).

    **Primary value proposition**: Track WiFi performance, bandwidth usage,
    and connection quality over time for end-user devices.

    **Supported Metrics:**
    - signal_strength (dbm) - WiFi signal strength
    - rssi (dbm) - RSSI value
    - tx_rate (kbps) - Upload speed
    - rx_rate (kbps) - Download speed
    - satisfaction (score) - Client satisfaction (0-100)
    - tx_bytes (bytes) - Total uploaded
    - rx_bytes (bytes) - Total downloaded
    """
    start_time = (datetime.now() - timedelta(days=days)).isoformat()

    # Get client info
    client_query = "SELECT mac, hostname, name FROM unifi_clients WHERE mac = ?"
    client_row = db.fetch_one(client_query, (client_mac,))

    if not client_row:
        raise HTTPException(status_code=404, detail="Client not found")

    client_name = client_row.get("hostname") or client_row.get("name") or client_mac

    # Parse requested metrics
    requested_metrics = None
    if metrics:
        requested_metrics = [m.strip() for m in metrics.split(",")]

    # Query client metrics
    query = """
        SELECT metric_name, metric_value, unit, recorded_at
        FROM unifi_client_metrics
        WHERE client_mac = ?
        AND recorded_at >= ?
    """
    params = [client_mac, start_time]

    if requested_metrics:
        placeholders = ",".join(["?" for _ in requested_metrics])
        query += f" AND metric_name IN ({placeholders})"
        params.extend(requested_metrics)

    query += " ORDER BY metric_name, recorded_at ASC"

    rows = db.fetch_all(query, tuple(params))

    # Group by metric name
    metrics_data = {}
    for row in rows:
        metric_name = row["metric_name"]
        if metric_name not in metrics_data:
            metrics_data[metric_name] = []
        metrics_data[metric_name].append(
            (row["recorded_at"], row["metric_value"], row["unit"])
        )

    # Determine aggregation interval
    aggregate_interval = None
    if aggregate and days > 7:
        if days <= 30:
            aggregate_interval = 60  # 1 hour for 8-30 days
        else:
            aggregate_interval = 240  # 4 hours for 31-90 days

    # Build response
    metrics_list = []
    for metric_name, metric_values in metrics_data.items():
        # Apply aggregation if needed
        if aggregate_interval:
            metric_values = aggregate_metrics_by_interval(
                metric_values, aggregate_interval
            )

        # Extract values for statistics
        values = [v[1] for v in metric_values]
        unit = metric_values[0][2] if metric_values else ""

        # Calculate statistics
        statistics = MetricStatistics(
            count=len(values),
            min=min(values) if values else 0,
            max=max(values) if values else 0,
            avg=sum(values) / len(values) if values else 0,
            p95=calculate_percentile(values, 95),
            p99=calculate_percentile(values, 99),
            latest=values[-1] if values else None,
        )

        # Build data points
        data_points = [
            MetricPoint(timestamp=ts, value=val, unit=u) for ts, val, u in metric_values
        ]

        metrics_list.append(
            MetricTimeSeries(
                metric_name=metric_name,
                unit=unit,
                data=data_points,
                statistics=statistics,
            )
        )

    return DeviceMetricsResponse(
        device_mac=client_mac,
        device_name=client_name,
        time_range=f"{days} days",
        metrics=metrics_list,
    )


@router.get(
    "/clients/compare",
    response_model=MultiDeviceMetricsResponse,
    summary="Compare metrics across multiple clients",
)
async def compare_client_metrics(
    client_macs: str = Query(..., description="Comma-separated client MAC addresses"),
    days: int = Query(7, ge=1, le=90, description="Number of days to query"),
    metrics: Optional[str] = Query(
        "signal_strength,tx_rate,rx_rate",
        description="Comma-separated metric names",
    ),
    aggregate: bool = Query(True, description="Auto-aggregate for long ranges"),
    db: Database = Depends(get_database),
):
    """
    Compare metrics across multiple client devices.

    Perfect for comparing WiFi performance between different devices,
    locations, or time periods.
    """
    mac_list = [mac.strip() for mac in client_macs.split(",")]

    if len(mac_list) > 10:
        raise HTTPException(
            status_code=400, detail="Maximum 10 clients allowed for comparison"
        )

    # Fetch metrics for each client
    clients_data = []
    for mac in mac_list:
        try:
            client_metrics = await get_client_historical_metrics(
                client_mac=mac,
                days=days,
                metrics=metrics,
                aggregate=aggregate,
                db=db,
            )
            clients_data.append(client_metrics)
        except HTTPException:
            continue

    if not clients_data:
        raise HTTPException(status_code=404, detail="No valid clients found")

    return MultiDeviceMetricsResponse(time_range=f"{days} days", devices=clients_data)


@router.get(
    "/clients/{client_mac}/export",
    summary="Export client metrics to CSV/JSON",
)
async def export_client_metrics(
    client_mac: str = Field(..., description="Client MAC address"),
    days: int = Query(7, ge=1, le=90, description="Number of days to query"),
    format: str = Query("csv", regex="^(csv|json)$", description="Export format"),
    metrics: Optional[str] = Query(None, description="Comma-separated metric names"),
    db: Database = Depends(get_database),
):
    """
    Export client metrics to CSV or JSON format.

    Download historical data for external analysis.
    """
    client_data = await get_client_historical_metrics(
        client_mac=client_mac,
        days=days,
        metrics=metrics,
        aggregate=False,
        db=db,
    )

    if format == "json":
        return client_data.dict()

    else:  # CSV
        import io

        output = io.StringIO()
        output.write("timestamp,metric_name,value,unit\n")

        for metric in client_data.metrics:
            for point in metric.data:
                line = (
                    f"{point.timestamp},{metric.metric_name},"
                    f"{point.value},{metric.unit}\n"
                )
                output.write(line)

        csv_content = output.getvalue()

        from fastapi.responses import Response

        filename = f"client_{client_mac}_metrics_{days}d.csv"
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )


# DEVICE METRICS ENDPOINTS (Infrastructure)


# Response models
class MetricPoint(BaseModel):
    """Single metric data point."""

    timestamp: str = Field(..., description="ISO 8601 timestamp")
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Unit of measurement")


class MetricStatistics(BaseModel):
    """Statistical summary of metrics."""

    count: int = Field(..., description="Number of data points")
    min: float = Field(..., description="Minimum value")
    max: float = Field(..., description="Maximum value")
    avg: float = Field(..., description="Average value")
    p95: Optional[float] = Field(None, description="95th percentile")
    p99: Optional[float] = Field(None, description="99th percentile")
    latest: Optional[float] = Field(None, description="Most recent value")


class MetricTimeSeries(BaseModel):
    """Time series data for a metric."""

    metric_name: str = Field(..., description="Metric name")
    unit: str = Field(..., description="Unit of measurement")
    data: List[MetricPoint] = Field(..., description="Data points")
    statistics: MetricStatistics = Field(..., description="Statistical summary")


class DeviceMetricsResponse(BaseModel):
    """Response for device historical metrics."""

    device_mac: str = Field(..., description="Device MAC address")
    device_name: Optional[str] = Field(None, description="Device name")
    time_range: str = Field(..., description="Time range queried")
    metrics: List[MetricTimeSeries] = Field(..., description="Metrics data")


class MultiDeviceMetricsResponse(BaseModel):
    """Response for multi-device comparison."""

    time_range: str = Field(..., description="Time range queried")
    devices: List[DeviceMetricsResponse] = Field(..., description="Device metrics")


def calculate_percentile(values: List[float], percentile: int) -> Optional[float]:
    """Calculate percentile value."""
    if not values:
        return None

    sorted_values = sorted(values)
    index = int(len(sorted_values) * (percentile / 100))
    if index >= len(sorted_values):
        index = len(sorted_values) - 1
    return sorted_values[index]


def aggregate_metrics_by_interval(
    metrics: List[tuple], interval_minutes: int
) -> List[tuple]:
    """
    Aggregate metrics by time interval to reduce data points.

    Args:
        metrics: List of (timestamp, value, unit) tuples
        interval_minutes: Interval in minutes

    Returns:
        Aggregated metrics list
    """
    if not metrics:
        return []

    # Group by interval
    aggregated = {}
    for timestamp, value, unit in metrics:
        # Parse timestamp and round to interval
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        # Round down to interval
        interval_start = dt.replace(
            minute=(dt.minute // interval_minutes) * interval_minutes,
            second=0,
            microsecond=0,
        )
        key = interval_start.isoformat()

        if key not in aggregated:
            aggregated[key] = {"values": [], "unit": unit}
        aggregated[key]["values"].append(value)

    # Calculate averages
    result = []
    for timestamp, data in sorted(aggregated.items()):
        avg_value = sum(data["values"]) / len(data["values"])
        result.append((timestamp, avg_value, data["unit"]))

    return result


@router.get(
    "/devices/{device_mac}/metrics",
    response_model=DeviceMetricsResponse,
    summary="Get historical device metrics",
)
async def get_device_historical_metrics(
    device_mac: str = Field(..., description="Device MAC address"),
    days: int = Query(7, ge=1, le=90, description="Number of days to query"),
    metrics: Optional[str] = Query(
        None,
        description=(
            "Comma-separated metric names " "(e.g., 'cpu_usage,memory_usage')"
        ),
    ),
    aggregate: bool = Query(
        True, description="Auto-aggregate for long ranges (>7 days)"
    ),
    db: Database = Depends(get_database),
):
    """
    Get historical metrics for a specific device.

    Returns time-series data for CPU, memory, temperature, and other
    metrics. Data is automatically aggregated for longer time ranges
    to improve performance.

    **Supported Metrics:**
    - cpu_usage (percent)
    - memory_usage (percent)
    - temperature (celsius)
    - uptime (seconds)
    - connected_clients (count)
    - network_rx_mbps (Mbps)
    - network_tx_mbps (Mbps)
    """
    # Calculate time range
    start_time = (datetime.now() - timedelta(days=days)).isoformat()

    # Get device info
    device_query = "SELECT mac, name FROM unifi_devices WHERE mac = ?"
    device_row = db.fetch_one(device_query, (device_mac,))

    if not device_row:
        raise HTTPException(status_code=404, detail="Device not found")

    device_name = device_row.get("name")

    # Parse requested metrics
    requested_metrics = None
    if metrics:
        requested_metrics = [m.strip() for m in metrics.split(",")]

    # Query metrics from database
    query = """
        SELECT metric_name, metric_value, unit, recorded_at
        FROM unifi_device_metrics
        WHERE device_mac = ?
        AND recorded_at >= ?
    """
    params = [device_mac, start_time]

    if requested_metrics:
        placeholders = ",".join(["?" for _ in requested_metrics])
        query += f" AND metric_name IN ({placeholders})"
        params.extend(requested_metrics)

    query += " ORDER BY metric_name, recorded_at ASC"

    rows = db.fetch_all(query, tuple(params))

    # Group by metric name
    metrics_data = {}
    for row in rows:
        metric_name = row["metric_name"]
        if metric_name not in metrics_data:
            metrics_data[metric_name] = []
        metrics_data[metric_name].append(
            (row["recorded_at"], row["metric_value"], row["unit"])
        )

    # Determine aggregation interval
    aggregate_interval = None
    if aggregate and days > 7:
        if days <= 30:
            aggregate_interval = 60  # 1 hour for 8-30 days
        else:
            aggregate_interval = 240  # 4 hours for 31-90 days

    # Build response
    metrics_list = []
    for metric_name, metric_values in metrics_data.items():
        # Apply aggregation if needed
        if aggregate_interval:
            metric_values = aggregate_metrics_by_interval(
                metric_values, aggregate_interval
            )

        # Extract values for statistics
        values = [v[1] for v in metric_values]
        unit = metric_values[0][2] if metric_values else ""

        # Calculate statistics
        statistics = MetricStatistics(
            count=len(values),
            min=min(values) if values else 0,
            max=max(values) if values else 0,
            avg=sum(values) / len(values) if values else 0,
            p95=calculate_percentile(values, 95),
            p99=calculate_percentile(values, 99),
            latest=values[-1] if values else None,
        )

        # Build data points
        data_points = [
            MetricPoint(timestamp=ts, value=val, unit=u) for ts, val, u in metric_values
        ]

        metrics_list.append(
            MetricTimeSeries(
                metric_name=metric_name,
                unit=unit,
                data=data_points,
                statistics=statistics,
            )
        )

    return DeviceMetricsResponse(
        device_mac=device_mac,
        device_name=device_name,
        time_range=f"{days} days",
        metrics=metrics_list,
    )


@router.get(
    "/devices/compare",
    response_model=MultiDeviceMetricsResponse,
    summary="Compare metrics across multiple devices",
)
async def compare_device_metrics(
    device_macs: str = Query(..., description="Comma-separated device MAC addresses"),
    days: int = Query(7, ge=1, le=90, description="Number of days to query"),
    metrics: Optional[str] = Query(
        "cpu_usage,memory_usage,temperature",
        description="Comma-separated metric names",
    ),
    aggregate: bool = Query(True, description="Auto-aggregate for long ranges"),
    db: Database = Depends(get_database),
):
    """
    Compare metrics across multiple devices.

    Returns time-series data for specified metrics across all devices.
    Useful for side-by-side performance comparison.

    **Example:** `/devices/compare?device_macs=aa:bb:cc:dd:ee:ff,`
    `11:22:33:44:55:66&days=30&metrics=cpu_usage,memory_usage`
    """
    # Parse device MACs
    mac_list = [mac.strip() for mac in device_macs.split(",")]

    if len(mac_list) > 10:
        raise HTTPException(
            status_code=400, detail="Maximum 10 devices allowed for comparison"
        )

    # Fetch metrics for each device
    devices_data = []
    for mac in mac_list:
        try:
            device_metrics = await get_device_historical_metrics(
                device_mac=mac,
                days=days,
                metrics=metrics,
                aggregate=aggregate,
                db=db,
            )
            devices_data.append(device_metrics)
        except HTTPException:
            # Skip devices that don't exist
            continue

    if not devices_data:
        raise HTTPException(status_code=404, detail="No valid devices found")

    return MultiDeviceMetricsResponse(time_range=f"{days} days", devices=devices_data)


@router.get(
    "/devices/{device_mac}/export",
    summary="Export device metrics to CSV/JSON",
)
async def export_device_metrics(
    device_mac: str = Field(..., description="Device MAC address"),
    days: int = Query(7, ge=1, le=90, description="Number of days to query"),
    format: str = Query("csv", regex="^(csv|json)$", description="Export format"),
    metrics: Optional[str] = Query(
        None,
        description=("Comma-separated metric names (exports all if not specified)"),
    ),
    db: Database = Depends(get_database),
):
    """
    Export device metrics to CSV or JSON format.

    Returns downloadable file with historical metrics data.
    """
    # Get metrics data
    device_data = await get_device_historical_metrics(
        device_mac=device_mac,
        days=days,
        metrics=metrics,
        aggregate=False,  # No aggregation for exports
        db=db,
    )

    if format == "json":
        # Return as JSON
        return device_data.dict()

    else:  # CSV
        # Build CSV content
        import io

        output = io.StringIO()
        output.write("timestamp,metric_name,value,unit\n")

        for metric in device_data.metrics:
            for point in metric.data:
                line = (
                    f"{point.timestamp},{metric.metric_name},"
                    f"{point.value},{metric.unit}\n"
                )
                output.write(line)

        csv_content = output.getvalue()

        from fastapi.responses import Response

        filename = f"device_{device_mac}_metrics_{days}d.csv"
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

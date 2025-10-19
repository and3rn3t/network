"""Optimized device comparison and correlation endpoints."""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.src.middleware.error_handler import NotFoundError, ValidationError
from backend.src.services.cache_service import (
    cache_key_for_comparison,
    cache_key_for_correlation,
    get_cache,
)
from backend.src.services.database_service import get_database
from src.database.database import Database

router = APIRouter()


def get_host_id_mapping(db: Database, device_ids: List[int]) -> dict:
    """
    Map numeric device IDs to database TEXT host_ids.

    Args:
        db: Database instance
        device_ids: List of numeric device IDs

    Returns:
        Dict mapping device_id -> (host_id, device_name)
    """
    if not device_ids:
        return {}

    # Build query with multiple offsets
    mapping = {}
    for device_id in device_ids:
        query = """
            SELECT id, name FROM hosts
            ORDER BY rowid
            LIMIT 1 OFFSET ?
        """
        cursor = db.execute(query, (device_id - 1,))
        row = cursor.fetchone()

        if row:
            mapping[device_id] = (row[0], row[1] or "Unknown")
        else:
            raise NotFoundError(f"Device with ID {device_id} not found")

    return mapping


@router.get("/compare")
async def compare_devices(
    device_ids: str = Query(
        ..., description="Comma-separated device IDs (e.g., 1,2,3)"
    ),
    metric_types: Optional[str] = Query(
        None,
        description="Comma-separated metric types to fetch (e.g., cpu_usage,memory_usage)",
    ),
    hours: int = Query(24, ge=1, le=168, description="Hours of history"),
    db: Database = Depends(get_database),
):
    """
    Compare multiple devices in a single request.

    This endpoint reduces API calls by fetching metrics for multiple devices
    in one optimized query.

    Example:
        /api/devices/compare?device_ids=1,2,3&metric_types=cpu_usage,memory_usage&hours=24
    """
    # Check cache first
    cache = get_cache()

    # Parse device IDs
    try:
        device_id_list = [int(x.strip()) for x in device_ids.split(",")]
    except ValueError:
        raise ValidationError(
            "Invalid device_ids format. Expected comma-separated integers."
        )

    # Parse metric types
    metric_type_list = None
    if metric_types:
        metric_type_list = [x.strip() for x in metric_types.split(",")]

    # Generate cache key
    cache_key = cache_key_for_comparison(device_id_list, hours, metric_type_list)

    # Try to get from cache
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        cached_result["cached"] = True
        return cached_result

    if len(device_id_list) > 10:
        raise ValidationError("Maximum 10 devices allowed for comparison")

    if not device_id_list:
        raise ValidationError("At least one device_id required")

    # Parse metric types (already done above for cache key)
    # metric_type_list already set

    # Get host ID mappings
    host_mapping = get_host_id_mapping(db, device_id_list)

    # Build optimized query for all devices
    since = datetime.utcnow() - timedelta(hours=hours)

    # Use IN clause for batch query
    host_ids = [host_mapping[dev_id][0] for dev_id in device_id_list]
    placeholders = ",".join(["?"] * len(host_ids))

    query = f"""
        SELECT host_id, metric_name, metric_value, unit, recorded_at
        FROM metrics
        WHERE host_id IN ({placeholders})
        AND recorded_at >= ?
    """
    params = list(host_ids) + [since.isoformat() + "Z"]

    if metric_type_list:
        metric_placeholders = ",".join(["?"] * len(metric_type_list))
        query += f" AND metric_name IN ({metric_placeholders})"
        params.extend(metric_type_list)

    query += " ORDER BY recorded_at ASC"

    rows = db.execute(query, tuple(params)).fetchall()

    # Group metrics by device
    device_metrics = {dev_id: [] for dev_id in device_id_list}

    # Create reverse mapping (host_id -> device_id)
    reverse_mapping = {v[0]: k for k, v in host_mapping.items()}

    for row in rows:
        host_id = row[0]
        device_id = reverse_mapping.get(host_id)

        if device_id:
            device_metrics[device_id].append(
                {
                    "metric_type": row[1],
                    "value": row[2],
                    "unit": row[3],
                    "timestamp": row[4],
                }
            )

    # Build response
    devices = []
    for device_id in device_id_list:
        host_id, device_name = host_mapping[device_id]
        devices.append(
            {
                "device_id": device_id,
                "device_name": device_name,
                "metrics": device_metrics[device_id],
                "count": len(device_metrics[device_id]),
            }
        )

    result = {
        "devices": devices,
        "total_devices": len(device_id_list),
        "hours": hours,
        "metric_types": metric_type_list,
        "query_time": datetime.utcnow().isoformat() + "Z",
        "cached": False,
    }

    # Cache the result (TTL: 2 minutes for comparison data)
    cache.set(cache_key, result, ttl_seconds=120)

    return result


@router.get("/{device_id}/correlation")
async def calculate_correlation(
    device_id: int,
    metric_x: str = Query(
        ..., description="First metric for correlation (e.g., cpu_usage)"
    ),
    metric_y: str = Query(
        ..., description="Second metric for correlation (e.g., memory_usage)"
    ),
    hours: int = Query(24, ge=1, le=168, description="Hours of history"),
    db: Database = Depends(get_database),
):
    """
    Calculate correlation between two metrics on the server side.

    Returns Pearson correlation coefficient, R² value, linear regression parameters,
    and the data points used for calculation.

    This is more efficient than fetching all data and calculating client-side,
    especially for large datasets.

    Example:
        /api/devices/1/correlation?metric_x=cpu_usage&metric_y=memory_usage&hours=24
    """
    # Check cache first
    cache = get_cache()
    cache_key = cache_key_for_correlation(device_id, metric_x, metric_y, hours)

    cached_result = cache.get(cache_key)
    if cached_result is not None:
        cached_result["cached"] = True
        return cached_result

    # Get host mapping
    host_mapping = get_host_id_mapping(db, [device_id])
    host_id, device_name = host_mapping[device_id]

    # Fetch both metrics
    since = datetime.utcnow() - timedelta(hours=hours)

    query = """
        SELECT metric_name, metric_value, recorded_at
        FROM metrics
        WHERE host_id = ?
        AND recorded_at >= ?
        AND metric_name IN (?, ?)
        ORDER BY recorded_at ASC
    """

    rows = db.execute(
        query, (host_id, since.isoformat() + "Z", metric_x, metric_y)
    ).fetchall()

    # Organize data by timestamp
    data_map = {}
    for row in rows:
        metric_name = row[0]
        metric_value = row[1]
        timestamp = row[2]

        if timestamp not in data_map:
            data_map[timestamp] = {}

        data_map[timestamp][metric_name] = metric_value

    # Filter to only timestamps with both metrics
    paired_data = []
    for timestamp, metrics in data_map.items():
        if metric_x in metrics and metric_y in metrics:
            paired_data.append(
                {
                    "timestamp": timestamp,
                    "x": metrics[metric_x],
                    "y": metrics[metric_y],
                }
            )

    if len(paired_data) < 2:
        result = {
            "device_id": device_id,
            "device_name": device_name,
            "metric_x": metric_x,
            "metric_y": metric_y,
            "correlation": {
                "coefficient": 0,
                "r_squared": 0,
                "slope": 0,
                "intercept": 0,
                "strength": "Insufficient Data",
                "direction": "None",
                "data_points": len(paired_data),
            },
            "data": paired_data,
            "hours": hours,
            "cached": False,
        }
        # Cache even insufficient data results (TTL: 5 minutes)
        cache.set(cache_key, result, ttl_seconds=300)
        return result

    # Calculate Pearson correlation
    n = len(paired_data)
    sum_x = sum(d["x"] for d in paired_data)
    sum_y = sum(d["y"] for d in paired_data)
    sum_xy = sum(d["x"] * d["y"] for d in paired_data)
    sum_x2 = sum(d["x"] ** 2 for d in paired_data)
    sum_y2 = sum(d["y"] ** 2 for d in paired_data)

    # Pearson correlation coefficient
    numerator = n * sum_xy - sum_x * sum_y
    denominator_x = n * sum_x2 - sum_x**2
    denominator_y = n * sum_y2 - sum_y**2
    denominator = (denominator_x * denominator_y) ** 0.5

    if denominator == 0:
        coefficient = 0
    else:
        coefficient = numerator / denominator

    # Linear regression
    mean_x = sum_x / n
    mean_y = sum_y / n

    if denominator_x == 0:
        slope = 0
        intercept = mean_y
    else:
        slope = (n * sum_xy - sum_x * sum_y) / denominator_x
        intercept = mean_y - slope * mean_x

    # R² value
    r_squared = coefficient**2

    # Determine strength
    abs_corr = abs(coefficient)
    if abs_corr >= 0.9:
        strength = "Very Strong"
    elif abs_corr >= 0.7:
        strength = "Strong"
    elif abs_corr >= 0.5:
        strength = "Moderate"
    elif abs_corr >= 0.3:
        strength = "Weak"
    else:
        strength = "Very Weak"

    # Determine direction
    if coefficient > 0:
        direction = "Positive"
    elif coefficient < 0:
        direction = "Negative"
    else:
        direction = "None"

    result = {
        "device_id": device_id,
        "device_name": device_name,
        "metric_x": metric_x,
        "metric_y": metric_y,
        "correlation": {
            "coefficient": round(coefficient, 6),
            "r_squared": round(r_squared, 6),
            "slope": round(slope, 6),
            "intercept": round(intercept, 6),
            "strength": strength,
            "direction": direction,
            "data_points": n,
        },
        "data": paired_data[:1000],  # Limit response size, send max 1000 points
        "hours": hours,
        "query_time": datetime.utcnow().isoformat() + "Z",
        "cached": False,
    }

    # Cache the result (TTL: 5 minutes)
    cache.set(cache_key, result, ttl_seconds=300)

    return result


@router.get("/batch-metrics")
async def batch_metrics(
    device_ids: str = Query(..., description="Comma-separated device IDs"),
    hours: int = Query(24, ge=1, le=168, description="Hours of history"),
    aggregate: Optional[str] = Query(
        None, description="Aggregation function: avg, min, max, count"
    ),
    interval_minutes: Optional[int] = Query(
        None, ge=1, le=1440, description="Group data by interval (minutes)"
    ),
    db: Database = Depends(get_database),
):
    """
    Fetch metrics for multiple devices with optional aggregation.

    This endpoint is optimized for dashboard widgets that need
    aggregated data from multiple devices.

    Example:
        /api/devices/batch-metrics?device_ids=1,2,3&hours=24&aggregate=avg&interval_minutes=60
    """
    # Parse device IDs
    try:
        device_id_list = [int(x.strip()) for x in device_ids.split(",")]
    except ValueError:
        raise ValidationError("Invalid device_ids format")

    if len(device_id_list) > 20:
        raise ValidationError("Maximum 20 devices allowed")

    # Get host mappings
    host_mapping = get_host_id_mapping(db, device_id_list)
    host_ids = [host_mapping[dev_id][0] for dev_id in device_id_list]

    since = datetime.utcnow() - timedelta(hours=hours)

    # Build query based on aggregation
    if aggregate and interval_minutes:
        # Aggregated query with time bucketing
        # SQLite doesn't have native time bucketing, so we'll do it in Python
        query = f"""
            SELECT host_id, metric_name, metric_value, unit, recorded_at
            FROM metrics
            WHERE host_id IN ({','.join(['?'] * len(host_ids))})
            AND recorded_at >= ?
            ORDER BY recorded_at ASC
        """
        params = list(host_ids) + [since.isoformat() + "Z"]

        rows = db.execute(query, tuple(params)).fetchall()

        # Group by device, metric, and time bucket
        from collections import defaultdict

        buckets = defaultdict(lambda: defaultdict(list))

        for row in rows:
            host_id = row[0]
            metric_name = row[1]
            metric_value = row[2]
            timestamp_str = row[4]

            # Parse timestamp and bucket it
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            bucket_key = (timestamp.timestamp() // (interval_minutes * 60)) * (
                interval_minutes * 60
            )
            bucket_time = datetime.fromtimestamp(bucket_key)

            buckets[(host_id, metric_name, bucket_time.isoformat() + "Z")].append(
                metric_value
            )

        # Calculate aggregates
        aggregated_data = []
        for (host_id, metric_name, bucket_time), values in buckets.items():
            if aggregate == "avg":
                agg_value = sum(values) / len(values)
            elif aggregate == "min":
                agg_value = min(values)
            elif aggregate == "max":
                agg_value = max(values)
            elif aggregate == "count":
                agg_value = len(values)
            else:
                agg_value = sum(values) / len(values)  # default to avg

            aggregated_data.append(
                {
                    "host_id": host_id,
                    "metric_name": metric_name,
                    "value": round(agg_value, 2),
                    "timestamp": bucket_time,
                    "sample_count": len(values),
                }
            )

        # Group by device
        reverse_mapping = {v[0]: k for k, v in host_mapping.items()}
        device_data = {dev_id: [] for dev_id in device_id_list}

        for item in aggregated_data:
            device_id = reverse_mapping.get(item["host_id"])
            if device_id:
                device_data[device_id].append(
                    {
                        "metric_type": item["metric_name"],
                        "value": item["value"],
                        "timestamp": item["timestamp"],
                        "sample_count": item["sample_count"],
                    }
                )

        devices = []
        for device_id in device_id_list:
            _, device_name = host_mapping[device_id]
            devices.append(
                {
                    "device_id": device_id,
                    "device_name": device_name,
                    "metrics": device_data[device_id],
                    "count": len(device_data[device_id]),
                }
            )

        return {
            "devices": devices,
            "total_devices": len(device_id_list),
            "hours": hours,
            "aggregation": aggregate,
            "interval_minutes": interval_minutes,
            "query_time": datetime.utcnow().isoformat() + "Z",
        }
    else:
        # Non-aggregated query (same as compare endpoint)
        placeholders = ",".join(["?"] * len(host_ids))
        query = f"""
            SELECT host_id, metric_name, metric_value, unit, recorded_at
            FROM metrics
            WHERE host_id IN ({placeholders})
            AND recorded_at >= ?
            ORDER BY recorded_at ASC
        """
        params = list(host_ids) + [since.isoformat() + "Z"]

        rows = db.execute(query, tuple(params)).fetchall()

        # Group by device
        reverse_mapping = {v[0]: k for k, v in host_mapping.items()}
        device_metrics = {dev_id: [] for dev_id in device_id_list}

        for row in rows:
            host_id = row[0]
            device_id = reverse_mapping.get(host_id)

            if device_id:
                device_metrics[device_id].append(
                    {
                        "metric_type": row[1],
                        "value": row[2],
                        "unit": row[3],
                        "timestamp": row[4],
                    }
                )

        devices = []
        for device_id in device_id_list:
            _, device_name = host_mapping[device_id]
            devices.append(
                {
                    "device_id": device_id,
                    "device_name": device_name,
                    "metrics": device_metrics[device_id],
                    "count": len(device_metrics[device_id]),
                }
            )

        return {
            "devices": devices,
            "total_devices": len(device_id_list),
            "hours": hours,
            "query_time": datetime.utcnow().isoformat() + "Z",
        }

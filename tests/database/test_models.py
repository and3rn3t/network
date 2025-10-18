"""Tests for database models."""

import json
from datetime import datetime

import pytest

from src.database.models import CollectionRun, Event, Host, HostStatus, Metric


class TestHost:
    """Test Host model."""

    def test_create_from_api_response(self):
        """Test creating Host from API response."""
        api_data = {
            "id": "host123",
            "hardwareId": "hw456",
            "type": "switch",
            "ipAddress": "192.168.1.100",
            "mac": "aa:bb:cc:dd:ee:ff",
            "name": "Office Switch",
            "owner": True,
            "isBlocked": False,
            "firmwareVersion": "6.5.59",
            "model": "USW-24-POE",
            "registrationTime": "2024-01-01T00:00:00Z",
        }

        host = Host.from_api_response(api_data)

        assert host.id == "host123"
        assert host.hardware_id == "hw456"
        assert host.type == "switch"
        assert host.ip_address == "192.168.1.100"
        assert host.mac_address == "aa:bb:cc:dd:ee:ff"
        assert host.name == "Office Switch"
        assert host.owner is True
        assert host.is_blocked is False
        assert host.firmware_version == "6.5.59"
        assert host.model == "USW-24-POE"

    def test_from_db_row(self):
        """Test creating Host from database row."""
        db_row = {
            "id": "host123",
            "hardware_id": "hw456",
            "type": "switch",
            "ip_address": "192.168.1.100",
            "mac_address": "aa:bb:cc:dd:ee:ff",
            "name": "Office Switch",
            "owner": 1,
            "is_blocked": 0,
            "firmware_version": "6.5.59",
            "model": "USW-24-POE",
            "registration_time": "2024-01-01T00:00:00Z",
            "first_seen": "2024-01-01T00:00:00Z",
            "last_seen": "2024-01-02T00:00:00Z",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
        }

        host = Host.from_db_row(db_row)

        assert host.id == "host123"
        assert host.owner is True
        assert host.is_blocked is False

    def test_to_db_params(self):
        """Test converting Host to database parameters."""
        host = Host(
            id="host123", hardware_id="hw456", type="switch", name="Test Switch"
        )

        params = host.to_db_params()

        assert len(params) == 11
        assert params[0] == "host123"
        assert params[1] == "hw456"
        assert params[2] == "switch"


class TestHostStatus:
    """Test HostStatus model."""

    def test_create_from_api_response(self):
        """Test creating HostStatus from API response."""
        api_data = {
            "isOnline": True,
            "uptimeSeconds": 86400,
            "metrics": {
                "cpu": 25.5,
                "memory": 45.2,
                "temperature": 42.0,
            },
            "lastConnectionStateChange": "2024-01-01T12:00:00Z",
            "latestBackupTime": "2024-01-01T00:00:00Z",
        }

        status = HostStatus.from_api_response("host123", api_data)

        assert status.host_id == "host123"
        assert status.status == "online"
        assert status.is_online is True
        assert status.uptime_seconds == 86400
        assert status.cpu_usage == 25.5
        assert status.memory_usage == 45.2
        assert status.temperature == 42.0

    def test_offline_status(self):
        """Test offline status detection."""
        api_data = {"isOnline": False}

        status = HostStatus.from_api_response("host123", api_data)

        assert status.status == "offline"
        assert status.is_online is False

    def test_to_db_params(self):
        """Test converting to database parameters."""
        status = HostStatus(
            host_id="host123", status="online", is_online=True, uptime_seconds=3600
        )

        params = status.to_db_params()

        assert params[0] == "host123"
        assert params[1] == "online"
        assert params[2] == 1  # Boolean converted to int


class TestEvent:
    """Test Event model."""

    def test_create_status_change_event(self):
        """Test creating status change event."""
        event = Event.create_status_change(
            host_id="host123", old_status="offline", new_status="online"
        )

        assert event.event_type == "status_change"
        assert event.severity == "info"
        assert event.host_id == "host123"
        assert "offline" in event.description
        assert "online" in event.description

    def test_create_error_event(self):
        """Test creating error event."""
        event = Event.create_error(
            host_id="host123",
            title="Connection Failed",
            description="Unable to reach host",
        )

        assert event.event_type == "error"
        assert event.severity == "error"
        assert event.host_id == "host123"
        assert event.title == "Connection Failed"
        assert event.description == "Unable to reach host"

    def test_create_custom_severity(self):
        """Test creating event with custom severity."""
        event = Event.create_error(
            host_id="host123",
            title="Warning",
            description="High CPU usage",
            severity="warning",
        )

        assert event.severity == "warning"

    def test_to_db_params(self):
        """Test converting to database parameters."""
        event = Event(
            event_type="test",
            severity="info",
            title="Test Event",
            host_id="host123",
            description="Test description",
        )

        params = event.to_db_params()

        assert params[0] == "host123"
        assert params[1] == "test"
        assert params[2] == "info"
        assert params[3] == "Test Event"


class TestMetric:
    """Test Metric model."""

    def test_create_metric(self):
        """Test creating metric."""
        metric = Metric(
            host_id="host123",
            metric_name="cpu_usage",
            metric_value=45.5,
            unit="percent",
        )

        assert metric.host_id == "host123"
        assert metric.metric_name == "cpu_usage"
        assert metric.metric_value == 45.5
        assert metric.unit == "percent"

    def test_to_db_params(self):
        """Test converting to database parameters."""
        metric = Metric(
            host_id="host123",
            metric_name="cpu_usage",
            metric_value=45.5,
            unit="percent",
        )

        params = metric.to_db_params()

        assert len(params) == 4
        assert params[0] == "host123"
        assert params[1] == "cpu_usage"
        assert params[2] == 45.5
        assert params[3] == "percent"

    def test_from_db_row(self):
        """Test creating from database row."""
        db_row = {
            "id": 1,
            "host_id": "host123",
            "metric_name": "cpu_usage",
            "metric_value": 45.5,
            "unit": "percent",
            "recorded_at": "2024-01-01T12:00:00Z",
        }

        metric = Metric.from_db_row(db_row)

        assert metric.id == 1
        assert metric.host_id == "host123"
        assert metric.metric_name == "cpu_usage"


class TestCollectionRun:
    """Test CollectionRun model."""

    def test_create_collection_run(self):
        """Test creating collection run."""
        run = CollectionRun(
            start_time="2024-01-01T12:00:00Z",
            status="completed",
            hosts_collected=10,
            duration_seconds=5.5,
        )

        assert run.start_time == "2024-01-01T12:00:00Z"
        assert run.status == "completed"
        assert run.hosts_collected == 10
        assert run.duration_seconds == 5.5

    def test_to_db_params(self):
        """Test converting to database parameters."""
        run = CollectionRun(
            start_time="2024-01-01T12:00:00Z",
            status="completed",
            hosts_collected=10,
            duration_seconds=5.5,
            error_message=None,
        )

        params = run.to_db_params()

        assert params[0] == "2024-01-01T12:00:00Z"
        assert params[1] == "completed"

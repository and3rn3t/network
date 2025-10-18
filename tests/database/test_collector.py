"""Tests for data collector."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.collector import CollectorConfig, DataCollector
from src.database import Database
from src.database.models import Host, HostStatus


@pytest.fixture
def test_config(tmp_path):
    """Create test collector configuration."""
    return CollectorConfig(
        api_key="test-key",
        api_base_url="https://api.test.com/v1",
        collection_interval=60,
        status_retention_days=30,
        event_retention_days=90,
        metric_retention_days=7,
        enable_metrics=True,
        enable_events=True,
        log_level="INFO",
        db_path=str(tmp_path / "test.db"),
    )


@pytest.fixture
def test_db(tmp_path):
    """Create test database."""
    db_path = tmp_path / "test.db"
    db = Database(db_path)
    db.initialize()
    yield db
    db.close()


@pytest.fixture
def mock_api_client():
    """Create mock API client."""
    client = Mock()
    client.get_hosts = Mock()
    return client


class TestCollectorConfig:
    """Test CollectorConfig."""

    def test_defaults(self):
        """Test default configuration."""
        config = CollectorConfig(api_key="test")

        assert config.collection_interval == 300
        assert config.status_retention_days == 90
        assert config.event_retention_days == 365
        assert config.metric_retention_days == 30
        assert config.enable_metrics is True
        assert config.enable_events is True

    def test_validation_missing_api_key(self):
        """Test validation fails without API key."""
        config = CollectorConfig()

        with pytest.raises(ValueError, match="api_key is required"):
            config.validate()

    def test_validation_invalid_interval(self):
        """Test validation fails with invalid interval."""
        config = CollectorConfig(api_key="test", collection_interval=30)

        with pytest.raises(ValueError, match="at least 60 seconds"):
            config.validate()

    def test_validation_invalid_retention(self):
        """Test validation fails with invalid retention."""
        config = CollectorConfig(api_key="test", status_retention_days=0)

        with pytest.raises(ValueError, match="at least 1"):
            config.validate()


class TestDataCollector:
    """Test DataCollector."""

    def test_init(self, test_config, mock_api_client, test_db):
        """Test collector initialization."""
        collector = DataCollector(
            test_config, api_client=mock_api_client, database=test_db
        )

        assert collector.config == test_config
        assert collector.api == mock_api_client
        assert collector.db == test_db
        assert collector._collection_count == 0
        assert collector._error_count == 0

    def test_collect_empty_response(self, test_config, mock_api_client, test_db):
        """Test collection with no hosts."""
        mock_api_client.get_hosts.return_value = []

        collector = DataCollector(
            test_config, api_client=mock_api_client, database=test_db
        )

        stats = collector.collect()

        assert stats["hosts_processed"] == 0
        assert stats["hosts_created"] == 0
        assert stats["errors"] == 0

    def test_collect_single_host_new(self, test_config, mock_api_client, test_db):
        """Test collecting a new host."""
        mock_api_client.get_hosts.return_value = [
            {
                "id": "host123",
                "hardwareId": "hw456",
                "type": "switch",
                "name": "Test Switch",
                "isOnline": True,
            }
        ]

        collector = DataCollector(
            test_config, api_client=mock_api_client, database=test_db
        )

        stats = collector.collect()

        assert stats["hosts_processed"] == 1
        assert stats["hosts_created"] == 1
        assert stats["hosts_updated"] == 0
        assert stats["status_records"] == 1
        assert stats["events_created"] == 1  # host_discovered event
        assert stats["errors"] == 0

        # Verify host was created
        host = collector.host_repo.get_by_id("host123")
        assert host is not None
        assert host.name == "Test Switch"

    def test_collect_existing_host(self, test_config, mock_api_client, test_db):
        """Test collecting an existing host."""
        # Create initial host
        collector = DataCollector(
            test_config, api_client=mock_api_client, database=test_db
        )

        initial_host = Host(
            id="host123", hardware_id="hw456", type="switch", name="Old Name"
        )
        collector.host_repo.create(initial_host)

        # Mock API with updated data
        mock_api_client.get_hosts.return_value = [
            {
                "id": "host123",
                "hardwareId": "hw456",
                "type": "switch",
                "name": "New Name",
                "isOnline": True,
            }
        ]

        stats = collector.collect()

        assert stats["hosts_processed"] == 1
        assert stats["hosts_created"] == 0
        assert stats["hosts_updated"] == 1
        assert stats["events_created"] == 0  # No status change

        # Verify host was updated
        host = collector.host_repo.get_by_id("host123")
        assert host.name == "New Name"

    def test_collect_status_change(self, test_config, mock_api_client, test_db):
        """Test detecting status changes."""
        collector = DataCollector(
            test_config, api_client=mock_api_client, database=test_db
        )

        # Create host with online status
        host = Host(id="host123", hardware_id="hw456", type="switch")
        collector.host_repo.create(host)

        status = HostStatus(host_id="host123", status="online", is_online=True)
        collector.status_repo.create(status)

        # Mock API with offline status
        mock_api_client.get_hosts.return_value = [
            {
                "id": "host123",
                "hardwareId": "hw456",
                "type": "switch",
                "isOnline": False,
            }
        ]

        stats = collector.collect()

        # Should generate status_change event
        assert stats["events_created"] == 1

        # Verify event was created
        events = collector.event_repo.get_for_host("host123")
        assert len(events) == 1
        assert events[0].event_type == "status_change"

    def test_collect_with_metrics(self, test_config, mock_api_client, test_db):
        """Test metric collection."""
        mock_api_client.get_hosts.return_value = [
            {
                "id": "host123",
                "hardwareId": "hw456",
                "type": "switch",
                "uptimeSeconds": 86400,
                "metrics": {
                    "cpu": 25.5,
                    "memory": 45.2,
                    "temperature": 42.0,
                },
            }
        ]

        collector = DataCollector(
            test_config, api_client=mock_api_client, database=test_db
        )

        stats = collector.collect()

        # Should create metrics
        assert stats["metrics_created"] > 0

        # Verify metrics were stored
        metrics = collector.metric_repo.get_for_host("host123")
        assert len(metrics) > 0

        metric_names = [m.metric_name for m in metrics]
        assert "cpu_usage" in metric_names
        assert "memory_usage" in metric_names
        assert "temperature" in metric_names
        assert "uptime" in metric_names

    def test_collect_with_errors(self, test_config, mock_api_client, test_db):
        """Test handling errors during collection."""
        # First host is valid, second causes error
        mock_api_client.get_hosts.return_value = [
            {
                "id": "host123",
                "hardwareId": "hw456",
                "type": "switch",
            },
            {
                "id": None,  # Missing ID will cause error
                "hardwareId": "hw789",
                "type": "ap",
            },
        ]

        collector = DataCollector(
            test_config, api_client=mock_api_client, database=test_db
        )

        stats = collector.collect()

        # Should process first host successfully
        assert stats["hosts_processed"] == 1
        # Should record error for second host
        assert stats["errors"] == 1

    def test_get_stats(self, test_config, mock_api_client, test_db):
        """Test getting collector statistics."""
        collector = DataCollector(
            test_config, api_client=mock_api_client, database=test_db
        )

        mock_api_client.get_hosts.return_value = [
            {
                "id": "host123",
                "hardwareId": "hw456",
                "type": "switch",
            }
        ]

        collector.collect()

        stats = collector.get_stats()

        assert stats["collection_count"] == 1
        assert stats["error_count"] == 0
        assert stats["total_hosts"] == 1
        assert stats["last_collection"] is not None

    def test_extract_metrics_with_data(self, test_config, mock_api_client, test_db):
        """Test metric extraction with complete data."""
        collector = DataCollector(
            test_config, api_client=mock_api_client, database=test_db
        )

        host_data = {
            "uptimeSeconds": 3600,
            "metrics": {
                "cpu": 25.5,
                "memory": 45.2,
                "temperature": 42.0,
            },
        }

        metrics = collector._extract_metrics("host123", host_data)

        assert len(metrics) == 4
        metric_names = [m.metric_name for m in metrics]
        assert "uptime" in metric_names
        assert "cpu_usage" in metric_names
        assert "memory_usage" in metric_names
        assert "temperature" in metric_names

    def test_extract_metrics_partial_data(self, test_config, mock_api_client, test_db):
        """Test metric extraction with partial data."""
        collector = DataCollector(
            test_config, api_client=mock_api_client, database=test_db
        )

        host_data = {
            "uptimeSeconds": 3600,
            "metrics": {
                "cpu": 25.5,
                # Missing memory and temperature
            },
        }

        metrics = collector._extract_metrics("host123", host_data)

        assert len(metrics) == 2  # Only uptime and cpu
        metric_names = [m.metric_name for m in metrics]
        assert "uptime" in metric_names
        assert "cpu_usage" in metric_names

    def test_metrics_disabled(self, test_config, mock_api_client, test_db):
        """Test collection with metrics disabled."""
        test_config.enable_metrics = False

        mock_api_client.get_hosts.return_value = [
            {
                "id": "host123",
                "hardwareId": "hw456",
                "type": "switch",
                "uptimeSeconds": 3600,
                "metrics": {"cpu": 25.5},
            }
        ]

        collector = DataCollector(
            test_config, api_client=mock_api_client, database=test_db
        )

        stats = collector.collect()

        assert stats["metrics_created"] == 0

    def test_events_disabled(self, test_config, mock_api_client, test_db):
        """Test collection with events disabled."""
        test_config.enable_events = False

        mock_api_client.get_hosts.return_value = [
            {
                "id": "host123",
                "hardwareId": "hw456",
                "type": "switch",
            }
        ]

        collector = DataCollector(
            test_config, api_client=mock_api_client, database=test_db
        )

        stats = collector.collect()

        assert stats["events_created"] == 0

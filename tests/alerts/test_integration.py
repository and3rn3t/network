"""
Integration tests for the alert system.

Tests complete alert lifecycle including:
- Rule creation and evaluation
- Alert triggering and resolution
- Notification delivery
- Alert acknowledgment and muting
- End-to-end workflows
"""

import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.alerts.alert_manager import AlertManager
from src.alerts.models import AlertRule, NotificationChannel
from src.database.database import Database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db = Database(db_path)
    db.initialize()

    # Load alert schema
    schema_path = (
        Path(__file__).parent.parent.parent / "src" / "database" / "schema_alerts.sql"
    )
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(db_path)
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()

    yield db

    # Cleanup
    db.close()
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def alert_manager(temp_db):
    """Create an AlertManager with temporary database."""
    return AlertManager(temp_db)


@pytest.fixture
def mock_notifiers():
    """Create mock notifiers for testing."""
    with patch("src.alerts.notifiers.email.smtplib.SMTP") as mock_smtp, patch(
        "src.alerts.notifiers.webhook.requests.post"
    ) as mock_post:
        # Configure SMTP mock
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        # Configure webhook mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_post.return_value = mock_response

        yield {
            "smtp": mock_smtp,
            "smtp_instance": mock_smtp_instance,
            "webhook": mock_post,
            "webhook_response": mock_response,
        }


class TestAlertLifecycle:
    """Test complete alert lifecycle from creation to resolution."""

    def test_threshold_alert_lifecycle(self, alert_manager, mock_notifiers):
        """Test threshold alert from trigger to resolution."""
        # 1. Create a notification channel
        channel_config = {
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "smtp_user": "alerts@example.com",
            "smtp_password": "password",
            "from_email": "alerts@example.com",
            "to_emails": ["admin@example.com"],
            "min_severity": "warning",
        }

        channel = alert_manager.create_channel(
            NotificationChannel(
                id="email_alerts",
                name="Email Alerts",
                channel_type="email",
                config=channel_config,
                enabled=True,
            )
        )

        assert channel.id is not None
        assert channel.name == "Email Alerts"

        # 2. Create an alert rule
        rule = alert_manager.create_alert_rule(
            name="High CPU Alert",
            description="Alert when CPU exceeds 80%",
            rule_type="threshold",
            metric_name="cpu_usage",
            condition=">",
            threshold=80.0,
            severity="warning",
            cooldown_minutes=5,
            notification_channels=[channel.id],
        )

        assert rule.id is not None
        assert rule.enabled is True

        # 3. Insert metric data that triggers the alert
        alert_manager.db.execute(
            """
            INSERT INTO metrics (host_id, metric_type, value, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            ("test-host-1", "cpu_usage", 85.0, datetime.now().isoformat()),
        )

        # 4. Evaluate rules (should trigger alert)
        triggered_count = alert_manager.evaluate_rules()
        assert triggered_count == 1

        # 5. Verify alert was created
        alerts = alert_manager.get_active_alerts()
        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.rule_id == rule.id
        assert alert.severity == "warning"
        assert alert.status == "triggered"
        assert "85.0" in alert.message

        # 6. Verify notification was sent
        mock_notifiers["smtp_instance"].send_message.assert_called_once()
        email_args = mock_notifiers["smtp_instance"].send_message.call_args
        assert "High CPU Alert" in str(email_args)

        # 7. Acknowledge the alert
        ack_alert = alert_manager.acknowledge_alert(
            alert.id, acknowledged_by="admin", notes="Investigating high CPU"
        )
        assert ack_alert.status == "acknowledged"
        assert ack_alert.acknowledged_by == "admin"

        # 8. Insert normal metric data
        alert_manager.db.execute(
            """
            INSERT INTO metrics (host_id, metric_type, value, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            ("test-host-1", "cpu_usage", 60.0, datetime.now().isoformat()),
        )

        # 9. Evaluate rules again (should resolve alert)
        alert_manager.evaluate_rules()

        # 10. Verify alert was resolved
        resolved_alert = alert_manager.get_alert(alert.id)
        assert resolved_alert.status == "resolved"
        assert resolved_alert.resolved_at is not None

        # Verify no active alerts remain
        active_alerts = alert_manager.get_active_alerts()
        assert len(active_alerts) == 0

    def test_status_change_alert_lifecycle(self, alert_manager, mock_notifiers):
        """Test status change alert from trigger to resolution."""
        # 1. Create webhook notification channel
        channel_config = {
            "webhook_url": "https://hooks.slack.com/services/TEST/TEST/TEST",
            "webhook_type": "slack",
            "min_severity": "critical",
        }

        channel = alert_manager.create_channel(
            NotificationChannel(
                id="slack_alerts",
                name="Slack Alerts",
                channel_type="webhook",
                config=channel_config,
                enabled=True,
            )
        )

        # 2. Create status change rule
        rule = alert_manager.create_alert_rule(
            name="Device Offline Alert",
            description="Alert when device goes offline",
            rule_type="status_change",
            metric_name="device_status",
            expected_status="online",
            severity="critical",
            cooldown_minutes=10,
            notification_channels=[channel.id],
        )

        # 3. Insert initial online status
        alert_manager.db.execute(
            """
            INSERT INTO metrics (host_id, metric_type, value, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (
                "device-001",
                "device_status",
                "online",
                datetime.now().isoformat(),
            ),
        )

        # 4. Change status to offline
        alert_manager.db.execute(
            """
            INSERT INTO metrics (host_id, metric_type, value, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (
                "device-001",
                "device_status",
                "offline",
                datetime.now().isoformat(),
            ),
        )

        # 5. Evaluate and trigger alert
        triggered = alert_manager.evaluate_rules()
        assert triggered == 1

        # 6. Verify alert and notification
        alerts = alert_manager.get_active_alerts()
        assert len(alerts) == 1
        assert alerts[0].severity == "critical"
        assert "offline" in alerts[0].message.lower()

        mock_notifiers["webhook"].assert_called_once()
        webhook_call = mock_notifiers["webhook"].call_args
        payload = webhook_call.kwargs.get("json") or json.loads(
            webhook_call.kwargs.get("data")
        )
        assert "Device Offline Alert" in str(payload)

        # 7. Restore online status
        alert_manager.db.execute(
            """
            INSERT INTO metrics (host_id, metric_type, value, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (
                "device-001",
                "device_status",
                "online",
                datetime.now().isoformat(),
            ),
        )

        # 8. Resolve alert
        alert_manager.evaluate_rules()
        resolved = alert_manager.get_alert(alerts[0].id)
        assert resolved.status == "resolved"


class TestAlertMuting:
    """Test alert muting functionality."""

    def test_muted_alerts_no_notification(self, alert_manager, mock_notifiers):
        """Verify muted alerts don't send notifications."""
        # 1. Create channel and rule
        channel = alert_manager.create_channel(
            NotificationChannel(
                id="test_email",
                name="Test Email",
                channel_type="email",
                config={
                    "smtp_host": "smtp.test.com",
                    "smtp_port": 587,
                    "smtp_user": "test@test.com",
                    "smtp_password": "pass",
                    "from_email": "test@test.com",
                    "to_emails": ["admin@test.com"],
                },
                enabled=True,
            )
        )

        rule = alert_manager.create_alert_rule(
            name="Test Rule",
            rule_type="threshold",
            metric_name="test_metric",
            condition=">",
            threshold=50.0,
            notification_channels=[channel.id],
        )

        # 2. Mute the rule
        mute = alert_manager.mute_rule(
            rule.id, duration_minutes=30, reason="Testing mute"
        )
        assert mute.rule_id == rule.id
        assert mute.is_active()

        # 3. Trigger alert
        alert_manager.db.execute(
            """
            INSERT INTO metrics (host_id, metric_type, value, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            ("test-host", "test_metric", 75.0, datetime.now().isoformat()),
        )

        # 4. Evaluate (should trigger but not notify)
        triggered = alert_manager.evaluate_rules()
        assert triggered == 1

        # 5. Verify alert exists but notification was skipped
        alerts = alert_manager.get_active_alerts()
        assert len(alerts) == 1
        mock_notifiers["smtp_instance"].send_message.assert_not_called()

        # 6. Unmute and verify notifications resume
        alert_manager.unmute(mute.id)
        alert_manager.db.execute(
            """
            INSERT INTO metrics (host_id, metric_type, value, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            ("test-host-2", "test_metric", 80.0, datetime.now().isoformat()),
        )

        alert_manager.evaluate_rules()
        mock_notifiers["smtp_instance"].send_message.assert_called()

    def test_host_muting(self, alert_manager, mock_notifiers):
        """Test muting alerts for specific hosts."""
        # Create rule
        channel = alert_manager.create_channel(
            NotificationChannel(
                id="test_channel",
                name="Test Channel",
                channel_type="email",
                config={
                    "smtp_host": "smtp.test.com",
                    "smtp_port": 587,
                    "smtp_user": "test@test.com",
                    "smtp_password": "pass",
                    "from_email": "test@test.com",
                    "to_emails": ["admin@test.com"],
                },
                enabled=True,
            )
        )

        alert_manager.create_alert_rule(
            name="CPU Alert",
            rule_type="threshold",
            metric_name="cpu",
            condition=">",
            threshold=80.0,
            notification_channels=[channel.id],
        )

        # Mute specific host
        alert_manager.mute_host("host-maintenance", reason="Scheduled maintenance")

        # Trigger alerts on both muted and unmuted hosts
        for host in ["host-maintenance", "host-normal"]:
            alert_manager.db.execute(
                """
                INSERT INTO metrics (host_id, metric_type, value, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (host, "cpu", 90.0, datetime.now().isoformat()),
            )

        # Evaluate
        alert_manager.evaluate_rules()

        # Only unmuted host should send notification
        assert mock_notifiers["smtp_instance"].send_message.call_count == 1


class TestCooldownBehavior:
    """Test alert cooldown functionality."""

    def test_cooldown_prevents_duplicate_alerts(self, alert_manager, mock_notifiers):
        """Verify cooldown prevents alert spam."""
        # Create channel and rule with 10-minute cooldown
        channel = alert_manager.create_channel(
            NotificationChannel(
                id="email",
                name="Email",
                channel_type="email",
                config={
                    "smtp_host": "smtp.test.com",
                    "smtp_port": 587,
                    "smtp_user": "test@test.com",
                    "smtp_password": "pass",
                    "from_email": "test@test.com",
                    "to_emails": ["admin@test.com"],
                },
                enabled=True,
            )
        )

        alert_manager.create_alert_rule(
            name="Memory Alert",
            rule_type="threshold",
            metric_name="memory",
            condition=">",
            threshold=90.0,
            cooldown_minutes=10,
            notification_channels=[channel.id],
        )

        # Trigger alert
        alert_manager.db.execute(
            """
            INSERT INTO metrics (host_id, metric_type, value, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            ("host-1", "memory", 95.0, datetime.now().isoformat()),
        )

        alert_manager.evaluate_rules()
        assert mock_notifiers["smtp_instance"].send_message.call_count == 1
        first_alert_id = alert_manager.get_active_alerts()[0].id

        # Try to trigger again immediately (should be blocked by cooldown)
        alert_manager.db.execute(
            """
            INSERT INTO metrics (host_id, metric_type, value, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            ("host-1", "memory", 96.0, datetime.now().isoformat()),
        )

        alert_manager.evaluate_rules()
        # Still only one notification
        assert mock_notifiers["smtp_instance"].send_message.call_count == 1

        # Still only one alert
        alerts = alert_manager.get_active_alerts()
        assert len(alerts) == 1
        assert alerts[0].id == first_alert_id


class TestMultiChannelNotification:
    """Test notifications to multiple channels."""

    def test_multiple_channels_all_notified(self, alert_manager, mock_notifiers):
        """Verify alerts sent to all configured channels."""
        # Create multiple channels
        email_channel = alert_manager.create_channel(
            NotificationChannel(
                id="email",
                name="Email",
                channel_type="email",
                config={
                    "smtp_host": "smtp.test.com",
                    "smtp_port": 587,
                    "smtp_user": "test@test.com",
                    "smtp_password": "pass",
                    "from_email": "test@test.com",
                    "to_emails": ["admin@test.com"],
                },
                enabled=True,
            )
        )

        slack_channel = alert_manager.create_channel(
            NotificationChannel(
                id="slack",
                name="Slack",
                channel_type="webhook",
                config={
                    "webhook_url": "https://hooks.slack.com/test",
                    "webhook_type": "slack",
                },
                enabled=True,
            )
        )

        # Create rule with both channels
        alert_manager.create_alert_rule(
            name="Critical Alert",
            rule_type="threshold",
            metric_name="error_rate",
            condition=">",
            threshold=10.0,
            severity="critical",
            notification_channels=[email_channel.id, slack_channel.id],
        )

        # Trigger alert
        alert_manager.db.execute(
            """
            INSERT INTO metrics (host_id, metric_type, value, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            ("app-server", "error_rate", 25.0, datetime.now().isoformat()),
        )

        alert_manager.evaluate_rules()

        # Both channels should have been notified
        assert mock_notifiers["smtp_instance"].send_message.call_count == 1
        assert mock_notifiers["webhook"].call_count == 1

    def test_severity_filtering(self, alert_manager, mock_notifiers):
        """Test that channels only receive alerts matching severity filter."""
        # Create channel with WARNING minimum severity
        channel = alert_manager.create_channel(
            NotificationChannel(
                id="warning_plus_only",
                name="Warning+ Only",
                channel_type="email",
                config={
                    "smtp_host": "smtp.test.com",
                    "smtp_port": 587,
                    "smtp_user": "test@test.com",
                    "smtp_password": "pass",
                    "from_email": "test@test.com",
                    "to_emails": ["admin@test.com"],
                    "min_severity": "warning",
                },
                enabled=True,
            )
        )

        # Create INFO rule (should not notify)
        alert_manager.create_alert_rule(
            name="Info Alert",
            rule_type="threshold",
            metric_name="requests",
            condition=">",
            threshold=100.0,
            severity="info",
            notification_channels=[channel.id],
        )

        # Create WARNING rule (should notify)
        alert_manager.create_alert_rule(
            name="Warning Alert",
            rule_type="threshold",
            metric_name="latency",
            condition=">",
            threshold=500.0,
            severity="warning",
            notification_channels=[channel.id],
        )

        # Trigger INFO alert
        alert_manager.db.execute(
            """
            INSERT INTO metrics (host_id, metric_type, value, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            ("server-1", "requests", 150.0, datetime.now().isoformat()),
        )
        alert_manager.evaluate_rules()
        assert mock_notifiers["smtp_instance"].send_message.call_count == 0

        # Trigger WARNING alert
        alert_manager.db.execute(
            """
            INSERT INTO metrics (host_id, metric_type, value, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            ("server-1", "latency", 750.0, datetime.now().isoformat()),
        )
        alert_manager.evaluate_rules()
        assert mock_notifiers["smtp_instance"].send_message.call_count == 1


class TestAlertQueries:
    """Test alert query and filtering functionality."""

    def test_alert_filtering_by_status(self, alert_manager):
        """Test filtering alerts by status."""
        # Create multiple alerts with different statuses
        channel = alert_manager.create_channel(
            NotificationChannel(
                id="test",
                name="Test",
                channel_type="email",
                config={
                    "smtp_host": "smtp.test.com",
                    "smtp_port": 587,
                    "smtp_user": "test@test.com",
                    "smtp_password": "pass",
                    "from_email": "test@test.com",
                    "to_emails": ["admin@test.com"],
                },
                enabled=True,
            )
        )

        alert_manager.create_alert_rule(
            name="Test Rule",
            rule_type="threshold",
            metric_name="test",
            condition=">",
            threshold=50.0,
            notification_channels=[channel.id],
        )

        # Create triggered alerts
        for i in range(3):
            alert_manager.db.execute(
                """
                INSERT INTO metrics (host_id, metric_type, value, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (f"host-{i}", "test", 75.0, datetime.now().isoformat()),
            )

        alert_manager.evaluate_rules()
        active = alert_manager.get_active_alerts()
        assert len(active) == 3

        # Acknowledge one
        alert_manager.acknowledge_alert(active[0].id, "admin")

        # Filter by acknowledged
        acknowledged = alert_manager.get_alerts(status="acknowledged")
        assert len(acknowledged) == 1

        # Filter by triggered
        triggered = alert_manager.get_alerts(status="triggered")
        assert len(triggered) == 2

    def test_alert_filtering_by_severity(self, alert_manager):
        """Test filtering alerts by severity."""
        channel = alert_manager.create_channel(
            NotificationChannel(
                id="test",
                name="Test",
                channel_type="email",
                config={
                    "smtp_host": "smtp.test.com",
                    "smtp_port": 587,
                    "smtp_user": "test@test.com",
                    "smtp_password": "pass",
                    "from_email": "test@test.com",
                    "to_emails": ["admin@test.com"],
                },
                enabled=True,
            )
        )

        # Create rules with different severities
        severities = [
            "info",
            "warning",
            "critical",
        ]
        for severity in severities:
            alert_manager.create_alert_rule(
                name=f"{severity} Rule",
                rule_type="threshold",
                metric_name=f"metric_{severity}",
                condition=">",
                threshold=50.0,
                severity=severity,
                notification_channels=[channel.id],
            )

            alert_manager.db.execute(
                """
                INSERT INTO metrics (host_id, metric_type, value, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (
                    "host-1",
                    f"metric_{severity}",
                    75.0,
                    datetime.now().isoformat(),
                ),
            )

        alert_manager.evaluate_rules()

        # Filter by severity
        critical_alerts = alert_manager.get_alerts(severity="critical")
        assert len(critical_alerts) == 1
        assert critical_alerts[0].severity == "critical"


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_channel_config(self, alert_manager):
        """Test that invalid channel configs are rejected."""
        with pytest.raises(ValueError):
            alert_manager.create_channel(
                NotificationChannel(
                    id="bad_email",
                    name="Bad Email",
                    channel_type="email",
                    # Missing required fields
                    config={"smtp_host": "smtp.test.com"},
                    enabled=True,
                )
            )

    def test_disabled_channel_no_notification(self, alert_manager, mock_notifiers):
        """Test that disabled channels don't send notifications."""
        channel = alert_manager.create_channel(
            NotificationChannel(
                id="disabled_channel",
                name="Disabled Channel",
                channel_type="email",
                config={
                    "smtp_host": "smtp.test.com",
                    "smtp_port": 587,
                    "smtp_user": "test@test.com",
                    "smtp_password": "pass",
                    "from_email": "test@test.com",
                    "to_emails": ["admin@test.com"],
                },
                enabled=False,  # Disabled
            )
        )

        alert_manager.create_alert_rule(
            name="Test Rule",
            rule_type="threshold",
            metric_name="test",
            condition=">",
            threshold=50.0,
            notification_channels=[channel.id],
        )

        alert_manager.db.execute(
            """
            INSERT INTO metrics (host_id, metric_type, value, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            ("host-1", "test", 75.0, datetime.now().isoformat()),
        )

        alert_manager.evaluate_rules()
        mock_notifiers["smtp_instance"].send_message.assert_not_called()

    def test_disabled_rule_no_evaluation(self, alert_manager):
        """Test that disabled rules are not evaluated."""
        channel = alert_manager.create_channel(
            NotificationChannel(
                id="channel",
                name="Channel",
                channel_type="email",
                config={
                    "smtp_host": "smtp.test.com",
                    "smtp_port": 587,
                    "smtp_user": "test@test.com",
                    "smtp_password": "pass",
                    "from_email": "test@test.com",
                    "to_emails": ["admin@test.com"],
                },
                enabled=True,
            )
        )

        alert_manager.create_alert_rule(
            name="Disabled Rule",
            rule_type="threshold",
            metric_name="test",
            condition=">",
            threshold=50.0,
            notification_channels=[channel.id],
            enabled=False,
        )

        alert_manager.db.execute(
            """
            INSERT INTO metrics (host_id, metric_type, value, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            ("host-1", "test", 75.0, datetime.now().isoformat()),
        )

        triggered = alert_manager.evaluate_rules()
        assert triggered == 0
        assert len(alert_manager.get_active_alerts()) == 0

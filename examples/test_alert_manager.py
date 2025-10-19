"""
Test the AlertManager - high-level alert system API.

Tests the complete integration of AlertEngine and NotificationManager
through the AlertManager interface.
"""

import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from alerts import AlertManager, AlertRule, NotificationChannel
from alerts.notifiers import EmailNotifier, WebhookNotifier
from database.database import Database
from database.models import Host, Metric
from database.repositories.host_repository import HostRepository
from database.repositories.metric_repository import MetricRepository


def test_alert_manager_initialization():
    """Test AlertManager initialization."""
    print("\n" + "=" * 60)
    print("TEST: AlertManager Initialization")
    print("=" * 60)

    db = Database(":memory:")
    db.initialize()
    db.initialize_alerts()

    manager = AlertManager(db)
    assert manager.db is db, "❌ Database not set"
    assert manager.rule_repo is not None, "❌ Rule repo not initialized"
    assert manager.alert_repo is not None, "❌ Alert repo not initialized"
    assert manager.engine is not None, "❌ Engine not initialized"
    assert manager.notification_manager is not None, "❌ Notif mgr not initialized"
    print("✓ AlertManager initialized successfully")

    manager.close()
    print("✓ All initialization tests passed!\n")


def test_rule_management():
    """Test alert rule CRUD operations through AlertManager."""
    print("=" * 60)
    print("TEST: Rule Management")
    print("=" * 60)

    db = Database(":memory:")
    db.initialize()
    db.initialize_alerts()

    with AlertManager(db) as manager:
        # Create a rule
        rule = AlertRule(
            name="High CPU Alert",
            rule_type="threshold",
            condition="gt",
            severity="warning",
            notification_channels=["email-1"],
            metric_name="cpu_usage",
            threshold=80.0,
            enabled=True,
        )
        created_rule = manager.create_rule(rule)
        assert created_rule.id is not None, "❌ Rule ID not assigned"
        print(f"✓ Created rule: {created_rule.name} (ID: {created_rule.id})")

        # Get rule
        fetched_rule = manager.get_rule(created_rule.id)
        assert fetched_rule is not None, "❌ Rule not found"
        assert fetched_rule.name == rule.name, "❌ Rule name mismatch"
        print("✓ Retrieved rule by ID")

        # List rules
        all_rules = manager.list_rules()
        assert len(all_rules) == 1, "❌ Wrong number of rules"
        print(f"✓ Listed all rules: {len(all_rules)} found")

        # Update rule
        created_rule.threshold = 90.0
        success = manager.update_rule(created_rule)
        assert success, "❌ Rule update failed"
        updated = manager.get_rule(created_rule.id)
        assert updated.threshold == 90.0, "❌ Threshold not updated"
        print("✓ Updated rule threshold")

        # Disable rule
        success = manager.disable_rule(created_rule.id)
        assert success, "❌ Rule disable failed"
        disabled = manager.get_rule(created_rule.id)
        assert not disabled.enabled, "❌ Rule still enabled"
        print("✓ Disabled rule")

        # Enable rule
        success = manager.enable_rule(created_rule.id)
        assert success, "❌ Rule enable failed"
        enabled = manager.get_rule(created_rule.id)
        assert enabled.enabled, "❌ Rule not enabled"
        print("✓ Enabled rule")

        # Delete rule
        success = manager.delete_rule(created_rule.id)
        assert success, "❌ Rule delete failed"
        deleted = manager.get_rule(created_rule.id)
        assert deleted is None, "❌ Rule still exists"
        print("✓ Deleted rule")

    print("✓ All rule management tests passed!\n")


def test_channel_management():
    """Test notification channel management."""
    print("=" * 60)
    print("TEST: Channel Management")
    print("=" * 60)

    db = Database(":memory:")
    db.initialize()
    db.initialize_alerts()

    with AlertManager(db) as manager:
        # Create email channel
        email_channel = NotificationChannel(
            id="email-test",
            channel_type="email",
            name="Test Email",
            enabled=True,
            config={
                "to_emails": ["test@example.com"],
                "min_severity": "warning",
            },
        )
        created = manager.create_channel(email_channel)
        assert created.id == "email-test", "❌ Channel ID mismatch"
        print(f"✓ Created email channel: {created.name}")

        # List channels (includes sample channels from schema)
        all_channels = manager.list_channels()
        assert len(all_channels) >= 1, "❌ No channels found"
        print(f"✓ Listed all channels: {len(all_channels)} found")

        # List by type (includes email_default from schema + our test channel)
        email_channels = manager.list_channels(channel_type="email")
        assert len(email_channels) >= 1, "❌ No email channels found"
        assert any(
            ch.id == "email-test" for ch in email_channels
        ), "❌ Test channel not found"
        print(f"✓ Listed email channels: {len(email_channels)} found")

        # Disable channel
        success = manager.disable_channel("email-test")
        assert success, "❌ Channel disable failed"
        print("✓ Disabled channel")

        # Enable channel
        success = manager.enable_channel("email-test")
        assert success, "❌ Channel enable failed"
        print("✓ Enabled channel")

    print("✓ All channel management tests passed!\n")


def test_notifier_registration():
    """Test notifier registration."""
    print("=" * 60)
    print("TEST: Notifier Registration")
    print("=" * 60)

    db = Database(":memory:")
    db.initialize()
    db.initialize_alerts()

    with AlertManager(db) as manager:
        # Register mock notifiers
        mock_email = Mock()
        manager.register_notifier("email", mock_email)
        print("✓ Registered email notifier")

        mock_webhook = Mock()
        manager.register_notifier("webhook", mock_webhook)
        print("✓ Registered webhook notifier")

        # Verify registration
        assert (
            "email" in manager.notification_manager.notifiers
        ), "❌ Email not registered"
        assert (
            "webhook" in manager.notification_manager.notifiers
        ), "❌ Webhook not registered"
        print("✓ All notifiers registered successfully")

    print("✓ All notifier registration tests passed!\n")


def test_mute_management():
    """Test alert muting operations."""
    print("=" * 60)
    print("TEST: Mute Management")
    print("=" * 60)

    db = Database(":memory:")
    db.initialize()
    db.initialize_alerts()

    with AlertManager(db) as manager:
        # Create a test rule
        rule = AlertRule(
            name="Test Rule",
            rule_type="threshold",
            condition="gt",
            severity="warning",
            notification_channels=[],
            metric_name="test_metric",
            threshold=80.0,
        )
        created_rule = manager.create_rule(rule)
        print(f"✓ Created test rule (ID: {created_rule.id})")

        # Mute the rule
        mute = manager.mute_rule(
            rule_id=created_rule.id,
            muted_by="test_user",
            duration_minutes=60,
            reason="Testing mute functionality",
        )
        assert mute.id is not None, "❌ Mute ID not assigned"
        print(f"✓ Muted rule for 60 minutes")

        # List active mutes
        active_mutes = manager.list_active_mutes()
        assert len(active_mutes) == 1, "❌ Wrong number of active mutes"
        print(f"✓ Listed active mutes: {len(active_mutes)} found")

        # Unmute the rule
        success = manager.unmute_rule(created_rule.id)
        assert success, "❌ Unmute failed"
        print("✓ Unmuted rule")

        # Verify no active mutes
        active_mutes = manager.list_active_mutes()
        assert len(active_mutes) == 0, "❌ Mutes still active"
        print("✓ Verified mute removed")

    print("✓ All mute management tests passed!\n")


def test_alert_queries():
    """Test alert querying operations."""
    print("=" * 60)
    print("TEST: Alert Queries")
    print("=" * 60)

    db = Database(":memory:")
    db.initialize()
    db.initialize_alerts()

    with AlertManager(db) as manager:
        # Create test rule
        rule = AlertRule(
            name="Test Rule",
            rule_type="threshold",
            condition="gt",
            severity="warning",
            notification_channels=[],
            metric_name="test_metric",
            threshold=80.0,
        )
        created_rule = manager.create_rule(rule)

        # Create test alert
        from alerts.models import Alert

        alert = Alert(
            alert_rule_id=created_rule.id,
            severity="warning",
            message="Test alert",
            triggered_at=datetime.now(),
        )
        created_alert = manager.alert_repo.create(alert)
        print(f"✓ Created test alert (ID: {created_alert.id})")

        # Get alert by ID
        fetched = manager.get_alert(created_alert.id)
        assert fetched is not None, "❌ Alert not found"
        print("✓ Retrieved alert by ID")

        # List active alerts
        active = manager.list_active_alerts()
        assert len(active) == 1, "❌ Wrong number of active alerts"
        print(f"✓ Listed active alerts: {len(active)} found")

        # List recent alerts
        recent = manager.list_recent_alerts(hours=24)
        assert len(recent) == 1, "❌ Wrong number of recent alerts"
        print(f"✓ Listed recent alerts: {len(recent)} found")

        # Get statistics
        stats = manager.get_alert_statistics(days=7)
        assert "warning" in stats, "❌ Statistics missing severity"
        print(f"✓ Retrieved alert statistics: {stats}")

        # Acknowledge alert
        success = manager.acknowledge_alert(created_alert.id, "test_user")
        assert success, "❌ Alert acknowledge failed"
        print("✓ Acknowledged alert")

        # Resolve alert
        success = manager.resolve_alert(created_alert.id)
        assert success, "❌ Alert resolve failed"
        print("✓ Resolved alert")

    print("✓ All alert query tests passed!\n")


if __name__ == "__main__":
    try:
        test_alert_manager_initialization()
        test_rule_management()
        test_channel_management()
        test_notifier_registration()
        test_mute_management()
        test_alert_queries()

        print("=" * 60)
        print("✓ ALL ALERT MANAGER TESTS PASSED!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

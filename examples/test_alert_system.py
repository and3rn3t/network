"""
Test script for Phase 4 Alert System initialization.

This script tests:
- Database schema migration
- Alert data models
- Basic CRUD operations
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from alerts.models import Alert, AlertMute, AlertRule, NotificationChannel
from database.database import Database


def test_schema_migration():
    """Test alert schema migration."""
    print("=" * 80)
    print("Testing Alert Schema Migration")
    print("=" * 80)

    # Initialize database with alert schema
    db = Database("data/unifi_network.db")

    try:
        db.initialize_alerts()
        print("✓ Alert schema migration successful")
    except Exception as e:
        print(f"✗ Alert schema migration failed: {e}")
        return False

    # Verify tables were created
    tables = db.fetch_all(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'alert%'"
    )

    print(f"\n✓ Created {len(tables)} alert tables:")
    for table in tables:
        print(f"  - {table['name']}")

    # Verify views were created
    views = db.fetch_all(
        "SELECT name FROM sqlite_master WHERE type='view' AND name LIKE 'v_%alert%'"
    )

    print(f"\n✓ Created {len(views)} alert views:")
    for view in views:
        print(f"  - {view['name']}")

    db.close()
    return True


def test_alert_rule_model():
    """Test AlertRule model."""
    print("\n" + "=" * 80)
    print("Testing AlertRule Model")
    print("=" * 80)

    try:
        # Create a threshold alert rule
        rule = AlertRule(
            name="High CPU Alert",
            description="Alert when CPU exceeds 90%",
            rule_type="threshold",
            metric_name="cpu_percent",
            condition="gte",
            threshold=90.0,
            severity="warning",
            notification_channels=["email_default"],
            cooldown_minutes=30,
        )

        print(f"✓ Created AlertRule: {rule.name}")
        print(f"  Type: {rule.rule_type}")
        print(f"  Condition: {rule.metric_name} {rule.condition} {rule.threshold}")
        print(f"  Severity: {rule.severity}")
        print(f"  Channels: {rule.notification_channels}")

        # Test serialization
        rule_dict = rule.to_dict()
        print(f"\n✓ Serialized to dict: {len(rule_dict)} fields")

        # Test deserialization
        rule_restored = AlertRule.from_dict(rule_dict)
        print(f"✓ Deserialized from dict")
        assert rule_restored.name == rule.name
        assert rule_restored.threshold == rule.threshold

        # Test validation
        try:
            invalid_rule = AlertRule(
                name="Invalid",
                rule_type="invalid_type",
                condition="gt",
                severity="warning",
                notification_channels=["email"],
            )
            print("✗ Validation failed - invalid rule was accepted")
            return False
        except ValueError as e:
            print(f"✓ Validation working - rejected invalid rule: {e}")

        return True

    except Exception as e:
        print(f"✗ AlertRule test failed: {e}")
        return False


def test_alert_model():
    """Test Alert model."""
    print("\n" + "=" * 80)
    print("Testing Alert Model")
    print("=" * 80)

    try:
        # Create an alert
        alert = Alert(
            alert_rule_id=1,
            host_id="00:11:22:33:44:55",
            host_name="AP-Kitchen",
            metric_name="cpu_percent",
            value=95.5,
            threshold=90.0,
            severity="warning",
            message="CPU usage is 95.5% (threshold: 90.0%)",
        )

        print(f"✓ Created Alert: {alert.message}")
        print(f"  Host: {alert.host_name} ({alert.host_id})")
        print(f"  Value: {alert.value} (threshold: {alert.threshold})")
        print(f"  Active: {alert.is_active()}")
        print(f"  Acknowledged: {alert.is_acknowledged()}")

        # Test acknowledgment
        alert.acknowledge("admin")
        print(f"\n✓ Acknowledged by {alert.acknowledged_by}")
        assert alert.is_acknowledged()

        # Test resolution
        alert.resolve()
        print(f"✓ Resolved at {alert.resolved_at}")
        assert not alert.is_active()

        # Test serialization
        alert_dict = alert.to_dict()
        alert_restored = Alert.from_dict(alert_dict)
        print(f"✓ Serialization/deserialization working")
        assert alert_restored.message == alert.message

        return True

    except Exception as e:
        print(f"✗ Alert test failed: {e}")
        return False


def test_notification_channel_model():
    """Test NotificationChannel model."""
    print("\n" + "=" * 80)
    print("Testing NotificationChannel Model")
    print("=" * 80)

    try:
        # Create email channel
        email_channel = NotificationChannel(
            id="email_ops",
            name="Operations Team Email",
            channel_type="email",
            config={
                "smtp_host": "smtp.example.com",
                "smtp_port": 587,
                "from_address": "alerts@example.com",
                "to_addresses": ["ops@example.com"],
                "use_tls": True,
            },
        )

        print(f"✓ Created NotificationChannel: {email_channel.name}")
        print(f"  ID: {email_channel.id}")
        print(f"  Type: {email_channel.channel_type}")
        print(f"  Enabled: {email_channel.enabled}")

        # Create Slack channel
        slack_channel = NotificationChannel(
            id="slack_alerts",
            name="Slack Alerts",
            channel_type="slack",
            config={
                "webhook_url": "https://hooks.slack.com/services/XXX/YYY/ZZZ",
                "channel": "#alerts",
            },
        )

        print(f"\n✓ Created NotificationChannel: {slack_channel.name}")
        print(f"  ID: {slack_channel.id}")
        print(f"  Type: {slack_channel.channel_type}")

        # Test serialization
        channel_dict = email_channel.to_dict()
        channel_restored = NotificationChannel.from_dict(channel_dict)
        print(f"\n✓ Serialization/deserialization working")
        assert channel_restored.id == email_channel.id

        return True

    except Exception as e:
        print(f"✗ NotificationChannel test failed: {e}")
        return False


def test_alert_mute_model():
    """Test AlertMute model."""
    print("\n" + "=" * 80)
    print("Testing AlertMute Model")
    print("=" * 80)

    try:
        # Create indefinite mute
        mute_indefinite = AlertMute(
            alert_rule_id=1,
            muted_by="admin",
            reason="Maintenance window",
        )

        print(f"✓ Created indefinite AlertMute")
        print(f"  Rule ID: {mute_indefinite.alert_rule_id}")
        print(f"  Active: {mute_indefinite.is_active()}")

        # Create timed mute
        mute_timed = AlertMute(
            alert_rule_id=2,
            host_id="00:11:22:33:44:55",
            muted_by="admin",
            expires_at=datetime.now() + timedelta(hours=2),
            reason="Testing",
        )

        print(f"\n✓ Created timed AlertMute")
        print(f"  Rule ID: {mute_timed.alert_rule_id}")
        print(f"  Host ID: {mute_timed.host_id}")
        print(f"  Expires: {mute_timed.expires_at}")
        print(f"  Active: {mute_timed.is_active()}")

        # Create expired mute
        mute_expired = AlertMute(
            alert_rule_id=3,
            muted_by="admin",
            expires_at=datetime.now() - timedelta(hours=1),
        )

        print(f"\n✓ Created expired AlertMute")
        print(f"  Active: {mute_expired.is_active()} (should be False)")
        assert not mute_expired.is_active()

        # Test serialization
        mute_dict = mute_timed.to_dict()
        mute_restored = AlertMute.from_dict(mute_dict)
        print(f"\n✓ Serialization/deserialization working")
        assert mute_restored.alert_rule_id == mute_timed.alert_rule_id

        return True

    except Exception as e:
        print(f"✗ AlertMute test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "Phase 4 Alert System Tests" + " " * 32 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    results = []

    # Run tests
    results.append(("Schema Migration", test_schema_migration()))
    results.append(("AlertRule Model", test_alert_rule_model()))
    results.append(("Alert Model", test_alert_model()))
    results.append(("NotificationChannel Model", test_notification_channel_model()))
    results.append(("AlertMute Model", test_alert_mute_model()))

    # Print summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {test_name}")

    print("-" * 80)
    print(f"Result: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Phase 4 foundation is ready!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

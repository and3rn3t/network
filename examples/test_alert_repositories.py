"""
Test script for alert repositories.

Tests CRUD operations for all alert repositories.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from alerts.models import Alert, AlertMute, AlertRule, NotificationChannel
from database.database import Database
from database.repositories import (
    AlertMuteRepository,
    AlertRepository,
    AlertRuleRepository,
    NotificationChannelRepository,
)


def test_alert_rule_repository():
    """Test AlertRuleRepository operations."""
    print("=" * 80)
    print("Testing AlertRuleRepository")
    print("=" * 80)

    db = Database("data/unifi_network.db")
    repo = AlertRuleRepository(db)

    try:
        # Create a test rule
        rule = AlertRule(
            name="Test High CPU Alert",
            description="Test alert for high CPU usage",
            rule_type="threshold",
            metric_name="cpu_percent",
            condition="gte",
            threshold=90.0,
            severity="warning",
            notification_channels=["email_default"],
            cooldown_minutes=30,
        )

        # Test create
        created_rule = repo.create(rule)
        print(f"✓ Created rule: {created_rule.name} (ID: {created_rule.id})")

        # Test get_by_id
        found_rule = repo.get_by_id(created_rule.id)
        assert found_rule is not None
        assert found_rule.name == rule.name
        print(f"✓ Retrieved rule by ID: {found_rule.id}")

        # Test get_by_name
        found_by_name = repo.get_by_name(rule.name)
        assert found_by_name is not None
        print(f"✓ Retrieved rule by name: {found_by_name.name}")

        # Test get_all
        all_rules = repo.get_all()
        print(f"✓ Retrieved all rules: {len(all_rules)} total")

        # Test get_all_enabled
        enabled_rules = repo.get_all_enabled()
        print(f"✓ Retrieved enabled rules: {len(enabled_rules)} enabled")

        # Test update
        found_rule.threshold = 95.0
        updated = repo.update(found_rule)
        assert updated
        updated_rule = repo.get_by_id(created_rule.id)
        assert updated_rule.threshold == 95.0
        print(f"✓ Updated rule threshold to: {updated_rule.threshold}")

        # Test disable
        disabled = repo.disable(created_rule.id)
        assert disabled
        print(f"✓ Disabled rule ID: {created_rule.id}")

        # Test enable
        enabled = repo.enable(created_rule.id)
        assert enabled
        print(f"✓ Enabled rule ID: {created_rule.id}")

        # Test delete
        deleted = repo.delete(created_rule.id)
        assert deleted
        print(f"✓ Deleted rule ID: {created_rule.id}")

        # Verify deletion
        assert repo.get_by_id(created_rule.id) is None
        print("✓ Verified deletion")

        db.close()
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        db.close()
        return False


def test_alert_repository():
    """Test AlertRepository operations."""
    print("\n" + "=" * 80)
    print("Testing AlertRepository")
    print("=" * 80)

    db = Database("data/unifi_network.db")
    alert_repo = AlertRepository(db)
    rule_repo = AlertRuleRepository(db)

    try:
        # Create a test rule first
        rule = AlertRule(
            name="Test Alert Repo Rule",
            rule_type="threshold",
            metric_name="cpu_percent",
            condition="gte",
            threshold=90.0,
            severity="critical",
            notification_channels=["email_default"],
        )
        created_rule = rule_repo.create(rule)

        # Create a test alert
        alert = Alert(
            alert_rule_id=created_rule.id,
            host_id="00:11:22:33:44:55",
            host_name="Test-AP",
            metric_name="cpu_percent",
            value=95.5,
            threshold=90.0,
            severity="critical",
            message="CPU usage is 95.5% (threshold: 90.0%)",
        )

        # Test create
        created_alert = alert_repo.create(alert)
        print(f"✓ Created alert: ID {created_alert.id}")

        # Test get_by_id
        found_alert = alert_repo.get_by_id(created_alert.id)
        assert found_alert is not None
        print(f"✓ Retrieved alert by ID: {found_alert.id}")

        # Test get_active
        active_alerts = alert_repo.get_active()
        print(f"✓ Retrieved active alerts: {len(active_alerts)} active")

        # Test acknowledge
        acknowledged = alert_repo.acknowledge(created_alert.id, "test_user")
        assert acknowledged
        ack_alert = alert_repo.get_by_id(created_alert.id)
        assert ack_alert.is_acknowledged()
        print(f"✓ Acknowledged alert by: {ack_alert.acknowledged_by}")

        # Test resolve
        resolved = alert_repo.resolve(created_alert.id)
        assert resolved
        resolved_alert = alert_repo.get_by_id(created_alert.id)
        assert not resolved_alert.is_active()
        print(f"✓ Resolved alert at: {resolved_alert.resolved_at}")

        # Test get_alert_counts
        counts = alert_repo.get_alert_counts(hours=24)
        print(f"✓ Alert counts: {counts}")

        # Cleanup
        alert_repo.delete_by_id(created_alert.id)
        rule_repo.delete(created_rule.id)
        print("✓ Cleaned up test data")

        db.close()
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        db.close()
        return False


def test_notification_channel_repository():
    """Test NotificationChannelRepository operations."""
    print("\n" + "=" * 80)
    print("Testing NotificationChannelRepository")
    print("=" * 80)

    db = Database("data/unifi_network.db")
    repo = NotificationChannelRepository(db)

    try:
        # Create a test channel
        channel = NotificationChannel(
            id="test_email_channel",
            name="Test Email Channel",
            channel_type="email",
            config={
                "smtp_host": "smtp.test.com",
                "smtp_port": 587,
                "from_address": "test@example.com",
                "to_addresses": ["admin@example.com"],
            },
        )

        # Test create
        created_channel = repo.create(channel)
        print(f"✓ Created channel: {created_channel.name} ({created_channel.id})")

        # Test get_by_id
        found_channel = repo.get_by_id(created_channel.id)
        assert found_channel is not None
        print(f"✓ Retrieved channel by ID: {found_channel.id}")

        # Test get_all
        all_channels = repo.get_all()
        print(f"✓ Retrieved all channels: {len(all_channels)} total")

        # Test get_all_enabled
        enabled_channels = repo.get_all_enabled()
        print(f"✓ Retrieved enabled channels: {len(enabled_channels)} enabled")

        # Test update
        found_channel.name = "Updated Test Channel"
        updated = repo.update(found_channel)
        assert updated
        updated_channel = repo.get_by_id(created_channel.id)
        assert updated_channel.name == "Updated Test Channel"
        print(f"✓ Updated channel name to: {updated_channel.name}")

        # Test disable
        disabled = repo.disable(created_channel.id)
        assert disabled
        print(f"✓ Disabled channel: {created_channel.id}")

        # Test enable
        enabled = repo.enable(created_channel.id)
        assert enabled
        print(f"✓ Enabled channel: {created_channel.id}")

        # Test delete
        deleted = repo.delete(created_channel.id)
        assert deleted
        print(f"✓ Deleted channel: {created_channel.id}")

        db.close()
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        db.close()
        return False


def test_alert_mute_repository():
    """Test AlertMuteRepository operations."""
    print("\n" + "=" * 80)
    print("Testing AlertMuteRepository")
    print("=" * 80)

    db = Database("data/unifi_network.db")
    mute_repo = AlertMuteRepository(db)
    rule_repo = AlertRuleRepository(db)

    try:
        # Clean up any existing test rule
        existing = rule_repo.get_by_name("Test Mute Rule")
        if existing:
            rule_repo.delete(existing.id)

        # Create a test rule first
        rule = AlertRule(
            name="Test Mute Rule",
            rule_type="threshold",
            metric_name="cpu_percent",
            condition="gte",
            threshold=90.0,
            severity="warning",
            notification_channels=["email_default"],
        )
        created_rule = rule_repo.create(rule)

        # Test mute_rule (indefinite)
        mute1 = mute_repo.mute_rule(
            rule_id=created_rule.id,
            muted_by="test_user",
            reason="Testing indefinite mute",
        )
        print(f"✓ Created indefinite mute: ID {mute1.id}")

        # Test is_muted
        assert mute_repo.is_muted(created_rule.id)
        print(f"✓ Confirmed rule {created_rule.id} is muted")

        # Test get_active
        active_mutes = mute_repo.get_active()
        print(f"✓ Retrieved active mutes: {len(active_mutes)} active")

        # Test unmute_rule
        count = mute_repo.unmute_rule(created_rule.id)
        assert count > 0
        print(f"✓ Unmuted rule (removed {count} mutes)")

        # Test mute_rule (timed)
        mute2 = mute_repo.mute_rule(
            rule_id=created_rule.id,
            muted_by="test_user",
            duration_minutes=60,
            reason="Testing timed mute",
        )
        print(f"✓ Created timed mute: ID {mute2.id}, expires {mute2.expires_at}")

        # Verify muted
        assert mute_repo.is_muted(created_rule.id)
        print("✓ Confirmed timed mute is active")

        # Cleanup
        mute_repo.unmute_rule(created_rule.id)
        rule_repo.delete(created_rule.id)
        print("✓ Cleaned up test data")

        db.close()
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        db.close()
        return False


def main():
    """Run all repository tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 22 + "Alert Repository Tests" + " " * 34 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    results = []

    # Run tests
    results.append(("AlertRuleRepository", test_alert_rule_repository()))
    results.append(("AlertRepository", test_alert_repository()))
    results.append(
        ("NotificationChannelRepository", test_notification_channel_repository())
    )
    results.append(("AlertMuteRepository", test_alert_mute_repository()))

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
        print("\n🎉 All repository tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

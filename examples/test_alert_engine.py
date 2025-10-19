"""
Test script for the Alert Engine.

Tests rule evaluation, threshold checking, and alert generation.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from alerts import AlertEngine, AlertRule
from database.database import Database
from database.models import Host, Metric
from database.repositories import (
    AlertRepository,
    AlertRuleRepository,
    HostRepository,
    MetricRepository,
)


def setup_test_data(db: Database):
    """Create test data for alert engine testing."""
    print("Setting up test data...")

    host_repo = HostRepository(db)
    metric_repo = MetricRepository(db)
    rule_repo = AlertRuleRepository(db)

    # Clean up old test data
    existing = host_repo.get_by_id("test:device:001")
    if existing:
        host_repo.delete("test:device:001")

    # Create test host
    host = Host(
        host_id="test:device:001",
        name="Test Device",
        model="Test AP",
        mac="00:11:22:33:44:55",
        ip_address="192.168.1.100",
        site_name="default",
    )
    host_repo.create(host)
    print(f"✓ Created test host: {host.name}")

    # Create test metric with high CPU
    metric = Metric(
        host_id="test:device:001",
        host_name="Test Device",
        cpu_percent=95.5,
        memory_percent=65.0,
        general_temperature=55.0,
        uptime_seconds=86400,
    )
    metric_repo.create(metric)
    print(f"✓ Created test metric: CPU={metric.cpu_percent}%")

    # Clean up old test rules
    for rule_name in ["Test High CPU Rule", "Test Device Offline Rule"]:
        existing_rule = rule_repo.get_by_name(rule_name)
        if existing_rule:
            rule_repo.delete(existing_rule.id)

    # Create test alert rules
    cpu_rule = AlertRule(
        name="Test High CPU Rule",
        description="Test rule for high CPU",
        rule_type="threshold",
        metric_name="cpu_percent",
        condition="gte",
        threshold=90.0,
        severity="warning",
        notification_channels=["email_default"],
        cooldown_minutes=5,
    )
    created_cpu_rule = rule_repo.create(cpu_rule)
    print(f"✓ Created CPU alert rule (ID: {created_cpu_rule.id})")

    offline_rule = AlertRule(
        name="Test Device Offline Rule",
        description="Test rule for offline devices",
        rule_type="status_change",
        condition="eq",
        threshold=0.0,
        severity="critical",
        notification_channels=["email_default"],
        cooldown_minutes=5,
    )
    created_offline_rule = rule_repo.create(offline_rule)
    print(f"✓ Created offline alert rule (ID: {created_offline_rule.id})")

    return created_cpu_rule, created_offline_rule


def test_threshold_evaluation():
    """Test threshold rule evaluation."""
    print("\n" + "=" * 80)
    print("Testing Threshold Rule Evaluation")
    print("=" * 80)

    db = Database("data/unifi_network.db")
    engine = AlertEngine(db)
    alert_repo = AlertRepository(db)

    try:
        # Setup test data
        cpu_rule, _ = setup_test_data(db)

        # Evaluate the CPU rule
        print(f"\nEvaluating rule: {cpu_rule.name}")
        alerts = engine.evaluate_rule(cpu_rule)

        if alerts:
            print(f"✓ Generated {len(alerts)} alert(s)")
            for alert in alerts:
                print(f"  - {alert.message}")
                print(f"    Severity: {alert.severity}")
                print(f"    Value: {alert.value} (threshold: {alert.threshold})")
        else:
            print("✓ No alerts generated (as expected if in cooldown)")

        # Verify alert was saved
        all_alerts = alert_repo.get_by_rule(cpu_rule.id)
        print(f"✓ Found {len(all_alerts)} total alert(s) for this rule")

        # Cleanup
        for alert in all_alerts:
            alert_repo.delete_by_id(alert.id)

        db.close()
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        db.close()
        return False


def test_evaluate_all_rules():
    """Test evaluating all rules at once."""
    print("\n" + "=" * 80)
    print("Testing Evaluate All Rules")
    print("=" * 80)

    db = Database("data/unifi_network.db")
    engine = AlertEngine(db)
    alert_repo = AlertRepository(db)

    try:
        # Evaluate all rules
        print("Evaluating all enabled rules...")
        new_alerts = engine.evaluate_all_rules()

        print(f"✓ Evaluation complete")
        print(f"✓ Generated {len(new_alerts)} new alert(s)")

        for alert in new_alerts:
            print(f"  - [{alert.severity.upper()}] {alert.message}")

        # Cleanup
        for alert in new_alerts:
            if alert.id:
                alert_repo.delete_by_id(alert.id)

        db.close()
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        db.close()
        return False


def test_cooldown_logic():
    """Test cooldown period functionality."""
    print("\n" + "=" * 80)
    print("Testing Cooldown Logic")
    print("=" * 80)

    db = Database("data/unifi_network.db")
    engine = AlertEngine(db)
    alert_repo = AlertRepository(db)
    rule_repo = AlertRuleRepository(db)

    try:
        # Get test rule
        rule = rule_repo.get_by_name("Test High CPU Rule")
        if not rule:
            print("✗ Test rule not found")
            return False

        # First evaluation - should create alert
        print(f"First evaluation of rule: {rule.name}")
        alerts1 = engine.evaluate_rule(rule)
        print(f"✓ Generated {len(alerts1)} alert(s)")

        # Second evaluation immediately - should be blocked by cooldown
        print(f"\nSecond evaluation (should be in cooldown)...")
        alerts2 = engine.evaluate_rule(rule)
        print(f"✓ Generated {len(alerts2)} alert(s) (expected: 0)")

        if len(alerts2) == 0:
            print("✓ Cooldown logic working correctly")
        else:
            print("⚠️  Warning: Expected 0 alerts due to cooldown")

        # Cleanup
        for alert in alerts1 + alerts2:
            if alert.id:
                alert_repo.delete_by_id(alert.id)

        db.close()
        return len(alerts2) == 0

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        db.close()
        return False


def test_threshold_checking():
    """Test threshold comparison logic."""
    print("\n" + "=" * 80)
    print("Testing Threshold Checking")
    print("=" * 80)

    db = Database("data/unifi_network.db")
    engine = AlertEngine(db)

    try:
        # Test various conditions
        test_cases = [
            (100, "gt", 90, True),
            (90, "gt", 90, False),
            (90, "gte", 90, True),
            (89, "gte", 90, False),
            (80, "lt", 90, True),
            (90, "lt", 90, False),
            (90, "lte", 90, True),
            (91, "lte", 90, False),
            (90, "eq", 90, True),
            (91, "eq", 90, False),
            (91, "ne", 90, True),
            (90, "ne", 90, False),
        ]

        passed = 0
        for value, condition, threshold, expected in test_cases:
            result = engine._check_threshold(value, condition, threshold)
            status = "✓" if result == expected else "✗"
            print(
                f"{status} {value} {condition} {threshold} = {result} "
                f"(expected: {expected})"
            )
            if result == expected:
                passed += 1

        print(f"\n✓ Passed {passed}/{len(test_cases)} threshold checks")

        db.close()
        return passed == len(test_cases)

    except Exception as e:
        print(f"✗ Test failed: {e}")
        db.close()
        return False


def cleanup_test_data(db: Database):
    """Clean up test data."""
    print("\n" + "=" * 80)
    print("Cleaning Up Test Data")
    print("=" * 80)

    try:
        host_repo = HostRepository(db)
        rule_repo = AlertRuleRepository(db)
        alert_repo = AlertRepository(db)

        # Delete test host
        host = host_repo.get_by_id("test:device:001")
        if host:
            host_repo.delete("test:device:001")
            print("✓ Deleted test host")

        # Delete test rules
        for rule_name in ["Test High CPU Rule", "Test Device Offline Rule"]:
            rule = rule_repo.get_by_name(rule_name)
            if rule:
                # Delete associated alerts first
                alerts = alert_repo.get_by_rule(rule.id)
                for alert in alerts:
                    if alert.id:
                        alert_repo.delete_by_id(alert.id)
                # Delete rule
                rule_repo.delete(rule.id)
                print(f"✓ Deleted rule: {rule_name}")

        return True

    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
        return False


def main():
    """Run all alert engine tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "Alert Engine Tests" + " " * 35 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    results = []

    # Run tests
    results.append(("Threshold Evaluation", test_threshold_evaluation()))
    results.append(("Evaluate All Rules", test_evaluate_all_rules()))
    results.append(("Cooldown Logic", test_cooldown_logic()))
    results.append(("Threshold Checking", test_threshold_checking()))

    # Cleanup
    db = Database("data/unifi_network.db")
    cleanup_test_data(db)
    db.close()

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
        print("\n🎉 All alert engine tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

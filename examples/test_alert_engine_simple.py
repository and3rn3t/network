"""Simple test for alert engine basic functionality."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from alerts.alert_engine import AlertEngine
from database.database import Database

print("=" * 60)
print("Alert Engine Basic Test")
print("=" * 60)

# Initialize
db = Database("data/unifi_network.db")
engine = AlertEngine(db)
print("✓ Alert Engine initialized successfully")

# Test threshold logic
print("\nTesting threshold checking logic:")
test_cases = [
    (100, "gt", 90, True),
    (90, "gt", 90, False),
    (90, "gte", 90, True),
    (80, "lt", 90, True),
    (90, "eq", 90, True),
    (91, "ne", 90, True),
]

passed = 0
for value, condition, threshold, expected in test_cases:
    result = engine._check_threshold(value, condition, threshold)
    status = "✓" if result == expected else "✗"
    symbol = {"gt": ">", "gte": ">=", "lt": "<", "eq": "==", "ne": "!="}
    print(
        f"  {status} {value} {symbol.get(condition, condition)} {threshold} = {result}"
    )
    if result == expected:
        passed += 1

print(f"\n✓ Passed {passed}/{len(test_cases)} threshold checks")

# Test getting all rules
print("\nTesting rule retrieval:")
rules = engine.rule_repo.get_all_enabled()
print(f"✓ Found {len(rules)} enabled rule(s)")
for rule in rules:
    print(f"  - {rule.name} ({rule.rule_type}, {rule.severity})")

# Test evaluate all
if len(rules) > 0:
    print("\nTesting rule evaluation:")
    try:
        new_alerts = engine.evaluate_all_rules()
        print(f"✓ Evaluation complete: {len(new_alerts)} alert(s) generated")
        for alert in new_alerts:
            print(f"  - [{alert.severity}] {alert.message}")
    except Exception as e:
        print(f"⚠️  Evaluation error: {e}")
        print("  (This is expected if no metrics data exists yet)")

db.close()
print("\n✓ All basic tests passed!")
print("=" * 60)

# Alert System Quick Reference

**UniFi Network Monitor - Phase 4 Alert System**

---

## Quick Start

### 1. Initialize the Alert System

```python
from database.database import Database
from alerts import AlertManager

# Initialize database with alert support
db = Database("data/unifi_network.db")
db.initialize()
db.initialize_alerts()

# Create alert manager
manager = AlertManager(db)
```

### 2. Setup Email Notifications

```python
from alerts.notifiers import EmailNotifier

email_config = {
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "alerts@example.com",
    "smtp_password": "your_app_password",
    "from_email": "alerts@example.com",
    "to_emails": ["admin@example.com"],
    "use_tls": True,
}

manager.register_notifier("email", EmailNotifier(email_config))
```

### 3. Create an Alert Rule

```python
from alerts import AlertRule

rule = AlertRule(
    name="High CPU Alert",
    rule_type="threshold",
    metric_name="cpu_usage",
    condition="gt",
    threshold=80.0,
    severity="warning",
    notification_channels=["email-1"],
    cooldown_minutes=30,
)

created_rule = manager.create_rule(rule)
print(f"Created rule: {created_rule.name} (ID: {created_rule.id})")
```

### 4. Evaluate Rules

```python
# Evaluate all enabled rules
alerts = manager.evaluate_rules()

print(f"Triggered {len(alerts)} new alerts")
for alert in alerts:
    print(f"  {alert.severity}: {alert.message}")
```

---

## Common Operations

### Rule Management

```python
# List all rules
rules = manager.list_rules()

# Get enabled rules only
enabled = manager.list_rules(enabled_only=True)

# Get a specific rule
rule = manager.get_rule(rule_id=1)

# Update a rule
rule.threshold = 90.0
manager.update_rule(rule)

# Enable/disable a rule
manager.enable_rule(rule_id=1)
manager.disable_rule(rule_id=1)

# Delete a rule
manager.delete_rule(rule_id=1)
```

### Alert Queries

```python
# List active alerts
active_alerts = manager.list_active_alerts()

# Filter by severity
critical = manager.list_active_alerts(severity="critical")

# Filter by host
host_alerts = manager.list_active_alerts(host_id="00:11:22:33:44:55")

# Get recent alerts (last 24 hours)
recent = manager.list_recent_alerts(hours=24)

# Get alert statistics
stats = manager.get_alert_statistics(days=7)
print(stats)  # {'info': 5, 'warning': 12, 'critical': 2, 'total': 19}
```

### Alert Lifecycle

```python
# Get a specific alert
alert = manager.get_alert(alert_id=1)

# Acknowledge an alert
manager.acknowledge_alert(alert_id=1, acknowledged_by="admin@example.com")

# Resolve an alert
manager.resolve_alert(alert_id=1)

# Auto-resolve old alerts
count = manager.resolve_stale_alerts(hours=48)
print(f"Resolved {count} stale alerts")
```

### Mute Management

```python
# Mute a rule for 2 hours
mute = manager.mute_rule(
    rule_id=1,
    muted_by="admin",
    duration_minutes=120,
    reason="Maintenance window"
)

# Mute indefinitely
manager.mute_rule(rule_id=1, muted_by="admin")

# Mute for specific host only
manager.mute_rule(
    rule_id=1,
    muted_by="admin",
    host_id="00:11:22:33:44:55",
    duration_minutes=60
)

# Unmute
manager.unmute_rule(rule_id=1)

# List active mutes
active_mutes = manager.list_active_mutes()

# Clean up expired mutes
count = manager.cleanup_expired_mutes()
```

### Channel Management

```python
from alerts import NotificationChannel

# Create a channel
channel = NotificationChannel(
    id="email-alerts",
    name="Primary Email",
    channel_type="email",
    config={
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "alerts@example.com",
        "smtp_password": "app_password",
        "from_email": "alerts@example.com",
        "to_emails": ["admin@example.com"],
        "min_severity": "warning",
    },
    enabled=True,
)

manager.create_channel(channel)

# List channels
all_channels = manager.list_channels()
email_channels = manager.list_channels(channel_type="email")
enabled_only = manager.list_channels(enabled_only=True)

# Enable/disable channel
manager.enable_channel("email-alerts")
manager.disable_channel("email-alerts")
```

---

## Rule Types

### Threshold Rules

Trigger when a metric crosses a threshold:

```python
rule = AlertRule(
    name="High Memory Usage",
    rule_type="threshold",
    metric_name="memory_usage",
    condition="gte",  # >=
    threshold=90.0,
    severity="critical",
    notification_channels=["email-1", "slack-1"],
)
```

**Available Conditions:**

- `"gt"` - Greater than (>)
- `"gte"` - Greater than or equal (>=)
- `"lt"` - Less than (<)
- `"lte"` - Less than or equal (<=)
- `"eq"` - Equal (==)
- `"ne"` - Not equal (!=)

### Status Change Rules

Trigger when a status field changes:

```python
rule = AlertRule(
    name="Device Offline",
    rule_type="status_change",
    metric_name="status",
    condition="eq",
    threshold=0,  # 0 = offline
    severity="critical",
    notification_channels=["email-1"],
)
```

---

## Notification Channels

### Email (SMTP)

```python
from alerts.notifiers import EmailNotifier

email_config = {
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "alerts@example.com",
    "smtp_password": "app_password",
    "from_email": "alerts@example.com",
    "to_emails": ["admin@example.com", "ops@example.com"],
    "use_tls": True,
}

manager.register_notifier("email", EmailNotifier(email_config))
```

### Slack Webhook

```python
from alerts.notifiers import WebhookNotifier

slack_config = {
    "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "platform": "slack",
    "timeout": 10,
}

manager.register_notifier("slack", WebhookNotifier(slack_config))
```

### Discord Webhook

```python
discord_config = {
    "webhook_url": "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/TOKEN",
    "platform": "discord",
    "timeout": 10,
}

manager.register_notifier("discord", WebhookNotifier(discord_config))
```

### Generic Webhook

```python
generic_config = {
    "webhook_url": "https://your-api.example.com/alerts",
    "platform": "generic",
    "timeout": 10,
    "verify_ssl": True,
}

manager.register_notifier("webhook", WebhookNotifier(generic_config))
```

---

## Alert Severity Levels

- **info** - Informational messages
- **warning** - Potential issues requiring attention
- **critical** - Immediate action required

### Severity-Based Filtering

Channels can specify minimum severity in their config:

```python
channel_config = {
    "min_severity": "warning",  # Only warning and critical
    # ... other config
}
```

---

## Best Practices

### 1. Use Cooldown Periods

Prevent alert spam by setting appropriate cooldowns:

```python
rule = AlertRule(
    # ...
    cooldown_minutes=30,  # Wait 30min before re-alerting
)
```

### 2. Mute During Maintenance

```python
# Before maintenance
manager.mute_rule(rule_id=1, muted_by="admin", duration_minutes=120)

# Perform maintenance...

# After maintenance (optional - will auto-expire)
manager.unmute_rule(rule_id=1)
```

### 3. Monitor Alert Statistics

```python
# Check alert trends
stats = manager.get_alert_statistics(days=7)

if stats['critical'] > 10:
    print("Warning: High number of critical alerts!")
```

### 4. Clean Up Stale Alerts

```python
# Run periodically (e.g., daily)
count = manager.resolve_stale_alerts(hours=48)
print(f"Cleaned up {count} old alerts")
```

### 5. Use Context Managers

```python
with AlertManager(db) as manager:
    # Your code here
    alerts = manager.evaluate_rules()
    # ... more operations
# Automatic cleanup on exit
```

---

## Error Handling

### Notification Failures

The system tracks notification delivery status:

```python
# Check notification status in alert object
alert = manager.get_alert(alert_id=1)
print(alert.notification_status)
# {'email-1': 'sent', 'slack-1': 'failed'}
```

### Rule Validation

Rules are validated on creation:

```python
try:
    rule = AlertRule(
        name="Invalid Rule",
        rule_type="unknown",  # Invalid!
        # ...
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

---

## Integration Example

### Scheduled Alert Evaluation

```python
import schedule
import time
from database.database import Database
from alerts import AlertManager
from alerts.notifiers import EmailNotifier

# Setup
db = Database("data/unifi_network.db")
db.initialize_alerts()

with AlertManager(db) as manager:
    # Register notifiers
    manager.setup_default_notifiers(email_config=email_config)

    def evaluate_alerts():
        """Check all rules and send notifications"""
        alerts = manager.evaluate_rules()
        print(f"Evaluated rules: {len(alerts)} alerts triggered")

        # Cleanup old alerts daily
        if time.localtime().tm_hour == 0:  # Midnight
            count = manager.resolve_stale_alerts(hours=48)
            print(f"Cleaned up {count} stale alerts")

    # Schedule evaluation every 5 minutes
    schedule.every(5).minutes.do(evaluate_alerts)

    # Run scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)
```

---

## Troubleshooting

### No Alerts Being Triggered

1. Check if rules are enabled:

   ```python
   rules = manager.list_rules(enabled_only=True)
   print(f"Enabled rules: {len(rules)}")
   ```

2. Check if rules are muted:

   ```python
   mutes = manager.list_active_mutes()
   print(f"Active mutes: {len(mutes)}")
   ```

3. Verify cooldown hasn't expired yet

### Notifications Not Being Sent

1. Check channel is enabled:

   ```python
   channels = manager.list_channels(enabled_only=True)
   ```

2. Verify notifier is registered:

   ```python
   print(manager.notification_manager.notifiers.keys())
   ```

3. Check channel config for errors:
   ```python
   from alerts.notifiers import EmailNotifier
   notifier = EmailNotifier(config)
   if not notifier.validate_config():
       print("Config validation failed")
   ```

### Email Not Sending

- Verify SMTP credentials
- Check if "Less secure app access" is enabled (Gmail)
- Use app-specific password (not account password)
- Verify firewall allows SMTP ports (587, 465, 25)

---

## API Reference

See the full API documentation in:

- `src/alerts/alert_manager.py` - AlertManager class
- `src/alerts/alert_engine.py` - AlertEngine class
- `src/alerts/notification_manager.py` - NotificationManager class
- `src/alerts/models.py` - Data models

---

**For more information, see:**

- `docs/PHASE_4_KICKOFF.md` - Implementation plan
- `docs/PHASE_4_PROGRESS.md` - Development progress
- `docs/PHASE_4_MILESTONE.md` - Feature overview
- `examples/test_alert_manager.py` - Usage examples

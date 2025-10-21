# Phase 4: Alerting & Notifications - Kickoff

**Start Date:** October 18, 2025
**Status:** 🚀 In Progress
**Priority:** Medium
**Estimated Effort:** 18-28 hours

---

## Executive Summary

Phase 4 focuses on building a comprehensive alerting and notification system to enable proactive monitoring of the UniFi network. The system will detect critical events, evaluate alert rules, and deliver notifications through multiple channels.

### Key Objectives

1. ✅ Build intelligent alert engine with rule-based conditions
2. ✅ Implement multi-channel notification system (email, webhooks)
3. ✅ Create alert management features (mute, snooze, acknowledge)
4. ✅ Enable automated monitoring without manual intervention

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Alert System Architecture                 │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Metrics &  │───────▶│    Alert     │────────▶│ Notification │
│    Events    │         │    Engine    │         │   Manager    │
└──────────────┘         └──────────────┘         └──────────────┘
                                │                         │
                                ▼                         ▼
                         ┌──────────────┐         ┌──────────────┐
                         │ Alert Rules  │         │   Channels   │
                         │  (Database)  │         │   (Plugins)  │
                         └──────────────┘         └──────────────┘
                                                          │
                                    ┌─────────────────────┼─────────────────────┐
                                    ▼                     ▼                     ▼
                            ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
                            │    Email     │     │   Webhook    │     │   SMS/Other  │
                            │   Notifier   │     │   Notifier   │     │  (Optional)  │
                            └──────────────┘     └──────────────┘     └──────────────┘
```

---

## Components to Build

### 1. Database Schema

**File:** `src/database/schema_alerts.sql` (new migration)

**Tables:**

```sql
-- Alert rule definitions
CREATE TABLE alert_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    rule_type TEXT NOT NULL,  -- 'threshold', 'status_change', 'custom'
    metric_name TEXT,
    host_id TEXT,  -- NULL for network-wide rules
    condition TEXT NOT NULL,  -- 'gt', 'lt', 'eq', 'ne', 'gte', 'lte'
    threshold REAL,
    severity TEXT NOT NULL,  -- 'info', 'warning', 'critical'
    enabled INTEGER NOT NULL DEFAULT 1,
    notification_channels TEXT,  -- JSON array of channel IDs
    cooldown_minutes INTEGER DEFAULT 60,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Alert history
CREATE TABLE alert_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_rule_id INTEGER NOT NULL,
    host_id TEXT,
    host_name TEXT,
    metric_name TEXT,
    value REAL,
    threshold REAL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    triggered_at TEXT NOT NULL,
    acknowledged_at TEXT,
    acknowledged_by TEXT,
    resolved_at TEXT,
    notification_status TEXT,  -- JSON: {channel: status}
    FOREIGN KEY (alert_rule_id) REFERENCES alert_rules(id)
);

-- Notification channels configuration
CREATE TABLE notification_channels (
    id TEXT PRIMARY KEY,  -- e.g., 'email_primary', 'slack_ops'
    name TEXT NOT NULL,
    channel_type TEXT NOT NULL,  -- 'email', 'slack', 'discord', 'webhook'
    config TEXT NOT NULL,  -- JSON configuration
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Alert mute/snooze tracking
CREATE TABLE alert_mutes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_rule_id INTEGER NOT NULL,
    host_id TEXT,  -- NULL for all hosts
    muted_by TEXT NOT NULL,
    muted_at TEXT NOT NULL,
    expires_at TEXT,  -- NULL for indefinite
    reason TEXT,
    FOREIGN KEY (alert_rule_id) REFERENCES alert_rules(id)
);
```

**Indexes:**

```sql
CREATE INDEX idx_alert_history_rule ON alert_history(alert_rule_id);
CREATE INDEX idx_alert_history_triggered ON alert_history(triggered_at);
CREATE INDEX idx_alert_history_host ON alert_history(host_id);
CREATE INDEX idx_alert_mutes_expires ON alert_mutes(expires_at);
CREATE INDEX idx_alert_rules_enabled ON alert_rules(enabled);
```

---

### 2. Data Models

**File:** `src/alerts/models.py`

**Models:**

```python
@dataclass
class AlertRule:
    """Alert rule definition"""
    id: Optional[int]
    name: str
    description: Optional[str]
    rule_type: str  # 'threshold', 'status_change', 'custom'
    metric_name: Optional[str]
    host_id: Optional[str]
    condition: str
    threshold: Optional[float]
    severity: str
    enabled: bool
    notification_channels: List[str]
    cooldown_minutes: int
    created_at: datetime
    updated_at: datetime

@dataclass
class Alert:
    """Alert instance (triggered rule)"""
    id: Optional[int]
    alert_rule_id: int
    host_id: Optional[str]
    host_name: Optional[str]
    metric_name: Optional[str]
    value: Optional[float]
    threshold: Optional[float]
    severity: str
    message: str
    triggered_at: datetime
    acknowledged_at: Optional[datetime]
    acknowledged_by: Optional[str]
    resolved_at: Optional[datetime]
    notification_status: Dict[str, str]

@dataclass
class NotificationChannel:
    """Notification channel configuration"""
    id: str
    name: str
    channel_type: str
    config: Dict[str, Any]
    enabled: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class AlertMute:
    """Alert mute/snooze configuration"""
    id: Optional[int]
    alert_rule_id: int
    host_id: Optional[str]
    muted_by: str
    muted_at: datetime
    expires_at: Optional[datetime]
    reason: Optional[str]
```

---

### 3. Alert Engine

**File:** `src/alerts/alert_engine.py`

**Core Responsibilities:**

- Evaluate alert rules against current metrics/events
- Detect threshold breaches
- Detect status changes
- Generate alerts with proper severity
- Respect cooldown periods
- Check mute/snooze status
- Trigger notifications

**Key Methods:**

```python
class AlertEngine:
    def evaluate_rules(self) -> List[Alert]
    def evaluate_threshold_rule(self, rule: AlertRule) -> Optional[Alert]
    def evaluate_status_change_rule(self, rule: AlertRule) -> Optional[Alert]
    def check_cooldown(self, rule: AlertRule, host_id: str) -> bool
    def is_muted(self, rule: AlertRule, host_id: str) -> bool
    def create_alert(self, rule: AlertRule, ...) -> Alert
    def resolve_alert(self, alert: Alert) -> None
```

---

### 4. Notification System

**File:** `src/alerts/notification_manager.py`

**Core Responsibilities:**

- Manage notification channels
- Route alerts to appropriate channels
- Handle notification failures and retries
- Track notification delivery status

**Key Methods:**

```python
class NotificationManager:
    def send_alert(self, alert: Alert, channels: List[str]) -> Dict[str, str]
    def register_channel(self, channel: NotificationChannel) -> None
    def get_notifier(self, channel_type: str) -> BaseNotifier
```

---

### 5. Notification Channels

**Files:**

- `src/alerts/notifiers/base.py` - Abstract base class
- `src/alerts/notifiers/email.py` - Email notifier
- `src/alerts/notifiers/webhook.py` - Webhook notifier (Slack, Discord, generic)

**Email Notifier:**

```python
class EmailNotifier(BaseNotifier):
    def send(self, alert: Alert, config: Dict) -> bool
    def render_template(self, alert: Alert) -> str
```

**Webhook Notifier:**

```python
class WebhookNotifier(BaseNotifier):
    def send(self, alert: Alert, config: Dict) -> bool
    def format_slack_message(self, alert: Alert) -> Dict
    def format_discord_message(self, alert: Alert) -> Dict
```

---

### 6. Alert Management

**File:** `src/alerts/alert_manager.py`

**Core Responsibilities:**

- Acknowledge alerts
- Mute/snooze alert rules
- Resolve alerts manually
- Query alert history

**Key Methods:**

```python
class AlertManager:
    def acknowledge_alert(self, alert_id: int, user: str) -> None
    def mute_rule(self, rule_id: int, duration_minutes: int, reason: str) -> None
    def unmute_rule(self, rule_id: int) -> None
    def resolve_alert(self, alert_id: int) -> None
    def get_active_alerts(self) -> List[Alert]
    def get_alert_history(self, filters: Dict) -> List[Alert]
```

---

### 7. Repositories

**Files:**

- `src/database/repositories/alert_rule_repository.py`
- `src/database/repositories/alert_repository.py`
- `src/database/repositories/notification_channel_repository.py`

**Key Methods:**

```python
class AlertRuleRepository:
    def create(self, rule: AlertRule) -> AlertRule
    def get_all_enabled(self) -> List[AlertRule]
    def get_by_host(self, host_id: str) -> List[AlertRule]
    def update(self, rule: AlertRule) -> None
    def delete(self, rule_id: int) -> None

class AlertRepository:
    def create(self, alert: Alert) -> Alert
    def get_active_by_rule(self, rule_id: int) -> List[Alert]
    def get_recent(self, hours: int) -> List[Alert]
    def acknowledge(self, alert_id: int, user: str) -> None
    def resolve(self, alert_id: int) -> None
```

---

### 8. CLI Tool

**File:** `examples/manage_alerts.py`

**Features:**

```bash
# Rule management
python examples/manage_alerts.py add-rule --name "High CPU" --metric cpu_percent --threshold 90
python examples/manage_alerts.py list-rules
python examples/manage_alerts.py enable-rule <id>
python examples/manage_alerts.py disable-rule <id>

# Channel management
python examples/manage_alerts.py add-channel --type email --name "Ops Team"
python examples/manage_alerts.py test-channel <id>

# Alert management
python examples/manage_alerts.py list-alerts --active
python examples/manage_alerts.py acknowledge <id>
python examples/manage_alerts.py mute <rule_id> --duration 60

# Testing
python examples/manage_alerts.py test-alert --rule <id>
```

---

### 9. Configuration

**File:** `src/alerts/config.py`

**Configuration Options:**

```python
@dataclass
class AlertConfig:
    evaluation_interval: int = 60  # seconds
    default_cooldown: int = 60  # minutes
    max_retries: int = 3
    retry_delay: int = 5  # seconds
    batch_size: int = 100
    enable_auto_resolve: bool = True
    auto_resolve_minutes: int = 60
```

---

## Implementation Plan

### Week 1: Core Infrastructure

**Day 1-2: Database & Models**

- ✅ Create schema migration for alert tables
- ✅ Implement alert data models
- ✅ Create repositories for alerts, rules, channels
- ✅ Write unit tests for models and repositories

**Day 3-4: Alert Engine**

- ✅ Implement AlertEngine class
- ✅ Build threshold evaluation logic
- ✅ Build status change detection
- ✅ Implement cooldown and mute checking
- ✅ Write comprehensive tests

### Week 2: Notifications & Management

**Day 5-6: Notification System**

- ✅ Build NotificationManager
- ✅ Implement EmailNotifier with HTML templates
- ✅ Implement WebhookNotifier (Slack, Discord)
- ✅ Test notification delivery

**Day 7: Alert Management**

- ✅ Implement AlertManager
- ✅ Build acknowledge/mute/resolve features
- ✅ Create CLI tool for management

### Week 3: Testing & Documentation

**Day 8-9: Testing**

- ✅ Integration tests for full alert flow
- ✅ Test all notification channels
- ✅ Load testing with multiple rules
- ✅ Edge case testing

**Day 10: Documentation & Examples**

- ✅ Write ALERTING.md guide
- ✅ Create example alert configurations
- ✅ Update main documentation
- ✅ Create Phase 4 completion report

---

## Success Criteria

### Functional Requirements

- ✅ Alert rules can be created, updated, deleted
- ✅ Alert engine evaluates rules every minute
- ✅ Alerts trigger notifications within 30 seconds
- ✅ Email notifications are delivered successfully
- ✅ Webhook notifications work with Slack/Discord
- ✅ Alerts can be acknowledged and resolved
- ✅ Rules can be muted/snoozed temporarily
- ✅ Cooldown periods prevent alert spam

### Performance Requirements

- ✅ Rule evaluation completes in <5 seconds for 100 rules
- ✅ Notification delivery in <10 seconds
- ✅ No missed alerts during evaluation
- ✅ Minimal CPU/memory overhead

### Quality Requirements

- ✅ 70%+ test coverage
- ✅ Type hints on all functions
- ✅ Comprehensive documentation
- ✅ Error handling for all failure scenarios
- ✅ Logging for debugging and audit trail

---

## Common Alert Rule Examples

### Device Offline

```python
AlertRule(
    name="Device Offline",
    rule_type="status_change",
    condition="eq",
    threshold=0,  # status = offline
    severity="critical",
    notification_channels=["email_primary", "slack_ops"]
)
```

### High CPU Usage

```python
AlertRule(
    name="High CPU Usage",
    rule_type="threshold",
    metric_name="cpu_percent",
    condition="gte",
    threshold=90.0,
    severity="warning",
    cooldown_minutes=30
)
```

### High Temperature

```python
AlertRule(
    name="High Temperature",
    rule_type="threshold",
    metric_name="general_temperature",
    condition="gte",
    threshold=75.0,
    severity="critical",
    cooldown_minutes=15
)
```

### Low Memory

```python
AlertRule(
    name="Low Memory",
    rule_type="threshold",
    metric_name="memory_percent",
    condition="gte",
    threshold=85.0,
    severity="warning"
)
```

---

## Technical Considerations

### Alert Deduplication

- Use cooldown periods to prevent spam
- Track last alert time per rule + host
- Configurable cooldown per rule
- Auto-resolve old alerts

### Notification Reliability

- Retry failed notifications (max 3 attempts)
- Exponential backoff for retries
- Log all delivery attempts
- Track notification status in database

### Performance

- Batch rule evaluation
- Index all query columns
- Cache active rules in memory
- Parallel notification delivery

### Security

- Never log notification credentials
- Secure storage of API tokens
- Validate all webhook URLs
- Rate limit notification attempts

---

## Dependencies

### New Dependencies

```
# Phase 4 dependencies
APScheduler>=3.10.4  # Task scheduling (optional, for daemon mode)
jinja2>=3.1.2        # Email templates
```

### Optional Dependencies

```
twilio>=8.10.0       # SMS notifications (Phase 4 extension)
```

---

## Next Steps

1. **Create database schema migration**
2. **Implement data models**
3. **Build alert engine core**
4. **Implement email notifier**
5. **Create CLI management tool**

---

**Created:** October 18, 2025
**Next Review:** Weekly progress checks
**Completion Target:** ~3 weeks

Let's build an intelligent alerting system! 🚨

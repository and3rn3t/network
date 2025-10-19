-- Alert System Schema Migration
-- Phase 4: Alerting & Notifications
-- Version: 1.0.0
-- Date: October 18, 2025
-- ============================================================================
-- TABLE: alert_rules
-- Purpose: Store alert rule definitions
-- ============================================================================
CREATE TABLE IF NOT EXISTS alert_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    rule_type TEXT NOT NULL CHECK(
        rule_type IN ('threshold', 'status_change', 'custom')
    ),
    metric_name TEXT,
    -- Required for threshold rules
    host_id TEXT,
    -- NULL for network-wide rules
    condition TEXT NOT NULL CHECK(
        condition IN ('gt', 'lt', 'eq', 'ne', 'gte', 'lte')
    ),
    threshold REAL,
    -- Required for threshold rules
    severity TEXT NOT NULL CHECK(severity IN ('info', 'warning', 'critical')),
    enabled INTEGER NOT NULL DEFAULT 1 CHECK(enabled IN (0, 1)),
    notification_channels TEXT NOT NULL,
    -- JSON array of channel IDs
    cooldown_minutes INTEGER NOT NULL DEFAULT 60 CHECK(cooldown_minutes >= 0),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
-- ============================================================================
-- TABLE: alert_history
-- Purpose: Store triggered alerts and their lifecycle
-- ============================================================================
CREATE TABLE IF NOT EXISTS alert_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_rule_id INTEGER NOT NULL,
    host_id TEXT,
    host_name TEXT,
    metric_name TEXT,
    value REAL,
    threshold REAL,
    severity TEXT NOT NULL CHECK(severity IN ('info', 'warning', 'critical')),
    message TEXT NOT NULL,
    triggered_at TEXT NOT NULL,
    acknowledged_at TEXT,
    acknowledged_by TEXT,
    resolved_at TEXT,
    notification_status TEXT,
    -- JSON: {channel_id: "sent|failed|pending"}
    FOREIGN KEY (alert_rule_id) REFERENCES alert_rules(id) ON DELETE CASCADE
);
-- ============================================================================
-- TABLE: notification_channels
-- Purpose: Store notification channel configurations
-- ============================================================================
CREATE TABLE IF NOT EXISTS notification_channels (
    id TEXT PRIMARY KEY,
    -- e.g., 'email_primary', 'slack_ops', 'discord_alerts'
    name TEXT NOT NULL,
    channel_type TEXT NOT NULL CHECK(
        channel_type IN ('email', 'slack', 'discord', 'webhook', 'sms')
    ),
    config TEXT NOT NULL,
    -- JSON configuration (SMTP details, webhook URLs, etc.)
    enabled INTEGER NOT NULL DEFAULT 1 CHECK(enabled IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
-- ============================================================================
-- TABLE: alert_mutes
-- Purpose: Track muted/snoozed alerts
-- ============================================================================
CREATE TABLE IF NOT EXISTS alert_mutes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_rule_id INTEGER NOT NULL,
    host_id TEXT,
    -- NULL for all hosts
    muted_by TEXT NOT NULL,
    muted_at TEXT NOT NULL,
    expires_at TEXT,
    -- NULL for indefinite mute
    reason TEXT,
    FOREIGN KEY (alert_rule_id) REFERENCES alert_rules(id) ON DELETE CASCADE
);
-- ============================================================================
-- INDEXES: Optimize common queries
-- ============================================================================
-- Alert rules indexes
CREATE INDEX IF NOT EXISTS idx_alert_rules_enabled ON alert_rules(enabled);
CREATE INDEX IF NOT EXISTS idx_alert_rules_host ON alert_rules(host_id)
WHERE host_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_alert_rules_type ON alert_rules(rule_type, enabled);
-- Alert history indexes
CREATE INDEX IF NOT EXISTS idx_alert_history_rule ON alert_history(alert_rule_id);
CREATE INDEX IF NOT EXISTS idx_alert_history_triggered ON alert_history(triggered_at DESC);
CREATE INDEX IF NOT EXISTS idx_alert_history_host ON alert_history(host_id)
WHERE host_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_alert_history_unresolved ON alert_history(resolved_at)
WHERE resolved_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_alert_history_unacknowledged ON alert_history(acknowledged_at)
WHERE acknowledged_at IS NULL;
-- Alert mutes indexes
CREATE INDEX IF NOT EXISTS idx_alert_mutes_rule ON alert_mutes(alert_rule_id);
CREATE INDEX IF NOT EXISTS idx_alert_mutes_expires ON alert_mutes(expires_at)
WHERE expires_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_alert_mutes_rule_expires ON alert_mutes(alert_rule_id, expires_at);
-- Notification channels indexes
CREATE INDEX IF NOT EXISTS idx_notification_channels_type ON notification_channels(channel_type, enabled);
-- ============================================================================
-- VIEWS: Convenient queries
-- ============================================================================
-- Active alerts view
CREATE VIEW IF NOT EXISTS v_active_alerts AS
SELECT ah.*,
    ar.name as rule_name,
    ar.cooldown_minutes,
    ar.notification_channels
FROM alert_history ah
    JOIN alert_rules ar ON ah.alert_rule_id = ar.id
WHERE ah.resolved_at IS NULL
ORDER BY ah.triggered_at DESC;
-- Recent alerts summary
CREATE VIEW IF NOT EXISTS v_recent_alerts_summary AS
SELECT date(triggered_at) as alert_date,
    severity,
    COUNT(*) as alert_count,
    COUNT(
        CASE
            WHEN acknowledged_at IS NOT NULL THEN 1
        END
    ) as acknowledged_count,
    COUNT(
        CASE
            WHEN resolved_at IS NOT NULL THEN 1
        END
    ) as resolved_count
FROM alert_history
WHERE triggered_at >= datetime('now', '-30 days')
GROUP BY date(triggered_at),
    severity
ORDER BY alert_date DESC,
    severity;
-- Alert rule effectiveness view
CREATE VIEW IF NOT EXISTS v_rule_effectiveness AS
SELECT ar.id,
    ar.name,
    ar.severity,
    ar.enabled,
    COUNT(ah.id) as total_alerts,
    COUNT(
        CASE
            WHEN ah.resolved_at IS NOT NULL THEN 1
        END
    ) as resolved_count,
    COUNT(
        CASE
            WHEN ah.acknowledged_at IS NOT NULL THEN 1
        END
    ) as acknowledged_count,
    MAX(ah.triggered_at) as last_triggered,
    AVG(
        CASE
            WHEN ah.resolved_at IS NOT NULL THEN (
                julianday(ah.resolved_at) - julianday(ah.triggered_at)
            ) * 24 * 60
        END
    ) as avg_resolution_minutes
FROM alert_rules ar
    LEFT JOIN alert_history ah ON ar.id = ah.alert_rule_id
GROUP BY ar.id,
    ar.name,
    ar.severity,
    ar.enabled
ORDER BY total_alerts DESC;
-- Currently muted rules view
CREATE VIEW IF NOT EXISTS v_muted_rules AS
SELECT am.*,
    ar.name as rule_name,
    ar.severity,
    CASE
        WHEN am.expires_at IS NULL THEN 'indefinite'
        WHEN am.expires_at > datetime('now') THEN 'active'
        ELSE 'expired'
    END as mute_status
FROM alert_mutes am
    JOIN alert_rules ar ON am.alert_rule_id = ar.id
WHERE am.expires_at IS NULL
    OR am.expires_at > datetime('now')
ORDER BY am.muted_at DESC;
-- ============================================================================
-- TRIGGERS: Maintain data integrity
-- ============================================================================
-- Update timestamp on alert_rules update
CREATE TRIGGER IF NOT EXISTS trg_alert_rules_update
AFTER
UPDATE ON alert_rules FOR EACH ROW BEGIN
UPDATE alert_rules
SET updated_at = datetime('now')
WHERE id = NEW.id;
END;
-- Update timestamp on notification_channels update
CREATE TRIGGER IF NOT EXISTS trg_notification_channels_update
AFTER
UPDATE ON notification_channels FOR EACH ROW BEGIN
UPDATE notification_channels
SET updated_at = datetime('now')
WHERE id = NEW.id;
END;
-- Auto-expire old mutes (cleanup trigger)
CREATE TRIGGER IF NOT EXISTS trg_cleanup_expired_mutes
AFTER
INSERT ON alert_mutes BEGIN
DELETE FROM alert_mutes
WHERE expires_at IS NOT NULL
    AND expires_at < datetime('now', '-30 days');
END;
-- ============================================================================
-- INITIAL DATA: Sample notification channels
-- ============================================================================
-- Note: These are templates. Users should configure with their actual settings.
-- Example email channel (disabled by default)
INSERT
    OR IGNORE INTO notification_channels (
        id,
        name,
        channel_type,
        config,
        enabled,
        created_at,
        updated_at
    )
VALUES (
        'email_default',
        'Default Email',
        'email',
        json_object(
            'smtp_host',
            'smtp.example.com',
            'smtp_port',
            587,
            'smtp_user',
            'alerts@example.com',
            'smtp_password',
            '',
            'from_address',
            'alerts@example.com',
            'to_addresses',
            json_array('admin@example.com'),
            'use_tls',
            1
        ),
        0,
        -- Disabled until configured
        datetime('now'),
        datetime('now')
    );
-- Example Slack webhook channel (disabled by default)
INSERT
    OR IGNORE INTO notification_channels (
        id,
        name,
        channel_type,
        config,
        enabled,
        created_at,
        updated_at
    )
VALUES (
        'slack_default',
        'Slack Notifications',
        'slack',
        json_object(
            'webhook_url',
            'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
            'channel',
            '#alerts',
            'username',
            'UniFi Monitor'
        ),
        0,
        -- Disabled until configured
        datetime('now'),
        datetime('now')
    );
-- Example Discord webhook channel (disabled by default)
INSERT
    OR IGNORE INTO notification_channels (
        id,
        name,
        channel_type,
        config,
        enabled,
        created_at,
        updated_at
    )
VALUES (
        'discord_default',
        'Discord Notifications',
        'discord',
        json_object(
            'webhook_url',
            'https://discord.com/api/webhooks/YOUR/WEBHOOK/URL',
            'username',
            'UniFi Monitor'
        ),
        0,
        -- Disabled until configured
        datetime('now'),
        datetime('now')
    );
-- ============================================================================
-- COMMENTS: Schema documentation
-- ============================================================================
-- Alert Rule Types:
--   - threshold: Compare metric value against threshold (e.g., CPU > 90%)
--   - status_change: Detect status changes (e.g., device goes offline)
--   - custom: Custom logic (future extension)
-- Conditions:
--   - gt: Greater than (>)
--   - gte: Greater than or equal (>=)
--   - lt: Less than (<)
--   - lte: Less than or equal (<=)
--   - eq: Equal (==)
--   - ne: Not equal (!=)
-- Severity Levels:
--   - info: Informational, no immediate action required
--   - warning: Requires attention, not critical
--   - critical: Immediate action required
-- Notification Status:
--   JSON object mapping channel_id to delivery status:
--   {"email_primary": "sent", "slack_ops": "failed"}
-- Migration complete!

-- UniFi Network Database Schema
-- SQLite Database for storing host data, metrics, and events
-- Version: 1.0
-- Created: October 17, 2025
-- =============================================================================
-- Table: hosts
-- Description: Primary table for network hosts/devices
-- =============================================================================
CREATE TABLE IF NOT EXISTS hosts (
    id TEXT PRIMARY KEY,
    -- UniFi host ID
    hardware_id TEXT UNIQUE NOT NULL,
    -- Hardware identifier
    type TEXT NOT NULL,
    -- console, gateway, switch, ap
    ip_address TEXT,
    -- Current IP address
    mac_address TEXT,
    -- MAC address
    name TEXT,
    -- Friendly name
    owner BOOLEAN DEFAULT 0,
    -- Is primary owner
    is_blocked BOOLEAN DEFAULT 0,
    -- Blocked status
    firmware_version TEXT,
    -- Current firmware
    model TEXT,
    -- Device model
    registration_time TEXT,
    -- ISO format timestamp
    first_seen TEXT DEFAULT (datetime('now')),
    last_seen TEXT DEFAULT (datetime('now')),
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
-- =============================================================================
-- Table: host_status
-- Description: Historical status tracking for each host
-- =============================================================================
CREATE TABLE IF NOT EXISTS host_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_id TEXT NOT NULL,
    status TEXT NOT NULL,
    -- online, offline, upgrading, etc.
    is_online BOOLEAN,
    uptime_seconds INTEGER,
    cpu_usage REAL,
    memory_usage REAL,
    temperature REAL,
    last_connection_change TEXT,
    -- ISO format timestamp
    last_backup_time TEXT,
    -- ISO format timestamp
    error_message TEXT,
    raw_data TEXT,
    -- Full JSON response
    recorded_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (host_id) REFERENCES hosts(id) ON DELETE CASCADE
);
-- Indexes for host_status
CREATE INDEX IF NOT EXISTS idx_host_status_host_id ON host_status(host_id);
CREATE INDEX IF NOT EXISTS idx_host_status_recorded_at ON host_status(recorded_at);
CREATE INDEX IF NOT EXISTS idx_host_status_status ON host_status(status);
CREATE INDEX IF NOT EXISTS idx_host_status_is_online ON host_status(is_online);
-- =============================================================================
-- Table: events
-- Description: Significant events (status changes, errors, alerts)
-- =============================================================================
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_id TEXT,
    event_type TEXT NOT NULL,
    -- status_change, error, alert, reboot
    severity TEXT NOT NULL,
    -- info, warning, error, critical
    title TEXT NOT NULL,
    description TEXT,
    previous_value TEXT,
    -- For status changes
    new_value TEXT,
    metadata TEXT,
    -- JSON additional data
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (host_id) REFERENCES hosts(id) ON DELETE CASCADE
);
-- Indexes for events
CREATE INDEX IF NOT EXISTS idx_events_host_id ON events(host_id);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity);
-- =============================================================================
-- Table: metrics
-- Description: Time-series metrics for analytics
-- =============================================================================
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    -- cpu_usage, memory_usage, uptime, etc.
    metric_value REAL NOT NULL,
    unit TEXT,
    -- %, seconds, bytes, etc.
    recorded_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (host_id) REFERENCES hosts(id) ON DELETE CASCADE
);
-- Indexes for metrics
CREATE INDEX IF NOT EXISTS idx_metrics_host_id_name ON metrics(host_id, metric_name);
CREATE INDEX IF NOT EXISTS idx_metrics_recorded_at ON metrics(recorded_at);
CREATE INDEX IF NOT EXISTS idx_metrics_metric_name ON metrics(metric_name);
-- =============================================================================
-- Table: collection_runs
-- Description: Track data collection execution for monitoring
-- =============================================================================
CREATE TABLE IF NOT EXISTS collection_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT NOT NULL,
    end_time TEXT,
    status TEXT NOT NULL,
    -- running, success, failed
    hosts_collected INTEGER DEFAULT 0,
    errors_encountered INTEGER DEFAULT 0,
    error_message TEXT,
    duration_seconds REAL,
    created_at TEXT DEFAULT (datetime('now'))
);
-- Indexes for collection_runs
CREATE INDEX IF NOT EXISTS idx_collection_runs_start_time ON collection_runs(start_time);
CREATE INDEX IF NOT EXISTS idx_collection_runs_status ON collection_runs(status);
-- =============================================================================
-- Table: database_metadata
-- Description: Store database version and configuration
-- =============================================================================
CREATE TABLE IF NOT EXISTS database_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT DEFAULT (datetime('now'))
);
-- Insert initial metadata
INSERT
    OR IGNORE INTO database_metadata (key, value)
VALUES ('schema_version', '1.0'),
    ('created_at', datetime('now')),
    ('last_migration', datetime('now'));
-- =============================================================================
-- Views for common queries
-- =============================================================================
-- View: Latest host status
CREATE VIEW IF NOT EXISTS v_latest_host_status AS
SELECT h.id,
    h.name,
    h.type,
    h.ip_address,
    hs.status,
    hs.is_online,
    hs.uptime_seconds,
    hs.recorded_at,
    hs.last_connection_change
FROM hosts h
    LEFT JOIN host_status hs ON h.id = hs.host_id
WHERE hs.id = (
        SELECT MAX(id)
        FROM host_status
        WHERE host_id = h.id
    );
-- View: Host uptime statistics
CREATE VIEW IF NOT EXISTS v_host_uptime_stats AS
SELECT host_id,
    COUNT(*) as total_checks,
    SUM(
        CASE
            WHEN is_online = 1 THEN 1
            ELSE 0
        END
    ) as online_count,
    ROUND(
        AVG(
            CASE
                WHEN is_online = 1 THEN 100.0
                ELSE 0.0
            END
        ),
        2
    ) as uptime_percentage,
    MAX(recorded_at) as last_check,
    MIN(recorded_at) as first_check
FROM host_status
GROUP BY host_id;
-- View: Recent events
CREATE VIEW IF NOT EXISTS v_recent_events AS
SELECT e.id,
    e.host_id,
    h.name as host_name,
    e.event_type,
    e.severity,
    e.title,
    e.description,
    e.created_at
FROM events e
    LEFT JOIN hosts h ON e.host_id = h.id
ORDER BY e.created_at DESC
LIMIT 100;

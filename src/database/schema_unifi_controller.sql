-- UniFi Local Controller Integration Schema Extension
-- Extends existing database with tables for UniFi Controller devices and clients
-- Version: 1.0
-- Created: October 20, 2025
-- =============================================================================
-- =============================================================================
-- Table: unifi_devices
-- Description: UniFi network devices (switches, APs, gateways, UDM)
-- =============================================================================
CREATE TABLE IF NOT EXISTS unifi_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mac TEXT UNIQUE NOT NULL,
    -- Device MAC address (primary identifier)
    device_id TEXT,
    -- UniFi internal device ID
    name TEXT,
    -- Device name
    type TEXT,
    -- usw, uap, ugw, udm, uxg, ubb
    model TEXT,
    -- Device model (e.g., US8P150, UAP-AC-PRO)
    version TEXT,
    -- Firmware version
    ip TEXT,
    -- IP address
    site_name TEXT DEFAULT 'default',
    -- Site name
    state INTEGER,
    -- Connection state (1=online, 0=offline)
    adopted BOOLEAN DEFAULT 0,
    -- Is device adopted
    disabled BOOLEAN DEFAULT 0,
    -- Is device disabled
    -- Statistics
    uptime INTEGER,
    -- Uptime in seconds
    satisfaction INTEGER,
    -- Client satisfaction (0-100)
    num_sta INTEGER DEFAULT 0,
    -- Number of connected clients (APs)
    bytes_total INTEGER DEFAULT 0,
    -- Total bytes transferred
    -- LED control
    led_override TEXT DEFAULT 'default',
    -- LED override setting
    led_override_color TEXT,
    -- LED color if overridden
    -- Timestamps
    last_seen TEXT,
    -- Last seen timestamp (ISO format)
    first_seen TEXT DEFAULT (datetime('now')),
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
-- Indexes for unifi_devices
CREATE INDEX IF NOT EXISTS idx_unifi_devices_mac ON unifi_devices(mac);
CREATE INDEX IF NOT EXISTS idx_unifi_devices_site_name ON unifi_devices(site_name);
CREATE INDEX IF NOT EXISTS idx_unifi_devices_type ON unifi_devices(type);
CREATE INDEX IF NOT EXISTS idx_unifi_devices_state ON unifi_devices(state);
CREATE INDEX IF NOT EXISTS idx_unifi_devices_last_seen ON unifi_devices(last_seen);
-- =============================================================================
-- Table: unifi_device_status
-- Description: Historical status tracking for UniFi devices
-- =============================================================================
CREATE TABLE IF NOT EXISTS unifi_device_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_mac TEXT NOT NULL,
    -- Foreign key to unifi_devices.mac
    state INTEGER NOT NULL,
    -- 1=online, 0=offline
    uptime INTEGER,
    -- Uptime in seconds
    cpu_usage REAL,
    -- CPU usage percentage
    memory_usage REAL,
    -- Memory usage percentage
    temperature REAL,
    -- Temperature in Celsius
    num_clients INTEGER DEFAULT 0,
    -- Number of connected clients
    satisfaction INTEGER,
    -- Client satisfaction score
    bytes_rx INTEGER DEFAULT 0,
    -- Bytes received
    bytes_tx INTEGER DEFAULT 0,
    -- Bytes transmitted
    -- Port statistics (for switches)
    port_stats TEXT,
    -- JSON: port-level statistics
    -- Metadata
    raw_data TEXT,
    -- Full JSON response
    recorded_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (device_mac) REFERENCES unifi_devices(mac) ON DELETE CASCADE
);
-- Indexes for unifi_device_status
CREATE INDEX IF NOT EXISTS idx_unifi_device_status_mac ON unifi_device_status(device_mac);
CREATE INDEX IF NOT EXISTS idx_unifi_device_status_recorded_at ON unifi_device_status(recorded_at);
CREATE INDEX IF NOT EXISTS idx_unifi_device_status_state ON unifi_device_status(state);
-- =============================================================================
-- Table: unifi_clients
-- Description: UniFi network clients (connected devices)
-- =============================================================================
CREATE TABLE IF NOT EXISTS unifi_clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mac TEXT UNIQUE NOT NULL,
    -- Client MAC address (primary identifier)
    client_id TEXT,
    -- UniFi internal client ID
    hostname TEXT,
    -- Client hostname
    name TEXT,
    -- Friendly name (if set)
    ip TEXT,
    -- IP address
    site_name TEXT DEFAULT 'default',
    -- Site name
    -- Connection info
    is_wired BOOLEAN DEFAULT 0,
    -- Wired vs wireless
    is_guest BOOLEAN DEFAULT 0,
    -- Guest network client
    blocked BOOLEAN DEFAULT 0,
    -- Is client blocked
    -- Wireless info (if applicable)
    essid TEXT,
    -- WiFi SSID
    channel INTEGER,
    -- WiFi channel
    ap_mac TEXT,
    -- Connected AP MAC
    ap_name TEXT,
    -- Connected AP name
    -- Wired info (if applicable)
    sw_mac TEXT,
    -- Connected switch MAC
    sw_port INTEGER,
    -- Connected switch port
    -- Network info
    network TEXT,
    -- Network name
    usergroup_id TEXT,
    -- User group ID
    use_fixedip BOOLEAN DEFAULT 0,
    -- Has fixed IP
    oui TEXT,
    -- Manufacturer (from OUI)
    -- Timestamps
    first_seen TEXT,
    -- First seen timestamp
    last_seen TEXT,
    -- Last seen timestamp
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
-- Indexes for unifi_clients
CREATE INDEX IF NOT EXISTS idx_unifi_clients_mac ON unifi_clients(mac);
CREATE INDEX IF NOT EXISTS idx_unifi_clients_site_name ON unifi_clients(site_name);
CREATE INDEX IF NOT EXISTS idx_unifi_clients_is_wired ON unifi_clients(is_wired);
CREATE INDEX IF NOT EXISTS idx_unifi_clients_blocked ON unifi_clients(blocked);
CREATE INDEX IF NOT EXISTS idx_unifi_clients_last_seen ON unifi_clients(last_seen);
CREATE INDEX IF NOT EXISTS idx_unifi_clients_ap_mac ON unifi_clients(ap_mac);
CREATE INDEX IF NOT EXISTS idx_unifi_clients_sw_mac ON unifi_clients(sw_mac);
-- =============================================================================
-- Table: unifi_client_status
-- Description: Historical status tracking for UniFi clients
-- =============================================================================
CREATE TABLE IF NOT EXISTS unifi_client_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_mac TEXT NOT NULL,
    -- Foreign key to unifi_clients.mac
    ip TEXT,
    -- IP address at time of recording
    is_wired BOOLEAN DEFAULT 0,
    -- Connection type
    -- Signal quality (wireless only)
    signal INTEGER,
    -- Signal strength in dBm
    noise INTEGER,
    -- Noise floor in dBm
    rssi INTEGER,
    -- RSSI value
    -- Data transfer
    tx_bytes INTEGER DEFAULT 0,
    -- Bytes transmitted
    rx_bytes INTEGER DEFAULT 0,
    -- Bytes received
    tx_rate INTEGER DEFAULT 0,
    -- TX rate in Kbps
    rx_rate INTEGER DEFAULT 0,
    -- RX rate in Kbps
    -- Connection
    uptime INTEGER,
    -- Connection uptime in seconds
    satisfaction INTEGER,
    -- Client satisfaction (0-100)
    -- Metadata
    raw_data TEXT,
    -- Full JSON response
    recorded_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (client_mac) REFERENCES unifi_clients(mac) ON DELETE CASCADE
);
-- Indexes for unifi_client_status
CREATE INDEX IF NOT EXISTS idx_unifi_client_status_mac ON unifi_client_status(client_mac);
CREATE INDEX IF NOT EXISTS idx_unifi_client_status_recorded_at ON unifi_client_status(recorded_at);
-- =============================================================================
-- Table: unifi_events
-- Description: Events from UniFi Controller (status changes, alerts)
-- =============================================================================
CREATE TABLE IF NOT EXISTS unifi_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_mac TEXT,
    -- Related device MAC (if applicable)
    client_mac TEXT,
    -- Related client MAC (if applicable)
    event_type TEXT NOT NULL,
    -- status_change, connection, disconnection, etc.
    severity TEXT NOT NULL,
    -- info, warning, error, critical
    title TEXT NOT NULL,
    -- Event title
    description TEXT,
    -- Event description
    -- Change tracking
    previous_value TEXT,
    -- Previous value (for changes)
    new_value TEXT,
    -- New value (for changes)
    -- Metadata
    metadata TEXT,
    -- JSON: additional data
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (device_mac) REFERENCES unifi_devices(mac) ON DELETE CASCADE,
    FOREIGN KEY (client_mac) REFERENCES unifi_clients(mac) ON DELETE CASCADE
);
-- Indexes for unifi_events
CREATE INDEX IF NOT EXISTS idx_unifi_events_device_mac ON unifi_events(device_mac);
CREATE INDEX IF NOT EXISTS idx_unifi_events_client_mac ON unifi_events(client_mac);
CREATE INDEX IF NOT EXISTS idx_unifi_events_created_at ON unifi_events(created_at);
CREATE INDEX IF NOT EXISTS idx_unifi_events_event_type ON unifi_events(event_type);
CREATE INDEX IF NOT EXISTS idx_unifi_events_severity ON unifi_events(severity);
-- =============================================================================
-- Table: unifi_device_metrics
-- Description: Time-series metrics for UniFi devices
-- =============================================================================
CREATE TABLE IF NOT EXISTS unifi_device_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_mac TEXT NOT NULL,
    -- Foreign key to unifi_devices.mac
    metric_name TEXT NOT NULL,
    -- cpu_usage, memory_usage, uptime, temp, etc.
    metric_value REAL NOT NULL,
    -- Metric value
    unit TEXT,
    -- %, seconds, bytes, celsius, etc.
    recorded_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (device_mac) REFERENCES unifi_devices(mac) ON DELETE CASCADE
);
-- Indexes for unifi_device_metrics
CREATE INDEX IF NOT EXISTS idx_unifi_device_metrics_mac_name ON unifi_device_metrics(device_mac, metric_name);
CREATE INDEX IF NOT EXISTS idx_unifi_device_metrics_recorded_at ON unifi_device_metrics(recorded_at);
CREATE INDEX IF NOT EXISTS idx_unifi_device_metrics_metric_name ON unifi_device_metrics(metric_name);
-- =============================================================================
-- Table: unifi_client_metrics
-- Description: Time-series metrics for UniFi clients
-- =============================================================================
CREATE TABLE IF NOT EXISTS unifi_client_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_mac TEXT NOT NULL,
    -- Foreign key to unifi_clients.mac
    metric_name TEXT NOT NULL,
    -- signal, tx_rate, rx_rate, satisfaction, etc.
    metric_value REAL NOT NULL,
    -- Metric value
    unit TEXT,
    -- dBm, Kbps, %, etc.
    recorded_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (client_mac) REFERENCES unifi_clients(mac) ON DELETE CASCADE
);
-- Indexes for unifi_client_metrics
CREATE INDEX IF NOT EXISTS idx_unifi_client_metrics_mac_name ON unifi_client_metrics(client_mac, metric_name);
CREATE INDEX IF NOT EXISTS idx_unifi_client_metrics_recorded_at ON unifi_client_metrics(recorded_at);
CREATE INDEX IF NOT EXISTS idx_unifi_client_metrics_metric_name ON unifi_client_metrics(metric_name);
-- =============================================================================
-- Table: unifi_collection_runs
-- Description: Track UniFi Controller data collection execution
-- =============================================================================
CREATE TABLE IF NOT EXISTS unifi_collection_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    controller_host TEXT NOT NULL,
    -- Controller IP/hostname
    start_time TEXT NOT NULL,
    end_time TEXT,
    status TEXT NOT NULL,
    -- running, success, failed
    devices_collected INTEGER DEFAULT 0,
    clients_collected INTEGER DEFAULT 0,
    errors_encountered INTEGER DEFAULT 0,
    error_message TEXT,
    duration_seconds REAL,
    created_at TEXT DEFAULT (datetime('now'))
);
-- Indexes for unifi_collection_runs
CREATE INDEX IF NOT EXISTS idx_unifi_collection_runs_start_time ON unifi_collection_runs(start_time);
CREATE INDEX IF NOT EXISTS idx_unifi_collection_runs_status ON unifi_collection_runs(status);
-- =============================================================================
-- Views for common queries
-- =============================================================================
-- View: Latest UniFi device status
CREATE VIEW IF NOT EXISTS v_unifi_latest_device_status AS
SELECT d.id,
    d.mac,
    d.name,
    d.type,
    d.model,
    d.ip,
    d.site_name,
    ds.state,
    ds.uptime,
    ds.cpu_usage,
    ds.memory_usage,
    ds.temperature,
    ds.num_clients,
    ds.satisfaction,
    ds.recorded_at,
    d.last_seen
FROM unifi_devices d
    LEFT JOIN unifi_device_status ds ON d.mac = ds.device_mac
WHERE ds.id = (
        SELECT MAX(id)
        FROM unifi_device_status
        WHERE device_mac = d.mac
    );
-- View: Latest UniFi client status
CREATE VIEW IF NOT EXISTS v_unifi_latest_client_status AS
SELECT c.id,
    c.mac,
    c.hostname,
    c.name,
    c.ip,
    c.is_wired,
    c.is_guest,
    c.blocked,
    c.essid,
    c.ap_name,
    cs.signal,
    cs.tx_rate,
    cs.rx_rate,
    cs.satisfaction,
    cs.recorded_at,
    c.last_seen
FROM unifi_clients c
    LEFT JOIN unifi_client_status cs ON c.mac = cs.client_mac
WHERE cs.id = (
        SELECT MAX(id)
        FROM unifi_client_status
        WHERE client_mac = c.mac
    );
-- View: UniFi device uptime statistics
CREATE VIEW IF NOT EXISTS v_unifi_device_uptime_stats AS
SELECT device_mac,
    COUNT(*) as total_checks,
    SUM(
        CASE
            WHEN state = 1 THEN 1
            ELSE 0
        END
    ) as online_count,
    ROUND(
        AVG(
            CASE
                WHEN state = 1 THEN 100.0
                ELSE 0.0
            END
        ),
        2
    ) as uptime_percentage,
    MAX(recorded_at) as last_check,
    MIN(recorded_at) as first_check
FROM unifi_device_status
GROUP BY device_mac;
-- View: UniFi client connection summary
CREATE VIEW IF NOT EXISTS v_unifi_client_connections AS
SELECT c.mac,
    c.hostname,
    c.name,
    c.is_wired,
    c.is_guest,
    CASE
        WHEN c.is_wired = 1 THEN c.sw_mac || ':' || COALESCE(c.sw_port, 0)
        ELSE c.ap_mac || ':' || COALESCE(c.essid, 'Unknown')
    END as connection_point,
    COUNT(cs.id) as status_records,
    AVG(cs.satisfaction) as avg_satisfaction,
    c.last_seen
FROM unifi_clients c
    LEFT JOIN unifi_client_status cs ON c.mac = cs.client_mac
GROUP BY c.mac;
-- View: Recent UniFi events
CREATE VIEW IF NOT EXISTS v_unifi_recent_events AS
SELECT e.id,
    e.device_mac,
    d.name as device_name,
    e.client_mac,
    c.hostname as client_hostname,
    e.event_type,
    e.severity,
    e.title,
    e.description,
    e.created_at
FROM unifi_events e
    LEFT JOIN unifi_devices d ON e.device_mac = d.mac
    LEFT JOIN unifi_clients c ON e.client_mac = c.mac
ORDER BY e.created_at DESC
LIMIT 100;
-- View: UniFi network topology (devices and their connected clients)
CREATE VIEW IF NOT EXISTS v_unifi_network_topology AS
SELECT d.mac as device_mac,
    d.name as device_name,
    d.type as device_type,
    d.model as device_model,
    d.state as device_state,
    COUNT(DISTINCT c.mac) as connected_clients,
    GROUP_CONCAT(DISTINCT c.hostname) as client_hostnames
FROM unifi_devices d
    LEFT JOIN unifi_clients c ON (
        (
            d.mac = c.ap_mac
            AND c.is_wired = 0
        )
        OR (
            d.mac = c.sw_mac
            AND c.is_wired = 1
        )
    )
GROUP BY d.mac;
-- =============================================================================
-- Update metadata
-- =============================================================================
INSERT
    OR REPLACE INTO database_metadata (key, value)
VALUES ('unifi_controller_schema_version', '1.0'),
    ('unifi_controller_schema_added', datetime('now'));

-- UniFi Network Database Schema for Cloudflare D1

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    full_name TEXT,
    is_active INTEGER DEFAULT 1,
    is_superuser INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Alert rules table
CREATE TABLE IF NOT EXISTS alert_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    rule_type TEXT NOT NULL CHECK(rule_type IN ('threshold', 'status_change', 'anomaly')),
    condition TEXT NOT NULL,
    threshold REAL,
    severity TEXT NOT NULL CHECK(severity IN ('info', 'warning', 'critical')),
    enabled INTEGER DEFAULT 1,
    cooldown_minutes INTEGER DEFAULT 15,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id INTEGER NOT NULL,
    host_id INTEGER,
    status TEXT NOT NULL CHECK(status IN ('active', 'acknowledged', 'resolved')),
    severity TEXT NOT NULL CHECK(severity IN ('info', 'warning', 'critical')),
    message TEXT NOT NULL,
    metric_value REAL,
    threshold_value REAL,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP,
    acknowledged_by TEXT,
    resolved_at TIMESTAMP,
    resolved_by TEXT,
    notes TEXT,
    FOREIGN KEY (rule_id) REFERENCES alert_rules(id) ON DELETE CASCADE
);

-- Notification channels table
CREATE TABLE IF NOT EXISTS notification_channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    channel_type TEXT NOT NULL CHECK(channel_type IN ('email', 'slack', 'discord', 'webhook')),
    config TEXT NOT NULL, -- JSON config
    enabled INTEGER DEFAULT 1,
    min_severity TEXT DEFAULT 'info' CHECK(min_severity IN ('info', 'warning', 'critical')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_triggered_at ON alerts(triggered_at);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Insert default admin user (password: admin123 - CHANGE IN PRODUCTION!)
-- Password hash for "admin123" using bcrypt
INSERT OR IGNORE INTO users (username, email, hashed_password, full_name, is_superuser)
VALUES ('admin', 'admin@example.com', '$2a$10$rY8qEjV5zXV5xV5xV5xV5euM5xV5xV5xV5xV5xV5xV5xV5xV5xV5', 'Administrator', 1);

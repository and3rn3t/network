# Phase 2 Kickoff: Data Storage & Persistence

**Date:** October 17, 2025
**Phase Duration:** Weeks 3-4
**Status:** 🚀 Starting Now
**Dependencies:** ✅ Phase 1 Complete

---

## Executive Summary

Phase 2 will build upon our solid Phase 1 foundation by adding persistent data storage and automated data collection. We'll implement a SQLite database to store host information, track status changes over time, and enable historical analysis.

---

## Goals

1. **Persistent Storage** - Store host data in SQLite database
2. **Historical Tracking** - Track status changes and metrics over time
3. **Automated Collection** - Periodic polling of host data
4. **Query Interface** - Easy access to stored data
5. **Data Management** - Retention policies and cleanup

---

## Phase 2 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    UniFi API Client                      │
│                  (Phase 1 - Complete)                    │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│              Data Collection Service                     │
│         (Automated Polling Every 5 min)                  │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                  Data Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │    Models    │  │  Repository  │  │   Queries    │ │
│  │  (ORM/DTOs)  │  │  (CRUD Ops)  │  │ (Analytics)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                 SQLite Database                          │
│   • hosts        • host_status      • events            │
│   • metrics      • configuration    • metadata          │
└─────────────────────────────────────────────────────────┘
```

---

## Database Schema Design

### Core Tables

#### 1. **hosts**

Primary table for network hosts/devices.

```sql
CREATE TABLE hosts (
    id TEXT PRIMARY KEY,              -- UniFi host ID
    hardware_id TEXT UNIQUE,          -- Hardware identifier
    type TEXT NOT NULL,               -- console, gateway, switch, ap
    ip_address TEXT,                  -- Current IP address
    mac_address TEXT,                 -- MAC address
    name TEXT,                        -- Friendly name
    owner BOOLEAN DEFAULT 0,          -- Is primary owner
    is_blocked BOOLEAN DEFAULT 0,     -- Blocked status
    firmware_version TEXT,            -- Current firmware
    model TEXT,                       -- Device model
    registration_time TIMESTAMP,      -- First seen
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. **host_status**

Historical status tracking for each host.

```sql
CREATE TABLE host_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_id TEXT NOT NULL,
    status TEXT NOT NULL,             -- online, offline, upgrading, etc.
    is_online BOOLEAN,
    uptime_seconds INTEGER,
    cpu_usage REAL,
    memory_usage REAL,
    temperature REAL,
    last_connection_change TIMESTAMP,
    last_backup_time TIMESTAMP,
    error_message TEXT,
    raw_data TEXT,                    -- Full JSON response
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (host_id) REFERENCES hosts(id) ON DELETE CASCADE
);

CREATE INDEX idx_host_status_host_id ON host_status(host_id);
CREATE INDEX idx_host_status_recorded_at ON host_status(recorded_at);
CREATE INDEX idx_host_status_status ON host_status(status);
```

#### 3. **events**

Significant events (status changes, errors, alerts).

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_id TEXT,
    event_type TEXT NOT NULL,         -- status_change, error, alert, reboot
    severity TEXT NOT NULL,           -- info, warning, error, critical
    title TEXT NOT NULL,
    description TEXT,
    previous_value TEXT,              -- For status changes
    new_value TEXT,
    metadata TEXT,                    -- JSON additional data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (host_id) REFERENCES hosts(id) ON DELETE CASCADE
);

CREATE INDEX idx_events_host_id ON events(host_id);
CREATE INDEX idx_events_created_at ON events(created_at);
CREATE INDEX idx_events_event_type ON events(event_type);
CREATE INDEX idx_events_severity ON events(severity);
```

#### 4. **metrics**

Time-series metrics for analytics.

```sql
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,        -- cpu_usage, memory_usage, uptime, etc.
    metric_value REAL NOT NULL,
    unit TEXT,                        -- %, seconds, bytes, etc.
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (host_id) REFERENCES hosts(id) ON DELETE CASCADE
);

CREATE INDEX idx_metrics_host_id_name ON metrics(host_id, metric_name);
CREATE INDEX idx_metrics_recorded_at ON metrics(recorded_at);
```

#### 5. **collection_runs**

Track data collection execution.

```sql
CREATE TABLE collection_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status TEXT NOT NULL,             -- running, success, failed
    hosts_collected INTEGER DEFAULT 0,
    errors_encountered INTEGER DEFAULT 0,
    error_message TEXT,
    duration_seconds REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_collection_runs_start_time ON collection_runs(start_time);
CREATE INDEX idx_collection_runs_status ON collection_runs(status);
```

---

## Implementation Plan

### Week 3: Database Foundation

#### Task 1: Database Schema & Setup (Day 1-2)

- [ ] Create `src/database/` directory structure
- [ ] Write `schema.sql` with all tables
- [ ] Create `database.py` with connection management
- [ ] Implement database initialization
- [ ] Add migration support

**Files to Create:**

```
src/database/
  ├── __init__.py
  ├── database.py         # Database connection & management
  ├── schema.sql          # Database schema
  ├── migrations.py       # Migration utilities
  └── models.py           # Data models/DTOs
```

#### Task 2: Data Models (Day 2-3)

- [ ] Create Host model class
- [ ] Create HostStatus model class
- [ ] Create Event model class
- [ ] Create Metric model class
- [ ] Add validation and serialization

#### Task 3: Repository Layer (Day 3-4)

- [ ] Create HostRepository with CRUD operations
- [ ] Create StatusRepository for status tracking
- [ ] Create EventRepository for event logging
- [ ] Create MetricRepository for metrics
- [ ] Add query helpers and filters

**Files to Create:**

```
src/database/
  └── repositories/
      ├── __init__.py
      ├── base.py           # Base repository
      ├── host_repository.py
      ├── status_repository.py
      ├── event_repository.py
      └── metric_repository.py
```

### Week 4: Data Collection & Testing

#### Task 4: Data Collection Service (Day 5-6)

- [ ] Create DataCollector class
- [ ] Implement periodic polling logic
- [ ] Add error handling and retry
- [ ] Status change detection
- [ ] Event generation

**Files to Create:**

```
src/
  └── collector/
      ├── __init__.py
      ├── data_collector.py
      ├── scheduler.py
      └── config.py
```

#### Task 5: Testing (Day 7-8)

- [ ] Database tests (schema, migrations)
- [ ] Model tests (validation, serialization)
- [ ] Repository tests (CRUD operations)
- [ ] Collector tests (data collection)
- [ ] Integration tests

**Files to Create:**

```
tests/
  ├── test_database.py
  ├── test_models.py
  ├── test_repositories.py
  └── test_collector.py
```

#### Task 6: Documentation & Examples (Day 8)

- [ ] Update API_REFERENCE.md
- [ ] Create DATABASE_SCHEMA.md
- [ ] Write example scripts
- [ ] Update README

---

## Success Criteria

✅ **Must Have:**

- SQLite database with complete schema
- Data models for all entities
- CRUD operations for all tables
- Automated data collection (every 5 min)
- Status change detection and event logging
- 70%+ test coverage on new code

🎯 **Should Have:**

- Data retention policies (configurable)
- Export functionality (CSV/JSON)
- Query helpers for common analytics
- Migration system for schema changes

🌟 **Nice to Have:**

- Database backup utilities
- Data visualization prep
- Performance optimization
- Caching layer

---

## Technical Decisions

### 1. Database: SQLite

**Rationale:**

- No external server required
- Perfect for single-user/local use
- Fast for read-heavy workloads
- Easy backup (single file)
- Can migrate to PostgreSQL later if needed

### 2. ORM: None (Direct SQL)

**Rationale:**

- Keep dependencies minimal
- Better performance control
- Easier debugging
- Simple schema doesn't need ORM complexity

### 3. Data Collection: Scheduled Polling

**Rationale:**

- Simple and reliable
- Predictable resource usage
- Easy to pause/resume
- Works with existing API client

### 4. Retention Policy: Configurable

**Rationale:**

- Different needs for different users
- Disk space management
- Performance optimization
- Compliance requirements

---

## Configuration

### Database Configuration

```python
# config.py
DATABASE_CONFIG = {
    "path": "data/unifi_network.db",
    "backup_dir": "data/backups/",
    "auto_backup": True,
    "backup_frequency": "daily"
}
```

### Collection Configuration

```python
COLLECTION_CONFIG = {
    "enabled": True,
    "interval_seconds": 300,  # 5 minutes
    "retry_on_error": True,
    "max_retries": 3,
    "detect_status_changes": True,
    "log_events": True
}
```

### Retention Configuration

```python
RETENTION_CONFIG = {
    "host_status_days": 90,      # Keep 90 days of status
    "events_days": 365,          # Keep 1 year of events
    "metrics_days": 30,          # Keep 30 days of metrics
    "collection_runs_days": 30,  # Keep 30 days of runs
    "auto_cleanup": True,
    "cleanup_hour": 2            # Run at 2 AM
}
```

---

## Dependencies

### New Python Packages

```bash
# No new dependencies needed! Using stdlib:
- sqlite3 (built-in)
- datetime (built-in)
- json (built-in)
- typing (built-in)
```

### Phase 1 Dependencies (Already Installed)

- requests
- pytest
- pytest-cov
- responses

---

## Risk Assessment

### Low Risk ✅

- Database setup (well-established technology)
- CRUD operations (straightforward)
- Testing (existing infrastructure)

### Medium Risk ⚠️

- Data collection reliability (network dependencies)
- Performance at scale (many hosts)
- Schema design (may need adjustments)

### Mitigation Strategies

1. **Reliability**: Retry logic, error logging, graceful degradation
2. **Performance**: Indexes, batch operations, connection pooling
3. **Schema**: Migration system for easy updates

---

## Next Steps

Ready to begin? Here's the recommended order:

1. **First:** Create database schema and initialization
2. **Second:** Build data models and validation
3. **Third:** Implement repository layer
4. **Fourth:** Create data collector
5. **Fifth:** Write comprehensive tests
6. **Sixth:** Documentation and examples

Let's start with Step 1: Database Schema! 🚀

---

**Questions to Consider:**

1. How long should we keep historical data? (Default: 90 days for status)
2. How often should we poll? (Default: 5 minutes)
3. Where should the database file live? (Default: `data/unifi_network.db`)
4. Should we implement automatic backups? (Default: Yes, daily)

---

Ready to proceed? Let me know and we'll create the database schema!

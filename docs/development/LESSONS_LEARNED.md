# Lessons Learned - UniFi Network Monitor Project

**Last Updated**: October 20, 2025
**Project Phase**: Task 8 Complete - Production Ready

## Overview

This document captures key lessons, solutions, and best practices discovered during the development of the UniFi Network Monitor project. These insights will help prevent future issues and guide similar projects.

---

## Table of Contents

1. [Python Development](#python-development)
2. [UniFi API Integration](#unifi-api-integration)
3. [Database Design](#database-design)
4. [Testing Strategies](#testing-strategies)
5. [Repository Organization](#repository-organization)
6. [Documentation Practices](#documentation-practices)
7. [Common Pitfalls](#common-pitfalls)

---

## Python Development

### Circular Import Resolution

**Problem**: Circular imports between repository classes and models causing import failures.

**Solution**:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.alerts.engine import AlertEngine
    from src.alerts.manager import AlertManager

# Use lazy imports in methods
def get_alert_engine(self) -> "AlertEngine":
    from src.alerts.engine import AlertEngine
    return AlertEngine()
```

**Key Learnings**:

- Use `TYPE_CHECKING` for type hints only
- Implement lazy imports within methods that need the dependency
- Keep `__init__.py` minimal - avoid re-exporting classes that create circular dependencies
- Structure modules to have clear dependency hierarchy

### Type Hints and Mypy

**Best Practices**:

- Always use type hints for function parameters and returns
- Use `Optional[T]` for nullable values, not `T | None` (Python 3.9 compatibility)
- For database results: `list[dict[str, Any]]` is clearer than `List[Dict]`
- Run `mypy src/` regularly to catch type errors early

**Common Patterns**:

```python
from typing import Optional, Any
from datetime import datetime

def process_data(
    data: dict[str, Any],
    timestamp: Optional[datetime] = None
) -> list[dict[str, Any]]:
    """Process data with optional timestamp."""
    pass
```

### Path Resolution for Scripts

**Problem**: Scripts in subdirectories couldn't import from `src/`.

**Solution** (standardized pattern):

```python
from pathlib import Path
import sys
import os

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Change to project root for relative paths
os.chdir(Path(__file__).parent.parent)
```

**Key Learnings**:

- Always use `Path(__file__).parent.parent` for scripts in `scripts/`
- Use `os.chdir()` when scripts need to access files with relative paths
- Test scripts from both root and subdirectories
- Document expected working directory in script docstrings

---

## UniFi API Integration

### Controller Authentication

**Key Findings**:

- UniFi Controller uses cookie-based sessions, not token auth
- Login endpoint: `POST /api/login` with `{"username": "...", "password": "..."}`
- Session cookies must be preserved across requests using `requests.Session()`
- Sessions expire after ~24 hours of inactivity

**Best Practices**:

```python
import requests

class UniFiClient:
    def __init__(self, base_url: str, username: str, password: str, verify_ssl: bool = True):
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.base_url = base_url
        self._login(username, password)

    def _login(self, username: str, password: str) -> None:
        """Login and establish session."""
        response = self.session.post(
            f"{self.base_url}/api/login",
            json={"username": username, "password": password},
            timeout=30
        )
        response.raise_for_status()
```

### API Method Signatures

**Problem**: UniFi API methods evolved, breaking compatibility.

**Example Issue**:

```python
# Old signature (worked with cloud API)
def get_devices(self, site: str = "default") -> list[dict]:
    pass

# New signature (local controller)
def get_devices(self) -> list[dict]:  # No site parameter
    pass
```

**Solution**:

- Always check actual API implementation before calling
- Don't assume cloud API patterns work with local controllers
- Test with actual controller responses, not mock data
- Document which controller versions are tested

### Site Context

**Key Learnings**:

- Local controllers often default to "default" site automatically
- Site ID vs Site Name: APIs use name, database uses ID
- Always include site in endpoint path: `/api/s/{site}/stat/device`
- Site "default" is common but not guaranteed - check with `/api/self/sites`

### Data Models and IDs

**Important Patterns**:

- **Devices**: Identified by MAC address (primary key in our schema)
- **Clients**: Identified by MAC address (ephemeral - only active/recent)
- **MAC Addresses**: Stored lowercase without colons for consistency
- **Timestamps**: UniFi uses Unix epoch (seconds), convert to ISO 8601 for storage

**UniFi Data Quirks**:

```python
# UniFi returns MACs in various formats
mac_raw = "12:34:56:78:9a:bc"  # From API
mac_normalized = mac_raw.replace(":", "").lower()  # For storage

# UniFi timestamps are Unix epoch
timestamp_raw = 1729458000  # From API
timestamp_iso = datetime.fromtimestamp(timestamp_raw).isoformat()  # For DB

# Client data is ephemeral
clients = get_clients()  # Only returns currently connected or recently seen
# Missing clients doesn't mean they don't exist - they may just be offline
```

### Request Best Practices

**Rate Limiting**:

- UniFi controllers can be overwhelmed by rapid requests
- Add delay between batch operations (0.5-1 second)
- Cache site lists when making multiple calls
- Use batch endpoints when available

**Error Handling**:

```python
from requests.exceptions import RequestException, Timeout

try:
    response = self._request("GET", endpoint)
except Timeout:
    # Controller may be slow or network issues
    logger.error("Request timeout - controller may be overloaded")
except RequestException as e:
    # Generic network/HTTP errors
    logger.error(f"API request failed: {e}")
```

---

## Database Design

### Schema Evolution

**Lesson**: Start with flexible schema, add constraints later.

**Good Pattern**:

```sql
-- Start with basics
CREATE TABLE unifi_devices (
    mac_address TEXT PRIMARY KEY,
    name TEXT,
    model TEXT,
    data JSON,  -- Store full API response initially
    last_seen TIMESTAMP
);

-- Add constraints after understanding data
ALTER TABLE unifi_devices
ADD CONSTRAINT check_mac_format
CHECK (mac_address GLOB '[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]');
```

### Database Locking Issues

**Problem**: SQLite database locked during development.

**Causes**:

1. VS Code SQLite extension holding read locks
2. Multiple scripts accessing database simultaneously
3. Long-running queries in other tools

**Solutions**:

- Close database connections in VS Code extensions
- Restart VS Code to release all locks
- Use `PRAGMA busy_timeout = 5000;` for automatic retry
- Implement connection pooling with proper cleanup
- Use WAL mode for better concurrency: `PRAGMA journal_mode=WAL;`

**Prevention**:

```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db_connection(db_path: str):
    """Context manager for database connections."""
    conn = sqlite3.connect(db_path, timeout=5.0)
    conn.execute("PRAGMA busy_timeout = 5000")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

### JSON Storage vs. Relational

**When to Use JSON**:

- Storing full API responses for debugging
- Flexible data that varies by device type
- Configuration data with nested structures

**When to Use Relational**:

- Data you need to query or join
- Metrics and time-series data
- Normalized data (devices, clients, users)

**Hybrid Approach** (our solution):

```sql
CREATE TABLE unifi_devices (
    mac_address TEXT PRIMARY KEY,
    name TEXT,              -- Queryable fields
    model TEXT,
    ip_address TEXT,
    raw_data JSON,          -- Full API response
    last_seen TIMESTAMP
);

-- Index queryable fields
CREATE INDEX idx_devices_model ON unifi_devices(model);
CREATE INDEX idx_devices_last_seen ON unifi_devices(last_seen);
```

---

## Testing Strategies

### Integration Testing Approach

**Lesson**: Test with real data as early as possible.

**Progression**:

1. **Unit Tests**: Mock UniFi API responses
2. **Integration Tests**: Real controller, test database
3. **System Tests**: Real controller, production database
4. **Production**: Automated collection with monitoring

**Critical Test Cases**:

- Empty device list (new controller)
- Device offline/online transitions
- Client connects/disconnects
- Network errors and timeouts
- Database lock scenarios

### Test Data Management

**Best Practices**:

- Use separate test database (`test_unifi.db`)
- Reset test database before each test run
- Save sample API responses in `tests/fixtures/`
- Test with both mock and real data

**Example**:

```python
import pytest
from pathlib import Path

@pytest.fixture
def test_db():
    """Create fresh test database."""
    db_path = Path("test_unifi.db")
    if db_path.exists():
        db_path.unlink()

    # Create schema
    from src.database.schema import create_tables
    create_tables(str(db_path))

    yield str(db_path)

    # Cleanup
    if db_path.exists():
        db_path.unlink()
```

---

## Repository Organization

### Directory Structure

**Final Structure** (after Task 8):

```
network/
├── src/                    # Source code (production)
├── scripts/                # Utilities and tests (44 files)
├── docs/                   # All documentation (92 files)
├── data/                   # Database backups
├── config.py              # Configuration
└── collect_unifi_data.py  # Main script
```

**Key Learnings**:

- Keep root directory minimal (< 10 files)
- Separate production code (`src/`) from utilities (`scripts/`)
- Archive completed documentation (`docs/archive/`)
- Use `data/` for test databases and backups
- Main entry point stays in root for easy access

### Script Organization

**Categories** (44 total in `scripts/`):

1. **Database Utilities** (5): `create_fresh_db.py`, `setup_database.py`, etc.
2. **Collection Scripts** (4): `collect_metrics.py`, `quick_collect.py`, etc.
3. **Testing Scripts** (20+): `test_*.py` for all components
4. **Diagnostics** (5+): `diagnose_*.py`, `debug_*.py`
5. **PowerShell Automation** (4): `*.ps1` for Windows tasks
6. **API Testing** (1): `api_explorer.http`

**Benefits**:

- Easy to find utilities without cluttering root
- Clear separation of concerns
- All scripts use standardized path resolution
- README in scripts/ directory for quick reference

### Migration Pattern

**When Moving Scripts**:

1. Create target directory
2. Move files in batches (by category)
3. Update path resolution in each file
4. Test from new location
5. Update documentation references
6. Verify with `python scripts/script_name.py --help`

---

## Documentation Practices

### Documentation Types

**Identified Types** (from 92 docs):

1. **Reference Guides** (10): API_REFERENCE.md, CLI_USER_GUIDE.md, etc.
2. **Quick Starts** (3): QUICKSTART.md, UNIFI_QUICKSTART.md
3. **Completion Reports** (32): PHASE*\*\_COMPLETE.md, TASK*\*\_COMPLETE.md
4. **Progress Tracking** (15): PHASE\__\_PROGRESS.md, _\_STATUS_REPORT.md
5. **Configuration** (5): CONFIGURATION.md, UDM_SETUP.md
6. **Development** (10): TESTING_GUIDE.md, TROUBLESHOOTING.md

### Organization Strategy

**Proposed Structure**:

```
docs/
├── README.md                    # Documentation index
├── guides/                      # User-facing guides
│   ├── QUICKSTART.md
│   ├── UNIFI_QUICKSTART.md
│   ├── CLI_USER_GUIDE.md
│   └── USAGE_GUIDE.md
├── reference/                   # Technical reference
│   ├── API_REFERENCE.md
│   ├── BACKEND_API_REFERENCE.md
│   └── UNIFI_CONTROLLER_API_REFERENCE.md
├── development/                 # Developer docs
│   ├── TESTING_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   └── LESSONS_LEARNED.md
└── archive/                     # Historical records
    ├── PHASE_*_COMPLETE.md
    ├── TASK_*_COMPLETE.md
    └── progress/
```

### Documentation Anti-Patterns

**Avoid**:

- ❌ Creating completion report for every small task
- ❌ Duplicating information across multiple files
- ❌ Leaving outdated docs in main directory
- ❌ Using overly generic names (SUMMARY.md, PROGRESS.md)

**Better**:

- ✅ Single project summary updated incrementally
- ✅ Living documents (ROADMAP.md, WHATS_NEXT.md)
- ✅ Archive completed phase/task reports
- ✅ Specific, searchable names (UNIFI_INTEGRATION_COMPLETE.md)

---

## Common Pitfalls

### 1. Assuming API Behavior

**Pitfall**: Assuming UniFi local controller works like cloud API.

**Reality**:

- Different authentication mechanisms
- Different endpoint structures
- Different data formats
- Different site handling

**Solution**: Always test with actual controller, read API responses carefully.

### 2. Database Connection Leaks

**Pitfall**: Not closing database connections properly.

**Solution**: Always use context managers or try/finally blocks:

```python
# Bad
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT * FROM devices")

# Good
with get_db_connection(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM devices")
    # Connection closed automatically
```

### 3. Hardcoding Configuration

**Pitfall**: Hardcoding URLs, credentials, paths in scripts.

**Solution**: Use `config.py` pattern:

```python
# config.py (not in git)
UNIFI_HOST = "192.168.1.1"
UNIFI_USERNAME = "admin"
UNIFI_PASSWORD = "secret"

# config.example.py (in git)
UNIFI_HOST = "192.168.1.1"  # Your UniFi controller IP
UNIFI_USERNAME = "admin"     # Your admin username
UNIFI_PASSWORD = ""          # Your password (fill in)
```

### 4. Ignoring Error Cases

**Pitfall**: Only testing happy path scenarios.

**Reality**: Networks fail, controllers restart, APIs change.

**Solution**: Test error scenarios:

- Controller unreachable
- Invalid credentials
- Empty device lists
- Malformed responses
- Database locks
- Disk full

### 5. Over-Engineering Early

**Pitfall**: Building complex abstractions before understanding the domain.

**Better Approach**:

1. Start simple - direct API calls
2. Identify patterns through use
3. Extract common code into utilities
4. Build abstractions based on real needs
5. Refactor incrementally

**Example Evolution**:

```python
# V1: Direct calls
response = requests.post(f"{base_url}/api/login", json={"username": user, "password": pwd})

# V2: Helper method
def login(base_url, username, password):
    return requests.post(f"{base_url}/api/login", json={"username": username, "password": password})

# V3: Class with session management
class UniFiClient:
    def login(self):
        # Reusable session, error handling, logging
        pass
```

---

## Success Patterns

### What Worked Well

1. **Incremental Testing**: Test each component before integration
2. **Real Data Early**: Used actual UniFi controller from start
3. **Comprehensive Logging**: Made debugging much easier
4. **Type Hints**: Caught many bugs before runtime
5. **Documentation**: Captured decisions and context as we went
6. **Repository Organization**: Clean structure improved productivity

### Metrics of Success

**Task 8 - Testing & Validation**:

- ✅ First collection: 2.93 seconds
- ✅ 6 devices collected successfully
- ✅ 38 clients stored correctly
- ✅ 267 metrics captured
- ✅ Zero errors in production run

**Code Quality**:

- ✅ 100% type hint coverage in `src/`
- ✅ All scripts follow consistent patterns
- ✅ Clean separation of concerns
- ✅ Production-ready error handling

**Documentation**:

- ✅ 92 documentation files
- ✅ Multiple quick-start guides
- ✅ Complete API reference
- ✅ This lessons learned document

---

## Recommendations for Future Projects

### Starting a New UniFi Integration

1. **Setup** (Day 1):

   - Get access to actual UniFi controller
   - Use UDM Pro or Cloud Key if possible
   - Create test site with known devices
   - Document controller version and firmware

2. **Development** (Week 1):

   - Start with simple API client (login, one endpoint)
   - Use `requests.Session()` from the beginning
   - Store raw API responses for reference
   - Build incrementally, test constantly

3. **Database** (Week 1-2):

   - Start with simple schema (MAC, name, JSON blob)
   - Add structure as you understand the data
   - Use SQLite for development (easy, portable)
   - Consider PostgreSQL for production scale

4. **Testing** (Ongoing):

   - Test with real controller daily
   - Keep test database separate
   - Save sample responses as fixtures
   - Test error conditions

5. **Organization** (Week 2+):
   - Keep root clean from day one
   - Use `scripts/` for utilities
   - Archive completed docs regularly
   - Update lessons learned weekly

### Tools and Libraries

**Essential**:

- `requests` - HTTP client with session support
- `sqlite3` - Built-in, perfect for development
- `pathlib` - Modern path handling
- `typing` - Type hints and mypy
- `pytest` - Testing framework

**Helpful**:

- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking
- `ipython` - Interactive debugging

**Avoid**:

- Complex ORMs for simple projects
- Heavy frameworks (Django, Flask) unless needed
- Unmaintained UniFi libraries (API changes often)

---

## Conclusion

This project demonstrated that careful planning, incremental development, and real-world testing lead to robust systems. The key is balancing:

- **Speed vs. Quality**: Move fast, but test thoroughly
- **Simplicity vs. Flexibility**: Start simple, add complexity when needed
- **Documentation vs. Development**: Document as you go, organize later
- **Abstraction vs. Directness**: Direct code first, patterns emerge naturally

The UniFi Network Monitor is now production-ready with:

- ✅ Comprehensive data collection
- ✅ Robust error handling
- ✅ Clean, organized codebase
- ✅ Extensive documentation
- ✅ Clear lessons for future development

**Total Development**: 8 Tasks over multiple sessions
**Final Status**: Production Ready 🎉
**Lines of Code**: ~15,000+ across all modules
**Test Coverage**: Core functionality fully tested

---

_For questions or clarifications about any lesson, see the related documentation in `docs/` or refer to specific completion reports in `docs/archive/`._

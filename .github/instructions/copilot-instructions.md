# GitHub Copilot Instructions for UniFi Network API Project

## Project Context

This is a comprehensive UniFi Network Controller monitoring and management system written in Python. The project provides:

- **Core API Client** - Clean, Pythonic interface for UniFi Network Controllers
- **Data Collection** - Automated polling and time-series data storage
- **Analytics Engine** - Statistical analysis, trend detection, anomaly detection
- **Alerting System** - Rule-based alerting with multi-channel notifications
- **Dashboard & Reports** - Terminal UI, HTML/PDF reports, data export

The system is designed for production use with full type safety, comprehensive testing, and extensive documentation.

**Current Status**: ✅ Production Ready (Task 8 Complete - October 2025)

- Successfully collecting from local UniFi Controller (UDM Pro)
- 6 devices, 38+ clients, 267 metrics per collection
- Collection time: ~3 seconds
- All 8 project tasks completed

## Repository Structure

```
network/
├── src/                        # Production source code
│   ├── api/                   # UniFi API client
│   ├── collector/             # Data collection
│   ├── database/              # Database and repositories
│   ├── analytics/             # Analytics engine
│   └── alerts/                # Alert system
├── scripts/                    # Utilities and testing (44 files)
│   ├── *.py                   # Database, collection, test scripts
│   ├── *.ps1                  # PowerShell automation
│   └── api_explorer.http      # REST API testing
├── docs/                       # Documentation (92 files)
│   ├── guides/                # User guides
│   ├── reference/             # Technical reference
│   ├── development/           # Developer docs
│   └── archive/               # Historical progress reports
├── data/                       # Database backups
├── config.py                   # Configuration (not in git)
├── config.example.py           # Configuration template
└── collect_unifi_data.py      # Main collection script
```

**Important**: Keep root directory minimal (≤10 files). Utilities go in `scripts/`, documentation in `docs/`.

## Code Style & Standards

### Python Standards

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write docstrings in Google style format
- Use f-strings for string formatting
- Prefer explicit over implicit (follow Zen of Python)
- Maximum line length: 100 characters

### Naming Conventions

- Classes: `PascalCase` (e.g., `UniFiClient`)
- Functions/methods: `snake_case` (e.g., `get_device_info`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT`)
- Private methods: prefix with `_` (e.g., `_make_request`)

### Error Handling

- Use specific exception types, not bare `except:`
- Create custom exceptions for API-specific errors
- Always include meaningful error messages
- Log errors appropriately with context

### Circular Import Prevention

**Critical Pattern**: Avoid circular imports using TYPE_CHECKING and lazy imports:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.alerts.engine import AlertEngine  # Type hints only
    from src.alerts.manager import AlertManager

# Lazy import in method
def get_engine(self) -> "AlertEngine":
    from src.alerts.engine import AlertEngine  # Import at runtime
    return AlertEngine()
```

**Rules**:

- Keep `__init__.py` minimal - avoid re-exporting classes
- Use TYPE_CHECKING for type hints only
- Implement lazy imports in methods that need dependencies
- Structure modules with clear dependency hierarchy

## API Client Development

### Request Handling

- All API requests should go through a centralized request method
- Implement proper authentication (login, session management, logout)
- Handle rate limiting gracefully
- Include retry logic with exponential backoff for transient failures
- Set appropriate timeouts (default: 30 seconds)

### Response Processing

- Validate response status codes
- Parse JSON responses safely with error handling
- Return clean, Pythonic data structures (dicts/lists, not raw JSON)
- Strip unnecessary metadata from responses when possible

### Authentication

- Support both traditional login and API token authentication
- Store credentials securely (never in code)
- Implement session reuse to minimize login requests
- Auto-refresh expired sessions when possible

## Testing & Examples

### Example Scripts

- Keep examples simple and focused on one task
- Include error handling in examples
- Add comments explaining UniFi-specific concepts
- Use config file for credentials (never hardcode)

### Documentation

- Document all public methods with docstrings
- Include parameter types and return types
- Provide usage examples in docstrings
- Keep API_REFERENCE.md updated with new endpoints

## UniFi-Specific Guidelines

### Authentication

**Local Controller Pattern**:

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

**Key Facts**:

- UniFi uses cookie-based sessions (not token auth)
- Sessions expire after ~24 hours of inactivity
- Must use `requests.Session()` to maintain cookies
- Local controllers have different auth than cloud API

### Common Endpoints

- `/api/self/sites` - List sites
- `/api/s/{site}/stat/device` - List devices
- `/api/s/{site}/stat/sta` - List clients (active only)
- `/api/s/{site}/rest/user` - Manage users
- `/api/s/{site}/cmd/devmgr` - Device commands

### Data Models

- Sites are identified by name or ID
- Devices have MAC addresses as primary identifiers
- Client data is ephemeral (only active/recently active clients)
- Settings are often nested in the `config` field
- MAC addresses: stored lowercase without colons for consistency
- Timestamps: UniFi uses Unix epoch, convert to ISO 8601 for storage

### API Quirks and Patterns

**Method Signatures**:

```python
# Local controller - no site parameter (uses 'default' internally)
def get_devices(self) -> list[dict]:
    return self._request("GET", "/api/s/default/stat/device")

# Cloud API - requires site parameter
def get_devices(self, site: str) -> list[dict]:
    return self._request("GET", f"/api/s/{site}/stat/device")
```

**Data Normalization**:

```python
# MAC addresses - normalize format
mac_raw = "12:34:56:78:9a:bc"  # From API
mac_normalized = mac_raw.replace(":", "").lower()  # For storage

# Timestamps - convert from Unix epoch
from datetime import datetime
timestamp_raw = 1729458000  # From API
timestamp_iso = datetime.fromtimestamp(timestamp_raw).isoformat()  # For DB
```

### Best Practices

- Always specify the site context for operations
- Use MAC addresses in lowercase without colons for consistency
- Cache site lists when making multiple calls
- Respect the controller's load (avoid rapid successive calls)
- Add 0.5-1 second delay between batch operations
- Test with actual controller responses, not mock data
- Client list only shows active/recent - offline clients won't appear

## Dependencies

- `requests` - HTTP client
- Keep dependencies minimal
- Pin major versions in requirements.txt

## Configuration

- Use `config.py` for user configuration (not in git)
- Provide `config.example.py` as template
- Support environment variables as alternative to config file
- Validate configuration on client initialization

## Script Path Resolution

**Standard Pattern** for scripts in `scripts/` directory:

```python
from pathlib import Path
import sys
import os

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Change to project root for relative paths (if needed)
os.chdir(Path(__file__).parent.parent)
```

**Rules**:

- All scripts in `scripts/` use `parent.parent` to reach project root
- Use `os.chdir()` when script needs relative file paths
- Test scripts from both root and subdirectories
- Document expected working directory in docstrings

## Database Best Practices

### Connection Management

**Always use context managers** to prevent database locks:

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

### Lock Prevention

- Close database viewers in VS Code before running scripts
- Use WAL mode for better concurrency: `PRAGMA journal_mode=WAL`
- Set busy timeout: `PRAGMA busy_timeout = 5000`
- Restart VS Code if database remains locked

## Common Patterns

### Making API Calls

```python
def get_something(self, site: str = "default") -> list[dict]:
    """Get something from the UniFi controller.

    Args:
        site: Site name (default: "default")

    Returns:
        List of items

    Raises:
        UniFiAPIError: If the API request fails
    """
    endpoint = f"/api/s/{site}/stat/something"
    response = self._request("GET", endpoint)
    return response.get("data", [])
```

### Error Handling

```python
try:
    result = client.some_operation()
except UniFiAuthError:
    # Handle authentication failures
    pass
except UniFiAPIError as e:
    # Handle API errors
    print(f"API error: {e}")
```

## Alert System Guidelines (Phase 4)

### Alert Rules

- Rules are defined with `AlertRule` dataclass (name, type, condition, threshold, severity)
- Support threshold rules (numeric comparisons) and status_change rules
- Always include cooldown periods to prevent alert spam
- Use severity levels: info, warning, critical

### Notification System

- All notifiers inherit from `BaseNotifier` abstract class
- Support multiple channels: Email (SMTP), Slack, Discord, generic webhooks
- Implement parallel delivery via `NotificationManager`
- Include severity filtering per channel (min_severity)
- Always validate notification configs in notifier constructors

### Alert Management

- Use `AlertManager` as the high-level API (coordinates engine + notifications)
- Support alert lifecycle: triggered → acknowledged → resolved
- Implement muting for maintenance windows (duration-based or indefinite)
- Track notification delivery status per alert
- Provide CLI commands for all operations

### Database Design

- Alert tables: `alert_rules`, `alert_history`, `notification_channels`, `alert_mutes`
- Use views for common queries (`v_active_alerts`, `v_recent_alerts_summary`)
- Implement triggers for automatic timestamp management
- Store notification configs as JSON in database
- Foreign key constraints with CASCADE for cleanup

### CLI Development

- Use argparse with subcommands for clear command structure
- Format output with emojis and tables for readability
- Include confirmation prompts for destructive operations
- Support --force flags to skip confirmations
- Provide detailed help text and examples

## When Suggesting Code

- Prioritize readability and maintainability
- Add type hints and docstrings
- Consider error cases
- Suggest logging for debugging
- Think about real-world UniFi API quirks and edge cases
- Provide complete, working examples when possible
- For alerts, always consider cooldown periods and notification routing

## Security Considerations

- Never log credentials or tokens
- Use HTTPS for all API calls
- Support SSL certificate verification (with option to disable for self-signed)
- Implement proper session cleanup
- Clear sensitive data from memory when done
- Store SMTP passwords in config files (not in code)
- Validate webhook URLs before use

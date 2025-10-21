# Scripts Directory

This directory contains utility and test scripts for the UniFi Network Monitor project.

## Running Scripts

All scripts should be run from the scripts directory:

```powershell
cd scripts
python script_name.py
```

Or from the project root:

```powershell
python scripts/script_name.py
```

Scripts automatically adjust their working directory to the project root and configure Python paths appropriately.

## Categories

### PowerShell Scripts

- **setup_collection.ps1** - Setup automated collection with Task Scheduler
- **show_status.ps1** - Show collection status and recent runs
- **create_task.ps1** - Create Windows scheduled task for collection
- **unifi-alerts.ps1** - Alert management PowerShell wrapper

### API Testing

- **api_explorer.http** - REST Client file for API exploration (use with VS Code REST Client extension)

### Database Utilities

- **create_fresh_db.py** - Create a fresh database with all schemas
- **setup_database.py** - Setup database with retry logic
- **setup_unifi_tables.py** - Setup only UniFi tables
- **check_metrics.py** - Check metrics in database
- **debug_hosts.py** - Debug host data

### Collection Scripts

- **collect_metrics.py** - Collect cloud API metrics
- **collect_real_metrics.py** - Collect real metrics with error handling
- **quick_collect.py** - Quick collection test
- **start_metrics_collection.py** - Start metrics collection daemon

### Testing Scripts

- **test_unifi_integration.py** - Full UniFi integration tests
- **test_unifi_collector.py** - Test UniFi collector service
- **test_unifi_repositories.py** - Test repository layer
- **test_unifi_models.py** - Test data models
- **test_complete_integration.py** - Complete end-to-end tests
- **test_quick_integration.py** - Quick integration tests
- **test_quick_collection.py** - Quick collection test with fresh DB
- **test_direct_collection.py** - Direct controller testing
- **test_collection_fresh_db.py** - Collection with fresh database
- **test_performance.py** - Performance benchmarking
- **test_error_handling.py** - Error handling tests
- **test_migration.py** - Database migration tests

### Controller Testing

- **quick_test_unifi.py** - Quick UniFi controller connection test
- **test_udm_login.py** - Test UDM login
- **test_browser_login.py** - Test browser-based login
- **test_all_login_paths.py** - Test all login methods
- **test_login_methods.py** - Various login method tests
- **test_credentials.py** - Credential validation
- **diagnose_unifi_site.py** - Diagnose UniFi site issues
- **find_unifi_port.py** - Find correct UniFi port
- **check_controller_type.py** - Check controller type

### Analytics & Demo

- **unifi_analytics_demo.py** - Analytics demonstration
- **test_analytics.py** - Analytics engine tests
- **test_analytics_simple.py** - Simple analytics tests
- **check_network_stats.py** - Check network statistics

### Data Generation

- **generate_sample_metrics.py** - Generate sample metrics for testing

## Standard Script Template

Scripts follow this standard pattern for imports and path setup:

```python
"""Script description"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os

# Change to project root directory
os.chdir(Path(__file__).parent.parent)

# Now import project modules
import config
from src.module import something

# Script code here...
```

This ensures:

- Scripts can import from `src/` package
- Relative paths like `config.py` and `network_monitor.db` work correctly
- Scripts work whether called from root or scripts directory

# UniFi Network API Client

A comprehensive Python client library for the UniFi Network Controller API with automated data collection, analytics, and monitoring capabilities.

## Project Status

✅ **Production Ready** (Task 8 Complete - October 2025)

All 8 project tasks completed:

- ✅ **Core API Client** - UniFi local controller integration
- ✅ **Data Collection** - Automated polling and storage
- ✅ **Analytics Engine** - Statistical analysis and health scoring
- ✅ **Alert System** - Rule-based alerting with multi-channel notifications
- ✅ **Testing & Validation** - Tested with real UniFi Controller (UDM Pro)

**Current Performance**:

- Collection: 6 devices, 38+ clients in ~3 seconds
- Metrics: 267 per collection cycle
- Success Rate: 100% in production testing

## Documentation

📚 **[Complete Documentation Index](docs/README.md)** - All 92 documentation files organized

**Quick Links**:

- 🚀 [UniFi Quick Start](docs/guides/UNIFI_QUICKSTART.md) - Get started with local controller
- 📖 [Project Summary](docs/PROJECT_SUMMARY.md) - Complete project overview
- 💡 [Lessons Learned](docs/development/LESSONS_LEARNED.md) - Key insights and best practices
- 🔧 [Troubleshooting](docs/development/TROUBLESHOOTING.md) - Common issues and solutions
- 📘 [API Reference](docs/reference/API_REFERENCE.md) - Complete API documentation
- 🎯 [Roadmap](docs/ROADMAP.md) - Future plans and enhancements

## Key Features

### Core Infrastructure

- **UniFi Controller Integration** - Local controller support (UDM Pro, Cloud Key, software)
- **Data Collector** - Automated polling with daemon mode (sub-3-second collection)
- **Database Layer** - SQLite storage with 12 tables, 6 views, comprehensive indexing
- **Event System** - Automatic change detection and event generation
- **Metrics Collection** - Time-series data (performance, status, network stats)

### Analytics & Monitoring

- **Analytics Engine** - Statistical analysis, trend detection, anomaly detection
- **Health Scoring** - Device and network health metrics
- **Report Generation** - HTML/PDF reports with export capabilities
- **Data Export** - CSV, JSON formats for external integrations

### Alerting & Notifications

- **Alert Rules** - Threshold and status-change based alerting
- **Multi-Channel Notifications** - Email (SMTP), Slack, Discord, webhooks
- **Alert Management** - Lifecycle tracking (triggered → acknowledged → resolved)
- **CLI Tool** - Comprehensive command-line interface
- **Smart Filtering** - Cooldown periods, severity levels, muting

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd network

# Install dependencies
pip install -r requirements.txt

# Create configuration file
cp config.example.py config.py
# Edit config.py with your UniFi credentials
```

### Database Setup

```bash
# Create fresh database with all tables
python scripts/create_fresh_db.py
```

### Basic Usage

#### 1. Collect UniFi data (recommended)

```bash
# Run collection once
python collect_unifi_data.py --verbose

# Run continuously (daemon mode, polls every 5 minutes)
python collect_unifi_data.py --daemon --interval 300
```

#### 2. View analytics

```bash
python scripts/unifi_analytics_demo.py
```

#### 3. Test controller connection

```bash
python scripts/quick_test_unifi.py
```

### Legacy Cloud API Usage

#### 1. List all devices

```bash
python examples/list_hosts.py
```

#### 2. Get detailed device information

```bash
python examples/get_device_info.py
```

#### 3. Start the data collector (daemon mode)

```bash
# Run once
python examples/run_collector.py --once

# Run continuously (polls every 60 seconds)
python examples/run_collector.py --daemon --interval 60
```

#### 4. View analytics dashboard

```bash
# Show once
python examples/dashboard_rich.py --once

# Live mode with auto-refresh
python examples/dashboard_rich.py --refresh 30
```

#### 5. Manage alerts with CLI

```bash
# Set environment (Windows PowerShell)
$env:PYTHONPATH="C:\git\network\src"

# Create an alert rule
python -m alerts.cli rule create --name "High CPU" --type threshold \
  --metric cpu_usage --condition gt --threshold 85 \
  --severity warning --channels email-1

# List alert rules
python -m alerts.cli rule list

# View alert statistics
python -m alerts.cli alert stats

# List notification channels
python -m alerts.cli channel list
```

See [docs/CLI_USER_GUIDE.md](docs/CLI_USER_GUIDE.md) for complete CLI documentation.

## Utility Scripts

All utility and test scripts are located in the `scripts/` directory. See [scripts/README.md](scripts/README.md) for a complete list and documentation.

## Analytics Features

The analytics engine provides comprehensive insights into your network:

- **Statistics**: Mean, median, min, max, std dev for any metric
- **Trend Detection**: Linear regression analysis to detect upward/downward trends
- **Anomaly Detection**: Z-score based outlier detection
- **Capacity Forecasting**: Predict when resources will reach capacity
- **Health Scores**: Weighted scoring based on multiple metrics
- **Network Summary**: Overall network status and statistics

See [docs/PHASE_3_PROGRESS.md](docs/PHASE_3_PROGRESS.md) for detailed analytics documentation.

## Dashboard

The enhanced dashboard provides a beautiful terminal UI with:

- **Device Status Table**: Real-time device health, CPU trends, and status
- **Network Summary**: Total devices, active/offline counts, recent events
- **Events Panel**: Last 10 events with timestamps and descriptions
- **Alerts Panel**: Critical warnings for anomalies and capacity issues
- **Live Mode**: Auto-refresh with configurable intervals

See [docs/ENHANCED_DASHBOARD.md](docs/ENHANCED_DASHBOARD.md) for complete dashboard documentation.

## Repository Structure

```
network/
├── collect_unifi_data.py      # Main collection script
├── config.py                   # Configuration (create from config.example.py)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── network_monitor.db          # Active database
│
├── src/                        # Source code
│   ├── unifi_controller.py     # UniFi Controller API client
│   ├── collector/              # Data collection services
│   ├── database/               # Database layer (models, repositories, schemas)
│   ├── analytics/              # Analytics engine
│   └── alerts/                 # Alert system
│
├── scripts/                    # Utility & test scripts
│   ├── README.md               # Script documentation
│   ├── *.py                    # Python utilities (40 scripts)
│   ├── *.ps1                   # PowerShell automation (4 scripts)
│   └── api_explorer.http       # REST Client API testing
│
├── docs/                       # Documentation (92 files)
│   ├── QUICKSTART.md           # Cloud API quick start
│   ├── UNIFI_QUICKSTART.md     # UniFi local controller quick start
│   ├── ROADMAP.md              # Project roadmap
│   └── *.md                    # Detailed guides and references
│
├── data/                       # Data storage & backups
│   ├── *.db                    # Database backups
│   └── hosts_list.json         # Cached host data
│
├── examples/                   # Example scripts
├── tests/                      # Test suite
├── exports/                    # Generated exports
└── reports/                    # Generated reports
```

## Documentation

### Getting Started

- [Quick Start Guide](docs/QUICKSTART.md) - Get up and running quickly
- [Features](docs/FEATURES.md) - Detailed feature descriptions
- [Usage Guide](docs/USAGE_GUIDE.md) - Common usage patterns

### API & Reference

- [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- [Configuration Guide](docs/CONFIGURATION.md) - System configuration

### Analytics & Monitoring

- [Enhanced Dashboard](docs/ENHANCED_DASHBOARD.md) - Dashboard usage guide
- [Report Generation](docs/REPORT_GENERATION.md) - Creating reports
- [Data Export](docs/DATA_EXPORT.md) - Exporting data

### Alerting System (NEW!)

- [Alert System Quick Reference](docs/ALERT_SYSTEM_QUICKREF.md) - Quick start & examples
- [CLI User Guide](docs/CLI_USER_GUIDE.md) - Command-line interface documentation
- [Phase 4 Progress](docs/PHASE_4_PROGRESS.md) - Alert system implementation details

## Project Structure

```text
network/
├── src/
│   ├── unifi_client.py          # Core API client
│   ├── database/                # Database layer
│   │   ├── models.py            # Data models
│   │   ├── database.py          # Database connection
│   │   ├── schema.sql           # Core schema
│   │   ├── schema_alerts.sql    # Alert system schema
│   │   └── repositories/        # Data access layer (8 repositories)
│   ├── collector/               # Data collection service
│   │   ├── data_collector.py   # Automated polling
│   │   └── scheduler.py         # Job scheduling
│   ├── analytics/               # Analytics engine
│   │   └── analytics_engine.py  # Statistics, trends, forecasting
│   ├── alerts/                  # Alert system (NEW!)
│   │   ├── models.py            # Alert models
│   │   ├── alert_engine.py      # Rule evaluation
│   │   ├── alert_manager.py     # High-level API
│   │   ├── notification_manager.py  # Notification routing
│   │   ├── cli.py               # Command-line interface
│   │   └── notifiers/           # Notification plugins
│   │       ├── base.py          # Base notifier
│   │       ├── email.py         # SMTP email
│   │       └── webhook.py       # Slack/Discord/webhooks
│   ├── reports/                 # Report generation
│   │   └── report_generator.py  # HTML/PDF reports
│   └── export/                  # Data export
│       └── data_exporter.py     # CSV/JSON/Prometheus
├── examples/
│   ├── list_hosts.py            # List all devices
│   ├── get_device_info.py       # Get device details
│   ├── run_collector.py         # Run data collector
│   ├── dashboard_rich.py        # Enhanced dashboard
│   ├── test_analytics.py        # Analytics examples
│   └── test_alert_*.py          # Alert system tests
├── docs/                        # Comprehensive documentation
├── tests/                       # Test suite (100% alert coverage)
└── config.example.py            # Configuration template
```

## Development

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_unifi_client.py

# Run with verbose output
pytest -v
```

### Test Coverage

Current coverage: **72%** (54 passing tests)

- Core API client: Comprehensive coverage
- Database models: Full coverage
- Repositories: High coverage
- Analytics: Tested with live data

## Requirements

- Python 3.7+
- requests >= 2.25.0
- python-dotenv >= 0.19.0
- sqlalchemy >= 1.4.0
- rich >= 13.0.0 (for enhanced dashboard)

Development dependencies:

- pytest >= 7.0.0
- pytest-cov >= 3.0.0
- pytest-mock >= 3.6.0
- responses >= 0.20.0

## Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Write docstrings in Google style
4. Include unit tests for new features
5. Update documentation as needed

See [.github/instructions/copilot-instructions.md](.github/instructions/copilot-instructions.md) for detailed coding standards.

## License

[Add your license here]

## Roadmap

### Phase 1: Foundation & Core API ✅

- UniFi Site Manager API client
- Authentication and session management
- Comprehensive test suite

### Phase 2: Data Storage & Persistence ✅

- SQLite database with 6 tables
- Automated data collector
- Event detection system
- Time-series metrics

### Phase 3: Analytics & Visualization ✅

- ✅ Analytics engine (statistics, trends, anomalies, forecasting)
- ✅ Enhanced dashboard with rich terminal UI
- ✅ Report generation (daily/weekly/monthly)
- ✅ Data export (CSV, JSON, Prometheus)

### Phase 4: Alerting & Notifications 🚀 (95% Complete)

- ✅ Alert rules engine (threshold, status-change)
- ✅ Multi-channel notifications (Email, Slack, Discord, webhooks)
- ✅ Alert management API (acknowledge, resolve, mute)
- ✅ Command-line interface (900+ lines)
- ✅ Database schema with views and triggers
- ⏳ Integration tests
- ⏳ Final documentation

### Phase 5: Advanced Features (Planned)

- Web-based dashboard
- Multi-site support
- Historical data analysis
- Performance optimization
- Advanced alert correlation

## Support

For questions or issues:

1. Check the [documentation](docs/)
2. Review [existing issues](issues/)
3. Create a new issue with details

---

**Made with ❤️ for UniFi network management**

# UniFi Network API Client

A comprehensive Python client library for the UniFi Site Manager API with automated data collection, analytics, and monitoring capabilities.

## Project Status

- ✅ **Phase 1: Core API Client** - Complete (72% test coverage, 54 passing tests)
- ✅ **Phase 2: Data Storage & Persistence** - Complete (~2,500 lines of code)
- ✅ **Phase 3: Analytics & Visualization** - **COMPLETE!** (~4,440 lines of code)
  - ✅ Analytics Engine - Complete
  - ✅ Enhanced Dashboard - Complete
  - ✅ Report Generation - Complete
  - ✅ Data Export - Complete

## Key Features

- **API Client** - Full UniFi Site Manager API integration with retry logic and error handling
- **Data Collector** - Automated polling service with daemon mode and graceful shutdown
- **Database Layer** - SQLite storage with 6 tables, 3 views, 12 indexes
- **Event System** - Change detection with automatic event generation
- **Metrics Collection** - Time-series data (CPU, memory, temperature, uptime)
- **Analytics Engine** - Statistical analysis, trend detection, anomaly detection, capacity forecasting
- **Enhanced Dashboard** - Beautiful terminal UI with health scores, trends, and alerts
- **Report Generation** - HTML/PDF reports with email delivery (daily/weekly/monthly)
- **Data Export** - CSV, JSON, and Prometheus metrics for external integrations

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

### Basic Usage

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

## Documentation

- [Quick Start Guide](docs/QUICKSTART.md) - Get up and running quickly
- [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- [Features](docs/FEATURES.md) - Detailed feature descriptions
- [Phase 3 Progress](docs/PHASE_3_PROGRESS.md) - Analytics & visualization implementation
- [Enhanced Dashboard](docs/ENHANCED_DASHBOARD.md) - Dashboard usage guide

## Project Structure

```
network/
├── src/
│   ├── unifi_client.py          # Core API client
│   ├── database/                # Database layer
│   │   ├── models/              # SQLAlchemy models
│   │   ├── repositories/        # Data access layer
│   │   └── schema.py            # Database schema
│   ├── collector/               # Data collection service
│   │   └── data_collector.py   # Automated polling
│   └── analytics/               # Analytics engine
│       └── analytics_engine.py  # Statistics, trends, forecasting
├── examples/
│   ├── list_hosts.py            # List all devices
│   ├── get_device_info.py       # Get device details
│   ├── run_collector.py         # Run data collector
│   ├── dashboard_rich.py        # Enhanced dashboard
│   └── test_analytics.py        # Analytics examples
├── docs/                        # Documentation
├── tests/                       # Test suite (72% coverage)
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

### Phase 3: Analytics & Visualization 🔄

- ✅ Analytics engine (statistics, trends, anomalies, forecasting)
- ✅ Enhanced dashboard with rich terminal UI
- ⏳ Report generation (daily/weekly/monthly)
- ⏳ Data export (CSV, JSON, Prometheus)

### Phase 4: Advanced Features (Planned)

- Web-based dashboard
- Alerting system with notifications
- Multi-site support
- Historical data analysis
- Performance optimization

## Support

For questions or issues:

1. Check the [documentation](docs/)
2. Review [existing issues](issues/)
3. Create a new issue with details

---

**Made with ❤️ for UniFi network management**

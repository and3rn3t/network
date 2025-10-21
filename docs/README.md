# Documentation Index

**UniFi Network Monitor** - Complete documentation for the UniFi Network Controller monitoring and management system.

**Last Updated**: October 20, 2025
**Project Status**: ✅ Production Ready (Task 8 Complete)

---

## Quick Access

### For New Users

- **[Quick Start Guide](guides/QUICKSTART.md)** - Get started with the system
- **[UniFi Quick Start](guides/UNIFI_QUICKSTART.md)** - Set up with local UniFi controller
- **[UDM Setup Guide](guides/UDM_SETUP.md)** - UniFi Dream Machine specific setup

### For Developers

- **[Lessons Learned](development/LESSONS_LEARNED.md)** - Key insights and best practices
- **[Testing Guide](development/TESTING_GUIDE.md)** - How to run tests
- **[Troubleshooting](development/TROUBLESHOOTING.md)** - Common issues and solutions

### For System Operators

- **[CLI User Guide](guides/CLI_USER_GUIDE.md)** - Command-line interface reference
- **[Analytics Guide](guides/UNIFI_ANALYTICS_GUIDE.md)** - Using the analytics engine
- **[Configuration Reference](reference/CONFIGURATION.md)** - All configuration options

---

## Documentation Structure

### 📖 User Guides (`guides/`)

Documentation for end users and system operators.

| Document                                                    | Description                       |
| ----------------------------------------------------------- | --------------------------------- |
| [QUICKSTART.md](guides/QUICKSTART.md)                       | General quick start guide         |
| [UNIFI_QUICKSTART.md](guides/UNIFI_QUICKSTART.md)           | UniFi local controller setup      |
| [UDM_SETUP.md](guides/UDM_SETUP.md)                         | UniFi Dream Machine configuration |
| [CLI_USER_GUIDE.md](guides/CLI_USER_GUIDE.md)               | Command-line interface guide      |
| [USAGE_GUIDE.md](guides/USAGE_GUIDE.md)                     | General usage patterns            |
| [UNIFI_ANALYTICS_GUIDE.md](guides/UNIFI_ANALYTICS_GUIDE.md) | Analytics engine features         |
| [API_KEY_SETUP.md](guides/API_KEY_SETUP.md)                 | API key configuration             |

### 📚 Technical Reference (`reference/`)

Detailed technical documentation and API references.

| Document                                                                         | Description              |
| -------------------------------------------------------------------------------- | ------------------------ |
| [API_REFERENCE.md](reference/API_REFERENCE.md)                                   | Python API reference     |
| [BACKEND_API_REFERENCE.md](reference/BACKEND_API_REFERENCE.md)                   | Backend API endpoints    |
| [UNIFI_CONTROLLER_API_REFERENCE.md](reference/UNIFI_CONTROLLER_API_REFERENCE.md) | UniFi Controller API     |
| [WEBSOCKET_QUICK_REFERENCE.md](reference/WEBSOCKET_QUICK_REFERENCE.md)           | WebSocket API reference  |
| [AUTH_QUICK_REFERENCE.md](reference/AUTH_QUICK_REFERENCE.md)                     | Authentication guide     |
| [ALERT_SYSTEM_QUICKREF.md](reference/ALERT_SYSTEM_QUICKREF.md)                   | Alert system reference   |
| [CONFIGURATION.md](reference/CONFIGURATION.md)                                   | Configuration options    |
| [DATA_EXPORT.md](reference/DATA_EXPORT.md)                                       | Data export formats      |
| [REPORT_GENERATION.md](reference/REPORT_GENERATION.md)                           | Report generation        |
| [DEVICE_CLIENT_MANAGEMENT.md](reference/DEVICE_CLIENT_MANAGEMENT.md)             | Device/client management |
| [UNIFI_CONTROLLER_CONFIGURATION.md](reference/UNIFI_CONTROLLER_CONFIGURATION.md) | Controller configuration |

### 🔧 Development (`development/`)

Information for developers working on the project.

| Document                                                 | Description                         |
| -------------------------------------------------------- | ----------------------------------- |
| [LESSONS_LEARNED.md](development/LESSONS_LEARNED.md)     | **Key insights and best practices** |
| [TESTING_GUIDE.md](development/TESTING_GUIDE.md)         | Testing strategies and examples     |
| [TROUBLESHOOTING.md](development/TROUBLESHOOTING.md)     | Common issues and solutions         |
| [FEATURES.md](development/FEATURES.md)                   | Feature descriptions                |
| [FRONTEND_STRATEGY.md](development/FRONTEND_STRATEGY.md) | Frontend development approach       |

### 📦 Archive (`archive/`)

Historical documentation and progress reports.

#### Phase Completion Reports (`archive/phases/`)

- PHASE_1_COMPLETE.md - Initial setup and API client
- PHASE_2_COMPLETE.md - Data collection
- PHASE_3_COMPLETE.md - Analytics engine
- PHASE_4_COMPLETE.md - Alert system
- PHASE*5*\*.md - UI and dashboard development

#### Task Completion Reports (`archive/tasks/`)

- TASK*6*\*.md - Collection implementation
- TASK*7*\*.md - Analytics implementation
- TASK*8*\*.md - Testing and validation
- TASK*9*\*.md - Additional features

#### Other Historical Documents (`archive/`)

- Completion reports (\*\_COMPLETE.md)
- Progress tracking (_\_PROGRESS.md,_\_STATUS_REPORT.md)
- Testing reports (\*\_RESULTS.md, **TESTING**.md)
- Integration summaries (**INTEGRATION**.md)
- Session notes (SESSION\_\*.md)

---

## Project Overview Documents

Located in the docs root:

| Document                                 | Description                      |
| ---------------------------------------- | -------------------------------- |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Overall project summary          |
| [ROADMAP.md](ROADMAP.md)                 | Project roadmap and future plans |
| [WHATS_NEXT.md](WHATS_NEXT.md)           | Upcoming features and priorities |

---

## Quick Reference

### Common Tasks

**Getting Started**:

1. Read [UNIFI_QUICKSTART.md](guides/UNIFI_QUICKSTART.md)
2. Configure using [CONFIGURATION.md](reference/CONFIGURATION.md)
3. Start collecting: `python collect_unifi_data.py`

**Development**:

1. Review [LESSONS_LEARNED.md](development/LESSONS_LEARNED.md)
2. Set up testing: [TESTING_GUIDE.md](development/TESTING_GUIDE.md)
3. Check scripts: `scripts/README.md` (in project root)

**Troubleshooting**:

1. Check [TROUBLESHOOTING.md](development/TROUBLESHOOTING.md)
2. Review error logs in collection output
3. Test connection: `python scripts/diagnose_unifi_site.py`

### System Architecture

```
┌─────────────────────────────────────────────────────┐
│                UniFi Network Monitor                 │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────┐      ┌──────────────────────┐    │
│  │ UniFi API    │─────▶│ Data Collector       │    │
│  │ Client       │      │ (collect_unifi_data) │    │
│  └──────────────┘      └──────────────────────┘    │
│         │                        │                   │
│         ▼                        ▼                   │
│  ┌──────────────────────────────────────────┐      │
│  │        SQLite Database                    │      │
│  │  - Devices, Clients, Metrics              │      │
│  │  - Events, Status, Time Series            │      │
│  └──────────────────────────────────────────┘      │
│         │                                            │
│         ▼                                            │
│  ┌──────────────┐      ┌──────────────────────┐    │
│  │ Analytics    │      │ Alert System         │    │
│  │ Engine       │      │ (Rules & Notify)     │    │
│  └──────────────┘      └──────────────────────┘    │
│         │                        │                   │
│         ▼                        ▼                   │
│  ┌──────────────────────────────────────────┐      │
│  │  Reports, Dashboards, Exports             │      │
│  └──────────────────────────────────────────┘      │
│                                                       │
└─────────────────────────────────────────────────────┘
```

### Key Features

- **Real-time Collection**: 6 devices, 38+ clients, ~3 second collection time
- **Time-series Storage**: 267+ metrics per collection cycle
- **Analytics Engine**: Trend detection, anomaly detection, health scores
- **Alert System**: Rule-based alerts with multi-channel notifications
- **Flexible Reporting**: Terminal UI, HTML/PDF, CSV/JSON export

---

## Documentation Guidelines

### For Contributors

When adding documentation:

1. **User Guides** → `guides/` - End-user focused, how-to format
2. **Technical Reference** → `reference/` - API docs, configuration, schemas
3. **Development Docs** → `development/` - For developers, testing, troubleshooting
4. **Completion Reports** → `archive/` - Historical progress tracking

### Documentation Standards

- Use Markdown format
- Include table of contents for long documents (> 100 lines)
- Add "Last Updated" date at top
- Use code blocks with language specifiers
- Link to related documents
- Keep line length ≤ 100 characters (where practical)

---

## Support

- **Issues**: Document problems in [TROUBLESHOOTING.md](development/TROUBLESHOOTING.md)
- **Development**: Follow patterns in [LESSONS_LEARNED.md](development/LESSONS_LEARNED.md)
- **Questions**: Check relevant reference docs or guides

---

_This documentation structure was established in Task 8 (October 2025) to organize 92 documentation files into a logical, maintainable structure._

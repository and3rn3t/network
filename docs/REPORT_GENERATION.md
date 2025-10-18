# Report Generation Documentation

## Overview

The UniFi Network Monitoring System includes comprehensive report generation capabilities. Generate professional HTML and PDF reports with network statistics, device details, events, and analytics insights.

## Features

- **Multiple Report Types**: Daily, weekly, and monthly reports
- **Rich HTML Reports**: Beautiful, responsive HTML with CSS styling
- **PDF Export**: Convert reports to PDF format (requires weasyprint)
- **Email Delivery**: Automatically send reports via SMTP
- **Comprehensive Data**: Device status, events, metrics, and analytics
- **Customizable**: Configure what data to include

## Installation

### Basic Installation

```bash
# Report generation works out of the box with HTML only
pip install -r requirements.txt
```

### PDF Support (Optional)

For PDF report generation, install weasyprint:

```bash
pip install weasyprint
```

**Note**: weasyprint has system dependencies. See [Installation Guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation) for platform-specific instructions.

## Quick Start

### Generate a Daily Report

```bash
python examples/generate_report.py --type daily
```

This creates an HTML report in the `reports/` directory.

### Generate Weekly Report with PDF

```bash
python examples/generate_report.py --type weekly --pdf
```

### Send Monthly Report via Email

```bash
python examples/generate_report.py --type monthly --email
```

## Report Types

### Daily Report

- **Time Range**: Last 24 hours
- **Use Case**: Daily monitoring and quick status checks
- **Best For**: Identifying recent issues and changes

### Weekly Report

- **Time Range**: Last 7 days
- **Use Case**: Weekly summaries and trend analysis
- **Best For**: Management updates and trend identification

### Monthly Report

- **Time Range**: Last 30 days
- **Use Case**: Long-term analysis and capacity planning
- **Best For**: Monthly reviews and strategic planning

## Report Sections

Every report includes the following sections:

### 1. Executive Summary

- Total device count
- Active vs. offline devices
- Event count for the period
- Average network health score

### 2. Device Details

- Device name and model
- MAC address
- Online/offline status
- Health score (0-100)
- Last seen timestamp

### 3. Recent Events

- Event timestamp
- Event type (status_change, metric_threshold, etc.)
- Severity level
- Description

### 4. Metrics Summary

- Total data points collected
- Statistics for each metric type:
  - Count, mean, median
  - Min, max, standard deviation
- Available metrics: CPU, memory, temperature, uptime

### 5. Analytics & Insights

- Network overview
- Per-host analysis:
  - Health scores
  - Trend indicators
  - Detected anomalies
- Capacity planning forecasts

## Configuration

### Basic Configuration

Create a `config.py` file with report settings:

```python
# Email Configuration (for report delivery)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
EMAIL_FROM = "monitoring@example.com"
EMAIL_TO = ["admin@example.com", "team@example.com"]

# Report Configuration
REPORT_OUTPUT_DIR = "reports"
ENABLE_PDF_REPORTS = True
```

### Programmatic Configuration

```python
from src.reports import ReportGenerator, ReportConfig, ReportType

config = ReportConfig(
    report_type=ReportType.WEEKLY,
    database_path="network.db",

    # Email settings
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_username="user@gmail.com",
    smtp_password="password",
    email_from="monitoring@example.com",
    email_to=["admin@example.com"],

    # PDF settings
    enable_pdf=True,
    pdf_output_dir="reports",

    # Content settings
    include_device_details=True,
    include_metrics=True,
    include_events=True,
    include_analytics=True,
)

generator = ReportGenerator(config)
```

## Usage Examples

### Example 1: Generate HTML Report

```python
from src.reports import ReportGenerator, ReportConfig, ReportType

config = ReportConfig(
    report_type=ReportType.DAILY,
    database_path="network.db",
    enable_pdf=False,
)

generator = ReportGenerator(config)
html_path = generator.generate_and_save_report()
print(f"Report saved to: {html_path}")
```

### Example 2: Generate PDF Report

```python
from src.reports import ReportGenerator, ReportConfig, ReportType

config = ReportConfig(
    report_type=ReportType.WEEKLY,
    database_path="network.db",
    enable_pdf=True,
    pdf_output_dir="reports/pdf",
)

generator = ReportGenerator(config)
html_path = generator.generate_and_save_report()
# PDF is automatically generated alongside HTML
```

### Example 3: Send Report via Email

```python
from src.reports import ReportGenerator, ReportConfig, ReportType

config = ReportConfig(
    report_type=ReportType.MONTHLY,
    database_path="network.db",
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_username="user@gmail.com",
    smtp_password="app-password",
    email_from="monitoring@example.com",
    email_to=["admin@example.com"],
)

generator = ReportGenerator(config)
success = generator.generate_and_email_report(
    subject="Monthly Network Report - October 2025"
)

if success:
    print("Report sent successfully!")
```

### Example 4: Custom Date Range

```python
from datetime import datetime, timedelta
from src.reports import ReportGenerator, ReportConfig, ReportType

config = ReportConfig(
    report_type=ReportType.DAILY,
    database_path="network.db",
)

generator = ReportGenerator(config)

# Generate report for specific date range
end_date = datetime(2025, 10, 15)
start_date = end_date - timedelta(days=7)

report_data = generator.generate_report(
    start_date=start_date,
    end_date=end_date
)
```

### Example 5: Minimal Report

```python
from src.reports import ReportGenerator, ReportConfig, ReportType

config = ReportConfig(
    report_type=ReportType.DAILY,
    database_path="network.db",
    include_device_details=False,  # Exclude device table
    include_metrics=False,          # Exclude metrics
    include_events=True,            # Include events only
    include_analytics=False,        # Exclude analytics
)

generator = ReportGenerator(config)
html_path = generator.generate_and_save_report()
```

## Email Setup

### Gmail Setup

1. Enable 2-factor authentication in Google Account
2. Generate an app-specific password:
   - Go to Google Account Settings → Security
   - Select "2-Step Verification"
   - Scroll to "App passwords"
   - Generate password for "Mail"
3. Use the generated password in `SMTP_PASSWORD`

```python
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-16-char-app-password"
```

### Other Email Providers

#### Outlook/Office 365

```python
SMTP_HOST = "smtp.office365.com"
SMTP_PORT = 587
```

#### Yahoo Mail

```python
SMTP_HOST = "smtp.mail.yahoo.com"
SMTP_PORT = 587
```

#### Custom SMTP Server

```python
SMTP_HOST = "mail.yourdomain.com"
SMTP_PORT = 587  # or 465 for SSL
```

## Automation

### Schedule with Cron (Linux/Mac)

```bash
# Daily report at 8 AM
0 8 * * * cd /path/to/network && python examples/generate_report.py --type daily --email

# Weekly report on Monday at 9 AM
0 9 * * 1 cd /path/to/network && python examples/generate_report.py --type weekly --email

# Monthly report on 1st at 10 AM
0 10 1 * * cd /path/to/network && python examples/generate_report.py --type monthly --email --pdf
```

### Schedule with Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily/weekly/monthly)
4. Action: Start a program
5. Program: `python`
6. Arguments: `C:\path\to\network\examples\generate_report.py --type daily --email`
7. Start in: `C:\path\to\network`

### Schedule with Python

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from src.reports import ReportGenerator, ReportConfig, ReportType

def generate_daily_report():
    config = ReportConfig(
        report_type=ReportType.DAILY,
        database_path="network.db",
        # ... email config ...
    )
    generator = ReportGenerator(config)
    generator.generate_and_email_report()

scheduler = BlockingScheduler()

# Daily at 8 AM
scheduler.add_job(generate_daily_report, 'cron', hour=8)

# Weekly on Monday at 9 AM
scheduler.add_job(generate_weekly_report, 'cron', day_of_week='mon', hour=9)

scheduler.start()
```

## Troubleshooting

### PDF Generation Fails

**Error**: `ImportError: No module named 'weasyprint'`

**Solution**: Install weasyprint:

```bash
pip install weasyprint
```

**Error**: `OSError: cannot load library`

**Solution**: Install system dependencies. See [weasyprint docs](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation).

### Email Sending Fails

**Error**: `smtplib.SMTPAuthenticationError: Username and Password not accepted`

**Solutions**:

- Verify username and password
- For Gmail: Use app-specific password, not account password
- Check SMTP host and port settings
- Ensure "Less secure app access" is enabled (if applicable)

**Error**: `smtplib.SMTPServerDisconnected: Connection unexpectedly closed`

**Solutions**:

- Check firewall settings
- Try different port (587 for TLS, 465 for SSL)
- Verify SMTP server address

### Empty Reports

**Issue**: Report shows no data

**Solutions**:

- Verify database path is correct
- Ensure data collector has run
- Check database has data: `sqlite3 network.db "SELECT COUNT(*) FROM hosts;"`
- Verify date range includes data

### Report Format Issues

**Issue**: HTML not rendering properly

**Solutions**:

- Open in modern browser (Chrome, Firefox, Edge)
- Check file encoding (should be UTF-8)
- Verify HTML file is complete (check file size)

## API Reference

### ReportConfig

```python
@dataclass
class ReportConfig:
    report_type: ReportType          # DAILY, WEEKLY, or MONTHLY
    database_path: str = "network.db"

    # Email settings (optional)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: Optional[str] = None
    email_to: Optional[List[str]] = None

    # PDF settings
    enable_pdf: bool = True
    pdf_output_dir: str = "reports"

    # Report content settings
    include_device_details: bool = True
    include_metrics: bool = True
    include_events: bool = True
    include_analytics: bool = True
```

### ReportGenerator Methods

#### `__init__(config: ReportConfig)`

Initialize report generator with configuration.

#### `generate_report(start_date=None, end_date=None) -> Dict[str, Any]`

Generate report data as dictionary.

**Returns**: Dictionary with sections: metadata, summary, devices, events, metrics, analytics

#### `generate_and_save_report(output_filename=None) -> str`

Generate and save report as HTML (and PDF if enabled).

**Returns**: Path to generated HTML file

#### `generate_and_email_report(subject=None) -> bool`

Generate report and send via email.

**Returns**: True if email sent successfully, False otherwise

## Best Practices

1. **Schedule Regular Reports**: Set up automated daily/weekly/monthly reports
2. **Use Email Wisely**: Don't spam - weekly/monthly emails are usually sufficient
3. **Archive Reports**: Keep historical reports for trend analysis
4. **Customize Content**: Disable sections you don't need to reduce report size
5. **Test Email First**: Send test report before scheduling automated delivery
6. **Secure Credentials**: Never commit config.py with real credentials
7. **Monitor Disk Space**: PDF reports can be large - implement cleanup policy

## Performance

### Report Generation Time

- **Daily report**: < 1 second (100 devices, 1,000 events)
- **Weekly report**: 1-2 seconds (100 devices, 10,000 events)
- **Monthly report**: 2-5 seconds (100 devices, 50,000 events)

### File Sizes

- **HTML only**: 50-200 KB
- **With PDF**: 200-500 KB (PDF is larger)

### Optimization Tips

- Use `include_*` flags to disable unused sections
- Limit event history shown (currently 50 most recent)
- Archive old reports regularly
- Use HTML for daily reports, PDF for weekly/monthly only

## Support

For questions or issues:

1. Check this documentation
2. Review example scripts in `examples/`
3. Check [GitHub Issues](https://github.com/your-repo/issues)
4. Create new issue with report sample (redact sensitive data)

---

**Last Updated**: October 17, 2025
**Version**: 1.0.0

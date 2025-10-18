"""UniFi Network API Configuration Example.

Copy this file to config.py and fill in your actual credentials.
DO NOT commit config.py to version control!
"""

# UniFi Site Manager API Configuration
API_KEY = "your-api-key-here"
SITE_ID = "your-site-id-here"  # Optional, defaults to "default"

# Database Configuration
DATABASE_PATH = "network.db"

# Data Collector Configuration
COLLECTOR_INTERVAL = 60  # Seconds between polls (default: 60)

# Email Configuration (for report delivery)
# Leave as None if you don't want to use email reports
SMTP_HOST = None  # e.g., "smtp.gmail.com"
SMTP_PORT = 587  # Standard TLS port
SMTP_USERNAME = None  # Your email username
SMTP_PASSWORD = None  # Your email password or app-specific password
EMAIL_FROM = None  # Sender email address
EMAIL_TO = []  # List of recipient emails, e.g., ["admin@example.com"]

# Report Configuration
REPORT_OUTPUT_DIR = "reports"  # Directory for generated reports
ENABLE_PDF_REPORTS = True  # Requires weasyprint: pip install weasyprint

# Analytics Configuration
ANALYTICS_ANOMALY_THRESHOLD = 2.0  # Z-score threshold for anomaly detection
ANALYTICS_TREND_MIN_POINTS = 5  # Minimum data points for trend analysis

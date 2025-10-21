"""UniFi Network API Configuration Example.

Copy this file to config.py and fill in your actual credentials.
DO NOT commit config.py to version control!
"""

# =============================================================================
# UniFi Site Manager API Configuration (Cloud-based)
# =============================================================================
# Note: This is for the UniFi Site Manager cloud API (api.ui.com)
# For local controller, use the settings below instead
API_KEY = "your-api-key-here"
BASE_URL = "https://api.ui.com/v1"

# =============================================================================
# UniFi Network Controller Configuration (Local/Self-hosted)
# =============================================================================
# Use these settings for a local UniFi Network Controller
CONTROLLER_HOST = "192.168.1.1"  # Controller IP or hostname
CONTROLLER_PORT = 443  # HTTPS port (usually 443 or 8443)
CONTROLLER_USERNAME = "admin"  # Admin username
CONTROLLER_PASSWORD = "your-password-here"  # Admin password
CONTROLLER_SITE = "default"  # Site name (usually "default")
CONTROLLER_VERIFY_SSL = False  # Set to False for self-signed certificates

# Choose which API to use: "cloud" or "local"
API_TYPE = "local"  # "cloud" for Site Manager API, "local" for local controller

# =============================================================================
# Database Configuration
# =============================================================================
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

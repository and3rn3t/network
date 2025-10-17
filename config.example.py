"""
Configuration file for UniFi API credentials.

Copy this file to config.py and add your actual API key.
NEVER commit config.py to version control!
"""

# Your UniFi Site Manager API Key
# Get this from https://unifi.ui.com in the API section
API_KEY = "your-api-key-here"

# Base URL for UniFi API
BASE_URL = "https://api.ui.com/v1"

# Optional: Configure logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/unifi_api.log"

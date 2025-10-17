# Quick Start Guide

This guide will help you get started with the UniFi Network API experimentation repository.

## Prerequisites

Before you begin, ensure you have:

- Python 3.7 or higher installed
- A UniFi Site Manager account at [unifi.ui.com](https://unifi.ui.com)
- At least one UniFi device connected to your network
- Basic familiarity with Python and command line

## Step 1: Clone the Repository

```bash
git clone https://github.com/and3rn3t/network.git
cd network
```

## Step 2: Set Up Python Environment

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `requests` - For making HTTP requests to the API
- `python-dotenv` - For managing environment variables

## Step 4: Configure Your API Key

### Get Your API Key

1. Visit [UniFi Site Manager](https://unifi.ui.com)
2. Log in to your account
3. Navigate to Settings → API
4. Click "Create API Key"
5. Give it a descriptive name (e.g., "Network Experiments")
6. Copy the generated API key

### Set Up Configuration

```bash
# Copy the example configuration
cp config.example.py config.py

# Edit config.py with your favorite editor
nano config.py  # or vim, code, etc.
```

Replace `your-api-key-here` with your actual API key:

```python
API_KEY = "your-actual-api-key-from-unifi"
BASE_URL = "https://api.ui.com/v1"
```

⚠️ **Important:** Never commit `config.py` to version control! It's already in `.gitignore`.

## Step 5: Test Your Connection

Let's verify everything is working:

```bash
python examples/list_hosts.py
```

If successful, you should see:
```
Connecting to UniFi API...
Connection successful!

Fetching list of hosts...

Found X host(s):

Host #1:
  ID: abc123
  Name: Access Point Living Room
  Model: UAP-AC-PRO
  ...
```

If you get an error, check:
- Your API key is correct
- Your internet connection is working
- You have at least one UniFi device connected

## Step 6: Explore Device Information

Get detailed information about a specific device:

```bash
# List devices and select one interactively
python examples/get_device_info.py

# Or specify a device ID directly
python examples/get_device_info.py abc123
```

## What's Next?

### Experiment Ideas

1. **Device Monitoring**
   - Set up periodic polling of device status
   - Create alerts for offline devices
   - Track uptime statistics

2. **Data Collection**
   - Store historical device metrics
   - Analyze performance trends
   - Generate reports

3. **Automation**
   - Schedule automatic device reboots
   - Auto-backup configurations
   - Implement auto-recovery for offline devices

### Project Structure

```
network/
├── src/                    # Core library code
│   ├── __init__.py
│   └── unifi_client.py    # Main API client
├── examples/              # Example scripts
│   ├── list_hosts.py
│   └── get_device_info.py
├── docs/                  # Documentation
│   ├── API_REFERENCE.md
│   ├── FEATURES.md
│   └── QUICKSTART.md
├── logs/                  # Log files (auto-created)
├── data/                  # Data storage (auto-created)
├── config.py             # Your configuration (not in git)
└── config.example.py     # Configuration template
```

### Extending the Client

You can extend the `UniFiClient` class with additional methods:

```python
from src import UniFiClient

client = UniFiClient(api_key="your-key")

# The client already provides:
# - client.get_hosts()          # List all devices
# - client.get_host(host_id)    # Get device details
# - client.get_host_status(id)  # Get device status
# - client.reboot_host(host_id) # Reboot device
# - client.test_connection()    # Test API connection
```

### Creating Your Own Scripts

Create a new Python file in the `examples/` directory:

```python
#!/usr/bin/env python3
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import UniFiClient
import config

# Create client
client = UniFiClient(api_key=config.API_KEY)

# Your code here
hosts = client.get_hosts()
for host in hosts:
    print(f"{host['name']}: {host['state']}")
```

## Common Issues

### "Module not found" Error

Make sure you:
1. Activated your virtual environment
2. Installed dependencies with `pip install -r requirements.txt`
3. Are running scripts from the repository root or using the correct path

### "Invalid API Key" Error

Check that:
1. You copied the API key correctly (no extra spaces)
2. The API key is still valid in UniFi Site Manager
3. Your `config.py` file is in the repository root

### "No hosts found" Message

This could mean:
1. You don't have any UniFi devices connected yet
2. The API response format differs from expected
3. Your account doesn't have access to the devices

Enable debug logging to see more details:

```python
from src import setup_logging
setup_logging(log_level="DEBUG")
```

## Additional Resources

- **API Documentation:** [docs/API_REFERENCE.md](API_REFERENCE.md)
- **Feature Ideas:** [docs/FEATURES.md](FEATURES.md)
- **Official API Docs:** https://developer.ui.com/site-manager-api/gettingstarted

## Getting Help

If you encounter issues:
1. Check the logs in `logs/unifi_api.log`
2. Enable DEBUG logging for more details
3. Review the official API documentation
4. Check the UniFi community forums

## Security Reminders

- ✅ Keep your API key secret
- ✅ Never commit `config.py` to version control
- ✅ Use environment variables in production
- ✅ Rotate your API keys periodically
- ✅ Use read-only keys when possible

Happy experimenting! 🚀

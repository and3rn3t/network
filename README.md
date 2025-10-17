# UniFi Network API Experimentation

This repository is for experimenting with Ubiquiti's UniFi Network Site Manager API. It provides tools and examples for interacting with the UniFi API to manage network devices, store logs, and analyze data.

## Overview

The UniFi Site Manager API allows you to programmatically interact with your UniFi network devices, retrieve performance metrics, manage configurations, and automate network operations.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- A UniFi Site Manager account at [unifi.ui.com](https://unifi.ui.com)
- An API key (see Authentication section below)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/and3rn3t/network.git
cd network
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your API key:
```bash
cp config.example.py config.py
# Edit config.py and add your API key
```

### Authentication

To use the UniFi API, you need to generate an API key:

1. Sign in to [UniFi Site Manager](https://unifi.ui.com)
2. Navigate to the API section
3. Click "Create API Key"
4. Copy the key and add it to your `config.py` file

**Important:** Never commit your API key to version control!

## API Documentation

The UniFi Site Manager API documentation is available at:
- [Official Documentation](https://developer.ui.com/site-manager-api/gettingstarted)

### Base URL
```
https://api.ui.com/v1/
```

### Rate Limits
- Early Access: 100 requests per minute
- Stable Release: 10,000 requests per minute

### Key Headers
All API requests must include:
```
X-API-KEY: your-api-key-here
```

## Project Structure

```
network/
├── src/           # Core library code
├── examples/      # Example scripts
├── docs/          # Additional documentation
├── logs/          # Log storage (gitignored)
└── data/          # Data storage (gitignored)
```

## Features & Experiments

See [FEATURES.md](docs/FEATURES.md) for a comprehensive list of API features and experiment ideas.

## Examples

Check the `examples/` directory for sample scripts:

- `list_hosts.py` - List all network devices
- `get_device_info.py` - Get detailed device information
- More examples coming soon!

## Contributing

This is a personal experimentation repository, but feel free to fork and adapt for your own use.

## Resources

- [UniFi API Documentation](https://developer.ui.com/site-manager-api/gettingstarted)
- [UniFi Community](https://community.ui.com/)

## License

This project is for educational and experimental purposes.

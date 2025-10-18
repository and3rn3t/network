"""
Example: Using the UniFi API with an API key

This example shows how to initialize the client with your API key.
"""

import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config_loader import get_base_url, load_api_key
from src.unifi_client import UniFiClient


def main():
    # Load API key from config.py, .env, or environment variable
    api_key = load_api_key()

    if not api_key:
        print("ERROR: API key not found!")
        print("\nPlease add your API key in one of these ways:")
        print("1. Copy config.example.py to config.py and add your API key")
        print("2. Copy .env.example to .env and add your API key")
        print("3. Set UNIFI_API_KEY environment variable")
        return

    # Initialize the client
    base_url = get_base_url()
    client = UniFiClient(api_key, base_url)

    print(f"✓ Connected to {base_url}")
    print("\nYou can now use the client to make API calls:")
    print("  - client.get_sites()")
    print("  - client.get_devices()")
    print("  - etc.")

    # Example: Make an API call (uncomment when ready)
    # try:
    #     sites = client.get_sites()
    #     print(f"\nFound {len(sites)} sites")
    # except Exception as e:
    #     print(f"Error: {e}")


if __name__ == "__main__":
    main()

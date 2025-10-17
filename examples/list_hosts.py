#!/usr/bin/env python3
"""
Example: List All Network Hosts

This script demonstrates how to retrieve a list of all network devices
using the UniFi API.
"""

import sys
import os
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import UniFiClient, setup_logging

# Try to import config
try:
    import config
    API_KEY = config.API_KEY
    BASE_URL = config.BASE_URL
except ImportError:
    print("Error: config.py not found!")
    print("Please copy config.example.py to config.py and add your API key.")
    sys.exit(1)


def main():
    """Main function to list all hosts."""
    # Set up logging
    setup_logging(log_level="INFO")
    
    # Create client
    print("Connecting to UniFi API...")
    client = UniFiClient(api_key=API_KEY, base_url=BASE_URL)
    
    # Test connection
    if not client.test_connection():
        print("Failed to connect to UniFi API. Check your API key and network connection.")
        sys.exit(1)
    
    print("Connection successful!\n")
    
    # Get list of hosts
    print("Fetching list of hosts...")
    try:
        hosts = client.get_hosts()
        
        if not hosts:
            print("No hosts found or empty response from API.")
            return
        
        print(f"\nFound {len(hosts)} host(s):\n")
        
        # Display host information
        for i, host in enumerate(hosts, 1):
            print(f"Host #{i}:")
            print(f"  ID: {host.get('id', 'N/A')}")
            print(f"  Name: {host.get('name', 'N/A')}")
            print(f"  Model: {host.get('model', 'N/A')}")
            print(f"  IP Address: {host.get('ip', 'N/A')}")
            print(f"  MAC Address: {host.get('mac', 'N/A')}")
            print(f"  Status: {host.get('state', 'N/A')}")
            print()
        
        # Save to file
        output_file = "data/hosts_list.json"
        os.makedirs("data", exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(hosts, f, indent=2)
        
        print(f"Host data saved to {output_file}")
        
    except Exception as e:
        print(f"Error fetching hosts: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

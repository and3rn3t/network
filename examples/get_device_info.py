#!/usr/bin/env python3
"""
Example: Get Device Information

This script demonstrates how to retrieve detailed information about a
specific network device using the UniFi API.
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


def print_device_info(device_info: dict):
    """Print device information in a readable format."""
    print("\nDevice Information:")
    print("=" * 50)
    
    # Basic info
    print(f"ID: {device_info.get('id', 'N/A')}")
    print(f"Name: {device_info.get('name', 'N/A')}")
    print(f"Model: {device_info.get('model', 'N/A')}")
    print(f"MAC Address: {device_info.get('mac', 'N/A')}")
    print(f"IP Address: {device_info.get('ip', 'N/A')}")
    
    # Status
    print(f"\nStatus: {device_info.get('state', 'N/A')}")
    print(f"Uptime: {device_info.get('uptime', 'N/A')} seconds")
    
    # Firmware
    print(f"\nFirmware Version: {device_info.get('version', 'N/A')}")
    
    # Additional info (if available)
    if 'cpu' in device_info:
        print(f"\nCPU Usage: {device_info['cpu']}%")
    if 'memory' in device_info:
        print(f"Memory Usage: {device_info['memory']}%")
    
    print("=" * 50)


def main():
    """Main function to get device information."""
    # Set up logging
    setup_logging(log_level="INFO")
    
    # Create client
    print("Connecting to UniFi API...")
    client = UniFiClient(api_key=API_KEY, base_url=BASE_URL)
    
    # Get device ID from command line or list devices
    if len(sys.argv) > 1:
        device_id = sys.argv[1]
    else:
        print("\nFetching list of devices...")
        try:
            hosts = client.get_hosts()
            
            if not hosts:
                print("No devices found.")
                sys.exit(1)
            
            print(f"\nAvailable devices:")
            for i, host in enumerate(hosts, 1):
                print(f"{i}. {host.get('name', 'N/A')} (ID: {host.get('id', 'N/A')})")
            
            choice = input("\nEnter device number or ID: ").strip()
            
            # Try to parse as number first
            try:
                index = int(choice) - 1
                if 0 <= index < len(hosts):
                    device_id = hosts[index].get('id')
                else:
                    print("Invalid device number.")
                    sys.exit(1)
            except ValueError:
                # Use as ID directly
                device_id = choice
        
        except Exception as e:
            print(f"Error fetching device list: {e}")
            sys.exit(1)
    
    # Get device information
    print(f"\nFetching information for device: {device_id}")
    
    try:
        device_info = client.get_host(device_id)
        
        # Display device information
        print_device_info(device_info)
        
        # Save to file
        output_file = f"data/device_{device_id}.json"
        os.makedirs("data", exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(device_info, f, indent=2)
        
        print(f"\nDevice data saved to {output_file}")
        
    except Exception as e:
        print(f"Error fetching device information: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

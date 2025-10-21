"""Simple script to collect UniFi data without circular imports."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import API_KEY, BASE_URL
from src.database.database import Database
from src.database.models import Host
from src.unifi_client import UniFiClient


def main():
    """Fetch hosts from UniFi and store in database."""
    print("Connecting to UniFi API...")
    client = UniFiClient(api_key=API_KEY, base_url=BASE_URL)

    print("Fetching hosts...")
    hosts_data = client.get_hosts()
    print(f"Found {len(hosts_data)} hosts")

    print("Storing in database...")
    db = Database("network.db")

    for host_data in hosts_data:
        # Handle the API response structure
        reported = host_data.get("reportedState", {})
        hardware = reported.get("hardware", {})

        name = reported.get("name", reported.get("hostname", "Unknown"))
        mac = hardware.get("mac", host_data.get("mac", "Unknown"))
        hardware_id = host_data.get("hardwareId", hardware.get("uuid", mac))
        model = hardware.get("name", "Unknown")
        device_type = host_data.get("type", "console")
        ip = reported.get("ip", host_data.get("ipAddress", "Unknown"))
        firmware = hardware.get("firmwareVersion", reported.get("version", "Unknown"))

        print(f"  - {name} ({model}) - {mac} - {ip}")

        # Use transaction context manager to ensure commit
        with db.transaction():
            db.execute(
                """
                INSERT OR REPLACE INTO hosts (
                    id, hardware_id, mac_address, name, model, type, ip_address,
                    firmware_version, registration_time, first_seen, last_seen,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """,
                (
                    host_data.get("id", hardware_id),
                    hardware_id,
                    mac,
                    name,
                    model,
                    device_type,
                    ip,
                    firmware,
                    host_data.get("registrationTime"),
                    host_data.get("registrationTime"),  # Use registration as first seen
                    host_data.get("lastConnectionStateChange"),
                ),
            )

    print(f"\n✅ Successfully stored {len(hosts_data)} hosts in database!")
    print("Refresh your browser to see devices in the dropdown.")


if __name__ == "__main__":
    main()

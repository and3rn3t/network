"""
Test script for UniFi data models.
"""

import json
from datetime import datetime

from src.database.models_unifi import (
    UniFiClient,
    UniFiClientStatus,
    UniFiDevice,
    UniFiDeviceStatus,
    UniFiEvent,
)


def test_device_model():
    """Test UniFiDevice model."""
    print("Testing UniFiDevice model...")

    # Sample API response from controller
    api_data = {
        "mac": "aa:bb:cc:dd:ee:ff",
        "_id": "device123",
        "name": "Switch-Office",
        "type": "usw",
        "model": "US8P150",
        "version": "6.5.59.14777",
        "ip": "192.168.1.10",
        "state": 1,
        "adopted": True,
        "disabled": False,
        "uptime": 86400,
        "satisfaction": 95,
        "num_sta": 5,
        "bytes": 1024000,
        "led_override": "on",
        "last_seen": int(datetime.now().timestamp()),
    }

    # Test from_controller_response
    device = UniFiDevice.from_controller_response(api_data, site="default")
    print(f"✅ Created from API: {device}")
    print(f"   - Is online: {device.is_online()}")

    # Test to_db_params
    params = device.to_db_params()
    print(f"✅ DB params: {len(params)} values")

    # Test to_dict
    device_dict = device.to_dict()
    print(f"✅ Dictionary: {len(device_dict)} fields")

    # Simulate database row
    db_row = {
        "id": 1,
        "mac": device.mac,
        "device_id": device.device_id,
        "name": device.name,
        "type": device.type,
        "model": device.model,
        "version": device.version,
        "ip": device.ip,
        "site_name": device.site_name,
        "state": device.state,
        "adopted": 1,
        "disabled": 0,
        "uptime": device.uptime,
        "satisfaction": device.satisfaction,
        "num_sta": device.num_sta,
        "bytes_total": device.bytes_total,
        "led_override": device.led_override,
        "led_override_color": device.led_override_color,
        "last_seen": device.last_seen,
        "first_seen": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    # Test from_db_row
    device_from_db = UniFiDevice.from_db_row(db_row)
    print(f"✅ Created from DB: {device_from_db}")

    print()


def test_device_status_model():
    """Test UniFiDeviceStatus model."""
    print("Testing UniFiDeviceStatus model...")

    # Sample API response
    api_data = {
        "mac": "aa:bb:cc:dd:ee:ff",
        "state": 1,
        "uptime": 86400,
        "system-stats": {"cpu": 25.5, "mem": 40.2},
        "general_temperature": 45.0,
        "num_sta": 5,
        "satisfaction": 95,
        "rx_bytes": 500000,
        "tx_bytes": 300000,
        "port_table": [
            {"port_idx": 1, "up": True},
            {"port_idx": 2, "up": False},
        ],
    }

    # Test from_controller_response
    status = UniFiDeviceStatus.from_controller_response("aa:bb:cc:dd:ee:ff", api_data)
    print(f"✅ Created from API: {status}")

    # Test to_db_params
    params = status.to_db_params()
    print(f"✅ DB params: {len(params)} values")

    print()


def test_client_model():
    """Test UniFiClient model."""
    print("Testing UniFiClient model...")

    # Sample API response (wireless client)
    api_data = {
        "mac": "11:22:33:44:55:66",
        "_id": "client123",
        "hostname": "johns-laptop",
        "name": "John's Laptop",
        "ip": "192.168.1.100",
        "is_wired": False,
        "is_guest": False,
        "blocked": False,
        "essid": "MyWiFi",
        "channel": 36,
        "ap_mac": "aa:bb:cc:dd:ee:ff",
        "ap_name": "AP-Office",
        "network": "LAN",
        "use_fixedip": False,
        "oui": "Apple",
        "first_seen": int(datetime.now().timestamp()) - 86400,
        "last_seen": int(datetime.now().timestamp()),
    }

    # Test from_controller_response
    client = UniFiClient.from_controller_response(api_data)
    print(f"✅ Created from API: {client}")
    print(f"   - Connection: {client.connection_type()}")

    # Test to_db_params
    params = client.to_db_params()
    print(f"✅ DB params: {len(params)} values")

    print()


def test_client_status_model():
    """Test UniFiClientStatus model."""
    print("Testing UniFiClientStatus model...")

    # Sample API response (wireless client)
    api_data = {
        "mac": "11:22:33:44:55:66",
        "ip": "192.168.1.100",
        "is_wired": False,
        "signal": -55,
        "noise": -95,
        "rssi": 40,
        "tx_bytes": 100000,
        "rx_bytes": 500000,
        "tx_rate": 866,
        "rx_rate": 433,
        "uptime": 3600,
        "satisfaction": 92,
    }

    # Test from_controller_response
    status = UniFiClientStatus.from_controller_response("11:22:33:44:55:66", api_data)
    print(f"✅ Created from API: {status}")
    print(f"   - Signal quality: {status.signal_quality()}")

    # Test wired client
    wired_data = {**api_data, "is_wired": True, "signal": None}
    wired_status = UniFiClientStatus.from_controller_response(
        "11:22:33:44:55:66", wired_data
    )
    print(f"✅ Wired client: {wired_status}")
    print(f"   - Signal quality: {wired_status.signal_quality()}")

    print()


def test_event_model():
    """Test UniFiEvent model."""
    print("Testing UniFiEvent model...")

    # Create event
    event = UniFiEvent(
        event_type="status_change",
        severity="warning",
        title="Device went offline",
        description="Switch-Office lost connection",
        device_mac="aa:bb:cc:dd:ee:ff",
        previous_value="1",
        new_value="0",
        metadata=json.dumps({"location": "Office"}),
    )
    print(f"✅ Created event: {event}")

    # Test to_db_params
    params = event.to_db_params()
    print(f"✅ DB params: {len(params)} values")

    print()


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing UniFi Data Models")
    print("=" * 60)
    print()

    try:
        test_device_model()
        test_device_status_model()
        test_client_model()
        test_client_status_model()
        test_event_model()

        print("=" * 60)
        print("✅ All model tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

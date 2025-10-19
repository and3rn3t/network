"""Check what metrics are available in UniFi API response"""

import json

from config import API_KEY, BASE_URL
from src.unifi_client import UniFiClient

client = UniFiClient(api_key=API_KEY, base_url=BASE_URL)
hosts = client.get_hosts()
host = hosts[0]
reported = host.get("reportedState", {})

print("=== Hardware Info ===")
hardware = reported.get("hardware", {})
print(json.dumps(list(hardware.keys()), indent=2))

print("\n=== Looking for Stats ===")
for key in reported.keys():
    if (
        "stat" in key.lower()
        or "cpu" in key.lower()
        or "mem" in key.lower()
        or "uptime" in key.lower()
    ):
        print(f"{key}: {reported[key]}")

print("\n=== Full reportedState Keys ===")
print(json.dumps(list(reported.keys()), indent=2))

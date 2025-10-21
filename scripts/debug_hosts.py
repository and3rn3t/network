"""Debug script to see what data UniFi API returns."""

import json

from config import API_KEY, BASE_URL
from src.unifi_client import UniFiClient

client = UniFiClient(api_key=API_KEY, base_url=BASE_URL)
hosts = client.get_hosts()

print(f"Found {len(hosts)} hosts")
print("\nHost data:")
for host in hosts:
    print(json.dumps(host, indent=2))

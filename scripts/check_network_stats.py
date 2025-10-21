"""Explore WAN and network metrics"""

import json

from config import API_KEY, BASE_URL
from src.unifi_client import UniFiClient

client = UniFiClient(api_key=API_KEY, base_url=BASE_URL)
hosts = client.get_hosts()
host = hosts[0]
reported = host.get("reportedState", {})

print("=== WAN Info ===")
wans = reported.get("wans", [])
if wans:
    print(f"Found {len(wans)} WAN(s)")
    for i, wan in enumerate(wans):
        print(f"\nWAN {i+1} keys:")
        print(json.dumps(list(wan.keys()), indent=2))
else:
    print("No WAN data")

print("\n=== Controllers Info ===")
controllers = reported.get("controllers", [])
if controllers:
    print(f"Found {len(controllers)} controller(s)")
    for i, ctrl in enumerate(controllers):
        print(f"\nController {i+1} keys:")
        print(json.dumps(list(ctrl.keys()), indent=2))
else:
    print("No controller data")

print("\n=== Apps Info ===")
apps = reported.get("apps", {})
if apps:
    print("App keys:")
    print(json.dumps(list(apps.keys()), indent=2))
else:
    print("No apps data")

"""
Analyze UniFi Host Data

This script provides a detailed analysis of your UniFi host data.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def parse_timestamp(timestamp_str):
    """Parse ISO timestamp to readable format."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except:
        return timestamp_str


def analyze_host(host_data):
    """Analyze a single host."""
    print("\n" + "=" * 70)
    print("HOST ANALYSIS")
    print("=" * 70)

    # Basic Info
    print(f"\n{'Field':<30} {'Value':<40}")
    print("-" * 70)
    print(f"{'ID':<30} {host_data.get('id', 'N/A')[:40]}")
    print(f"{'Hardware ID':<30} {host_data.get('hardwareId', 'N/A')}")
    print(f"{'Type':<30} {host_data.get('type', 'N/A').upper()}")
    print(f"{'IP Address':<30} {host_data.get('ipAddress', 'N/A')}")
    print(f"{'Owner':<30} {'Yes' if host_data.get('owner') else 'No'}")
    print(f"{'Blocked':<30} {'Yes' if host_data.get('isBlocked') else 'No'}")

    # Timestamps
    print(f"\n{'Timeline':<30} {'Date/Time':<40}")
    print("-" * 70)
    if "registrationTime" in host_data:
        print(f"{'Registered':<30} {parse_timestamp(host_data['registrationTime'])}")
    if "lastConnectionStateChange" in host_data:
        print(
            f"{'Last Connection Change':<30} {parse_timestamp(host_data['lastConnectionStateChange'])}"
        )
    if "latestBackupTime" in host_data:
        print(f"{'Latest Backup':<30} {parse_timestamp(host_data['latestBackupTime'])}")

    # User Data / Console Info
    if "userData" in host_data:
        user_data = host_data["userData"]

        # Applications
        if "apps" in user_data:
            print(f"\n{'Installed Apps':<30} {', '.join(user_data['apps'])}")

        # Console Group Members
        if "consoleGroupMembers" in user_data:
            print(f"\n{'Console Devices':<30} {'Details':<40}")
            print("-" * 70)
            for member in user_data["consoleGroupMembers"]:
                mac = member.get("mac", "N/A")
                role = member.get("role", "N/A")
                print(f"{mac:<30} {role}")

                # Show supported applications
                if (
                    "roleAttributes" in member
                    and "applications" in member["roleAttributes"]
                ):
                    apps = member["roleAttributes"]["applications"]
                    print(f"\n{'  Supported Applications:':<30}")
                    for app_name, app_info in apps.items():
                        status = "✅ Owned" if app_info.get("owned") else "⚪ Available"
                        required = " (Required)" if app_info.get("required") else ""
                        print(f"    • {app_name.title():<20} {status}{required}")

    # Report Info
    if "reportCrash" in host_data:
        print(
            f"\n{'Crash Reporting':<30} {'Enabled' if host_data['reportCrash'] else 'Disabled'}"
        )

    if "reportStats" in host_data:
        print(
            f"{'Stats Reporting':<30} {'Enabled' if host_data['reportStats'] else 'Disabled'}"
        )

    print("\n" + "=" * 70)


def main():
    # Try to load the most recent hosts data
    data_file = Path(__file__).parent.parent / "data" / "hosts_list.json"

    if not data_file.exists():
        print("❌ No host data found. Run 'python examples/list_hosts.py' first.")
        return

    print(f"📖 Reading host data from: {data_file}")

    with open(data_file, "r") as f:
        hosts = json.load(f)

    print(f"\n✅ Found {len(hosts)} host(s)")

    for i, host in enumerate(hosts, 1):
        print(f"\n{'#' * 70}")
        print(f"HOST #{i}")
        analyze_host(host)

    print("\n💡 Next Steps:")
    print("  1. Check which UniFi applications you can enable")
    print("  2. Explore the Console Group Members (your devices)")
    print("  3. Review the full JSON in data/hosts_list.json")
    print("  4. Try api_explorer.http for more endpoints")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Analysis cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()

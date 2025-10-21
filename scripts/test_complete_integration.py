"""
Complete UniFi Data Collector Integration Test

Tests the full stack:
1. Configuration
2. Database schema
3. Controller connection
4. Data collection via orchestrator
5. Database storage
6. Analytics engine
7. Performance
"""

import sys
import time
from datetime import datetime
from pathlib import Path

from src.collector.orchestrator import create_orchestrator_from_config_file
from src.database import Database
from src.database.repositories.unifi_repository import (
    UniFiClientRepository,
    UniFiDeviceRepository,
    UniFiEventRepository,
    UniFiMetricRepository,
)


def print_header(title: str):
    """Print test section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def print_test(name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = "✅" if passed else "❌"
    print(f"{status} {name}")
    if details:
        for line in details.split("\n"):
            print(f"   {line}")


def main():
    """Run complete integration test"""
    print("\n" + "=" * 80)
    print("  UniFi Data Collector - Complete Integration Test")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)

    test_results = []

    # Test 1: Configuration
    print_header("Test 1: Configuration")
    try:
        import config

        has_host = hasattr(config, "CONTROLLER_HOST")
        has_user = hasattr(config, "CONTROLLER_USERNAME")
        has_pass = hasattr(config, "CONTROLLER_PASSWORD")
        has_type = hasattr(config, "API_TYPE")
        is_local = getattr(config, "API_TYPE", "") == "local"

        print_test("Config file loaded", True)
        print_test(
            "CONTROLLER_HOST set", has_host, getattr(config, "CONTROLLER_HOST", "")
        )
        print_test(
            "CONTROLLER_USERNAME set",
            has_user,
            getattr(config, "CONTROLLER_USERNAME", ""),
        )
        print_test("CONTROLLER_PASSWORD set", has_pass)
        print_test(
            "API_TYPE = 'local'",
            is_local,
            f"Current: {getattr(config, 'API_TYPE', 'not set')}",
        )

        config_ok = has_host and has_user and has_pass and is_local
        test_results.append(("Configuration", config_ok))

        if not config_ok:
            print("\n⚠️  Please configure config.py for local controller access")
            print(
                "   Set API_TYPE = 'local' and provide CONTROLLER_HOST, USERNAME, PASSWORD"
            )
            return 1

    except Exception as e:
        print_test("Configuration", False, str(e))
        test_results.append(("Configuration", False))
        return 1

    # Test 2: Database Schema
    print_header("Test 2: Database Schema")
    try:
        db = Database("network_monitor.db")

        tables = [
            "unifi_devices",
            "unifi_device_status",
            "unifi_clients",
            "unifi_client_status",
            "unifi_events",
            "unifi_metrics",
        ]

        all_tables_exist = True
        for table in tables:
            query = (
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
            )
            result = db.execute(query).fetchone()
            exists = result is not None
            print_test(f"Table: {table}", exists)
            if not exists:
                all_tables_exist = False

        db.close()
        test_results.append(("Database Schema", all_tables_exist))

    except Exception as e:
        print_test("Database Schema", False, str(e))
        test_results.append(("Database Schema", False))

    # Test 3: Controller Connection
    print_header("Test 3: Controller Connection")
    try:
        import config
        from src.unifi_controller import UniFiController

        controller = UniFiController(
            host=config.CONTROLLER_HOST,
            username=config.CONTROLLER_USERNAME,
            password=config.CONTROLLER_PASSWORD,
            verify_ssl=getattr(config, "VERIFY_SSL", False),
        )

        controller.login()
        print_test("Login successful", True)

        sites = controller.get_sites()
        print_test("Get sites", True, f"Found {len(sites)} site(s)")

        controller.logout()
        print_test("Logout successful", True)

        test_results.append(("Controller Connection", True))

    except Exception as e:
        print_test("Controller Connection", False, str(e))
        test_results.append(("Controller Connection", False))
        return 1

    # Test 4: Data Collection
    print_header("Test 4: Data Collection (via Orchestrator)")
    try:
        orchestrator = create_orchestrator_from_config_file("config.py")
        print_test("Orchestrator created", True)

        print("\n⏳ Collecting data from controller... (may take 10-30 seconds)\n")
        start_time = time.time()
        stats = orchestrator.collect_all()
        duration = time.time() - start_time

        print_test("Collection completed", True, f"Duration: {duration:.1f}s")

        if "unifi_stats" in stats:
            us = stats["unifi_stats"]
            devices = us.get("devices_collected", 0)
            clients = us.get("clients_collected", 0)
            events = us.get("events_generated", 0)
            metrics = us.get("metrics_stored", 0)

            print(f"\n   📊 Collection Results:")
            print_test("Devices collected", devices > 0, f"{devices} devices")
            print_test("Clients collected", clients > 0, f"{clients} clients")
            print_test("Events generated", events >= 0, f"{events} events")
            print_test("Metrics stored", metrics > 0, f"{metrics} metrics")

            collection_ok = devices > 0 and metrics > 0
            test_results.append(("Data Collection", collection_ok))
        else:
            print_test("UniFi stats in result", False)
            test_results.append(("Data Collection", False))

        orchestrator.close()

    except Exception as e:
        print_test("Data Collection", False, str(e))
        test_results.append(("Data Collection", False))

    # Test 5: Database Storage
    print_header("Test 5: Database Storage Verification")
    try:
        db = Database("network_monitor.db")

        device_repo = UniFiDeviceRepository(db)
        client_repo = UniFiClientRepository(db)
        event_repo = UniFiEventRepository(db)
        metric_repo = UniFiMetricRepository(db)

        devices = device_repo.get_all()
        print_test("Devices stored", len(devices) > 0, f"{len(devices)} devices")

        if devices:
            print(f"\n   Sample device:")
            dev = devices[0]
            print(f"   - Name: {dev.name}")
            print(f"   - MAC: {dev.mac}")
            print(f"   - Model: {dev.model}")
            print(f"   - Type: {dev.device_type}")

        clients = client_repo.get_all()
        active_clients = client_repo.get_active_clients()
        print_test(
            "Clients stored",
            len(clients) > 0,
            f"{len(clients)} clients ({len(active_clients)} active)",
        )

        events = event_repo.get_recent(limit=10)
        print_test("Events stored", len(events) >= 0, f"{len(events)} recent events")

        metrics = metric_repo.get_recent(limit=10)
        print_test("Metrics stored", len(metrics) > 0, f"{len(metrics)} recent metrics")

        storage_ok = len(devices) > 0 and len(metrics) > 0
        test_results.append(("Database Storage", storage_ok))

        db.close()

    except Exception as e:
        print_test("Database Storage", False, str(e))
        test_results.append(("Database Storage", False))

    # Test 6: Analytics Engine
    print_header("Test 6: Analytics Engine")
    try:
        from src.analytics.unifi_analytics import UniFiAnalyticsEngine

        db = Database("network_monitor.db")
        analytics = UniFiAnalyticsEngine(db)

        # Network health summary
        summary = analytics.get_network_health_summary(hours=1)
        print_test("Network health summary", True)

        print(f"\n   📊 Network Health:")
        print(f"   - Total devices: {summary['devices']['total']}")
        print(f"   - Active clients: {summary['clients']['total_active']}")

        if summary["devices"]["avg_health_score"]:
            print(
                f"   - Avg device health: {summary['devices']['avg_health_score']:.1f}/100"
            )

        # Device health
        device_repo = UniFiDeviceRepository(db)
        devices = device_repo.get_all()

        if devices:
            health = analytics.calculate_device_health(devices[0].mac, hours=1)
            if health:
                print_test(
                    "Device health calculation",
                    True,
                    f"Score: {health.health_score:.1f}/100",
                )
            else:
                print_test(
                    "Device health calculation",
                    False,
                    "Insufficient data (need more collection cycles)",
                )

        # Network topology
        topology = analytics.analyze_network_topology()
        print_test(
            "Network topology",
            True,
            f"{topology.total_devices} devices, {topology.total_clients} clients",
        )

        # Signal quality
        signal = analytics.analyze_signal_quality()
        total_wireless = (
            signal.excellent_count
            + signal.good_count
            + signal.fair_count
            + signal.poor_count
        )
        print_test(
            "Signal quality", True, f"{total_wireless} wireless clients analyzed"
        )

        test_results.append(("Analytics Engine", True))

        db.close()

    except Exception as e:
        print_test("Analytics Engine", False, str(e))
        test_results.append(("Analytics Engine", False))

    # Test 7: Performance
    print_header("Test 7: Performance Test")
    try:
        print("⏳ Running 3 collection cycles...\n")

        orchestrator = create_orchestrator_from_config_file("config.py")
        durations = []

        for i in range(3):
            start = time.time()
            stats = orchestrator.collect_all()
            duration = time.time() - start
            durations.append(duration)

            if "unifi_stats" in stats:
                us = stats["unifi_stats"]
                print(
                    f"   Cycle {i+1}: {duration:.2f}s ({us.get('devices_collected', 0)} devices, {us.get('clients_collected', 0)} clients)"
                )

            if i < 2:
                time.sleep(2)

        avg = sum(durations) / len(durations)
        acceptable = avg < 60

        print_test(f"\nAverage collection time", True, f"{avg:.2f}s")
        print_test(
            "Performance acceptable (<60s)",
            acceptable,
            f"Target: <60s, Actual: {avg:.2f}s",
        )

        test_results.append(("Performance", acceptable))

        orchestrator.close()

    except Exception as e:
        print_test("Performance", False, str(e))
        test_results.append(("Performance", False))

    # Summary
    print_header("Test Summary")

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\n{'=' * 80}")
    print(f"  Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print(f"{'=' * 80}\n")

    if passed == total:
        print("🎉 SUCCESS! All integration tests passed!")
        print("\nThe UniFi Data Collector is fully operational:")
        print("  ✅ Controller connection working")
        print("  ✅ Data collection working")
        print("  ✅ Database storage working")
        print("  ✅ Analytics working")
        print("  ✅ Performance acceptable")
        print("\nYou can now:")
        print("  • Run continuous collection: python collect_unifi_data.py --daemon")
        print("  • View analytics: python unifi_analytics_demo.py")
        print("  • Access data via repositories and analytics API")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the results above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

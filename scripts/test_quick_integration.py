"""
Quick UniFi Integration Test

Direct test avoiding circular imports.
Tests connection, collection, storage, and analytics.
"""

import sys
import time
from datetime import datetime


def print_header(title: str):
    """Print section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def test_result(name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = "✅" if passed else "❌"
    print(f"{status} {name}")
    if details:
        for line in details.split("\n"):
            print(f"   {line}")


def main():
    """Run quick integration test"""
    print("\n" + "=" * 80)
    print("  UniFi Controller - Quick Integration Test")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)

    results = []

    # Test 1: Config
    print_header("Test 1: Configuration")
    try:
        import config

        has_host = hasattr(config, "CONTROLLER_HOST")
        has_user = hasattr(config, "CONTROLLER_USERNAME")
        has_pass = hasattr(config, "CONTROLLER_PASSWORD")
        is_local = getattr(config, "API_TYPE", "") == "local"

        test_result("Config loaded", True)
        test_result("Controller host", has_host, getattr(config, "CONTROLLER_HOST", ""))
        test_result("API_TYPE = local", is_local)

        config_ok = has_host and has_user and has_pass and is_local
        results.append(("Configuration", config_ok))

        if not config_ok:
            print("\n⚠️  Config not set up for local controller")
            return 1

    except Exception as e:
        test_result("Configuration", False, str(e))
        return 1

    # Test 2: Database
    print_header("Test 2: Database Schema")
    try:
        from src.database import Database

        db = Database("network_monitor.db")

        tables = ["unifi_devices", "unifi_clients", "unifi_events", "unifi_metrics"]
        all_exist = True

        for table in tables:
            query = (
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
            )
            result = db.execute(query).fetchone()
            exists = result is not None
            test_result(f"Table: {table}", exists)
            if not exists:
                all_exist = False

        db.close()
        results.append(("Database Schema", all_exist))

    except Exception as e:
        test_result("Database", False, str(e))
        results.append(("Database Schema", False))

    # Test 3: Controller Connection
    print_header("Test 3: Controller Connection")
    try:
        import config
        from src.unifi_controller import UniFiController

        controller = UniFiController(
            host=config.CONTROLLER_HOST,
            username=config.CONTROLLER_USERNAME,
            password=config.CONTROLLER_PASSWORD,
            verify_ssl=False,
        )

        controller.login()
        test_result("Login", True)

        sites = controller.get_sites()
        test_result("Get sites", True, f"{len(sites)} site(s)")

        devices = controller.get_devices()
        test_result("Get devices", True, f"{len(devices)} device(s)")

        clients = controller.get_clients()
        test_result("Get clients", True, f"{len(clients)} client(s)")

        controller.logout()
        test_result("Logout", True)

        results.append(("Controller Connection", True))

    except Exception as e:
        test_result("Controller Connection", False, str(e))
        results.append(("Controller Connection", False))
        return 1

    # Test 4: Data Collection
    print_header("Test 4: Direct Data Collection")
    try:
        import config
        from src.collector.unifi_collector import (
            UniFiCollectorConfig,
            UniFiDataCollector,
        )
        from src.database import Database

        db = Database("network_monitor.db")

        # Create collector config
        collector_config = UniFiCollectorConfig(
            controller_url=config.CONTROLLER_HOST,
            username=config.CONTROLLER_USERNAME,
            password=config.CONTROLLER_PASSWORD,
            site=config.CONTROLLER_SITE,
            verify_ssl=False,
            collection_interval=300,
        )

        # Create collector
        collector = UniFiDataCollector(collector_config, db)
        test_result("Collector created", True)

        # Run collection
        print("\n⏳ Collecting data...\n")
        start = time.time()
        stats = collector.collect()
        duration = time.time() - start

        test_result("Collection completed", True, f"Duration: {duration:.1f}s")

        devices = stats.get("devices_collected", 0)
        clients = stats.get("clients_collected", 0)
        events = stats.get("events_generated", 0)
        metrics = stats.get("metrics_stored", 0)

        print("\n   Collection Results:")
        test_result("Devices", devices > 0, f"{devices} devices")
        test_result("Clients", clients > 0, f"{clients} clients")
        test_result("Events", events >= 0, f"{events} events")
        test_result("Metrics", metrics > 0, f"{metrics} metrics")

        collector.close()
        db.close()

        collection_ok = devices > 0 and metrics > 0
        results.append(("Data Collection", collection_ok))

    except Exception as e:
        test_result("Data Collection", False, str(e))
        results.append(("Data Collection", False))

    # Test 5: Database Storage
    print_header("Test 5: Database Storage")
    try:
        import src.database.repositories.unifi_repository as unifi_repos
        from src.database import Database

        db = Database("network_monitor.db")

        device_repo = unifi_repos.UniFiDeviceRepository(db)
        client_repo = unifi_repos.UniFiClientRepository(db)
        metric_repo = unifi_repos.UniFiMetricRepository(db)

        devices = device_repo.get_all()
        test_result("Devices in DB", len(devices) > 0, f"{len(devices)} devices")

        if devices:
            print(f"\n   Sample device:")
            print(f"   - {devices[0].name} ({devices[0].mac})")
            print(f"   - Model: {devices[0].model}")

        clients = client_repo.get_all()
        test_result("Clients in DB", len(clients) > 0, f"{len(clients)} clients")

        metrics = metric_repo.get_recent(limit=10)
        test_result("Metrics in DB", len(metrics) > 0, f"{len(metrics)} metrics")

        db.close()

        storage_ok = len(devices) > 0 and len(metrics) > 0
        results.append(("Database Storage", storage_ok))

    except Exception as e:
        test_result("Database Storage", False, str(e))
        results.append(("Database Storage", False))

    # Test 6: Analytics
    print_header("Test 6: Analytics Engine")
    try:
        from src.analytics.unifi_analytics import UniFiAnalyticsEngine
        from src.database import Database

        db = Database("network_monitor.db")
        analytics = UniFiAnalyticsEngine(db)

        # Network health
        summary = analytics.get_network_health_summary(hours=1)
        test_result("Network health", True)

        print(f"\n   Network Health:")
        print(f"   - Devices: {summary['devices']['total']}")
        print(f"   - Clients: {summary['clients']['total_active']}")

        if summary["devices"]["avg_health_score"]:
            print(f"   - Avg health: {summary['devices']['avg_health_score']:.1f}/100")

        # Topology
        topology = analytics.analyze_network_topology()
        test_result(
            "Topology",
            True,
            f"{topology.total_devices} devices, {topology.total_clients} clients",
        )

        # Signal quality
        signal = analytics.analyze_signal_quality()
        total = (
            signal.excellent_count
            + signal.good_count
            + signal.fair_count
            + signal.poor_count
        )
        test_result("Signal quality", True, f"{total} wireless clients")

        db.close()
        results.append(("Analytics", True))

    except Exception as e:
        test_result("Analytics", False, str(e))
        results.append(("Analytics", False))

    # Summary
    print_header("Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\n{'=' * 80}")
    print(f"  Results: {passed}/{total} passed ({passed/total*100:.0f}%)")
    print(f"{'=' * 80}\n")

    if passed == total:
        print("🎉 SUCCESS! All tests passed!")
        print("\nNext steps:")
        print("  • Run daemon: python collect_unifi_data.py --daemon")
        print("  • View analytics: python unifi_analytics_demo.py")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

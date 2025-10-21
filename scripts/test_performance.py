#!/usr/bin/env python3
"""
UniFi Controller Performance Testing

This script tests the performance of various UniFi Controller operations:
1. Single operation performance (baseline)
2. Bulk operations (multiple devices/clients)
3. Concurrent requests
4. Memory usage profiling
5. Session reuse efficiency
"""

import statistics
import sys
import time
import tracemalloc
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from src.exceptions import UniFiAPIError
from src.unifi_controller import UniFiController


class PerformanceTimer:
    """Context manager for timing operations."""

    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.elapsed = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed = time.perf_counter() - self.start_time
        return False


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 0.001:
        return f"{seconds * 1000000:.0f}µs"
    elif seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    else:
        return f"{seconds:.2f}s"


def print_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_result(label: str, value: Any, unit: str = ""):
    """Print a formatted result."""
    print(f"  {label:.<50} {value}{unit}")


def test_single_operations(controller: UniFiController) -> Dict[str, float]:
    """Test performance of individual operations."""
    print_header("Test 1: Single Operation Performance (Baseline)")

    results = {}

    # Test login
    print("\n📡 Testing authentication...")
    with PerformanceTimer("login") as timer:
        controller.login()
    results["login"] = timer.elapsed
    print_result("Login time", format_duration(timer.elapsed))

    # Test get_sites
    print("\n📍 Testing get_sites...")
    times = []
    for i in range(5):
        with PerformanceTimer("get_sites") as timer:
            sites = controller.get_sites()
        times.append(timer.elapsed)
    results["get_sites_avg"] = statistics.mean(times)
    results["get_sites_min"] = min(times)
    results["get_sites_max"] = max(times)
    print_result("Average time", format_duration(results["get_sites_avg"]))
    print_result("Min time", format_duration(results["get_sites_min"]))
    print_result("Max time", format_duration(results["get_sites_max"]))
    print_result("Sites found", len(sites))

    # Test get_devices
    print("\n🖥️  Testing get_devices...")
    times = []
    for i in range(5):
        with PerformanceTimer("get_devices") as timer:
            devices = controller.get_devices()
        times.append(timer.elapsed)
    results["get_devices_avg"] = statistics.mean(times)
    results["get_devices_min"] = min(times)
    results["get_devices_max"] = max(times)
    print_result("Average time", format_duration(results["get_devices_avg"]))
    print_result("Min time", format_duration(results["get_devices_min"]))
    print_result("Max time", format_duration(results["get_devices_max"]))
    print_result("Devices found", len(devices))

    # Test get_clients
    print("\n👥 Testing get_clients...")
    times = []
    for i in range(5):
        with PerformanceTimer("get_clients") as timer:
            clients = controller.get_clients()
        times.append(timer.elapsed)
    results["get_clients_avg"] = statistics.mean(times)
    results["get_clients_min"] = min(times)
    results["get_clients_max"] = max(times)
    print_result("Average time", format_duration(results["get_clients_avg"]))
    print_result("Min time", format_duration(results["get_clients_min"]))
    print_result("Max time", format_duration(results["get_clients_max"]))
    print_result("Clients found", len(clients))

    # Test get_device (single)
    print("\n🔍 Testing get_device (single lookup)...")
    if devices:
        test_mac = devices[0].get("mac")
        times = []
        for i in range(5):
            with PerformanceTimer("get_device") as timer:
                device = controller.get_device(test_mac)
            times.append(timer.elapsed)
        results["get_device_avg"] = statistics.mean(times)
        print_result("Average time", format_duration(results["get_device_avg"]))
        print_result("Device name", device.get("name", "Unknown"))

    return results


def test_bulk_operations(controller: UniFiController) -> Dict[str, float]:
    """Test performance of bulk operations."""
    print_header("Test 2: Bulk Operations")

    results = {}

    # Get all devices for bulk testing
    print("\n🖥️  Fetching devices for bulk operations...")
    devices = controller.get_devices()
    device_count = len(devices)
    print_result("Devices available", device_count)

    if device_count == 0:
        print("⚠️  No devices found, skipping bulk device tests")
        return results

    # Test bulk device info retrieval
    print("\n📊 Testing bulk device info retrieval...")
    with PerformanceTimer("bulk_device_info") as timer:
        device_infos = []
        for device in devices:
            try:
                info = controller.get_device_info(device.get("mac"))
                device_infos.append(info)
            except Exception as e:
                print(f"  ⚠️  Failed to get info for {device.get('name')}: {e}")
    results["bulk_device_info_total"] = timer.elapsed
    results["bulk_device_info_per_device"] = (
        timer.elapsed / device_count if device_count > 0 else 0
    )
    print_result("Total time", format_duration(timer.elapsed))
    print_result(
        "Time per device", format_duration(results["bulk_device_info_per_device"])
    )
    print_result("Throughput", f"{device_count / timer.elapsed:.1f} devices/sec")

    # Get all clients for bulk testing
    print("\n👥 Fetching clients for bulk operations...")
    clients = controller.get_clients()
    client_count = len(clients)
    print_result("Clients available", client_count)

    if client_count == 0:
        print("⚠️  No clients found, skipping bulk client tests")
        return results

    # Test bulk client lookup
    print("\n🔍 Testing bulk client lookup...")
    sample_clients = clients[: min(10, client_count)]  # Test with up to 10 clients
    with PerformanceTimer("bulk_client_lookup") as timer:
        for client in sample_clients:
            try:
                mac = client.get("mac")
                found_client = controller.get_client(mac)
            except Exception as e:
                print(f"  ⚠️  Failed to find client {mac}: {e}")
    results["bulk_client_lookup_total"] = timer.elapsed
    results["bulk_client_lookup_per_client"] = timer.elapsed / len(sample_clients)
    print_result("Total time", format_duration(timer.elapsed))
    print_result(
        "Time per client", format_duration(results["bulk_client_lookup_per_client"])
    )
    print_result("Clients tested", len(sample_clients))

    return results


def test_concurrent_requests(controller: UniFiController) -> Dict[str, float]:
    """Test performance of concurrent requests."""
    print_header("Test 3: Concurrent Requests")

    results = {}

    def fetch_devices():
        """Fetch devices (thread-safe)."""
        return controller.get_devices()

    def fetch_clients():
        """Fetch clients (thread-safe)."""
        return controller.get_clients()

    # Test concurrent device fetches
    print("\n🔄 Testing concurrent device requests...")
    num_concurrent = 5
    with PerformanceTimer("concurrent_devices") as timer:
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(fetch_devices) for _ in range(num_concurrent)]
            results_list = [future.result() for future in as_completed(futures)]
    results["concurrent_devices_total"] = timer.elapsed
    results["concurrent_devices_avg"] = timer.elapsed / num_concurrent
    print_result("Total time", format_duration(timer.elapsed))
    print_result(
        "Average per request", format_duration(results["concurrent_devices_avg"])
    )
    print_result("Concurrent requests", num_concurrent)
    print_result(
        "Speedup vs sequential",
        f"{(results.get('get_devices_avg', 0) * num_concurrent / timer.elapsed):.1f}x",
    )

    # Test concurrent client fetches
    print("\n🔄 Testing concurrent client requests...")
    with PerformanceTimer("concurrent_clients") as timer:
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(fetch_clients) for _ in range(num_concurrent)]
            results_list = [future.result() for future in as_completed(futures)]
    results["concurrent_clients_total"] = timer.elapsed
    results["concurrent_clients_avg"] = timer.elapsed / num_concurrent
    print_result("Total time", format_duration(timer.elapsed))
    print_result(
        "Average per request", format_duration(results["concurrent_clients_avg"])
    )
    print_result("Concurrent requests", num_concurrent)
    print_result(
        "Speedup vs sequential",
        f"{(results.get('get_clients_avg', 0) * num_concurrent / timer.elapsed):.1f}x",
    )

    # Test mixed concurrent requests
    print("\n🔄 Testing mixed concurrent requests (devices + clients)...")
    with PerformanceTimer("concurrent_mixed") as timer:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for _ in range(5):
                futures.append(executor.submit(fetch_devices))
                futures.append(executor.submit(fetch_clients))
            results_list = [future.result() for future in as_completed(futures)]
    results["concurrent_mixed_total"] = timer.elapsed
    print_result("Total time", format_duration(timer.elapsed))
    print_result("Requests completed", len(futures))

    return results


def test_memory_usage(controller: UniFiController) -> Dict[str, float]:
    """Test memory usage of operations."""
    print_header("Test 4: Memory Usage Analysis")

    results = {}

    # Start memory tracking
    tracemalloc.start()

    # Get baseline memory
    baseline = tracemalloc.get_traced_memory()[0]
    print_result("Baseline memory", f"{baseline / 1024 / 1024:.2f} MB")

    # Test memory for get_devices
    print("\n🖥️  Testing memory usage for get_devices...")
    snapshot1 = tracemalloc.take_snapshot()
    devices = controller.get_devices()
    snapshot2 = tracemalloc.take_snapshot()

    current, peak = tracemalloc.get_traced_memory()
    results["devices_memory_current"] = current - baseline
    results["devices_memory_peak"] = peak - baseline
    print_result("Current memory", f"{results['devices_memory_current'] / 1024:.1f} KB")
    print_result("Peak memory", f"{results['devices_memory_peak'] / 1024:.1f} KB")
    print_result(
        "Memory per device",
        f"{results['devices_memory_current'] / len(devices):.1f} bytes",
    )

    # Test memory for get_clients
    print("\n👥 Testing memory usage for get_clients...")
    tracemalloc.reset_peak()
    baseline2 = tracemalloc.get_traced_memory()[0]
    clients = controller.get_clients()
    current, peak = tracemalloc.get_traced_memory()
    results["clients_memory_current"] = current - baseline2
    results["clients_memory_peak"] = peak - baseline2
    print_result("Current memory", f"{results['clients_memory_current'] / 1024:.1f} KB")
    print_result("Peak memory", f"{results['clients_memory_peak'] / 1024:.1f} KB")
    print_result(
        "Memory per client",
        f"{results['clients_memory_current'] / len(clients):.1f} bytes",
    )

    # Test memory for repeated requests (check for leaks)
    print("\n🔁 Testing for memory leaks (100 repeated requests)...")
    tracemalloc.reset_peak()
    baseline3 = tracemalloc.get_traced_memory()[0]
    for _ in range(100):
        devices = controller.get_devices()
    current, peak = tracemalloc.get_traced_memory()
    results["leak_test_memory"] = current - baseline3
    results["leak_test_peak"] = peak - baseline3
    print_result(
        "Memory after 100 requests", f"{results['leak_test_memory'] / 1024:.1f} KB"
    )
    print_result("Peak memory", f"{results['leak_test_peak'] / 1024:.1f} KB")

    if results["leak_test_memory"] < results["devices_memory_current"] * 2:
        print("  ✅ No significant memory leak detected")
    else:
        print("  ⚠️  Possible memory leak detected")

    tracemalloc.stop()

    return results


def test_session_reuse(controller: UniFiController) -> Dict[str, float]:
    """Test efficiency of session reuse."""
    print_header("Test 5: Session Reuse Efficiency")

    results = {}

    # Test with session reuse (current implementation)
    print("\n♻️  Testing with session reuse...")
    controller.login()  # Ensure logged in
    with PerformanceTimer("with_session_reuse") as timer:
        for _ in range(20):
            devices = controller.get_devices()
    results["with_session_reuse"] = timer.elapsed
    print_result("20 requests with session reuse", format_duration(timer.elapsed))
    print_result("Average per request", format_duration(timer.elapsed / 20))

    # Test without session reuse (new instance each time)
    print("\n🔄 Testing without session reuse (baseline comparison)...")
    with PerformanceTimer("without_session_reuse") as timer:
        for _ in range(20):
            temp_controller = UniFiController(
                host=config.CONTROLLER_HOST,
                username=config.CONTROLLER_USERNAME,
                password=config.CONTROLLER_PASSWORD,
                port=config.CONTROLLER_PORT,
                site=config.CONTROLLER_SITE,
                verify_ssl=config.CONTROLLER_VERIFY_SSL,
            )
            temp_controller.login()
            devices = temp_controller.get_devices()
            temp_controller.logout()
    results["without_session_reuse"] = timer.elapsed
    print_result("20 requests without session reuse", format_duration(timer.elapsed))
    print_result("Average per request", format_duration(timer.elapsed / 20))

    # Calculate efficiency gain
    efficiency_gain = (
        results["without_session_reuse"] / results["with_session_reuse"] - 1
    ) * 100
    results["efficiency_gain_percent"] = efficiency_gain
    print_result("\nSession reuse efficiency gain", f"{efficiency_gain:.1f}%")

    return results


def generate_performance_report(all_results: Dict[str, Dict[str, float]]):
    """Generate a summary performance report."""
    print_header("Performance Test Summary")

    print("\n📊 Key Metrics:")
    print_result("Login time", format_duration(all_results["single"]["login"]))
    print_result(
        "Get devices (avg)", format_duration(all_results["single"]["get_devices_avg"])
    )
    print_result(
        "Get clients (avg)", format_duration(all_results["single"]["get_clients_avg"])
    )

    if "bulk_device_info_per_device" in all_results["bulk"]:
        print_result(
            "Device info retrieval",
            format_duration(all_results["bulk"]["bulk_device_info_per_device"]),
        )

    print("\n⚡ Performance Characteristics:")
    if "concurrent_devices_avg" in all_results["concurrent"]:
        print_result("Concurrent request handling", "✅ Supported")
        speedup = (
            all_results["single"]["get_devices_avg"]
            * 5
            / all_results["concurrent"]["concurrent_devices_total"]
        )
        print_result("Concurrency speedup", f"{speedup:.1f}x")

    print("\n💾 Memory Efficiency:")
    if "devices_memory_peak" in all_results["memory"]:
        print_result(
            "Device list memory",
            f"{all_results['memory']['devices_memory_peak'] / 1024:.1f} KB",
        )
    if "clients_memory_peak" in all_results["memory"]:
        print_result(
            "Client list memory",
            f"{all_results['memory']['clients_memory_peak'] / 1024:.1f} KB",
        )
    if "leak_test_memory" in all_results["memory"]:
        print_result(
            "Memory leak test",
            (
                "✅ Passed"
                if all_results["memory"]["leak_test_memory"] < 100 * 1024
                else "⚠️  Check needed"
            ),
        )

    print("\n♻️  Session Management:")
    if "efficiency_gain_percent" in all_results["session"]:
        print_result(
            "Session reuse efficiency",
            f"+{all_results['session']['efficiency_gain_percent']:.1f}%",
        )

    print("\n🎯 Recommendations:")

    # Check if operations are fast enough
    if all_results["single"]["get_devices_avg"] < 0.5:
        print("  ✅ Device retrieval is fast (< 0.5s)")
    else:
        print("  ⚠️  Device retrieval could be faster (consider caching)")

    if all_results["single"]["get_clients_avg"] < 0.5:
        print("  ✅ Client retrieval is fast (< 0.5s)")
    else:
        print("  ⚠️  Client retrieval could be faster (consider caching)")

    # Check concurrency
    if "concurrent_devices_avg" in all_results["concurrent"]:
        if (
            all_results["concurrent"]["concurrent_devices_avg"]
            < all_results["single"]["get_devices_avg"] * 1.5
        ):
            print("  ✅ Concurrent requests are efficient")
        else:
            print("  ⚠️  Concurrent requests have overhead (check connection pooling)")

    # Check session reuse
    if "efficiency_gain_percent" in all_results["session"]:
        if all_results["session"]["efficiency_gain_percent"] > 200:
            print("  ✅ Session reuse provides significant performance benefit")
        else:
            print("  ℹ️  Session reuse benefit is moderate")


def main():
    """Run all performance tests."""
    print("\n" + "=" * 80)
    print("  UniFi Controller Performance Testing")
    print("=" * 80)
    print(f"\n  Controller: {config.CONTROLLER_HOST}:{config.CONTROLLER_PORT}")
    print(f"  Site: {config.CONTROLLER_SITE}")

    # Initialize controller
    controller = UniFiController(
        host=config.CONTROLLER_HOST,
        username=config.CONTROLLER_USERNAME,
        password=config.CONTROLLER_PASSWORD,
        port=config.CONTROLLER_PORT,
        site=config.CONTROLLER_SITE,
        verify_ssl=config.CONTROLLER_VERIFY_SSL,
    )

    all_results = {}

    try:
        # Run all tests
        all_results["single"] = test_single_operations(controller)
        all_results["bulk"] = test_bulk_operations(controller)
        all_results["concurrent"] = test_concurrent_requests(controller)
        all_results["memory"] = test_memory_usage(controller)
        all_results["session"] = test_session_reuse(controller)

        # Generate summary report
        generate_performance_report(all_results)

        print("\n" + "=" * 80)
        print("  ✅ Performance Testing Complete!")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Clean up
        try:
            controller.logout()
        except Exception:
            pass


if __name__ == "__main__":
    main()

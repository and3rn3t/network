"""
Standalone UniFi data collection script.

Collects data from UniFi Controller and stores it in the database.
Supports both one-time collection and daemon mode.
"""

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.collector.orchestrator import create_orchestrator_from_config_file

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO", log_file: str = None):
    """Set up logging configuration."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=handlers,
    )


def print_stats(stats: dict):
    """Print collection statistics in a readable format."""
    print("\n" + "=" * 60)
    print("Collection Statistics")
    print("=" * 60)

    # Overall stats
    print(f"\n⏱️  Duration: {stats.get('duration_seconds', 0):.2f}s")
    print(f"🔧 Collectors run: {stats.get('collectors_run', 0)}")
    print(f"❌ Collectors failed: {stats.get('collectors_failed', 0)}")
    print(f"⚠️  Total errors: {stats.get('total_errors', 0)}")

    # Cloud collector stats
    if stats.get("cloud_stats"):
        cloud = stats["cloud_stats"]
        print(f"\n☁️  Cloud Collector:")
        print(f"   - Hosts processed: {cloud.get('hosts_processed', 0)}")
        print(f"   - Hosts created: {cloud.get('hosts_created', 0)}")
        print(f"   - Hosts updated: {cloud.get('hosts_updated', 0)}")
        print(f"   - Status records: {cloud.get('status_records', 0)}")
        print(f"   - Events created: {cloud.get('events_created', 0)}")
        print(f"   - Metrics created: {cloud.get('metrics_created', 0)}")

    # UniFi Controller stats
    if stats.get("unifi_stats"):
        unifi = stats["unifi_stats"]
        print(f"\n🌐 UniFi Controller Collector:")
        print(f"   - Devices processed: {unifi.get('devices_processed', 0)}")
        print(f"   - Devices created: {unifi.get('devices_created', 0)}")
        print(f"   - Devices updated: {unifi.get('devices_updated', 0)}")
        print(f"   - Clients processed: {unifi.get('clients_processed', 0)}")
        print(f"   - Clients created: {unifi.get('clients_created', 0)}")
        print(f"   - Clients updated: {unifi.get('clients_updated', 0)}")
        print(f"   - Status records: {unifi.get('status_records', 0)}")
        print(f"   - Events created: {unifi.get('events_created', 0)}")
        print(f"   - Metrics created: {unifi.get('metrics_created', 0)}")

    print("\n" + "=" * 60)


def run_once(config_file: str, verbose: bool = False):
    """Run collection once and exit."""
    print(f"Starting single collection cycle...")
    print(f"Config file: {config_file}")
    print()

    try:
        # Create orchestrator from config
        orchestrator = create_orchestrator_from_config_file(config_file)

        # Get initial stats
        initial_stats = orchestrator.get_stats()
        print(f"Collectors configured: {initial_stats['collectors_configured']}")
        print()

        # Run collection
        start_time = datetime.now()
        print(f"Collection started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        stats = orchestrator.collect_all()

        # Print results
        if verbose:
            print_stats(stats)
        else:
            print(f"\n✅ Collection completed in {stats['duration_seconds']:.2f}s")
            if stats.get("unifi_stats"):
                unifi = stats["unifi_stats"]
                print(
                    f"   - {unifi.get('devices_processed', 0)} devices, "
                    f"{unifi.get('clients_processed', 0)} clients processed"
                )
            if stats["total_errors"] > 0:
                print(f"   - ⚠️  {stats['total_errors']} errors encountered")

        # Close orchestrator
        orchestrator.close()

        return 0

    except KeyboardInterrupt:
        print("\n\nCollection interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Collection failed: {e}", exc_info=True)
        print(f"\n❌ Collection failed: {e}")
        return 1


def run_daemon(config_file: str, interval: int = 300, verbose: bool = False):
    """Run collection continuously in daemon mode."""
    print(f"Starting collection daemon...")
    print(f"Config file: {config_file}")
    print(f"Collection interval: {interval} seconds ({interval/60:.1f} minutes)")
    print()
    print("Press Ctrl+C to stop")
    print()

    try:
        # Create orchestrator from config
        orchestrator = create_orchestrator_from_config_file(config_file)

        # Get initial stats
        initial_stats = orchestrator.get_stats()
        print(f"Collectors configured: {initial_stats['collectors_configured']}")
        print()

        cycle = 0

        while True:
            cycle += 1
            start_time = datetime.now()

            print(f"[Cycle {cycle}] Starting at {start_time.strftime('%H:%M:%S')}")

            try:
                # Run collection
                stats = orchestrator.collect_all()

                # Print summary
                if verbose:
                    print_stats(stats)
                else:
                    print(
                        f"[Cycle {cycle}] Completed in {stats['duration_seconds']:.2f}s"
                    )
                    if stats.get("unifi_stats"):
                        unifi = stats["unifi_stats"]
                        print(
                            f"             {unifi.get('devices_processed', 0)} devices, "
                            f"{unifi.get('clients_processed', 0)} clients, "
                            f"{unifi.get('events_created', 0)} events"
                        )
                    if stats["total_errors"] > 0:
                        print(f"             ⚠️  {stats['total_errors']} errors")

            except Exception as e:
                logger.error(f"Collection cycle {cycle} failed: {e}", exc_info=True)
                print(f"[Cycle {cycle}] ❌ Failed: {e}")

            # Calculate sleep time
            elapsed = (datetime.now() - start_time).total_seconds()
            sleep_time = max(0, interval - elapsed)

            if sleep_time > 0:
                next_run = datetime.now().timestamp() + sleep_time
                next_run_time = datetime.fromtimestamp(next_run).strftime("%H:%M:%S")
                print(f"[Cycle {cycle}] Next collection at {next_run_time}")
                print()
                time.sleep(sleep_time)
            else:
                print(f"[Cycle {cycle}] ⚠️  Collection took longer than interval!")
                print()

    except KeyboardInterrupt:
        print("\n\n🛑 Daemon stopped by user")
        print("\nShutting down...")
        orchestrator.close()
        print("✅ Shutdown complete")
        return 0
    except Exception as e:
        logger.error(f"Daemon failed: {e}", exc_info=True)
        print(f"\n❌ Daemon failed: {e}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="UniFi data collection script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run once with default config
  python collect_unifi_data.py

  # Run in daemon mode (every 5 minutes)
  python collect_unifi_data.py --daemon --interval 300

  # Run with custom config file
  python collect_unifi_data.py --config my_config.py

  # Run with verbose output
  python collect_unifi_data.py --verbose

  # Run with debug logging
  python collect_unifi_data.py --log-level DEBUG
        """,
    )

    parser.add_argument(
        "--config",
        "-c",
        default="config.py",
        help="Path to configuration file (default: config.py)",
    )

    parser.add_argument(
        "--daemon",
        "-d",
        action="store_true",
        help="Run in daemon mode (continuous collection)",
    )

    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=300,
        help="Collection interval in seconds for daemon mode (default: 300)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed statistics",
    )

    parser.add_argument(
        "--log-level",
        "-l",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    parser.add_argument(
        "--log-file",
        help="Log file path (default: logs to stdout)",
    )

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.log_level, args.log_file)

    # Check if config file exists
    if not Path(args.config).exists():
        print(f"❌ Error: Config file not found: {args.config}")
        print()
        print("Please create a config.py file with your UniFi Controller settings.")
        print("See config.example.py for an example.")
        return 1

    # Run collection
    if args.daemon:
        return run_daemon(args.config, args.interval, args.verbose)
    else:
        return run_once(args.config, args.verbose)


if __name__ == "__main__":
    sys.exit(main())

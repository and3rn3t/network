"""Export UniFi Network data to various formats.

This script demonstrates data export capabilities including:
- CSV export (Excel-compatible)
- JSON export (API-ready)
- Prometheus metrics

Usage:
    # Export hosts to CSV
    python examples/export_data.py --format csv --type hosts

    # Export events to JSON
    python examples/export_data.py --format json --type events --days 30

    # Export metrics to CSV
    python examples/export_data.py --format csv --type metrics --days 7

    # Generate Prometheus metrics
    python examples/export_data.py --format prometheus
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.export import CSVExporter, JSONExporter, PrometheusExporter


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Export UniFi Network monitoring data")
    parser.add_argument(
        "--format",
        choices=["csv", "json", "prometheus"],
        default="json",
        help="Export format (default: json)",
    )
    parser.add_argument(
        "--type",
        choices=["hosts", "events", "metrics"],
        default="hosts",
        help="Data type to export (default: hosts)",
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: auto-generated)",
    )
    parser.add_argument(
        "--db",
        default="network.db",
        help="Database path (default: network.db)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days for events/metrics (default: 7)",
    )
    parser.add_argument(
        "--host-id",
        help="Filter metrics by host ID",
    )
    parser.add_argument(
        "--metric-name",
        help="Filter metrics by metric name",
    )

    args = parser.parse_args()

    # Generate output filename if not provided
    if args.output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if args.format == "prometheus":
            args.output = f"exports/prometheus_metrics_{timestamp}.txt"
        else:
            args.output = f"exports/{args.type}_{timestamp}.{args.format}"

    # Create output directory
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    # Export data
    try:
        if args.format == "csv":
            print(f"📊 Exporting {args.type} to CSV...")
            exporter = CSVExporter(args.db)

            if args.type == "hosts":
                count = exporter.export_hosts(args.output)
            elif args.type == "events":
                count = exporter.export_events(args.output, days=args.days)
            else:  # metrics
                count = exporter.export_metrics(
                    args.output,
                    host_id=args.host_id,
                    metric_name=args.metric_name,
                    days=args.days,
                )

            print(f"✅ Exported {count} rows to {args.output}")

        elif args.format == "json":
            print(f"📄 Exporting {args.type} to JSON...")
            exporter = JSONExporter(args.db)

            if args.type == "hosts":
                result = exporter.export_hosts(args.output)
            elif args.type == "events":
                result = exporter.export_events(args.output, days=args.days)
            else:  # metrics
                result = exporter.export_metrics(
                    args.output,
                    host_id=args.host_id,
                    metric_name=args.metric_name,
                    days=args.days,
                )

            print(f"✅ Exported {result['rows']} records to {args.output}")

        else:  # prometheus
            print("📈 Generating Prometheus metrics...")
            exporter = PrometheusExporter(args.db)
            count = exporter.export_to_file(args.output)
            print(f"✅ Generated {count} metrics in {args.output}")

            # Show sample
            with open(args.output, "r") as f:
                lines = f.readlines()
                print("\n📝 Sample metrics (first 10 lines):")
                for line in lines[:10]:
                    print(f"   {line.rstrip()}")

        return 0

    except Exception as e:
        print(f"❌ Error exporting data: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""Generate UniFi Network reports.

This script demonstrates report generation capabilities including:
- Daily/weekly/monthly reports
- HTML and PDF export
- Email delivery (optional)

Usage:
    # Generate daily report (HTML only)
    python examples/generate_report.py --type daily

    # Generate weekly report with PDF
    python examples/generate_report.py --type weekly --pdf

    # Generate monthly report and email it
    python examples/generate_report.py --type monthly --email

    # Custom database location
    python examples/generate_report.py --type daily --db /path/to/network.db
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.reports.report_generator import ReportConfig, ReportGenerator, ReportType


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate UniFi Network monitoring reports"
    )
    parser.add_argument(
        "--type",
        choices=["daily", "weekly", "monthly"],
        default="daily",
        help="Report type (default: daily)",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Generate PDF in addition to HTML (requires weasyprint)",
    )
    parser.add_argument(
        "--email",
        action="store_true",
        help="Send report via email (requires email config in config.py)",
    )
    parser.add_argument(
        "--db",
        default="network.db",
        help="Database path (default: network.db)",
    )
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Output directory for reports (default: reports)",
    )

    args = parser.parse_args()

    # Create configuration
    config = ReportConfig(
        report_type=ReportType(args.type),
        database_path=args.db,
        enable_pdf=args.pdf,
        pdf_output_dir=args.output_dir,
    )

    # Load email config if needed
    if args.email:
        try:
            import config as cfg

            config.smtp_host = getattr(cfg, "SMTP_HOST", None)
            config.smtp_port = getattr(cfg, "SMTP_PORT", 587)
            config.smtp_username = getattr(cfg, "SMTP_USERNAME", None)
            config.smtp_password = getattr(cfg, "SMTP_PASSWORD", None)
            config.email_from = getattr(cfg, "EMAIL_FROM", None)
            config.email_to = getattr(cfg, "EMAIL_TO", [])
        except ImportError:
            print("Warning: config.py not found. Email settings not loaded.")

    # Create report generator
    print(f"🌐 Generating {args.type} UniFi Network report...")
    generator = ReportGenerator(config)

    try:
        if args.email:
            # Generate and email report
            print("📧 Sending report via email...")
            success = generator.generate_and_email_report()

            if success:
                print("✅ Report sent successfully!")
            else:
                print("❌ Failed to send email. Check email configuration.")
                return 1

        else:
            # Generate and save report
            html_path = generator.generate_and_save_report()
            print(f"✅ Report generated successfully!")
            print(f"📄 HTML: {html_path}")

            if args.pdf:
                pdf_path = html_path.replace(".html", ".pdf")
                if Path(pdf_path).exists():
                    print(f"📑 PDF: {pdf_path}")

        # Show summary
        report_data = generator.generate_report()
        summary = report_data["summary"]

        print("\n📊 Report Summary:")
        print(f"   Total Devices: {summary['total_devices']}")
        print(f"   Active: {summary['active_devices']}")
        print(f"   Offline: {summary['offline_devices']}")
        print(f"   Total Events: {summary['total_events']}")
        print(f"   Avg Health: {summary.get('average_health', 0):.1f}/100")

        return 0

    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

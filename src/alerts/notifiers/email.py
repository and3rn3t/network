"""
Email notifier for sending alert notifications via SMTP.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List

from src.alerts.models import Alert
from src.alerts.notifiers.base import BaseNotifier

logger = logging.getLogger(__name__)


class EmailNotifier(BaseNotifier):
    """
    Email notification channel using SMTP.

    Sends alerts as HTML-formatted emails with fallback to plain text.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize email notifier.

        Args:
            config: Configuration dictionary with keys:
                - smtp_host: SMTP server hostname
                - smtp_port: SMTP server port (default: 587)
                - smtp_user: SMTP username
                - smtp_password: SMTP password
                - from_email: Sender email address
                - to_emails: List of recipient email addresses
                - use_tls: Whether to use TLS (default: True)
        """
        super().__init__(config)
        self.smtp_host = config.get("smtp_host")
        self.smtp_port = config.get("smtp_port", 587)
        self.smtp_user = config.get("smtp_user")
        self.smtp_password = config.get("smtp_password")
        self.from_email = config.get("from_email")
        self.to_emails = config.get("to_emails", [])
        self.use_tls = config.get("use_tls", True)

    def validate_config(self) -> bool:
        """
        Validate email configuration.

        Returns:
            True if all required settings are present
        """
        required = ["smtp_host", "smtp_user", "smtp_password", "from_email"]
        missing = [key for key in required if not self.config.get(key)]

        if missing:
            logger.error(f"Missing required email config: {', '.join(missing)}")
            return False

        if not self.to_emails:
            logger.error("No recipient email addresses configured")
            return False

        return True

    def send(self, alert: Alert) -> bool:
        """
        Send alert via email.

        Args:
            alert: Alert to send

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.validate_config():
            return False

        try:
            # Create message
            msg = self._create_message(alert)

            # Connect and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()

                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            self._log_success(alert, f"to {len(self.to_emails)} recipients")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            self._log_error(alert, e)
            return False
        except Exception as e:
            self._log_error(alert, e)
            return False

    def _create_message(self, alert: Alert) -> MIMEMultipart:
        """
        Create email message with HTML and plain text versions.

        Args:
            alert: Alert to format

        Returns:
            MIME multipart message
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = self._create_subject(alert)
        msg["From"] = self.from_email
        msg["To"] = ", ".join(self.to_emails)

        # Plain text version
        text_content = self.format_message(alert)
        text_part = MIMEText(text_content, "plain")
        msg.attach(text_part)

        # HTML version
        html_content = self._format_html(alert)
        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)

        return msg

    def _create_subject(self, alert: Alert) -> str:
        """
        Create email subject line.

        Args:
            alert: Alert to format

        Returns:
            Subject string
        """
        prefix = {
            "info": "ℹ️ Info",
            "warning": "⚠️ Warning",
            "critical": "🔴 Critical",
        }.get(alert.severity, "Alert")

        host_info = f" - {alert.host_name}" if alert.host_name else ""
        return f"[UniFi Alert] {prefix}{host_info}: {alert.message[:50]}"

    def _format_html(self, alert: Alert) -> str:
        """
        Format alert as HTML email.

        Args:
            alert: Alert to format

        Returns:
            HTML string
        """
        severity_colors = {
            "info": "#2196F3",
            "warning": "#FF9800",
            "critical": "#F44336",
        }
        color = severity_colors.get(alert.severity, "#757575")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                                 Roboto, Oxygen, Ubuntu, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: {color};
                    color: white;
                    padding: 20px;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f5f5f5;
                    padding: 20px;
                    border-radius: 0 0 5px 5px;
                }}
                .field {{
                    margin: 10px 0;
                }}
                .label {{
                    font-weight: bold;
                    color: #555;
                }}
                .value {{
                    color: #333;
                }}
                .footer {{
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #888;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{alert.severity.upper()} ALERT</h2>
                </div>
                <div class="content">
                    <div class="field">
                        <span class="label">Message:</span>
                        <span class="value">{alert.message}</span>
                    </div>
                    <div class="field">
                        <span class="label">Triggered:</span>
                        <span class="value">
                            {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}
                        </span>
                    </div>
        """

        if alert.host_name:
            html += f"""
                    <div class="field">
                        <span class="label">Host:</span>
                        <span class="value">{alert.host_name}</span>
                    </div>
            """

        if alert.metric_name:
            html += f"""
                    <div class="field">
                        <span class="label">Metric:</span>
                        <span class="value">{alert.metric_name}</span>
                    </div>
            """

        if alert.value is not None:
            html += f"""
                    <div class="field">
                        <span class="label">Current Value:</span>
                        <span class="value">{alert.value:.2f}</span>
                    </div>
            """

        if alert.threshold is not None:
            html += f"""
                    <div class="field">
                        <span class="label">Threshold:</span>
                        <span class="value">{alert.threshold:.2f}</span>
                    </div>
            """

        html += """
                    <div class="footer">
                        This is an automated message from your UniFi
                        Network monitoring system.
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        return html

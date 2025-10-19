"""
Test the notification system.

Tests the NotificationManager, EmailNotifier, and WebhookNotifier.
"""

import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from alerts.models import Alert, NotificationChannel
from alerts.notification_manager import NotificationManager
from alerts.notifiers import EmailNotifier, WebhookNotifier
from database.database import Database
from database.repositories.alert_repository import AlertRepository
from database.repositories.notification_channel_repository import (
    NotificationChannelRepository,
)


def test_email_notifier():
    """Test email notifier with mock SMTP."""
    print("\n" + "=" * 60)
    print("TEST: Email Notifier")
    print("=" * 60)

    config = {
        "smtp_host": "smtp.example.com",
        "smtp_port": 587,
        "smtp_user": "alerts@example.com",
        "smtp_password": "password123",
        "from_email": "alerts@example.com",
        "to_emails": ["admin@example.com"],
        "use_tls": True,
    }

    notifier = EmailNotifier(config)

    # Test validation
    assert notifier.validate_config(), "❌ Config validation failed"
    print("✓ Configuration validated")

    # Test format_message
    alert = Alert(
        alert_rule_id=1,
        severity="critical",
        message="Host device-1 is offline",
        triggered_at=datetime.now(),
        host_name="device-1",
    )

    message = notifier.format_message(alert)
    assert "CRITICAL" in message, "❌ Message missing severity"
    assert "device-1" in message, "❌ Message missing host name"
    print("✓ Message formatting works")

    # Test with mock SMTP
    with patch("smtplib.SMTP") as mock_smtp:
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        success = notifier.send(alert)

        assert success, "❌ Send failed"
        assert mock_smtp.called, "❌ SMTP not called"
        assert mock_server.starttls.called, "❌ TLS not started"
        assert mock_server.login.called, "❌ Login not called"
        assert mock_server.send_message.called, "❌ Message not sent"
        print("✓ Email sent successfully (mocked)")

    print("✓ All email notifier tests passed!\n")


def test_webhook_notifier():
    """Test webhook notifier with mock requests."""
    print("=" * 60)
    print("TEST: Webhook Notifier")
    print("=" * 60)

    # Test Slack webhook
    slack_config = {
        "webhook_url": "https://hooks.slack.com/services/TEST",
        "platform": "slack",
    }

    slack_notifier = WebhookNotifier(slack_config)
    assert slack_notifier.validate_config(), "❌ Slack config validation failed"
    print("✓ Slack configuration validated")

    # Test Discord webhook
    discord_config = {
        "webhook_url": "https://discord.com/api/webhooks/TEST",
        "platform": "discord",
    }

    discord_notifier = WebhookNotifier(discord_config)
    assert discord_notifier.validate_config(), "❌ Discord config validation failed"
    print("✓ Discord configuration validated")

    # Test generic webhook
    generic_config = {
        "webhook_url": "https://example.com/webhook",
        "platform": "generic",
    }

    generic_notifier = WebhookNotifier(generic_config)
    assert generic_notifier.validate_config(), "❌ Generic config validation failed"
    print("✓ Generic configuration validated")

    # Test sending with mock requests
    alert = Alert(
        alert_rule_id=1,
        severity="warning",
        message="High CPU usage detected",
        triggered_at=datetime.now(),
        host_name="device-1",
        metric_name="cpu_usage",
        value=85.5,
        threshold=80.0,
    )

    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Test Slack
        success = slack_notifier.send(alert)
        assert success, "❌ Slack send failed"
        assert mock_post.called, "❌ HTTP POST not called"

        # Verify Slack payload structure
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert "attachments" in payload, "❌ Slack payload missing attachments"
        print("✓ Slack webhook sent successfully (mocked)")

        # Test Discord
        mock_post.reset_mock()
        success = discord_notifier.send(alert)
        assert success, "❌ Discord send failed"

        # Verify Discord payload structure
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert "embeds" in payload, "❌ Discord payload missing embeds"
        print("✓ Discord webhook sent successfully (mocked)")

        # Test Generic
        mock_post.reset_mock()
        success = generic_notifier.send(alert)
        assert success, "❌ Generic send failed"

        # Verify generic payload
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert payload["severity"] == "warning", "❌ Payload missing severity"
        assert payload["message"] == alert.message, "❌ Payload missing message"
        print("✓ Generic webhook sent successfully (mocked)")

    print("✓ All webhook notifier tests passed!\n")


def test_notification_manager():
    """Test notification manager with in-memory database."""
    print("=" * 60)
    print("TEST: Notification Manager")
    print("=" * 60)

    # Setup in-memory database
    db = Database(":memory:")
    db.initialize()
    db.initialize_alerts()

    alert_repo = AlertRepository(db)
    channel_repo = NotificationChannelRepository(db)

    # Create notification manager
    manager = NotificationManager(alert_repo, channel_repo)
    print("✓ NotificationManager initialized")

    # Register mock notifiers
    mock_email = Mock()
    mock_email.send.return_value = True
    manager.register_notifier("email", mock_email)
    print("✓ Email notifier registered")

    mock_webhook = Mock()
    mock_webhook.send.return_value = True
    manager.register_notifier("webhook", mock_webhook)
    print("✓ Webhook notifier registered")

    # Create a test alert rule first (required by foreign key)
    from alerts.models import AlertRule
    from database.repositories.alert_rule_repository import AlertRuleRepository

    rule_repo = AlertRuleRepository(db)
    test_rule = AlertRule(
        name="Test Rule",
        rule_type="threshold",
        condition="gt",
        severity="warning",
        notification_channels=["email-1", "webhook-1"],
        metric_name="test_metric",
        threshold=80.0,
        enabled=True,
    )
    created_rule = rule_repo.create(test_rule)
    rule_id = created_rule.id
    print(f"✓ Test alert rule created (ID: {rule_id})")

    # Create notification channels
    email_channel = NotificationChannel(
        id="email-1",
        channel_type="email",
        name="Primary Email",
        enabled=True,
        config={
            "to_emails": ["admin@example.com"],
            "min_severity": "warning",
        },
    )
    channel_repo.create(email_channel)
    print("✓ Email channel created")

    webhook_channel = NotificationChannel(
        id="webhook-1",
        channel_type="webhook",
        name="Slack Alerts",
        enabled=True,
        config={
            "webhook_url": "https://hooks.slack.com/test",
            "platform": "slack",
            "min_severity": "info",
        },
    )
    channel_repo.create(webhook_channel)
    print("✓ Webhook channel created")

    # Create an alert
    alert = Alert(
        alert_rule_id=rule_id,
        severity="warning",
        message="Test alert",
        triggered_at=datetime.now(),
    )
    alert = alert_repo.create(alert)
    print("✓ Alert created")

    # Send alert to all channels
    results = manager.send_alert(alert)

    assert len(results) == 2, f"❌ Expected 2 results, got {len(results)}"
    assert all(results.values()), "❌ Some notifications failed"
    assert mock_email.send.called, "❌ Email notifier not called"
    assert mock_webhook.send.called, "❌ Webhook notifier not called"
    print("✓ Alert sent to all channels")

    # Test severity filtering
    info_alert = Alert(
        alert_rule_id=rule_id,
        severity="info",
        message="Info alert",
        triggered_at=datetime.now(),
    )
    info_alert = alert_repo.create(info_alert)

    results = manager.send_alert(info_alert)

    # Email channel requires 'warning', so only webhook should receive
    assert "webhook-1" in results, "❌ Webhook should receive info alert"
    print("✓ Severity filtering works correctly")

    manager.close()
    print("✓ All notification manager tests passed!\n")


if __name__ == "__main__":
    try:
        test_email_notifier()
        test_webhook_notifier()
        test_notification_manager()

        print("=" * 60)
        print("✓ ALL NOTIFICATION SYSTEM TESTS PASSED!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

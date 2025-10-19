# Alert CLI Tool - User Guide

**Command-Line Interface for UniFi Network Alert System**

---

## Overview

The `unifi-alerts` CLI provides a comprehensive command-line interface for managing alert rules, viewing alerts, configuring notification channels, and controlling alert system behavior.

## Installation & Setup

### Prerequisites

- Python 3.8+
- UniFi Network database initialized with alert schema

### Running the CLI

**On Windows (PowerShell):**

```powershell
$env:PYTHONPATH="C:\git\network\src"
python -m alerts.cli [command]
```

**Using the convenience wrapper:**

```powershell
.\unifi-alerts.ps1 [command]
```

**Specify custom database:**

```bash
python -m alerts.cli --db /path/to/database.db [command]
```

---

## Command Structure

```
alerts.cli [--db PATH] <command> <subcommand> [options]
```

### Available Commands

1. **rule** - Manage alert rules
2. **alert** - Manage alerts
3. **channel** - Manage notification channels
4. **mute** - Manage rule mutes
5. **evaluate** - Run alert evaluation

---

## Rule Management

### Create a Rule

Create a new alert rule:

```bash
alerts.cli rule create \
  --name "High CPU Alert" \
  --type threshold \
  --metric cpu_usage \
  --condition gt \
  --threshold 85 \
  --severity warning \
  --channels email-1,slack-1 \
  --description "Alert when CPU exceeds 85%" \
  --cooldown 30
```

**Options:**

- `--name` (required) - Rule name
- `--type` (required) - Rule type: `threshold`, `status_change`
- `--metric` (required) - Metric name to monitor
- `--condition` (required) - Condition: `gt`, `gte`, `lt`, `lte`, `eq`, `ne`
- `--threshold` (required) - Threshold value
- `--severity` (required) - Severity: `info`, `warning`, `critical`
- `--channels` (required) - Comma-separated channel IDs
- `--description` - Rule description
- `--host` - Filter by specific host MAC address
- `--cooldown` - Cooldown minutes (default: 30)
- `--disabled` - Create rule in disabled state

**Examples:**

```bash
# High memory alert
alerts.cli rule create --name "High Memory" --type threshold \
  --metric memory_usage --condition gt --threshold 90 \
  --severity critical --channels email-1

# Device offline alert
alerts.cli rule create --name "Device Offline" --type status_change \
  --metric status --condition eq --threshold 0 \
  --severity critical --channels email-1,slack-1

# Host-specific alert
alerts.cli rule create --name "Router CPU" --type threshold \
  --metric cpu_usage --condition gt --threshold 70 \
  --severity warning --channels email-1 \
  --host "00:11:22:33:44:55"
```

### List Rules

```bash
# List all rules
alerts.cli rule list

# List only enabled rules
alerts.cli rule list --enabled-only
```

**Output:**

```
ID    Name                Type      Condition           Severity  Enabled
------------------------------------------------------------------------------
1     High CPU Alert      threshold cpu_usage gt 85.0  warning   ✓
2     Device Offline      status    status eq 0.0      critical  ✓
```

### Show Rule Details

```bash
alerts.cli rule show <rule_id>
```

**Example:**

```bash
alerts.cli rule show 1
```

**Output:**

```
📋 Rule Details
============================================================
ID:                  1
Name:                High CPU Alert
Description:         Alert when CPU exceeds 85%
Type:                threshold
Metric:              cpu_usage
Condition:           gt 85.0
Severity:            ⚠️  WARNING
Enabled:             Yes
Cooldown:            30 minutes
Channels:            email-1
Host Filter:         All hosts
Created:             2025-10-18 14:30:00
Updated:             2025-10-18 14:30:00
```

### Enable/Disable Rules

```bash
# Enable a rule
alerts.cli rule enable <rule_id>

# Disable a rule
alerts.cli rule disable <rule_id>
```

### Delete a Rule

```bash
# Delete with confirmation
alerts.cli rule delete <rule_id>

# Delete without confirmation
alerts.cli rule delete <rule_id> --force
```

---

## Alert Management

### List Alerts

```bash
# List active alerts
alerts.cli alert list

# Filter by severity
alerts.cli alert list --severity critical

# Filter by host
alerts.cli alert list --host "00:11:22:33:44:55"

# Show recent alerts (last N hours)
alerts.cli alert list --recent 24
```

**Output:**

```
ID    Rule                  Severity   Host            Value   Triggered
------------------------------------------------------------------------------
5     High CPU Alert        warning    00:11:22:33:44  92.5    2025-10-18 15:30:00
6     Device Offline        critical   00:aa:bb:cc:dd  0.0     2025-10-18 16:00:00
```

### Show Alert Details

```bash
alerts.cli alert show <alert_id>
```

**Output:**

```
🚨 Alert Details
============================================================
ID:                  5
Rule ID:             1
Rule Name:           High CPU Alert
Severity:            ⚠️  WARNING
Host ID:             00:11:22:33:44:55
Current Value:       92.5
Threshold:           85.0
Message:             CPU usage (92.5%) exceeded threshold (85.0%)
Triggered:           2025-10-18 15:30:00
Acknowledged:        N/A
Resolved:            N/A

📬 Notification Status:
  ✓ email-1: sent
  ✓ slack-1: sent
```

### Acknowledge an Alert

```bash
alerts.cli alert acknowledge <alert_id> --by "admin"
```

### Resolve an Alert

```bash
alerts.cli alert resolve <alert_id>
```

### View Alert Statistics

```bash
# Last 7 days (default)
alerts.cli alert stats

# Custom time period
alerts.cli alert stats --days 30
```

**Output:**

```
📊 Alert Statistics (Last 7 days)
============================================================
ℹ️  Info:             5
⚠️  Warning:          12
🔴 Critical:         3
────────────────────────────────────────────────────────────
Total:              20
```

---

## Notification Channel Management

### Create a Channel

Create a notification channel from a JSON config file:

```bash
alerts.cli channel create \
  --id "email-ops" \
  --name "Operations Email" \
  --type email \
  --config email_config.json
```

**Config File Examples:**

**email_config.json:**

```json
{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "alerts@example.com",
  "smtp_password": "app_password",
  "from_email": "alerts@example.com",
  "to_emails": ["ops@example.com", "admin@example.com"],
  "use_tls": true,
  "min_severity": "warning"
}
```

**slack_config.json:**

```json
{
  "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
  "platform": "slack",
  "timeout": 10,
  "min_severity": "warning"
}
```

**discord_config.json:**

```json
{
  "webhook_url": "https://discord.com/api/webhooks/YOUR_ID/TOKEN",
  "platform": "discord",
  "timeout": 10
}
```

### List Channels

```bash
# List all channels
alerts.cli channel list

# Filter by type
alerts.cli channel list --type email

# Show only enabled
alerts.cli channel list --enabled-only
```

**Output:**

```
ID                   Name                Type      Enabled
----------------------------------------------------------------
email-ops            Operations Email    email     ✓
slack-1              Slack Alerts        slack     ✓
discord-1            Discord Alerts      discord   ✗
```

### Enable/Disable Channels

```bash
# Enable
alerts.cli channel enable <channel_id>

# Disable
alerts.cli channel disable <channel_id>
```

---

## Mute Management

Temporarily mute alert rules to prevent notifications during maintenance windows or known issues.

### Mute a Rule

```bash
# Mute for specific duration
alerts.cli mute create <rule_id> \
  --duration 120 \
  --reason "System maintenance" \
  --by "admin"

# Mute indefinitely
alerts.cli mute create <rule_id> --reason "Under investigation"

# Mute for specific host only
alerts.cli mute create <rule_id> \
  --host "00:11:22:33:44:55" \
  --duration 60
```

**Options:**

- `--duration` - Duration in minutes (omit for indefinite)
- `--host` - Mute for specific host only
- `--reason` - Reason for muting
- `--by` - Who muted (default: "cli-user")

### List Active Mutes

```bash
alerts.cli mute list
```

**Output:**

```
Rule ID  Host                Expires              Reason
---------------------------------------------------------------------------
1        All                 2025-10-18 18:00:00  System maintenance
3        00:11:22:33:44:55   Never                Under investigation
```

### Remove a Mute

```bash
# Unmute rule for all hosts
alerts.cli mute remove <rule_id>

# Unmute for specific host
alerts.cli mute remove <rule_id> --host "00:11:22:33:44:55"
```

---

## Evaluation

Run alert evaluation manually:

```bash
# Evaluate without sending notifications
alerts.cli evaluate

# Evaluate and send notifications
alerts.cli evaluate --email-config email_config.json

# Verbose output
alerts.cli evaluate --verbose
```

**Output:**

```
✅ Evaluation complete: 3 alert(s) triggered

Triggered Alerts:
  ⚠️  WARNING High CPU on host 00:11:22:33:44:55
  🔴 CRITICAL Device offline: 00:aa:bb:cc:dd:ee
  ⚠️  WARNING High memory usage on host 00:22:33:44:55:66
```

---

## Common Workflows

### Setup a New Alert Rule

```bash
# 1. Create notification channel
alerts.cli channel create --id "email-1" --name "Admin Email" \
  --type email --config email_config.json

# 2. Create alert rule
alerts.cli rule create --name "High CPU" --type threshold \
  --metric cpu_usage --condition gt --threshold 80 \
  --severity warning --channels email-1

# 3. Test by evaluating
alerts.cli evaluate --email-config email_config.json --verbose

# 4. Check alerts
alerts.cli alert list
```

### Maintenance Window

```bash
# 1. Mute critical rules
alerts.cli mute create 1 --duration 120 --reason "Network maintenance"
alerts.cli mute create 2 --duration 120 --reason "Network maintenance"

# 2. Verify mutes
alerts.cli mute list

# 3. After maintenance, remove mutes (or let them expire)
alerts.cli mute remove 1
alerts.cli mute remove 2
```

### Daily Alert Review

```bash
# 1. Check statistics
alerts.cli alert stats --days 1

# 2. Review active alerts
alerts.cli alert list

# 3. Review critical alerts
alerts.cli alert list --severity critical

# 4. Acknowledge reviewed alerts
alerts.cli alert acknowledge 5 --by "admin"
alerts.cli alert acknowledge 6 --by "admin"
```

---

## Automation Examples

### PowerShell Script for Scheduled Evaluation

```powershell
# run-alerts.ps1
$env:PYTHONPATH = "C:\git\network\src"

# Run evaluation
$result = python -m alerts.cli evaluate --email-config email_config.json

if ($LASTEXITCODE -ne 0) {
    Write-Error "Alert evaluation failed"
    exit 1
}

# Cleanup stale alerts (could add CLI command for this)
# ...

Write-Host "Alert evaluation completed successfully"
```

### Scheduled Task (Windows)

```powershell
# Create scheduled task to run every 5 minutes
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-File C:\git\network\run-alerts.ps1"

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 5)

Register-ScheduledTask -TaskName "UniFi Alerts" `
    -Action $action -Trigger $trigger
```

---

## Troubleshooting

### Command Not Found

Ensure PYTHONPATH is set:

```powershell
$env:PYTHONPATH="C:\git\network\src"
```

### Database Not Found

Specify database path explicitly:

```bash
alerts.cli --db "C:\full\path\to\database.db" rule list
```

### Import Errors

Make sure you're in the project root directory and all dependencies are installed:

```bash
pip install -r requirements.txt
```

### Channel Config Validation Failed

Check your JSON config file:

```bash
# Validate JSON
python -c "import json; print(json.load(open('email_config.json')))"
```

---

## Tips & Best Practices

1. **Use Mutes During Maintenance** - Prevent alert spam
2. **Set Appropriate Cooldowns** - Avoid notification fatigue
3. **Use Severity Levels** - Configure channel min_severity
4. **Regular Stats Review** - Monitor alert trends
5. **Test Channels First** - Verify configs before production use
6. **Descriptive Names** - Use clear rule and channel names

---

## See Also

- `docs/ALERT_SYSTEM_QUICKREF.md` - Quick reference guide
- `docs/PHASE_4_STATUS_REPORT.md` - Complete system documentation
- `examples/email_config.example.json` - Example email config
- `examples/slack_config.example.json` - Example Slack config

---

**Version:** 1.0
**Last Updated:** October 18, 2025

# Alert Management UI - Manual Testing Guide

## Prerequisites

### 1. Start Backend Server

```powershell
cd c:\git\network\backend
python -m uvicorn src.main:app --reload
```

**Expected Output:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

**Verify:** Open <http://localhost:8000/docs> - should see FastAPI Swagger UI

### 2. Start Frontend Server

```powershell
cd c:\git\network\frontend
npm run dev
```

**Expected Output:**

```
VITE v5.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**Verify:** Open <http://localhost:5173> - should see login page

### 3. Login

- Navigate to <http://localhost:5173>
- Login with credentials (from backend auth)
- Should see Dashboard

---

## Testing Checklist

### Phase 1: Navigation (5 min)

**Goal:** Verify new menu structure

1. ✅ Look at left sidebar menu
2. ✅ Find "Alert System" menu item with Bell icon
3. ✅ Click to expand submenu - should see 3 items:
   - **Active Alerts** (Bell icon) - may have badge with count
   - **Alert Rules** (Thunderbolt icon)
   - **Notification Channels** (Notification icon)
4. ✅ Verify badge shows alert count (may be 0)

**Expected:** Submenu expands/collapses, all icons visible

---

### Phase 2: Alerts Page (15 min)

**URL:** <http://localhost:5173/alerts>

#### 2.1 Page Load

1. ✅ Click "Active Alerts" in menu
2. ✅ Page loads without errors
3. ✅ See page title: "Active Alerts" with badge
4. ✅ See description: "Monitor and manage network alerts"
5. ✅ See 3 summary cards:
   - **Active Alerts** (red) - count of triggered alerts
   - **Acknowledged** (orange) - count of acknowledged alerts
   - **Total Alerts** (green) - total count

**Screenshot Location:** Save as `docs/screenshots/alerts-01-overview.png`

#### 2.2 Filter Controls

1. ✅ See two dropdown filters:
   - **Status Filter:** All Statuses, Triggered, Acknowledged, Resolved
   - **Severity Filter:** (All), Critical, Warning, Info
2. ✅ Click Status filter - dropdown opens
3. ✅ Select "Triggered" - table updates
4. ✅ Click Severity filter - dropdown opens
5. ✅ Select "Critical" - table updates
6. ✅ Click "Refresh" button - data reloads

**Expected:** Filters work, table updates, no console errors

#### 2.3 Alerts Table

1. ✅ See table with columns:
   - Severity (icon + badge)
   - Message (with metric value)
   - Status (tag)
   - Triggered At (timestamp)
   - Actions (buttons)
2. ✅ If no alerts: See "No data" message
3. ✅ If alerts exist: See rows with colored severity badges

**To Test with Data:** You need to create alert rules and trigger them (see Phase 3)

#### 2.4 Alert Actions (if alerts exist)

1. ✅ Click "Acknowledge" button on an alert
2. ✅ See success message: "Alert acknowledged"
3. ✅ Alert status changes to "Acknowledged" (orange tag)
4. ✅ Acknowledged count increases
5. ✅ Click "Resolve" button on acknowledged alert
6. ✅ Modal opens: "Resolve Alert"
7. ✅ Enter notes: "Fixed by restarting device"
8. ✅ Click "Resolve"
9. ✅ See success message: "Alert resolved"
10. ✅ Alert status changes to "Resolved" (green tag)

**Screenshot Location:** Save as `docs/screenshots/alerts-02-actions.png`

#### 2.5 Alert Details Modal

1. ✅ Click anywhere on an alert row
2. ✅ Modal opens: "Alert Details"
3. ✅ See all alert information:
   - Severity (with icon)
   - Status (with color)
   - Message
   - Metric Value
   - Threshold
   - Triggered At timestamp
   - Acknowledged At (if acknowledged)
   - Resolved At (if resolved)
   - Notes (if resolved)
4. ✅ Click "Acknowledge" in modal - alert acknowledged
5. ✅ Click "Resolve" in modal - resolution modal opens
6. ✅ Click "Close" - modal closes

**Screenshot Location:** Save as `docs/screenshots/alerts-03-details.png`

---

### Phase 3: Rules Page (15 min)

**URL:** <http://localhost:5173/rules>

#### 3.1 Page Load

1. ✅ Click "Alert Rules" in menu
2. ✅ Page loads without errors
3. ✅ See page title: "Alert Rules"
4. ✅ See description: "Configure alert rules to monitor your network health"
5. ✅ See 3 summary cards:
   - **Total Rules** (blue)
   - **Enabled** (green)
   - **Disabled** (gray)
6. ✅ See "Create Rule" button (blue)
7. ✅ See "Refresh" button

**Screenshot Location:** Save as `docs/screenshots/rules-01-overview.png`

#### 3.2 Rules Table

1. ✅ See table with columns:
   - Name (with type & condition)
   - Threshold
   - Severity (badge)
   - Cooldown (minutes)
   - Status (toggle switch)
   - Actions (Edit/Delete buttons)
2. ✅ If no rules: See "No data" message

#### 3.3 Create Alert Rule

1. ✅ Click "Create Rule" button
2. ✅ Modal opens: "Create Alert Rule"
3. ✅ Fill in form:
   - **Rule Name:** "High CPU Alert"
   - **Rule Type:** "Threshold"
   - **Severity:** "Warning"
   - **Condition:** "cpu_usage > threshold"
   - **Threshold Value:** 80
   - **Cooldown (minutes):** 60
   - **Enabled:** Toggle ON (blue)
4. ✅ Click "OK"
5. ✅ See success message: "Rule created successfully"
6. ✅ Table updates with new rule
7. ✅ Total Rules count increases
8. ✅ Enabled count increases

**Screenshot Location:** Save as `docs/screenshots/rules-02-create.png`

#### 3.4 Edit Rule

1. ✅ Click "Edit" button on a rule
2. ✅ Modal opens: "Edit Alert Rule"
3. ✅ Form pre-populated with existing values
4. ✅ Change Threshold Value: 85
5. ✅ Change Severity: "Critical"
6. ✅ Click "OK"
7. ✅ See success message: "Rule updated successfully"
8. ✅ Table shows updated values

**Screenshot Location:** Save as `docs/screenshots/rules-03-edit.png`

#### 3.5 Enable/Disable Rule

1. ✅ Find rule with toggle switch ON (green)
2. ✅ Click toggle switch
3. ✅ See success message: "Rule disabled"
4. ✅ Toggle turns gray/OFF
5. ✅ Enabled count decreases
6. ✅ Disabled count increases
7. ✅ Click toggle again
8. ✅ See success message: "Rule enabled"
9. ✅ Toggle turns green/ON

#### 3.6 Delete Rule

1. ✅ Click "Delete" button (red) on a rule
2. ✅ Confirmation modal appears
3. ✅ See warning: "Are you sure you want to delete this rule?"
4. ✅ Click "Cancel" - modal closes, nothing deleted
5. ✅ Click "Delete" again
6. ✅ Click "Delete" in confirmation
7. ✅ See success message: "Rule deleted successfully"
8. ✅ Rule removed from table
9. ✅ Total Rules count decreases

**Screenshot Location:** Save as `docs/screenshots/rules-04-delete.png`

---

### Phase 4: Channels Page (20 min)

**URL:** <http://localhost:5173/channels>

#### 4.1 Page Load

1. ✅ Click "Notification Channels" in menu
2. ✅ Page loads without errors
3. ✅ See page title: "Notification Channels"
4. ✅ See description: "Configure where and how alert notifications are delivered"
5. ✅ See 4 summary cards:
   - **Total Channels** (blue)
   - **Email** (green)
   - **Slack** (purple)
   - **Webhooks** (orange)
6. ✅ See "Add Channel" button (blue)
7. ✅ See "Refresh" button

**Screenshot Location:** Save as `docs/screenshots/channels-01-overview.png`

#### 4.2 Channels Table

1. ✅ See table with columns:
   - Name (with icon & type)
   - Configuration (summary)
   - Min Severity (badge)
   - Status (Enabled/Disabled tag)
   - Actions (Test/Edit/Delete buttons)
2. ✅ If no channels: See "No data" message

#### 4.3 Create Email Channel

1. ✅ Click "Add Channel" button
2. ✅ Modal opens: "Add Notification Channel"
3. ✅ Fill in form:
   - **Channel Name:** "Team Email Alerts"
   - **Channel Type:** Select "Email (SMTP)"
4. ✅ Form changes to show email-specific fields
5. ✅ Fill in email config:
   - **SMTP Host:** smtp.gmail.com
   - **SMTP Port:** 587
   - **SMTP Username:** <your-email@gmail.com>
   - **SMTP Password:** your-app-password
   - **From Email:** <alerts@yourcompany.com>
   - **To Emails:** <admin@yourcompany.com>
   - **Minimum Severity:** "Warning"
6. ✅ Click "OK"
7. ✅ See success message: "Channel created successfully"
8. ✅ Table updates with new channel
9. ✅ Email count increases

**Screenshot Location:** Save as `docs/screenshots/channels-02-email.png`

**Note:** Use Gmail App Password, not regular password. Generate at: <https://myaccount.google.com/apppasswords>

#### 4.4 Create Slack Channel

1. ✅ Click "Add Channel" button
2. ✅ Fill in form:
   - **Channel Name:** "Slack Critical Alerts"
   - **Channel Type:** Select "Slack"
3. ✅ Form shows webhook field
4. ✅ Fill in:
   - **Webhook URL:** <https://hooks.slack.com/services/YOUR/WEBHOOK/URL>
   - **Minimum Severity:** "Critical"
5. ✅ Click "OK"
6. ✅ Channel created
7. ✅ Slack count increases

**Screenshot Location:** Save as `docs/screenshots/channels-03-slack.png`

**To get Slack webhook:**

1. Go to <https://api.slack.com/apps>
2. Create New App → From scratch
3. Add Incoming Webhooks feature
4. Add webhook to workspace
5. Copy webhook URL

#### 4.5 Create Discord Channel

1. ✅ Click "Add Channel"
2. ✅ Fill in:
   - **Name:** "Discord Alerts"
   - **Type:** "Discord"
   - **Webhook URL:** Discord webhook URL
   - **Min Severity:** "Info"
3. ✅ Channel created

**To get Discord webhook:**

1. Open Discord server settings
2. Integrations → Webhooks
3. New Webhook
4. Copy webhook URL

#### 4.6 Test Channel

1. ✅ Click "Test" button on email channel
2. ✅ See message: "Test notification sent"
3. ✅ Check email inbox for test message
4. ✅ Verify email received with alert format
5. ✅ Click "Test" on Slack channel
6. ✅ Check Slack channel for test message

**Screenshot Location:** Save as `docs/screenshots/channels-04-test.png`

#### 4.7 Edit Channel

1. ✅ Click "Edit" button on a channel
2. ✅ Modal opens: "Edit Notification Channel"
3. ✅ Form pre-populated with existing config
4. ✅ **Channel Type dropdown is DISABLED** (can't change type)
5. ✅ Change Min Severity: "Critical"
6. ✅ Click "OK"
7. ✅ Channel updated

#### 4.8 Delete Channel

1. ✅ Click "Delete" button (red)
2. ✅ Confirmation modal appears
3. ✅ Click "Delete"
4. ✅ Channel removed from table

---

### Phase 5: Integration Testing (15 min)

**Goal:** Test full alert workflow

#### 5.1 Setup

1. ✅ Create alert rule (Rules page):
   - Name: "Test CPU Alert"
   - Type: Threshold
   - Condition: "cpu_usage > threshold"
   - Threshold: 50 (low threshold for easy triggering)
   - Severity: Warning
   - Cooldown: 1 minute
   - Enabled: ON
2. ✅ Create notification channel (Channels page):
   - Type: Email
   - Configure with your email
   - Min Severity: Info

#### 5.2 Trigger Alert

1. ✅ Wait for data collection (runs every 5 minutes)
2. ✅ OR manually trigger by updating device metrics in database
3. ✅ Check Alerts page - should see new alert
4. ✅ Alert appears with:
   - Severity: Warning (orange)
   - Status: Triggered (red tag)
   - Message includes CPU value and threshold

#### 5.3 Notification Received

1. ✅ Check email inbox
2. ✅ See alert notification email
3. ✅ Email contains:
   - Alert severity
   - Device information
   - Metric value vs threshold
   - Timestamp

#### 5.4 Alert Lifecycle

1. ✅ Navigate to Alerts page
2. ✅ Click "Acknowledge" on test alert
3. ✅ Alert status changes to "Acknowledged"
4. ✅ Check email - should receive acknowledgment notification
5. ✅ Click "Resolve" button
6. ✅ Enter notes: "Resolved by restarting device"
7. ✅ Click "Resolve"
8. ✅ Alert status changes to "Resolved"
9. ✅ Check email - should receive resolution notification

**Screenshot Location:** Save as `docs/screenshots/integration-workflow.png`

---

## Testing Results

### Summary

| Phase                  | Status | Issues | Notes |
| ---------------------- | ------ | ------ | ----- |
| Phase 1: Navigation    | ⏳     |        |       |
| Phase 2: Alerts Page   | ⏳     |        |       |
| Phase 3: Rules Page    | ⏳     |        |       |
| Phase 4: Channels Page | ⏳     |        |       |
| Phase 5: Integration   | ⏳     |        |       |

### Issues Found

Record any issues here:

1. **Issue:**
   - **Page:**
   - **Steps:**
   - **Expected:**
   - **Actual:**
   - **Severity:**

### Browser Console Errors

Check browser console (F12) during testing. Record any errors:

```
[Error messages here]
```

### Network Errors

Check Network tab in browser DevTools. Record failed API calls:

```
[Failed API calls here]
```

---

## Quick Start Command Summary

```powershell
# Terminal 1: Start Backend
cd c:\git\network\backend
python -m uvicorn src.main:app --reload

# Terminal 2: Start Frontend
cd c:\git\network\frontend
npm run dev

# Terminal 3: Test APIs (optional)
cd c:\git\network
.\scripts\test_alert_apis.ps1
```

---

## Success Criteria

All items must be ✅:

- [ ] All 3 pages load without errors
- [ ] Navigation submenu works correctly
- [ ] Create operations work (rules, channels)
- [ ] Edit operations work (rules, channels)
- [ ] Delete operations work (rules, channels)
- [ ] Enable/disable toggle works (rules)
- [ ] Test notification works (channels)
- [ ] Alert acknowledge works
- [ ] Alert resolve works
- [ ] Filters work (alerts page)
- [ ] Detail modal works (alerts page)
- [ ] No console errors
- [ ] No network errors
- [ ] End-to-end workflow complete

---

## Next Steps After Testing

Once all tests pass:

1. **Update status** in `docs/ALERT_MANAGEMENT_COMPLETE.md`
2. **Add screenshots** to `docs/screenshots/` folder
3. **Document any bugs** in GitHub issues
4. **Create user guide** with screenshots
5. **Deploy to production**

---

**Estimated Testing Time:** 60-70 minutes

**Tester:** ********\_\_\_********
**Date:** ********\_\_\_********
**Version:** Alert Management UI v1.0

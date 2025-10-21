# Device & Client Management - User Guide

## Table of Contents

1. [Overview](#overview)
2. [Accessing Management Features](#accessing-management-features)
3. [Device Management](#device-management)
4. [Client Management](#client-management)
5. [Bulk Operations](#bulk-operations)
6. [Safety & Best Practices](#safety--best-practices)
7. [Permissions & Requirements](#permissions--requirements)
8. [API Reference](#api-reference)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The Device & Client Management features provide comprehensive control over your UniFi network infrastructure. These tools allow you to:

### Device Management

- ✅ **Monitor** device status, performance, and health metrics
- ✅ **Control** devices remotely (reboot, restart, locate)
- ✅ **Configure** device names and settings
- ✅ **Analyze** detailed device information and statistics
- ✅ **Perform** bulk operations on multiple devices

### Client Management

- ✅ **View** all network clients with detailed information
- ✅ **Block/Unblock** clients from network access
- ✅ **Reconnect** clients experiencing connectivity issues
- ✅ **Set** bandwidth limits for Quality of Service (QoS)
- ✅ **Authorize** temporary guest access
- ✅ **Manage** multiple clients simultaneously

### Key Benefits

- 🎯 **Centralized Control** - Manage all devices and clients from one interface
- ⚡ **Real-time Operations** - Immediate feedback and status updates
- 🔄 **Bulk Actions** - Efficient management of multiple items
- 📊 **Detailed Insights** - Comprehensive device and client information
- 🛡️ **Safety Features** - Confirmation dialogs for destructive actions
- 🔍 **Search & Filter** - Quickly find specific devices or clients

---

## Accessing Management Features

### Navigation

1. **Device Management**

   - Click "Device Management" in the left sidebar
   - Or navigate to `/devices`

2. **Client Management**
   - Click "Client Management" in the left sidebar
   - Or navigate to `/clients`

### Dashboard Layout

Both management pages feature a consistent layout:

```
┌─────────────────────────────────────────┐
│  Statistics Cards (Total, Online, etc.) │
├─────────────────────────────────────────┤
│  Search & Filter Controls               │
├─────────────────────────────────────────┤
│  Main Data Table                        │
│  - Status indicators                    │
│  - Device/Client information            │
│  - Action buttons                       │
├─────────────────────────────────────────┤
│  Bulk Action Buttons                    │
└─────────────────────────────────────────┘
```

---

## Device Management

### Viewing Devices

The device table displays:

- **Status** - Online (green) or Offline (red)
- **Name** - Device identifier
- **Model** - Hardware model (e.g., UAP-AC-PRO, US-8-150W)
- **Type** - Device type (Access Point, Switch, Gateway)
- **IP Address** - Current network address
- **MAC Address** - Physical hardware address
- **Firmware** - Current firmware version
- **Uptime** - Time since last reboot (days, hours, minutes)

### Searching & Filtering

**Search Box**:

- Search by device name, MAC address, IP address, or model
- Real-time filtering as you type
- Case-insensitive matching

**Status Filter**:

- View all devices
- Filter by "Online" devices only
- Filter by "Offline" devices only

### Individual Device Actions

#### 1. Reboot Device

**Purpose**: Restart device completely (power cycle equivalent)

**Steps**:

1. Click the **Reboot** button (red) in the device row
2. Confirm the action in the dialog
3. Wait for device to restart (typically 30-60 seconds)

**When to Use**:

- Device is experiencing performance issues
- After firmware updates
- Scheduled maintenance
- Troubleshooting connectivity problems

⚠️ **Warning**: Rebooting will temporarily disconnect the device and all connected clients.

#### 2. Locate Device

**Purpose**: Blink device LED to physically identify it

**Steps**:

1. Click the **Locate** button in the device row
2. Device LED will blink for 30 seconds
3. Physically locate the device by the blinking light

**When to Use**:

- Finding device in equipment rack
- Verifying physical location
- Identifying device during installation

ℹ️ **Note**: Does not affect network operation.

#### 3. Rename Device

**Purpose**: Change device display name for better organization

**Steps**:

1. Click the **Edit** (pencil) icon in the device row
2. Enter new name (1-100 characters)
3. Click **Rename** to save

**Best Practices**:

- Use descriptive names (e.g., "Office AP 2nd Floor")
- Include location or function
- Avoid special characters that may cause issues
- Maintain consistent naming convention

#### 4. View Device Details

**Purpose**: Access comprehensive device information

**Steps**:

1. Click the **Info** (ℹ️) icon in the device row
2. Browse through tabs:

**Overview Tab**:

- Real-time statistics (CPU, Memory, Temperature)
- Device information (MAC, IP, Firmware)
- Network traffic summary
- Quick action buttons

**Ports Tab** (Switches only):

- Port status (Up/Down/Disabled)
- Speed and duplex mode
- PoE status and power consumption
- Traffic statistics per port

**Network Tab**:

- IP configuration (IP, Netmask, Gateway)
- DNS servers
- VLAN assignment
- Adopt IP address

**Events Tab**:

- Recent device events (online, offline, restart)
- Firmware updates history
- Configuration changes
- Error messages with timestamps

**Configuration Tab**:

- View current device configuration (JSON)
- Download configuration file
- Review device settings

**Metrics Tab** (Coming Soon):

- Historical CPU/Memory graphs
- Temperature trends
- Network traffic charts

### Bulk Device Operations

#### Bulk Reboot

**Purpose**: Reboot multiple devices simultaneously

**Steps**:

1. Select devices using checkboxes
2. Click **Bulk Reboot** button
3. Review selection in transfer component
   - Move devices between "Available" and "Selected"
   - Search for specific devices
   - Offline devices are automatically disabled
4. Click **Execute Operation**
5. Monitor progress in real-time
6. Review results (success/failed)
7. Retry failed operations if needed

**Selection Helpers**:

- **Select All** - Select all devices
- **Select Online** - Select only online devices
- **Select Offline** - Select only offline devices
- **Invert** - Invert current selection

**Best Practices**:

- Schedule during maintenance windows
- Start with a few devices to test
- Avoid rebooting critical devices during business hours
- Document reasons for maintenance logs

⚠️ **Warning**: Bulk operations can impact many users. Plan accordingly.

---

## Client Management

### Viewing Clients

The client table displays:

- **Status** - Active (green) or Blocked (red)
- **Client Name** - Friendly name or hostname
- **IP Address** - Current network address
- **MAC Address** - Physical address (unique identifier)
- **Connected To** - Device client is connected to
- **Signal Strength** - WiFi signal quality (dBm)
  - Excellent: ≥ -50 dBm (green)
  - Good: -50 to -60 dBm (blue)
  - Fair: < -60 dBm (orange)
- **Bandwidth Limits** - Current QoS restrictions
- **Device Type** - Icon showing device category (laptop, phone, tablet)

### Searching & Filtering

**Search Box**:

- Search by client name, MAC address, IP address, or hostname
- Real-time filtering
- Case-insensitive

**Status Filter**:

- View all clients
- Filter by "Active" clients only
- Filter by "Blocked" clients only

### Individual Client Actions

#### 1. Block Client

**Purpose**: Prevent client from accessing the network

**Steps**:

1. Click the **Block** button in the client row
2. Configure block settings:
   - **Reason** (optional): Document why client is blocked
   - **Type**: Permanent or Temporary
   - **Duration** (if temporary): 60 seconds to 24 hours
3. Click **Block** to confirm

**When to Use**:

- Security threats or unauthorized devices
- Policy violations
- Temporary access restriction
- Network abuse prevention

**Block Types**:

- **Permanent**: Remains blocked until manually unblocked
- **Temporary**: Automatically unblocks after specified duration

⚠️ **Warning**: Blocking immediately disconnects the client.

#### 2. Unblock Client

**Purpose**: Restore network access to blocked client

**Steps**:

1. Click the **Unblock** button in the client row
2. Confirm the action
3. Client can reconnect immediately

**When to Use**:

- Issue resolved
- Temporary block expired but showing as blocked
- Policy change
- False positive detection

#### 3. Reconnect Client

**Purpose**: Force client to disconnect and reconnect

**Steps**:

1. Click the **Reconnect** button in the client row
2. Client will be disconnected
3. Client will automatically reconnect

**When to Use**:

- Client experiencing connectivity issues
- Apply new VLAN or network settings
- Refresh DHCP lease
- Troubleshooting connection problems

ℹ️ **Note**: Only available for active (connected) clients.

#### 4. Set Bandwidth Limits

**Purpose**: Control Quality of Service (QoS) for client

**Steps**:

1. Click the **Bandwidth** button in the client row
2. Set limits:
   - **Download Limit**: 0-1,000,000 Kbps (0 = unlimited)
   - **Upload Limit**: 0-1,000,000 Kbps (0 = unlimited)
3. Click **Set Bandwidth** to apply

**Common Scenarios**:

| Use Case        | Download              | Upload              |
| --------------- | --------------------- | ------------------- |
| Video Streaming | 25,000 Kbps (25 Mbps) | 5,000 Kbps (5 Mbps) |
| Web Browsing    | 10,000 Kbps (10 Mbps) | 2,000 Kbps (2 Mbps) |
| Guest Network   | 5,000 Kbps (5 Mbps)   | 1,000 Kbps (1 Mbps) |
| VoIP Phone      | 1,000 Kbps (1 Mbps)   | 1,000 Kbps (1 Mbps) |
| IoT Device      | 500 Kbps              | 500 Kbps            |

**Conversion Helper**:

- 1 Mbps = 1,000 Kbps
- 10 Mbps = 10,000 Kbps
- 50 Mbps = 50,000 Kbps
- 100 Mbps = 100,000 Kbps

**When to Use**:

- Prevent bandwidth hogging
- Fair usage enforcement
- Guest network restrictions
- Prioritize critical applications

#### 5. Authorize Guest Access

**Purpose**: Grant temporary network access

**Steps**:

1. Click the **Guest** button in the client row
2. Set duration:
   - Enter seconds (300-86400)
   - Or use quick presets: 1h, 4h, 8h, 24h
3. Click **Authorize** to grant access

**When to Use**:

- Visitors and guests
- Temporary contractors
- Time-limited access for specific events
- Testing and demonstration

**Duration Presets**:

- **1 hour** (3,600 seconds) - Short visit
- **4 hours** (14,400 seconds) - Half-day meeting
- **8 hours** (28,800 seconds) - Full workday
- **24 hours** (86,400 seconds) - Overnight guest

ℹ️ **Note**: Access automatically expires after duration.

### Bulk Client Operations

#### Bulk Block

**Purpose**: Block multiple clients simultaneously

**Steps**:

1. Select clients using checkboxes
2. Click **Bulk Block** button
3. Review selection in transfer component
4. Click **Execute Operation**
5. Monitor progress
6. Review results

**When to Use**:

- Mass security response
- End of event cleanup
- Policy enforcement
- Network maintenance

#### Bulk Unblock

**Purpose**: Unblock multiple clients simultaneously

**Steps**:

1. Select blocked clients using checkboxes
2. Click **Bulk Unblock** button
3. Review and execute

**When to Use**:

- Restore access after event
- Resolve false positives
- Mass policy change

**Selection Helpers**:

- **Select All** - All clients
- **Invert Selection** - Flip selection
- **Clear** - Deselect all
- **Select Active** - Only active clients
- **Select Blocked** - Only blocked clients

---

## Bulk Operations

### Understanding the Bulk Operations Interface

The enhanced bulk operations modal provides:

1. **Transfer Component**

   - Left panel: Available items
   - Right panel: Selected for operation
   - Drag and drop support
   - Search functionality
   - Select all / clear buttons

2. **Progress Tracking**

   - Real-time statistics (Total, Success, Failed, Pending)
   - Progress bar showing completion percentage
   - Per-item status indicators
   - Timestamp for each operation

3. **Error Handling**
   - Individual item error messages
   - Retry failed operations button
   - Detailed error reporting
   - Success/failure summary

### Best Practices for Bulk Operations

#### Planning

1. **Schedule Appropriately**

   - Off-peak hours for maximum impact operations
   - Communicate maintenance windows
   - Have rollback plan ready

2. **Test First**

   - Start with 1-2 items
   - Verify expected behavior
   - Then proceed with larger batches

3. **Monitor Progress**
   - Watch for failures
   - Note error patterns
   - Be ready to intervene

#### Execution

1. **Review Selection Carefully**

   - Verify all items are correct
   - Remove any that shouldn't be included
   - Double-check critical devices

2. **Document Actions**

   - Note reason in provided fields
   - Keep change log
   - Record start/end times

3. **Handle Failures**
   - Review error messages
   - Retry after investigating
   - Manually handle if needed

#### Recovery

1. **Failed Operations**

   - Use "Retry Failed" button
   - Check device/client status first
   - May need individual attention

2. **Unexpected Results**
   - Individual device/client operations can fix issues
   - Contact support if persistent
   - Check logs for details

---

## Safety & Best Practices

### ⚠️ Critical Warnings

#### Device Operations

**DO NOT**:

- ❌ Reboot critical devices during production hours
- ❌ Rename devices without documentation
- ❌ Perform bulk operations without testing
- ❌ Ignore offline devices in bulk operations
- ❌ Reboot gateway devices without planning

**DO**:

- ✅ Schedule reboots during maintenance windows
- ✅ Test on non-critical devices first
- ✅ Document all changes
- ✅ Verify device status before operations
- ✅ Have console access to gateway as backup

#### Client Operations

**DO NOT**:

- ❌ Block clients without documenting reason
- ❌ Set bandwidth limits without testing
- ❌ Block critical service clients (servers, VoIP)
- ❌ Perform mass blocks during business hours
- ❌ Set overly restrictive limits

**DO**:

- ✅ Document all block/unblock actions
- ✅ Test bandwidth limits before wide deployment
- ✅ Verify client identity before blocking
- ✅ Use temporary blocks when appropriate
- ✅ Monitor impact after setting limits

### Operation Impact Matrix

| Operation        | Impact Level | Downtime  | User Visible                |
| ---------------- | ------------ | --------- | --------------------------- |
| Device Reboot    | HIGH         | 30-60s    | Yes - Disconnection         |
| Device Restart   | MEDIUM       | 5-10s     | Possible brief disruption   |
| Device Locate    | NONE         | 0s        | No                          |
| Device Rename    | NONE         | 0s        | No                          |
| Client Block     | HIGH         | Immediate | Yes - Access denied         |
| Client Unblock   | LOW          | 0s        | No - Must reconnect         |
| Client Reconnect | MEDIUM       | 2-5s      | Yes - Brief disconnect      |
| Bandwidth Limit  | LOW          | 0s        | Possible performance change |
| Guest Auth       | NONE         | 0s        | No                          |

### Recovery Procedures

#### Device Won't Come Back Online After Reboot

1. Wait 5 minutes for full reboot cycle
2. Check physical power and connections
3. Access device via console if available
4. Check controller adoption status
5. Contact support if still offline

#### Client Can't Reconnect After Unblock

1. Verify client shows as unblocked
2. Have user forget and re-add WiFi network
3. Check if bandwidth limits are too restrictive
4. Try reconnect action
5. Check controller logs for errors

#### Bulk Operation Partially Failed

1. Review failed items in results panel
2. Check error messages for patterns
3. Retry failed items using retry button
4. Manually handle remaining failures
5. Document issues for future reference

---

## Permissions & Requirements

### User Permissions

Different operations require different permission levels:

| Operation       | Required Permission | Role            |
| --------------- | ------------------- | --------------- |
| View Devices    | Read                | Observer, Admin |
| View Clients    | Read                | Observer, Admin |
| Reboot Device   | Write               | Admin           |
| Rename Device   | Write               | Admin           |
| Locate Device   | Write               | Admin           |
| Block Client    | Write               | Admin           |
| Set Bandwidth   | Write               | Admin           |
| Bulk Operations | Write               | Admin           |

### System Requirements

**Browser Requirements**:

- Modern browser (Chrome, Firefox, Edge, Safari)
- JavaScript enabled
- WebSocket support (for real-time updates)
- Minimum resolution: 1280x720

**Network Requirements**:

- Access to UniFi Network Application
- Valid authentication credentials
- Network connectivity to UniFi Controller
- API access enabled

**UniFi Controller Requirements**:

- UniFi Network Application 7.0+
- Devices adopted and managed
- Admin or Super Admin access
- API access enabled

### Feature Availability

Some features may not be available for all device types:

| Feature        | UAP | USW | USG/UDM    | Other      |
| -------------- | --- | --- | ---------- | ---------- |
| Reboot         | ✅  | ✅  | ✅         | ✅         |
| Locate         | ✅  | ✅  | ✅         | ⚠️ Varies  |
| Port Info      | ❌  | ✅  | ⚠️ Limited | ❌         |
| PoE Stats      | ❌  | ✅  | ❌         | ❌         |
| Advanced Stats | ✅  | ✅  | ✅         | ⚠️ Limited |

Legend: UAP (Access Point), USW (Switch), USG (Security Gateway), UDM (Dream Machine)

---

## API Reference

### For Developers

All management operations are available through the `managementApi` module:

```typescript
import { managementApi } from "@/api/management";
```

### Device API

```typescript
// Reboot device
await managementApi.devices.reboot(deviceId, { reason: "Maintenance" });

// Locate device
await managementApi.devices.locate(deviceId, { duration: 60 });

// Rename device
await managementApi.devices.rename(deviceId, { name: "New Name" });

// Get device info
const info = await managementApi.devices.getInfo(deviceId);

// Bulk reboot
const result = await managementApi.devices.bulkReboot({
  device_ids: ["id1", "id2"],
  reason: "Bulk maintenance",
});
```

### Client API

```typescript
// Block client
await managementApi.clients.block(mac, {
  duration: 3600,
  reason: "Security",
});

// Unblock client
await managementApi.clients.unblock(mac);

// Set bandwidth
await managementApi.clients.setBandwidth(mac, {
  download_limit: 50000, // Kbps
  upload_limit: 10000,
});

// Authorize guest
await managementApi.clients.authorizeGuest(mac, {
  duration: 3600,
});

// Bulk operations
await managementApi.clients.bulkBlock({
  mac_addresses: ["mac1", "mac2"],
  reason: "Bulk action",
});
```

### Error Handling

```typescript
import { ManagementApiError } from "@/api/management";

try {
  await managementApi.devices.reboot(deviceId);
} catch (error) {
  if (error instanceof ManagementApiError) {
    console.error("Status:", error.statusCode);
    console.error("Message:", error.message);
    console.error("Response:", error.response);
  }
}
```

For complete API documentation, see [API_INTEGRATION_COMPLETE.md](./API_INTEGRATION_COMPLETE.md).

---

## Troubleshooting

### Common Issues

#### Issue: Device Not Responding to Commands

**Symptoms**:

- Commands timeout
- Device shows as online but doesn't respond
- Error: "Device not found" or "Connection timeout"

**Solutions**:

1. Verify device is truly online (check controller)
2. Refresh device list
3. Check network connectivity to device
4. Try accessing device directly via SSH
5. Restart UniFi Controller service
6. Re-adopt device if necessary

#### Issue: Client Block Not Working

**Symptoms**:

- Client still has network access after blocking
- Block command succeeds but client not affected
- Client shows as blocked but is connected

**Solutions**:

1. Verify correct MAC address
2. Clear DHCP lease for client
3. Force client to reconnect
4. Check firewall rules aren't bypassing block
5. Verify client isn't using static IP outside DHCP range
6. Check for MAC address spoofing

#### Issue: Bandwidth Limits Not Applied

**Symptoms**:

- Client exceeds set bandwidth limits
- Speed tests show no restriction
- Limits set successfully but not enforced

**Solutions**:

1. Verify QoS is enabled on controller
2. Check if client is on excluded network
3. Reconnect client after setting limits
4. Verify limits are in Kbps, not Mbps
5. Check for multiple limit rules (last one wins)
6. Ensure device supports QoS (not all do)

#### Issue: Bulk Operation Failures

**Symptoms**:

- Most/all items fail in bulk operation
- Error: "Too many requests"
- Some items succeed, many fail

**Solutions**:

1. Reduce batch size (try 10-20 items at a time)
2. Wait between operations
3. Check controller performance (CPU/Memory)
4. Verify all items exist and are accessible
5. Check for network issues
6. Review error messages for patterns

#### Issue: Device Details Not Loading

**Symptoms**:

- Modal opens but shows loading spinner
- Error: "Failed to load device details"
- Some tabs load, others don't

**Solutions**:

1. Refresh the page
2. Check browser console for errors
3. Verify API access
4. Check device is adopted
5. Try different browser
6. Clear browser cache

### Error Messages Explained

#### "Device not found (404)"

- Device doesn't exist or has been removed
- Wrong device ID
- Device not adopted by controller

**Fix**: Verify device ID, check controller device list

#### "Unauthorized (401)"

- Session expired
- Invalid credentials
- Insufficient permissions

**Fix**: Re-login, check permissions

#### "Validation Error (422)"

- Invalid input parameters
- Missing required fields
- Value out of acceptable range

**Fix**: Check input values, review validation rules

#### "Rate Limit Exceeded (429)"

- Too many requests in short time
- Bulk operation too large
- API throttling active

**Fix**: Reduce request rate, use smaller batches

#### "Internal Server Error (500)"

- Controller error
- Database issue
- Unexpected error

**Fix**: Check controller logs, contact support

### Getting Help

#### Before Contacting Support

Gather this information:

1. What operation were you performing?
2. What was the expected result?
3. What actually happened?
4. Any error messages (exact text)?
5. Browser console errors
6. Controller version
7. Device/client details

#### Support Channels

1. **Documentation**

   - Check this guide
   - Review API documentation
   - Check troubleshooting section

2. **Logs**

   - Browser console (F12 → Console tab)
   - Network tab (F12 → Network tab)
   - Controller logs (Settings → System → Logs)

3. **Community**

   - UniFi Community Forums
   - GitHub Issues (if open source)
   - Stack Overflow

4. **Professional Support**
   - Ubiquiti Support Portal
   - Enterprise Support Contract
   - Professional Services

### Debug Mode

Enable debug logging for detailed information:

1. Open browser console (F12)
2. Run: `localStorage.setItem('debug', 'true')`
3. Refresh page
4. Reproduce issue
5. Check console for detailed logs

To disable:

```javascript
localStorage.removeItem("debug");
```

---

## Summary

This comprehensive management system provides powerful tools for controlling your UniFi network infrastructure. Key takeaways:

✅ **Device Management**: Complete control over network devices
✅ **Client Management**: Granular client access and QoS control
✅ **Bulk Operations**: Efficient management at scale
✅ **Safety Features**: Confirmations and validation prevent accidents
✅ **Real-time Monitoring**: Immediate feedback and status updates
✅ **Detailed Insights**: Comprehensive device and client information

**Remember**:

- Test operations on non-critical systems first
- Document all changes
- Schedule disruptive operations appropriately
- Monitor results and be ready to intervene
- Use bulk operations judiciously

For additional help, refer to:

- [API Integration Documentation](./API_INTEGRATION_COMPLETE.md)
- [Feature Documentation](./FEATURES.md)
- [Configuration Guide](./CONFIGURATION.md)

**Version**: 1.0.0
**Last Updated**: October 19, 2025
**Feedback**: Please report issues or suggestions through your normal support channels.

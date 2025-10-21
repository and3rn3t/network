/**
 * Management API Usage Examples
 * Demonstrates how to use the device and client management API
 */

import { message } from "antd";
import { managementApi, ManagementApiError } from "../api/management";

// ============================================================================
// Device Management Examples
// ============================================================================

/**
 * Example: Reboot a single device
 */
export async function exampleRebootDevice(deviceId: string) {
  try {
    const result = await managementApi.devices.reboot(deviceId, {
      reason: "Scheduled maintenance",
    });

    message.success(result.message);
    console.log("Reboot result:", result.data);
  } catch (error) {
    if (error instanceof ManagementApiError) {
      message.error(`Failed to reboot device: ${error.message}`);
      console.error("Error details:", error.response);
    }
  }
}

/**
 * Example: Locate a device (blink LED)
 */
export async function exampleLocateDevice(deviceId: string) {
  try {
    const result = await managementApi.devices.locate(deviceId, {
      duration: 60, // Blink for 60 seconds
    });

    message.success(result.message);
  } catch (error) {
    if (error instanceof ManagementApiError) {
      message.error(`Failed to locate device: ${error.message}`);
    }
  }
}

/**
 * Example: Rename a device
 */
export async function exampleRenameDevice(deviceId: string, newName: string) {
  try {
    const result = await managementApi.devices.rename(deviceId, {
      name: newName,
    });

    message.success(result.message);
    return result.data;
  } catch (error) {
    if (error instanceof ManagementApiError) {
      message.error(`Failed to rename device: ${error.message}`);
      throw error;
    }
  }
}

/**
 * Example: Get detailed device information
 */
export async function exampleGetDeviceInfo(deviceId: string) {
  try {
    const deviceInfo = await managementApi.devices.getInfo(deviceId);

    console.log("Device Information:");
    console.log("- Name:", deviceInfo.name);
    console.log("- Model:", deviceInfo.model);
    console.log("- IP:", deviceInfo.ip);
    console.log("- Status:", deviceInfo.status);

    if (deviceInfo.stats) {
      console.log("- CPU Usage:", deviceInfo.stats.cpu_usage, "%");
      console.log("- Memory Usage:", deviceInfo.stats.memory_usage, "%");
      console.log("- Temperature:", deviceInfo.stats.temperature, "°C");
    }

    return deviceInfo;
  } catch (error) {
    if (error instanceof ManagementApiError) {
      message.error(`Failed to get device info: ${error.message}`);
      throw error;
    }
  }
}

/**
 * Example: Bulk reboot multiple devices
 */
export async function exampleBulkRebootDevices(deviceIds: string[]) {
  try {
    const result = await managementApi.devices.bulkReboot({
      device_ids: deviceIds,
      reason: "Bulk maintenance operation",
    });

    message.success(
      `Bulk reboot completed: ${result.success} successful, ${result.failed} failed`
    );

    // Log failed devices
    result.results
      .filter((r) => !r.success)
      .forEach((r) => {
        console.warn(`Device ${r.device_id} failed: ${r.message}`);
      });

    return result;
  } catch (error) {
    if (error instanceof ManagementApiError) {
      message.error(`Bulk reboot failed: ${error.message}`);
      throw error;
    }
  }
}

// ============================================================================
// Client Management Examples
// ============================================================================

/**
 * Example: Block a client permanently
 */
export async function exampleBlockClient(mac: string, reason?: string) {
  try {
    const result = await managementApi.clients.block(mac, {
      reason: reason || "Manual block",
    });

    message.success(result.message);
  } catch (error) {
    if (error instanceof ManagementApiError) {
      message.error(`Failed to block client: ${error.message}`);
    }
  }
}

/**
 * Example: Block a client temporarily
 */
export async function exampleBlockClientTemporary(
  mac: string,
  durationSeconds: number
) {
  try {
    const result = await managementApi.clients.block(mac, {
      duration: durationSeconds,
      reason: "Temporary suspension",
    });

    message.success(result.message);
  } catch (error) {
    if (error instanceof ManagementApiError) {
      message.error(`Failed to block client: ${error.message}`);
    }
  }
}

/**
 * Example: Unblock a client
 */
export async function exampleUnblockClient(mac: string) {
  try {
    const result = await managementApi.clients.unblock(mac);

    message.success(result.message);
  } catch (error) {
    if (error instanceof ManagementApiError) {
      message.error(`Failed to unblock client: ${error.message}`);
    }
  }
}

/**
 * Example: Set bandwidth limits for a client
 */
export async function exampleSetBandwidth(
  mac: string,
  downloadMbps: number,
  uploadMbps: number
) {
  try {
    // Convert Mbps to Kbps
    const result = await managementApi.clients.setBandwidth(mac, {
      download_limit: downloadMbps * 1000,
      upload_limit: uploadMbps * 1000,
    });

    message.success(result.message);
  } catch (error) {
    if (error instanceof ManagementApiError) {
      message.error(`Failed to set bandwidth: ${error.message}`);
    }
  }
}

/**
 * Example: Authorize guest access
 */
export async function exampleAuthorizeGuest(mac: string, hours: number) {
  try {
    const durationSeconds = hours * 3600;
    const result = await managementApi.clients.authorizeGuest(mac, {
      duration: durationSeconds,
    });

    message.success(result.message);
  } catch (error) {
    if (error instanceof ManagementApiError) {
      message.error(`Failed to authorize guest: ${error.message}`);
    }
  }
}

/**
 * Example: Get client connection history
 */
export async function exampleGetClientHistory(mac: string) {
  try {
    const result = await managementApi.clients.getHistory(mac);

    console.log("Client History:", result.data);
    return result.data;
  } catch (error) {
    if (error instanceof ManagementApiError) {
      message.error(`Failed to get client history: ${error.message}`);
      throw error;
    }
  }
}

/**
 * Example: Bulk block multiple clients
 */
export async function exampleBulkBlockClients(macs: string[]) {
  try {
    const result = await managementApi.clients.bulkBlock({
      mac_addresses: macs,
      reason: "Bulk security action",
    });

    message.success(
      `Bulk block completed: ${result.success} successful, ${result.failed} failed`
    );

    // Log failed clients
    result.results
      .filter((r) => !r.success)
      .forEach((r) => {
        console.warn(`Client ${r.mac} failed: ${r.message}`);
      });

    return result;
  } catch (error) {
    if (error instanceof ManagementApiError) {
      message.error(`Bulk block failed: ${error.message}`);
      throw error;
    }
  }
}

/**
 * Example: Bulk unblock multiple clients
 */
export async function exampleBulkUnblockClients(macs: string[]) {
  try {
    const result = await managementApi.clients.bulkUnblock({
      mac_addresses: macs,
    });

    message.success(
      `Bulk unblock completed: ${result.success} successful, ${result.failed} failed`
    );

    return result;
  } catch (error) {
    if (error instanceof ManagementApiError) {
      message.error(`Bulk unblock failed: ${error.message}`);
      throw error;
    }
  }
}

/**
 * Example: Reconnect a client
 */
export async function exampleReconnectClient(mac: string) {
  try {
    const result = await managementApi.clients.reconnect(mac);

    message.success(result.message);
  } catch (error) {
    if (error instanceof ManagementApiError) {
      message.error(`Failed to reconnect client: ${error.message}`);
    }
  }
}

// ============================================================================
// Advanced Usage Examples
// ============================================================================

/**
 * Example: Handle multiple operations with error recovery
 */
export async function exampleMultipleOperationsWithRecovery(
  deviceIds: string[]
) {
  const results = {
    successful: [] as string[],
    failed: [] as { id: string; error: string }[],
  };

  for (const deviceId of deviceIds) {
    try {
      await managementApi.devices.restart(deviceId);
      results.successful.push(deviceId);
    } catch (error) {
      if (error instanceof ManagementApiError) {
        results.failed.push({
          id: deviceId,
          error: error.message,
        });
      }
    }
  }

  console.log("Operation Results:");
  console.log("- Successful:", results.successful.length);
  console.log("- Failed:", results.failed.length);

  if (results.failed.length > 0) {
    console.error("Failed operations:", results.failed);
  }

  return results;
}

/**
 * Example: Conditional operation based on device info
 */
export async function exampleConditionalOperation(deviceId: string) {
  try {
    // Get device info first
    const deviceInfo = await managementApi.devices.getInfo(deviceId);

    // Check if device needs reboot based on uptime
    const uptimeDays = deviceInfo.uptime / 86400;
    if (uptimeDays > 30) {
      console.log(
        `Device ${deviceInfo.name} has been up for ${uptimeDays.toFixed(
          1
        )} days`
      );

      // Confirm before rebooting
      const shouldReboot = confirm(
        `Device ${deviceInfo.name} has high uptime. Reboot now?`
      );

      if (shouldReboot) {
        await managementApi.devices.reboot(deviceId, {
          reason: "High uptime maintenance",
        });
        message.success("Device rebooted successfully");
      }
    } else {
      message.info("Device uptime is acceptable, no reboot needed");
    }
  } catch (error) {
    if (error instanceof ManagementApiError) {
      message.error(`Operation failed: ${error.message}`);
    }
  }
}

/**
 * Example: Progressive bulk operation with status updates
 */
export async function exampleProgressiveBulkOperation(
  clientMacs: string[],
  onProgress?: (completed: number, total: number) => void
) {
  const total = clientMacs.length;
  let completed = 0;

  for (const mac of clientMacs) {
    try {
      await managementApi.clients.reconnect(mac);
      completed++;
      onProgress?.(completed, total);
    } catch (error) {
      console.error(`Failed to reconnect ${mac}:`, error);
      completed++;
      onProgress?.(completed, total);
    }
  }

  message.success(`Completed ${completed}/${total} reconnections`);
}

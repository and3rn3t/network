/**
 * Devices API endpoints - focused on historical data
 */

import type {
  Device,
  DeviceMetrics,
  DeviceMetricsHistory,
} from "@/types/device";
import { apiClient } from "./client";

export interface DevicesResponse {
  devices: Device[];
  total: number;
  limit: number;
  offset: number;
}

export interface DeviceMetricsResponse {
  device_id: number;
  device_name: string;
  metrics: DeviceMetrics[];
  count: number;
  hours: number;
}

/**
 * Get all devices
 */
export const getDevices = async (): Promise<DevicesResponse> => {
  const response = await apiClient.get<DevicesResponse>("/api/devices");
  return response.data;
};

/**
 * Get single device by ID
 */
export const getDevice = async (deviceId: string): Promise<Device> => {
  const response = await apiClient.get<Device>(`/api/devices/${deviceId}`);
  return response.data;
};

/**
 * Get device metrics history for analysis
 * @param deviceId - Device ID
 * @param hours - Number of hours to look back (default: 24)
 */
export const getDeviceMetrics = async (
  deviceId: string,
  hours = 24
): Promise<DeviceMetricsResponse> => {
  const response = await apiClient.get<DeviceMetricsResponse>(
    `/api/devices/${deviceId}/metrics`,
    {
      params: { hours },
    }
  );
  return response.data;
};

/**
 * Get metrics history for multiple devices (for comparison)
 * @param deviceIds - Array of device IDs
 * @param hours - Number of hours to look back
 */
export const getMultiDeviceMetrics = async (
  deviceIds: string[],
  hours = 24
): Promise<DeviceMetricsHistory[]> => {
  const promises = deviceIds.map(async (deviceId) => {
    const response = await getDeviceMetrics(deviceId, hours);
    return {
      device_id: response.device_id,
      device_name: response.device_name,
      metrics: response.metrics,
    };
  });
  return Promise.all(promises);
};

/**
 * Export device metrics to CSV
 * @param deviceId - Device ID
 * @param hours - Number of hours to export
 */
export const exportDeviceMetrics = async (
  deviceId: string,
  hours = 24
): Promise<Blob> => {
  const response = await apiClient.get(
    `/api/devices/${deviceId}/metrics/export`,
    {
      params: { hours, format: "csv" },
      responseType: "blob",
    }
  );
  return response.data;
};

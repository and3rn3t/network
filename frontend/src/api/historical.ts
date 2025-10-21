/**
 * Historical data API endpoints
 */

import { apiClient } from "./client";

// Types
export interface MetricPoint {
  timestamp: string;
  value: number;
  unit: string;
}

export interface MetricStatistics {
  count: number;
  min: number;
  max: number;
  avg: number;
  p95: number | null;
  p99: number | null;
  latest: number | null;
}

export interface MetricTimeSeries {
  metric_name: string;
  unit: string;
  data: MetricPoint[];
  statistics: MetricStatistics;
}

export interface DeviceMetricsResponse {
  device_mac: string;
  device_name: string | null;
  time_range: string;
  metrics: MetricTimeSeries[];
}

export interface MultiDeviceMetricsResponse {
  time_range: string;
  devices: DeviceMetricsResponse[];
}

/**
 * Get historical metrics for a client device
 */
export const getClientHistoricalMetrics = async (
  clientMac: string,
  days: number = 7,
  metrics?: string,
  aggregate: boolean = true
): Promise<DeviceMetricsResponse> => {
  const params = new URLSearchParams({
    days: days.toString(),
    aggregate: aggregate.toString(),
  });

  if (metrics) {
    params.append("metrics", metrics);
  }

  const response = await apiClient.get(
    `/api/historical/clients/${clientMac}/metrics?${params.toString()}`
  );
  return response.data;
};

/**
 * Get historical metrics for a device (infrastructure)
 */
export const getDeviceHistoricalMetrics = async (
  deviceMac: string,
  days: number = 7,
  metrics?: string,
  aggregate: boolean = true
): Promise<DeviceMetricsResponse> => {
  const params = new URLSearchParams({
    days: days.toString(),
    aggregate: aggregate.toString(),
  });

  if (metrics) {
    params.append("metrics", metrics);
  }

  const response = await apiClient.get(
    `/api/historical/devices/${deviceMac}/metrics?${params.toString()}`
  );
  return response.data;
};

/**
 * Compare metrics across multiple client devices
 */
export const compareClientMetrics = async (
  clientMacs: string[],
  days: number = 7,
  metrics?: string,
  aggregate: boolean = true
): Promise<MultiDeviceMetricsResponse> => {
  const params = new URLSearchParams({
    client_macs: clientMacs.join(","),
    days: days.toString(),
    aggregate: aggregate.toString(),
  });

  if (metrics) {
    params.append("metrics", metrics);
  }

  const response = await apiClient.get(
    `/api/historical/clients/compare?${params.toString()}`
  );
  return response.data;
};

/**
 * Compare metrics across multiple infrastructure devices
 */
export const compareDeviceMetrics = async (
  deviceMacs: string[],
  days: number = 7,
  metrics?: string,
  aggregate: boolean = true
): Promise<MultiDeviceMetricsResponse> => {
  const params = new URLSearchParams({
    device_macs: deviceMacs.join(","),
    days: days.toString(),
    aggregate: aggregate.toString(),
  });

  if (metrics) {
    params.append("metrics", metrics);
  }

  const response = await apiClient.get(
    `/api/historical/devices/compare?${params.toString()}`
  );
  return response.data;
};

/**
 * Export client metrics as CSV
 */
export const exportClientMetricsCSV = async (
  clientMac: string,
  days: number = 7,
  metrics?: string
): Promise<Blob> => {
  const params = new URLSearchParams({
    days: days.toString(),
    format: "csv",
  });

  if (metrics) {
    params.append("metrics", metrics);
  }

  const response = await apiClient.get(
    `/api/historical/clients/${clientMac}/export?${params.toString()}`,
    {
      responseType: "blob",
    }
  );
  return response.data;
};

/**
 * Export device metrics as CSV
 */
export const exportDeviceMetricsCSV = async (
  deviceMac: string,
  days: number = 7,
  metrics?: string
): Promise<Blob> => {
  const params = new URLSearchParams({
    days: days.toString(),
    format: "csv",
  });

  if (metrics) {
    params.append("metrics", metrics);
  }

  const response = await apiClient.get(
    `/api/historical/devices/${deviceMac}/export?${params.toString()}`,
    {
      responseType: "blob",
    }
  );
  return response.data;
};

/**
 * Export client metrics as JSON
 */
export const exportClientMetricsJSON = async (
  clientMac: string,
  days: number = 7,
  metrics?: string
): Promise<DeviceMetricsResponse> => {
  const params = new URLSearchParams({
    days: days.toString(),
    format: "json",
  });

  if (metrics) {
    params.append("metrics", metrics);
  }

  const response = await apiClient.get(
    `/api/historical/clients/${clientMac}/export?${params.toString()}`
  );
  return response.data;
};

/**
 * Export device metrics as JSON
 */
export const exportDeviceMetricsJSON = async (
  deviceMac: string,
  days: number = 7,
  metrics?: string
): Promise<DeviceMetricsResponse> => {
  const params = new URLSearchParams({
    days: days.toString(),
    format: "json",
  });

  if (metrics) {
    params.append("metrics", metrics);
  }

  const response = await apiClient.get(
    `/api/historical/devices/${deviceMac}/export?${params.toString()}`
  );
  return response.data;
};

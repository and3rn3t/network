/**
 * React Query hooks for device data
 */

import type { DeviceMetricsResponse } from "@/api/devices";
import { getDevice, getDeviceMetrics, getDevices } from "@/api/devices";
import { useQuery } from "@tanstack/react-query";

/**
 * Fetch all devices
 */
export const useDevices = () => {
  return useQuery({
    queryKey: ["devices"],
    queryFn: getDevices,
    staleTime: 2 * 60 * 1000, // 2 minutes - devices don't change often
  });
};

/**
 * Fetch single device by ID
 */
export const useDevice = (deviceId: string | undefined) => {
  return useQuery({
    queryKey: ["device", deviceId],
    queryFn: () => getDevice(deviceId!),
    enabled: !!deviceId, // Only fetch if deviceId is provided
    staleTime: 2 * 60 * 1000,
  });
};

/**
 * Fetch device metrics history
 */
export const useDeviceMetrics = (
  deviceId: string | undefined,
  hours: number = 24
) => {
  return useQuery<DeviceMetricsResponse>({
    queryKey: ["deviceMetrics", deviceId, hours],
    queryFn: () => getDeviceMetrics(deviceId!, hours),
    enabled: !!deviceId,
    staleTime: 1 * 60 * 1000, // 1 minute - metrics change frequently
    refetchInterval: 5 * 60 * 1000, // Auto-refetch every 5 minutes
  });
};

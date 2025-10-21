/**
 * React Query hooks for historical data
 */

import {
  type DeviceMetricsResponse,
  type MultiDeviceMetricsResponse,
  compareClientMetrics,
  exportClientMetricsCSV,
  exportClientMetricsJSON,
  getClientHistoricalMetrics,
} from "@/api/historical";
import { useMutation, useQuery } from "@tanstack/react-query";
import { message } from "antd";

/**
 * Fetch historical metrics for a client device
 */
export const useClientHistoricalMetrics = (
  clientMac: string | undefined,
  days: number = 7,
  metrics?: string,
  aggregate: boolean = true
) => {
  return useQuery<DeviceMetricsResponse>({
    queryKey: ["clientHistoricalMetrics", clientMac, days, metrics, aggregate],
    queryFn: () =>
      getClientHistoricalMetrics(clientMac!, days, metrics, aggregate),
    enabled: !!clientMac,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Compare metrics across multiple client devices
 */
export const useCompareClientMetrics = (
  clientMacs: string[],
  days: number = 7,
  metrics?: string,
  aggregate: boolean = true
) => {
  return useQuery<MultiDeviceMetricsResponse>({
    queryKey: ["compareClientMetrics", clientMacs, days, metrics, aggregate],
    queryFn: () => compareClientMetrics(clientMacs, days, metrics, aggregate),
    enabled: clientMacs.length > 0,
    staleTime: 5 * 60 * 1000,
  });
};

/**
 * Export client metrics as CSV
 */
export const useExportClientMetricsCSV = () => {
  return useMutation({
    mutationFn: ({
      clientMac,
      days,
      metrics,
    }: {
      clientMac: string;
      days: number;
      metrics?: string;
    }) => exportClientMetricsCSV(clientMac, days, metrics),
    onSuccess: (blob, variables) => {
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `client_${variables.clientMac}_metrics_${variables.days}d.csv`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      message.success("CSV exported successfully");
    },
    onError: () => {
      message.error("Failed to export CSV");
    },
  });
};

/**
 * Export client metrics as JSON
 */
export const useExportClientMetricsJSON = () => {
  return useMutation({
    mutationFn: ({
      clientMac,
      days,
      metrics,
    }: {
      clientMac: string;
      days: number;
      metrics?: string;
    }) => exportClientMetricsJSON(clientMac, days, metrics),
    onSuccess: (data, variables) => {
      const jsonString = JSON.stringify(data, null, 2);
      const blob = new Blob([jsonString], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `client_${variables.clientMac}_metrics_${variables.days}d.json`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      message.success("JSON exported successfully");
    },
    onError: () => {
      message.error("Failed to export JSON");
    },
  });
};

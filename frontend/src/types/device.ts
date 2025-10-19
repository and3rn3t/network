/**
 * Device-related types for historical analysis
 */

export interface Device {
  id: number;
  name: string;
  mac: string;
  ip: string;
  type: string;
  model: string;
  status: string;
  version?: string;
  uptime: number;
  last_seen: string | null;
  site_id?: string;
}

export interface DeviceMetrics {
  metric_type: string; // e.g., "cpu_usage", "memory_usage", "temperature"
  value: number;
  timestamp: string;
}

export interface DeviceMetricsHistory {
  device_id: number;
  device_name: string;
  metrics: DeviceMetrics[];
}

export interface DeviceStats {
  device_id: string;
  avg_cpu: number;
  max_cpu: number;
  avg_memory: number;
  max_memory: number;
  avg_temperature: number;
  max_temperature: number;
  uptime_percentage: number;
}

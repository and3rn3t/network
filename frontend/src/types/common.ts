/**
 * Common types used across the application
 */

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export type SeverityLevel = "info" | "warning" | "critical";
export type AlertStatus = "open" | "acknowledged" | "resolved";

export interface TimeRange {
  start: Date;
  end: Date;
}

export interface ChartDataPoint {
  timestamp: string;
  value: number;
}

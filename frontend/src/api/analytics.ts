/**
 * Advanced Analytics API Client
 * 
 * TypeScript client for forecasting, predictions, anomaly detection, and ML insights.
 */

import apiClient from './client';

/**
 * Forecast Point Interface
 */
export interface ForecastPoint {
  timestamp: string;
  predicted_value: number;
  confidence_lower: number;
  confidence_upper: number;
  confidence_level: number;
}

/**
 * Forecast Response
 */
export interface ForecastResponse {
  device_id: number;
  metric_type: string;
  current_value: number;
  forecast_days: number;
  forecast: ForecastPoint[];
  generated_at: string;
}

/**
 * Capacity Forecast Response
 */
export interface CapacityForecastResponse {
  device_id: number;
  metric_type: string;
  current_value: number;
  current_utilization: number;
  capacity: number;
  threshold_percent: number;
  threshold_value: number;
  predicted_value_30d: number;
  days_until_threshold: number | null;
  recommendation: string;
  generated_at: string;
}

/**
 * Anomaly Interface
 */
export interface Anomaly {
  timestamp: string;
  value: number;
  expected_range: [number, number];
  anomaly_score: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
}

/**
 * Anomaly Detection Response
 */
export interface AnomalyDetectionResponse {
  device_id: number;
  device_name: string;
  metric_type: string;
  days_analyzed: number;
  total_data_points: number;
  anomalies_detected: number;
  anomalies: Anomaly[];
  generated_at: string;
}

/**
 * Failure Prediction Response
 */
export interface FailurePredictionResponse {
  device_id: number;
  device_name: string;
  failure_probability: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  time_to_failure_days: number | null;
  contributing_factors: string[];
  recommendation: string;
  analysis_period_days: number;
  generated_at: string;
}

/**
 * Network Insights Response
 */
export interface NetworkInsightsResponse {
  network_summary: {
    total_devices: number;
    online_devices: number;
    offline_devices: number;
    active_alerts: number;
  };
  avg_metrics_24h: Record<string, number>;
  insights: string[];
  recommendations: string[];
  generated_at: string;
}

/**
 * Get device metric forecast
 */
export async function getForecast(
  deviceId: number,
  metricType: string,
  forecastDays: number = 30
): Promise<ForecastResponse> {
  const response = await apiClient.get(`/analytics/forecast/${deviceId}`, {
    params: {
      metric_type: metricType,
      forecast_days: forecastDays,
    },
  });
  return response.data;
}

/**
 * Get capacity forecast (when will resource reach threshold)
 */
export async function getCapacityForecast(
  deviceId: number,
  metricType: string,
  capacity: number,
  thresholdPercent: number = 80
): Promise<CapacityForecastResponse> {
  const response = await apiClient.get(`/analytics/capacity-forecast/${deviceId}`, {
    params: {
      metric_type: metricType,
      capacity,
      threshold_percent: thresholdPercent,
    },
  });
  return response.data;
}

/**
 * Detect anomalies in device metrics
 */
export async function detectAnomalies(
  deviceId: number,
  metricType: string,
  days: number = 7
): Promise<AnomalyDetectionResponse> {
  const response = await apiClient.get(`/analytics/anomalies/${deviceId}`, {
    params: {
      metric_type: metricType,
      days,
    },
  });
  return response.data;
}

/**
 * Predict device failure probability
 */
export async function predictFailure(deviceId: number): Promise<FailurePredictionResponse> {
  const response = await apiClient.get(`/analytics/failure-prediction/${deviceId}`);
  return response.data;
}

/**
 * Get network-wide insights
 */
export async function getNetworkInsights(): Promise<NetworkInsightsResponse> {
  const response = await apiClient.get('/analytics/network-insights');
  return response.data;
}

/**
 * Analytics API object (alternative export style)
 */
export const analyticsApi = {
  getForecast,
  getCapacityForecast,
  detectAnomalies,
  predictFailure,
  getNetworkInsights,
};

export default analyticsApi;

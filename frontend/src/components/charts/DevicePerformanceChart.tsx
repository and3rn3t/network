/**
 * Device Performance Chart Component
 * Displays time-series data for device metrics (CPU, Memory, Temperature)
 */

import type { DeviceMetrics } from "@/types/device";
import { Alert, Card, Empty, Spin } from "antd";
import dayjs from "dayjs";
import type { ReactElement } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface DevicePerformanceChartProps {
  data: DeviceMetrics[] | undefined;
  loading?: boolean;
  error?: Error | null;
  metricType: "cpu_usage" | "memory_usage" | "temperature";
  title: string;
  color?: string;
  unit?: string;
}

// Custom dot component for anomaly highlighting
const AnomalyDot = (props: {
  cx?: number;
  cy?: number;
  payload?: { isAnomaly?: boolean };
}): ReactElement | null => {
  const { cx, cy, payload } = props;
  if (!cx || !cy || !payload?.isAnomaly) {
    return null;
  }
  return (
    <circle
      cx={cx}
      cy={cy}
      r={5}
      fill="var(--md-sys-color-error)"
      stroke="#fff"
      strokeWidth={2}
    />
  );
};

export const DevicePerformanceChart: React.FC<DevicePerformanceChartProps> = ({
  data,
  loading,
  error,
  metricType,
  title,
  color = "#1890ff",
  unit = "%",
}) => {
  // Transform data for Recharts
  const chartData =
    data
      ?.filter((m) => m.metric_type === metricType)
      ?.map((m) => ({
        timestamp: dayjs(m.timestamp).format("MM/DD HH:mm"),
        value: m.value,
        fullTimestamp: m.timestamp,
      }))
      ?.reverse() || []; // Reverse to show oldest first

  if (loading) {
    return (
      <Card title={title}>
        <div style={{ textAlign: "center", padding: "40px" }}>
          <Spin size="large" tip="Loading metrics..." />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title={title}>
        <Alert
          message="Error Loading Metrics"
          description={error.message}
          type="error"
          showIcon
        />
      </Card>
    );
  }

  if (!chartData || chartData.length === 0) {
    return (
      <Card title={title}>
        <Empty description="No metrics data available for this time range" />
      </Card>
    );
  }

  // Calculate statistics
  const values = chartData.map((d) => d.value);
  const avg = (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1);
  const max = Math.max(...values).toFixed(1);
  const min = Math.min(...values).toFixed(1);

  // Detect anomalies (values that are 2 standard deviations from mean)
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const stdDev = Math.sqrt(
    values.reduce((sum, val) => sum + (val - mean) ** 2, 0) / values.length
  );
  const threshold = 2 * stdDev;

  // Mark anomalies
  const chartDataWithAnomalies = chartData.map((point) => ({
    ...point,
    isAnomaly: Math.abs(point.value - mean) > threshold,
  }));

  return (
    <Card
      title={title}
      extra={
        <span style={{ fontSize: 12, color: "rgba(0, 0, 0, 0.65)" }}>
          Avg: {avg}
          {unit} | Max: {max}
          {unit} | Min: {min}
          {unit}
        </span>
      }
    >
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={chartDataWithAnomalies}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="timestamp"
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis
            label={{ value: unit, angle: -90, position: "insideLeft" }}
            domain={[0, "auto"]}
          />
          <Tooltip
            contentStyle={{ backgroundColor: "#fff", border: "1px solid #ccc" }}
            formatter={(value: number) => [
              `${value.toFixed(2)}${unit}`,
              "Value",
            ]}
            labelFormatter={(label) => `Time: ${label}`}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            dot={<AnomalyDot />}
            name={title}
            animationDuration={300}
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
};

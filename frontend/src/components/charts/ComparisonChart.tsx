/**
 * Comparison Chart Component
 * Shows multiple device metrics on the same chart for comparison
 */

import { Alert, Card, Spin } from "antd";
import { format, parseISO } from "date-fns";
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

interface DeviceMetric {
  recorded_at: string;
  metric_value: number;
}

interface ComparisonDevice {
  device: {
    id: string;
    name: string;
    color: string;
  };
  metrics: DeviceMetric[];
  loading: boolean;
  error: any;
}

interface ComparisonChartProps {
  data: ComparisonDevice[];
  metricType: string;
  title: string;
  unit: string;
  timeRange: {
    hours: number;
    label: string;
  };
}

export const ComparisonChart: React.FC<ComparisonChartProps> = ({
  data,
  metricType,
  title,
  unit,
  timeRange,
}) => {
  const isLoading = data.some((d) => d.loading);
  const hasError = data.some((d) => d.error);

  if (isLoading) {
    return (
      <Card title={title}>
        <div style={{ textAlign: "center", padding: "50px" }}>
          <Spin size="large" tip="Loading comparison data..." />
        </div>
      </Card>
    );
  }

  if (hasError) {
    return (
      <Card title={title}>
        <Alert
          message="Error Loading Comparison Data"
          description="Failed to load metrics for one or more devices. Please try again."
          type="error"
          showIcon
        />
      </Card>
    );
  }

  // Transform data for Recharts
  // Create a map of timestamps to values for each device
  const timeMap = new Map<string, any>();

  data.forEach(({ device, metrics }) => {
    metrics
      .filter((m) => m.metric_value !== null && m.metric_value !== undefined)
      .forEach((metric) => {
        const time = metric.recorded_at;
        if (!timeMap.has(time)) {
          timeMap.set(time, { time });
        }
        const entry = timeMap.get(time);
        entry[device.name] = metric.metric_value;
      });
  });

  // Convert to array and sort by time
  const chartData = Array.from(timeMap.values()).sort(
    (a, b) => new Date(a.time).getTime() - new Date(b.time).getTime()
  );

  // Format time labels based on time range
  const formatTime = (timeStr: string) => {
    try {
      const date = parseISO(timeStr);
      if (timeRange.hours <= 6) {
        return format(date, "HH:mm"); // Show hours:minutes for short ranges
      } else if (timeRange.hours <= 24) {
        return format(date, "HH:mm"); // Show hours:minutes for 24h
      } else {
        return format(date, "MM/dd HH:mm"); // Show date for longer ranges
      }
    } catch {
      return timeStr;
    }
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    return (
      <div
        style={{
          backgroundColor: "white",
          border: "1px solid #ccc",
          padding: "10px",
          borderRadius: "4px",
        }}
      >
        <p style={{ margin: 0, fontWeight: "bold", marginBottom: "5px" }}>
          {formatTime(payload[0].payload.time)}
        </p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ margin: 0, color: entry.color }}>
            {entry.name}: {entry.value?.toFixed(2)} {unit}
          </p>
        ))}
      </div>
    );
  };

  if (chartData.length === 0) {
    return (
      <Card title={title}>
        <Alert
          message="No Data Available"
          description={`No ${metricType} data found for the selected devices and time range.`}
          type="info"
          showIcon
        />
      </Card>
    );
  }

  return (
    <Card title={title}>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="time"
            tickFormatter={formatTime}
            minTickGap={50}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis
            label={{ value: unit, angle: -90, position: "insideLeft" }}
            domain={[0, "auto"]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ paddingTop: "20px" }} />
          {data.map(({ device }) => (
            <Line
              key={device.id}
              type="monotone"
              dataKey={device.name}
              stroke={device.color}
              strokeWidth={2}
              dot={false}
              connectNulls
              name={device.name}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
};

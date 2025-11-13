/**
 * Live Metrics Chart Component
 * 
 * Real-time updating chart for network metrics using WebSocket data streams.
 * Displays bandwidth, client count, device status with live updates.
 */

import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Card, Badge, Space, Typography } from 'antd';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import RemoveIcon from '@mui/icons-material/Remove';
import { useWebSocket } from '@/hooks/useWebSocket';
import './LiveMetricsChart.css';

const { Text } = Typography;

export interface LiveMetricsChartProps {
  metricType: 'bandwidth' | 'clients' | 'cpu' | 'memory';
  title: string;
  unit?: string;
  maxDataPoints?: number;
  height?: number;
  color?: string;
}

interface MetricDataPoint {
  timestamp: string;
  value: number;
  time: string; // Formatted time for display
}

/**
 * LiveMetricsChart - Real-time chart with WebSocket updates
 */
export const LiveMetricsChart: React.FC<LiveMetricsChartProps> = ({
  metricType,
  title,
  unit = '',
  maxDataPoints = 30,
  height = 300,
  color = '#1976d2',
}) => {
  const [dataPoints, setDataPoints] = useState<MetricDataPoint[]>([]);
  const [currentValue, setCurrentValue] = useState<number | null>(null);
  const [trend, setTrend] = useState<'up' | 'down' | 'stable'>('stable');
  const [isLive, setIsLive] = useState(false);

  // Connect to WebSocket
  const ws = useWebSocket({
    url: 'ws://localhost:8000/ws',
    autoReconnect: true,
    onConnect: () => {
      console.log('WebSocket connected - subscribing to metrics');
      setIsLive(true);
    },
    onDisconnect: () => {
      console.log('WebSocket disconnected');
      setIsLive(false);
    },
    onMessage: (message) => {
      if (message.type === 'metrics_update' && message.data) {
        handleMetricsUpdate(message.data);
      }
    },
  });

  // Subscribe to metrics room
  useEffect(() => {
    if (ws.status === 'connected') {
      ws.subscribe('metrics');
    }
    return () => {
      if (ws.status === 'connected') {
        ws.unsubscribe('metrics');
      }
    };
  }, [ws]);

  const handleMetricsUpdate = (metrics: any[]) => {
    // Filter metrics for the specific type we care about
    const relevantMetrics = metrics.filter(
      (m) => m.metric_type === metricType
    );

    if (relevantMetrics.length === 0) return;

    // Get the latest metric
    const latest = relevantMetrics[0];
    const value = parseFloat(latest.value);
    const timestamp = new Date(latest.timestamp);

    setCurrentValue(value);

    // Add new data point
    setDataPoints((prev) => {
      const newPoint: MetricDataPoint = {
        timestamp: latest.timestamp,
        value,
        time: timestamp.toLocaleTimeString(),
      };

      const updated = [...prev, newPoint];

      // Keep only the last N points
      if (updated.length > maxDataPoints) {
        updated.shift();
      }

      // Calculate trend
      if (updated.length >= 2) {
        const lastValue = updated[updated.length - 2].value;
        const change = ((value - lastValue) / lastValue) * 100;

        if (change > 5) {
          setTrend('up');
        } else if (change < -5) {
          setTrend('down');
        } else {
          setTrend('stable');
        }
      }

      return updated;
    });
  };

  const getTrendIcon = () => {
    if (trend === 'up') {
      return <TrendingUpIcon style={{ color: '#4caf50', fontSize: 20 }} />;
    } else if (trend === 'down') {
      return <TrendingDownIcon style={{ color: '#f44336', fontSize: 20 }} />;
    }
    return <RemoveIcon style={{ color: '#2196f3', fontSize: 20 }} />;
  };

  const getStatusBadge = () => {
    if (ws.status === 'connecting') {
      return <Badge status="processing" text="Connecting..." />;
    } else if (ws.status === 'connected') {
      return <Badge status="success" text="Live" />;
    } else if (ws.status === 'error') {
      return <Badge status="error" text="Error" />;
    }
    return <Badge status="default" text="Disconnected" />;
  };

  return (
    <Card
      title={
        <Space>
          {title}
          {getStatusBadge()}
        </Space>
      }
      extra={
        <Space>
          {getTrendIcon()}
          <Text strong style={{ fontSize: 18 }}>
            {currentValue !== null ? `${currentValue.toFixed(1)}${unit}` : '--'}
          </Text>
        </Space>
      }
      bordered={false}
      style={{ marginBottom: 16 }}
    >
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={dataPoints}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="time"
            tick={{ fontSize: 12 }}
            stroke="#666"
          />
          <YAxis
            tick={{ fontSize: 12 }}
            stroke="#666"
            label={{
              value: unit,
              angle: -90,
              position: 'insideLeft',
              style: { fontSize: 12 },
            }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e0e0e0',
              borderRadius: 4,
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="value"
            name={title}
            stroke={color}
            strokeWidth={2}
            dot={false}
            isAnimationActive={true}
            animationDuration={300}
          />
        </LineChart>
      </ResponsiveContainer>

      {dataPoints.length === 0 && (
        <div className="live-metrics-empty">
          <p>Waiting for live data...</p>
          <p className="live-metrics-empty-subtitle">
            Make sure the backend is collecting metrics
          </p>
        </div>
      )}
    </Card>
  );
};

/**
 * Multiple Live Metrics Dashboard
 */
export const LiveMetricsDashboard: React.FC = () => {
  return (
    <div className="live-metrics-dashboard">
      <Typography.Title level={3}>Live Network Metrics</Typography.Title>
      <Typography.Paragraph type="secondary">
        Real-time updates from your network devices via WebSocket
      </Typography.Paragraph>

      <div className="live-metrics-grid">
        <LiveMetricsChart
          metricType="bandwidth"
          title="Bandwidth Usage"
          unit=" Mbps"
          color="#1976d2"
        />
        <LiveMetricsChart
          metricType="clients"
          title="Connected Clients"
          unit=" clients"
          color="#2e7d32"
        />
        <LiveMetricsChart
          metricType="cpu"
          title="Average CPU Usage"
          unit="%"
          color="#ed6c02"
        />
        <LiveMetricsChart
          metricType="memory"
          title="Average Memory Usage"
          unit="%"
          color="#9c27b0"
        />
      </div>
    </div>
  );
};

export default LiveMetricsChart;

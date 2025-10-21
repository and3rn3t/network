/**
 * Enhanced Historical Performance Trends Page
 * Comprehensive historical analysis with multiple metrics and comparison
 */

import { MaterialCard } from "@/components/MaterialCard";
import { useDevices } from "@/hooks/useDevices";
import {
  useDeviceHistoricalMetrics,
  useExportDeviceMetricsCSV,
  useExportDeviceMetricsJSON,
} from "@/hooks/useHistorical";
import {
  DownloadOutlined,
  InfoCircleOutlined,
  LineChartOutlined,
} from "@ant-design/icons";
import {
  Alert,
  Button,
  Col,
  Divider,
  Row,
  Select,
  Space,
  Statistic,
  Tabs,
  Typography,
  message,
} from "antd";
import { useMemo, useState } from "react";
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

const { Text, Title } = Typography;
const { Option } = Select;

// Time range options
const TIME_RANGES = [
  { value: 7, label: "Last 7 Days" },
  { value: 30, label: "Last 30 Days" },
  { value: 90, label: "Last 90 Days" },
];

export const HistoricalPerformanceTrends = () => {
  const [selectedDeviceMac, setSelectedDeviceMac] = useState<
    string | undefined
  >();
  const [days, setDays] = useState<number>(7);

  // Fetch devices list
  const { data: devicesResponse, isLoading: devicesLoading } = useDevices();
  const devices = devicesResponse?.devices || [];

  // Fetch historical metrics for selected device
  const {
    data: metricsData,
    isLoading: metricsLoading,
    error: metricsError,
  } = useDeviceHistoricalMetrics(selectedDeviceMac, days);

  // Export mutations
  const exportCSVMutation = useExportDeviceMetricsCSV();
  const exportJSONMutation = useExportDeviceMetricsJSON();

  // Get selected device info
  const selectedDevice = useMemo(
    () => devices.find((d) => d.mac === selectedDeviceMac),
    [devices, selectedDeviceMac]
  );

  // Process metrics for charts
  const chartData = useMemo(() => {
    if (!metricsData?.metrics) return {};

    const result: Record<string, any[]> = {};

    metricsData.metrics.forEach((metric) => {
      const dataPoints = metric.data.map((point) => ({
        timestamp: new Date(point.timestamp).getTime(),
        value: point.value,
        formattedTime: new Date(point.timestamp).toLocaleString(),
      }));
      result[metric.metric_name] = dataPoints;
    });

    return result;
  }, [metricsData]);

  // Get statistics for each metric
  const statistics = useMemo(() => {
    if (!metricsData?.metrics) return {};

    const result: Record<string, any> = {};
    metricsData.metrics.forEach((metric) => {
      result[metric.metric_name] = metric.statistics;
    });
    return result;
  }, [metricsData]);

  const handleDeviceChange = (mac: string) => {
    setSelectedDeviceMac(mac);
  };

  const handleTimeRangeChange = (value: number) => {
    setDays(value);
  };

  const handleExportCSV = () => {
    if (!selectedDeviceMac) {
      message.warning("Please select a device first");
      return;
    }

    exportCSVMutation.mutate({
      deviceMac: selectedDeviceMac,
      days,
    });
  };

  const handleExportJSON = () => {
    if (!selectedDeviceMac) {
      message.warning("Please select a device first");
      return;
    }

    exportJSONMutation.mutate({
      deviceMac: selectedDeviceMac,
      days,
    });
  };

  // Custom tooltip for charts
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div
          style={{
            backgroundColor: "var(--md-sys-color-surface-container)",
            padding: "12px",
            borderRadius: "8px",
            border: "1px solid var(--md-sys-color-outline)",
          }}
        >
          <Text strong style={{ display: "block", marginBottom: "8px" }}>
            {payload[0].payload.formattedTime}
          </Text>
          <Text style={{ color: "var(--md-sys-color-primary)" }}>
            {payload[0].value.toFixed(2)} {payload[0].unit}
          </Text>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ padding: "24px" }}>
      {/* Page Header */}
      <div style={{ marginBottom: "24px" }}>
        <Title level={2}>
          <LineChartOutlined style={{ marginRight: "12px" }} />
          Historical Performance Trends
        </Title>
        <Text type="secondary">
          Analyze device performance over time with detailed metrics and
          statistics
        </Text>
      </div>

      {/* Info Banner */}
      <Alert
        message="Historical Analysis"
        description="View long-term performance trends, detect anomalies, and analyze patterns over 7, 30, or 90 days. Data is automatically aggregated for better performance on longer time ranges."
        type="info"
        icon={<InfoCircleOutlined />}
        showIcon
        closable
        style={{ marginBottom: "24px" }}
      />

      {/* Controls */}
      <MaterialCard style={{ marginBottom: "24px" }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} md={12}>
            <Space direction="vertical" style={{ width: "100%" }}>
              <Text strong>Select Device</Text>
              <Select
                showSearch
                placeholder="Choose a device to analyze"
                value={selectedDeviceMac}
                onChange={handleDeviceChange}
                loading={devicesLoading}
                style={{ width: "100%" }}
                size="large"
                optionFilterProp="children"
              >
                {devices.map((device) => (
                  <Option key={device.mac} value={device.mac}>
                    {device.name || device.mac} - {device.model}
                  </Option>
                ))}
              </Select>
            </Space>
          </Col>

          <Col xs={24} md={12}>
            <Space direction="vertical" style={{ width: "100%" }}>
              <Text strong>Time Range</Text>
              <Select
                value={days}
                onChange={handleTimeRangeChange}
                style={{ width: "100%" }}
                size="large"
              >
                {TIME_RANGES.map((range) => (
                  <Option key={range.value} value={range.value}>
                    {range.label}
                  </Option>
                ))}
              </Select>
            </Space>
          </Col>
        </Row>

        {selectedDeviceMac && (
          <div style={{ marginTop: "16px" }}>
            <Divider />
            <Space>
              <Button
                icon={<DownloadOutlined />}
                onClick={handleExportCSV}
                loading={exportCSVMutation.isPending}
              >
                Export CSV
              </Button>
              <Button
                icon={<DownloadOutlined />}
                onClick={handleExportJSON}
                loading={exportJSONMutation.isPending}
              >
                Export JSON
              </Button>
            </Space>
          </div>
        )}
      </MaterialCard>

      {/* Loading/Error States */}
      {metricsLoading && selectedDeviceMac && (
        <MaterialCard>
          <Text>Loading metrics data...</Text>
        </MaterialCard>
      )}

      {metricsError && (
        <Alert
          message="Error Loading Data"
          description="Failed to load historical metrics. Please try again."
          type="error"
          showIcon
        />
      )}

      {/* Metrics Display */}
      {metricsData && selectedDeviceMac && !metricsLoading && (
        <>
          {/* Device Info */}
          <MaterialCard style={{ marginBottom: "24px" }}>
            <Row gutter={16}>
              <Col span={24}>
                <Title level={4}>
                  {selectedDevice?.name || "Unknown Device"}
                </Title>
                <Space split={<Divider type="vertical" />}>
                  <Text type="secondary">MAC: {selectedDeviceMac}</Text>
                  <Text type="secondary">Model: {selectedDevice?.model}</Text>
                  <Text type="secondary">
                    Time Range: {metricsData.time_range}
                  </Text>
                </Space>
              </Col>
            </Row>
          </MaterialCard>

          {/* Metrics Tabs */}
          <MaterialCard>
            <Tabs
              items={metricsData.metrics.map((metric) => ({
                key: metric.metric_name,
                label: (
                  <span style={{ textTransform: "capitalize" }}>
                    {metric.metric_name.replace(/_/g, " ")}
                  </span>
                ),
                children: (
                  <div>
                    {/* Statistics */}
                    <Row gutter={16} style={{ marginBottom: "24px" }}>
                      <Col span={4}>
                        <Statistic
                          title="Latest"
                          value={metric.statistics.latest?.toFixed(2) || "N/A"}
                          suffix={metric.unit}
                        />
                      </Col>
                      <Col span={4}>
                        <Statistic
                          title="Average"
                          value={metric.statistics.avg.toFixed(2)}
                          suffix={metric.unit}
                        />
                      </Col>
                      <Col span={4}>
                        <Statistic
                          title="Minimum"
                          value={metric.statistics.min.toFixed(2)}
                          suffix={metric.unit}
                        />
                      </Col>
                      <Col span={4}>
                        <Statistic
                          title="Maximum"
                          value={metric.statistics.max.toFixed(2)}
                          suffix={metric.unit}
                        />
                      </Col>
                      <Col span={4}>
                        <Statistic
                          title="95th Percentile"
                          value={metric.statistics.p95?.toFixed(2) || "N/A"}
                          suffix={metric.unit}
                        />
                      </Col>
                      <Col span={4}>
                        <Statistic
                          title="99th Percentile"
                          value={metric.statistics.p99?.toFixed(2) || "N/A"}
                          suffix={metric.unit}
                        />
                      </Col>
                    </Row>

                    {/* Chart */}
                    <ResponsiveContainer width="100%" height={400}>
                      <LineChart data={chartData[metric.metric_name] || []}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey="timestamp"
                          type="number"
                          domain={["dataMin", "dataMax"]}
                          tickFormatter={(value) =>
                            new Date(value).toLocaleDateString()
                          }
                        />
                        <YAxis
                          label={{
                            value: metric.unit,
                            angle: -90,
                            position: "insideLeft",
                          }}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="value"
                          stroke="var(--md-sys-color-primary)"
                          strokeWidth={2}
                          dot={false}
                          name={metric.metric_name}
                        />
                      </LineChart>
                    </ResponsiveContainer>

                    <Text
                      type="secondary"
                      style={{ marginTop: "16px", display: "block" }}
                    >
                      Data points: {metric.statistics.count}
                    </Text>
                  </div>
                ),
              }))}
            />
          </MaterialCard>
        </>
      )}

      {/* No Device Selected */}
      {!selectedDeviceMac && !devicesLoading && (
        <MaterialCard>
          <div
            style={{
              textAlign: "center",
              padding: "48px 24px",
            }}
          >
            <LineChartOutlined
              style={{
                fontSize: "64px",
                color: "var(--md-sys-color-primary)",
                marginBottom: "16px",
              }}
            />
            <Title level={3}>Select a Device to Begin</Title>
            <Text type="secondary">
              Choose a device from the dropdown above to view its historical
              performance trends and detailed metrics analysis.
            </Text>
          </div>
        </MaterialCard>
      )}
    </div>
  );
};

export default HistoricalPerformanceTrends;

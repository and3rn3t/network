/**
 * Enhanced Historical Performance Trends Page
 * Comprehensive historical analysis for client devices
 */

import { MaterialCard } from "@/components/MaterialCard";
import { useClients } from "@/hooks/useClients";
import {
  useClientHistoricalMetrics,
  useExportClientMetricsCSV,
  useExportClientMetricsJSON,
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

export const Historical = () => {
  const [selectedClientMac, setSelectedClientMac] = useState<
    string | undefined
  >();
  const [days, setDays] = useState<number>(7);

  // Fetch clients list
  const { data: clientsResponse, isLoading: clientsLoading } = useClients();
  const clients = clientsResponse?.clients || [];

  // Fetch historical metrics for selected client
  const {
    data: metricsData,
    isLoading: metricsLoading,
    error: metricsError,
  } = useClientHistoricalMetrics(selectedClientMac, days);

  // Export mutations
  const exportCSVMutation = useExportClientMetricsCSV();
  const exportJSONMutation = useExportClientMetricsJSON();

  // Get selected client info
  const selectedClient = useMemo(
    () => clients.find((c) => c.mac === selectedClientMac),
    [clients, selectedClientMac]
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

  const handleClientChange = (mac: string) => {
    setSelectedClientMac(mac);
  };

  const handleTimeRangeChange = (value: number) => {
    setDays(value);
  };

  const handleExportCSV = () => {
    if (!selectedClientMac) {
      message.warning("Please select a client first");
      return;
    }

    exportCSVMutation.mutate({
      clientMac: selectedClientMac,
      days,
    });
  };

  const handleExportJSON = () => {
    if (!selectedClientMac) {
      message.warning("Please select a client first");
      return;
    }

    exportJSONMutation.mutate({
      clientMac: selectedClientMac,
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
          Client Performance History
        </Title>
        <Text type="secondary">
          Analyze client WiFi performance over time with signal strength,
          bandwidth, and connection quality metrics
        </Text>
      </div>

      {/* Info Banner */}
      <Alert
        message="Historical Analysis"
        description="View long-term client performance trends, analyze WiFi signal patterns, and track bandwidth usage over 7, 30, or 90 days. Perfect for troubleshooting connectivity issues and optimizing placement."
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
              <Text strong>Select Client Device</Text>
              <Select
                showSearch
                placeholder="Choose a client to analyze"
                value={selectedClientMac}
                onChange={handleClientChange}
                loading={clientsLoading}
                style={{ width: "100%" }}
                size="large"
                optionFilterProp="children"
              >
                {clients.map((client) => (
                  <Option key={client.mac} value={client.mac}>
                    {client.hostname || client.name || client.mac}
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

        {selectedClientMac && (
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
      {metricsLoading && selectedClientMac && (
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
      {metricsData && selectedClientMac && !metricsLoading && (
        <>
          {/* Client Info */}
          <MaterialCard style={{ marginBottom: "24px" }}>
            <Row gutter={16}>
              <Col span={24}>
                <Title level={4}>
                  {selectedClient?.hostname ||
                    selectedClient?.name ||
                    "Unknown Client"}
                </Title>
                <Space split={<Divider type="vertical" />}>
                  <Text type="secondary">MAC: {selectedClientMac}</Text>
                  <Text type="secondary">IP: {selectedClient?.ip}</Text>
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

      {/* No Client Selected */}
      {!selectedClientMac && !clientsLoading && (
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
            <Title level={3}>Select a Client to Begin</Title>
            <Text type="secondary">
              Choose a client device from the dropdown above to view its WiFi
              performance history, signal strength trends, and bandwidth usage.
            </Text>
          </div>
        </MaterialCard>
      )}
    </div>
  );
};

export default Historical;

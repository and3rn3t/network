/**
 * Enhanced Historical Performance Trends Page
 * Comprehensive historical analysis for client devices
 */

import { MaterialCard } from "@/components/MaterialCard";
import { useGlobalFilters } from "@/contexts/GlobalFilterContext";
import { usePageMetadata } from "@/contexts/PageMetadataContext";
import { useClients } from "@/hooks/useClients";
import {
  useClientHistoricalMetrics,
  useExportClientMetricsCSV,
  useExportClientMetricsJSON,
} from "@/hooks/useHistorical";
import type { Client } from "@/types/client";
import {
  ClockCircleOutlined,
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
  Tag,
  Typography,
  message,
} from "antd";
import { useEffect, useMemo, useState } from "react";
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
import "./Historical.css";

const { Text, Title } = Typography;
const { Option } = Select;

// Custom tooltip component for charts
interface TooltipProps {
  active?: boolean;
  payload?: Array<{
    value: number;
    unit?: string;
    payload: {
      formattedTime: string;
    };
  }>;
}

const CustomTooltip: React.FC<TooltipProps> = ({ active, payload }) => {
  if (active && payload?.length) {
    return (
      <div className="historical-tooltip">
        <Text strong className="historical-tooltip-title">
          {payload[0].payload.formattedTime}
        </Text>
        <Text className="historical-tooltip-value">
          {payload[0].value.toFixed(2)} {payload[0].unit || ""}
        </Text>
      </div>
    );
  }
  return null;
};

export const Historical = () => {
  const [selectedClientMac, setSelectedClientMac] = useState<
    string | undefined
  >();
  const { setMetadata } = usePageMetadata();
  const { timeRange } = useGlobalFilters();

  useEffect(() => {
    setMetadata({
      title: "Client Performance History",
      description:
        "Analyze signal strength, throughput, and stability trends over time",
      icon: <LineChartOutlined />,
      showFilters: true,
      filtersConfig: {
        showSitePicker: false,
      },
    });
  }, [setMetadata]);

  const selectedDays = useMemo(() => {
    if (timeRange.start && timeRange.end) {
      const diffHours = timeRange.end.diff(timeRange.start, "hour", true);
      if (Number.isFinite(diffHours) && diffHours > 0) {
        return Math.max(1, Math.ceil(diffHours / 24));
      }
    }
    return Math.max(1, Math.ceil((timeRange.hours ?? 24) / 24));
  }, [timeRange]);

  const timeRangeLabel = timeRange.label || "Custom Range";

  // Fetch clients list
  const { data: clientsResponse, isLoading: clientsLoading } = useClients();

  // Memoize clients array to prevent unnecessary re-renders
  const clients = useMemo(
    () => clientsResponse?.clients || [],
    [clientsResponse?.clients]
  );

  // Fetch historical metrics for selected client
  const {
    data: metricsData,
    isLoading: metricsLoading,
    error: metricsError,
  } = useClientHistoricalMetrics(selectedClientMac, selectedDays);

  // Export mutations
  const exportCSVMutation = useExportClientMetricsCSV();
  const exportJSONMutation = useExportClientMetricsJSON();

  // Get selected client info
  const selectedClient = useMemo(
    () => clients.find((c: Client) => c.mac === selectedClientMac),
    [clients, selectedClientMac]
  );

  // Process metrics for charts
  const chartData = useMemo(() => {
    if (!metricsData?.metrics) return {};

    const result: Record<
      string,
      Array<{
        timestamp: number;
        value: number;
        formattedTime: string;
      }>
    > = {};

    for (const metric of metricsData.metrics) {
      const dataPoints = metric.data.map((point) => ({
        timestamp: new Date(point.timestamp).getTime(),
        value: point.value,
        formattedTime: new Date(point.timestamp).toLocaleString(),
      }));
      result[metric.metric_name] = dataPoints;
    }

    return result;
  }, [metricsData]);

  const handleClientChange = (mac: string) => {
    setSelectedClientMac(mac);
  };

  const handleExportCSV = () => {
    if (!selectedClientMac) {
      message.warning("Please select a client first");
      return;
    }

    exportCSVMutation.mutate({
      clientMac: selectedClientMac,
      days: selectedDays,
    });
  };

  const handleExportJSON = () => {
    if (!selectedClientMac) {
      message.warning("Please select a client first");
      return;
    }

    exportJSONMutation.mutate({
      clientMac: selectedClientMac,
      days: selectedDays,
    });
  };

  return (
    <div className="historical-page">
      {/* Info Banner */}
      <Alert
        message="Historical Analysis"
        description="Use the global time range filter above to view long-term client performance trends, analyze WiFi signal patterns, and track bandwidth usage."
        type="info"
        icon={<InfoCircleOutlined />}
        showIcon
        closable
        className="historical-banner"
      />

      {/* Controls */}
      <MaterialCard className="historical-control-card">
        <Row gutter={[16, 16]}>
          <Col xs={24} md={12}>
            <Space direction="vertical" className="historical-full-width">
              <Text strong>Select Client Device</Text>
              <Select
                showSearch
                placeholder="Choose a client to analyze"
                value={selectedClientMac}
                onChange={handleClientChange}
                loading={clientsLoading}
                className="historical-full-width"
                size="large"
                optionFilterProp="children"
              >
                {clients.map((client: Client) => (
                  <Option key={client.mac} value={client.mac}>
                    {client.hostname || client.name || client.mac}
                  </Option>
                ))}
              </Select>
            </Space>
          </Col>

          <Col xs={24} md={12}>
            <Space direction="vertical" className="historical-full-width">
              <Text strong>Time Range</Text>
              <Tag
                icon={<ClockCircleOutlined />}
                color="var(--md-sys-color-primary-container)"
                className="historical-time-range-tag"
              >
                {timeRangeLabel}
              </Tag>
              <Text type="secondary" className="historical-time-range-hint">
                Adjust the analysis window using the global filters above.
              </Text>
            </Space>
          </Col>
        </Row>

        {selectedClientMac && (
          <div className="historical-export-actions">
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
          <MaterialCard className="historical-client-card">
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
                  <span className="historical-metric-title">
                    {metric.metric_name.replaceAll("_", " ")}
                  </span>
                ),
                children: (
                  <div>
                    {/* Statistics */}
                    <Row gutter={16} className="historical-metric-stats">
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

                    <Text type="secondary" className="historical-data-label">
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
          <div className="historical-empty-state">
            <LineChartOutlined className="historical-empty-icon" />
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

import { MaterialCard } from "@/components/MaterialCard";
import type { TimeRange } from "@/components/TimeRangeSelector";
import { TimeRangeSelector } from "@/components/TimeRangeSelector";
import { ComparisonChart } from "@/components/charts/ComparisonChart";
import { useClients } from "@/hooks/useClients";
import { useClientHistoricalMetrics } from "@/hooks/useHistorical";
import type { Client } from "@/types/client";
import {
  CloseCircleOutlined,
  DownloadOutlined,
  InfoCircleOutlined,
  SwapOutlined,
} from "@ant-design/icons";
import {
  Alert,
  Button,
  Col,
  Divider,
  Empty,
  Row,
  Select,
  Space,
  Tag,
  Typography,
} from "antd";
import { useState } from "react";

const { Text } = Typography;
const { Option } = Select;

interface SelectedClient {
  id: string; // Use MAC as ID for compatibility with ComparisonChart
  mac: string;
  name: string;
  color: string;
}

// Color palette for client comparison - using Material Design 3 colors
const CLIENT_COLORS = [
  "var(--md-sys-color-primary)",
  "var(--md-sys-color-secondary)",
  "var(--md-sys-color-tertiary)",
  "#722ed1", // Purple
  "#eb2f96", // Pink
  "#13c2c2", // Cyan
  "#faad14", // Gold
  "#a0d911", // Lime
];

export const Comparison = () => {
  const [selectedClients, setSelectedClients] = useState<SelectedClient[]>([]);
  const [timeRange, setTimeRange] = useState<TimeRange>({
    hours: 24,
    label: "Last 24 Hours",
  });

  // Fetch clients list
  const { data: clientsResponse, isLoading: clientsLoading } = useClients();
  const clients = clientsResponse?.clients || [];

  // Convert hours to days for client historical metrics API
  const days = Math.ceil(timeRange.hours / 24);

  // Fetch metrics for all selected clients (up to 6)
  // Always call hooks the same number of times
  const metrics1 = useClientHistoricalMetrics(selectedClients[0]?.mac, days);
  const metrics2 = useClientHistoricalMetrics(selectedClients[1]?.mac, days);
  const metrics3 = useClientHistoricalMetrics(selectedClients[2]?.mac, days);
  const metrics4 = useClientHistoricalMetrics(selectedClients[3]?.mac, days);
  const metrics5 = useClientHistoricalMetrics(selectedClients[4]?.mac, days);
  const metrics6 = useClientHistoricalMetrics(selectedClients[5]?.mac, days);

  const metricsQueries = [
    metrics1,
    metrics2,
    metrics3,
    metrics4,
    metrics5,
    metrics6,
  ];

  const handleAddClient = (clientMac: string) => {
    const client = clients.find((c: Client) => c.mac === clientMac);
    if (!client) return;

    // Check if already selected
    if (selectedClients.some((c) => c.mac === clientMac)) {
      return;
    }

    // Add client with next available color
    const colorIndex = selectedClients.length % CLIENT_COLORS.length;
    const newClient: SelectedClient = {
      id: clientMac, // Use MAC as ID for compatibility
      mac: clientMac,
      name: client.hostname || client.name || client.mac,
      color: CLIENT_COLORS[colorIndex],
    };

    setSelectedClients([...selectedClients, newClient]);
  };

  const handleRemoveClient = (clientMac: string) => {
    setSelectedClients(selectedClients.filter((c) => c.mac !== clientMac));
  };

  const handleTimeRangeChange = (range: TimeRange) => {
    setTimeRange(range);
  };

  const handleExportComparison = () => {
    // Prepare comparison data for export
    const exportData = {
      timestamp: new Date().toISOString(),
      timeRange: timeRange.label,
      clients: selectedClients.map((client, index) => ({
        ...client,
        metrics: metricsQueries[index].data?.metrics || [],
      })),
    };

    // Create JSON blob and download
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `client-comparison-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const availableClients = clients.filter(
    (client: Client) => !selectedClients.some((c) => c.mac === client.mac)
  );

  // Combine metrics from all clients and transform to ComparisonChart format
  const comparisonData = selectedClients.map((client, index) => {
    const queryData = metricsQueries[index].data;

    // Transform MetricTimeSeries[] to DeviceMetric[] format
    const transformedMetrics =
      queryData?.metrics?.flatMap((metricSeries) =>
        metricSeries.data.map((point) => ({
          recorded_at: point.timestamp,
          metric_value: point.value,
          metric_type: metricSeries.metric_name,
        }))
      ) || [];

    return {
      device: client, // Keep property name for compatibility with ComparisonChart
      metrics: transformedMetrics,
      loading: metricsQueries[index].isLoading,
      error: metricsQueries[index].error,
    };
  });

  return (
    <div>
      {/* Page Header */}
      <div
        className="page-header"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
        }}
      >
        <div>
          <h1 className="page-header-title">
            <SwapOutlined style={{ marginRight: 12 }} />
            Client Performance Comparison
          </h1>
          <p className="page-header-description">
            Compare WiFi performance metrics across multiple clients
          </p>
        </div>

        {selectedClients.length >= 2 && (
          <Button
            type="primary"
            icon={<DownloadOutlined />}
            onClick={handleExportComparison}
            size="large"
          >
            Export Comparison
          </Button>
        )}
      </div>

      <Divider style={{ margin: "24px 0" }} />

      {/* Controls */}
      <MaterialCard elevation={1} style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} md={16}>
            <Space direction="vertical" style={{ width: "100%" }}>
              <Text strong>Add Clients to Compare:</Text>
              <Select
                showSearch
                placeholder="Select a client to add to comparison"
                optionFilterProp="children"
                onChange={handleAddClient}
                loading={clientsLoading}
                style={{ width: "100%" }}
                size="large"
                value={undefined}
                disabled={selectedClients.length >= 6}
              >
                {availableClients.map((client: Client) => (
                  <Option key={client.mac} value={client.mac}>
                    {client.hostname || client.name || client.mac} - {client.ip}
                  </Option>
                ))}
              </Select>
              <Text style={{ fontSize: 12, color: "rgba(0, 0, 0, 0.65)" }}>
                Select up to 6 clients for comparison
              </Text>
            </Space>
          </Col>

          <Col xs={24} md={8}>
            <Space direction="vertical" style={{ width: "100%" }}>
              <Text strong>Time Range:</Text>
              <TimeRangeSelector
                onChange={handleTimeRangeChange}
                defaultHours={24}
                showQuickOptions={true}
              />
            </Space>
          </Col>
        </Row>

        {/* Selected Clients */}
        {selectedClients.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <Text strong>Selected Clients ({selectedClients.length}):</Text>
            <div style={{ marginTop: 8 }}>
              <Space wrap>
                {selectedClients.map((client) => (
                  <Tag
                    key={client.id}
                    color={client.color}
                    closable
                    onClose={() => handleRemoveClient(client.mac)}
                    icon={<CloseCircleOutlined />}
                    style={{ padding: "4px 8px", fontSize: 14 }}
                  >
                    {client.name}
                  </Tag>
                ))}
              </Space>
            </div>
          </div>
        )}

        {selectedClients.length >= 2 && (
          <Alert
            message={
              <span>
                <InfoCircleOutlined /> Comparing {selectedClients.length}{" "}
                clients over {timeRange.label.toLowerCase()}
              </span>
            }
            type="info"
            showIcon={false}
            style={{ marginTop: 16 }}
          />
        )}

        {selectedClients.length === 1 && (
          <Alert
            message="Add at least one more client to see comparison charts"
            type="warning"
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
      </MaterialCard>

      {/* Comparison Charts */}
      {selectedClients.length >= 2 ? (
        <Row gutter={[16, 16]}>
          <Col xs={24}>
            <ComparisonChart
              data={comparisonData}
              metricType="signal_strength"
              title="WiFi Signal Strength Comparison"
              unit="dBm"
              timeRange={timeRange}
            />
          </Col>

          <Col xs={24}>
            <ComparisonChart
              data={comparisonData}
              metricType="tx_rate"
              title="Upload Speed Comparison"
              unit="Mbps"
              timeRange={timeRange}
            />
          </Col>

          <Col xs={24}>
            <ComparisonChart
              data={comparisonData}
              metricType="rx_rate"
              title="Download Speed Comparison"
              unit="Mbps"
              timeRange={timeRange}
            />
          </Col>

          <Col xs={24}>
            <ComparisonChart
              data={comparisonData}
              metricType="satisfaction"
              title="Connection Quality Comparison"
              unit="score"
              timeRange={timeRange}
            />
          </Col>
        </Row>
      ) : selectedClients.length === 1 ? (
        <MaterialCard elevation={1}>
          <Empty
            description={
              <span>
                <Text>
                  You've selected 1 client. Add at least one more client to see
                  comparison charts.
                </Text>
              </span>
            }
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        </MaterialCard>
      ) : (
        <MaterialCard elevation={1}>
          <Empty
            description={
              <span>
                <Text>
                  No clients selected. Use the dropdown above to add clients to
                  compare.
                </Text>
              </span>
            }
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        </MaterialCard>
      )}
    </div>
  );
};

export default Comparison;

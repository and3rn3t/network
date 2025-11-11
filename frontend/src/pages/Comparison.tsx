import { MaterialCard } from "@/components/MaterialCard";
import { ComparisonChart } from "@/components/charts/ComparisonChart";
import { useGlobalFilters } from "@/contexts/GlobalFilterContext";
import { usePageMetadata } from "@/contexts/PageMetadataContext";
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
  Empty,
  Row,
  Select,
  Space,
  Tag,
  Typography,
} from "antd";
import { useCallback, useEffect, useMemo, useState } from "react";
import "./Comparison.css";

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
  const { timeRange } = useGlobalFilters();
  const { setMetadata } = usePageMetadata();

  useEffect(() => {
    setMetadata({
      title: "Client Performance Comparison",
      description: "Compare WiFi performance metrics across multiple clients",
      icon: <SwapOutlined />,
      showFilters: true,
      filtersConfig: {
        showSitePicker: false,
      },
    });
  }, [setMetadata]);

  // Fetch clients list
  const { data: clientsResponse, isLoading: clientsLoading } = useClients();
  const clients = clientsResponse?.clients || [];

  // Convert hours to days for client historical metrics API
  const days = useMemo(() => {
    if (timeRange.start && timeRange.end) {
      const diffHours = timeRange.end.diff(timeRange.start, "hour", true);
      if (Number.isFinite(diffHours) && diffHours > 0) {
        return Math.max(1, Math.ceil(diffHours / 24));
      }
    }
    return Math.max(1, Math.ceil((timeRange.hours ?? 24) / 24));
  }, [timeRange]);

  // Fetch metrics for all selected clients (up to 6)
  // Always call hooks the same number of times
  const metrics1 = useClientHistoricalMetrics(selectedClients[0]?.mac, days);
  const metrics2 = useClientHistoricalMetrics(selectedClients[1]?.mac, days);
  const metrics3 = useClientHistoricalMetrics(selectedClients[2]?.mac, days);
  const metrics4 = useClientHistoricalMetrics(selectedClients[3]?.mac, days);
  const metrics5 = useClientHistoricalMetrics(selectedClients[4]?.mac, days);
  const metrics6 = useClientHistoricalMetrics(selectedClients[5]?.mac, days);

  const metricsQueries = useMemo(
    () => [metrics1, metrics2, metrics3, metrics4, metrics5, metrics6],
    [metrics1, metrics2, metrics3, metrics4, metrics5, metrics6]
  );

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

  const handleExportComparison = useCallback(() => {
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
  }, [metricsQueries, selectedClients, timeRange.label]);

  useEffect(() => {
    if (selectedClients.length >= 2) {
      setMetadata({
        actions: (
          <Button
            type="primary"
            icon={<DownloadOutlined />}
            onClick={handleExportComparison}
            size="large"
          >
            Export Comparison
          </Button>
        ),
      });
    } else {
      setMetadata({ actions: undefined });
    }

    return () => {
      setMetadata({ actions: undefined });
    };
  }, [handleExportComparison, selectedClients.length, setMetadata]);

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

  const timeRangeLabel = timeRange.label || "Custom Range";

  return (
    <div className="comparison-page">
      {/* Controls */}
      <MaterialCard elevation={1} className="comparison-control-card">
        <Row gutter={[16, 16]}>
          <Col xs={24} md={16}>
            <Space direction="vertical" className="comparison-section">
              <Text strong>Add Clients to Compare</Text>
              <Select
                showSearch
                placeholder="Select a client to add to comparison"
                optionFilterProp="children"
                onChange={handleAddClient}
                loading={clientsLoading}
                className="comparison-full-width"
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
              <Text className="comparison-hint">
                Select up to 6 clients for comparison
              </Text>
            </Space>
          </Col>

          <Col xs={24} md={8}>
            <Space direction="vertical" className="comparison-section">
              <Text strong>Time Range</Text>
              <Tag
                icon={<SwapOutlined />}
                className="comparison-time-range-tag"
                color="var(--md-sys-color-primary-container)"
              >
                {timeRangeLabel}
              </Tag>
              <Text type="secondary" className="comparison-hint">
                Adjust the window using the global filters above.
              </Text>
            </Space>
          </Col>
        </Row>

        {/* Selected Clients */}
        {selectedClients.length > 0 && (
          <div className="comparison-selected">
            <Text strong>Selected Clients ({selectedClients.length})</Text>
            <div className="comparison-tags">
              <Space wrap>
                {selectedClients.map((client) => (
                  <Tag
                    key={client.id}
                    color={client.color}
                    closable
                    onClose={() => handleRemoveClient(client.mac)}
                    closeIcon={<CloseCircleOutlined />}
                    className="comparison-client-tag"
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
                clients over {timeRangeLabel.toLowerCase()}
              </span>
            }
            type="info"
            showIcon={false}
            className="comparison-alert"
          />
        )}

        {selectedClients.length === 1 && (
          <Alert
            message="Add at least one more client to see comparison charts"
            type="warning"
            showIcon
            className="comparison-alert"
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

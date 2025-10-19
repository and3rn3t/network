import { MaterialCard } from "@/components/MaterialCard";
import type { TimeRange } from "@/components/TimeRangeSelector";
import { TimeRangeSelector } from "@/components/TimeRangeSelector";
import { ComparisonChart } from "@/components/charts/ComparisonChart";
import { useDeviceMetrics, useDevices } from "@/hooks/useDevices";
import type { Device } from "@/types/device";
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

interface SelectedDevice {
  id: string;
  name: string;
  color: string;
}

// Color palette for device comparison - using Material Design 3 colors
const DEVICE_COLORS = [
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
  const [selectedDevices, setSelectedDevices] = useState<SelectedDevice[]>([]);
  const [timeRange, setTimeRange] = useState<TimeRange>({
    hours: 24,
    label: "Last 24 Hours",
  });

  // Fetch devices list
  const { data: devicesResponse, isLoading: devicesLoading } = useDevices();
  const devices = devicesResponse?.devices || [];

  // Fetch metrics for all selected devices (up to 6)
  // Always call hooks the same number of times
  const metrics1 = useDeviceMetrics(selectedDevices[0]?.id, timeRange.hours);
  const metrics2 = useDeviceMetrics(selectedDevices[1]?.id, timeRange.hours);
  const metrics3 = useDeviceMetrics(selectedDevices[2]?.id, timeRange.hours);
  const metrics4 = useDeviceMetrics(selectedDevices[3]?.id, timeRange.hours);
  const metrics5 = useDeviceMetrics(selectedDevices[4]?.id, timeRange.hours);
  const metrics6 = useDeviceMetrics(selectedDevices[5]?.id, timeRange.hours);

  const metricsQueries = [
    metrics1,
    metrics2,
    metrics3,
    metrics4,
    metrics5,
    metrics6,
  ];

  const handleAddDevice = (deviceId: string) => {
    const device = devices.find((d: Device) => d.id.toString() === deviceId);
    if (!device) return;

    // Check if already selected
    if (selectedDevices.some((d) => d.id === deviceId)) {
      return;
    }

    // Add device with next available color
    const colorIndex = selectedDevices.length % DEVICE_COLORS.length;
    const newDevice: SelectedDevice = {
      id: deviceId,
      name: device.name || device.ip,
      color: DEVICE_COLORS[colorIndex],
    };

    setSelectedDevices([...selectedDevices, newDevice]);
  };

  const handleRemoveDevice = (deviceId: string) => {
    setSelectedDevices(selectedDevices.filter((d) => d.id !== deviceId));
  };

  const handleTimeRangeChange = (range: TimeRange) => {
    setTimeRange(range);
  };

  const handleExportComparison = () => {
    // Prepare comparison data for export
    const exportData = {
      timestamp: new Date().toISOString(),
      timeRange: timeRange.label,
      devices: selectedDevices.map((device, index) => ({
        ...device,
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
    link.download = `device-comparison-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const availableDevices = devices.filter(
    (device: Device) =>
      !selectedDevices.some((d) => d.id === device.id.toString())
  );

  // Combine metrics from all devices
  const comparisonData = selectedDevices.map((device, index) => ({
    device,
    metrics: metricsQueries[index].data?.metrics || [],
    loading: metricsQueries[index].isLoading,
    error: metricsQueries[index].error,
  }));

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
            Device Comparison
          </h1>
          <p className="page-header-description">
            Compare performance metrics across multiple devices
          </p>
        </div>

        {selectedDevices.length >= 2 && (
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
              <Text strong>Add Devices to Compare:</Text>
              <Select
                showSearch
                placeholder="Select a device to add to comparison"
                optionFilterProp="children"
                onChange={handleAddDevice}
                loading={devicesLoading}
                style={{ width: "100%" }}
                size="large"
                value={undefined}
                disabled={selectedDevices.length >= 6}
              >
                {availableDevices.map((device: Device) => (
                  <Option key={device.id} value={device.id.toString()}>
                    {device.name} ({device.model}) - {device.ip}
                  </Option>
                ))}
              </Select>
              <Text style={{ fontSize: 12, color: "rgba(0, 0, 0, 0.65)" }}>
                Select up to 6 devices for comparison
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

        {/* Selected Devices */}
        {selectedDevices.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <Text strong>Selected Devices ({selectedDevices.length}):</Text>
            <div style={{ marginTop: 8 }}>
              <Space wrap>
                {selectedDevices.map((device) => (
                  <Tag
                    key={device.id}
                    color={device.color}
                    closable
                    onClose={() => handleRemoveDevice(device.id)}
                    icon={<CloseCircleOutlined />}
                    style={{ padding: "4px 8px", fontSize: 14 }}
                  >
                    {device.name}
                  </Tag>
                ))}
              </Space>
            </div>
          </div>
        )}

        {selectedDevices.length >= 2 && (
          <Alert
            message={
              <span>
                <InfoCircleOutlined /> Comparing {selectedDevices.length}{" "}
                devices over {timeRange.label.toLowerCase()}
              </span>
            }
            type="info"
            showIcon={false}
            style={{ marginTop: 16 }}
          />
        )}

        {selectedDevices.length === 1 && (
          <Alert
            message="Add at least one more device to see comparison charts"
            type="warning"
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
      </MaterialCard>

      {/* Comparison Charts */}
      {selectedDevices.length >= 2 ? (
        <Row gutter={[16, 16]}>
          <Col xs={24}>
            <ComparisonChart
              data={comparisonData}
              metricType="cpu_usage"
              title="CPU Usage Comparison"
              unit="%"
              timeRange={timeRange}
            />
          </Col>

          <Col xs={24}>
            <ComparisonChart
              data={comparisonData}
              metricType="memory_usage"
              title="Memory Usage Comparison"
              unit="%"
              timeRange={timeRange}
            />
          </Col>

          <Col xs={24}>
            <ComparisonChart
              data={comparisonData}
              metricType="network_rx_mbps"
              title="Network Download Comparison"
              unit="Mbps"
              timeRange={timeRange}
            />
          </Col>

          <Col xs={24}>
            <ComparisonChart
              data={comparisonData}
              metricType="network_tx_mbps"
              title="Network Upload Comparison"
              unit="Mbps"
              timeRange={timeRange}
            />
          </Col>
        </Row>
      ) : selectedDevices.length === 1 ? (
        <MaterialCard elevation={1}>
          <Empty
            description={
              <span>
                <Text>
                  You've selected 1 device. Add at least one more device to see
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
                  No devices selected. Use the dropdown above to add devices to
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

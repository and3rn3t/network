/**
 * Historical Analysis Page
 * Primary value proposition - historical performance trends and analysis
 */

import { useState } from "react";
import {
  Card,
  Row,
  Col,
  Typography,
  Select,
  Space,
  Divider,
  Alert,
} from "antd";
import { LineChartOutlined, InfoCircleOutlined } from "@ant-design/icons";
import type { TimeRange } from "@/components/TimeRangeSelector";
import { TimeRangeSelector } from "@/components/TimeRangeSelector";
import { DevicePerformanceChart } from "@/components/charts/DevicePerformanceChart";
import { useDevices, useDeviceMetrics } from "@/hooks/useDevices";

const { Title, Text } = Typography;
const { Option } = Select;

export const Historical = () => {
  const [selectedDeviceId, setSelectedDeviceId] = useState<
    string | undefined
  >();
  const [timeRange, setTimeRange] = useState<TimeRange>({
    hours: 24,
    label: "Last 24 Hours",
  });

  // Fetch devices list
  const { data: devicesResponse, isLoading: devicesLoading } = useDevices();
  const devices = devicesResponse?.devices || [];

  // Fetch metrics for selected device
  const {
    data: metricsResponse,
    isLoading: metricsLoading,
    error: metricsError,
  } = useDeviceMetrics(selectedDeviceId, timeRange.hours);

  const metricsData = metricsResponse?.metrics || [];

  const handleDeviceChange = (deviceId: string) => {
    setSelectedDeviceId(deviceId);
  };

  const handleTimeRangeChange = (range: TimeRange) => {
    setTimeRange(range);
  };

  return (
    <div>
      <Title level={2}>
        <LineChartOutlined /> Historical Analysis
      </Title>
      <Text type="secondary" style={{ fontSize: "16px" }}>
        Analyze device performance trends over time
      </Text>

      <Divider />

      {/* Controls */}
      <Card style={{ marginBottom: "24px" }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} md={12}>
            <Space direction="vertical" style={{ width: "100%" }}>
              <Text strong>Select Device:</Text>
              <Select
                showSearch
                placeholder="Choose a device to analyze"
                optionFilterProp="children"
                onChange={handleDeviceChange}
                loading={devicesLoading}
                style={{ width: "100%" }}
                size="large"
                value={selectedDeviceId}
              >
                {devices.map((device: any) => (
                  <Option key={device.id} value={device.id}>
                    {device.name} ({device.model}) - {device.ip}
                  </Option>
                ))}
              </Select>
            </Space>
          </Col>

          <Col xs={24} md={12}>
            <Space direction="vertical" style={{ width: "100%" }}>
              <Text strong>Time Range:</Text>
              <TimeRangeSelector onChange={handleTimeRangeChange} />
            </Space>
          </Col>
        </Row>

        {selectedDeviceId && (
          <Alert
            message={
              <span>
                <InfoCircleOutlined /> Showing {timeRange.label.toLowerCase()}{" "}
                of historical data
              </span>
            }
            type="info"
            showIcon={false}
            style={{ marginTop: "16px" }}
          />
        )}
      </Card>

      {/* Performance Charts */}
      {selectedDeviceId ? (
        <Row gutter={[16, 16]}>
          <Col xs={24}>
            <DevicePerformanceChart
              data={metricsData}
              loading={metricsLoading}
              error={metricsError}
              metricType="cpu_usage"
              title="CPU Usage Over Time"
              color="#1890ff"
              unit="%"
            />
          </Col>

          <Col xs={24}>
            <DevicePerformanceChart
              data={metricsData}
              loading={metricsLoading}
              error={metricsError}
              metricType="memory_usage"
              title="Memory Usage Over Time"
              color="#52c41a"
              unit="%"
            />
          </Col>

          <Col xs={24}>
            <DevicePerformanceChart
              data={metricsData}
              loading={metricsLoading}
              error={metricsError}
              metricType="temperature"
              title="Temperature Over Time"
              color="#fa8c16"
              unit="°C"
            />
          </Col>
        </Row>
      ) : (
        <Card>
          <Alert
            message="No Device Selected"
            description="Please select a device from the dropdown above to view historical performance data."
            type="info"
            showIcon
            icon={<InfoCircleOutlined />}
          />
        </Card>
      )}
    </div>
  );
};

export default Historical;

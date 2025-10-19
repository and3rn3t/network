/**
 * Historical Analysis Page
 * Primary value proposition - historical performance trends and analysis
 */

import { MaterialCard } from "@/components/MaterialCard";
import type { TimeRange } from "@/components/TimeRangeSelector";
import { TimeRangeSelector } from "@/components/TimeRangeSelector";
import { DevicePerformanceChart } from "@/components/charts/DevicePerformanceChart";
import { useDeviceMetrics, useDevices } from "@/hooks/useDevices";
import { InfoCircleOutlined, LineChartOutlined } from "@ant-design/icons";
import { Alert, Col, Divider, Row, Select, Space, Typography } from "antd";
import { useState } from "react";

const { Text } = Typography;
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
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-header-title">
          <LineChartOutlined style={{ marginRight: 12 }} />
          Historical Analysis
        </h1>
        <p className="page-header-description">
          Analyze device performance trends over time
        </p>
      </div>

      <Divider style={{ margin: "24px 0" }} />

      {/* Controls */}
      <MaterialCard elevation={1} style={{ marginBottom: 24 }}>
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
              <TimeRangeSelector
                onChange={handleTimeRangeChange}
                showQuickOptions={true}
                defaultHours={24}
              />
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
            style={{ marginTop: 16 }}
          />
        )}
      </MaterialCard>

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
              color="var(--md-sys-color-primary)"
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
              color="var(--md-sys-color-success)"
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
              color="var(--md-sys-color-warning)"
              unit="°C"
            />
          </Col>
        </Row>
      ) : (
        <MaterialCard elevation={1}>
          <Alert
            message="No Device Selected"
            description="Please select a device from the dropdown above to view historical performance data."
            type="info"
            showIcon
            icon={<InfoCircleOutlined />}
          />
        </MaterialCard>
      )}
    </div>
  );
};

export default Historical;

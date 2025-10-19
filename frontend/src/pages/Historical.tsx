/**
 * Historical Analysis Page
 * Primary value proposition - historical performance trends and analysis
 */

import { MaterialCard } from "@/components/MaterialCard";
import type { TimeRange } from "@/components/TimeRangeSelector";
import { TimeRangeSelector } from "@/components/TimeRangeSelector";
import { DevicePerformanceChart } from "@/components/charts/DevicePerformanceChart";
import { useDeviceMetrics, useDevices } from "@/hooks/useDevices";
import type { Device } from "@/types/device";
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
  Typography,
  message,
} from "antd";
import dayjs from "dayjs";
import { useMemo, useState } from "react";

const { Text } = Typography;
const { Option } = Select;

export const Historical = () => {
  const [selectedDeviceId, setSelectedDeviceId] = useState<
    number | undefined
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
  } = useDeviceMetrics(
    selectedDeviceId ? selectedDeviceId.toString() : undefined,
    timeRange.hours
  );

  // Wrap metricsData in useMemo to prevent dependency issues
  const metricsData = useMemo(
    () => metricsResponse?.metrics || [],
    [metricsResponse]
  );

  // Calculate statistics for each metric type
  const statistics = useMemo(() => {
    if (!metricsData || metricsData.length === 0) {
      return null;
    }

    const calculateStats = (metricType: string) => {
      const values = metricsData
        .filter((m) => m.metric_type === metricType)
        .map((m) => m.value);

      if (values.length === 0) return null;

      const avg = values.reduce((a, b) => a + b, 0) / values.length;
      const max = Math.max(...values);
      const min = Math.min(...values);
      const latest = values.at(-1) || 0;

      return { avg, max, min, latest, count: values.length };
    };

    return {
      cpu: calculateStats("cpu_usage"),
      memory: calculateStats("memory_usage"),
      temperature: calculateStats("temperature"),
    };
  }, [metricsData]);

  // Get selected device info
  const selectedDevice = devices.find((d) => d.id === selectedDeviceId);

  // Helper function to get temperature color
  const getTemperatureColor = (temp: number) => {
    if (temp > 70) return "var(--md-sys-color-error)";
    if (temp > 60) return "var(--md-sys-color-warning)";
    return "var(--md-sys-color-success)";
  };

  const handleDeviceChange = (value: number) => {
    setSelectedDeviceId(value);
  };

  const handleTimeRangeChange = (range: TimeRange) => {
    setTimeRange(range);
  };

  // Export data as CSV
  const handleExportCSV = () => {
    if (!metricsData || metricsData.length === 0) {
      message.warning("No data to export");
      return;
    }

    const csvHeaders = "Timestamp,Metric Type,Value\n";
    const csvRows = metricsData
      .map((m) => `${m.timestamp},${m.metric_type},${m.value}`)
      .join("\n");

    const csvContent = csvHeaders + csvRows;
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${
      selectedDevice?.name || "device"
    }_metrics_${dayjs().format("YYYYMMDD_HHmmss")}.csv`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);

    message.success("Data exported successfully");
  };

  // Export data as JSON
  const handleExportJSON = () => {
    if (!metricsData || metricsData.length === 0) {
      message.warning("No data to export");
      return;
    }

    const exportData = {
      device: {
        id: selectedDevice?.id,
        name: selectedDevice?.name,
        model: selectedDevice?.model,
        ip: selectedDevice?.ip,
      },
      timeRange: timeRange.label,
      exportedAt: new Date().toISOString(),
      statistics,
      metrics: metricsData,
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${
      selectedDevice?.name || "device"
    }_metrics_${dayjs().format("YYYYMMDD_HHmmss")}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);

    message.success("Data exported successfully");
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
                {devices.map((device: Device) => (
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
          <>
            <Alert
              message={
                <span>
                  <InfoCircleOutlined /> Showing {timeRange.label.toLowerCase()}{" "}
                  of historical data for <strong>{selectedDevice?.name}</strong>
                </span>
              }
              type="info"
              showIcon={false}
              style={{ marginTop: 16 }}
            />

            <Divider />

            <Row gutter={16} align="middle">
              <Col>
                <Text strong>Export Data:</Text>
              </Col>
              <Col>
                <Space>
                  <Button
                    icon={<DownloadOutlined />}
                    onClick={handleExportCSV}
                    disabled={!metricsData || metricsData.length === 0}
                  >
                    Export CSV
                  </Button>
                  <Button
                    icon={<DownloadOutlined />}
                    onClick={handleExportJSON}
                    disabled={!metricsData || metricsData.length === 0}
                  >
                    Export JSON
                  </Button>
                </Space>
              </Col>
            </Row>
          </>
        )}
      </MaterialCard>

      {/* Statistics Summary */}
      {selectedDeviceId && statistics && (
        <MaterialCard
          title="Performance Summary"
          elevation={1}
          style={{ marginBottom: 24 }}
        >
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} lg={6}>
              <Statistic
                title="Current CPU Usage"
                value={statistics.cpu?.latest.toFixed(1) || 0}
                suffix="%"
                valueStyle={{
                  color:
                    (statistics.cpu?.latest || 0) > 80
                      ? "var(--md-sys-color-error)"
                      : "var(--md-sys-color-success)",
                }}
              />
              <Text
                type="secondary"
                style={{ fontSize: 12, color: "rgba(0, 0, 0, 0.65)" }}
              >
                Avg: {statistics.cpu?.avg.toFixed(1)}% | Max:{" "}
                {statistics.cpu?.max.toFixed(1)}%
              </Text>
            </Col>

            <Col xs={24} sm={12} lg={6}>
              <Statistic
                title="Current Memory Usage"
                value={statistics.memory?.latest.toFixed(1) || 0}
                suffix="%"
                valueStyle={{
                  color:
                    (statistics.memory?.latest || 0) > 80
                      ? "var(--md-sys-color-error)"
                      : "var(--md-sys-color-success)",
                }}
              />
              <Text
                type="secondary"
                style={{ fontSize: 12, color: "rgba(0, 0, 0, 0.65)" }}
              >
                Avg: {statistics.memory?.avg.toFixed(1)}% | Max:{" "}
                {statistics.memory?.max.toFixed(1)}%
              </Text>
            </Col>

            <Col xs={24} sm={12} lg={6}>
              <Statistic
                title="Current Temperature"
                value={statistics.temperature?.latest.toFixed(1) || 0}
                suffix="°C"
                valueStyle={{
                  color: getTemperatureColor(
                    statistics.temperature?.latest || 0
                  ),
                }}
              />
              <Text
                type="secondary"
                style={{ fontSize: 12, color: "rgba(0, 0, 0, 0.65)" }}
              >
                Avg: {statistics.temperature?.avg.toFixed(1)}°C | Max:{" "}
                {statistics.temperature?.max.toFixed(1)}°C
              </Text>
            </Col>

            <Col xs={24} sm={12} lg={6}>
              <Statistic
                title="Data Points"
                value={statistics.cpu?.count || 0}
                valueStyle={{ color: "var(--md-sys-color-primary)" }}
              />
              <Text
                type="secondary"
                style={{ fontSize: 12, color: "rgba(0, 0, 0, 0.65)" }}
              >
                Collected over {timeRange.label.toLowerCase()}
              </Text>
            </Col>
          </Row>
        </MaterialCard>
      )}

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

/**
 * Correlation Analysis Page
 * Analyze relationships between different metrics
 */

import { MaterialCard } from "@/components/MaterialCard";
import { TimeRangeSelector } from "@/components/TimeRangeSelector";
import { CorrelationScatterPlot } from "@/components/charts/CorrelationScatterPlot";
import { useDeviceMetrics, useDevices } from "@/hooks/useDevices";
import type { Device } from "@/types/device";
import {
  DownloadOutlined,
  FundProjectionScreenOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { Button, Col, message, Row, Select, Space, Typography } from "antd";
import dayjs from "dayjs";
import { useState } from "react";

const { Text, Paragraph } = Typography;
const { Option } = Select;

interface TimeRange {
  hours: number;
  label: string;
}

interface MetricConfig {
  key: string;
  label: string;
  unit: string;
}

const AVAILABLE_METRICS: MetricConfig[] = [
  { key: "cpu_usage", label: "CPU Usage", unit: "%" },
  { key: "memory_usage", label: "Memory Usage", unit: "%" },
  { key: "network_rx_mbps", label: "Network RX", unit: "Mbps" },
  { key: "network_tx_mbps", label: "Network TX", unit: "Mbps" },
  { key: "client_count", label: "Client Count", unit: "clients" },
];

export default function Correlation() {
  const [selectedDevice, setSelectedDevice] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<TimeRange>({
    hours: 24,
    label: "Last 24 Hours",
  });
  const [xMetric, setXMetric] = useState<string>("cpu_usage");
  const [yMetric, setYMetric] = useState<string>("memory_usage");

  const { data: devicesData, isLoading: devicesLoading } = useDevices();
  const devices: Device[] = devicesData?.devices || [];

  // Fetch metrics for both X and Y axis
  const metricsQuery = useDeviceMetrics(
    selectedDevice ? Number.parseInt(selectedDevice) : undefined,
    timeRange.hours
  );

  // Filter metrics by type
  const xAxisData =
    metricsQuery.data?.metrics
      .filter((m) => m.metric_type === xMetric)
      .map((m) => ({ timestamp: m.timestamp, value: m.value })) || [];

  const yAxisData =
    metricsQuery.data?.metrics
      .filter((m) => m.metric_type === yMetric)
      .map((m) => ({ timestamp: m.timestamp, value: m.value })) || [];

  const handleDeviceChange = (deviceId: string) => {
    setSelectedDevice(deviceId);
  };

  const handleTimeRangeChange = (range: TimeRange) => {
    setTimeRange(range);
  };

  const handleExportCorrelation = () => {
    if (!selectedDevice) {
      message.warning("Please select a device first");
      return;
    }

    const device = devices.find((d) => d.id.toString() === selectedDevice);
    const exportData = {
      timestamp: new Date().toISOString(),
      device: {
        id: selectedDevice,
        name: device?.name || device?.ip,
      },
      timeRange: timeRange.label,
      xMetric: AVAILABLE_METRICS.find((m) => m.key === xMetric),
      yMetric: AVAILABLE_METRICS.find((m) => m.key === yMetric),
      xData: xAxisData,
      yData: yAxisData,
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `correlation_${
      device?.name || selectedDevice
    }_${xMetric}_${yMetric}_${dayjs().format("YYYYMMDD_HHmmss")}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);

    message.success("Correlation data exported successfully");
  };

  const handleRefresh = () => {
    metricsQuery.refetch();
    message.success("Data refreshed");
  };

  const getMetricConfig = (metricKey: string): MetricConfig => {
    return (
      AVAILABLE_METRICS.find((m) => m.key === metricKey) || AVAILABLE_METRICS[0]
    );
  };

  const selectedDeviceData = devices.find(
    (d) => d.id.toString() === selectedDevice
  );

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-header-title">
          <FundProjectionScreenOutlined style={{ marginRight: 12 }} />
          Correlation Analysis
        </h1>
        <p className="page-header-description">
          Analyze relationships between different metrics to discover patterns
          and dependencies. A strong correlation indicates that two metrics tend
          to change together.
        </p>
      </div>

      {/* Controls */}
      <MaterialCard elevation={1} style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: "100%" }} size="large">
          {/* Device Selection */}
          <Row gutter={16} align="middle">
            <Col span={4}>
              <Text strong>Select Device:</Text>
            </Col>
            <Col span={20}>
              <Select
                style={{ width: "100%" }}
                placeholder="Choose a device to analyze"
                onChange={handleDeviceChange}
                value={selectedDevice}
                loading={devicesLoading}
                disabled={devicesLoading}
              >
                {devices.map((device: Device) => (
                  <Option key={device.id} value={device.id.toString()}>
                    {device.name || device.ip} - {device.type}
                  </Option>
                ))}
              </Select>
            </Col>
          </Row>

          {/* Time Range */}
          <Row gutter={16} align="middle">
            <Col span={4}>
              <Text strong>Time Range:</Text>
            </Col>
            <Col span={20}>
              <TimeRangeSelector
                onChange={handleTimeRangeChange}
                defaultHours={24}
                showQuickOptions={true}
              />
            </Col>
          </Row>

          {/* Metric Selection */}
          <Row gutter={16}>
            <Col span={12}>
              <Space direction="vertical" style={{ width: "100%" }}>
                <Text strong>X-Axis Metric:</Text>
                <Select
                  style={{ width: "100%" }}
                  value={xMetric}
                  onChange={setXMetric}
                  disabled={!selectedDevice}
                >
                  {AVAILABLE_METRICS.map((metric) => (
                    <Option
                      key={metric.key}
                      value={metric.key}
                      disabled={metric.key === yMetric}
                    >
                      {metric.label} ({metric.unit})
                    </Option>
                  ))}
                </Select>
              </Space>
            </Col>
            <Col span={12}>
              <Space direction="vertical" style={{ width: "100%" }}>
                <Text strong>Y-Axis Metric:</Text>
                <Select
                  style={{ width: "100%" }}
                  value={yMetric}
                  onChange={setYMetric}
                  disabled={!selectedDevice}
                >
                  {AVAILABLE_METRICS.map((metric) => (
                    <Option
                      key={metric.key}
                      value={metric.key}
                      disabled={metric.key === xMetric}
                    >
                      {metric.label} ({metric.unit})
                    </Option>
                  ))}
                </Select>
              </Space>
            </Col>
          </Row>

          {/* Actions */}
          <Row gutter={16}>
            <Col>
              <Button
                type="primary"
                icon={<DownloadOutlined />}
                onClick={handleExportCorrelation}
                disabled={!selectedDevice}
              >
                Export Data
              </Button>
            </Col>
            <Col>
              <Button
                icon={<ReloadOutlined />}
                onClick={handleRefresh}
                disabled={!selectedDevice}
              >
                Refresh
              </Button>
            </Col>
          </Row>
        </Space>
      </MaterialCard>

      {/* Correlation Plot */}
      {selectedDevice ? (
        <CorrelationScatterPlot
          xAxisData={xAxisData}
          yAxisData={yAxisData}
          xAxisLabel={getMetricConfig(xMetric).label}
          yAxisLabel={getMetricConfig(yMetric).label}
          xAxisUnit={getMetricConfig(xMetric).unit}
          yAxisUnit={getMetricConfig(yMetric).unit}
          deviceName={
            selectedDeviceData?.name || selectedDeviceData?.ip || "Unknown"
          }
          loading={metricsQuery.isLoading}
          error={metricsQuery.error}
        />
      ) : (
        <MaterialCard elevation={1}>
          <div style={{ textAlign: "center", padding: "60px 20px" }}>
            <Text style={{ fontSize: 16, color: "rgba(0, 0, 0, 0.65)" }}>
              Select a device and time range to begin correlation analysis
            </Text>
          </div>
        </MaterialCard>
      )}

      {/* Information Card */}
      <MaterialCard
        title="Understanding Correlation"
        elevation={1}
        style={{ marginTop: 24 }}
      >
        <Space direction="vertical" size="middle">
          <div>
            <Text strong>Correlation Coefficient (r):</Text>
            <Paragraph style={{ marginTop: 8, marginLeft: 16 }}>
              • <strong>+0.9 to +1.0:</strong> Very strong positive correlation
              <br />• <strong>+0.7 to +0.9:</strong> Strong positive correlation
              <br />• <strong>+0.5 to +0.7:</strong> Moderate positive
              correlation
              <br />• <strong>+0.3 to +0.5:</strong> Weak positive correlation
              <br />• <strong>-0.3 to +0.3:</strong> Very weak or no correlation
              <br />• <strong>-0.5 to -0.3:</strong> Weak negative correlation
              <br />• <strong>-0.7 to -0.5:</strong> Moderate negative
              correlation
              <br />• <strong>-0.9 to -0.7:</strong> Strong negative correlation
              <br />• <strong>-1.0 to -0.9:</strong> Very strong negative
              correlation
            </Paragraph>
          </div>
          <div>
            <Text strong>R² Value (Coefficient of Determination):</Text>
            <Paragraph style={{ marginTop: 8, marginLeft: 16 }}>
              Indicates the percentage of variance in one metric that can be
              predicted from the other metric. For example, an R² of 0.80 (80%)
              means that 80% of the variation in the Y-axis metric can be
              explained by the X-axis metric.
            </Paragraph>
          </div>
          <div>
            <Text strong>Use Cases:</Text>
            <Paragraph style={{ marginTop: 8, marginLeft: 16 }}>
              • <strong>CPU vs Memory:</strong> Identify if high CPU usage
              corresponds to high memory usage
              <br />• <strong>Network Traffic vs Client Count:</strong> See if
              more clients result in higher bandwidth usage
              <br />• <strong>CPU vs Network:</strong> Determine if processing
              load affects network performance
              <br />• <strong>Memory vs Client Count:</strong> Understand memory
              consumption patterns with user load
            </Paragraph>
          </div>
        </Space>
      </MaterialCard>
    </div>
  );
}

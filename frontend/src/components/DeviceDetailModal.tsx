/**
 * Device Detail Modal - Comprehensive device information viewer
 * Shows configuration, statistics, ports, network info, events, and metrics
 */

import {
  ApiOutlined,
  CloudDownloadOutlined,
  DashboardOutlined,
  EnvironmentOutlined,
  HistoryOutlined,
  LineChartOutlined,
  ReloadOutlined,
  SettingOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import {
  Badge,
  Button,
  Card,
  Col,
  Descriptions,
  Divider,
  Empty,
  message,
  Modal,
  Progress,
  Row,
  Space,
  Statistic,
  Table,
  Tabs,
  Tag,
  Timeline,
  Tooltip,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import axios from "axios";
import React, { useEffect, useState } from "react";

interface Device {
  id: string;
  name: string;
  mac: string;
  model: string;
  type: string;
  ip: string;
  firmware_version: string;
  uptime: number;
  status: "online" | "offline";
}

interface DeviceStats {
  cpu_usage: number;
  memory_usage: number;
  temperature: number;
  uptime: number;
  bytes_sent: number;
  bytes_received: number;
}

interface PortInfo {
  port_idx: number;
  name: string;
  enabled: boolean;
  up: boolean;
  speed: number;
  full_duplex: boolean;
  poe_enable: boolean;
  poe_power: number;
  rx_bytes: number;
  tx_bytes: number;
}

interface NetworkInfo {
  ip: string;
  netmask: string;
  gateway: string;
  dns: string[];
  vlan: number;
  adopt_ip: string;
}

interface DeviceEvent {
  timestamp: string;
  type: string;
  message: string;
  severity: "info" | "warning" | "error";
}

interface DeviceDetailModalProps {
  visible: boolean;
  device: Device | null;
  onClose: () => void;
  onRefresh?: () => void;
}

export const DeviceDetailModal: React.FC<DeviceDetailModalProps> = ({
  visible,
  device,
  onClose,
  onRefresh,
}) => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [stats, setStats] = useState<DeviceStats | null>(null);
  const [ports, setPorts] = useState<PortInfo[]>([]);
  const [networkInfo, setNetworkInfo] = useState<NetworkInfo | null>(null);
  const [events, setEvents] = useState<DeviceEvent[]>([]);
  const [config, setConfig] = useState<any>(null);

  // Load device details when modal opens
  useEffect(() => {
    if (visible && device) {
      loadDeviceDetails();
    }
  }, [visible, device]);

  const loadDeviceDetails = async () => {
    if (!device) return;

    setLoading(true);
    try {
      // Load device info from API
      const response = await axios.get(`/api/devices/${device.id}/info`);
      const data = response.data;

      // Set stats
      setStats({
        cpu_usage: data.stats?.cpu_usage || 0,
        memory_usage: data.stats?.memory_usage || 0,
        temperature: data.stats?.temperature || 0,
        uptime: data.uptime || 0,
        bytes_sent: data.stats?.bytes_sent || 0,
        bytes_received: data.stats?.bytes_received || 0,
      });

      // Set ports (if switch)
      if (data.ports) {
        setPorts(data.ports);
      }

      // Set network info
      setNetworkInfo({
        ip: data.ip || device.ip,
        netmask: data.netmask || "255.255.255.0",
        gateway: data.gateway || "192.168.1.1",
        dns: data.dns || ["8.8.8.8", "8.8.4.4"],
        vlan: data.vlan || 1,
        adopt_ip: data.adopt_ip || "",
      });

      // Set events
      setEvents(data.events || []);

      // Set config
      setConfig(data.config || {});
    } catch (error) {
      console.error("Failed to load device details:", error);

      // Set sample data for development
      setStats({
        cpu_usage: 45,
        memory_usage: 62,
        temperature: 58,
        uptime: device.uptime,
        bytes_sent: 1024 * 1024 * 1024 * 50,
        bytes_received: 1024 * 1024 * 1024 * 120,
      });

      if (device.type === "switch") {
        setPorts([
          {
            port_idx: 1,
            name: "Port 1",
            enabled: true,
            up: true,
            speed: 1000,
            full_duplex: true,
            poe_enable: true,
            poe_power: 15.2,
            rx_bytes: 1024 * 1024 * 1024 * 5,
            tx_bytes: 1024 * 1024 * 1024 * 3,
          },
          {
            port_idx: 2,
            name: "Port 2",
            enabled: true,
            up: true,
            speed: 1000,
            full_duplex: true,
            poe_enable: true,
            poe_power: 8.4,
            rx_bytes: 1024 * 1024 * 1024 * 2,
            tx_bytes: 1024 * 1024 * 1024 * 1,
          },
          {
            port_idx: 3,
            name: "Port 3",
            enabled: true,
            up: false,
            speed: 0,
            full_duplex: false,
            poe_enable: false,
            poe_power: 0,
            rx_bytes: 0,
            tx_bytes: 0,
          },
        ]);
      }

      setNetworkInfo({
        ip: device.ip,
        netmask: "255.255.255.0",
        gateway: "192.168.1.1",
        dns: ["8.8.8.8", "8.8.4.4"],
        vlan: 1,
        adopt_ip: "192.168.1.10",
      });

      setEvents([
        {
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          type: "device_online",
          message: "Device came online",
          severity: "info",
        },
        {
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          type: "firmware_update",
          message: "Firmware updated to " + device.firmware_version,
          severity: "info",
        },
        {
          timestamp: new Date(Date.now() - 86400000).toISOString(),
          type: "device_restart",
          message: "Device restarted",
          severity: "warning",
        },
      ]);

      setConfig({
        name: device.name,
        model: device.model,
        mac: device.mac,
        ip: device.ip,
        firmware_version: device.firmware_version,
        settings: {
          led_enabled: true,
          locate_enabled: false,
          ssh_enabled: true,
          snmp_enabled: false,
        },
      });
    } finally {
      setLoading(false);
    }
  };

  const handleReboot = async () => {
    if (!device) return;

    Modal.confirm({
      title: "Reboot Device",
      content: `Are you sure you want to reboot ${device.name}? This will cause a brief service interruption.`,
      okText: "Reboot",
      okType: "danger",
      onOk: async () => {
        try {
          await axios.post(`/api/devices/${device.id}/reboot`, {
            reason: "Manual reboot from device details",
          });
          message.success("Device reboot initiated");
          onRefresh?.();
        } catch (error) {
          message.error("Failed to reboot device");
        }
      },
    });
  };

  const handleRestart = async () => {
    if (!device) return;

    try {
      await axios.post(`/api/devices/${device.id}/restart`);
      message.success("Device restart initiated");
      onRefresh?.();
    } catch (error) {
      message.error("Failed to restart device");
    }
  };

  const handleLocate = async () => {
    if (!device) return;

    try {
      await axios.post(`/api/devices/${device.id}/locate`, {
        duration: 30,
      });
      message.success("Device LED blinking for 30 seconds");
    } catch (error) {
      message.error("Failed to locate device");
    }
  };

  const handleDownloadConfig = () => {
    if (!config) return;

    const dataStr = JSON.stringify(config, null, 2);
    const dataUri =
      "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);
    const exportFileDefaultName = `${device?.name || "device"}_config.json`;

    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.click();
    message.success("Configuration downloaded");
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB", "TB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  };

  const formatUptime = (seconds: number): string => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  const getEventColor = (severity: string): string => {
    switch (severity) {
      case "error":
        return "red";
      case "warning":
        return "orange";
      default:
        return "blue";
    }
  };

  const portColumns: ColumnsType<PortInfo> = [
    {
      title: "Port",
      dataIndex: "port_idx",
      key: "port_idx",
      render: (idx: number, record: PortInfo) => (
        <Space>
          <Badge
            status={record.up ? "success" : "default"}
            text={record.name || `Port ${idx}`}
          />
        </Space>
      ),
    },
    {
      title: "Status",
      dataIndex: "up",
      key: "status",
      render: (up: boolean, record: PortInfo) =>
        !record.enabled ? (
          <Tag color="default">Disabled</Tag>
        ) : up ? (
          <Tag color="success">Up</Tag>
        ) : (
          <Tag color="error">Down</Tag>
        ),
    },
    {
      title: "Speed",
      dataIndex: "speed",
      key: "speed",
      render: (speed: number, record: PortInfo) =>
        record.up ? `${speed} Mbps` : "—",
    },
    {
      title: "Duplex",
      dataIndex: "full_duplex",
      key: "duplex",
      render: (full: boolean, record: PortInfo) =>
        record.up ? (full ? "Full" : "Half") : "—",
    },
    {
      title: "PoE",
      dataIndex: "poe_enable",
      key: "poe",
      render: (enabled: boolean, record: PortInfo) =>
        enabled ? (
          <Tooltip title={`${record.poe_power.toFixed(1)}W`}>
            <Tag color="blue">Enabled</Tag>
          </Tooltip>
        ) : (
          <Tag>Disabled</Tag>
        ),
    },
    {
      title: "RX",
      dataIndex: "rx_bytes",
      key: "rx",
      render: (bytes: number) => formatBytes(bytes),
    },
    {
      title: "TX",
      dataIndex: "tx_bytes",
      key: "tx",
      render: (bytes: number) => formatBytes(bytes),
    },
  ];

  const overviewTab = (
    <div>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="CPU Usage"
              value={stats?.cpu_usage || 0}
              suffix="%"
              valueStyle={{
                color:
                  (stats?.cpu_usage || 0) > 80
                    ? "var(--md-sys-color-error)"
                    : undefined,
              }}
              prefix={<DashboardOutlined />}
            />
            <Progress percent={stats?.cpu_usage || 0} showInfo={false} />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Memory Usage"
              value={stats?.memory_usage || 0}
              suffix="%"
              valueStyle={{
                color:
                  (stats?.memory_usage || 0) > 90
                    ? "var(--md-sys-color-error)"
                    : undefined,
              }}
              prefix={<DashboardOutlined />}
            />
            <Progress percent={stats?.memory_usage || 0} showInfo={false} />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Temperature"
              value={stats?.temperature || 0}
              suffix="°C"
              valueStyle={{
                color:
                  (stats?.temperature || 0) > 70
                    ? "var(--md-sys-color-error)"
                    : undefined,
              }}
              prefix={<ThunderboltOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Uptime"
              value={formatUptime(stats?.uptime || 0)}
              prefix={<HistoryOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Divider />

      <Descriptions title="Device Information" bordered column={2}>
        <Descriptions.Item label="Name">{device?.name}</Descriptions.Item>
        <Descriptions.Item label="Model">{device?.model}</Descriptions.Item>
        <Descriptions.Item label="Type">
          <Tag color="blue">{device?.type}</Tag>
        </Descriptions.Item>
        <Descriptions.Item label="Status">
          <Badge
            status={device?.status === "online" ? "success" : "error"}
            text={device?.status}
          />
        </Descriptions.Item>
        <Descriptions.Item label="MAC Address">
          <code>{device?.mac}</code>
        </Descriptions.Item>
        <Descriptions.Item label="IP Address">{device?.ip}</Descriptions.Item>
        <Descriptions.Item label="Firmware">
          {device?.firmware_version}
        </Descriptions.Item>
        <Descriptions.Item label="Uptime">
          {formatUptime(device?.uptime || 0)}
        </Descriptions.Item>
      </Descriptions>

      <Divider />

      <Row gutter={[16, 16]}>
        <Col xs={24} md={12}>
          <Card title="Network Traffic" size="small">
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Bytes Sent">
                {formatBytes(stats?.bytes_sent || 0)}
              </Descriptions.Item>
              <Descriptions.Item label="Bytes Received">
                {formatBytes(stats?.bytes_received || 0)}
              </Descriptions.Item>
              <Descriptions.Item label="Total">
                {formatBytes(
                  (stats?.bytes_sent || 0) + (stats?.bytes_received || 0)
                )}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="Quick Actions" size="small">
            <Space direction="vertical" style={{ width: "100%" }}>
              <Button
                icon={<ReloadOutlined />}
                onClick={handleReboot}
                danger
                block
              >
                Reboot Device
              </Button>
              <Button
                icon={<ThunderboltOutlined />}
                onClick={handleRestart}
                block
              >
                Restart Services
              </Button>
              <Button
                icon={<EnvironmentOutlined />}
                onClick={handleLocate}
                block
              >
                Locate (Blink LED)
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );

  const portsTab =
    ports.length > 0 ? (
      <Table
        columns={portColumns}
        dataSource={ports}
        rowKey="port_idx"
        pagination={false}
        size="small"
      />
    ) : (
      <Empty description="No port information available for this device type" />
    );

  const networkTab = networkInfo ? (
    <Descriptions title="Network Configuration" bordered column={1}>
      <Descriptions.Item label="IP Address">{networkInfo.ip}</Descriptions.Item>
      <Descriptions.Item label="Netmask">
        {networkInfo.netmask}
      </Descriptions.Item>
      <Descriptions.Item label="Gateway">
        {networkInfo.gateway}
      </Descriptions.Item>
      <Descriptions.Item label="DNS Servers">
        {networkInfo.dns.join(", ")}
      </Descriptions.Item>
      <Descriptions.Item label="VLAN">{networkInfo.vlan}</Descriptions.Item>
      <Descriptions.Item label="Adopt IP">
        {networkInfo.adopt_ip || "—"}
      </Descriptions.Item>
    </Descriptions>
  ) : (
    <Empty description="No network information available" />
  );

  const eventsTab =
    events.length > 0 ? (
      <Timeline
        items={events.map((event) => ({
          color: getEventColor(event.severity),
          children: (
            <div>
              <div>
                <Tag color={getEventColor(event.severity)}>
                  {event.severity}
                </Tag>
                <Tag>{event.type}</Tag>
                <span
                  style={{
                    marginLeft: 8,
                    color: "var(--md-sys-color-outline)",
                  }}
                >
                  {new Date(event.timestamp).toLocaleString()}
                </span>
              </div>
              <div style={{ marginTop: 8 }}>{event.message}</div>
            </div>
          ),
        }))}
      />
    ) : (
      <Empty description="No recent events" />
    );

  const configTab = config ? (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<CloudDownloadOutlined />} onClick={handleDownloadConfig}>
          Download Configuration
        </Button>
      </Space>
      <pre
        style={{
          background: "var(--md-sys-color-surface-variant)",
          padding: 16,
          borderRadius: 8,
          overflow: "auto",
          maxHeight: 400,
        }}
      >
        {JSON.stringify(config, null, 2)}
      </pre>
    </div>
  ) : (
    <Empty description="No configuration available" />
  );

  const metricsTab = (
    <Empty
      description="Metrics visualization coming soon"
      image={Empty.PRESENTED_IMAGE_SIMPLE}
    >
      <p style={{ color: "var(--md-sys-color-outline)" }}>
        This tab will show historical metrics graphs for CPU, memory,
        temperature, and network traffic.
      </p>
    </Empty>
  );

  const tabItems = [
    {
      key: "overview",
      label: (
        <span>
          <DashboardOutlined /> Overview
        </span>
      ),
      children: overviewTab,
    },
    {
      key: "ports",
      label: (
        <span>
          <ApiOutlined /> Ports
        </span>
      ),
      children: portsTab,
    },
    {
      key: "network",
      label: (
        <span>
          <SettingOutlined /> Network
        </span>
      ),
      children: networkTab,
    },
    {
      key: "events",
      label: (
        <span>
          <HistoryOutlined /> Events
        </span>
      ),
      children: eventsTab,
    },
    {
      key: "config",
      label: (
        <span>
          <SettingOutlined /> Configuration
        </span>
      ),
      children: configTab,
    },
    {
      key: "metrics",
      label: (
        <span>
          <LineChartOutlined /> Metrics
        </span>
      ),
      children: metricsTab,
    },
  ];

  return (
    <Modal
      title={
        <Space>
          <span>{device?.name || "Device Details"}</span>
          <Badge
            status={device?.status === "online" ? "success" : "error"}
            text={device?.status}
          />
        </Space>
      }
      open={visible}
      onCancel={onClose}
      footer={null}
      width={1000}
      style={{ top: 20 }}
    >
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={tabItems}
        tabBarStyle={{ marginBottom: 16 }}
      />
    </Modal>
  );
};

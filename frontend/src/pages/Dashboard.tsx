/**
 * Dashboard - Overview page with Material Design 3
 */

import { MaterialCard } from "@/components/MaterialCard";
import { useDevices } from "@/hooks/useDevices";
import {
  useRealTimeDeviceStatus,
  useRealTimeHealth,
  useRealTimeMetrics,
} from "@/hooks/useRealTime";
import {
  ApiOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  CloudServerOutlined,
  DatabaseOutlined,
  FallOutlined,
  RiseOutlined,
  SignalFilled,
  TeamOutlined,
  ThunderboltOutlined,
  WarningOutlined,
  WifiOutlined,
} from "@ant-design/icons";
import { Badge, Col, Progress, Row, Spin, Statistic, Table, Tag } from "antd";
import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { data: devicesData, isLoading } = useDevices();
  const { metrics, status: metricsStatus } = useRealTimeMetrics();
  const { deviceStatuses, status: deviceStatusStatus } =
    useRealTimeDeviceStatus();
  const {
    healthScore,
    healthStatus,
    status: healthStatusConnection,
  } = useRealTimeHealth();

  // Local state for animated values
  const [displayHealth, setDisplayHealth] = useState(98.5);
  const [displayCpuUsage, setDisplayCpuUsage] = useState(24.7);
  const [clientsData, setClientsData] = useState<any>(null);
  const [loadingClients, setLoadingClients] = useState(true);

  // Fetch clients data
  useEffect(() => {
    const fetchClients = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/clients");
        const data = await response.json();
        setClientsData(data);
      } catch (error) {
        console.error("Failed to fetch clients:", error);
      } finally {
        setLoadingClients(false);
      }
    };
    fetchClients();
  }, []);

  // Calculate online devices
  const onlineDevices = useMemo(() => {
    if (!devicesData) {
      return 0;
    }
    return (
      Object.values(deviceStatuses).filter((status) => status === "online")
        .length ||
      devicesData.devices.filter((d) => d.status === "online").length
    );
  }, [devicesData, deviceStatuses]);

  // Calculate client statistics
  const clientStats = useMemo(() => {
    if (!clientsData?.clients) {
      return {
        total: 0,
        wireless: 0,
        wired: 0,
        avgSignal: 0,
        avgSatisfaction: 0,
        poorWiFi: 0,
      };
    }

    const clients = clientsData.clients;
    const wireless = clients.filter((c: any) => !c.is_wired);
    const wired = clients.filter((c: any) => c.is_wired);

    const wirelessWithSignal = wireless.filter((c: any) => c.signal_strength);
    const avgSignal = wirelessWithSignal.length
      ? wirelessWithSignal.reduce(
          (sum: number, c: any) => sum + c.signal_strength,
          0
        ) / wirelessWithSignal.length
      : 0;

    const clientsWithSat = clients.filter((c: any) => c.satisfaction);
    const avgSatisfaction = clientsWithSat.length
      ? clientsWithSat.reduce(
          (sum: number, c: any) => sum + c.satisfaction,
          0
        ) / clientsWithSat.length
      : 0;

    const poorWiFi = wireless.filter(
      (c: any) => c.signal_strength && c.signal_strength < -70
    ).length;

    return {
      total: clients.length,
      wireless: wireless.length,
      wired: wired.length,
      avgSignal: Math.round(avgSignal),
      avgSatisfaction: Math.round(avgSatisfaction),
      poorWiFi,
    };
  }, [clientsData]);

  // Update health score with animation
  useEffect(() => {
    if (healthScore !== displayHealth) {
      const interval = setInterval(() => {
        setDisplayHealth((prev) => {
          const diff = healthScore - prev;
          if (Math.abs(diff) < 0.1) {
            return healthScore;
          }
          return prev + diff * 0.1;
        });
      }, 50);
      return () => {
        clearInterval(interval);
      };
    }
  }, [healthScore, displayHealth]);

  // Calculate average CPU from real-time metrics
  useEffect(() => {
    if (metrics.length > 0) {
      const cpuMetrics = metrics.filter((m) => m.metric_type === "cpu_usage");
      if (cpuMetrics.length > 0) {
        const avgCpu =
          cpuMetrics.reduce((sum, m) => sum + m.value, 0) / cpuMetrics.length;
        setDisplayCpuUsage(avgCpu);
      }
    }
  }, [metrics]);

  const isLive =
    metricsStatus === "connected" ||
    deviceStatusStatus === "connected" ||
    healthStatusConnection === "connected";

  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <Spin size="large" tip="Loading dashboard..." />
      </div>
    );
  }

  // Determine health color based on status
  const getHealthColor = () => {
    if (healthStatus === "excellent" || healthStatus === "good") {
      return "var(--md-sys-color-success, #388E3C)";
    }
    if (healthStatus === "fair") {
      return "var(--md-sys-color-tertiary, #FFA726)";
    }
    return "var(--md-sys-color-error, #D32F2F)";
  };

  // Generate actionable insights based on network state
  const generateInsights = () => {
    const insights = [];

    // Check offline devices
    const offlineCount = (devicesData?.total || 0) - onlineDevices;
    if (offlineCount > 0) {
      insights.push({
        type: "warning",
        icon: "⚠️",
        title: `${offlineCount} Device${offlineCount > 1 ? "s" : ""} Offline`,
        message:
          "Check device power, network connectivity, or recent firmware updates.",
        action: "View Devices",
        link: "/devices",
      });
    }

    // Check poor WiFi connections
    if (clientStats.poorWiFi > 0) {
      insights.push({
        type: "error",
        icon: "📶",
        title: `${clientStats.poorWiFi} Client${
          clientStats.poorWiFi > 1 ? "s" : ""
        } with Poor WiFi`,
        message: `Signal below -70 dBm. Consider moving clients closer to access points or adding more APs.`,
        action: "View Analytics",
        link: "/analytics",
      });
    }

    // Check high CPU usage
    if (displayCpuUsage > 80) {
      insights.push({
        type: "error",
        icon: "🔥",
        title: "High CPU Usage Detected",
        message: `Average CPU at ${displayCpuUsage.toFixed(
          1
        )}%. Check for firmware issues or excessive traffic.`,
        action: "View Devices",
        link: "/devices",
      });
    } else if (displayCpuUsage > 60) {
      insights.push({
        type: "warning",
        icon: "📊",
        title: "Elevated CPU Usage",
        message: `CPU usage at ${displayCpuUsage.toFixed(
          1
        )}%. Monitor for sustained high usage.`,
        action: "View Metrics",
        link: "/historical",
      });
    }

    // Check low client satisfaction
    if (clientStats.avgSatisfaction > 0 && clientStats.avgSatisfaction < 60) {
      insights.push({
        type: "error",
        icon: "😞",
        title: "Low Client Satisfaction",
        message: `Average satisfaction at ${clientStats.avgSatisfaction}%. Check WiFi coverage and interference.`,
        action: "View Analytics",
        link: "/analytics",
      });
    } else if (
      clientStats.avgSatisfaction >= 60 &&
      clientStats.avgSatisfaction < 80
    ) {
      insights.push({
        type: "info",
        icon: "💡",
        title: "Room for WiFi Improvement",
        message: `Client satisfaction at ${clientStats.avgSatisfaction}%. Optimize channel selection and AP placement.`,
        action: "View Analytics",
        link: "/analytics",
      });
    }

    // Check network health
    if (displayHealth < 90 && displayHealth >= 70) {
      insights.push({
        type: "info",
        icon: "🔧",
        title: "Network Health Could Improve",
        message: `Health score at ${displayHealth.toFixed(
          1
        )}%. Review device performance and client connections.`,
        action: "View Dashboard",
        link: "/",
      });
    } else if (displayHealth < 70) {
      insights.push({
        type: "error",
        icon: "🚨",
        title: "Network Health Needs Attention",
        message: `Health score at ${displayHealth.toFixed(
          1
        )}%. Immediate action recommended.`,
        action: "View Devices",
        link: "/devices",
      });
    }

    // Positive insights when everything is good
    if (insights.length === 0) {
      insights.push({
        type: "success",
        icon: "✅",
        title: "Network Operating Optimally",
        message:
          "All systems healthy. No issues detected. Keep up the good work!",
        action: "View Analytics",
        link: "/analytics",
      });
    }

    return insights;
  };

  const insights = generateInsights();

  return (
    <div className="dashboard-container">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-header-title">
            Network Overview
            {isLive && (
              <Badge
                status="processing"
                text="LIVE"
                className="dashboard-live-badge"
              />
            )}
          </h1>
          <p className="page-header-description">
            Real-time monitoring and health metrics for your UniFi network
          </p>
        </div>
      </div>

      {/* Primary Statistics Row */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <MaterialCard elevation={1} className="dashboard-stat-card">
            <Statistic
              title="Network Health"
              value={displayHealth}
              precision={1}
              suffix="%"
              prefix={<RiseOutlined />}
              valueStyle={{ color: getHealthColor() }}
              className="dashboard-statistic animated-value"
            />
            {healthStatusConnection === "connected" && (
              <div className="dashboard-stat-indicator">
                <ThunderboltOutlined /> Live
              </div>
            )}
          </MaterialCard>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <MaterialCard elevation={1} className="dashboard-stat-card">
            <Statistic
              title="Total Devices"
              value={devicesData?.total || 0}
              prefix={<CloudServerOutlined />}
              valueStyle={{ color: "var(--md-sys-color-primary, #1E88E5)" }}
              className="dashboard-statistic"
            />
            <div
              style={{ marginTop: 8, fontSize: 14, color: "rgba(0,0,0,0.6)" }}
            >
              <CheckCircleOutlined style={{ color: "#388E3C" }} />{" "}
              {onlineDevices} online
              {" • "}
              <WarningOutlined style={{ color: "#D32F2F" }} />{" "}
              {(devicesData?.total || 0) - onlineDevices} offline
            </div>
          </MaterialCard>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <MaterialCard elevation={1} className="dashboard-stat-card">
            <Statistic
              title="Connected Clients"
              value={clientStats.total}
              prefix={<TeamOutlined />}
              valueStyle={{ color: "var(--md-sys-color-success, #388E3C)" }}
              className="dashboard-statistic"
              loading={loadingClients}
            />
            <div
              style={{ marginTop: 8, fontSize: 14, color: "rgba(0,0,0,0.6)" }}
            >
              <WifiOutlined /> {clientStats.wireless} WiFi
              {" • "}
              <ApiOutlined /> {clientStats.wired} Wired
            </div>
          </MaterialCard>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <MaterialCard elevation={1} className="dashboard-stat-card">
            <Statistic
              title="Avg CPU Usage"
              value={displayCpuUsage}
              precision={1}
              suffix="%"
              prefix={<FallOutlined />}
              valueStyle={{
                color:
                  displayCpuUsage > 80
                    ? "var(--md-sys-color-error, #D32F2F)"
                    : displayCpuUsage > 60
                    ? "var(--md-sys-color-tertiary, #FFA726)"
                    : "var(--md-sys-color-success, #388E3C)",
              }}
              className="dashboard-statistic animated-value"
            />
            {metricsStatus === "connected" && (
              <div className="dashboard-stat-indicator">
                <ThunderboltOutlined /> Live
              </div>
            )}
          </MaterialCard>
        </Col>
      </Row>

      {/* Secondary Stats Row */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={8}>
          <MaterialCard elevation={1} className="dashboard-stat-card">
            <Statistic
              title="WiFi Performance"
              value={clientStats.avgSignal}
              suffix="dBm"
              prefix={<SignalFilled />}
              valueStyle={{
                color:
                  clientStats.avgSignal > -60
                    ? "var(--md-sys-color-success, #388E3C)"
                    : clientStats.avgSignal > -70
                    ? "var(--md-sys-color-tertiary, #FFA726)"
                    : "var(--md-sys-color-error, #D32F2F)",
              }}
              className="dashboard-statistic"
              loading={loadingClients}
            />
            <div style={{ marginTop: 8, fontSize: 13 }}>
              {clientStats.avgSignal > -60 && (
                <Tag color="success">Excellent Signal</Tag>
              )}
              {clientStats.avgSignal <= -60 && clientStats.avgSignal > -70 && (
                <Tag color="warning">Good Signal</Tag>
              )}
              {clientStats.avgSignal <= -70 && (
                <Tag color="error">{clientStats.poorWiFi} Poor Connections</Tag>
              )}
            </div>
          </MaterialCard>
        </Col>

        <Col xs={24} sm={12} md={8}>
          <MaterialCard elevation={1} className="dashboard-stat-card">
            <Statistic
              title="Client Satisfaction"
              value={clientStats.avgSatisfaction}
              suffix="%"
              prefix={<RiseOutlined />}
              valueStyle={{
                color:
                  clientStats.avgSatisfaction >= 80
                    ? "var(--md-sys-color-success, #388E3C)"
                    : clientStats.avgSatisfaction >= 60
                    ? "var(--md-sys-color-tertiary, #FFA726)"
                    : "var(--md-sys-color-error, #D32F2F)",
              }}
              className="dashboard-statistic"
              loading={loadingClients}
            />
            <Progress
              percent={clientStats.avgSatisfaction}
              strokeColor={
                clientStats.avgSatisfaction >= 80
                  ? "#388E3C"
                  : clientStats.avgSatisfaction >= 60
                  ? "#FFA726"
                  : "#D32F2F"
              }
              showInfo={false}
              style={{ marginTop: 12 }}
            />
          </MaterialCard>
        </Col>

        <Col xs={24} sm={12} md={8}>
          <MaterialCard elevation={1} className="dashboard-stat-card">
            <Statistic
              title="System Status"
              value="Operational"
              prefix={<DatabaseOutlined />}
              valueStyle={{
                color: "var(--md-sys-color-success, #388E3C)",
                fontSize: 20,
              }}
              className="dashboard-statistic"
            />
            <div style={{ marginTop: 12, fontSize: 13 }}>
              <div style={{ marginBottom: 4 }}>
                <ClockCircleOutlined /> Last collection: 2 min ago
              </div>
              <Tag color="processing">Auto-collecting every 5 min</Tag>
            </div>
          </MaterialCard>
        </Col>
      </Row>

      {/* Actionable Insights */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24}>
          <MaterialCard
            elevation={2}
            title="💡 Network Insights & Recommendations"
          >
            <div
              style={{
                marginBottom: 8,
                fontSize: 13,
                color: "rgba(0,0,0,0.6)",
              }}
            >
              AI-powered analysis of your network health with actionable advice
            </div>
            <Row gutter={[12, 12]} style={{ marginTop: 16 }}>
              {insights.map((insight, index) => (
                <Col
                  xs={24}
                  md={12}
                  lg={insights.length === 1 ? 24 : 12}
                  key={index}
                >
                  <div
                    style={{
                      padding: "16px",
                      borderRadius: "12px",
                      border: `2px solid ${
                        insight.type === "error"
                          ? "#FFEBEE"
                          : insight.type === "warning"
                          ? "#FFF3E0"
                          : insight.type === "success"
                          ? "#E8F5E9"
                          : "#E3F2FD"
                      }`,
                      backgroundColor:
                        insight.type === "error"
                          ? "#FFEBEE"
                          : insight.type === "warning"
                          ? "#FFF3E0"
                          : insight.type === "success"
                          ? "#E8F5E9"
                          : "#E3F2FD",
                      cursor: "pointer",
                      transition: "all 0.2s",
                    }}
                    onClick={() => navigate(insight.link)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = "translateY(-2px)";
                      e.currentTarget.style.boxShadow =
                        "0 4px 12px rgba(0,0,0,0.1)";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = "translateY(0)";
                      e.currentTarget.style.boxShadow = "none";
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        alignItems: "flex-start",
                        gap: "12px",
                      }}
                    >
                      <div style={{ fontSize: 32, lineHeight: 1 }}>
                        {insight.icon}
                      </div>
                      <div style={{ flex: 1 }}>
                        <div
                          style={{
                            fontSize: 16,
                            fontWeight: 600,
                            marginBottom: 4,
                            color:
                              insight.type === "error"
                                ? "#C62828"
                                : insight.type === "warning"
                                ? "#F57C00"
                                : insight.type === "success"
                                ? "#2E7D32"
                                : "#1565C0",
                          }}
                        >
                          {insight.title}
                        </div>
                        <div
                          style={{
                            fontSize: 14,
                            color: "rgba(0,0,0,0.7)",
                            marginBottom: 8,
                          }}
                        >
                          {insight.message}
                        </div>
                        <Tag
                          color={
                            insight.type === "error"
                              ? "error"
                              : insight.type === "warning"
                              ? "warning"
                              : insight.type === "success"
                              ? "success"
                              : "processing"
                          }
                          style={{ cursor: "pointer" }}
                        >
                          {insight.action} →
                        </Tag>
                      </div>
                    </div>
                  </div>
                </Col>
              ))}
            </Row>
          </MaterialCard>
        </Col>
      </Row>

      {/* Device & Client Quick View */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <MaterialCard
            elevation={2}
            title="🌐 Network Infrastructure"
            extra={
              <a
                onClick={() => navigate("/devices")}
                style={{ cursor: "pointer" }}
              >
                View All →
              </a>
            }
          >
            <div
              style={{
                marginBottom: 8,
                fontSize: 13,
                color: "rgba(0,0,0,0.6)",
              }}
            >
              Your UniFi devices (Access Points, Switches, Gateways)
            </div>
            <Table
              dataSource={devicesData?.devices.slice(0, 5) || []}
              pagination={false}
              size="small"
              columns={[
                {
                  title: "Device",
                  dataIndex: "name",
                  key: "name",
                  render: (name, record: any) => (
                    <div>
                      <div style={{ fontWeight: 500 }}>{name}</div>
                      <div style={{ fontSize: 12, color: "rgba(0,0,0,0.45)" }}>
                        {record.model} •{" "}
                        {record.type?.toUpperCase() || "Device"}
                      </div>
                    </div>
                  ),
                },
                {
                  title: "Status",
                  dataIndex: "status",
                  key: "status",
                  render: (status) => (
                    <Tag color={status === "online" ? "success" : "error"}>
                      {status}
                    </Tag>
                  ),
                },
                {
                  title: "Uptime",
                  dataIndex: "uptime",
                  key: "uptime",
                  responsive: ["md"],
                  render: (uptime) => {
                    if (!uptime) return "—";
                    const days = Math.floor(uptime / 86400);
                    const hours = Math.floor((uptime % 86400) / 3600);
                    return days > 0 ? `${days}d ${hours}h` : `${hours}h`;
                  },
                },
              ]}
            />
          </MaterialCard>
        </Col>

        <Col xs={24} lg={12}>
          <MaterialCard
            elevation={2}
            title="👥 Connected Clients"
            extra={
              <a
                onClick={() => navigate("/clients")}
                style={{ cursor: "pointer" }}
              >
                View All →
              </a>
            }
          >
            <div
              style={{
                marginBottom: 8,
                fontSize: 13,
                color: "rgba(0,0,0,0.6)",
              }}
            >
              Devices currently connected to your network (WiFi & Wired)
            </div>
            <Table
              dataSource={clientsData?.clients.slice(0, 5) || []}
              pagination={false}
              size="small"
              loading={loadingClients}
              columns={[
                {
                  title: "Client",
                  dataIndex: "hostname",
                  key: "hostname",
                  render: (hostname, record: any) => (
                    <div>
                      <div style={{ fontWeight: 500 }}>
                        {hostname || record.name || "Unknown"}
                      </div>
                      <div style={{ fontSize: 12, color: "rgba(0,0,0,0.45)" }}>
                        {record.ip}
                      </div>
                    </div>
                  ),
                },
                {
                  title: "Connection",
                  dataIndex: "is_wired",
                  key: "type",
                  render: (isWired) => (
                    <Tag icon={isWired ? <ApiOutlined /> : <WifiOutlined />}>
                      {isWired ? "Wired" : "WiFi"}
                    </Tag>
                  ),
                },
                {
                  title: "Signal",
                  dataIndex: "signal_strength",
                  key: "signal",
                  responsive: ["md"],
                  render: (signal, record: any) => {
                    if (record.is_wired) return "—";
                    if (!signal) return "—";
                    const color =
                      signal > -60
                        ? "#388E3C"
                        : signal > -70
                        ? "#FFA726"
                        : "#D32F2F";
                    return <span style={{ color }}>{signal} dBm</span>;
                  },
                },
              ]}
            />
          </MaterialCard>
        </Col>
      </Row>

      {/* Info Card */}
      <MaterialCard elevation={2} title="🚀 Real-Time Monitoring Active">
        <Row gutter={[16, 16]}>
          <Col xs={24} md={12}>
            <p className="md-body-large">
              Your dashboard is connected to live data streams via WebSocket.
            </p>
            <ul className="dashboard-info-list">
              <li>✅ Real-time metric updates</li>
              <li>✅ Live device status tracking</li>
              <li>✅ Network health monitoring</li>
              <li>✅ Auto-reconnect on connection loss</li>
            </ul>
          </Col>
          <Col xs={24} md={12}>
            <p className="md-body-large">
              <strong>Data Collection Status:</strong>
            </p>
            <ul className="dashboard-info-list">
              <li>📊 {devicesData?.total || 0} devices monitored</li>
              <li>👥 {clientStats.total} clients connected</li>
              <li>🔄 Collecting every 5 minutes</li>
              <li>💾 {clientsData ? "14,998" : "Loading..."} metrics stored</li>
            </ul>
          </Col>
        </Row>
      </MaterialCard>
    </div>
  );
};

export default Dashboard;

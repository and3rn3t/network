/**
 * Analytics Dashboard - Comprehensive network insights and WiFi optimization
 */

import apiClient from "@/api/client";
import { MaterialCard } from "@/components/MaterialCard";
import {
  BarChartOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  SignalFilled,
  ThunderboltOutlined,
  WarningOutlined,
  WifiOutlined,
} from "@ant-design/icons";
import {
  Badge,
  Card,
  Col,
  Progress,
  Row,
  Statistic,
  Table,
  Tag,
  Tooltip,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import React, { useEffect, useState } from "react";

// Types
interface HealthScore {
  health_score: number;
  total_devices: number;
  online_devices: number;
  offline_devices: number;
  active_alerts: {
    critical: number;
    warning: number;
    total: number;
  };
  timestamp: string;
}

interface ClientIssue {
  mac: string;
  name: string;
  hostname: string;
  ip: string;
  signal_strength: number;
  tx_rate: number;
  rx_rate: number;
  channel: number;
  issues: string[];
  severity: "critical" | "warning" | "info";
  recommendation: string;
}

const Analytics: React.FC = () => {
  const [healthScore, setHealthScore] = useState<HealthScore | null>(null);
  const [poorClients, setPoorClients] = useState<ClientIssue[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);

      // Fetch health score
      const healthResponse = await apiClient.get<HealthScore>(
        "/api/analytics/health-score"
      );
      setHealthScore(healthResponse.data);

      // Fetch clients and analyze WiFi experience
      const clientsResponse = await apiClient.get("/api/clients");
      const clients = clientsResponse.data;

      // Analyze each client for WiFi issues
      const issues: ClientIssue[] = [];
      clients.forEach((client: any) => {
        const clientIssues: string[] = [];
        let severity: "critical" | "warning" | "info" = "info";
        let recommendation = "";

        // Check signal strength
        if (client.signal_strength < -70) {
          clientIssues.push("Weak signal");
          severity = "critical";
          recommendation =
            "Consider moving closer to access point or adding mesh node";
        } else if (client.signal_strength < -65) {
          clientIssues.push("Below optimal signal");
          severity = "warning";
          recommendation = "Slight repositioning may improve connection";
        }

        // Check TX/RX rates
        if (client.tx_rate < 50 || client.rx_rate < 50) {
          clientIssues.push("Low data rates");
          if (severity !== "critical") severity = "warning";
          recommendation +=
            (recommendation ? " • " : "") +
            "Check for interference or upgrade AP";
        }

        // Check for 2.4GHz on busy channel
        if (client.channel <= 14 && client.channel_utilization > 50) {
          clientIssues.push("Congested channel");
          if (severity !== "critical") severity = "warning";
          recommendation +=
            (recommendation ? " • " : "") +
            "Switch to 5GHz band or change channel";
        }

        // Only include clients with issues
        if (clientIssues.length > 0) {
          issues.push({
            mac: client.mac,
            name: client.name || "Unknown",
            hostname: client.hostname || "N/A",
            ip: client.ip || "N/A",
            signal_strength: client.signal_strength || 0,
            tx_rate: client.tx_rate || 0,
            rx_rate: client.rx_rate || 0,
            channel: client.channel || 0,
            issues: clientIssues,
            severity,
            recommendation: recommendation || "Monitor performance",
          });
        }
      });

      // Sort by severity (critical first)
      issues.sort((a, b) => {
        const severityOrder = { critical: 0, warning: 1, info: 2 };
        return severityOrder[a.severity] - severityOrder[b.severity];
      });

      setPoorClients(issues);
    } catch (error) {
      console.error("Failed to fetch analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  const getHealthColor = (score: number): string => {
    if (score >= 80) return "#52c41a";
    if (score >= 60) return "#faad14";
    return "#ff4d4f";
  };

  const getHealthStatus = (score: number): string => {
    if (score >= 80) return "Excellent";
    if (score >= 60) return "Good";
    if (score >= 40) return "Fair";
    return "Poor";
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "critical":
        return <ExclamationCircleOutlined style={{ color: "#ff4d4f" }} />;
      case "warning":
        return <WarningOutlined style={{ color: "#faad14" }} />;
      default:
        return <CheckCircleOutlined style={{ color: "#52c41a" }} />;
    }
  };

  const columns: ColumnsType<ClientIssue> = [
    {
      title: "Client",
      key: "client",
      render: (_: any, record: ClientIssue) => (
        <div>
          <div style={{ fontWeight: 500 }}>
            {record.name || record.hostname}
          </div>
          <div style={{ fontSize: 12, color: "#666" }}>{record.ip}</div>
        </div>
      ),
    },
    {
      title: "Signal",
      dataIndex: "signal_strength",
      key: "signal",
      width: 120,
      render: (signal: number) => {
        const strength =
          signal >= -60 ? "good" : signal >= -70 ? "fair" : "poor";
        const color =
          strength === "good"
            ? "#52c41a"
            : strength === "fair"
            ? "#faad14"
            : "#ff4d4f";
        return (
          <Tooltip title={`${signal} dBm`}>
            <Tag color={color}>
              <SignalFilled /> {signal} dBm
            </Tag>
          </Tooltip>
        );
      },
      sorter: (a: ClientIssue, b: ClientIssue) =>
        b.signal_strength - a.signal_strength,
    },
    {
      title: "Speed",
      key: "speed",
      width: 120,
      render: (_: any, record: ClientIssue) => (
        <div style={{ fontSize: 12 }}>
          <div>↓ {record.rx_rate} Mbps</div>
          <div>↑ {record.tx_rate} Mbps</div>
        </div>
      ),
    },
    {
      title: "Channel",
      dataIndex: "channel",
      key: "channel",
      width: 80,
      render: (channel: number) => {
        const band = channel <= 14 ? "2.4GHz" : "5GHz";
        return (
          <Tag color={channel <= 14 ? "blue" : "green"}>
            {band} Ch{channel}
          </Tag>
        );
      },
    },
    {
      title: "Issues",
      dataIndex: "issues",
      key: "issues",
      render: (issues: string[], record: ClientIssue) => (
        <div>
          {issues.map((issue, idx) => (
            <Tag
              key={idx}
              icon={getSeverityIcon(record.severity)}
              style={{ marginBottom: 4 }}
            >
              {issue}
            </Tag>
          ))}
        </div>
      ),
    },
    {
      title: "Recommendation",
      dataIndex: "recommendation",
      key: "recommendation",
      render: (text: string) => (
        <span style={{ fontSize: 12, color: "#666" }}>{text}</span>
      ),
    },
  ];

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-header-title">
          <BarChartOutlined style={{ marginRight: 12 }} />
          Network Analytics
        </h1>
        <p className="page-header-description">
          Comprehensive insights, anomaly detection, and WiFi optimization
        </p>
      </div>

      {/* Health Score Overview */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading}>
            <Statistic
              title="Network Health"
              value={healthScore?.health_score || 0}
              precision={1}
              valueStyle={{
                color: getHealthColor(healthScore?.health_score || 0),
              }}
              suffix="/100"
              prefix={<ThunderboltOutlined />}
            />
            <Progress
              percent={healthScore?.health_score || 0}
              strokeColor={getHealthColor(healthScore?.health_score || 0)}
              showInfo={false}
              style={{ marginTop: 8 }}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: "#666" }}>
              Status: {getHealthStatus(healthScore?.health_score || 0)}
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading}>
            <Statistic
              title="Online Devices"
              value={healthScore?.online_devices || 0}
              suffix={`/ ${healthScore?.total_devices || 0}`}
              prefix={<WifiOutlined />}
              valueStyle={{ color: "#52c41a" }}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: "#666" }}>
              {healthScore?.offline_devices || 0} offline
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading}>
            <Statistic
              title="Active Alerts"
              value={healthScore?.active_alerts.total || 0}
              prefix={<WarningOutlined />}
              valueStyle={{
                color:
                  (healthScore?.active_alerts.critical || 0) > 0
                    ? "#ff4d4f"
                    : "#faad14",
              }}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: "#666" }}>
              {healthScore?.active_alerts.critical || 0} critical •{" "}
              {healthScore?.active_alerts.warning || 0} warnings
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card loading={loading}>
            <Statistic
              title="WiFi Issues"
              value={poorClients.length}
              prefix={<SignalFilled />}
              valueStyle={{
                color:
                  poorClients.filter((c) => c.severity === "critical").length >
                  0
                    ? "#ff4d4f"
                    : "#faad14",
              }}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: "#666" }}>
              {poorClients.filter((c) => c.severity === "critical").length}{" "}
              critical issues
            </div>
          </Card>
        </Col>
      </Row>

      {/* WiFi Optimization Recommendations */}
      <MaterialCard
        elevation={1}
        title={
          <>
            <WifiOutlined style={{ marginRight: 8 }} />
            WiFi Optimization Recommendations
          </>
        }
        style={{ marginBottom: 24 }}
      >
        {poorClients.length === 0 ? (
          <div style={{ textAlign: "center", padding: "40px 0" }}>
            <CheckCircleOutlined
              style={{ fontSize: 48, color: "#52c41a", marginBottom: 16 }}
            />
            <h3>All Clients Have Good WiFi Experience!</h3>
            <p style={{ color: "#666" }}>
              No optimization recommendations at this time.
            </p>
          </div>
        ) : (
          <>
            <div style={{ marginBottom: 16 }}>
              <Badge
                count={
                  poorClients.filter((c) => c.severity === "critical").length
                }
                style={{ backgroundColor: "#ff4d4f" }}
              >
                <Tag color="error">Critical</Tag>
              </Badge>
              <Badge
                count={
                  poorClients.filter((c) => c.severity === "warning").length
                }
                style={{ backgroundColor: "#faad14", marginLeft: 16 }}
              >
                <Tag color="warning">Warnings</Tag>
              </Badge>
            </div>
            <Table
              columns={columns}
              dataSource={poorClients}
              rowKey="mac"
              loading={loading}
              pagination={{ pageSize: 10 }}
              size="small"
            />
          </>
        )}
      </MaterialCard>

      {/* Quick Insights */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <MaterialCard elevation={1} title="🎯 Quick Insights">
            <ul style={{ paddingLeft: 20 }}>
              <li>
                <strong>Signal Strength Guidelines:</strong>
                <ul style={{ marginTop: 8 }}>
                  <li>-50 to -60 dBm: Excellent</li>
                  <li>-60 to -70 dBm: Good</li>
                  <li>-70 to -80 dBm: Fair (may experience issues)</li>
                  <li>Below -80 dBm: Poor (action needed)</li>
                </ul>
              </li>
              <li style={{ marginTop: 12 }}>
                <strong>Speed Recommendations:</strong>
                <ul style={{ marginTop: 8 }}>
                  <li>Streaming HD video: 25+ Mbps</li>
                  <li>Video calls: 10+ Mbps</li>
                  <li>Web browsing: 5+ Mbps</li>
                </ul>
              </li>
            </ul>
          </MaterialCard>
        </Col>

        <Col xs={24} lg={12}>
          <MaterialCard elevation={1} title="💡 Optimization Tips">
            <ul style={{ paddingLeft: 20 }}>
              <li>Place access points in central, elevated locations</li>
              <li>Avoid physical obstructions (walls, metal objects)</li>
              <li>Use 5GHz band for better speeds (shorter range)</li>
              <li>Keep 2.4GHz for compatibility and longer range</li>
              <li>Enable band steering to push clients to 5GHz</li>
              <li>Use channels 1, 6, or 11 on 2.4GHz to minimize overlap</li>
              <li>Consider mesh nodes for large areas</li>
              <li>Update firmware regularly for best performance</li>
            </ul>
          </MaterialCard>
        </Col>
      </Row>
    </div>
  );
};

export default Analytics;

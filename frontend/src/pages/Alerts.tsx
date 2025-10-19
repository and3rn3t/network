/**
 * Alerts page - Alert intelligence and real-time notifications
 */

import { MaterialCard } from "@/components/MaterialCard";
import { useRealTimeAlerts } from "@/hooks/useRealTime";
import {
  BellOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  ThunderboltOutlined,
  WarningOutlined,
} from "@ant-design/icons";
import { Badge, Button, Empty, List, Space, Tag, message } from "antd";
import React, { useEffect } from "react";
import "./Alerts.css";

const Alerts: React.FC = () => {
  const { alerts, newAlertCount, lastAlert, status, clearNewAlertCount } =
    useRealTimeAlerts();

  // Show toast notification for new alerts
  useEffect(() => {
    if (lastAlert && newAlertCount > 0) {
      const severity = lastAlert.severity;
      const messageText = `${severity.toUpperCase()}: ${lastAlert.message}`;

      if (severity === "critical") {
        void message.error({
          content: messageText,
          duration: 8,
          icon: <ExclamationCircleOutlined />,
        });
      } else if (severity === "warning") {
        void message.warning({
          content: messageText,
          duration: 5,
          icon: <WarningOutlined />,
        });
      } else {
        void message.info({
          content: messageText,
          duration: 3,
          icon: <BellOutlined />,
        });
      }
    }
  }, [lastAlert, newAlertCount]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "error";
      case "warning":
        return "warning";
      case "info":
        return "default";
      default:
        return "default";
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "critical":
        return <CloseCircleOutlined />;
      case "warning":
        return <WarningOutlined />;
      case "info":
        return <ExclamationCircleOutlined />;
      default:
        return <BellOutlined />;
    }
  };

  const getStatusColor = (alertStatus: string) => {
    switch (alertStatus) {
      case "open":
        return "error";
      case "acknowledged":
        return "warning";
      case "resolved":
        return "success";
      default:
        return "default";
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) {
      return "Just now";
    }
    if (diffMins < 60) {
      return `${diffMins} min${diffMins > 1 ? "s" : ""} ago`;
    }
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) {
      return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`;
    }
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} day${diffDays > 1 ? "s" : ""} ago`;
  };

  return (
    <div className="alerts-container">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-header-title">
            <BellOutlined className="page-header-icon" />
            Alert Intelligence
            {status === "connected" && (
              <Badge
                status="processing"
                text="LIVE"
                className="alerts-live-badge"
              />
            )}
          </h1>
          <p className="page-header-description">
            Real-time alert monitoring and intelligent pattern analysis
          </p>
        </div>
        {newAlertCount > 0 && (
          <Button
            type="primary"
            icon={<CheckCircleOutlined />}
            onClick={clearNewAlertCount}
          >
            Clear {newAlertCount} New
          </Button>
        )}
      </div>

      <Space direction="vertical" size="large" className="alerts-content">
        {/* Real-Time Alerts */}
        <MaterialCard
          elevation={2}
          title={
            <span>
              <ThunderboltOutlined className="alerts-card-icon" />
              Recent Alerts
              {newAlertCount > 0 && (
                <Badge
                  count={newAlertCount}
                  className="alerts-new-badge"
                  offset={[10, 0]}
                />
              )}
            </span>
          }
        >
          {alerts.length === 0 ? (
            <Empty
              description="No recent alerts"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          ) : (
            <List
              dataSource={alerts}
              renderItem={(alert) => (
                <List.Item
                  key={alert.id}
                  className={`alerts-list-item alerts-severity-${alert.severity}`}
                  actions={[
                    <Tag color={getStatusColor(alert.status)} key="status">
                      {alert.status.toUpperCase()}
                    </Tag>,
                  ]}
                >
                  <List.Item.Meta
                    avatar={getSeverityIcon(alert.severity)}
                    title={
                      <Space>
                        <Tag color={getSeverityColor(alert.severity)}>
                          {alert.severity.toUpperCase()}
                        </Tag>
                        <span>{alert.message}</span>
                      </Space>
                    }
                    description={
                      <Space direction="vertical" size="small">
                        <span className="alerts-timestamp">
                          {formatTimestamp(alert.triggered_at)}
                        </span>
                        {alert.device_id && (
                          <span className="alerts-device">
                            Device: {alert.device_id}
                          </span>
                        )}
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </MaterialCard>

        <MaterialCard elevation={1} title="📈 Alert Analytics">
          <p className="md-body-large">
            <strong>Coming soon:</strong>
          </p>
          <ul className="alerts-feature-list">
            <li>Alert frequency trends (last 90 days)</li>
            <li>Alert type distribution (pie charts)</li>
            <li>MTTA/MTTR tracking by alert type</li>
            <li>Alert effectiveness scoring</li>
            <li>Pattern recognition (recurring alert sequences)</li>
          </ul>
        </MaterialCard>

        <MaterialCard elevation={1} title="🔗 Alert Correlation">
          <p className="md-body-large">
            <strong>Root cause analysis:</strong>
          </p>
          <ul className="alerts-feature-list">
            <li>Visual alert timeline (drill-down by device/type)</li>
            <li>Alert correlation matrix (which alerts happen together?)</li>
            <li>Root cause chain visualization</li>
            <li>Alert storm detection and analysis</li>
          </ul>
        </MaterialCard>

        <MaterialCard elevation={1} title="🎯 Alert Effectiveness">
          <p className="md-body-large">
            <strong>Optimization insights:</strong>
          </p>
          <ul className="alerts-feature-list">
            <li>Which rules trigger most often?</li>
            <li>False positive rate by rule</li>
            <li>Alert tuning recommendations</li>
            <li>Alert fatigue metrics</li>
          </ul>
        </MaterialCard>
      </Space>
    </div>
  );
};

export default Alerts;

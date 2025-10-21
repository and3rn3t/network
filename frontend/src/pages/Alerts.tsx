/**
 * Alerts Page - View and manage active alerts
 */

import { MaterialCard } from "@/components/MaterialCard";
import {
  BellOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  FilterOutlined,
  ReloadOutlined,
  WarningOutlined,
} from "@ant-design/icons";
import {
  Badge,
  Button,
  Col,
  Descriptions,
  Modal,
  Row,
  Select,
  Space,
  Table,
  Tag,
  message,
} from "antd";
import { format } from "date-fns";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Alerts.css";

interface Alert {
  id: number;
  rule_id: number;
  host_id: number;
  status: string;
  severity: string;
  message: string;
  metric_value: number;
  threshold_value: number;
  triggered_at: string;
  acknowledged_at?: string;
  acknowledged_by?: string;
  resolved_at?: string;
  resolved_by?: string;
  notes?: string;
}

const Alerts: React.FC = () => {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>("triggered");
  const [severityFilter, setSeverityFilter] = useState<string | null>(null);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [detailsVisible, setDetailsVisible] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (statusFilter) params.append("status", statusFilter);
      if (severityFilter) params.append("severity", severityFilter);
      params.append("limit", "100");

      const response = await fetch(
        `http://localhost:8000/api/alerts?${params}`
      );
      const data = await response.json();
      setAlerts(data.alerts || []);
      setTotal(data.total || 0);
    } catch (error) {
      message.error("Failed to fetch alerts");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [statusFilter, severityFilter]);

  const handleAcknowledge = async (alertId: number) => {
    setActionLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/alerts/${alertId}/acknowledge`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ acknowledged_by: "admin" }),
        }
      );
      if (response.ok) {
        message.success("Alert acknowledged");
        fetchAlerts();
        setDetailsVisible(false);
      } else {
        message.error("Failed to acknowledge alert");
      }
    } catch (error) {
      message.error("Failed to acknowledge alert");
    } finally {
      setActionLoading(false);
    }
  };

  const handleResolve = async (alertId: number, notes?: string) => {
    setActionLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/alerts/${alertId}/resolve`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ resolved_by: "admin", notes }),
        }
      );
      if (response.ok) {
        message.success("Alert resolved");
        fetchAlerts();
        setDetailsVisible(false);
      } else {
        message.error("Failed to resolve alert");
      }
    } catch (error) {
      message.error("Failed to resolve alert");
    } finally {
      setActionLoading(false);
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "critical":
        return <CloseCircleOutlined style={{ color: "#f5222d" }} />;
      case "warning":
        return <ExclamationCircleOutlined style={{ color: "#fa8c16" }} />;
      case "info":
        return <BellOutlined style={{ color: "#1890ff" }} />;
      default:
        return <BellOutlined />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "error";
      case "warning":
        return "warning";
      case "info":
        return "processing";
      default:
        return "default";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "triggered":
        return "error";
      case "acknowledged":
        return "warning";
      case "resolved":
        return "success";
      default:
        return "default";
    }
  };

  const columns = [
    {
      title: "Severity",
      dataIndex: "severity",
      key: "severity",
      width: 100,
      render: (severity: string) => (
        <Tag
          icon={getSeverityIcon(severity)}
          color={getSeverityColor(severity)}
        >
          {severity.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: "Message",
      dataIndex: "message",
      key: "message",
      render: (msg: string, record: Alert) => (
        <div>
          <div style={{ fontWeight: 500 }}>{msg}</div>
          <div style={{ fontSize: 12, color: "rgba(0,0,0,0.45)" }}>
            Value: {record.metric_value?.toFixed(2)} | Threshold:{" "}
            {record.threshold_value?.toFixed(2)}
          </div>
        </div>
      ),
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 120,
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>{status.toUpperCase()}</Tag>
      ),
    },
    {
      title: "Triggered",
      dataIndex: "triggered_at",
      key: "triggered_at",
      width: 180,
      render: (date: string) => format(new Date(date), "MMM dd, yyyy HH:mm"),
    },
    {
      title: "Actions",
      key: "actions",
      width: 150,
      render: (_: unknown, record: Alert) => (
        <Space>
          <Button
            size="small"
            onClick={() => {
              setSelectedAlert(record);
              setDetailsVisible(true);
            }}
          >
            Details
          </Button>
          {record.status === "triggered" && (
            <Button
              size="small"
              type="primary"
              onClick={() => handleAcknowledge(record.id)}
            >
              Acknowledge
            </Button>
          )}
        </Space>
      ),
    },
  ];

  const activeCount = alerts.filter((a) => a.status === "triggered").length;
  const acknowledgedCount = alerts.filter(
    (a) => a.status === "acknowledged"
  ).length;

  return (
    <div className="dashboard-container">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-header-title">
            Alert Management
            {activeCount > 0 && (
              <Badge
                count={activeCount}
                style={{
                  marginLeft: 16,
                  backgroundColor: "#f5222d",
                }}
              />
            )}
          </h1>
          <p className="page-header-description">
            Monitor and manage network alerts and notifications
          </p>
        </div>
        <Space>
          <Button icon={<FilterOutlined />} onClick={() => navigate("/rules")}>
            Manage Rules
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchAlerts}
            loading={loading}
          >
            Refresh
          </Button>
        </Space>
      </div>

      {/* Summary Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <MaterialCard elevation={1}>
            <div style={{ textAlign: "center" }}>
              <WarningOutlined
                style={{ fontSize: 32, color: "#f5222d", marginBottom: 8 }}
              />
              <div style={{ fontSize: 28, fontWeight: 600, color: "#f5222d" }}>
                {activeCount}
              </div>
              <div style={{ color: "rgba(0,0,0,0.45)" }}>Active Alerts</div>
            </div>
          </MaterialCard>
        </Col>
        <Col xs={24} sm={8}>
          <MaterialCard elevation={1}>
            <div style={{ textAlign: "center" }}>
              <ClockCircleOutlined
                style={{ fontSize: 32, color: "#fa8c16", marginBottom: 8 }}
              />
              <div style={{ fontSize: 28, fontWeight: 600, color: "#fa8c16" }}>
                {acknowledgedCount}
              </div>
              <div style={{ color: "rgba(0,0,0,0.45)" }}>Acknowledged</div>
            </div>
          </MaterialCard>
        </Col>
        <Col xs={24} sm={8}>
          <MaterialCard elevation={1}>
            <div style={{ textAlign: "center" }}>
              <CheckCircleOutlined
                style={{ fontSize: 32, color: "#52c41a", marginBottom: 8 }}
              />
              <div style={{ fontSize: 28, fontWeight: 600, color: "#52c41a" }}>
                {total}
              </div>
              <div style={{ color: "rgba(0,0,0,0.45)" }}>Total Alerts</div>
            </div>
          </MaterialCard>
        </Col>
      </Row>

      {/* Filters */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12} md={8}>
          <Select
            style={{ width: "100%" }}
            placeholder="Filter by status"
            value={statusFilter}
            onChange={setStatusFilter}
          >
            <Select.Option value="">All Statuses</Select.Option>
            <Select.Option value="triggered">Triggered</Select.Option>
            <Select.Option value="acknowledged">Acknowledged</Select.Option>
            <Select.Option value="resolved">Resolved</Select.Option>
          </Select>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Select
            style={{ width: "100%" }}
            placeholder="Filter by severity"
            value={severityFilter}
            onChange={setSeverityFilter}
            allowClear
          >
            <Select.Option value="critical">Critical</Select.Option>
            <Select.Option value="warning">Warning</Select.Option>
            <Select.Option value="info">Info</Select.Option>
          </Select>
        </Col>
      </Row>

      {/* Alerts Table */}
      <MaterialCard elevation={2}>
        <Table
          dataSource={alerts}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{
            total,
            pageSize: 100,
            showSizeChanger: false,
            showTotal: (total) => `Total ${total} alerts`,
          }}
        />
      </MaterialCard>

      {/* Alert Details Modal */}
      <Modal
        title="Alert Details"
        open={detailsVisible}
        onCancel={() => setDetailsVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailsVisible(false)}>
            Close
          </Button>,
          selectedAlert?.status === "triggered" && (
            <Button
              key="acknowledge"
              onClick={() => handleAcknowledge(selectedAlert.id)}
              loading={actionLoading}
            >
              Acknowledge
            </Button>
          ),
          selectedAlert?.status !== "resolved" && (
            <Button
              key="resolve"
              type="primary"
              onClick={() => handleResolve(selectedAlert!.id)}
              loading={actionLoading}
            >
              Resolve
            </Button>
          ),
        ]}
        width={700}
      >
        {selectedAlert && (
          <Descriptions column={1} bordered>
            <Descriptions.Item label="Severity">
              <Tag
                icon={getSeverityIcon(selectedAlert.severity)}
                color={getSeverityColor(selectedAlert.severity)}
              >
                {selectedAlert.severity.toUpperCase()}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Status">
              <Tag color={getStatusColor(selectedAlert.status)}>
                {selectedAlert.status.toUpperCase()}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Message">
              {selectedAlert.message}
            </Descriptions.Item>
            <Descriptions.Item label="Metric Value">
              {selectedAlert.metric_value?.toFixed(2)}
            </Descriptions.Item>
            <Descriptions.Item label="Threshold">
              {selectedAlert.threshold_value?.toFixed(2)}
            </Descriptions.Item>
            <Descriptions.Item label="Triggered At">
              {format(new Date(selectedAlert.triggered_at), "PPpp")}
            </Descriptions.Item>
            {selectedAlert.acknowledged_at && (
              <Descriptions.Item label="Acknowledged At">
                {format(new Date(selectedAlert.acknowledged_at), "PPpp")}
                <br />
                By: {selectedAlert.acknowledged_by}
              </Descriptions.Item>
            )}
            {selectedAlert.resolved_at && (
              <Descriptions.Item label="Resolved At">
                {format(new Date(selectedAlert.resolved_at), "PPpp")}
                <br />
                By: {selectedAlert.resolved_by}
              </Descriptions.Item>
            )}
            {selectedAlert.notes && (
              <Descriptions.Item label="Notes">
                {selectedAlert.notes}
              </Descriptions.Item>
            )}
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default Alerts;

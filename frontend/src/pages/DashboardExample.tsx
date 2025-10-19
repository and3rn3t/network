/**
 * Example Dashboard Page with Material Design 3 Components
 * This shows how to use the new Material Design styling
 */

import { MaterialCard } from "@/components/MaterialCard";
import {
  ArrowDownOutlined,
  ArrowUpOutlined,
  ClockCircleOutlined,
  CloudServerOutlined,
  WifiOutlined,
} from "@ant-design/icons";
import { Alert, Button, Col, Row, Space, Statistic, Tag } from "antd";
import React from "react";

export const DashboardExample: React.FC = () => {
  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-header-title">Network Dashboard</h1>
        <p className="page-header-description">
          Real-time overview of your UniFi network performance and health
        </p>
      </div>

      {/* Alert Example */}
      <Alert
        message="Network Status"
        description="All systems operational. 24 devices online."
        type="success"
        showIcon
        closable
        style={{ marginBottom: "var(--md-sys-spacing-lg)" }}
      />

      {/* Statistics Cards */}
      <Row
        gutter={[24, 24]}
        style={{ marginBottom: "var(--md-sys-spacing-xl)" }}
      >
        <Col xs={24} sm={12} lg={6}>
          <MaterialCard elevation={1} variant="elevated">
            <Statistic
              title="Total Devices"
              value={24}
              prefix={<CloudServerOutlined />}
              suffix={
                <Tag color="success" style={{ marginLeft: 8 }}>
                  Online
                </Tag>
              }
            />
          </MaterialCard>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <MaterialCard elevation={1} variant="elevated">
            <Statistic
              title="Active Clients"
              value={142}
              prefix={<WifiOutlined />}
              valueStyle={{ color: "var(--md-sys-color-primary)" }}
              suffix={
                <div style={{ fontSize: "14px", fontWeight: "normal" }}>
                  <ArrowUpOutlined style={{ color: "#52c41a" }} /> 12%
                </div>
              }
            />
          </MaterialCard>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <MaterialCard elevation={1} variant="elevated">
            <Statistic
              title="Network Load"
              value={68.5}
              precision={1}
              prefix={<ArrowUpOutlined />}
              suffix="%"
              valueStyle={{ color: "var(--md-sys-color-warning, #F57C00)" }}
            />
          </MaterialCard>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <MaterialCard elevation={1} variant="elevated">
            <Statistic
              title="Avg Response Time"
              value={23}
              prefix={<ClockCircleOutlined />}
              suffix="ms"
              valueStyle={{ color: "var(--md-sys-color-success, #388E3C)" }}
              suffix={
                <div style={{ fontSize: "14px", fontWeight: "normal" }}>
                  <ArrowDownOutlined style={{ color: "#52c41a" }} /> 5%
                </div>
              }
            />
          </MaterialCard>
        </Col>
      </Row>

      {/* Content Cards */}
      <Row gutter={[24, 24]}>
        <Col xs={24} lg={12}>
          <MaterialCard
            title="Device Health"
            elevation={2}
            extra={<Button type="link">View All</Button>}
          >
            <Space direction="vertical" size="middle" style={{ width: "100%" }}>
              <div>
                <h4 className="md-title-small" style={{ marginBottom: 8 }}>
                  CPU Usage
                </h4>
                <p className="md-body-medium">
                  Average CPU utilization across all devices is 45%. This is
                  within normal operating parameters.
                </p>
              </div>
              <div>
                <h4 className="md-title-small" style={{ marginBottom: 8 }}>
                  Memory Status
                </h4>
                <p className="md-body-medium">
                  Memory usage is stable at 62% across the network. No devices
                  are experiencing memory pressure.
                </p>
              </div>
            </Space>
          </MaterialCard>
        </Col>

        <Col xs={24} lg={12}>
          <MaterialCard
            title="Recent Alerts"
            elevation={2}
            extra={<Button type="link">Manage Alerts</Button>}
          >
            <Space direction="vertical" size="middle" style={{ width: "100%" }}>
              <Alert
                message="High CPU Usage Detected"
                description="Device AP-Living-Room exceeded 80% CPU threshold."
                type="warning"
                showIcon
                closable
              />
              <Alert
                message="Client Connected"
                description="New device joined the network: iPhone-14."
                type="info"
                showIcon
                closable
              />
            </Space>
          </MaterialCard>
        </Col>
      </Row>

      {/* Different Card Variants */}
      <Row gutter={[24, 24]} style={{ marginTop: "var(--md-sys-spacing-xxl)" }}>
        <Col xs={24} md={8}>
          <MaterialCard title="Elevated Card" variant="elevated" elevation={1}>
            <p className="md-body-medium">
              This card uses the elevated variant with level 1 elevation.
              Perfect for standard content cards.
            </p>
            <Space style={{ marginTop: 16 }}>
              <Button type="primary">Primary Action</Button>
              <Button>Secondary</Button>
            </Space>
          </MaterialCard>
        </Col>

        <Col xs={24} md={8}>
          <MaterialCard title="Filled Card" variant="filled" elevation={0}>
            <p className="md-body-medium">
              This card uses the filled variant with no elevation. Great for
              secondary content or grouped information.
            </p>
            <Space style={{ marginTop: 16 }}>
              <Button type="default">Action</Button>
            </Space>
          </MaterialCard>
        </Col>

        <Col xs={24} md={8}>
          <MaterialCard title="Outlined Card" variant="outlined" elevation={0}>
            <p className="md-body-medium">
              This card uses the outlined variant. Ideal for emphasizing
              boundaries without shadow depth.
            </p>
            <Space style={{ marginTop: 16 }}>
              <Button type="dashed">Action</Button>
            </Space>
          </MaterialCard>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardExample;

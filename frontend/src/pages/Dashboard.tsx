/**
 * Dashboard - Overview page with Material Design 3
 */

import { MaterialCard } from "@/components/MaterialCard";
import {
  CheckCircleOutlined,
  FallOutlined,
  RiseOutlined,
  WarningOutlined,
} from "@ant-design/icons";
import { Col, Row, Statistic } from "antd";
import React from "react";

const Dashboard: React.FC = () => {
  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-header-title">Network Overview</h1>
        <p className="page-header-description">
          Welcome to your historical analysis and insights platform
        </p>
      </div>

      {/* Statistics Cards */}
      <Row gutter={[24, 24]} style={{ marginBottom: 32 }}>
        <Col xs={24} sm={12} lg={6}>
          <MaterialCard elevation={1}>
            <Statistic
              title="Total Devices"
              value={12}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: "var(--md-sys-color-success, #388E3C)" }}
            />
          </MaterialCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MaterialCard elevation={1}>
            <Statistic
              title="Network Health"
              value={98.5}
              suffix="%"
              prefix={<RiseOutlined />}
              valueStyle={{ color: "var(--md-sys-color-success, #388E3C)" }}
            />
          </MaterialCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MaterialCard elevation={1}>
            <Statistic
              title="Active Alerts"
              value={3}
              prefix={<WarningOutlined />}
              valueStyle={{ color: "var(--md-sys-color-error, #D32F2F)" }}
            />
          </MaterialCard>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MaterialCard elevation={1}>
            <Statistic
              title="Avg CPU Usage"
              value={24.7}
              suffix="%"
              prefix={<FallOutlined />}
              valueStyle={{ color: "var(--md-sys-color-primary, #1E88E5)" }}
            />
          </MaterialCard>
        </Col>
      </Row>

      {/* Info Card */}
      <MaterialCard elevation={2} title="🚀 Phase 5.2 Setup Complete!">
        <p className="md-body-large">
          The frontend foundation is ready with Material Design 3. Next steps:
        </p>
        <ul style={{ marginLeft: 24, marginTop: 16 }}>
          <li>✅ React + TypeScript project initialized</li>
          <li>✅ Material Design 3 theme implemented</li>
          <li>✅ Recharts for time-series visualization</li>
          <li>✅ React Router with authentication</li>
          <li>✅ Enhanced UI components</li>
          <li>✅ API client with JWT authentication</li>
          <li>✅ Modern layout and navigation</li>
        </ul>
        <p className="md-body-large" style={{ marginTop: 16, fontWeight: 600 }}>
          Ready to build Phase 5.3: Historical Analysis Dashboard! 📊
        </p>
      </MaterialCard>
    </div>
  );
};

export default Dashboard;

/**
 * Dashboard - Overview page
 */

import {
  CheckCircleOutlined,
  FallOutlined,
  RiseOutlined,
  WarningOutlined,
} from "@ant-design/icons";
import { Card, Col, Row, Statistic, Typography } from "antd";
import React from "react";

const { Title, Paragraph } = Typography;

const Dashboard: React.FC = () => {
  return (
    <div>
      <Title level={2}>Network Overview</Title>
      <Paragraph type="secondary">
        Welcome to your historical analysis and insights platform
      </Paragraph>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Devices"
              value={12}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: "#3f8600" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Network Health"
              value={98.5}
              suffix="%"
              prefix={<RiseOutlined />}
              valueStyle={{ color: "#3f8600" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Active Alerts"
              value={3}
              prefix={<WarningOutlined />}
              valueStyle={{ color: "#cf1322" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Avg CPU Usage"
              value={24.7}
              suffix="%"
              prefix={<FallOutlined />}
              valueStyle={{ color: "#1890ff" }}
            />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 24 }}>
        <Title level={4}>🚀 Phase 5.2 Setup Complete!</Title>
        <Paragraph>The frontend foundation is ready. Next steps:</Paragraph>
        <ul>
          <li>✅ React + TypeScript project initialized</li>
          <li>✅ Recharts for time-series visualization</li>
          <li>✅ React Router with authentication</li>
          <li>✅ Ant Design UI components</li>
          <li>✅ API client with JWT authentication</li>
          <li>✅ Basic layout and navigation</li>
        </ul>
        <Paragraph strong style={{ marginTop: 16 }}>
          Ready to build Phase 5.3: Historical Analysis Dashboard! 📊
        </Paragraph>
      </Card>
    </div>
  );
};

export default Dashboard;

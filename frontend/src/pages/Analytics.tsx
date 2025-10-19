/**
 * Analytics page - Anomaly detection and statistical analysis
 */

import { BarChartOutlined } from "@ant-design/icons";
import { Card, Space, Typography } from "antd";
import React from "react";

const { Title, Paragraph } = Typography;

const Analytics: React.FC = () => {
  return (
    <div>
      <Title level={2}>
        <BarChartOutlined /> Analytics Engine
      </Title>
      <Paragraph type="secondary">
        Anomaly detection, statistical analysis, and predictive insights
      </Paragraph>

      <Space direction="vertical" size="large" style={{ width: "100%" }}>
        <Card title="🔍 Anomaly Detection">
          <Paragraph>
            <strong>Coming in Phase 5.4:</strong>
          </Paragraph>
          <ul>
            <li>Visual anomaly highlighting on charts</li>
            <li>Automatic baseline learning</li>
            <li>"What's unusual right now?" summary</li>
            <li>Anomaly history and pattern recognition</li>
            <li>Correlation analysis (multiple devices acting strange)</li>
          </ul>
        </Card>

        <Card title="📊 Statistical Analysis">
          <Paragraph>
            <strong>Planned features:</strong>
          </Paragraph>
          <ul>
            <li>Percentile reports (95th, 99th percentile)</li>
            <li>Standard deviation tracking</li>
            <li>Moving averages (7-day, 30-day smoothing)</li>
            <li>Trend direction indicators (improving/worsening)</li>
          </ul>
        </Card>

        <Card title="🔮 Predictive Insights">
          <Paragraph>
            <strong>Machine learning powered:</strong>
          </Paragraph>
          <ul>
            <li>"Device likely to fail in next 48 hours" predictions</li>
            <li>Resource exhaustion forecasting</li>
            <li>Pattern-based failure prediction</li>
            <li>Seasonal trend detection</li>
          </ul>
        </Card>
      </Space>
    </div>
  );
};

export default Analytics;

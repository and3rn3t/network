/**
 * Analytics page - Anomaly detection and statistical analysis
 */

import { MaterialCard } from "@/components/MaterialCard";
import { BarChartOutlined } from "@ant-design/icons";
import { Space } from "antd";
import React from "react";

const Analytics: React.FC = () => {
  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-header-title">
          <BarChartOutlined style={{ marginRight: 12 }} />
          Analytics Engine
        </h1>
        <p className="page-header-description">
          Anomaly detection, statistical analysis, and predictive insights
        </p>
      </div>

      <Space direction="vertical" size="large" style={{ width: "100%" }}>
        <MaterialCard elevation={1} title="🔍 Anomaly Detection">
          <p className="md-body-large">
            <strong>Coming in Phase 5.4:</strong>
          </p>
          <ul className="mt-sm">
            <li>Visual anomaly highlighting on charts</li>
            <li>Automatic baseline learning</li>
            <li>"What's unusual right now?" summary</li>
            <li>Anomaly history and pattern recognition</li>
            <li>Correlation analysis (multiple devices acting strange)</li>
          </ul>
        </MaterialCard>

        <MaterialCard elevation={1} title="📊 Statistical Analysis">
          <p className="md-body-large">
            <strong>Planned features:</strong>
          </p>
          <ul className="mt-sm">
            <li>Percentile reports (95th, 99th percentile)</li>
            <li>Standard deviation tracking</li>
            <li>Moving averages (7-day, 30-day smoothing)</li>
            <li>Trend direction indicators (improving/worsening)</li>
          </ul>
        </MaterialCard>

        <MaterialCard elevation={1} title="🔮 Predictive Insights">
          <p className="md-body-large">
            <strong>Machine learning powered:</strong>
          </p>
          <ul className="mt-sm">
            <li>"Device likely to fail in next 48 hours" predictions</li>
            <li>Resource exhaustion forecasting</li>
            <li>Pattern-based failure prediction</li>
            <li>Seasonal trend detection</li>
          </ul>
        </MaterialCard>
      </Space>
    </div>
  );
};

export default Analytics;

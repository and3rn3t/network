/**
 * Alerts page - Alert intelligence and pattern analysis
 */

import { BellOutlined } from "@ant-design/icons";
import { Card, Space, Typography } from "antd";
import React from "react";

const { Title, Paragraph } = Typography;

const Alerts: React.FC = () => {
  return (
    <div>
      <Title level={2}>
        <BellOutlined /> Alert Intelligence
      </Title>
      <Paragraph type="secondary">
        Reduce alert fatigue with intelligent pattern analysis
      </Paragraph>

      <Space direction="vertical" size="large" style={{ width: "100%" }}>
        <Card title="📈 Alert Analytics">
          <Paragraph>
            <strong>Coming in Phase 5.5:</strong>
          </Paragraph>
          <ul>
            <li>Alert frequency trends (last 90 days)</li>
            <li>Alert type distribution (pie charts)</li>
            <li>MTTA/MTTR tracking by alert type</li>
            <li>Alert effectiveness scoring</li>
            <li>Pattern recognition (recurring alert sequences)</li>
          </ul>
        </Card>

        <Card title="🔗 Alert Correlation">
          <Paragraph>
            <strong>Root cause analysis:</strong>
          </Paragraph>
          <ul>
            <li>Visual alert timeline (drill-down by device/type)</li>
            <li>Alert correlation matrix (which alerts happen together?)</li>
            <li>Root cause chain visualization</li>
            <li>Alert storm detection and analysis</li>
          </ul>
        </Card>

        <Card title="🎯 Alert Effectiveness">
          <Paragraph>
            <strong>Optimization insights:</strong>
          </Paragraph>
          <ul>
            <li>Which rules trigger most often?</li>
            <li>False positive rate by rule</li>
            <li>Alert tuning recommendations</li>
            <li>Alert fatigue metrics</li>
          </ul>
        </Card>
      </Space>
    </div>
  );
};

export default Alerts;

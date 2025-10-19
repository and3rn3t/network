/**
 * Reports page - Data export and custom reports
 */

import { ExportOutlined } from "@ant-design/icons";
import { Card, Space, Typography } from "antd";
import React from "react";

const { Title, Paragraph } = Typography;

const Reports: React.FC = () => {
  return (
    <div>
      <Title level={2}>
        <ExportOutlined /> Reports & Data Export
      </Title>
      <Paragraph type="secondary">
        Generate custom reports and export data for external analysis
      </Paragraph>

      <Space direction="vertical" size="large" style={{ width: "100%" }}>
        <Card title="📄 Custom Report Builder">
          <Paragraph>
            <strong>Coming in Phase 5.6:</strong>
          </Paragraph>
          <ul>
            <li>Flexible metric and time range selection</li>
            <li>Multi-format export (CSV, JSON, PDF)</li>
            <li>Scheduled report generation</li>
            <li>Report templates library</li>
          </ul>
        </Card>

        <Card title="📊 Data Liberation">
          <Paragraph>
            <strong>Your data, your way:</strong>
          </Paragraph>
          <ul>
            <li>Export historical device metrics</li>
            <li>Download alert history</li>
            <li>API access for programmatic data retrieval</li>
            <li>Integration with external tools (Excel, Tableau, etc.)</li>
          </ul>
        </Card>

        <Card title="⏰ Scheduled Reports">
          <Paragraph>
            <strong>Automation:</strong>
          </Paragraph>
          <ul>
            <li>Daily/weekly/monthly scheduled reports</li>
            <li>Email delivery</li>
            <li>Executive summary templates</li>
            <li>SLA compliance reports</li>
          </ul>
        </Card>
      </Space>
    </div>
  );
};

export default Reports;

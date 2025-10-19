/**
 * Reports page - Data export and custom reports
 */

import { MaterialCard } from "@/components/MaterialCard";
import { ExportOutlined } from "@ant-design/icons";
import { Space, Typography } from "antd";
import React from "react";

const { Paragraph } = Typography;

const Reports: React.FC = () => {
  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-header-title">
          <ExportOutlined style={{ marginRight: 12 }} />
          Reports & Data Export
        </h1>
        <p className="page-header-description">
          Generate custom reports and export data for external analysis
        </p>
      </div>

      <Space direction="vertical" size="large" style={{ width: "100%" }}>
        <MaterialCard title="📄 Custom Report Builder" elevation={1}>
          <Paragraph>
            <strong>Coming in Phase 5.6:</strong>
          </Paragraph>
          <ul>
            <li>Flexible metric and time range selection</li>
            <li>Multi-format export (CSV, JSON, PDF)</li>
            <li>Scheduled report generation</li>
            <li>Report templates library</li>
          </ul>
        </MaterialCard>

        <MaterialCard title="📊 Data Liberation" elevation={1}>
          <Paragraph>
            <strong>Your data, your way:</strong>
          </Paragraph>
          <ul>
            <li>Export historical device metrics</li>
            <li>Download alert history</li>
            <li>API access for programmatic data retrieval</li>
            <li>Integration with external tools (Excel, Tableau, etc.)</li>
          </ul>
        </MaterialCard>

        <MaterialCard title="⏰ Scheduled Reports" elevation={1}>
          <Paragraph>
            <strong>Automation:</strong>
          </Paragraph>
          <ul>
            <li>Daily/weekly/monthly scheduled reports</li>
            <li>Email delivery</li>
            <li>Executive summary templates</li>
            <li>SLA compliance reports</li>
          </ul>
        </MaterialCard>
      </Space>
    </div>
  );
};

export default Reports;

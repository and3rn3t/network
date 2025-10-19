/**
 * Alerts page - Alert intelligence and pattern analysis
 */

import { MaterialCard } from "@/components/MaterialCard";
import { BellOutlined } from "@ant-design/icons";
import { Space } from "antd";
import React from "react";

const Alerts: React.FC = () => {
  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-header-title">
          <BellOutlined style={{ marginRight: 12 }} />
          Alert Intelligence
        </h1>
        <p className="page-header-description">
          Reduce alert fatigue with intelligent pattern analysis
        </p>
      </div>

      <Space direction="vertical" size="large" style={{ width: "100%" }}>
        <MaterialCard elevation={1} title="📈 Alert Analytics">
          <p className="md-body-large">
            <strong>Coming in Phase 5.5:</strong>
          </p>
          <ul className="mt-sm">
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
          <ul className="mt-sm">
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
          <ul className="mt-sm">
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

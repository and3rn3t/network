/**
 * Settings page - Configuration and preferences
 */

import { MaterialCard } from "@/components/MaterialCard";
import { SettingOutlined } from "@ant-design/icons";
import { Typography } from "antd";
import React from "react";

const { Paragraph } = Typography;

const Settings: React.FC = () => {
  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-header-title">
          <SettingOutlined style={{ marginRight: 12 }} />
          Settings
        </h1>
        <p className="page-header-description">
          Configure alert rules, notification channels, and preferences
        </p>
      </div>

      <MaterialCard title="⚙️ Configuration" elevation={1} style={{ marginTop: 24 }}>
        <Paragraph>
          <strong>Settings coming soon:</strong>
        </Paragraph>
        <ul>
          <li>Alert rule management</li>
          <li>Notification channel configuration</li>
          <li>User preferences</li>
          <li>API key management</li>
        </ul>
      </MaterialCard>
    </div>
  );
};

export default Settings;

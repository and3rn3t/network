/**
 * Settings page - Configuration and preferences
 */

import { SettingOutlined } from "@ant-design/icons";
import { Card, Typography } from "antd";
import React from "react";

const { Title, Paragraph } = Typography;

const Settings: React.FC = () => {
  return (
    <div>
      <Title level={2}>
        <SettingOutlined /> Settings
      </Title>
      <Paragraph type="secondary">
        Configure alert rules, notification channels, and preferences
      </Paragraph>

      <Card title="⚙️ Configuration" style={{ marginTop: 24 }}>
        <Paragraph>
          <strong>Settings coming soon:</strong>
        </Paragraph>
        <ul>
          <li>Alert rule management</li>
          <li>Notification channel configuration</li>
          <li>User preferences</li>
          <li>API key management</li>
        </ul>
      </Card>
    </div>
  );
};

export default Settings;

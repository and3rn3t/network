/**
 * Settings page - Configuration and preferences
 */

import { MaterialCard } from "@/components/MaterialCard";
import {
  BellOutlined,
  ExperimentOutlined,
  NotificationOutlined,
  SettingOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { Divider, Tabs, Typography } from "antd";
import React, { useState } from "react";

const { Text } = Typography;

// Tab components (will be implemented separately)
const AlertRulesTab = React.lazy(
  () => import("@/components/settings/AlertRulesTab")
);
const NotificationChannelsTab = React.lazy(
  () => import("@/components/settings/NotificationChannelsTab")
);
const UserPreferencesTab = React.lazy(
  () => import("@/components/settings/UserPreferencesTab")
);
const AdvancedTab = React.lazy(
  () => import("@/components/settings/AdvancedTab")
);

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState("alert-rules");

  const tabItems = [
    {
      key: "alert-rules",
      label: (
        <span>
          <BellOutlined />
          Alert Rules
        </span>
      ),
      children: (
        <React.Suspense
          fallback={
            <MaterialCard elevation={1}>
              <Text>Loading...</Text>
            </MaterialCard>
          }
        >
          <AlertRulesTab />
        </React.Suspense>
      ),
    },
    {
      key: "notification-channels",
      label: (
        <span>
          <NotificationOutlined />
          Notification Channels
        </span>
      ),
      children: (
        <React.Suspense
          fallback={
            <MaterialCard elevation={1}>
              <Text>Loading...</Text>
            </MaterialCard>
          }
        >
          <NotificationChannelsTab />
        </React.Suspense>
      ),
    },
    {
      key: "preferences",
      label: (
        <span>
          <UserOutlined />
          User Preferences
        </span>
      ),
      children: (
        <React.Suspense
          fallback={
            <MaterialCard elevation={1}>
              <Text>Loading...</Text>
            </MaterialCard>
          }
        >
          <UserPreferencesTab />
        </React.Suspense>
      ),
    },
    {
      key: "advanced",
      label: (
        <span>
          <ExperimentOutlined />
          Advanced
        </span>
      ),
      children: (
        <React.Suspense
          fallback={
            <MaterialCard elevation={1}>
              <Text>Loading...</Text>
            </MaterialCard>
          }
        >
          <AdvancedTab />
        </React.Suspense>
      ),
    },
  ];

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

      <Divider style={{ margin: "24px 0" }} />

      {/* Settings Tabs */}
      <MaterialCard elevation={1}>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={tabItems}
          size="large"
          style={{ marginTop: -16 }}
        />
      </MaterialCard>
    </div>
  );
};

export default Settings;

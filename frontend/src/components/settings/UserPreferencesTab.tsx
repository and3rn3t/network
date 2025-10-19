/**
 * User Preferences Tab Component
 * Manages user interface preferences (stored in local storage)
 */

import { MaterialCard } from "@/components/MaterialCard";
import type { UserPreferences } from "@/types/settings";
import { DEFAULT_PREFERENCES } from "@/types/settings";
import { SaveOutlined } from "@ant-design/icons";
import {
  Button,
  Col,
  Divider,
  Form,
  InputNumber,
  Row,
  Select,
  Space,
  Switch,
  Typography,
  message,
} from "antd";
import React, { useEffect, useState } from "react";

const { Text } = Typography;
const { Option } = Select;

const STORAGE_KEY = "unifi_monitor_preferences";

const UserPreferencesTab: React.FC = () => {
  const [form] = Form.useForm();
  const [preferences, setPreferences] =
    useState<UserPreferences>(DEFAULT_PREFERENCES);
  const [hasChanges, setHasChanges] = useState(false);

  // Load preferences from local storage on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setPreferences(parsed);
        form.setFieldsValue(parsed);
      } catch {
        message.error("Failed to load saved preferences");
      }
    } else {
      form.setFieldsValue(DEFAULT_PREFERENCES);
    }
  }, [form]);

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const updated: UserPreferences = values;

      // Save to local storage
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      setPreferences(updated);
      setHasChanges(false);

      message.success("Preferences saved successfully");

      // Optionally reload page to apply theme changes
      if (updated.theme !== preferences.theme) {
        message.info("Reload the page to apply theme changes");
      }
    } catch {
      message.error("Please fix validation errors before saving");
    }
  };

  const handleReset = () => {
    form.setFieldsValue(DEFAULT_PREFERENCES);
    setHasChanges(true);
    message.info("Preferences reset to defaults (not saved yet)");
  };

  const handleValuesChange = () => {
    setHasChanges(true);
  };

  return (
    <Space direction="vertical" size="large" style={{ width: "100%" }}>
      <Form form={form} layout="vertical" onValuesChange={handleValuesChange}>
        {/* Appearance Section */}
        <MaterialCard title="🎨 Appearance" elevation={1}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Theme"
                name="theme"
                extra="Choose your preferred color scheme"
              >
                <Select size="large">
                  <Option value="light">☀️ Light</Option>
                  <Option value="dark">🌙 Dark</Option>
                  <Option value="auto">🔄 Auto (System)</Option>
                </Select>
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item
                label="Time Format"
                name="timeFormat"
                extra="Display time in 12-hour or 24-hour format"
              >
                <Select size="large">
                  <Option value="12h">12-hour (AM/PM)</Option>
                  <Option value="24h">24-hour</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="Date Format"
            name="dateFormat"
            extra="Choose how dates are displayed throughout the app"
          >
            <Select size="large">
              <Option value="YYYY-MM-DD">YYYY-MM-DD (2024-01-15)</Option>
              <Option value="MM/DD/YYYY">MM/DD/YYYY (01/15/2024)</Option>
              <Option value="DD/MM/YYYY">DD/MM/YYYY (15/01/2024)</Option>
              <Option value="MMM DD, YYYY">MMM DD, YYYY (Jan 15, 2024)</Option>
            </Select>
          </Form.Item>
        </MaterialCard>

        <Divider />

        {/* Data & Performance Section */}
        <MaterialCard title="⚡ Data & Performance" elevation={1}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Default Time Range (hours)"
                name="defaultTimeRange"
                rules={[
                  { required: true, message: "Required" },
                  {
                    type: "number",
                    min: 1,
                    max: 168,
                    message: "Must be 1-168 hours",
                  },
                ]}
                extra="Default time range for historical data views"
              >
                <InputNumber
                  min={1}
                  max={168}
                  size="large"
                  style={{ width: "100%" }}
                />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item
                label="Auto Refresh Interval (seconds)"
                name="refreshInterval"
                rules={[
                  { required: true, message: "Required" },
                  {
                    type: "number",
                    min: 10,
                    max: 300,
                    message: "Must be 10-300 seconds",
                  },
                ]}
                extra="How often to refresh dashboard data"
              >
                <InputNumber
                  min={10}
                  max={300}
                  size="large"
                  style={{ width: "100%" }}
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="Table Page Size"
            name="tablePageSize"
            rules={[
              { required: true, message: "Required" },
              { type: "number", min: 5, max: 100, message: "Must be 5-100" },
            ]}
            extra="Number of rows to display per page in tables"
          >
            <InputNumber
              min={5}
              max={100}
              size="large"
              style={{ width: "100%" }}
            />
          </Form.Item>
        </MaterialCard>

        <Divider />

        {/* Notifications Section */}
        <MaterialCard title="🔔 Notifications" elevation={1}>
          <Space direction="vertical" size="middle" style={{ width: "100%" }}>
            <Form.Item
              label="Browser Notifications"
              name="enableNotifications"
              valuePropName="checked"
            >
              <Switch
                checkedChildren="Enabled"
                unCheckedChildren="Disabled"
                size="default"
              />
            </Form.Item>

            <Text type="secondary">
              Allow the application to show browser notifications for critical
              alerts
            </Text>

            <Form.Item
              label="Notification Sounds"
              name="enableSounds"
              valuePropName="checked"
            >
              <Switch
                checkedChildren="Enabled"
                unCheckedChildren="Disabled"
                size="default"
              />
            </Form.Item>

            <Text type="secondary">
              Play audio alerts when critical notifications appear
            </Text>
          </Space>
        </MaterialCard>

        <Divider />

        {/* Dashboard Widgets Section */}
        <MaterialCard title="📊 Dashboard Widgets" elevation={1}>
          <Space direction="vertical" size="middle" style={{ width: "100%" }}>
            <Text type="secondary">
              Choose which widgets to display on the dashboard
            </Text>

            <Form.Item
              label="Show Alerts Widget"
              name={["dashboardWidgets", "showAlerts"]}
              valuePropName="checked"
            >
              <Switch
                checkedChildren="Visible"
                unCheckedChildren="Hidden"
                size="default"
              />
            </Form.Item>

            <Form.Item
              label="Show Performance Widget"
              name={["dashboardWidgets", "showPerformance"]}
              valuePropName="checked"
            >
              <Switch
                checkedChildren="Visible"
                unCheckedChildren="Hidden"
                size="default"
              />
            </Form.Item>

            <Form.Item
              label="Show Topology Widget"
              name={["dashboardWidgets", "showTopology"]}
              valuePropName="checked"
            >
              <Switch
                checkedChildren="Visible"
                unCheckedChildren="Hidden"
                size="default"
              />
            </Form.Item>

            <Form.Item
              label="Show Recent Activity Widget"
              name={["dashboardWidgets", "showRecent"]}
              valuePropName="checked"
            >
              <Switch
                checkedChildren="Visible"
                unCheckedChildren="Hidden"
                size="default"
              />
            </Form.Item>
          </Space>
        </MaterialCard>

        <Divider />

        {/* Action Buttons */}
        <Row justify="end" gutter={16}>
          <Col>
            <Button onClick={handleReset} size="large">
              Reset to Defaults
            </Button>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSave}
              disabled={!hasChanges}
              size="large"
            >
              Save Preferences
            </Button>
          </Col>
        </Row>
      </Form>
    </Space>
  );
};

export default UserPreferencesTab;

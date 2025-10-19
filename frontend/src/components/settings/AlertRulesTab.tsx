/**
 * Alert Rules Tab Component
 * Manages alert rule CRUD operations
 */

import {
  useAlertRules,
  useCreateAlertRule,
  useDeleteAlertRule,
  useNotificationChannels,
  useUpdateAlertRule,
} from "@/hooks/useSettings";
import type { AlertRule, AlertRuleFormData } from "@/types/settings";
import {
  CONDITIONS,
  METRIC_NAMES,
  RULE_TYPES,
  SEVERITIES,
} from "@/types/settings";
import {
  DeleteOutlined,
  EditOutlined,
  PlusOutlined,
  WarningOutlined,
} from "@ant-design/icons";
import {
  Alert,
  Badge,
  Button,
  Col,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Row,
  Select,
  Space,
  Switch,
  Table,
  Tag,
  Typography,
  message,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import React, { useState } from "react";

const { Text } = Typography;
const { Option } = Select;

const AlertRulesTab: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<AlertRule | null>(null);
  const [form] = Form.useForm();

  // Fetch data
  const { data: rulesResponse, isLoading, error } = useAlertRules();
  const { data: channelsResponse } = useNotificationChannels();

  // Mutations
  const createMutation = useCreateAlertRule();
  const updateMutation = useUpdateAlertRule();
  const deleteMutation = useDeleteAlertRule();

  const rules = rulesResponse?.rules || [];
  const channels = channelsResponse?.channels || [];

  const handleCreate = () => {
    setEditingRule(null);
    form.resetFields();
    form.setFieldsValue({
      enabled: true,
      cooldown_minutes: 60,
      rule_type: "threshold",
      condition: "gte",
      severity: "warning",
      notification_channels: [],
    });
    setIsModalOpen(true);
  };

  const handleEdit = (rule: AlertRule) => {
    setEditingRule(rule);
    form.setFieldsValue(rule);
    setIsModalOpen(true);
  };

  const handleDelete = async (ruleId: number) => {
    try {
      await deleteMutation.mutateAsync(ruleId);
      message.success("Alert rule deleted successfully");
    } catch {
      message.error("Failed to delete alert rule");
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const formData: AlertRuleFormData = values;

      if (editingRule) {
        await updateMutation.mutateAsync({
          id: editingRule.id!,
          data: formData,
        });
        message.success("Alert rule updated successfully");
      } else {
        await createMutation.mutateAsync(formData);
        message.success("Alert rule created successfully");
      }

      setIsModalOpen(false);
      form.resetFields();
    } catch (err) {
      if (err instanceof Error) {
        message.error(`Failed to save alert rule: ${err.message}`);
      }
    }
  };

  const getSeverityColor = (severity: string) => {
    const severityConfig = SEVERITIES.find((s) => s.value === severity);
    return severityConfig?.color || "#666";
  };

  const columns: ColumnsType<AlertRule> = [
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
      render: (text: string, record: AlertRule) => (
        <Space>
          <Text strong>{text}</Text>
          {!record.enabled && <Tag color="default">Disabled</Tag>}
        </Space>
      ),
    },
    {
      title: "Type",
      dataIndex: "rule_type",
      key: "rule_type",
      render: (type: string) => {
        const config = RULE_TYPES.find((t) => t.value === type);
        return <Tag>{config?.label || type}</Tag>;
      },
    },
    {
      title: "Metric",
      dataIndex: "metric_name",
      key: "metric_name",
      render: (metric: string) => {
        if (!metric) return <Text type="secondary">-</Text>;
        const config = METRIC_NAMES.find((m) => m.value === metric);
        return <Text>{config?.label || metric}</Text>;
      },
    },
    {
      title: "Condition",
      key: "condition",
      render: (_, record: AlertRule) => {
        if (record.rule_type !== "threshold") {
          return <Text type="secondary">-</Text>;
        }
        const condition = CONDITIONS.find((c) => c.value === record.condition);
        return (
          <Text>
            {condition?.label || record.condition} {record.threshold}
          </Text>
        );
      },
    },
    {
      title: "Severity",
      dataIndex: "severity",
      key: "severity",
      render: (severity: string) => {
        const config = SEVERITIES.find((s) => s.value === severity);
        return (
          <Badge
            color={getSeverityColor(severity)}
            text={config?.label || severity}
          />
        );
      },
    },
    {
      title: "Channels",
      dataIndex: "notification_channels",
      key: "notification_channels",
      render: (channelIds: string[]) => (
        <Text type="secondary">{channelIds.length} channel(s)</Text>
      ),
    },
    {
      title: "Status",
      dataIndex: "enabled",
      key: "enabled",
      render: (enabled: boolean) =>
        enabled ? (
          <Tag color="success">Enabled</Tag>
        ) : (
          <Tag color="default">Disabled</Tag>
        ),
    },
    {
      title: "Actions",
      key: "actions",
      width: 150,
      render: (_, record: AlertRule) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            size="small"
          >
            Edit
          </Button>
          <Popconfirm
            title="Delete Alert Rule"
            description="Are you sure you want to delete this alert rule?"
            onConfirm={() => handleDelete(record.id!)}
            okText="Delete"
            cancelText="Cancel"
            okButtonProps={{ danger: true }}
          >
            <Button type="text" danger icon={<DeleteOutlined />} size="small">
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  if (error) {
    return (
      <Alert
        message="Error Loading Alert Rules"
        description="Failed to load alert rules. Please try again later."
        type="error"
        showIcon
      />
    );
  }

  return (
    <>
      <Space direction="vertical" size="large" style={{ width: "100%" }}>
        {/* Header Actions */}
        <Row justify="space-between" align="middle">
          <Col>
            <Text type="secondary">
              {rules.length} alert rule(s) configured
            </Text>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreate}
            >
              Create Alert Rule
            </Button>
          </Col>
        </Row>

        {/* Alert Rules Table */}
        <Table
          columns={columns}
          dataSource={rules}
          rowKey="id"
          loading={isLoading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} rules`,
          }}
        />
      </Space>

      {/* Create/Edit Modal */}
      <Modal
        title={editingRule ? "Edit Alert Rule" : "Create Alert Rule"}
        open={isModalOpen}
        onOk={handleSubmit}
        onCancel={() => {
          setIsModalOpen(false);
          form.resetFields();
        }}
        width={700}
        okText={editingRule ? "Update" : "Create"}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 24 }}>
          <Row gutter={16}>
            <Col span={16}>
              <Form.Item
                label="Rule Name"
                name="name"
                rules={[
                  { required: true, message: "Please enter a rule name" },
                  {
                    min: 3,
                    max: 100,
                    message: "Name must be 3-100 characters",
                  },
                ]}
              >
                <Input placeholder="e.g., High CPU Usage Alert" />
              </Form.Item>
            </Col>

            <Col span={8}>
              <Form.Item label="Enabled" name="enabled" valuePropName="checked">
                <Switch
                  checkedChildren="Enabled"
                  unCheckedChildren="Disabled"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item label="Description" name="description">
            <Input.TextArea
              rows={2}
              placeholder="Optional description of what this rule monitors"
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Rule Type"
                name="rule_type"
                rules={[{ required: true, message: "Please select a type" }]}
              >
                <Select placeholder="Select rule type">
                  {RULE_TYPES.map((type) => (
                    <Option key={type.value} value={type.value}>
                      {type.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item
                label="Severity"
                name="severity"
                rules={[{ required: true, message: "Please select severity" }]}
              >
                <Select placeholder="Select severity">
                  {SEVERITIES.map((severity) => (
                    <Option key={severity.value} value={severity.value}>
                      <Badge color={severity.color} text={severity.label} />
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            noStyle
            shouldUpdate={(prevValues, currentValues) =>
              prevValues.rule_type !== currentValues.rule_type
            }
          >
            {({ getFieldValue }) =>
              getFieldValue("rule_type") === "threshold" && (
                <>
                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item
                        label="Metric"
                        name="metric_name"
                        rules={[
                          {
                            required: true,
                            message: "Please select a metric",
                          },
                        ]}
                      >
                        <Select placeholder="Select metric to monitor">
                          {METRIC_NAMES.map((metric) => (
                            <Option key={metric.value} value={metric.value}>
                              {metric.label}
                            </Option>
                          ))}
                        </Select>
                      </Form.Item>
                    </Col>

                    <Col span={12}>
                      <Form.Item
                        label="Condition"
                        name="condition"
                        rules={[
                          {
                            required: true,
                            message: "Please select a condition",
                          },
                        ]}
                      >
                        <Select placeholder="Select condition">
                          {CONDITIONS.map((condition) => (
                            <Option
                              key={condition.value}
                              value={condition.value}
                            >
                              {condition.label}
                            </Option>
                          ))}
                        </Select>
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item
                    label="Threshold Value"
                    name="threshold"
                    rules={[
                      {
                        required: true,
                        message: "Please enter a threshold value",
                      },
                    ]}
                  >
                    <InputNumber
                      style={{ width: "100%" }}
                      placeholder="e.g., 80"
                      min={0}
                      max={10000}
                    />
                  </Form.Item>
                </>
              )
            }
          </Form.Item>

          <Form.Item
            label="Notification Channels"
            name="notification_channels"
            rules={[
              {
                required: true,
                message: "Please select at least one notification channel",
              },
            ]}
          >
            <Select
              mode="multiple"
              placeholder="Select channels to notify"
              notFoundContent={
                <Text type="secondary">
                  No channels configured. Create channels in the Notification
                  Channels tab.
                </Text>
              }
            >
              {channels
                .filter((ch) => ch.enabled)
                .map((channel) => (
                  <Option key={channel.id} value={channel.id}>
                    {channel.name} ({channel.channel_type})
                  </Option>
                ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="Cooldown Period (minutes)"
            name="cooldown_minutes"
            rules={[
              {
                required: true,
                message: "Please enter a cooldown period",
              },
            ]}
            extra="Time to wait before re-alerting for the same condition"
          >
            <InputNumber
              style={{ width: "100%" }}
              min={0}
              max={10080}
              placeholder="e.g., 60"
            />
          </Form.Item>

          <Alert
            message="Important"
            description="Alert rules are evaluated every minute. Cooldown prevents alert spam for recurring conditions. Disabled rules are not evaluated and won't trigger alerts."
            type="info"
            icon={<WarningOutlined />}
            showIcon
            style={{ marginTop: 16 }}
          />
        </Form>
      </Modal>
    </>
  );
};

export default AlertRulesTab;

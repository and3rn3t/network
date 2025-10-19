/**
 * Notification Channels Tab Component
 * Manages notification channel configuration
 */

import {
  useCreateNotificationChannel,
  useDeleteNotificationChannel,
  useNotificationChannels,
  useTestNotificationChannel,
  useUpdateNotificationChannel,
} from "@/hooks/useSettings";
import type {
  DiscordChannelConfig,
  EmailChannelConfig,
  NotificationChannel,
  SlackChannelConfig,
  WebhookChannelConfig,
} from "@/types/settings";
import { CHANNEL_TYPES } from "@/types/settings";
import {
  DeleteOutlined,
  EditOutlined,
  PlusOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import {
  Alert,
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

const NotificationChannelsTab: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingChannel, setEditingChannel] =
    useState<NotificationChannel | null>(null);
  const [form] = Form.useForm();
  const [channelType, setChannelType] = useState<string>("email");

  // Fetch data
  const {
    data: channelsResponse,
    isLoading,
    error,
  } = useNotificationChannels();

  // Mutations
  const createMutation = useCreateNotificationChannel();
  const updateMutation = useUpdateNotificationChannel();
  const deleteMutation = useDeleteNotificationChannel();
  const testMutation = useTestNotificationChannel();

  const channels = channelsResponse?.channels || [];

  const handleCreate = () => {
    setEditingChannel(null);
    form.resetFields();
    form.setFieldsValue({
      enabled: true,
      channel_type: "email",
    });
    setChannelType("email");
    setIsModalOpen(true);
  };

  const handleEdit = (channel: NotificationChannel) => {
    setEditingChannel(channel);
    setChannelType(channel.channel_type);
    form.setFieldsValue({
      id: channel.id,
      name: channel.name,
      channel_type: channel.channel_type,
      enabled: channel.enabled,
      ...channel.config,
    });
    setIsModalOpen(true);
  };

  const handleDelete = async (channelId: string) => {
    try {
      await deleteMutation.mutateAsync(channelId);
      message.success("Notification channel deleted successfully");
    } catch {
      message.error("Failed to delete notification channel");
    }
  };

  const handleTest = async (channelId: string) => {
    try {
      await testMutation.mutateAsync(channelId);
      message.success("Test notification sent successfully");
    } catch {
      message.error("Failed to send test notification");
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();

      // Extract config based on channel type
      const config = extractConfig(values, channelType);

      const channelData: Omit<
        NotificationChannel,
        "created_at" | "updated_at"
      > = {
        id: values.id,
        name: values.name,
        channel_type: values.channel_type,
        config,
        enabled: values.enabled,
      };

      if (editingChannel) {
        await updateMutation.mutateAsync({
          id: editingChannel.id,
          data: channelData,
        });
        message.success("Notification channel updated successfully");
      } else {
        await createMutation.mutateAsync(channelData);
        message.success("Notification channel created successfully");
      }

      setIsModalOpen(false);
      form.resetFields();
    } catch (err) {
      if (err instanceof Error) {
        message.error(`Failed to save notification channel: ${err.message}`);
      }
    }
  };

  const extractConfig = (values: Record<string, unknown>, type: string) => {
    switch (type) {
      case "email":
        return {
          smtp_host: values.smtp_host,
          smtp_port: values.smtp_port,
          smtp_user: values.smtp_user,
          smtp_password: values.smtp_password,
          from_email: values.from_email,
          to_emails: (values.to_emails as string)
            ?.split(",")
            .map((e) => e.trim()),
          use_tls: values.use_tls,
        } as EmailChannelConfig;

      case "slack":
        return {
          webhook_url: values.webhook_url,
          channel: values.channel,
          username: values.username,
          icon_emoji: values.icon_emoji,
        } as SlackChannelConfig;

      case "discord":
        return {
          webhook_url: values.webhook_url,
          username: values.username,
          avatar_url: values.avatar_url,
        } as DiscordChannelConfig;

      case "webhook":
        return {
          url: values.url,
          method: values.method || "POST",
          headers: values.headers ? JSON.parse(values.headers as string) : {},
          auth_type: values.auth_type || "none",
          username: values.username,
          password: values.password,
          token: values.token,
        } as WebhookChannelConfig;

      default:
        return {};
    }
  };

  const columns: ColumnsType<NotificationChannel> = [
    {
      title: "Channel",
      key: "channel",
      render: (_, record: NotificationChannel) => {
        const typeConfig = CHANNEL_TYPES.find(
          (t) => t.value === record.channel_type
        );
        return (
          <Space>
            <span>{typeConfig?.icon}</span>
            <div>
              <Text strong>{record.name}</Text>
              <br />
              <Text type="secondary">{typeConfig?.label}</Text>
            </div>
          </Space>
        );
      },
    },
    {
      title: "ID",
      dataIndex: "id",
      key: "id",
      render: (id: string) => <Text code>{id}</Text>,
    },
    {
      title: "Configuration",
      key: "config",
      render: (_, record: NotificationChannel) => {
        const configInfo = getConfigSummary(record);
        return <Text type="secondary">{configInfo}</Text>;
      },
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
      width: 250,
      render: (_, record: NotificationChannel) => (
        <Space>
          <Button
            type="text"
            icon={<ThunderboltOutlined />}
            onClick={() => handleTest(record.id)}
            size="small"
            disabled={!record.enabled}
          >
            Test
          </Button>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            size="small"
          >
            Edit
          </Button>
          <Popconfirm
            title="Delete Channel"
            description="Are you sure? Alert rules using this channel will fail."
            onConfirm={() => handleDelete(record.id)}
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

  const getConfigSummary = (channel: NotificationChannel): string => {
    const config = channel.config;
    switch (channel.channel_type) {
      case "email":
        return `${(config as EmailChannelConfig).smtp_host}:${
          (config as EmailChannelConfig).smtp_port
        }`;
      case "slack":
      case "discord":
        return "Webhook configured";
      case "webhook":
        return (config as WebhookChannelConfig).url;
      default:
        return "Configured";
    }
  };

  if (error) {
    return (
      <Alert
        message="Error Loading Notification Channels"
        description="Failed to load notification channels. Please try again later."
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
              {channels.length} notification channel(s) configured
            </Text>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreate}
            >
              Create Channel
            </Button>
          </Col>
        </Row>

        {/* Channels Table */}
        <Table
          columns={columns}
          dataSource={channels}
          rowKey="id"
          loading={isLoading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} channels`,
          }}
        />
      </Space>

      {/* Create/Edit Modal */}
      <Modal
        title={
          editingChannel
            ? "Edit Notification Channel"
            : "Create Notification Channel"
        }
        open={isModalOpen}
        onOk={handleSubmit}
        onCancel={() => {
          setIsModalOpen(false);
          form.resetFields();
        }}
        width={700}
        okText={editingChannel ? "Update" : "Create"}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 24 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Channel ID"
                name="id"
                rules={[
                  { required: true, message: "Please enter a channel ID" },
                  {
                    pattern: /^[a-z0-9_-]+$/,
                    message: "Only lowercase letters, numbers, _ and -",
                  },
                ]}
              >
                <Input
                  placeholder="e.g., email_primary"
                  disabled={!!editingChannel}
                />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item
                label="Channel Name"
                name="name"
                rules={[
                  { required: true, message: "Please enter a channel name" },
                ]}
              >
                <Input placeholder="e.g., Primary Email" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={16}>
              <Form.Item
                label="Channel Type"
                name="channel_type"
                rules={[{ required: true, message: "Please select a type" }]}
              >
                <Select
                  placeholder="Select channel type"
                  onChange={setChannelType}
                  disabled={!!editingChannel}
                >
                  {CHANNEL_TYPES.map((type) => (
                    <Option key={type.value} value={type.value}>
                      {type.icon} {type.label}
                    </Option>
                  ))}
                </Select>
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

          {/* Channel-specific configuration */}
          {channelType === "email" && (
            <>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    label="SMTP Host"
                    name="smtp_host"
                    rules={[{ required: true, message: "Required" }]}
                  >
                    <Input placeholder="smtp.gmail.com" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    label="SMTP Port"
                    name="smtp_port"
                    rules={[{ required: true, message: "Required" }]}
                  >
                    <InputNumber
                      placeholder="587"
                      min={1}
                      max={65535}
                      style={{ width: "100%" }}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    label="SMTP User"
                    name="smtp_user"
                    rules={[{ required: true, message: "Required" }]}
                  >
                    <Input placeholder="user@example.com" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    label="SMTP Password"
                    name="smtp_password"
                    rules={[{ required: true, message: "Required" }]}
                  >
                    <Input.Password placeholder="••••••••" />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item
                label="From Email"
                name="from_email"
                rules={[
                  { required: true, message: "Required" },
                  { type: "email", message: "Invalid email" },
                ]}
              >
                <Input placeholder="alerts@example.com" />
              </Form.Item>

              <Form.Item
                label="To Emails (comma-separated)"
                name="to_emails"
                rules={[{ required: true, message: "Required" }]}
              >
                <Input.TextArea
                  rows={2}
                  placeholder="admin@example.com, ops@example.com"
                />
              </Form.Item>

              <Form.Item
                label="Use TLS"
                name="use_tls"
                valuePropName="checked"
                initialValue={true}
              >
                <Switch checkedChildren="Yes" unCheckedChildren="No" />
              </Form.Item>
            </>
          )}

          {channelType === "slack" && (
            <>
              <Form.Item
                label="Webhook URL"
                name="webhook_url"
                rules={[
                  { required: true, message: "Required" },
                  { type: "url", message: "Invalid URL" },
                ]}
              >
                <Input placeholder="https://hooks.slack.com/services/..." />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item label="Channel (optional)" name="channel">
                    <Input placeholder="#alerts" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="Username (optional)" name="username">
                    <Input placeholder="UniFi Monitor" />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item label="Icon Emoji (optional)" name="icon_emoji">
                <Input placeholder=":bell:" />
              </Form.Item>
            </>
          )}

          {channelType === "discord" && (
            <>
              <Form.Item
                label="Webhook URL"
                name="webhook_url"
                rules={[
                  { required: true, message: "Required" },
                  { type: "url", message: "Invalid URL" },
                ]}
              >
                <Input placeholder="https://discord.com/api/webhooks/..." />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item label="Username (optional)" name="username">
                    <Input placeholder="UniFi Monitor" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="Avatar URL (optional)" name="avatar_url">
                    <Input placeholder="https://..." />
                  </Form.Item>
                </Col>
              </Row>
            </>
          )}

          {channelType === "webhook" && (
            <>
              <Form.Item
                label="Webhook URL"
                name="url"
                rules={[
                  { required: true, message: "Required" },
                  { type: "url", message: "Invalid URL" },
                ]}
              >
                <Input placeholder="https://api.example.com/alerts" />
              </Form.Item>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item label="Method" name="method" initialValue="POST">
                    <Select>
                      <Option value="POST">POST</Option>
                      <Option value="PUT">PUT</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    label="Auth Type"
                    name="auth_type"
                    initialValue="none"
                  >
                    <Select>
                      <Option value="none">None</Option>
                      <Option value="basic">Basic Auth</Option>
                      <Option value="bearer">Bearer Token</Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item label="Custom Headers (JSON, optional)" name="headers">
                <Input.TextArea
                  rows={3}
                  placeholder='{"Content-Type": "application/json"}'
                />
              </Form.Item>
            </>
          )}
        </Form>
      </Modal>
    </>
  );
};

export default NotificationChannelsTab;

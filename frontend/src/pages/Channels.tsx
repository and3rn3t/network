/**
 * Notification Channels Page - Configure alert notification delivery
 */

import { MaterialCard } from "@/components/MaterialCard";
import {
  BellOutlined,
  DeleteOutlined,
  EditOutlined,
  MailOutlined,
  PlusOutlined,
  ReloadOutlined,
  SendOutlined,
  SlackOutlined,
} from "@ant-design/icons";
import {
  Button,
  Col,
  Form,
  Input,
  InputNumber,
  Modal,
  Row,
  Select,
  Space,
  Table,
  Tag,
  message,
} from "antd";
import React, { useEffect, useState } from "react";

interface NotificationChannel {
  id: number;
  name: string;
  channel_type: string;
  config: Record<string, any>;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

const Channels: React.FC = () => {
  const [channels, setChannels] = useState<NotificationChannel[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingChannel, setEditingChannel] =
    useState<NotificationChannel | null>(null);
  const [channelType, setChannelType] = useState<string>("email");
  const [form] = Form.useForm();

  const fetchChannels = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/channels");
      const data = await response.json();
      setChannels(data.channels || []);
    } catch (error) {
      message.error("Failed to fetch channels");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChannels();
  }, []);

  const handleCreate = () => {
    setEditingChannel(null);
    setChannelType("email");
    form.resetFields();
    form.setFieldsValue({ channel_type: "email", enabled: true });
    setModalVisible(true);
  };

  const handleEdit = (channel: NotificationChannel) => {
    setEditingChannel(channel);
    setChannelType(channel.channel_type);
    form.setFieldsValue({
      name: channel.name,
      channel_type: channel.channel_type,
      enabled: channel.enabled,
      ...channel.config,
    });
    setModalVisible(true);
  };

  const handleDelete = async (channelId: number) => {
    Modal.confirm({
      title: "Delete Notification Channel",
      content:
        "Are you sure you want to delete this channel? This action cannot be undone.",
      okText: "Delete",
      okType: "danger",
      onOk: async () => {
        try {
          const response = await fetch(
            `http://localhost:8000/api/channels/${channelId}`,
            {
              method: "DELETE",
            }
          );
          if (response.ok) {
            message.success("Channel deleted successfully");
            fetchChannels();
          } else {
            message.error("Failed to delete channel");
          }
        } catch (error) {
          message.error("Failed to delete channel");
        }
      },
    });
  };

  const handleTest = async (channelId: number) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/channels/${channelId}/test`,
        {
          method: "POST",
        }
      );
      if (response.ok) {
        message.success("Test notification sent");
      } else {
        message.error("Failed to send test notification");
      }
    } catch (error) {
      message.error("Failed to send test notification");
    }
  };

  const handleSubmit = async (values: any) => {
    try {
      // Build config object based on channel type
      const config: Record<string, any> = {};
      if (channelType === "email") {
        config.smtp_host = values.smtp_host;
        config.smtp_port = values.smtp_port;
        config.smtp_username = values.smtp_username;
        config.smtp_password = values.smtp_password;
        config.from_email = values.from_email;
        config.to_emails = values.to_emails;
        config.min_severity = values.min_severity || "info";
      } else if (channelType === "slack") {
        config.webhook_url = values.webhook_url;
        config.min_severity = values.min_severity || "info";
      } else if (channelType === "discord") {
        config.webhook_url = values.webhook_url;
        config.min_severity = values.min_severity || "info";
      } else if (channelType === "webhook") {
        config.url = values.url;
        config.method = values.method || "POST";
        config.headers = values.headers || {};
        config.min_severity = values.min_severity || "info";
      }

      const payload = {
        name: values.name,
        channel_type: channelType,
        config,
        enabled: values.enabled !== false,
      };

      const url = editingChannel
        ? `http://localhost:8000/api/channels/${editingChannel.id}`
        : "http://localhost:8000/api/channels";
      const method = editingChannel ? "PUT" : "POST";

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        message.success(
          `Channel ${editingChannel ? "updated" : "created"} successfully`
        );
        setModalVisible(false);
        fetchChannels();
      } else {
        message.error(
          `Failed to ${editingChannel ? "update" : "create"} channel`
        );
      }
    } catch (error) {
      message.error(
        `Failed to ${editingChannel ? "update" : "create"} channel`
      );
    }
  };

  const getChannelIcon = (type: string) => {
    switch (type) {
      case "email":
        return <MailOutlined />;
      case "slack":
        return <SlackOutlined />;
      case "discord":
      case "webhook":
        return <BellOutlined />;
      default:
        return <BellOutlined />;
    }
  };

  const columns = [
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
      render: (name: string, record: NotificationChannel) => (
        <div>
          <div style={{ fontWeight: 500 }}>
            {getChannelIcon(record.channel_type)} {name}
          </div>
          <div style={{ fontSize: 12, color: "rgba(0,0,0,0.45)" }}>
            {record.channel_type.toUpperCase()}
          </div>
        </div>
      ),
    },
    {
      title: "Configuration",
      dataIndex: "config",
      key: "config",
      render: (config: Record<string, any>, record: NotificationChannel) => {
        if (record.channel_type === "email") {
          return (
            <div>
              <div style={{ fontSize: 12 }}>
                {config.smtp_host}:{config.smtp_port}
              </div>
              <div style={{ fontSize: 11, color: "rgba(0,0,0,0.45)" }}>
                To: {config.to_emails}
              </div>
            </div>
          );
        } else if (
          record.channel_type === "slack" ||
          record.channel_type === "discord"
        ) {
          return (
            <div style={{ fontSize: 12, color: "rgba(0,0,0,0.45)" }}>
              Webhook configured
            </div>
          );
        } else {
          return (
            <div style={{ fontSize: 12, color: "rgba(0,0,0,0.45)" }}>
              {config.url || "Custom webhook"}
            </div>
          );
        }
      },
    },
    {
      title: "Min Severity",
      dataIndex: "config",
      key: "min_severity",
      width: 120,
      render: (config: Record<string, any>) => (
        <Tag
          color={
            config.min_severity === "critical"
              ? "error"
              : config.min_severity === "warning"
              ? "warning"
              : "processing"
          }
        >
          {(config.min_severity || "info").toUpperCase()}
        </Tag>
      ),
    },
    {
      title: "Status",
      dataIndex: "enabled",
      key: "enabled",
      width: 100,
      render: (enabled: boolean) => (
        <Tag color={enabled ? "success" : "default"}>
          {enabled ? "Enabled" : "Disabled"}
        </Tag>
      ),
    },
    {
      title: "Actions",
      key: "actions",
      width: 220,
      render: (_: unknown, record: NotificationChannel) => (
        <Space>
          <Button
            size="small"
            icon={<SendOutlined />}
            onClick={() => handleTest(record.id)}
          >
            Test
          </Button>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Edit
          </Button>
          <Button
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  const emailCount = channels.filter((c) => c.channel_type === "email").length;
  const slackCount = channels.filter((c) => c.channel_type === "slack").length;
  const webhookCount = channels.filter(
    (c) => c.channel_type === "webhook" || c.channel_type === "discord"
  ).length;

  const renderConfigFields = () => {
    if (channelType === "email") {
      return (
        <>
          <Row gutter={16}>
            <Col span={16}>
              <Form.Item
                label="SMTP Host"
                name="smtp_host"
                rules={[{ required: true, message: "Please enter SMTP host" }]}
              >
                <Input placeholder="smtp.gmail.com" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="SMTP Port"
                name="smtp_port"
                rules={[{ required: true }]}
              >
                <InputNumber style={{ width: "100%" }} placeholder="587" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="SMTP Username"
                name="smtp_username"
                rules={[{ required: true }]}
              >
                <Input placeholder="your-email@gmail.com" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="SMTP Password"
                name="smtp_password"
                rules={[{ required: true }]}
              >
                <Input.Password placeholder="App password" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item
            label="From Email"
            name="from_email"
            rules={[{ required: true, type: "email" }]}
          >
            <Input placeholder="alerts@yourcompany.com" />
          </Form.Item>
          <Form.Item
            label="To Emails (comma-separated)"
            name="to_emails"
            rules={[{ required: true }]}
          >
            <Input placeholder="admin@yourcompany.com, team@yourcompany.com" />
          </Form.Item>
        </>
      );
    } else if (channelType === "slack" || channelType === "discord") {
      return (
        <Form.Item
          label="Webhook URL"
          name="webhook_url"
          rules={[
            {
              required: true,
              type: "url",
              message: "Please enter valid webhook URL",
            },
          ]}
        >
          <Input.TextArea
            rows={3}
            placeholder={
              channelType === "slack"
                ? "https://hooks.slack.com/services/..."
                : "https://discord.com/api/webhooks/..."
            }
          />
        </Form.Item>
      );
    } else if (channelType === "webhook") {
      return (
        <>
          <Form.Item
            label="Webhook URL"
            name="url"
            rules={[{ required: true, type: "url" }]}
          >
            <Input placeholder="https://api.example.com/webhooks/alerts" />
          </Form.Item>
          <Form.Item label="HTTP Method" name="method">
            <Select defaultValue="POST">
              <Select.Option value="POST">POST</Select.Option>
              <Select.Option value="PUT">PUT</Select.Option>
            </Select>
          </Form.Item>
        </>
      );
    }
    return null;
  };

  return (
    <div className="dashboard-container">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-header-title">Notification Channels</h1>
          <p className="page-header-description">
            Configure where and how alert notifications are delivered
          </p>
        </div>
        <Space>
          <Button icon={<PlusOutlined />} type="primary" onClick={handleCreate}>
            Add Channel
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchChannels}
            loading={loading}
          >
            Refresh
          </Button>
        </Space>
      </div>

      {/* Summary Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={6}>
          <MaterialCard elevation={1}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 28, fontWeight: 600, color: "#1890ff" }}>
                {channels.length}
              </div>
              <div style={{ color: "rgba(0,0,0,0.45)" }}>Total Channels</div>
            </div>
          </MaterialCard>
        </Col>
        <Col xs={24} sm={6}>
          <MaterialCard elevation={1}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 28, fontWeight: 600, color: "#52c41a" }}>
                {emailCount}
              </div>
              <div style={{ color: "rgba(0,0,0,0.45)" }}>Email</div>
            </div>
          </MaterialCard>
        </Col>
        <Col xs={24} sm={6}>
          <MaterialCard elevation={1}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 28, fontWeight: 600, color: "#722ed1" }}>
                {slackCount}
              </div>
              <div style={{ color: "rgba(0,0,0,0.45)" }}>Slack</div>
            </div>
          </MaterialCard>
        </Col>
        <Col xs={24} sm={6}>
          <MaterialCard elevation={1}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 28, fontWeight: 600, color: "#fa8c16" }}>
                {webhookCount}
              </div>
              <div style={{ color: "rgba(0,0,0,0.45)" }}>Webhooks</div>
            </div>
          </MaterialCard>
        </Col>
      </Row>

      {/* Channels Table */}
      <MaterialCard elevation={2}>
        <Table
          dataSource={channels}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 20 }}
        />
      </MaterialCard>

      {/* Create/Edit Modal */}
      <Modal
        title={
          editingChannel
            ? "Edit Notification Channel"
            : "Add Notification Channel"
        }
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={700}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            label="Channel Name"
            name="name"
            rules={[{ required: true, message: "Please enter channel name" }]}
          >
            <Input placeholder="e.g., Team Email Alerts" />
          </Form.Item>

          <Form.Item
            label="Channel Type"
            name="channel_type"
            rules={[{ required: true }]}
          >
            <Select
              onChange={(value) => setChannelType(value)}
              disabled={!!editingChannel}
            >
              <Select.Option value="email">Email (SMTP)</Select.Option>
              <Select.Option value="slack">Slack</Select.Option>
              <Select.Option value="discord">Discord</Select.Option>
              <Select.Option value="webhook">Generic Webhook</Select.Option>
            </Select>
          </Form.Item>

          {renderConfigFields()}

          <Form.Item label="Minimum Severity" name="min_severity">
            <Select defaultValue="info">
              <Select.Option value="info">Info</Select.Option>
              <Select.Option value="warning">Warning</Select.Option>
              <Select.Option value="critical">Critical</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Channels;

/**
 * Advanced Tab Component
 * Manages alert muting and other advanced settings
 */

import { useDevices } from "@/hooks/useDevices";
import {
  useAlertMutes,
  useAlertRules,
  useCreateAlertMute,
  useDeleteAlertMute,
} from "@/hooks/useSettings";
import type { AlertMute, AlertMuteFormData } from "@/types/settings";
import { DeleteOutlined, PlusOutlined, StopOutlined } from "@ant-design/icons";
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
  Table,
  Tag,
  Typography,
  message,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import React, { useState } from "react";

dayjs.extend(relativeTime);

const { Text } = Typography;
const { Option } = Select;

const AdvancedTab: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();

  // Fetch data
  const { data: mutesResponse, isLoading, error } = useAlertMutes();
  const { data: rulesResponse } = useAlertRules();
  const { data: devicesResponse } = useDevices();

  // Mutations
  const createMutation = useCreateAlertMute();
  const deleteMutation = useDeleteAlertMute();

  const mutes = mutesResponse?.mutes || [];
  const rules = rulesResponse?.rules || [];
  const devices = devicesResponse?.devices || [];

  const handleCreate = () => {
    form.resetFields();
    form.setFieldsValue({
      muted_by: "admin",
    });
    setIsModalOpen(true);
  };

  const handleDelete = async (muteId: number) => {
    try {
      await deleteMutation.mutateAsync(muteId);
      message.success("Alert mute removed successfully");
    } catch {
      message.error("Failed to remove alert mute");
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      const formData: AlertMuteFormData = values;

      await createMutation.mutateAsync(formData);
      message.success("Alert mute created successfully");

      setIsModalOpen(false);
      form.resetFields();
    } catch (err) {
      if (err instanceof Error) {
        message.error(`Failed to create alert mute: ${err.message}`);
      }
    }
  };

  const columns: ColumnsType<AlertMute> = [
    {
      title: "Type",
      key: "type",
      render: (_, record: AlertMute) => {
        if (record.rule_id && record.host_id) {
          return <Tag color="orange">Rule + Host</Tag>;
        } else if (record.rule_id) {
          return <Tag color="blue">Rule</Tag>;
        } else if (record.host_id) {
          return <Tag color="green">Host</Tag>;
        }
        return <Tag color="default">Unknown</Tag>;
      },
    },
    {
      title: "Target",
      key: "target",
      render: (_, record: AlertMute) => {
        const parts: string[] = [];

        if (record.rule_id) {
          const rule = rules.find((r) => r.id === record.rule_id);
          parts.push(`Rule: ${rule?.name || record.rule_id}`);
        }

        if (record.host_id) {
          const device = devices.find((d) => d.id === record.host_id);
          parts.push(`Device: ${device?.name || record.host_id}`);
        }

        return <Text>{parts.join(" • ")}</Text>;
      },
    },
    {
      title: "Reason",
      dataIndex: "reason",
      key: "reason",
      render: (reason?: string) => (
        <Text type="secondary">{reason || "No reason provided"}</Text>
      ),
    },
    {
      title: "Muted By",
      dataIndex: "muted_by",
      key: "muted_by",
    },
    {
      title: "Expires",
      dataIndex: "expires_at",
      key: "expires_at",
      render: (expires?: string) => {
        if (!expires) {
          return <Tag color="red">Permanent</Tag>;
        }

        const expiryDate = dayjs(expires);
        const now = dayjs();

        if (expiryDate.isBefore(now)) {
          return <Tag color="default">Expired</Tag>;
        }

        const hoursRemaining = expiryDate.diff(now, "hours");
        if (hoursRemaining < 1) {
          return <Tag color="orange">Soon ({expiryDate.fromNow()})</Tag>;
        }

        return <Tag color="success">{expiryDate.fromNow()}</Tag>;
      },
    },
    {
      title: "Created",
      dataIndex: "created_at",
      key: "created_at",
      render: (created?: string) =>
        created ? (
          <Text type="secondary">
            {dayjs(created).format("MMM D, YYYY HH:mm")}
          </Text>
        ) : (
          <Text type="secondary">-</Text>
        ),
    },
    {
      title: "Actions",
      key: "actions",
      width: 120,
      render: (_, record: AlertMute) => (
        <Popconfirm
          title="Remove Mute"
          description="Are you sure you want to unmute this alert?"
          onConfirm={() => handleDelete(record.id!)}
          okText="Remove"
          cancelText="Cancel"
          okButtonProps={{ danger: true }}
        >
          <Button type="text" danger icon={<DeleteOutlined />} size="small">
            Remove
          </Button>
        </Popconfirm>
      ),
    },
  ];

  if (error) {
    return (
      <Alert
        message="Error Loading Alert Mutes"
        description="Failed to load alert mutes. Please try again later."
        type="error"
        showIcon
      />
    );
  }

  return (
    <>
      <Space direction="vertical" size="large" style={{ width: "100%" }}>
        {/* Info Alert */}
        <Alert
          message="Alert Muting"
          description="Temporarily or permanently disable alerts for specific rules, devices, or combinations. Useful during maintenance windows or troubleshooting."
          type="info"
          icon={<StopOutlined />}
          showIcon
        />

        {/* Header Actions */}
        <Row justify="space-between" align="middle">
          <Col>
            <Text type="secondary">{mutes.length} active mute(s)</Text>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreate}
            >
              Create Mute
            </Button>
          </Col>
        </Row>

        {/* Mutes Table */}
        <Table
          columns={columns}
          dataSource={mutes}
          rowKey="id"
          loading={isLoading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} mutes`,
          }}
        />
      </Space>

      {/* Create Modal */}
      <Modal
        title="Create Alert Mute"
        open={isModalOpen}
        onOk={handleSubmit}
        onCancel={() => {
          setIsModalOpen(false);
          form.resetFields();
        }}
        width={600}
        okText="Create"
        confirmLoading={createMutation.isPending}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 24 }}>
          <Alert
            message="Mute Scope"
            description="Select an alert rule, a device, or both to mute. Selecting both will only mute that specific rule for that specific device."
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />

          <Form.Item
            label="Alert Rule (optional)"
            name="rule_id"
            extra="Leave empty to mute all alerts for the selected device"
          >
            <Select
              placeholder="Select a rule to mute"
              allowClear
              showSearch
              optionFilterProp="children"
            >
              {rules.map((rule) => (
                <Option key={rule.id} value={rule.id}>
                  {rule.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="Device (optional)"
            name="host_id"
            extra="Leave empty to mute the rule for all devices"
          >
            <Select
              placeholder="Select a device to mute"
              allowClear
              showSearch
              optionFilterProp="children"
            >
              {devices.map((device) => (
                <Option key={device.id} value={device.id}>
                  {device.name} ({device.ip})
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="Duration (hours)"
            name="duration_hours"
            extra="Leave empty for permanent mute (must be manually removed)"
          >
            <InputNumber
              placeholder="e.g., 24"
              min={1}
              max={8760}
              style={{ width: "100%" }}
            />
          </Form.Item>

          <Form.Item label="Reason (optional)" name="reason">
            <Input.TextArea
              rows={3}
              placeholder="e.g., Scheduled maintenance, investigating issue..."
            />
          </Form.Item>

          <Form.Item
            label="Muted By"
            name="muted_by"
            rules={[{ required: true, message: "Please enter your name" }]}
          >
            <Input placeholder="Your name or username" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

export default AdvancedTab;

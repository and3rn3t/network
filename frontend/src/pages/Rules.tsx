/**
 * Alert Rules Page - Create and manage alert rules
 */

import { MaterialCard } from "@/components/MaterialCard";
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  DeleteOutlined,
  EditOutlined,
  PlusOutlined,
  ReloadOutlined,
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
  Switch,
  Table,
  Tag,
  message,
} from "antd";
import React, { useEffect, useState } from "react";

interface AlertRule {
  id: number;
  name: string;
  rule_type: string;
  condition: string;
  threshold_value: number;
  severity: string;
  enabled: boolean;
  cooldown_minutes: number;
  notification_channels?: string;
  created_at: string;
  updated_at: string;
}

const Rules: React.FC = () => {
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingRule, setEditingRule] = useState<AlertRule | null>(null);
  const [form] = Form.useForm();

  const fetchRules = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/rules");
      const data = await response.json();
      setRules(data.rules || []);
    } catch (error) {
      message.error("Failed to fetch rules");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const handleCreate = () => {
    setEditingRule(null);
    form.resetFields();
    form.setFieldsValue({
      enabled: true,
      cooldown_minutes: 60,
      severity: "warning",
      rule_type: "threshold",
    });
    setModalVisible(true);
  };

  const handleEdit = (rule: AlertRule) => {
    setEditingRule(rule);
    form.setFieldsValue(rule);
    setModalVisible(true);
  };

  const handleDelete = async (ruleId: number) => {
    Modal.confirm({
      title: "Delete Alert Rule",
      content:
        "Are you sure you want to delete this rule? This action cannot be undone.",
      okText: "Delete",
      okType: "danger",
      onOk: async () => {
        try {
          const response = await fetch(
            `http://localhost:8000/api/rules/${ruleId}`,
            {
              method: "DELETE",
            }
          );
          if (response.ok) {
            message.success("Rule deleted successfully");
            fetchRules();
          } else {
            message.error("Failed to delete rule");
          }
        } catch (error) {
          message.error("Failed to delete rule");
        }
      },
    });
  };

  const handleToggle = async (ruleId: number, enabled: boolean) => {
    try {
      const endpoint = enabled ? "enable" : "disable";
      const response = await fetch(
        `http://localhost:8000/api/rules/${ruleId}/${endpoint}`,
        {
          method: "POST",
        }
      );
      if (response.ok) {
        message.success(`Rule ${enabled ? "enabled" : "disabled"}`);
        fetchRules();
      } else {
        message.error(`Failed to ${enabled ? "enable" : "disable"} rule`);
      }
    } catch (error) {
      message.error(`Failed to ${enabled ? "enable" : "disable"} rule`);
    }
  };

  const handleSubmit = async (values: any) => {
    try {
      const url = editingRule
        ? `http://localhost:8000/api/rules/${editingRule.id}`
        : "http://localhost:8000/api/rules";
      const method = editingRule ? "PUT" : "POST";

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        message.success(
          `Rule ${editingRule ? "updated" : "created"} successfully`
        );
        setModalVisible(false);
        fetchRules();
      } else {
        message.error(`Failed to ${editingRule ? "update" : "create"} rule`);
      }
    } catch (error) {
      message.error(`Failed to ${editingRule ? "update" : "create"} rule`);
    }
  };

  const columns = [
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
      render: (name: string, record: AlertRule) => (
        <div>
          <div style={{ fontWeight: 500 }}>{name}</div>
          <div style={{ fontSize: 12, color: "rgba(0,0,0,0.45)" }}>
            {record.rule_type} • {record.condition}
          </div>
        </div>
      ),
    },
    {
      title: "Threshold",
      dataIndex: "threshold_value",
      key: "threshold",
      width: 120,
    },
    {
      title: "Severity",
      dataIndex: "severity",
      key: "severity",
      width: 100,
      render: (severity: string) => (
        <Tag
          color={
            severity === "critical"
              ? "error"
              : severity === "warning"
              ? "warning"
              : "processing"
          }
        >
          {severity.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: "Cooldown",
      dataIndex: "cooldown_minutes",
      key: "cooldown",
      width: 120,
      render: (minutes: number) => `${minutes} min`,
    },
    {
      title: "Status",
      dataIndex: "enabled",
      key: "enabled",
      width: 100,
      render: (enabled: boolean, record: AlertRule) => (
        <Switch
          checked={enabled}
          onChange={(checked) => handleToggle(record.id, checked)}
          checkedChildren={<CheckCircleOutlined />}
          unCheckedChildren={<CloseCircleOutlined />}
        />
      ),
    },
    {
      title: "Actions",
      key: "actions",
      width: 150,
      render: (_: unknown, record: AlertRule) => (
        <Space>
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

  const enabledCount = rules.filter((r) => r.enabled).length;

  return (
    <div className="dashboard-container">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-header-title">Alert Rules</h1>
          <p className="page-header-description">
            Configure alert rules to monitor your network health
          </p>
        </div>
        <Space>
          <Button icon={<PlusOutlined />} type="primary" onClick={handleCreate}>
            Create Rule
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchRules}
            loading={loading}
          >
            Refresh
          </Button>
        </Space>
      </div>

      {/* Summary Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <MaterialCard elevation={1}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 28, fontWeight: 600, color: "#1890ff" }}>
                {rules.length}
              </div>
              <div style={{ color: "rgba(0,0,0,0.45)" }}>Total Rules</div>
            </div>
          </MaterialCard>
        </Col>
        <Col xs={24} sm={8}>
          <MaterialCard elevation={1}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 28, fontWeight: 600, color: "#52c41a" }}>
                {enabledCount}
              </div>
              <div style={{ color: "rgba(0,0,0,0.45)" }}>Enabled</div>
            </div>
          </MaterialCard>
        </Col>
        <Col xs={24} sm={8}>
          <MaterialCard elevation={1}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 28, fontWeight: 600, color: "#8c8c8c" }}>
                {rules.length - enabledCount}
              </div>
              <div style={{ color: "rgba(0,0,0,0.45)" }}>Disabled</div>
            </div>
          </MaterialCard>
        </Col>
      </Row>

      {/* Rules Table */}
      <MaterialCard elevation={2}>
        <Table
          dataSource={rules}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 20 }}
        />
      </MaterialCard>

      {/* Create/Edit Modal */}
      <Modal
        title={editingRule ? "Edit Alert Rule" : "Create Alert Rule"}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={700}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            label="Rule Name"
            name="name"
            rules={[{ required: true, message: "Please enter rule name" }]}
          >
            <Input placeholder="e.g., High CPU Usage" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Rule Type"
                name="rule_type"
                rules={[{ required: true }]}
              >
                <Select>
                  <Select.Option value="threshold">Threshold</Select.Option>
                  <Select.Option value="status_change">
                    Status Change
                  </Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="Severity"
                name="severity"
                rules={[{ required: true }]}
              >
                <Select>
                  <Select.Option value="info">Info</Select.Option>
                  <Select.Option value="warning">Warning</Select.Option>
                  <Select.Option value="critical">Critical</Select.Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="Condition"
            name="condition"
            rules={[{ required: true, message: "Please enter condition" }]}
          >
            <Input placeholder="e.g., cpu_usage > threshold" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Threshold Value"
                name="threshold_value"
                rules={[{ required: true }]}
              >
                <InputNumber style={{ width: "100%" }} min={0} step={0.1} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="Cooldown (minutes)"
                name="cooldown_minutes"
                rules={[{ required: true }]}
              >
                <InputNumber style={{ width: "100%" }} min={1} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item label="Enabled" name="enabled" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Rules;

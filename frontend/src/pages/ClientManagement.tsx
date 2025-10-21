/**
 * ClientManagement - Manage network clients
 */

import type {
  BulkOperationItem,
  BulkOperationType,
} from "@/components/BulkOperationsModal";
import { BulkOperationsModal } from "@/components/BulkOperationsModal";
import { MaterialCard } from "@/components/MaterialCard";
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  DisconnectOutlined,
  LaptopOutlined,
  MobileOutlined,
  StopOutlined,
  TabletOutlined,
  ThunderboltOutlined,
  UserAddOutlined,
  UserOutlined,
} from "@ant-design/icons";
import {
  Badge,
  Button,
  Col,
  Form,
  Input,
  InputNumber,
  message,
  Modal,
  Row,
  Select,
  Space,
  Statistic,
  Table,
  Tag,
  Tooltip,
} from "antd";
import type { ColumnType } from "antd/es/table";
import axios from "axios";
import React, { useMemo, useState } from "react";
import "./ClientManagement.css";

const { Search } = Input;
const { confirm } = Modal;

interface Client {
  mac: string;
  name: string;
  ip: string;
  hostname: string;
  status: string;
  device_type: string;
  signal_strength: number;
  connected_device: string;
  first_seen: string;
  last_seen: string;
  blocked: boolean;
  download_limit?: number;
  upload_limit?: number;
}

const ClientManagement: React.FC = () => {
  // Sample data - in production, this would come from API
  const [clients, setClients] = useState<Client[]>([
    {
      mac: "aa:bb:cc:dd:ee:01",
      name: "John's iPhone",
      ip: "192.168.1.101",
      hostname: "johns-iphone",
      status: "active",
      device_type: "mobile",
      signal_strength: -45,
      connected_device: "Living Room AP",
      first_seen: "2025-10-15T10:30:00Z",
      last_seen: "2025-10-19T14:25:00Z",
      blocked: false,
    },
    {
      mac: "aa:bb:cc:dd:ee:02",
      name: "Office Laptop",
      ip: "192.168.1.102",
      hostname: "office-laptop",
      status: "active",
      device_type: "laptop",
      signal_strength: -52,
      connected_device: "Office AP",
      first_seen: "2025-10-10T08:00:00Z",
      last_seen: "2025-10-19T14:25:00Z",
      blocked: false,
      download_limit: 50000,
      upload_limit: 10000,
    },
    {
      mac: "aa:bb:cc:dd:ee:03",
      name: "Guest Device",
      ip: "192.168.1.103",
      hostname: "android-device",
      status: "blocked",
      device_type: "mobile",
      signal_strength: 0,
      connected_device: "",
      first_seen: "2025-10-19T12:00:00Z",
      last_seen: "2025-10-19T13:00:00Z",
      blocked: true,
    },
  ]);

  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [searchText, setSearchText] = useState("");
  const [statusFilter, setStatusFilter] = useState<string | undefined>(
    undefined
  );
  const [blockModalVisible, setBlockModalVisible] = useState(false);
  const [bandwidthModalVisible, setBandwidthModalVisible] = useState(false);
  const [guestModalVisible, setGuestModalVisible] = useState(false);
  const [currentClient, setCurrentClient] = useState<Client | null>(null);
  const [bulkModalVisible, setBulkModalVisible] = useState(false);
  const [bulkOperationType, setBulkOperationType] =
    useState<BulkOperationType>("client_block");
  const [blockForm] = Form.useForm();
  const [bandwidthForm] = Form.useForm();
  const [guestForm] = Form.useForm();

  // Filter clients based on search and status
  const filteredClients = useMemo(() => {
    return clients.filter((client: Client) => {
      const matchesSearch =
        !searchText ||
        client.name.toLowerCase().includes(searchText.toLowerCase()) ||
        client.mac.toLowerCase().includes(searchText.toLowerCase()) ||
        client.ip.toLowerCase().includes(searchText.toLowerCase()) ||
        client.hostname.toLowerCase().includes(searchText.toLowerCase());

      const matchesStatus =
        !statusFilter ||
        (statusFilter === "active" && client.status === "active") ||
        (statusFilter === "blocked" && client.blocked);

      return matchesSearch && matchesStatus;
    });
  }, [clients, searchText, statusFilter]);

  // Calculate statistics
  const stats = useMemo(() => {
    return {
      total: clients.length,
      active: clients.filter((c: Client) => c.status === "active").length,
      blocked: clients.filter((c: Client) => c.blocked).length,
      selected: selectedRowKeys.length,
    };
  }, [clients, selectedRowKeys]);

  // Handle client block
  const handleBlockClick = (client: Client) => {
    setCurrentClient(client);
    blockForm.resetFields();
    setBlockModalVisible(true);
  };

  const handleBlockSubmit = async () => {
    try {
      const values = await blockForm.validateFields();
      if (!currentClient) return;

      const duration = values.permanent ? undefined : values.duration;

      await axios.post(`/api/clients/${currentClient.mac}/block`, {
        mac: currentClient.mac,
        reason: values.reason || "Manual block from Client Management",
        duration: duration,
      });

      message.success(
        `Client ${currentClient.name} blocked${
          duration ? ` for ${duration}s` : " permanently"
        }`
      );

      // Update local state
      setClients(
        clients.map((c) =>
          c.mac === currentClient.mac
            ? { ...c, blocked: true, status: "blocked" }
            : c
        )
      );

      setBlockModalVisible(false);
      setCurrentClient(null);
      blockForm.resetFields();
    } catch (error) {
      message.error(`Failed to block client: ${error}`);
    }
  };

  // Handle client unblock
  const handleUnblock = async (client: Client) => {
    confirm({
      title: `Unblock ${client.name}?`,
      icon: <CheckCircleOutlined />,
      content: (
        <div>
          <p>This will allow the client to reconnect to the network.</p>
          <p>
            <strong>Client:</strong> {client.name} ({client.mac})
          </p>
        </div>
      ),
      okText: "Unblock",
      okType: "primary",
      cancelText: "Cancel",
      onOk: async () => {
        try {
          await axios.post(`/api/clients/${client.mac}/unblock`, {
            reason: "Manual unblock from Client Management",
          });

          message.success(`Client ${client.name} unblocked`);

          // Update local state
          setClients(
            clients.map((c) =>
              c.mac === client.mac
                ? { ...c, blocked: false, status: "active" }
                : c
            )
          );
        } catch (error) {
          message.error(`Failed to unblock client: ${error}`);
        }
      },
    });
  };

  // Handle client reconnect
  const handleReconnect = async (client: Client) => {
    confirm({
      title: `Reconnect ${client.name}?`,
      icon: <DisconnectOutlined />,
      content: (
        <div>
          <p>This will temporarily disconnect and reconnect the client.</p>
          <p>
            <strong>Client:</strong> {client.name} ({client.mac})
          </p>
        </div>
      ),
      okText: "Reconnect",
      okType: "primary",
      cancelText: "Cancel",
      onOk: async () => {
        try {
          await axios.post(`/api/clients/${client.mac}/reconnect`, {
            reason: "Manual reconnect from Client Management",
          });
          message.success(`Reconnect command sent to ${client.name}`);
        } catch (error) {
          message.error(`Failed to reconnect client: ${error}`);
        }
      },
    });
  };

  // Handle bandwidth limit
  const handleBandwidthClick = (client: Client) => {
    setCurrentClient(client);
    bandwidthForm.setFieldsValue({
      download_limit: client.download_limit || 0,
      upload_limit: client.upload_limit || 0,
    });
    setBandwidthModalVisible(true);
  };

  const handleBandwidthSubmit = async () => {
    try {
      const values = await bandwidthForm.validateFields();
      if (!currentClient) return;

      await axios.post(`/api/clients/${currentClient.mac}/bandwidth`, {
        download_limit: values.download_limit,
        upload_limit: values.upload_limit,
      });

      message.success(`Bandwidth limits updated for ${currentClient.name}`);

      // Update local state
      setClients(
        clients.map((c) =>
          c.mac === currentClient.mac
            ? {
                ...c,
                download_limit: values.download_limit,
                upload_limit: values.upload_limit,
              }
            : c
        )
      );

      setBandwidthModalVisible(false);
      setCurrentClient(null);
      bandwidthForm.resetFields();
    } catch (error) {
      message.error(`Failed to set bandwidth limits: ${error}`);
    }
  };

  // Handle guest authorization
  const handleGuestClick = (client: Client) => {
    setCurrentClient(client);
    guestForm.resetFields();
    setGuestModalVisible(true);
  };

  const handleGuestSubmit = async () => {
    try {
      const values = await guestForm.validateFields();
      if (!currentClient) return;

      await axios.post(`/api/clients/${currentClient.mac}/authorize-guest`, {
        duration: values.duration,
      });

      message.success(
        `Guest ${currentClient.name} authorized for ${values.duration} seconds`
      );

      setGuestModalVisible(false);
      setCurrentClient(null);
      guestForm.resetFields();
    } catch (error) {
      message.error(`Failed to authorize guest: ${error}`);
    }
  };

  // Handle bulk block
  const handleBulkBlock = () => {
    if (selectedRowKeys.length === 0) {
      message.warning("Please select clients to block");
      return;
    }
    setBulkOperationType("client_block");
    setBulkModalVisible(true);
  };

  // Handle bulk unblock
  const handleBulkUnblock = () => {
    if (selectedRowKeys.length === 0) {
      message.warning("Please select clients to unblock");
      return;
    }
    setBulkOperationType("client_unblock");
    setBulkModalVisible(true);
  };

  // Get bulk operation items from selected clients
  const getBulkOperationItems = (): BulkOperationItem[] => {
    return filteredClients
      .filter((client) => selectedRowKeys.includes(client.mac))
      .map((client) => ({
        key: client.mac,
        title: client.name || client.hostname || client.mac,
        description: `${client.ip} - ${getDeviceTypeName(client.device_type)}`,
        disabled: false,
      }));
  }; // Handle bulk unblock
  const handleBulkUnblock = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning("Please select clients to unblock");
      return;
    }

    confirm({
      title: `Unblock ${selectedRowKeys.length} client(s)?`,
      icon: <CheckCircleOutlined />,
      content: (
        <div>
          <p>
            This will allow {selectedRowKeys.length} client(s) to reconnect.
          </p>
        </div>
      ),
      okText: "Unblock All",
      okType: "primary",
      cancelText: "Cancel",
      onOk: async () => {
        try {
          await axios.post("/api/clients/bulk/unblock", {
            mac_addresses: selectedRowKeys,
            action: "unblock",
            reason: "Bulk unblock from Client Management",
          });

          message.success(
            `Unblock command sent to ${selectedRowKeys.length} client(s)`
          );

          // Update local state
          setClients(
            clients.map((c) =>
              selectedRowKeys.includes(c.mac)
                ? { ...c, blocked: false, status: "active" }
                : c
            )
          );

          setSelectedRowKeys([]);
        } catch (error) {
          message.error(`Failed to unblock clients: ${error}`);
        }
      },
    });
  };

  // Get device type icon
  const getDeviceIcon = (type: string) => {
    switch (type) {
      case "laptop":
        return <LaptopOutlined />;
      case "mobile":
        return <MobileOutlined />;
      case "tablet":
        return <TabletOutlined />;
      default:
        return <UserOutlined />;
    }
  };

  // Table columns
  const columns: ColumnType<Client>[] = [
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 100,
      render: (status: string, record: Client) => {
        if (record.blocked) {
          return (
            <Badge
              status="error"
              text={
                <span>
                  <StopOutlined /> Blocked
                </span>
              }
            />
          );
        }
        const statusConfig: Record<
          string,
          { color: string; icon: React.ReactNode; text: string }
        > = {
          active: {
            color: "success",
            icon: <CheckCircleOutlined />,
            text: "Active",
          },
          inactive: {
            color: "default",
            icon: <ClockCircleOutlined />,
            text: "Inactive",
          },
        };

        const config = statusConfig[status] || statusConfig.inactive;

        return (
          <Badge
            status={config.color as any}
            text={
              <span>
                {config.icon} {config.text}
              </span>
            }
          />
        );
      },
      filters: [
        { text: "Active", value: "active" },
        { text: "Blocked", value: "blocked" },
      ],
      onFilter: (value, record) =>
        value === "blocked" ? record.blocked : record.status === value,
    },
    {
      title: "Client",
      dataIndex: "name",
      key: "name",
      sorter: (a, b) => a.name.localeCompare(b.name),
      render: (name: string, record: Client) => (
        <Space>
          {getDeviceIcon(record.device_type)}
          <strong>{name}</strong>
        </Space>
      ),
    },
    {
      title: "IP Address",
      dataIndex: "ip",
      key: "ip",
      sorter: (a, b) => a.ip.localeCompare(b.ip),
    },
    {
      title: "MAC Address",
      dataIndex: "mac",
      key: "mac",
      responsive: ["lg"],
      render: (mac: string) => <code>{mac}</code>,
    },
    {
      title: "Connected To",
      dataIndex: "connected_device",
      key: "connected_device",
      responsive: ["xl"],
      render: (device: string) => device || <em>Not connected</em>,
    },
    {
      title: "Signal",
      dataIndex: "signal_strength",
      key: "signal_strength",
      responsive: ["lg"],
      render: (signal: number) => {
        if (signal === 0) return <em>N/A</em>;
        const quality =
          signal >= -50 ? "excellent" : signal >= -60 ? "good" : "fair";
        const color =
          quality === "excellent"
            ? "green"
            : quality === "good"
            ? "blue"
            : "orange";
        return (
          <Tag color={color}>
            {signal} dBm ({quality})
          </Tag>
        );
      },
    },
    {
      title: "Bandwidth Limits",
      key: "bandwidth",
      responsive: ["xl"],
      render: (_, record: Client) => {
        if (!record.download_limit && !record.upload_limit) {
          return <em>Unlimited</em>;
        }
        return (
          <div>
            {record.download_limit && (
              <div>↓ {(record.download_limit / 1000).toFixed(0)} Mbps</div>
            )}
            {record.upload_limit && (
              <div>↑ {(record.upload_limit / 1000).toFixed(0)} Mbps</div>
            )}
          </div>
        );
      },
    },
    {
      title: "Actions",
      key: "actions",
      width: 250,
      render: (_, record: Client) => (
        <Space size="small" wrap>
          {record.blocked ? (
            <Tooltip title="Unblock client">
              <Button
                type="primary"
                size="small"
                icon={<CheckCircleOutlined />}
                onClick={() => handleUnblock(record)}
              >
                Unblock
              </Button>
            </Tooltip>
          ) : (
            <Tooltip title="Block client">
              <Button
                danger
                size="small"
                icon={<StopOutlined />}
                onClick={() => handleBlockClick(record)}
              >
                Block
              </Button>
            </Tooltip>
          )}
          <Tooltip title="Reconnect client">
            <Button
              size="small"
              icon={<DisconnectOutlined />}
              onClick={() => handleReconnect(record)}
              disabled={record.status !== "active"}
            />
          </Tooltip>
          <Tooltip title="Set bandwidth limits">
            <Button
              size="small"
              icon={<ThunderboltOutlined />}
              onClick={() => handleBandwidthClick(record)}
            />
          </Tooltip>
          <Tooltip title="Authorize as guest">
            <Button
              size="small"
              icon={<UserAddOutlined />}
              onClick={() => handleGuestClick(record)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  // Row selection
  const rowSelection = {
    selectedRowKeys,
    onChange: (newSelectedRowKeys: React.Key[]) => {
      setSelectedRowKeys(newSelectedRowKeys);
    },
    selections: [
      Table.SELECTION_ALL,
      Table.SELECTION_INVERT,
      Table.SELECTION_NONE,
      {
        key: "active",
        text: "Select Active",
        onSelect: () => {
          const activeKeys = filteredClients
            .filter((c) => c.status === "active" && !c.blocked)
            .map((c) => c.mac);
          setSelectedRowKeys(activeKeys);
        },
      },
      {
        key: "blocked",
        text: "Select Blocked",
        onSelect: () => {
          const blockedKeys = filteredClients
            .filter((c) => c.blocked)
            .map((c) => c.mac);
          setSelectedRowKeys(blockedKeys);
        },
      },
    ],
  };

  return (
    <div className="client-management">
      {/* Statistics Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <MaterialCard variant="elevated" elevation={1}>
            <Statistic
              title="Total Clients"
              value={stats.total}
              prefix={<UserOutlined />}
            />
          </MaterialCard>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <MaterialCard variant="elevated" elevation={1}>
            <Statistic
              title="Active"
              value={stats.active}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: "var(--md-sys-color-success)" }}
            />
          </MaterialCard>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <MaterialCard variant="elevated" elevation={1}>
            <Statistic
              title="Blocked"
              value={stats.blocked}
              prefix={<StopOutlined />}
              valueStyle={{ color: "var(--md-sys-color-error)" }}
            />
          </MaterialCard>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <MaterialCard variant="elevated" elevation={1}>
            <Statistic
              title="Selected"
              value={stats.selected}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: "var(--md-sys-color-primary)" }}
            />
          </MaterialCard>
        </Col>
      </Row>

      {/* Main Content */}
      <MaterialCard variant="elevated" elevation={1}>
        {/* Toolbar */}
        <Space
          direction="vertical"
          size="middle"
          style={{ width: "100%", marginBottom: 16 }}
        >
          <Row gutter={16} align="middle">
            <Col flex="auto">
              <Search
                placeholder="Search by name, MAC, IP, or hostname..."
                allowClear
                enterButton
                onChange={(e) => setSearchText(e.target.value)}
                style={{ maxWidth: 600 }}
              />
            </Col>
            <Col>
              <Select
                placeholder="Filter by status"
                allowClear
                style={{ width: 150 }}
                onChange={(value) => setStatusFilter(value)}
                options={[
                  { label: "Active", value: "active" },
                  { label: "Blocked", value: "blocked" },
                ]}
              />
            </Col>
          </Row>

          {/* Bulk Actions */}
          {selectedRowKeys.length > 0 && (
            <Row>
              <Col span={24}>
                <Space>
                  <Tag color="blue">
                    {selectedRowKeys.length} client(s) selected
                  </Tag>
                  <Button
                    danger
                    icon={<StopOutlined />}
                    onClick={handleBulkBlock}
                  >
                    Bulk Block
                  </Button>
                  <Button
                    type="primary"
                    icon={<CheckCircleOutlined />}
                    onClick={handleBulkUnblock}
                  >
                    Bulk Unblock
                  </Button>
                  <Button onClick={() => setSelectedRowKeys([])}>
                    Clear Selection
                  </Button>
                </Space>
              </Col>
            </Row>
          )}
        </Space>

        {/* Client Table */}
        <Table
          rowSelection={rowSelection}
          columns={columns}
          dataSource={filteredClients}
          rowKey="mac"
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} clients`,
          }}
          scroll={{ x: 1400 }}
        />
      </MaterialCard>

      {/* Block Modal */}
      <Modal
        title="Block Client"
        open={blockModalVisible}
        onOk={handleBlockSubmit}
        onCancel={() => {
          setBlockModalVisible(false);
          setCurrentClient(null);
          blockForm.resetFields();
        }}
        okText="Block"
        okButtonProps={{ danger: true }}
      >
        <Form form={blockForm} layout="vertical">
          <Form.Item
            label="Reason"
            name="reason"
            rules={[
              { max: 200, message: "Reason must be less than 200 characters" },
            ]}
          >
            <Input.TextArea
              placeholder="Optional reason for blocking"
              rows={3}
            />
          </Form.Item>
          <Form.Item
            name="permanent"
            valuePropName="checked"
            initialValue={false}
          >
            <Select
              options={[
                { label: "Temporary (specify duration)", value: false },
                { label: "Permanent", value: true },
              ]}
            />
          </Form.Item>
          <Form.Item
            noStyle
            shouldUpdate={(prevValues, currentValues) =>
              prevValues.permanent !== currentValues.permanent
            }
          >
            {({ getFieldValue }) =>
              !getFieldValue("permanent") && (
                <Form.Item
                  label="Duration (seconds)"
                  name="duration"
                  initialValue={3600}
                  rules={[
                    { required: true, message: "Please enter duration" },
                    {
                      type: "number",
                      min: 60,
                      max: 86400,
                      message: "Duration must be between 60 and 86400 seconds",
                    },
                  ]}
                >
                  <InputNumber
                    style={{ width: "100%" }}
                    placeholder="Duration in seconds"
                    min={60}
                    max={86400}
                  />
                </Form.Item>
              )
            }
          </Form.Item>
          {currentClient && (
            <div
              style={{
                marginTop: 8,
                padding: 12,
                backgroundColor: "var(--md-sys-color-surface-variant)",
                borderRadius: 8,
              }}
            >
              <p>
                <strong>Client:</strong> {currentClient.name}
              </p>
              <p>
                <strong>MAC:</strong> {currentClient.mac}
              </p>
              <p>
                <strong>IP:</strong> {currentClient.ip}
              </p>
            </div>
          )}
        </Form>
      </Modal>

      {/* Bandwidth Limit Modal */}
      <Modal
        title="Set Bandwidth Limits"
        open={bandwidthModalVisible}
        onOk={handleBandwidthSubmit}
        onCancel={() => {
          setBandwidthModalVisible(false);
          setCurrentClient(null);
          bandwidthForm.resetFields();
        }}
        okText="Set Limits"
      >
        <Form form={bandwidthForm} layout="vertical">
          <Form.Item
            label="Download Limit (Kbps)"
            name="download_limit"
            help="0 = unlimited"
            rules={[
              { required: true, message: "Please enter download limit" },
              {
                type: "number",
                min: 0,
                max: 1000000,
                message: "Must be between 0 and 1,000,000 Kbps",
              },
            ]}
          >
            <InputNumber
              style={{ width: "100%" }}
              placeholder="Download limit in Kbps"
              min={0}
              max={1000000}
            />
          </Form.Item>
          <Form.Item
            label="Upload Limit (Kbps)"
            name="upload_limit"
            help="0 = unlimited"
            rules={[
              { required: true, message: "Please enter upload limit" },
              {
                type: "number",
                min: 0,
                max: 1000000,
                message: "Must be between 0 and 1,000,000 Kbps",
              },
            ]}
          >
            <InputNumber
              style={{ width: "100%" }}
              placeholder="Upload limit in Kbps"
              min={0}
              max={1000000}
            />
          </Form.Item>
          {currentClient && (
            <div
              style={{
                marginTop: 8,
                padding: 12,
                backgroundColor: "var(--md-sys-color-surface-variant)",
                borderRadius: 8,
              }}
            >
              <p>
                <strong>Client:</strong> {currentClient.name}
              </p>
              <p>
                <strong>Current Limits:</strong>
              </p>
              <ul>
                <li>
                  Download:{" "}
                  {currentClient.download_limit
                    ? `${(currentClient.download_limit / 1000).toFixed(0)} Mbps`
                    : "Unlimited"}
                </li>
                <li>
                  Upload:{" "}
                  {currentClient.upload_limit
                    ? `${(currentClient.upload_limit / 1000).toFixed(0)} Mbps`
                    : "Unlimited"}
                </li>
              </ul>
            </div>
          )}
        </Form>
      </Modal>

      {/* Guest Authorization Modal */}
      <Modal
        title="Authorize Guest"
        open={guestModalVisible}
        onOk={handleGuestSubmit}
        onCancel={() => {
          setGuestModalVisible(false);
          setCurrentClient(null);
          guestForm.resetFields();
        }}
        okText="Authorize"
      >
        <Form form={guestForm} layout="vertical">
          <Form.Item
            label="Duration (seconds)"
            name="duration"
            initialValue={3600}
            help="How long the guest authorization will last"
            rules={[
              { required: true, message: "Please enter duration" },
              {
                type: "number",
                min: 300,
                max: 86400,
                message: "Duration must be between 300 and 86400 seconds",
              },
            ]}
          >
            <InputNumber
              style={{ width: "100%" }}
              placeholder="Duration in seconds"
              min={300}
              max={86400}
            />
          </Form.Item>
          <div style={{ marginTop: 8 }}>
            <p>Common durations:</p>
            <Space wrap>
              <Button
                size="small"
                onClick={() => guestForm.setFieldsValue({ duration: 3600 })}
              >
                1 hour
              </Button>
              <Button
                size="small"
                onClick={() => guestForm.setFieldsValue({ duration: 14400 })}
              >
                4 hours
              </Button>
              <Button
                size="small"
                onClick={() => guestForm.setFieldsValue({ duration: 28800 })}
              >
                8 hours
              </Button>
              <Button
                size="small"
                onClick={() => guestForm.setFieldsValue({ duration: 86400 })}
              >
                24 hours
              </Button>
            </Space>
          </div>
          {currentClient && (
            <div
              style={{
                marginTop: 16,
                padding: 12,
                backgroundColor: "var(--md-sys-color-surface-variant)",
                borderRadius: 8,
              }}
            >
              <p>
                <strong>Client:</strong> {currentClient.name}
              </p>
              <p>
                <strong>MAC:</strong> {currentClient.mac}
              </p>
            </div>
          )}
        </Form>
      </Modal>

      {/* Bulk Operations Modal */}
      <BulkOperationsModal
        visible={bulkModalVisible}
        onClose={() => {
          setBulkModalVisible(false);
        }}
        onComplete={() => {
          // Update local state based on operation type
          if (bulkOperationType === "client_block") {
            setClients(
              clients.map((c) =>
                selectedRowKeys.includes(c.mac)
                  ? { ...c, blocked: true, status: "blocked" }
                  : c
              )
            );
          } else if (bulkOperationType === "client_unblock") {
            setClients(
              clients.map((c) =>
                selectedRowKeys.includes(c.mac)
                  ? { ...c, blocked: false, status: "active" }
                  : c
              )
            );
          }
          setSelectedRowKeys([]);
        }}
        operationType={bulkOperationType}
        items={getBulkOperationItems()}
        title={
          bulkOperationType === "client_block"
            ? "Bulk Client Block"
            : "Bulk Client Unblock"
        }
        description={
          bulkOperationType === "client_block"
            ? "Select clients to block from the network."
            : "Select clients to unblock and restore network access."
        }
        warningMessage={
          bulkOperationType === "client_block"
            ? "Blocking clients will immediately disconnect them from the network."
            : undefined
        }
      />
    </div>
  );
};

export default ClientManagement;

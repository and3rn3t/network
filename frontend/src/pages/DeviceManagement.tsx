/**
 * DeviceManagement - Manage UniFi network devices
 */

import type { BulkOperationItem } from "@/components/BulkOperationsModal";
import { BulkOperationsModal } from "@/components/BulkOperationsModal";
import { DeviceDetailModal } from "@/components/DeviceDetailModal";
import { MaterialCard } from "@/components/MaterialCard";
import { useDevices } from "@/hooks/useDevices";
import {
  AimOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  EditOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  PoweroffOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import {
  Badge,
  Button,
  Col,
  Form,
  Input,
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

const { Search } = Input;
const { confirm } = Modal;

interface Device {
  id: number;
  mac: string;
  name: string;
  model: string;
  type: string;
  ip: string;
  status: string;
  version: string;
  uptime: number;
  last_seen: string;
}

const DeviceManagement: React.FC = () => {
  const { data: devicesData, isLoading, refetch } = useDevices();
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [searchText, setSearchText] = useState("");
  const [statusFilter, setStatusFilter] = useState<string | undefined>(
    undefined
  );
  const [renameModalVisible, setRenameModalVisible] = useState(false);
  const [renamingDevice, setRenamingDevice] = useState<Device | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [detailDevice, setDetailDevice] = useState<Device | null>(null);
  const [bulkModalVisible, setBulkModalVisible] = useState(false);
  const [form] = Form.useForm();

  // Filter devices based on search and status
  const filteredDevices = useMemo(() => {
    if (!devicesData?.devices) return [];

    return devicesData.devices.filter((device: Device) => {
      const matchesSearch =
        !searchText ||
        device.name.toLowerCase().includes(searchText.toLowerCase()) ||
        device.mac.toLowerCase().includes(searchText.toLowerCase()) ||
        device.ip.toLowerCase().includes(searchText.toLowerCase()) ||
        device.model.toLowerCase().includes(searchText.toLowerCase());

      const matchesStatus = !statusFilter || device.status === statusFilter;

      return matchesSearch && matchesStatus;
    });
  }, [devicesData, searchText, statusFilter]);

  // Calculate statistics
  const stats = useMemo(() => {
    const devices = devicesData?.devices || [];
    return {
      total: devices.length,
      online: devices.filter((d: Device) => d.status === "online").length,
      offline: devices.filter((d: Device) => d.status === "offline").length,
      selected: selectedRowKeys.length,
    };
  }, [devicesData, selectedRowKeys]);

  // Handle device reboot
  const handleReboot = async (device: Device) => {
    confirm({
      title: `Reboot ${device.name}?`,
      icon: <ExclamationCircleOutlined />,
      content: (
        <div>
          <p>
            This will temporarily disconnect the device and any connected
            clients.
          </p>
          <p>
            <strong>Device:</strong> {device.name} ({device.ip})
          </p>
        </div>
      ),
      okText: "Reboot",
      okType: "danger",
      cancelText: "Cancel",
      onOk: async () => {
        try {
          await axios.post(`/api/devices/${device.id}/reboot`, {
            action: "reboot",
            reason: "Manual reboot from Device Management",
          });
          message.success(`Reboot command sent to ${device.name}`);
          refetch();
        } catch (error) {
          message.error(`Failed to reboot device: ${error}`);
        }
      },
    });
  };

  // Handle bulk reboot
  const handleBulkReboot = () => {
    if (selectedRowKeys.length === 0) {
      message.warning("Please select devices to reboot");
      return;
    }
    setBulkModalVisible(true);
  };

  // Get bulk operation items from selected devices
  const getBulkOperationItems = (): BulkOperationItem[] => {
    return filteredDevices
      .filter((device) => selectedRowKeys.includes(device.id))
      .map((device) => ({
        key: String(device.id),
        title: device.name,
        description: `${device.model} - ${device.ip}`,
        disabled: device.status === "offline",
      }));
  };

  // Handle device locate (LED blink)
  const handleLocate = async (device: Device) => {
    try {
      await axios.post(`/api/devices/${device.id}/locate?duration=30`, {});
      message.success(`LED blinking on ${device.name} for 30 seconds`);
    } catch (error) {
      message.error(`Failed to locate device: ${error}`);
    }
  };

  // Handle device rename
  const handleRenameClick = (device: Device) => {
    setRenamingDevice(device);
    form.setFieldsValue({ name: device.name });
    setRenameModalVisible(true);
  };

  const handleRenameSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (!renamingDevice) return;

      await axios.post(`/api/devices/${renamingDevice.id}/rename`, {
        name: values.name,
      });

      message.success(`Device renamed to ${values.name}`);
      setRenameModalVisible(false);
      setRenamingDevice(null);
      form.resetFields();
      refetch();
    } catch (error) {
      message.error(`Failed to rename device: ${error}`);
    }
  };

  // Table columns
  const columns: ColumnType<Device>[] = [
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 100,
      render: (status: string) => {
        const statusConfig: Record<
          string,
          { color: string; icon: React.ReactNode; text: string }
        > = {
          online: {
            color: "success",
            icon: <CheckCircleOutlined />,
            text: "Online",
          },
          offline: {
            color: "error",
            icon: <ExclamationCircleOutlined />,
            text: "Offline",
          },
          unknown: {
            color: "default",
            icon: <ClockCircleOutlined />,
            text: "Unknown",
          },
        };

        const config = statusConfig[status] || statusConfig.unknown;

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
        { text: "Online", value: "online" },
        { text: "Offline", value: "offline" },
      ],
      onFilter: (value, record) => record.status === value,
    },
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
      sorter: (a, b) => a.name.localeCompare(b.name),
      render: (name: string, record: Device) => (
        <Space>
          <strong>{name}</strong>
          <Tooltip title="Rename device">
            <Button
              type="text"
              size="small"
              icon={<EditOutlined />}
              onClick={() => handleRenameClick(record)}
            />
          </Tooltip>
        </Space>
      ),
    },
    {
      title: "Model",
      dataIndex: "model",
      key: "model",
      sorter: (a, b) => a.model.localeCompare(b.model),
    },
    {
      title: "Type",
      dataIndex: "type",
      key: "type",
      render: (type: string) => {
        const typeColors: Record<string, string> = {
          uap: "blue",
          usw: "green",
          ugw: "purple",
          usg: "orange",
        };
        return (
          <Tag color={typeColors[type] || "default"}>{type.toUpperCase()}</Tag>
        );
      },
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
      title: "Firmware",
      dataIndex: "version",
      key: "version",
      responsive: ["xl"],
    },
    {
      title: "Uptime",
      dataIndex: "uptime",
      key: "uptime",
      responsive: ["xl"],
      render: (uptime: number) => {
        const days = Math.floor(uptime / 86400);
        const hours = Math.floor((uptime % 86400) / 3600);
        const minutes = Math.floor((uptime % 3600) / 60);
        return `${days}d ${hours}h ${minutes}m`;
      },
    },
    {
      title: "Actions",
      key: "actions",
      width: 200,
      render: (_, record: Device) => (
        <Space size="small">
          <Tooltip title="Reboot device">
            <Button
              type="primary"
              danger
              size="small"
              icon={<ReloadOutlined />}
              onClick={() => handleReboot(record)}
              disabled={record.status === "offline"}
            >
              Reboot
            </Button>
          </Tooltip>
          <Tooltip title="Locate device (blink LED)">
            <Button
              size="small"
              icon={<AimOutlined />}
              onClick={() => handleLocate(record)}
              disabled={record.status === "offline"}
            >
              Locate
            </Button>
          </Tooltip>
          <Tooltip title="View details">
            <Button
              size="small"
              icon={<InfoCircleOutlined />}
              onClick={() => {
                setDetailDevice(record);
                setDetailModalVisible(true);
              }}
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
        key: "online",
        text: "Select Online",
        onSelect: (changeableRowKeys: React.Key[]) => {
          const onlineKeys = filteredDevices
            .filter((d) => d.status === "online")
            .map((d) => d.id);
          setSelectedRowKeys(onlineKeys);
        },
      },
      {
        key: "offline",
        text: "Select Offline",
        onSelect: (changeableRowKeys: React.Key[]) => {
          const offlineKeys = filteredDevices
            .filter((d) => d.status === "offline")
            .map((d) => d.id);
          setSelectedRowKeys(offlineKeys);
        },
      },
    ],
  };

  return (
    <div className="device-management">
      {/* Statistics Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <MaterialCard variant="elevated" elevation={1}>
            <Statistic
              title="Total Devices"
              value={stats.total}
              prefix={<InfoCircleOutlined />}
            />
          </MaterialCard>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <MaterialCard variant="elevated" elevation={1}>
            <Statistic
              title="Online"
              value={stats.online}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: "var(--md-sys-color-success)" }}
            />
          </MaterialCard>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <MaterialCard variant="elevated" elevation={1}>
            <Statistic
              title="Offline"
              value={stats.offline}
              prefix={<ExclamationCircleOutlined />}
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
                placeholder="Search by name, MAC, IP, or model..."
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
                  { label: "Online", value: "online" },
                  { label: "Offline", value: "offline" },
                ]}
              />
            </Col>
            <Col>
              <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
                Refresh
              </Button>
            </Col>
          </Row>

          {/* Bulk Actions */}
          {selectedRowKeys.length > 0 && (
            <Row>
              <Col span={24}>
                <Space>
                  <Tag color="blue">
                    {selectedRowKeys.length} device(s) selected
                  </Tag>
                  <Button
                    type="primary"
                    danger
                    icon={<PoweroffOutlined />}
                    onClick={handleBulkReboot}
                  >
                    Bulk Reboot
                  </Button>
                  <Button onClick={() => setSelectedRowKeys([])}>
                    Clear Selection
                  </Button>
                </Space>
              </Col>
            </Row>
          )}
        </Space>

        {/* Device Table */}
        <Table
          rowSelection={rowSelection}
          columns={columns}
          dataSource={filteredDevices}
          rowKey="id"
          loading={isLoading}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} devices`,
          }}
          scroll={{ x: 1200 }}
        />
      </MaterialCard>

      {/* Rename Modal */}
      <Modal
        title="Rename Device"
        open={renameModalVisible}
        onOk={handleRenameSubmit}
        onCancel={() => {
          setRenameModalVisible(false);
          setRenamingDevice(null);
          form.resetFields();
        }}
        okText="Rename"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="Device Name"
            name="name"
            rules={[
              { required: true, message: "Please enter a device name" },
              { min: 1, max: 100, message: "Name must be 1-100 characters" },
            ]}
          >
            <Input placeholder="Enter new device name" />
          </Form.Item>
          {renamingDevice && (
            <div style={{ marginTop: 8 }}>
              <p>
                <strong>Current name:</strong> {renamingDevice.name}
              </p>
              <p>
                <strong>MAC:</strong> {renamingDevice.mac}
              </p>
              <p>
                <strong>IP:</strong> {renamingDevice.ip}
              </p>
            </div>
          )}
        </Form>
      </Modal>

      {/* Device Detail Modal */}
      <DeviceDetailModal
        visible={detailModalVisible}
        device={
          detailDevice
            ? {
                id: String(detailDevice.id),
                name: detailDevice.name,
                mac: detailDevice.mac,
                model: detailDevice.model,
                type: detailDevice.type,
                ip: detailDevice.ip,
                firmware_version: detailDevice.version,
                uptime: detailDevice.uptime,
                status: detailDevice.status as "online" | "offline",
              }
            : null
        }
        onClose={() => {
          setDetailModalVisible(false);
          setDetailDevice(null);
        }}
        onRefresh={refetch}
      />

      {/* Bulk Operations Modal */}
      <BulkOperationsModal
        visible={bulkModalVisible}
        onClose={() => {
          setBulkModalVisible(false);
        }}
        onComplete={() => {
          setSelectedRowKeys([]);
          refetch();
        }}
        operationType="device_reboot"
        items={getBulkOperationItems()}
        title="Bulk Device Reboot"
        description="Select devices to reboot. Offline devices will be disabled."
        warningMessage="Rebooting devices will temporarily disconnect them and their connected clients (typically 30-60 seconds)."
      />
    </div>
  );
};

export default DeviceManagement;

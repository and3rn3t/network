/**
 * BulkOperationsModal - Enhanced UI for bulk operations with progress tracking
 * Supports devices and clients with visual feedback and error handling
 */

import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  LoadingOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import {
  Alert,
  Button,
  Card,
  Col,
  Divider,
  List,
  message,
  Modal,
  Progress,
  Row,
  Space,
  Statistic,
  Tag,
  Transfer,
  Typography,
} from "antd";
import type { TransferDirection } from "antd/es/transfer";
import React, { useEffect, useState } from "react";

const { Text, Title } = Typography;

export type BulkOperationType =
  | "device_reboot"
  | "device_restart"
  | "client_block"
  | "client_unblock"
  | "client_reconnect";

export interface BulkOperationItem {
  key: string;
  title: string;
  description?: string;
  disabled?: boolean;
}

interface OperationResult {
  key: string;
  status: "pending" | "processing" | "success" | "error";
  message?: string;
  timestamp?: Date;
}

interface BulkOperationsModalProps {
  visible: boolean;
  onClose: () => void;
  onComplete?: () => void;
  operationType: BulkOperationType;
  items: BulkOperationItem[];
  title: string;
  description?: string;
  warningMessage?: string;
}

export const BulkOperationsModal: React.FC<BulkOperationsModalProps> = ({
  visible,
  onClose,
  onComplete,
  operationType,
  items,
  title,
  description,
  warningMessage,
}) => {
  const [targetKeys, setTargetKeys] = useState<string[]>([]);
  const [selectedKeys, setSelectedKeys] = useState<string[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<Map<string, OperationResult>>(
    new Map()
  );
  const [showResults, setShowResults] = useState(false);

  // Initialize target keys with all items
  useEffect(() => {
    if (visible && items.length > 0) {
      setTargetKeys(
        items.filter((item) => !item.disabled).map((item) => item.key)
      );
    }
  }, [visible, items]);

  // Reset state when modal opens/closes
  useEffect(() => {
    if (!visible) {
      setTimeout(() => {
        setTargetKeys([]);
        setSelectedKeys([]);
        setIsProcessing(false);
        setResults(new Map());
        setShowResults(false);
      }, 300);
    }
  }, [visible]);

  const handleChange = (
    newTargetKeys: string[],
    direction: TransferDirection,
    moveKeys: string[]
  ) => {
    setTargetKeys(newTargetKeys);
  };

  const handleSelectChange = (
    sourceSelectedKeys: string[],
    targetSelectedKeys: string[]
  ) => {
    setSelectedKeys([...sourceSelectedKeys, ...targetSelectedKeys]);
  };

  const getApiEndpoint = (type: BulkOperationType): string => {
    switch (type) {
      case "device_reboot":
        return "/api/devices/bulk/reboot";
      case "device_restart":
        return "/api/devices/bulk/restart";
      case "client_block":
        return "/api/clients/bulk/block";
      case "client_unblock":
        return "/api/clients/bulk/unblock";
      case "client_reconnect":
        return "/api/clients/bulk/reconnect";
      default:
        return "";
    }
  };

  const executeOperation = async (itemKey: string): Promise<void> => {
    const endpoint = getApiEndpoint(operationType);

    // Update status to processing
    setResults((prev) => {
      const newResults = new Map(prev);
      newResults.set(itemKey, {
        key: itemKey,
        status: "processing",
        timestamp: new Date(),
      });
      return newResults;
    });

    try {
      // Simulate API call with delay for demo
      await new Promise((resolve) =>
        setTimeout(resolve, 500 + Math.random() * 1000)
      );

      // In production, make actual API call
      // await axios.post(endpoint, { ids: [itemKey] });

      // Update status to success
      setResults((prev) => {
        const newResults = new Map(prev);
        newResults.set(itemKey, {
          key: itemKey,
          status: "success",
          message: "Operation completed successfully",
          timestamp: new Date(),
        });
        return newResults;
      });
    } catch (error: any) {
      // Update status to error
      setResults((prev) => {
        const newResults = new Map(prev);
        newResults.set(itemKey, {
          key: itemKey,
          status: "error",
          message:
            error.response?.data?.detail || error.message || "Operation failed",
          timestamp: new Date(),
        });
        return newResults;
      });
    }
  };

  const handleExecute = async () => {
    if (targetKeys.length === 0) {
      message.warning("Please select at least one item");
      return;
    }

    setIsProcessing(true);
    setShowResults(true);

    // Initialize all as pending
    const initialResults = new Map<string, OperationResult>();
    targetKeys.forEach((key) => {
      initialResults.set(key, {
        key,
        status: "pending",
      });
    });
    setResults(initialResults);

    // Execute operations sequentially to avoid overwhelming the API
    for (const key of targetKeys) {
      await executeOperation(key);
    }

    setIsProcessing(false);
    message.success("Bulk operation completed");
    onComplete?.();
  };

  const handleRetryFailed = async () => {
    const failedKeys = Array.from(results.entries())
      .filter(([_, result]) => result.status === "error")
      .map(([key]) => key);

    if (failedKeys.length === 0) {
      message.info("No failed operations to retry");
      return;
    }

    setIsProcessing(true);

    for (const key of failedKeys) {
      await executeOperation(key);
    }

    setIsProcessing(false);
    message.success("Retry completed");
  };

  const stats = {
    total: targetKeys.length,
    pending: Array.from(results.values()).filter((r) => r.status === "pending")
      .length,
    processing: Array.from(results.values()).filter(
      (r) => r.status === "processing"
    ).length,
    success: Array.from(results.values()).filter((r) => r.status === "success")
      .length,
    error: Array.from(results.values()).filter((r) => r.status === "error")
      .length,
  };

  const progress =
    stats.total > 0
      ? Math.round(((stats.success + stats.error) / stats.total) * 100)
      : 0;

  const getStatusIcon = (status: OperationResult["status"]) => {
    switch (status) {
      case "success":
        return (
          <CheckCircleOutlined
            style={{ color: "var(--md-sys-color-primary)" }}
          />
        );
      case "error":
        return (
          <CloseCircleOutlined style={{ color: "var(--md-sys-color-error)" }} />
        );
      case "processing":
        return (
          <LoadingOutlined style={{ color: "var(--md-sys-color-tertiary)" }} />
        );
      default:
        return (
          <ExclamationCircleOutlined
            style={{ color: "var(--md-sys-color-outline)" }}
          />
        );
    }
  };

  const getStatusColor = (status: OperationResult["status"]) => {
    switch (status) {
      case "success":
        return "success";
      case "error":
        return "error";
      case "processing":
        return "processing";
      default:
        return "default";
    }
  };

  const renderTransferItem = (item: BulkOperationItem) => ({
    key: item.key,
    title: item.title,
    description: item.description,
    disabled: item.disabled,
  });

  return (
    <Modal
      title={title}
      open={visible}
      onCancel={onClose}
      width={900}
      footer={
        !showResults ? (
          <Space>
            <Button onClick={onClose}>Cancel</Button>
            <Button
              type="primary"
              onClick={handleExecute}
              disabled={targetKeys.length === 0}
              danger={
                operationType.includes("reboot") ||
                operationType.includes("block")
              }
            >
              Execute Operation ({targetKeys.length} items)
            </Button>
          </Space>
        ) : (
          <Space>
            {stats.error > 0 && !isProcessing && (
              <Button icon={<ReloadOutlined />} onClick={handleRetryFailed}>
                Retry Failed ({stats.error})
              </Button>
            )}
            <Button type="primary" onClick={onClose} disabled={isProcessing}>
              Close
            </Button>
          </Space>
        )
      }
    >
      {description && (
        <Alert
          message={description}
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {warningMessage && (
        <Alert
          message={warningMessage}
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {!showResults ? (
        <div>
          <Title level={5}>Select Items for Operation</Title>
          <Text type="secondary">
            Move items to the right panel to include them in the bulk operation.
            You can select and move multiple items at once.
          </Text>
          <Divider />
          <Transfer
            dataSource={items.map(renderTransferItem)}
            titles={["Available", "Selected for Operation"]}
            targetKeys={targetKeys}
            selectedKeys={selectedKeys}
            onChange={handleChange}
            onSelectChange={handleSelectChange}
            render={(item) => (
              <div>
                <div>{item.title}</div>
                {item.description && (
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {item.description}
                  </Text>
                )}
              </div>
            )}
            listStyle={{
              width: 400,
              height: 400,
            }}
            showSearch
            showSelectAll
            oneWay={false}
          />
        </div>
      ) : (
        <div>
          <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
            <Col span={6}>
              <Card size="small">
                <Statistic
                  title="Total"
                  value={stats.total}
                  valueStyle={{ fontSize: 24 }}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small">
                <Statistic
                  title="Success"
                  value={stats.success}
                  valueStyle={{
                    color: "var(--md-sys-color-primary)",
                    fontSize: 24,
                  }}
                  prefix={<CheckCircleOutlined />}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small">
                <Statistic
                  title="Failed"
                  value={stats.error}
                  valueStyle={{
                    color: "var(--md-sys-color-error)",
                    fontSize: 24,
                  }}
                  prefix={<CloseCircleOutlined />}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small">
                <Statistic
                  title="Pending"
                  value={stats.pending + stats.processing}
                  valueStyle={{ fontSize: 24 }}
                  prefix={isProcessing ? <LoadingOutlined /> : undefined}
                />
              </Card>
            </Col>
          </Row>

          <Progress
            percent={progress}
            status={
              isProcessing
                ? "active"
                : stats.error > 0
                ? "exception"
                : "success"
            }
            style={{ marginBottom: 16 }}
          />

          <Card
            title="Operation Results"
            size="small"
            style={{ maxHeight: 400, overflow: "auto" }}
          >
            <List
              dataSource={Array.from(results.entries()).map(([key, result]) => {
                const item = items.find((i) => i.key === key);
                return { ...result, item };
              })}
              renderItem={(result) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={getStatusIcon(result.status)}
                    title={
                      <Space>
                        <span>{result.item?.title || result.key}</span>
                        <Tag color={getStatusColor(result.status)}>
                          {result.status}
                        </Tag>
                      </Space>
                    }
                    description={
                      <div>
                        {result.item?.description && (
                          <div style={{ marginBottom: 4 }}>
                            <Text type="secondary">
                              {result.item.description}
                            </Text>
                          </div>
                        )}
                        {result.message && (
                          <Text
                            type={
                              result.status === "error" ? "danger" : "secondary"
                            }
                          >
                            {result.message}
                          </Text>
                        )}
                        {result.timestamp && (
                          <div style={{ marginTop: 4 }}>
                            <Text type="secondary" style={{ fontSize: 11 }}>
                              {result.timestamp.toLocaleTimeString()}
                            </Text>
                          </div>
                        )}
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>

          {stats.error > 0 && !isProcessing && (
            <Alert
              message={`${stats.error} operation(s) failed. You can retry failed operations using the button below.`}
              type="error"
              showIcon
              style={{ marginTop: 16 }}
            />
          )}
        </div>
      )}
    </Modal>
  );
};

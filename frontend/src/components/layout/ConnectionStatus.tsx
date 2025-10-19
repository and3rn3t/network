/**
 * WebSocket Connection Status Indicator
 * Shows live connection status with animated indicator
 */

import type { ConnectionStatus as StatusType } from "@/hooks/useWebSocket";
import { useWebSocket } from "@/hooks/useWebSocket";
import { Badge, Tooltip } from "antd";
import React, { useEffect, useState } from "react";
import "./ConnectionStatus.css";

export const ConnectionStatus: React.FC = () => {
  const { status, lastMessage } = useWebSocket({
    url: "ws://localhost:8000/ws",
    autoReconnect: true,
  });

  const [lastMessageTime, setLastMessageTime] = useState<Date | null>(null);

  useEffect(() => {
    if (lastMessage?.timestamp) {
      setLastMessageTime(new Date(lastMessage.timestamp));
    }
  }, [lastMessage]);

  const getStatusConfig = (
    currentStatus: StatusType
  ): {
    status: "success" | "processing" | "error" | "default";
    text: string;
    color: string;
  } => {
    switch (currentStatus) {
      case "connected":
        return {
          status: "success",
          text: "Connected",
          color: "var(--md-sys-color-primary)",
        };
      case "connecting":
        return {
          status: "processing",
          text: "Connecting...",
          color: "var(--md-sys-color-tertiary)",
        };
      case "disconnected":
        return {
          status: "default",
          text: "Disconnected",
          color: "var(--md-sys-color-outline)",
        };
      case "error":
        return {
          status: "error",
          text: "Connection Error",
          color: "var(--md-sys-color-error)",
        };
      default:
        return {
          status: "default",
          text: "Unknown",
          color: "var(--md-sys-color-outline)",
        };
    }
  };

  const statusConfig = getStatusConfig(status);

  const getTooltipContent = () => {
    const content = [`Status: ${statusConfig.text}`];

    if (lastMessageTime) {
      const secondsAgo = Math.floor(
        (Date.now() - lastMessageTime.getTime()) / 1000
      );
      content.push(`Last update: ${secondsAgo}s ago`);
    }

    return content.join("\n");
  };

  return (
    <Tooltip
      title={
        <div className="connection-status-tooltip">{getTooltipContent()}</div>
      }
      placement="bottomRight"
    >
      <div className="connection-status">
        <Badge
          status={statusConfig.status}
          text={
            <span
              className={`connection-status-text connection-status-${status}`}
            >
              {statusConfig.text}
            </span>
          }
        />
      </div>
    </Tooltip>
  );
};

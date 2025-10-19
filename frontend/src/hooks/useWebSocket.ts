/**
 * WebSocket Client Hook
 * Manages WebSocket connection with auto-reconnect, heartbeat, and room subscriptions
 */

import { useCallback, useEffect, useRef, useState } from "react";

export type ConnectionStatus =
  | "connecting"
  | "connected"
  | "disconnected"
  | "error";

export interface WebSocketMessage {
  type: string;
  data?: unknown;
  timestamp?: string;
  room?: string;
  status?: string;
}

export interface UseWebSocketOptions {
  url: string;
  autoReconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

export interface UseWebSocketReturn {
  status: ConnectionStatus;
  send: (message: WebSocketMessage) => void;
  subscribe: (room: string) => void;
  unsubscribe: (room: string) => void;
  connect: () => void;
  disconnect: () => void;
  lastMessage: WebSocketMessage | null;
  reconnectAttempts: number;
}

const STORAGE_KEY = "unifi_monitor_preferences";

/**
 * Custom hook for WebSocket connection management
 */
export const useWebSocket = (
  options: UseWebSocketOptions
): UseWebSocketReturn => {
  const {
    url,
    autoReconnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 10,
    heartbeatInterval = 30000,
    onMessage,
    onConnect,
    onDisconnect,
    onError,
  } = options;

  const [status, setStatus] = useState<ConnectionStatus>("disconnected");
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const heartbeatTimerRef = useRef<number | null>(null);
  const subscribedRooms = useRef<Set<string>>(new Set());
  const isIntentionalDisconnect = useRef(false);

  /**
   * Send a message through WebSocket
   */
  const send = useCallback((message: WebSocketMessage) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn("WebSocket is not connected. Cannot send message.");
    }
  }, []);

  /**
   * Subscribe to a room for targeted updates
   */
  const subscribe = useCallback(
    (room: string) => {
      subscribedRooms.current.add(room);
      send({ type: "subscribe", room });
    },
    [send]
  );

  /**
   * Unsubscribe from a room
   */
  const unsubscribe = useCallback(
    (room: string) => {
      subscribedRooms.current.delete(room);
      send({ type: "unsubscribe", room });
    },
    [send]
  );

  /**
   * Start heartbeat to keep connection alive
   */
  const startHeartbeat = useCallback(() => {
    if (heartbeatTimerRef.current) {
      clearInterval(heartbeatTimerRef.current);
    }

    heartbeatTimerRef.current = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        send({ type: "ping" });
      }
    }, heartbeatInterval);
  }, [heartbeatInterval, send]);

  /**
   * Stop heartbeat
   */
  const stopHeartbeat = useCallback(() => {
    if (heartbeatTimerRef.current) {
      clearInterval(heartbeatTimerRef.current);
      heartbeatTimerRef.current = null;
    }
  }, []);

  /**
   * Re-subscribe to all rooms after reconnection
   */
  const resubscribeRooms = useCallback(() => {
    for (const room of subscribedRooms.current) {
      send({ type: "subscribe", room });
    }
  }, [send]);

  /**
   * Connect to WebSocket
   */
  const connect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      return;
    }

    isIntentionalDisconnect.current = false;
    setStatus("connecting");

    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        console.log("WebSocket connected");
        setStatus("connected");
        setReconnectAttempts(0);
        startHeartbeat();
        resubscribeRooms();
        onConnect?.();
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
          onMessage?.(message);
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error);
        }
      };

      ws.onerror = (event) => {
        console.error("WebSocket error:", event);
        setStatus("error");
        onError?.(event);
      };

      ws.onclose = (event) => {
        console.log("WebSocket disconnected:", event.code, event.reason);
        setStatus("disconnected");
        stopHeartbeat();
        onDisconnect?.();

        // Auto-reconnect if not intentional disconnect
        if (
          !isIntentionalDisconnect.current &&
          autoReconnect &&
          reconnectAttempts < maxReconnectAttempts
        ) {
          reconnectTimerRef.current = setTimeout(() => {
            console.log(
              `Attempting to reconnect... (${
                reconnectAttempts + 1
              }/${maxReconnectAttempts})`
            );
            setReconnectAttempts((prev) => prev + 1);
            connect();
          }, reconnectInterval);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error("Failed to create WebSocket connection:", error);
      setStatus("error");
    }
  }, [
    url,
    autoReconnect,
    reconnectInterval,
    maxReconnectAttempts,
    reconnectAttempts,
    startHeartbeat,
    stopHeartbeat,
    resubscribeRooms,
    onConnect,
    onDisconnect,
    onError,
    onMessage,
  ]);

  /**
   * Disconnect from WebSocket
   */
  const disconnect = useCallback(() => {
    isIntentionalDisconnect.current = true;

    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }

    stopHeartbeat();

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setStatus("disconnected");
    setReconnectAttempts(0);
  }, [stopHeartbeat]);

  /**
   * Auto-connect on mount and cleanup on unmount
   */
  useEffect(() => {
    // Check if real-time updates are enabled in preferences
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const preferences = JSON.parse(stored);
        if (preferences.enableNotifications === false) {
          // User disabled real-time updates
          return;
        }
      }
    } catch {
      // Ignore parsing errors
    }

    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    status,
    send,
    subscribe,
    unsubscribe,
    connect,
    disconnect,
    lastMessage,
    reconnectAttempts,
  };
};

/**
 * Real-Time Data Hooks
 * Hooks for subscribing to real-time metrics and alerts via WebSocket
 */

import type { Alert } from "@/types/alert";
import { useCallback, useEffect, useState } from "react";
import type { WebSocketMessage } from "./useWebSocket";
import { useWebSocket } from "./useWebSocket";

const WS_URL = "ws://localhost:8000/ws";

// Types for real-time metric updates
interface MetricUpdate {
  device_id: number;
  metric_type: string;
  value: number;
  timestamp: string;
}

/**
 * Hook for real-time metrics updates
 */
export const useRealTimeMetrics = (deviceId?: string) => {
  const [metrics, setMetrics] = useState<MetricUpdate[]>([]);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const handleMessage = useCallback(
    (message: WebSocketMessage) => {
      if (message.type === "metric_update") {
        const metric = message.data as MetricUpdate;

        // Filter by device if specified
        if (deviceId && metric.device_id !== Number.parseInt(deviceId, 10)) {
          return;
        }

        setMetrics((prev) => {
          // Add new metric and keep last 100 points
          const updated = [...prev, metric].slice(-100);
          return updated;
        });

        setLastUpdate(new Date());
      }
    },
    [deviceId]
  );

  const { status, subscribe, unsubscribe, ...rest } = useWebSocket({
    url: WS_URL,
    onMessage: handleMessage,
    autoReconnect: true,
  });

  useEffect(() => {
    // Subscribe to metrics room
    const room = deviceId ? `metrics:${deviceId}` : "metrics";
    subscribe(room);

    return () => {
      unsubscribe(room);
    };
  }, [deviceId, subscribe, unsubscribe]);

  return {
    metrics,
    lastUpdate,
    status,
    ...rest,
  };
};

/**
 * Hook for real-time alert notifications
 */
export const useRealTimeAlerts = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [newAlertCount, setNewAlertCount] = useState(0);
  const [lastAlert, setLastAlert] = useState<Alert | null>(null);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    if (message.type === "alert_triggered") {
      const alert = message.data as Alert;

      setAlerts((prev) => [alert, ...prev].slice(0, 50));
      setNewAlertCount((prev) => prev + 1);
      setLastAlert(alert);

      // Play sound for critical alerts if enabled
      if (alert.severity === "critical") {
        playAlertSound();
      }
    } else if (message.type === "alert_acknowledged") {
      const data = message.data as { id: number; acknowledged_by: number };
      setAlerts((prev) =>
        prev.map((a) =>
          a.id === data.id
            ? {
                ...a,
                acknowledged_at: new Date().toISOString(),
                acknowledged_by: data.acknowledged_by,
              }
            : a
        )
      );
    } else if (message.type === "alert_resolved") {
      const data = message.data as { id: number; resolved_by: number };
      setAlerts((prev) =>
        prev.map((a) =>
          a.id === data.id
            ? {
                ...a,
                resolved_at: new Date().toISOString(),
                resolved_by: data.resolved_by,
              }
            : a
        )
      );
    }
  }, []);

  const { status, subscribe, unsubscribe, ...rest } = useWebSocket({
    url: WS_URL,
    onMessage: handleMessage,
    autoReconnect: true,
  });

  useEffect(() => {
    // Subscribe to alerts room
    subscribe("alerts");

    return () => {
      unsubscribe("alerts");
    };
  }, [subscribe, unsubscribe]);

  const clearNewAlertCount = useCallback(() => {
    setNewAlertCount(0);
  }, []);

  return {
    alerts,
    newAlertCount,
    lastAlert,
    status,
    clearNewAlertCount,
    ...rest,
  };
};

/**
 * Hook for real-time device status updates
 */
export const useRealTimeDeviceStatus = () => {
  const [deviceStatuses, setDeviceStatuses] = useState<
    Record<number, "online" | "offline">
  >({});
  const [lastStatusChange, setLastStatusChange] = useState<Date | null>(null);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    if (message.type === "device_status_change") {
      const data = message.data as {
        device_id: number;
        status: "online" | "offline";
      };

      setDeviceStatuses((prev) => ({
        ...prev,
        [data.device_id]: data.status,
      }));

      setLastStatusChange(new Date());
    }
  }, []);

  const { status, subscribe, unsubscribe, ...rest } = useWebSocket({
    url: WS_URL,
    onMessage: handleMessage,
    autoReconnect: true,
  });

  useEffect(() => {
    // Subscribe to device status room
    subscribe("devices");

    return () => {
      unsubscribe("devices");
    };
  }, [subscribe, unsubscribe]);

  return {
    deviceStatuses,
    lastStatusChange,
    status,
    ...rest,
  };
};

/**
 * Hook for real-time network health updates
 */
export const useRealTimeHealth = () => {
  const [healthScore, setHealthScore] = useState<number>(100);
  const [healthStatus, setHealthStatus] = useState<
    "excellent" | "good" | "fair" | "poor"
  >("excellent");
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    if (message.type === "health_update") {
      const data = message.data as {
        score: number;
        status: "excellent" | "good" | "fair" | "poor";
      };

      setHealthScore(data.score);
      setHealthStatus(data.status);
      setLastUpdate(new Date());
    }
  }, []);

  const { status, subscribe, unsubscribe, ...rest } = useWebSocket({
    url: WS_URL,
    onMessage: handleMessage,
    autoReconnect: true,
  });

  useEffect(() => {
    // Subscribe to health room
    subscribe("health");

    return () => {
      unsubscribe("health");
    };
  }, [subscribe, unsubscribe]);

  return {
    healthScore,
    healthStatus,
    lastUpdate,
    status,
    ...rest,
  };
};

/**
 * Play alert sound for critical alerts
 */
const playAlertSound = () => {
  try {
    // Check if sounds are enabled in preferences
    const stored = localStorage.getItem("unifi_monitor_preferences");
    if (stored) {
      const preferences = JSON.parse(stored);
      if (preferences.enableSounds === false) {
        return;
      }
    }

    // Play alert sound (browser beep)
    const AudioContextClass =
      globalThis.AudioContext ||
      (
        globalThis as typeof globalThis & {
          webkitAudioContext: typeof AudioContext;
        }
      ).webkitAudioContext;
    const audioContext = new AudioContextClass();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = 800; // Frequency in Hz
    oscillator.type = "sine";

    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(
      0.01,
      audioContext.currentTime + 0.5
    );

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
  } catch (error) {
    console.warn("Failed to play alert sound:", error);
  }
};

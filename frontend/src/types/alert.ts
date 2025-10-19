/**
 * Alert-related types
 */

import type { AlertStatus, SeverityLevel } from "./common";

export interface Alert {
  id: number;
  rule_id: number;
  device_id: string | null;
  severity: SeverityLevel;
  status: AlertStatus;
  message: string;
  details: Record<string, unknown>;
  triggered_at: string;
  acknowledged_at: string | null;
  acknowledged_by: number | null;
  resolved_at: string | null;
  resolved_by: number | null;
  notification_sent: boolean;
}

export interface AlertRule {
  id: number;
  name: string;
  description: string;
  rule_type: "threshold" | "status_change";
  condition: string;
  threshold: number | null;
  severity: SeverityLevel;
  enabled: boolean;
  cooldown_minutes: number;
  created_at: string;
  updated_at: string;
}

export interface AlertStats {
  total_alerts: number;
  open_alerts: number;
  acknowledged_alerts: number;
  resolved_alerts: number;
  by_severity: {
    info: number;
    warning: number;
    critical: number;
  };
}

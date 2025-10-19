/**
 * Settings-related type definitions
 * Aligned with backend data models
 */

/**
 * Alert Rule Definition
 * Defines conditions that trigger alerts
 */
export interface AlertRule {
  id?: number;
  name: string;
  description?: string;
  rule_type: "threshold" | "status_change" | "custom";
  metric_name?: string;
  host_id?: number;
  condition: "gt" | "lt" | "eq" | "ne" | "gte" | "lte";
  threshold?: number;
  expected_status?: string;
  severity: "info" | "warning" | "critical";
  enabled: boolean;
  notification_channels: string[];
  cooldown_minutes: number;
  created_at?: string;
  updated_at?: string;
}

/**
 * Alert Rule Form Data
 * Used for create/edit forms
 */
export interface AlertRuleFormData {
  name: string;
  description?: string;
  rule_type: "threshold" | "status_change" | "custom";
  metric_name?: string;
  host_id?: number;
  condition: "gt" | "lt" | "eq" | "ne" | "gte" | "lte";
  threshold?: number;
  expected_status?: string;
  severity: "info" | "warning" | "critical";
  enabled: boolean;
  notification_channels: string[];
  cooldown_minutes: number;
}

/**
 * Notification Channel Configuration
 * Defines how notifications are delivered
 */
export interface NotificationChannel {
  id: string;
  name: string;
  channel_type: "email" | "slack" | "discord" | "webhook" | "sms";
  config:
    | EmailChannelConfig
    | WebhookChannelConfig
    | SlackChannelConfig
    | DiscordChannelConfig
    | Record<string, unknown>;
  enabled: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * Email Channel Configuration
 */
export interface EmailChannelConfig {
  smtp_host: string;
  smtp_port: number;
  smtp_user: string;
  smtp_password: string;
  from_email: string;
  to_emails: string[];
  use_tls: boolean;
}

/**
 * Webhook Channel Configuration
 */
export interface WebhookChannelConfig {
  url: string;
  method: "POST" | "PUT";
  headers?: Record<string, string>;
  auth_type?: "none" | "basic" | "bearer";
  username?: string;
  password?: string;
  token?: string;
}

/**
 * Slack Channel Configuration
 */
export interface SlackChannelConfig {
  webhook_url: string;
  channel?: string;
  username?: string;
  icon_emoji?: string;
}

/**
 * Discord Channel Configuration
 */
export interface DiscordChannelConfig {
  webhook_url: string;
  username?: string;
  avatar_url?: string;
}

/**
 * Alert Mute Configuration
 * For temporarily or permanently disabling alerts
 */
export interface AlertMute {
  id?: number;
  rule_id?: number;
  host_id?: number;
  reason?: string;
  muted_by: string;
  muted_at?: string;
  expires_at?: string;
  created_at?: string;
}

/**
 * Alert Mute Form Data
 */
export interface AlertMuteFormData {
  rule_id?: number;
  host_id?: number;
  reason?: string;
  muted_by: string;
  duration_hours?: number; // null for permanent mute
}

/**
 * User Preferences
 * Stored in local storage
 */
export interface UserPreferences {
  theme: "light" | "dark" | "auto";
  defaultTimeRange: number; // hours
  refreshInterval: number; // seconds
  enableNotifications: boolean;
  enableSounds: boolean;
  dashboardWidgets: {
    showAlerts: boolean;
    showPerformance: boolean;
    showTopology: boolean;
    showRecent: boolean;
  };
  tablePageSize: number;
  dateFormat: string;
  timeFormat: "12h" | "24h";
}

/**
 * API Response types
 */
export interface AlertRulesResponse {
  rules: AlertRule[];
  count: number;
}

export interface NotificationChannelsResponse {
  channels: NotificationChannel[];
  count: number;
}

export interface AlertMutesResponse {
  mutes: AlertMute[];
  count: number;
}

export interface ApiSuccessResponse {
  success: boolean;
  message?: string;
}

/**
 * Form field options
 */
export const RULE_TYPES = [
  { value: "threshold", label: "Threshold" },
  { value: "status_change", label: "Status Change" },
  { value: "custom", label: "Custom" },
] as const;

export const CONDITIONS = [
  { value: "gt", label: "Greater Than (>)" },
  { value: "gte", label: "Greater Than or Equal (>=)" },
  { value: "lt", label: "Less Than (<)" },
  { value: "lte", label: "Less Than or Equal (<=)" },
  { value: "eq", label: "Equal To (=)" },
  { value: "ne", label: "Not Equal To (≠)" },
] as const;

export const SEVERITIES = [
  { value: "info", label: "Info", color: "#1976D2" },
  { value: "warning", label: "Warning", color: "#F57C00" },
  { value: "critical", label: "Critical", color: "#D32F2F" },
] as const;

export const CHANNEL_TYPES = [
  { value: "email", label: "Email (SMTP)", icon: "📧" },
  { value: "slack", label: "Slack", icon: "💬" },
  { value: "discord", label: "Discord", icon: "🎮" },
  { value: "webhook", label: "Webhook", icon: "🔗" },
  { value: "sms", label: "SMS", icon: "📱" },
] as const;

export const METRIC_NAMES = [
  { value: "cpu_usage", label: "CPU Usage (%)" },
  { value: "memory_usage", label: "Memory Usage (%)" },
  { value: "temperature", label: "Temperature (°C)" },
  { value: "uptime", label: "Uptime" },
  { value: "client_count", label: "Client Count" },
] as const;

/**
 * Default user preferences
 */
export const DEFAULT_PREFERENCES: UserPreferences = {
  theme: "auto",
  defaultTimeRange: 24,
  refreshInterval: 60,
  enableNotifications: true,
  enableSounds: false,
  dashboardWidgets: {
    showAlerts: true,
    showPerformance: true,
    showTopology: true,
    showRecent: true,
  },
  tablePageSize: 10,
  dateFormat: "YYYY-MM-DD",
  timeFormat: "24h",
};

/**
 * React Query hooks for Settings API
 * Provides hooks for alert rules, notification channels, and alert mutes
 */

import type {
  AlertMute,
  AlertMuteFormData,
  AlertMutesResponse,
  AlertRule,
  AlertRuleFormData,
  AlertRulesResponse,
  ApiSuccessResponse,
  NotificationChannel,
  NotificationChannelsResponse,
} from "@/types/settings";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";

const API_BASE = "http://localhost:8000/api";

// ==================== Alert Rules ====================

/**
 * Fetch all alert rules
 */
export const useAlertRules = (enabledOnly = false) => {
  return useQuery<AlertRulesResponse>({
    queryKey: ["alertRules", enabledOnly],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE}/rules`, {
        params: { enabled_only: enabledOnly },
      });
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
};

/**
 * Fetch single alert rule by ID
 */
export const useAlertRule = (ruleId?: number) => {
  return useQuery<AlertRule>({
    queryKey: ["alertRule", ruleId],
    queryFn: async () => {
      if (!ruleId) throw new Error("Rule ID required");
      const response = await axios.get(`${API_BASE}/rules/${ruleId}`);
      return response.data;
    },
    enabled: !!ruleId,
    staleTime: 2 * 60 * 1000,
  });
};

/**
 * Create new alert rule
 */
export const useCreateAlertRule = () => {
  const queryClient = useQueryClient();

  return useMutation<
    { success: boolean; rule: AlertRule },
    Error,
    AlertRuleFormData
  >({
    mutationFn: async (data: AlertRuleFormData) => {
      const response = await axios.post(`${API_BASE}/rules`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alertRules"] });
    },
  });
};

/**
 * Update existing alert rule
 */
export const useUpdateAlertRule = () => {
  const queryClient = useQueryClient();

  return useMutation<
    { success: boolean; rule: AlertRule },
    Error,
    { id: number; data: AlertRuleFormData }
  >({
    mutationFn: async ({ id, data }) => {
      const response = await axios.put(`${API_BASE}/rules/${id}`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["alertRules"] });
      queryClient.invalidateQueries({ queryKey: ["alertRule", variables.id] });
    },
  });
};

/**
 * Delete alert rule
 */
export const useDeleteAlertRule = () => {
  const queryClient = useQueryClient();

  return useMutation<ApiSuccessResponse, Error, number>({
    mutationFn: async (ruleId: number) => {
      const response = await axios.delete(`${API_BASE}/rules/${ruleId}`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alertRules"] });
    },
  });
};

/**
 * Toggle alert rule enabled state
 */
export const useToggleAlertRule = () => {
  const queryClient = useQueryClient();

  return useMutation<
    { success: boolean; rule: AlertRule },
    Error,
    { id: number; enabled: boolean }
  >({
    mutationFn: async ({ id, enabled }) => {
      const response = await axios.patch(`${API_BASE}/rules/${id}/toggle`, {
        enabled,
      });
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["alertRules"] });
      queryClient.invalidateQueries({ queryKey: ["alertRule", variables.id] });
    },
  });
};

// ==================== Notification Channels ====================

/**
 * Fetch all notification channels
 */
export const useNotificationChannels = () => {
  return useQuery<NotificationChannelsResponse>({
    queryKey: ["notificationChannels"],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE}/channels`);
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
};

/**
 * Fetch single notification channel by ID
 */
export const useNotificationChannel = (channelId?: string) => {
  return useQuery<NotificationChannel>({
    queryKey: ["notificationChannel", channelId],
    queryFn: async () => {
      if (!channelId) throw new Error("Channel ID required");
      const response = await axios.get(`${API_BASE}/channels/${channelId}`);
      return response.data;
    },
    enabled: !!channelId,
    staleTime: 2 * 60 * 1000,
  });
};

/**
 * Create new notification channel
 */
export const useCreateNotificationChannel = () => {
  const queryClient = useQueryClient();

  return useMutation<
    { success: boolean; channel: NotificationChannel },
    Error,
    Omit<NotificationChannel, "created_at" | "updated_at">
  >({
    mutationFn: async (data) => {
      const response = await axios.post(`${API_BASE}/channels`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notificationChannels"] });
    },
  });
};

/**
 * Update existing notification channel
 */
export const useUpdateNotificationChannel = () => {
  const queryClient = useQueryClient();

  return useMutation<
    { success: boolean; channel: NotificationChannel },
    Error,
    { id: string; data: Omit<NotificationChannel, "created_at" | "updated_at"> }
  >({
    mutationFn: async ({ id, data }) => {
      const response = await axios.put(`${API_BASE}/channels/${id}`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["notificationChannels"] });
      queryClient.invalidateQueries({
        queryKey: ["notificationChannel", variables.id],
      });
    },
  });
};

/**
 * Delete notification channel
 */
export const useDeleteNotificationChannel = () => {
  const queryClient = useQueryClient();

  return useMutation<ApiSuccessResponse, Error, string>({
    mutationFn: async (channelId: string) => {
      const response = await axios.delete(`${API_BASE}/channels/${channelId}`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notificationChannels"] });
    },
  });
};

/**
 * Test notification channel
 */
export const useTestNotificationChannel = () => {
  return useMutation<ApiSuccessResponse, Error, string>({
    mutationFn: async (channelId: string) => {
      const response = await axios.post(
        `${API_BASE}/channels/${channelId}/test`
      );
      return response.data;
    },
  });
};

// ==================== Alert Mutes ====================

/**
 * Fetch all alert mutes
 */
export const useAlertMutes = (activeOnly = true) => {
  return useQuery<AlertMutesResponse>({
    queryKey: ["alertMutes", activeOnly],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE}/mutes`, {
        params: { active_only: activeOnly },
      });
      return response.data;
    },
    staleTime: 1 * 60 * 1000, // 1 minute
    refetchInterval: 2 * 60 * 1000, // Refetch every 2 minutes
  });
};

/**
 * Create new alert mute
 */
export const useCreateAlertMute = () => {
  const queryClient = useQueryClient();

  return useMutation<
    { success: boolean; mute: AlertMute },
    Error,
    AlertMuteFormData
  >({
    mutationFn: async (data: AlertMuteFormData) => {
      const response = await axios.post(`${API_BASE}/mutes`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alertMutes"] });
    },
  });
};

/**
 * Delete alert mute (unmute)
 */
export const useDeleteAlertMute = () => {
  const queryClient = useQueryClient();

  return useMutation<ApiSuccessResponse, Error, number>({
    mutationFn: async (muteId: number) => {
      const response = await axios.delete(`${API_BASE}/mutes/${muteId}`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alertMutes"] });
    },
  });
};

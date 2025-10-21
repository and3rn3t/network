/**
 * Management API - Device and Client Management Operations
 * Provides typed methods for all management operations with error handling
 */

import axios, { AxiosError } from "axios";

// ============================================================================
// Type Definitions
// ============================================================================

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface DeviceRebootRequest {
  reason?: string;
}

export interface DeviceLocateRequest {
  duration?: number; // seconds, default 30
}

export interface DeviceRenameRequest {
  name: string;
}

export interface DeviceInfoResponse {
  id: string;
  name: string;
  mac: string;
  model: string;
  type: string;
  ip: string;
  firmware_version: string;
  uptime: number;
  status: string;
  stats?: {
    cpu_usage: number;
    memory_usage: number;
    temperature: number;
    bytes_sent: number;
    bytes_received: number;
  };
  ports?: Array<{
    port_idx: number;
    name: string;
    enabled: boolean;
    up: boolean;
    speed: number;
    full_duplex: boolean;
    poe_enable: boolean;
    poe_power: number;
    rx_bytes: number;
    tx_bytes: number;
  }>;
  config?: any;
  events?: Array<{
    timestamp: string;
    type: string;
    message: string;
    severity: string;
  }>;
}

export interface BulkRebootRequest {
  device_ids: (string | number)[];
  reason?: string;
}

export interface BulkRebootResponse {
  success: number;
  failed: number;
  results: Array<{
    device_id: string | number;
    success: boolean;
    message?: string;
  }>;
}

export interface ClientBlockRequest {
  reason?: string;
  duration?: number; // seconds, 0 for permanent
}

export interface ClientBandwidthRequest {
  download_limit: number; // Kbps, 0 for unlimited
  upload_limit: number; // Kbps, 0 for unlimited
}

export interface ClientGuestAuthRequest {
  duration: number; // seconds
}

export interface BulkClientRequest {
  mac_addresses: string[];
  reason?: string;
}

export interface BulkClientResponse {
  success: number;
  failed: number;
  results: Array<{
    mac: string;
    success: boolean;
    message?: string;
  }>;
}

// ============================================================================
// Error Handling
// ============================================================================

export class ManagementApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: any
  ) {
    super(message);
    this.name = "ManagementApiError";
  }
}

const handleApiError = (error: unknown): never => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<any>;
    const message =
      axiosError.response?.data?.detail ||
      axiosError.response?.data?.message ||
      axiosError.message ||
      "An unknown error occurred";
    throw new ManagementApiError(
      message,
      axiosError.response?.status,
      axiosError.response?.data
    );
  }
  throw new ManagementApiError(
    error instanceof Error ? error.message : "An unknown error occurred"
  );
};

// ============================================================================
// Device Management API
// ============================================================================

export const deviceApi = {
  /**
   * Reboot a device
   */
  async reboot(
    deviceId: string | number,
    request: DeviceRebootRequest = {}
  ): Promise<ApiResponse> {
    try {
      const response = await axios.post(
        `/api/devices/${deviceId}/reboot`,
        request
      );
      return {
        success: true,
        data: response.data,
        message: "Device reboot initiated successfully",
      };
    } catch (error) {
      handleApiError(error);
    }
  },

  /**
   * Locate a device (blink LED)
   */
  async locate(
    deviceId: string | number,
    request: DeviceLocateRequest = { duration: 30 }
  ): Promise<ApiResponse> {
    try {
      const response = await axios.post(
        `/api/devices/${deviceId}/locate`,
        request
      );
      return {
        success: true,
        data: response.data,
        message: `Device LED blinking for ${request.duration || 30} seconds`,
      };
    } catch (error) {
      handleApiError(error);
    }
  },

  /**
   * Rename a device
   */
  async rename(
    deviceId: string | number,
    request: DeviceRenameRequest
  ): Promise<ApiResponse> {
    try {
      const response = await axios.post(
        `/api/devices/${deviceId}/rename`,
        request
      );
      return {
        success: true,
        data: response.data,
        message: `Device renamed to ${request.name}`,
      };
    } catch (error) {
      handleApiError(error);
    }
  },

  /**
   * Restart device services
   */
  async restart(deviceId: string | number): Promise<ApiResponse> {
    try {
      const response = await axios.post(`/api/devices/${deviceId}/restart`);
      return {
        success: true,
        data: response.data,
        message: "Device services restart initiated",
      };
    } catch (error) {
      handleApiError(error);
    }
  },

  /**
   * Get device information
   */
  async getInfo(deviceId: string | number): Promise<DeviceInfoResponse> {
    try {
      const response = await axios.get(`/api/devices/${deviceId}/info`);
      return response.data;
    } catch (error) {
      handleApiError(error);
    }
  },

  /**
   * Bulk reboot devices
   */
  async bulkReboot(request: BulkRebootRequest): Promise<BulkRebootResponse> {
    try {
      const response = await axios.post(`/api/devices/bulk/reboot`, request);
      return response.data;
    } catch (error) {
      handleApiError(error);
    }
  },
};

// ============================================================================
// Client Management API
// ============================================================================

export const clientApi = {
  /**
   * Block a client
   */
  async block(
    mac: string,
    request: ClientBlockRequest = {}
  ): Promise<ApiResponse> {
    try {
      const response = await axios.post(`/api/clients/${mac}/block`, request);
      return {
        success: true,
        data: response.data,
        message: request.duration
          ? `Client blocked for ${request.duration} seconds`
          : "Client blocked permanently",
      };
    } catch (error) {
      handleApiError(error);
    }
  },

  /**
   * Unblock a client
   */
  async unblock(mac: string): Promise<ApiResponse> {
    try {
      const response = await axios.post(`/api/clients/${mac}/unblock`);
      return {
        success: true,
        data: response.data,
        message: "Client unblocked successfully",
      };
    } catch (error) {
      handleApiError(error);
    }
  },

  /**
   * Reconnect a client
   */
  async reconnect(mac: string): Promise<ApiResponse> {
    try {
      const response = await axios.post(`/api/clients/${mac}/reconnect`);
      return {
        success: true,
        data: response.data,
        message: "Client reconnect initiated",
      };
    } catch (error) {
      handleApiError(error);
    }
  },

  /**
   * Set bandwidth limits for a client
   */
  async setBandwidth(
    mac: string,
    request: ClientBandwidthRequest
  ): Promise<ApiResponse> {
    try {
      const response = await axios.post(
        `/api/clients/${mac}/bandwidth`,
        request
      );
      return {
        success: true,
        data: response.data,
        message: "Bandwidth limits updated successfully",
      };
    } catch (error) {
      handleApiError(error);
    }
  },

  /**
   * Authorize guest access
   */
  async authorizeGuest(
    mac: string,
    request: ClientGuestAuthRequest
  ): Promise<ApiResponse> {
    try {
      const response = await axios.post(
        `/api/clients/${mac}/authorize-guest`,
        request
      );
      return {
        success: true,
        data: response.data,
        message: `Guest access granted for ${request.duration} seconds`,
      };
    } catch (error) {
      handleApiError(error);
    }
  },

  /**
   * Get client connection history
   */
  async getHistory(mac: string): Promise<ApiResponse> {
    try {
      const response = await axios.get(`/api/clients/${mac}/history`);
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      handleApiError(error);
    }
  },

  /**
   * Bulk block clients
   */
  async bulkBlock(request: BulkClientRequest): Promise<BulkClientResponse> {
    try {
      const response = await axios.post(`/api/clients/bulk/block`, request);
      return response.data;
    } catch (error) {
      handleApiError(error);
    }
  },

  /**
   * Bulk unblock clients
   */
  async bulkUnblock(request: BulkClientRequest): Promise<BulkClientResponse> {
    try {
      const response = await axios.post(`/api/clients/bulk/unblock`, request);
      return response.data;
    } catch (error) {
      handleApiError(error);
    }
  },

  /**
   * Bulk reconnect clients
   */
  async bulkReconnect(request: BulkClientRequest): Promise<BulkClientResponse> {
    try {
      const response = await axios.post(`/api/clients/bulk/reconnect`, request);
      return response.data;
    } catch (error) {
      handleApiError(error);
    }
  },
};

// ============================================================================
// Unified Management API Export
// ============================================================================

export const managementApi = {
  devices: deviceApi,
  clients: clientApi,
};

export default managementApi;

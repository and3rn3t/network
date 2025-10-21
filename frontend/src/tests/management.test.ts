/**
 * Integration Tests for Management API
 * Tests device and client management operations
 */

import axios from "axios";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  clientApi,
  deviceApi,
  ManagementApiError,
  type BulkClientRequest,
  type BulkRebootRequest,
} from "../api/management";

// Mock axios
vi.mock("axios");
const mockedAxios = vi.mocked(axios, true);

describe("Device Management API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("deviceApi.reboot", () => {
    it("should successfully reboot a device", async () => {
      const mockResponse = {
        data: { success: true, message: "Reboot initiated" },
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const result = await deviceApi.reboot("device-1", {
        reason: "Maintenance",
      });

      expect(result.success).toBe(true);
      expect(result.message).toBe("Device reboot initiated successfully");
      expect(mockedAxios.post).toHaveBeenCalledWith(
        "/api/devices/device-1/reboot",
        { reason: "Maintenance" }
      );
    });

    it("should handle reboot errors", async () => {
      const mockError = {
        response: {
          status: 404,
          data: { detail: "Device not found" },
        },
        isAxiosError: true,
      };
      mockedAxios.post.mockRejectedValue(mockError);
      mockedAxios.isAxiosError.mockReturnValue(true);

      await expect(deviceApi.reboot("invalid-device")).rejects.toThrow(
        ManagementApiError
      );
      await expect(deviceApi.reboot("invalid-device")).rejects.toThrow(
        "Device not found"
      );
    });
  });

  describe("deviceApi.locate", () => {
    it("should successfully locate a device", async () => {
      const mockResponse = {
        data: { success: true },
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const result = await deviceApi.locate("device-1", { duration: 60 });

      expect(result.success).toBe(true);
      expect(result.message).toContain("60 seconds");
      expect(mockedAxios.post).toHaveBeenCalledWith(
        "/api/devices/device-1/locate",
        { duration: 60 }
      );
    });

    it("should use default duration if not provided", async () => {
      const mockResponse = {
        data: { success: true },
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const result = await deviceApi.locate("device-1");

      expect(result.success).toBe(true);
      expect(result.message).toContain("30 seconds");
    });
  });

  describe("deviceApi.rename", () => {
    it("should successfully rename a device", async () => {
      const mockResponse = {
        data: { success: true, name: "New Device Name" },
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const result = await deviceApi.rename("device-1", {
        name: "New Device Name",
      });

      expect(result.success).toBe(true);
      expect(result.message).toBe("Device renamed to New Device Name");
      expect(mockedAxios.post).toHaveBeenCalledWith(
        "/api/devices/device-1/rename",
        { name: "New Device Name" }
      );
    });

    it("should handle validation errors", async () => {
      const mockError = {
        response: {
          status: 422,
          data: { detail: "Name must be 1-100 characters" },
        },
        isAxiosError: true,
      };
      mockedAxios.post.mockRejectedValue(mockError);
      mockedAxios.isAxiosError.mockReturnValue(true);

      await expect(deviceApi.rename("device-1", { name: "" })).rejects.toThrow(
        ManagementApiError
      );
    });
  });

  describe("deviceApi.restart", () => {
    it("should successfully restart device services", async () => {
      const mockResponse = {
        data: { success: true },
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const result = await deviceApi.restart("device-1");

      expect(result.success).toBe(true);
      expect(result.message).toBe("Device services restart initiated");
      expect(mockedAxios.post).toHaveBeenCalledWith(
        "/api/devices/device-1/restart"
      );
    });
  });

  describe("deviceApi.getInfo", () => {
    it("should successfully get device info", async () => {
      const mockDeviceInfo = {
        id: "device-1",
        name: "Office AP",
        mac: "00:11:22:33:44:55",
        model: "UAP-AC-PRO",
        type: "uap",
        ip: "192.168.1.10",
        firmware_version: "6.5.55",
        uptime: 86400,
        status: "online",
        stats: {
          cpu_usage: 45,
          memory_usage: 62,
          temperature: 58,
          bytes_sent: 1000000000,
          bytes_received: 2000000000,
        },
      };
      mockedAxios.get.mockResolvedValue({ data: mockDeviceInfo });

      const result = await deviceApi.getInfo("device-1");

      expect(result.id).toBe("device-1");
      expect(result.name).toBe("Office AP");
      expect(result.stats?.cpu_usage).toBe(45);
      expect(mockedAxios.get).toHaveBeenCalledWith(
        "/api/devices/device-1/info"
      );
    });

    it("should handle device not found", async () => {
      const mockError = {
        response: {
          status: 404,
          data: { detail: "Device not found" },
        },
        isAxiosError: true,
      };
      mockedAxios.get.mockRejectedValue(mockError);
      mockedAxios.isAxiosError.mockReturnValue(true);

      await expect(deviceApi.getInfo("invalid-device")).rejects.toThrow(
        ManagementApiError
      );
    });
  });

  describe("deviceApi.bulkReboot", () => {
    it("should successfully bulk reboot devices", async () => {
      const mockResponse = {
        data: {
          success: 2,
          failed: 1,
          results: [
            { device_id: "device-1", success: true },
            { device_id: "device-2", success: true },
            {
              device_id: "device-3",
              success: false,
              message: "Device offline",
            },
          ],
        },
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const request: BulkRebootRequest = {
        device_ids: ["device-1", "device-2", "device-3"],
        reason: "Bulk maintenance",
      };

      const result = await deviceApi.bulkReboot(request);

      expect(result.success).toBe(2);
      expect(result.failed).toBe(1);
      expect(result.results).toHaveLength(3);
      expect(mockedAxios.post).toHaveBeenCalledWith(
        "/api/devices/bulk/reboot",
        request
      );
    });

    it("should handle bulk reboot with no devices", async () => {
      const mockError = {
        response: {
          status: 422,
          data: { detail: "At least one device ID is required" },
        },
        isAxiosError: true,
      };
      mockedAxios.post.mockRejectedValue(mockError);
      mockedAxios.isAxiosError.mockReturnValue(true);

      await expect(deviceApi.bulkReboot({ device_ids: [] })).rejects.toThrow(
        ManagementApiError
      );
    });
  });
});

describe("Client Management API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("clientApi.block", () => {
    it("should successfully block a client permanently", async () => {
      const mockResponse = {
        data: { success: true },
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const result = await clientApi.block("aa:bb:cc:dd:ee:ff", {
        reason: "Security",
      });

      expect(result.success).toBe(true);
      expect(result.message).toContain("permanently");
      expect(mockedAxios.post).toHaveBeenCalledWith(
        "/api/clients/aa:bb:cc:dd:ee:ff/block",
        { reason: "Security" }
      );
    });

    it("should successfully block a client temporarily", async () => {
      const mockResponse = {
        data: { success: true },
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const result = await clientApi.block("aa:bb:cc:dd:ee:ff", {
        duration: 3600,
        reason: "Temporary ban",
      });

      expect(result.success).toBe(true);
      expect(result.message).toContain("3600 seconds");
    });
  });

  describe("clientApi.unblock", () => {
    it("should successfully unblock a client", async () => {
      const mockResponse = {
        data: { success: true },
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const result = await clientApi.unblock("aa:bb:cc:dd:ee:ff");

      expect(result.success).toBe(true);
      expect(result.message).toBe("Client unblocked successfully");
      expect(mockedAxios.post).toHaveBeenCalledWith(
        "/api/clients/aa:bb:cc:dd:ee:ff/unblock"
      );
    });
  });

  describe("clientApi.reconnect", () => {
    it("should successfully reconnect a client", async () => {
      const mockResponse = {
        data: { success: true },
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const result = await clientApi.reconnect("aa:bb:cc:dd:ee:ff");

      expect(result.success).toBe(true);
      expect(result.message).toBe("Client reconnect initiated");
    });
  });

  describe("clientApi.setBandwidth", () => {
    it("should successfully set bandwidth limits", async () => {
      const mockResponse = {
        data: { success: true },
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const result = await clientApi.setBandwidth("aa:bb:cc:dd:ee:ff", {
        download_limit: 50000,
        upload_limit: 10000,
      });

      expect(result.success).toBe(true);
      expect(result.message).toBe("Bandwidth limits updated successfully");
      expect(mockedAxios.post).toHaveBeenCalledWith(
        "/api/clients/aa:bb:cc:dd:ee:ff/bandwidth",
        { download_limit: 50000, upload_limit: 10000 }
      );
    });

    it("should handle invalid bandwidth values", async () => {
      const mockError = {
        response: {
          status: 422,
          data: { detail: "Bandwidth limits must be non-negative" },
        },
        isAxiosError: true,
      };
      mockedAxios.post.mockRejectedValue(mockError);
      mockedAxios.isAxiosError.mockReturnValue(true);

      await expect(
        clientApi.setBandwidth("aa:bb:cc:dd:ee:ff", {
          download_limit: -1,
          upload_limit: 10000,
        })
      ).rejects.toThrow(ManagementApiError);
    });
  });

  describe("clientApi.authorizeGuest", () => {
    it("should successfully authorize guest access", async () => {
      const mockResponse = {
        data: { success: true },
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const result = await clientApi.authorizeGuest("aa:bb:cc:dd:ee:ff", {
        duration: 3600,
      });

      expect(result.success).toBe(true);
      expect(result.message).toContain("3600 seconds");
      expect(mockedAxios.post).toHaveBeenCalledWith(
        "/api/clients/aa:bb:cc:dd:ee:ff/authorize-guest",
        { duration: 3600 }
      );
    });

    it("should handle invalid duration", async () => {
      const mockError = {
        response: {
          status: 422,
          data: {
            detail: "Duration must be between 300 and 86400 seconds",
          },
        },
        isAxiosError: true,
      };
      mockedAxios.post.mockRejectedValue(mockError);
      mockedAxios.isAxiosError.mockReturnValue(true);

      await expect(
        clientApi.authorizeGuest("aa:bb:cc:dd:ee:ff", {
          duration: 100,
        })
      ).rejects.toThrow(ManagementApiError);
    });
  });

  describe("clientApi.getHistory", () => {
    it("should successfully get client history", async () => {
      const mockHistory = {
        mac: "aa:bb:cc:dd:ee:ff",
        connections: [
          {
            timestamp: "2025-10-19T10:00:00Z",
            event: "connected",
            device: "Office AP",
          },
          {
            timestamp: "2025-10-19T09:00:00Z",
            event: "disconnected",
            device: "Office AP",
          },
        ],
      };
      mockedAxios.get.mockResolvedValue({ data: mockHistory });

      const result = await clientApi.getHistory("aa:bb:cc:dd:ee:ff");

      expect(result.success).toBe(true);
      expect(result.data.mac).toBe("aa:bb:cc:dd:ee:ff");
      expect(result.data.connections).toHaveLength(2);
    });
  });

  describe("clientApi.bulkBlock", () => {
    it("should successfully bulk block clients", async () => {
      const mockResponse = {
        data: {
          success: 2,
          failed: 1,
          results: [
            { mac: "aa:bb:cc:dd:ee:ff", success: true },
            { mac: "11:22:33:44:55:66", success: true },
            {
              mac: "99:88:77:66:55:44",
              success: false,
              message: "Client not found",
            },
          ],
        },
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const request: BulkClientRequest = {
        mac_addresses: [
          "aa:bb:cc:dd:ee:ff",
          "11:22:33:44:55:66",
          "99:88:77:66:55:44",
        ],
        reason: "Bulk security action",
      };

      const result = await clientApi.bulkBlock(request);

      expect(result.success).toBe(2);
      expect(result.failed).toBe(1);
      expect(result.results).toHaveLength(3);
      expect(mockedAxios.post).toHaveBeenCalledWith(
        "/api/clients/bulk/block",
        request
      );
    });
  });

  describe("clientApi.bulkUnblock", () => {
    it("should successfully bulk unblock clients", async () => {
      const mockResponse = {
        data: {
          success: 3,
          failed: 0,
          results: [
            { mac: "aa:bb:cc:dd:ee:ff", success: true },
            { mac: "11:22:33:44:55:66", success: true },
            { mac: "99:88:77:66:55:44", success: true },
          ],
        },
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const request: BulkClientRequest = {
        mac_addresses: [
          "aa:bb:cc:dd:ee:ff",
          "11:22:33:44:55:66",
          "99:88:77:66:55:44",
        ],
      };

      const result = await clientApi.bulkUnblock(request);

      expect(result.success).toBe(3);
      expect(result.failed).toBe(0);
    });
  });

  describe("clientApi.bulkReconnect", () => {
    it("should successfully bulk reconnect clients", async () => {
      const mockResponse = {
        data: {
          success: 2,
          failed: 1,
          results: [
            { mac: "aa:bb:cc:dd:ee:ff", success: true },
            { mac: "11:22:33:44:55:66", success: true },
            {
              mac: "99:88:77:66:55:44",
              success: false,
              message: "Client not connected",
            },
          ],
        },
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const request: BulkClientRequest = {
        mac_addresses: [
          "aa:bb:cc:dd:ee:ff",
          "11:22:33:44:55:66",
          "99:88:77:66:55:44",
        ],
      };

      const result = await clientApi.bulkReconnect(request);

      expect(result.success).toBe(2);
      expect(result.failed).toBe(1);
    });
  });
});

describe("Error Handling", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should handle network errors", async () => {
    const mockError = new Error("Network Error");
    mockedAxios.post.mockRejectedValue(mockError);
    mockedAxios.isAxiosError.mockReturnValue(false);

    await expect(deviceApi.reboot("device-1")).rejects.toThrow(
      ManagementApiError
    );
    await expect(deviceApi.reboot("device-1")).rejects.toThrow("Network Error");
  });

  it("should handle 500 server errors", async () => {
    const mockError = {
      response: {
        status: 500,
        data: { detail: "Internal Server Error" },
      },
      isAxiosError: true,
    };
    mockedAxios.post.mockRejectedValue(mockError);
    mockedAxios.isAxiosError.mockReturnValue(true);

    await expect(deviceApi.reboot("device-1")).rejects.toThrow(
      "Internal Server Error"
    );
  });

  it("should handle 401 unauthorized errors", async () => {
    const mockError = {
      response: {
        status: 401,
        data: { detail: "Unauthorized" },
      },
      isAxiosError: true,
    };
    mockedAxios.get.mockRejectedValue(mockError);
    mockedAxios.isAxiosError.mockReturnValue(true);

    await expect(deviceApi.getInfo("device-1")).rejects.toThrow("Unauthorized");
  });
});

/**
 * Clients API endpoints
 */

import type { Client } from "@/types/client";
import { apiClient } from "./client";

export interface ClientsResponse {
  clients: Client[];
  total: number;
  limit: number;
  offset: number;
}

/**
 * Get all clients
 */
export const getClients = async (): Promise<ClientsResponse> => {
  const response = await apiClient.get<ClientsResponse>("/api/clients");
  return response.data;
};

/**
 * Get single client by MAC address
 */
export const getClient = async (mac: string): Promise<Client> => {
  const response = await apiClient.get<Client>(`/api/clients/${mac}`);
  return response.data;
};

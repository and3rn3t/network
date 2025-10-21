/**
 * React Query hooks for client data
 */

import { getClient, getClients } from "@/api/clients";
import { useQuery } from "@tanstack/react-query";

/**
 * Fetch all clients
 */
export const useClients = () => {
  return useQuery({
    queryKey: ["clients"],
    queryFn: getClients,
    staleTime: 2 * 60 * 1000, // 2 minutes - clients change frequently but not instantly
  });
};

/**
 * Fetch single client by MAC address
 */
export const useClient = (mac: string | undefined) => {
  return useQuery({
    queryKey: ["client", mac],
    queryFn: () => getClient(mac!),
    enabled: !!mac, // Only fetch if mac is provided
    staleTime: 2 * 60 * 1000,
  });
};

/**
 * Authentication API endpoints
 */

import { apiClient } from "./client";

export interface LoginRequest {
  username: string;
  password: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  last_login: string | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

/**
 * Login with username and password
 */
export const login = async (data: LoginRequest): Promise<LoginResponse> => {
  const response = await apiClient.post<LoginResponse>("/api/auth/login", data);
  return response.data;
};

/**
 * Get current authenticated user
 */
export const getCurrentUser = async (): Promise<User> => {
  const response = await apiClient.get<User>("/api/auth/me");
  return response.data;
};

/**
 * Logout current user
 */
export const logout = async (): Promise<void> => {
  await apiClient.post("/api/auth/logout");
  localStorage.removeItem("auth_token");
};

/**
 * Main App component with routing and Material Design 3 theming
 */

import { AppLayout } from "@/components/layout/AppLayout";
import { LoadingFallback } from "@/components/LoadingFallback";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { ThemeProvider, useTheme } from "@/contexts/ThemeContext";
import { materialDarkTheme, materialTheme } from "@/theme/material-theme";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ConfigProvider } from "antd";
import React, { Suspense, lazy } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

// Lazy-load pages for code splitting
const Dashboard = lazy(() => import("@/pages/Dashboard"));
const Historical = lazy(() => import("@/pages/Historical"));
const Comparison = lazy(() => import("@/pages/Comparison"));
const Correlation = lazy(() => import("@/pages/Correlation"));
const Analytics = lazy(() => import("@/pages/Analytics"));
const Alerts = lazy(() => import("@/pages/Alerts"));
const Reports = lazy(() => import("@/pages/Reports"));
const Settings = lazy(() => import("@/pages/Settings"));
const DeviceManagement = lazy(() => import("./pages/DeviceManagement"));
const ClientManagement = lazy(() => import("./pages/ClientManagement"));
const Login = lazy(() => import("@/pages/Login"));

// Configure React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Protected route wrapper
const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingFallback />;
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

// Theme wrapper that applies the correct Ant Design theme
const ThemedApp: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { effectiveTheme } = useTheme();
  const antTheme =
    effectiveTheme === "dark" ? materialDarkTheme : materialTheme;

  return <ConfigProvider theme={antTheme}>{children}</ConfigProvider>;
};

function App() {
  return (
    <ThemeProvider>
      <ThemedApp>
        <QueryClientProvider client={queryClient}>
          <AuthProvider>
            <BrowserRouter>
              <Suspense fallback={<LoadingFallback />}>
                <Routes>
                  <Route path="/login" element={<Login />} />
                  <Route
                    path="/"
                    element={
                      <PrivateRoute>
                        <AppLayout />
                      </PrivateRoute>
                    }
                  >
                    <Route index element={<Dashboard />} />
                    <Route path="historical" element={<Historical />} />
                    <Route path="comparison" element={<Comparison />} />
                    <Route path="correlation" element={<Correlation />} />
                    <Route path="analytics" element={<Analytics />} />
                    <Route path="alerts" element={<Alerts />} />
                    <Route path="reports" element={<Reports />} />
                    <Route path="devices" element={<DeviceManagement />} />
                    <Route path="clients" element={<ClientManagement />} />
                    <Route path="settings" element={<Settings />} />
                  </Route>
                </Routes>
              </Suspense>
            </BrowserRouter>
          </AuthProvider>
        </QueryClientProvider>
      </ThemedApp>
    </ThemeProvider>
  );
}

export default App;

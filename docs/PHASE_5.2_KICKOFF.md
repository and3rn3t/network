# Phase 5.2: Frontend Setup - Kickoff Document

**Phase:** 5.2 - Frontend Setup
**Status:** Ready to Start
**Prerequisites:** ✅ Phase 5.1 Backend Complete
**Estimated Time:** 2-3 hours
**Last Updated:** January 2025

---

## 📋 Quick Reference

### What We're Building

A modern React + TypeScript web frontend that connects to the Phase 5.1 backend API and provides:

- 🔐 Authentication (login, token management)
- 📊 Real-time dashboard with WebSocket updates
- 🖥️ Device monitoring and management
- 🚨 Alert management interface
- ⚙️ Rule configuration UI
- 📈 Analytics and reporting views

### Success Criteria

Phase 5.2 is complete when:

- [x] Backend server running and tested (http://localhost:8000)
- [ ] React + TypeScript project initialized
- [ ] UI component library configured (Ant Design or Material-UI)
- [ ] Routing setup with protected routes
- [ ] API client service with authentication
- [ ] Login page functional
- [ ] Basic layout with navigation
- [ ] Can authenticate and access dashboard
- [ ] WebSocket connection established

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (localhost:3000)                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              React Application                       │   │
│  │                                                       │   │
│  │  ┌──────────────┐  ┌──────────────┐                │   │
│  │  │   Pages      │  │  Components  │                 │   │
│  │  │ - Dashboard  │  │ - AppLayout  │                 │   │
│  │  │ - Devices    │  │ - LoginForm  │                 │   │
│  │  │ - Alerts     │  │ - DeviceCard │                 │   │
│  │  │ - Rules      │  │ - AlertList  │                 │   │
│  │  │ - Analytics  │  │ - Charts     │                 │   │
│  │  └──────────────┘  └──────────────┘                 │   │
│  │                                                       │   │
│  │  ┌──────────────┐  ┌──────────────┐                │   │
│  │  │  Contexts    │  │   Hooks      │                 │   │
│  │  │ - AuthCtx    │  │ - useAuth    │                 │   │
│  │  │              │  │ - useDevices │                 │   │
│  │  └──────────────┘  └──────────────┘                 │   │
│  │                                                       │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │          API Layer (Axios + React Query)     │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│                           │ HTTP/REST + WebSocket            │
│                           ▼                                  │
└─────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                           │                                  │
│  ┌────────────────────────▼────────────────────────────┐   │
│  │        FastAPI Backend (localhost:8000)             │   │
│  │                                                      │   │
│  │  • REST API (25+ endpoints)                         │   │
│  │  • WebSocket Server (real-time updates)             │   │
│  │  • JWT Authentication                                │   │
│  │  • SQLite Database                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│                  Backend Server                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Core Framework

- **React 18+** - UI library with hooks and concurrent features
- **TypeScript 5+** - Type safety and better IDE support
- **Vite** - Next-generation build tool (fast, HMR, ESM-first)

### Routing

- **React Router v6** - Client-side routing with nested routes

### State Management

- **React Query** - Server state management with caching
- **React Context** - Client state (auth, theme)

### UI Components

**Choose ONE:**

1. **Ant Design** (Recommended)

   - Comprehensive component library
   - Professional design system
   - Built-in icons
   - Good TypeScript support

2. **Material-UI (MUI)**

   - Google Material Design
   - Highly customizable
   - Large community

3. **Chakra UI**
   - Simple and accessible
   - Excellent TypeScript support
   - Smaller bundle size

### HTTP Client

- **Axios** - Promise-based HTTP client with interceptors

### Charts & Visualization

- **Recharts** - Composable charting library for React

### Utilities

- **Day.js** - Lightweight date formatting (2KB vs 67KB Moment.js)
- **Lodash** - Utility functions

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/                      # API client layer
│   │   ├── client.ts            # Axios instance with interceptors
│   │   ├── auth.ts              # Auth API calls
│   │   ├── devices.ts           # Device API calls
│   │   ├── alerts.ts            # Alert API calls
│   │   ├── rules.ts             # Rule API calls
│   │   ├── channels.ts          # Channel API calls
│   │   ├── analytics.ts         # Analytics API calls
│   │   └── websocket.ts         # WebSocket client manager
│   │
│   ├── components/               # React components
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx    # Main app layout with sidebar
│   │   │   ├── Header.tsx       # Top navigation bar
│   │   │   ├── Sidebar.tsx      # Side navigation menu
│   │   │   └── Footer.tsx       # Footer component
│   │   │
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx    # Login form component
│   │   │   └── ProtectedRoute.tsx # Route guard
│   │   │
│   │   ├── dashboard/
│   │   │   ├── StatsCard.tsx    # Stat display card
│   │   │   ├── RecentAlerts.tsx # Recent alerts widget
│   │   │   └── ActivityFeed.tsx # Activity timeline
│   │   │
│   │   ├── devices/
│   │   │   ├── DeviceList.tsx   # Device table
│   │   │   ├── DeviceCard.tsx   # Device summary card
│   │   │   └── DeviceMetrics.tsx # Device metrics chart
│   │   │
│   │   ├── alerts/
│   │   │   ├── AlertList.tsx    # Alert table
│   │   │   ├── AlertCard.tsx    # Alert item
│   │   │   └── AlertActions.tsx # Acknowledge/resolve buttons
│   │   │
│   │   └── common/
│   │       ├── Loading.tsx      # Loading spinner
│   │       ├── ErrorBoundary.tsx # Error handler
│   │       └── EmptyState.tsx   # Empty state display
│   │
│   ├── pages/                    # Route pages
│   │   ├── Dashboard.tsx        # Home dashboard
│   │   ├── Devices.tsx          # Device list page
│   │   ├── DeviceDetail.tsx     # Single device page
│   │   ├── Alerts.tsx           # Alert management
│   │   ├── Rules.tsx            # Rule configuration
│   │   ├── Channels.tsx         # Notification channels
│   │   ├── Analytics.tsx        # Analytics dashboard
│   │   └── Login.tsx            # Login page
│   │
│   ├── contexts/                 # React contexts
│   │   ├── AuthContext.tsx      # Authentication state
│   │   └── ThemeContext.tsx     # Theme state (optional)
│   │
│   ├── hooks/                    # Custom hooks
│   │   ├── useAuth.ts           # Auth hook
│   │   ├── useDevices.ts        # Device data hook
│   │   ├── useAlerts.ts         # Alert data hook
│   │   ├── useRules.ts          # Rule data hook
│   │   ├── useAnalytics.ts      # Analytics data hook
│   │   └── useWebSocket.ts      # WebSocket hook
│   │
│   ├── types/                    # TypeScript types
│   │   ├── auth.ts              # Auth types
│   │   ├── device.ts            # Device types
│   │   ├── alert.ts             # Alert types
│   │   ├── rule.ts              # Rule types
│   │   ├── channel.ts           # Channel types
│   │   ├── analytics.ts         # Analytics types
│   │   └── common.ts            # Common types
│   │
│   ├── utils/                    # Utility functions
│   │   ├── constants.ts         # App constants
│   │   ├── formatters.ts        # Date/number formatters
│   │   ├── validators.ts        # Form validators
│   │   └── helpers.ts           # Helper functions
│   │
│   ├── App.tsx                   # Root component
│   ├── main.tsx                  # Entry point
│   └── vite-env.d.ts            # Vite type definitions
│
├── public/                       # Static assets
│   ├── favicon.ico
│   └── logo.png
│
├── index.html                    # HTML entry point
├── package.json                  # Dependencies
├── tsconfig.json                 # TypeScript config
├── vite.config.ts                # Vite configuration
└── README.md                     # Frontend documentation
```

---

## 🚀 Implementation Steps

### Step 1: Project Initialization (5 minutes)

```bash
# Navigate to project root
cd c:\git\network

# Create React + TypeScript project with Vite
npm create vite@latest frontend -- --template react-ts

# Navigate into project
cd frontend

# Install dependencies
npm install
```

**Deliverable:** Empty React + TypeScript project

---

### Step 2: Install Dependencies (10 minutes)

```bash
# UI Component Library (choose ONE)
npm install antd                                    # Option A: Ant Design
npm install @mui/material @emotion/react @emotion/styled  # Option B: Material-UI

# Routing
npm install react-router-dom

# API & State Management
npm install axios
npm install @tanstack/react-query  # v5 (formerly react-query)

# Charts
npm install recharts

# Icons (match your UI library)
npm install @ant-design/icons      # If using Ant Design
npm install @mui/icons-material    # If using Material-UI

# Utilities
npm install dayjs
npm install lodash

# Dev Dependencies
npm install -D @types/lodash
```

**Deliverable:** All required packages installed

---

### Step 3: Configure Vite (5 minutes)

Update `vite.config.ts`:

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/ws": {
        target: "ws://localhost:8000",
        ws: true,
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
```

Update `tsconfig.json` to add path aliases:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

**Deliverable:** Vite configured with proxy and path aliases

---

### Step 4: Create API Client (20 minutes)

**File: `src/api/client.ts`**

```typescript
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor - add JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("auth_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("auth_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);
```

**File: `src/api/auth.ts`**

```typescript
import { apiClient } from "./client";

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    username: string;
    email: string;
    is_active: boolean;
    is_superuser: boolean;
  };
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

export const login = async (data: LoginRequest): Promise<LoginResponse> => {
  const response = await apiClient.post("/api/v1/auth/login", data);
  return response.data;
};

export const getCurrentUser = async (): Promise<User> => {
  const response = await apiClient.get("/api/v1/auth/me");
  return response.data;
};

export const logout = async (): Promise<void> => {
  await apiClient.post("/api/v1/auth/logout");
  localStorage.removeItem("auth_token");
};
```

**Deliverable:** API client with authentication endpoints

---

### Step 5: TypeScript Types (15 minutes)

**File: `src/types/common.ts`**

```typescript
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export type SeverityLevel = "info" | "warning" | "critical";
export type AlertStatus = "open" | "acknowledged" | "resolved";
```

**File: `src/types/device.ts`**

```typescript
export interface Device {
  id: string;
  name: string;
  mac: string;
  ip: string;
  type: string;
  model: string;
  status: "online" | "offline";
  uptime: number;
  last_seen: string;
}

export interface DeviceMetrics {
  device_id: string;
  timestamp: string;
  cpu: number;
  memory: number;
  temperature: number;
  uptime: number;
}
```

**File: `src/types/alert.ts`**

```typescript
import { SeverityLevel, AlertStatus } from "./common";

export interface Alert {
  id: number;
  rule_id: number;
  device_id: string | null;
  severity: SeverityLevel;
  status: AlertStatus;
  message: string;
  details: Record<string, any>;
  triggered_at: string;
  acknowledged_at: string | null;
  acknowledged_by: number | null;
  resolved_at: string | null;
  resolved_by: number | null;
  notification_sent: boolean;
}
```

**Deliverable:** Type definitions for API responses

---

### Step 6: Authentication Context (30 minutes)

**File: `src/contexts/AuthContext.tsx`**

```typescript
import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { login as apiLogin, getCurrentUser, logout as apiLogout } from "../api/auth";
import type { User } from "../api/auth";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (token) {
      getCurrentUser()
        .then(setUser)
        .catch(() => localStorage.removeItem("auth_token"))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (username: string, password: string) => {
    const response = await apiLogin({ username, password });
    localStorage.setItem("auth_token", response.access_token);
    setUser(response.user);
  };

  const logout = async () => {
    try {
      await apiLogout();
    } finally {
      localStorage.removeItem("auth_token");
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};
```

**Deliverable:** Authentication context with login/logout

---

### Step 7: Layout Components (30 minutes)

**File: `src/components/layout/AppLayout.tsx`** (Ant Design version)

```typescript
import React from "react";
import { Layout, Menu } from "antd";
import { Link, Outlet, useLocation } from "react-router-dom";
import { DashboardOutlined, ApiOutlined, BellOutlined, SettingOutlined, BarChartOutlined, NotificationOutlined } from "@ant-design/icons";
import { useAuth } from "@/contexts/AuthContext";

const { Header, Sider, Content, Footer } = Layout;

export const AppLayout: React.FC = () => {
  const location = useLocation();
  const { user, logout } = useAuth();

  const menuItems = [
    { key: "/", icon: <DashboardOutlined />, label: "Dashboard" },
    { key: "/devices", icon: <ApiOutlined />, label: "Devices" },
    { key: "/alerts", icon: <BellOutlined />, label: "Alerts" },
    { key: "/rules", icon: <SettingOutlined />, label: "Rules" },
    { key: "/channels", icon: <NotificationOutlined />, label: "Channels" },
    { key: "/analytics", icon: <BarChartOutlined />, label: "Analytics" },
  ];

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider theme="dark" width={240}>
        <div
          style={{
            color: "white",
            padding: "16px",
            fontSize: "20px",
            fontWeight: "bold",
            textAlign: "center",
          }}
        >
          UniFi Monitor
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems.map((item) => ({
            ...item,
            label: <Link to={item.key}>{item.label}</Link>,
          }))}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: "#fff",
            padding: "0 24px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <h2 style={{ margin: 0 }}>UniFi Network Monitor</h2>
          <div>
            <span style={{ marginRight: 16 }}>Welcome, {user?.username}</span>
            <a onClick={logout}>Logout</a>
          </div>
        </Header>
        <Content style={{ margin: "24px", padding: 24, background: "#fff", minHeight: 280 }}>
          <Outlet />
        </Content>
        <Footer style={{ textAlign: "center" }}>UniFi Network Monitor ©{new Date().getFullYear()} | Phase 5.2</Footer>
      </Layout>
    </Layout>
  );
};
```

**Deliverable:** Basic layout with sidebar navigation

---

### Step 8: Routing Setup (20 minutes)

**File: `src/App.tsx`**

```typescript
import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { AppLayout } from "./components/layout/AppLayout";

// Lazy-load pages
const Dashboard = React.lazy(() => import("./pages/Dashboard"));
const Devices = React.lazy(() => import("./pages/Devices"));
const Alerts = React.lazy(() => import("./pages/Alerts"));
const Rules = React.lazy(() => import("./pages/Rules"));
const Channels = React.lazy(() => import("./pages/Channels"));
const Analytics = React.lazy(() => import("./pages/Analytics"));
const Login = React.lazy(() => import("./pages/Login"));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div style={{ textAlign: "center", padding: 50 }}>Loading...</div>;
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <React.Suspense fallback={<div>Loading...</div>}>
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
                <Route path="devices" element={<Devices />} />
                <Route path="alerts" element={<Alerts />} />
                <Route path="rules" element={<Rules />} />
                <Route path="channels" element={<Channels />} />
                <Route path="analytics" element={<Analytics />} />
              </Route>
            </Routes>
          </React.Suspense>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
```

**Deliverable:** Complete routing with protected routes

---

### Step 9: Login Page (30 minutes)

**File: `src/pages/Login.tsx`** (Ant Design version)

```typescript
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Form, Input, Button, Card, message } from "antd";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import { useAuth } from "@/contexts/AuthContext";

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      await login(values.username, values.password);
      message.success("Login successful!");
      navigate("/");
    } catch (error) {
      message.error("Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        background: "#f0f2f5",
      }}
    >
      <Card title="UniFi Network Monitor" style={{ width: 400 }}>
        <Form onFinish={onFinish} layout="vertical">
          <Form.Item name="username" rules={[{ required: true, message: "Please enter your username" }]}>
            <Input prefix={<UserOutlined />} placeholder="Username" size="large" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: "Please enter your password" }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="Password" size="large" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block size="large">
              Log in
            </Button>
          </Form.Item>
        </Form>
        <div style={{ textAlign: "center", marginTop: 16, color: "#888" }}>Default: admin / admin123!</div>
      </Card>
    </div>
  );
};

export default Login;
```

**Deliverable:** Functional login page with form validation

---

### Step 10: Placeholder Pages (15 minutes)

**Create placeholder pages for all routes:**

**File: `src/pages/Dashboard.tsx`**

```typescript
import React from "react";
import { Card } from "antd";

const Dashboard: React.FC = () => {
  return (
    <div>
      <h1>Dashboard</h1>
      <Card>
        <p>Welcome to UniFi Network Monitor!</p>
        <p>Phase 5.2 Setup Complete ✅</p>
      </Card>
    </div>
  );
};

export default Dashboard;
```

Repeat similar structure for:

- `src/pages/Devices.tsx`
- `src/pages/Alerts.tsx`
- `src/pages/Rules.tsx`
- `src/pages/Channels.tsx`
- `src/pages/Analytics.tsx`

**Deliverable:** All route pages created with placeholders

---

### Step 11: WebSocket Hook (30 minutes)

**File: `src/hooks/useWebSocket.ts`**

```typescript
import { useEffect, useRef, useState } from "react";

interface UseWebSocketOptions {
  url: string;
  onMessage?: (data: any) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
}

export const useWebSocket = ({ url, onMessage, onOpen, onClose, onError }: UseWebSocketOptions) => {
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    const wsUrl = `${url}?token=${token}`;

    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      setIsConnected(true);
      onOpen?.();
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage?.(data);
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };

    ws.current.onerror = (error) => {
      console.error("WebSocket error:", error);
      onError?.(error);
    };

    ws.current.onclose = () => {
      setIsConnected(false);
      onClose?.();
    };

    return () => {
      ws.current?.close();
    };
  }, [url]);

  const send = (data: any) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data));
    }
  };

  return { send, isConnected };
};
```

**Deliverable:** WebSocket hook for real-time updates

---

## ✅ Acceptance Criteria

Phase 5.2 is complete when:

### Technical Requirements

- [ ] React 18+ with TypeScript installed
- [ ] Vite configured with proxy for backend API
- [ ] UI component library (Ant Design/Material-UI) integrated
- [ ] React Router v6 with nested routes configured
- [ ] React Query for data fetching setup
- [ ] Axios client with JWT interceptors working
- [ ] Authentication context managing user state
- [ ] Protected routes redirecting to login
- [ ] WebSocket hook created

### Functional Requirements

- [ ] User can access login page at /login
- [ ] User can login with username/password (admin/admin123!)
- [ ] Successful login redirects to dashboard
- [ ] Invalid credentials show error message
- [ ] Auth token stored in localStorage
- [ ] Protected routes check authentication
- [ ] Unauthenticated users redirect to login
- [ ] User can logout and return to login
- [ ] Navigation menu shows all routes
- [ ] All page routes render (even if placeholder)

### Code Quality

- [ ] TypeScript with no compilation errors
- [ ] All components properly typed
- [ ] API responses typed with interfaces
- [ ] ESLint passing (if configured)
- [ ] No console errors in browser
- [ ] Clean code structure following project layout

---

## 🧪 Testing Checklist

### Manual Testing

**Authentication Flow:**

1. [ ] Start backend server (localhost:8000)
2. [ ] Start frontend dev server (localhost:3000)
3. [ ] Navigate to http://localhost:3000
4. [ ] Should redirect to /login
5. [ ] Try invalid credentials - should show error
6. [ ] Try valid credentials (admin/admin123!) - should login
7. [ ] Should redirect to dashboard after login
8. [ ] Refresh page - should stay logged in
9. [ ] Click logout - should return to login
10. [ ] Try accessing /devices without login - should redirect to login

**Navigation:**

1. [ ] Click each menu item in sidebar
2. [ ] Verify route changes in URL
3. [ ] Verify correct page renders
4. [ ] Use browser back/forward buttons
5. [ ] Verify menu highlights active route

**API Connection:**

1. [ ] Open browser DevTools Network tab
2. [ ] Login - verify POST to /api/v1/auth/login
3. [ ] Verify Authorization header on subsequent requests
4. [ ] Check for 401 errors (should redirect to login)

---

## 🚀 Running the Application

### Terminal 1: Backend

```bash
cd backend
python -m uvicorn src.main:app --reload --port 8000
```

**Verify:** http://localhost:8000/docs should show API documentation

### Terminal 2: Frontend

```bash
cd frontend
npm run dev
```

**Verify:** http://localhost:3000 should show the application

### Both Running Simultaneously

**Backend:** localhost:8000 (API + WebSocket)
**Frontend:** localhost:3000 (React app with Vite proxy)

---

## 📚 Next Steps (Phase 5.3)

After Phase 5.2 is complete, Phase 5.3 will implement:

1. **Dashboard Home Page**

   - Network health overview
   - Quick stats cards
   - Recent alerts
   - Activity feed

2. **Device Management**

   - Device list with real-time status
   - Device detail page with metrics
   - Charts for CPU, memory, temperature

3. **Alert Management**

   - Alert list with filtering
   - Acknowledge/resolve actions
   - Alert detail view
   - Real-time alert notifications

4. **Rule Configuration**

   - Rule list with CRUD
   - Rule creation wizard
   - Enable/disable toggle

5. **Analytics Dashboard**
   - Time-series charts
   - Trend detection
   - Anomaly highlighting
   - Forecast visualization

---

## 📖 References

### Documentation

- **Backend API:** `c:\git\network\docs\BACKEND_API_REFERENCE.md`
- **Phase 5.1 Complete:** `c:\git\network\docs\PHASE_5.1_COMPLETE.md`
- **What's Next Guide:** `c:\git\network\WHATS_NEXT.md`

### External Resources

- **React Documentation:** https://react.dev/
- **TypeScript Handbook:** https://www.typescriptlang.org/docs/
- **Vite Guide:** https://vitejs.dev/guide/
- **React Router:** https://reactrouter.com/
- **React Query:** https://tanstack.com/query/latest
- **Ant Design:** https://ant.design/components/overview/
- **Material-UI:** https://mui.com/components/
- **Axios:** https://axios-http.com/docs/intro

---

## 🎯 Success Metrics

- ✅ Frontend app running without errors
- ✅ User can login and access dashboard
- ✅ All routes accessible with navigation
- ✅ API calls working with authentication
- ✅ Clean project structure ready for Phase 5.3
- ✅ TypeScript compilation successful
- ✅ No console errors in browser

---

**Ready to start? Follow the implementation steps and check off each deliverable!**

**Document Version:** 1.0
**Author:** GitHub Copilot
**Last Updated:** January 2025

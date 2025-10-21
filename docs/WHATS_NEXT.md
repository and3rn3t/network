# What's Next - Phase 5.2: Frontend Development 🎨

**Current Status:** ✅ Phase 5.1 Backend Complete
**Next Phase:** Phase 5.2 - Frontend Setup
**Estimated Time:** 2-3 hours

---

## 🎯 Strategic Vision

**Build a historical analysis dashboard that complements (not duplicates) the UniFi WiFi app.**

### What Makes This Unique

The UniFi app is excellent for **real-time management**. Our dashboard focuses on:

- 📊 **Historical Analysis** - Long-term trends, performance over time
- 🔍 **Deep Analytics** - Anomaly detection, statistical analysis, forecasting
- 📈 **Custom Reporting** - Flexible time ranges, exportable data
- 🚨 **Alert Intelligence** - Pattern recognition, alert effectiveness analysis
- 📉 **Performance Trends** - Degradation detection, capacity planning
- 🔬 **Data Mining** - Correlations, predictive insights

**Read the full strategy:** [`docs/FRONTEND_STRATEGY.md`](docs/FRONTEND_STRATEGY.md)

---

## 🎯 Phase 5.2 Objectives

Build the foundation for a historical analysis and insights platform.

### Goals

1. ✅ Initialize React + TypeScript project
2. ✅ Set up routing and navigation
3. ✅ Install charting library optimized for time-series data
4. ✅ Create API client for historical data queries
5. ✅ Implement authentication context
6. ✅ Build basic layout structure---

## 🛠️ Technology Stack

### Core Framework

- **React 18+** - UI library
- **TypeScript 5+** - Type safety
- **Vite** - Build tool (fast, modern)

### UI Components

**Choose one:**

- **Ant Design** (Recommended) - Comprehensive, professional
- **Material-UI** - Google Material Design
- **Chakra UI** - Simple, accessible

### Additional Libraries

- **React Router v6** - Navigation
- **Axios** - HTTP client
- **React Query** - Data fetching & caching
- **Recharts** - Charts and graphs
- **WebSocket** - Real-time updates

---

## � Step-by-Step Setup

### 1. Create React Project (5 minutes)

```bash

```

### 2. Install Dependencies (10 minutes)

```bash
# UI Component Library (choose one)
npm install antd  # Ant Design (Recommended)
# OR
npm install @mui/material @emotion/react @emotion/styled

# Routing
npm install react-router-dom

# API & State Management
npm install axios react-query

# Charts
npm install recharts

# Icons
npm install @ant-design/icons  # if using Ant Design
# OR
npm install @mui/icons-material  # if using Material-UI

# Utilities
npm install dayjs  # Date formatting
npm install lodash  # Utility functions
```

### 3. Project Structure (15 minutes)

Create this folder structure:

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts         # Axios instance
│   │   ├── auth.ts           # Auth API calls
│   │   ├── devices.ts        # Device API calls
│   │   ├── alerts.ts         # Alert API calls
│   │   └── websocket.ts      # WebSocket client
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   ├── auth/
│   │   │   └── LoginForm.tsx
│   │   └── common/
│   │       ├── Loading.tsx
│   │       └── ErrorBoundary.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Devices.tsx
│   │   ├── Alerts.tsx
│   │   ├── Rules.tsx
│   │   ├── Analytics.tsx
│   │   └── Login.tsx
│   ├── contexts/
│   │   └── AuthContext.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useDevices.ts
│   │   ├── useAlerts.ts
│   │   └── useWebSocket.ts
│   ├── types/
│   │   ├── auth.ts
│   │   ├── device.ts
│   │   ├── alert.ts
│   │   └── common.ts
│   ├── utils/
│   │   ├── constants.ts
│   │   ├── formatters.ts
│   │   └── validators.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

### 4. Configure Vite (5 minutes)

Update `vite.config.ts`:

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

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
});
```

### 5. Create API Client (20 minutes)

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

// Request interceptor - add auth token
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

// Response interceptor - handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem("auth_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);
```

### 6. Authentication Context (30 minutes)

**File: `src/contexts/AuthContext.tsx`**

```typescript
import React, { createContext, useContext, useState, useEffect } from "react";
import { login as apiLogin, getCurrentUser } from "../api/auth";

interface User {
  id: number;
  username: string;
  email: string;
  is_superuser: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
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
    const response = await apiLogin(username, password);
    localStorage.setItem("auth_token", response.access_token);
    setUser(response.user);
  };

  const logout = () => {
    localStorage.removeItem("auth_token");
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAuthenticated: !!user,
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

### 7. Create Basic Layout (30 minutes)

**File: `src/components/layout/AppLayout.tsx`**

```typescript
import React from "react";
import { Layout, Menu } from "antd";
import { Link, Outlet } from "react-router-dom";
import { DashboardOutlined, ApiOutlined, BellOutlined, SettingOutlined, BarChartOutlined } from "@ant-design/icons";

const { Header, Sider, Content } = Layout;

export const AppLayout: React.FC = () => {
  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider theme="dark">
        <div style={{ color: "white", padding: "16px", fontSize: "18px" }}>UniFi Monitor</div>
        <Menu theme="dark" mode="inline" defaultSelectedKeys={["dashboard"]}>
          <Menu.Item key="dashboard" icon={<DashboardOutlined />}>
            <Link to="/">Dashboard</Link>
          </Menu.Item>
          <Menu.Item key="devices" icon={<ApiOutlined />}>
            <Link to="/devices">Devices</Link>
          </Menu.Item>
          <Menu.Item key="alerts" icon={<BellOutlined />}>
            <Link to="/alerts">Alerts</Link>
          </Menu.Item>
          <Menu.Item key="rules" icon={<SettingOutlined />}>
            <Link to="/rules">Rules</Link>
          </Menu.Item>
          <Menu.Item key="analytics" icon={<BarChartOutlined />}>
            <Link to="/analytics">Analytics</Link>
          </Menu.Item>
        </Menu>
      </Sider>
      <Layout>
        <Header style={{ background: "#fff", padding: "0 16px" }}>UniFi Network Monitor</Header>
        <Content style={{ margin: "24px 16px", padding: 24, background: "#fff" }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};
```

### 8. Set Up Routing (20 minutes)

**File: `src/App.tsx`**

```typescript
import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "react-query";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { AppLayout } from "./components/layout/AppLayout";
import Dashboard from "./pages/Dashboard";
import Devices from "./pages/Devices";
import Alerts from "./pages/Alerts";
import Rules from "./pages/Rules";
import Analytics from "./pages/Analytics";
import Login from "./pages/Login";

const queryClient = new QueryClient();

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) return <div>Loading...</div>;
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
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
              <Route path="analytics" element={<Analytics />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
```

---

## 🎨 Next Steps After Setup

Once the basic structure is in place, focus on **historical analysis features**:

### Phase 5.3: Historical Analysis Dashboard (Priority 1)

1. **Historical Performance Trends** (6 hours)

   - Device CPU usage over time (7/30/90 day charts)
   - Memory utilization trends with forecasting
   - Temperature trends with anomaly highlighting
   - Multi-device comparison view
   - Flexible time range selector (custom dates)
   - Export to CSV/JSON for external analysis

2. **Device Health Timeline** (4 hours)

   - Device availability tracking (uptime over time)
   - Offline incident history with duration
   - Historical reliability metrics
   - Before/after comparison (firmware updates, config changes)

3. **Capacity Planning Dashboard** (4 hours)

   - Resource growth trends (CPU, memory over months)
   - "When will device reach 80% capacity?" predictions
   - Year-over-year comparison charts
   - Proactive upgrade recommendations

### Phase 5.4: Analytics Engine (Priority 2)

4. **Anomaly Detection Dashboard** (5 hours)

   - Visual anomaly highlighting on charts
   - Automatic baseline learning
   - "What's unusual right now?" summary
   - Anomaly history and pattern recognition
   - Correlation analysis (multiple devices acting strange)

5. **Statistical Analysis** (4 hours)

   - Percentile reports (95th, 99th percentile)
   - Standard deviation tracking
   - Moving averages (7-day, 30-day smoothing)
   - Trend direction indicators (improving/worsening)

### Phase 5.5: Alert Intelligence (Priority 3)

6. **Alert Analytics Dashboard** (5 hours)

   - Alert frequency trends (last 90 days)
   - Alert type distribution (pie charts)
   - MTTA/MTTR tracking by alert type
   - Alert effectiveness scoring
   - Pattern recognition (recurring alert sequences)

7. **Alert History & Correlation** (4 hours)

   - Visual alert timeline (drill-down by device/type)
   - Alert correlation matrix (which alerts happen together?)
   - Root cause analysis visualization
   - Alert storm detection and analysis

### Phase 5.6: Reporting & Data Export (Priority 4)

8. **Custom Report Builder** (4 hours)

   - Flexible metric and time range selection
   - Multi-format export (CSV, JSON, PDF)
   - Scheduled report generation
   - Report templates library

---

## 🎯 Key Differentiators from UniFi App

**Focus Areas (What We Build):**

- ✅ Historical data visualization (trends over weeks/months)
- ✅ Statistical analysis and anomaly detection
- ✅ Predictive insights and forecasting
- ✅ Alert pattern analysis and intelligence
- ✅ Data export for external analysis
- ✅ Custom time range reporting

**Avoid Building (Already in UniFi App):**

- ❌ Real-time device configuration
- ❌ Firmware updates and device management
- ❌ Client blocking/unblocking
- ❌ Network configuration (SSIDs, VLANs)
- ❌ Mobile-first push notifications

**Our Value:** Historical context, insights, predictions, and data liberation

- Forecast graphs

---

## � Running the Application

### Development Mode

**Terminal 1 - Backend:**

```bash
cd backend
python -m uvicorn src.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm run dev
```

Access the app at: http://localhost:3000

### Production Build

```bash
cd frontend
npm run build
```

Serve the `dist/` directory with any static file server.

---

## 📚 Resources

### Documentation

- **Backend API:** `docs/BACKEND_API_REFERENCE.md`
- **Phase 5.1 Complete:** `docs/PHASE_5.1_COMPLETE.md`

### UI Libraries

- **Ant Design:** https://ant.design/components/overview/
- **Material-UI:** https://mui.com/components/
- **Recharts:** https://recharts.org/en-US/

### React Resources

- **React Docs:** https://react.dev/
- **TypeScript:** https://www.typescriptlang.org/docs/
- **React Router:** https://reactrouter.com/
- **React Query:** https://tanstack.com/query/latest

---

## ✅ Checklist

Before starting Phase 5.2:

- [x] Phase 5.1 Backend complete
- [x] Backend server running at http://localhost:8000
- [x] Authentication working (admin/admin123!)
- [x] API documentation reviewed
- [ ] Node.js installed (v18+)
- [ ] npm or yarn installed
- [ ] Code editor ready (VS Code recommended)

---

## 🎯 Success Criteria

Phase 5.2 is complete when:

- [ ] React + TypeScript project initialized
- [ ] UI component library installed and configured
- [ ] Routing set up with all main pages
- [ ] API client service created
- [ ] Authentication context working
- [ ] Login page functional
- [ ] Basic layout with navigation
- [ ] Can login and access protected routes
- [ ] WebSocket connection established

---

**Ready to build the frontend?** Let's create something beautiful! 🎨

---

**Document Version:** 1.0
**Last Updated:** January 2025
**Next Phase:** Phase 5.2 - Frontend Setup

---

## 📖 Additional Resources (Legacy)

The following sections are from the original Phase 1-4 implementation and may still be useful for understanding the backend API:

### API Exploration

    # Your code here!
    print("🚀 Starting my UniFi tool...")

    # Example: Get all hosts
    hosts = client.get_hosts()
    print(f"Found {len(hosts)} devices")

    # Add your logic here

if **name** == "**main**":
main()

````

Save as `examples/my_tool.py` and run it!

---

## 📊 Recommended Learning Path

### Week 1: Basics

- ✅ Day 1: Configuration (Done!)
- 📅 Day 2: List devices and understand response structure
- 📅 Day 3: Get detailed device information
- 📅 Day 4: Explore different endpoints with REST Client
- 📅 Day 5: Read API documentation thoroughly

### Week 2: Intermediate

- 📅 Day 1: Write a device health monitoring script
- 📅 Day 2: Implement error handling and logging
- 📅 Day 3: Add retry logic for API calls
- 📅 Day 4: Create a report generator (CSV/JSON)
- 📅 Day 5: Build a simple dashboard script

### Week 3: Advanced

- 📅 Day 1: Implement caching for performance
- 📅 Day 2: Add rate limiting
- 📅 Day 3: Create scheduled automation
- 📅 Day 4: Build a CLI tool with argparse
- 📅 Day 5: Package your tool for reuse

---

## 🎓 Learning Resources

### In This Repository

- `docs/API_REFERENCE.md` - Complete endpoint reference
- `docs/FEATURES.md` - Feature ideas and use cases
- `docs/QUICKSTART.md` - Getting started guide
- `docs/CONFIGURATION.md` - Configuration options
- `api_explorer.http` - Interactive API testing

### External Resources

- [UniFi API Documentation](https://unifi.ui.com/api-docs)
- [UniFi Community Forums](https://community.ui.com)
- [Python Requests Documentation](https://requests.readthedocs.io)

---

## 🚦 Next Action Items

Choose your path:

### 🟢 **Beginner** - Learn the Basics

```bash
# Run this next:
python examples/list_hosts.py
````

Then open and read the response structure.

### 🟡 **Intermediate** - Build Something

Create a script that:

1. Lists all devices
2. Checks which are offline
3. Sends you a report

### 🔴 **Advanced** - Automate

Build a monitoring system that:

1. Polls devices every 5 minutes
2. Logs status changes
3. Alerts on issues
4. Generates daily reports

---

## 💬 Common Next Questions

### "What can I actually do with this API?"

Check `docs/FEATURES.md` for a comprehensive list of capabilities.

### "How do I know what endpoints are available?"

Check `docs/API_REFERENCE.md` or use the `api_explorer.http` file.

### "Can I automate [specific task]?"

Most likely yes! The API supports:

- Device management
- Configuration changes
- Client monitoring
- Network operations
- Firmware updates

### "Where do I go for help?"

1. Check the documentation in `docs/`
2. Review example scripts in `examples/`
3. Use GitHub Copilot to ask questions
4. Check UniFi Community forums

---

## 🎉 Recommended First Project

**Build a Device Health Dashboard**

1. List all devices
2. Show online/offline status
3. Display uptime and versions
4. Highlight devices needing updates
5. Export to a simple HTML report

This will teach you:

- API calls
- Data processing
- Error handling
- Output formatting

**Estimated time:** 2-3 hours

---

## ⚡ Quick Commands Reference

```bash
# Check configuration
python examples/check_config.py

# List devices
python examples/list_hosts.py

# Get device details
python examples/get_device_info.py

# Run your custom script
python examples/my_tool.py

# Enable debug logging (in config.py)
# Change: LOG_LEVEL = "DEBUG"
```

---

## 📈 Track Your Progress

- [ ] Configuration working ✅
- [ ] Listed all devices
- [ ] Retrieved device details
- [ ] Explored with REST Client
- [ ] Built first custom script
- [ ] Implemented error handling
- [ ] Added logging
- [ ] Created automation
- [ ] Built monitoring tool
- [ ] Shared with community

---

## 🎯 Your Immediate Next Step

**Run this command right now:**

```bash
python examples/list_hosts.py
```

This will show you your actual network devices and give you data to work with!

After that, open `api_explorer.http` and start clicking "Send Request" on different endpoints to see what data is available.

**Happy exploring! 🚀**

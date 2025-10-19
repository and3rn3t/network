/**
 * Main application layout with navigation
 */

import { useAuth } from "@/contexts/AuthContext";
import {
  BarChartOutlined,
  BellOutlined,
  DashboardOutlined,
  ExportOutlined,
  LineChartOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { Layout, Menu } from "antd";
import React from "react";
import { Link, Outlet, useLocation } from "react-router-dom";

const { Header, Sider, Content, Footer } = Layout;

export const AppLayout: React.FC = () => {
  const location = useLocation();
  const { user, logout } = useAuth();

  const menuItems = [
    {
      key: "/",
      icon: <DashboardOutlined />,
      label: <Link to="/">Dashboard</Link>,
    },
    {
      key: "/historical",
      icon: <LineChartOutlined />,
      label: <Link to="/historical">Historical Analysis</Link>,
    },
    {
      key: "/analytics",
      icon: <BarChartOutlined />,
      label: <Link to="/analytics">Analytics</Link>,
    },
    {
      key: "/alerts",
      icon: <BellOutlined />,
      label: <Link to="/alerts">Alert Intelligence</Link>,
    },
    {
      key: "/reports",
      icon: <ExportOutlined />,
      label: <Link to="/reports">Reports & Export</Link>,
    },
    {
      key: "/settings",
      icon: <SettingOutlined />,
      label: <Link to="/settings">Settings</Link>,
    },
  ];

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider theme="dark" width={250}>
        <div
          style={{
            color: "white",
            padding: "20px",
            fontSize: "20px",
            fontWeight: "bold",
            textAlign: "center",
            borderBottom: "1px solid rgba(255, 255, 255, 0.1)",
          }}
        >
          📊 UniFi Insights
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
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
            boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
          }}
        >
          <h2 style={{ margin: 0, fontSize: "18px", color: "#1890ff" }}>
            Historical Analysis & Insights Platform
          </h2>
          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            <span style={{ color: "#666" }}>
              Welcome, <strong>{user?.username}</strong>
            </span>
            <a onClick={logout} style={{ cursor: "pointer", color: "#1890ff" }}>
              Logout
            </a>
          </div>
        </Header>
        <Content
          style={{
            margin: "24px",
            padding: 24,
            background: "#fff",
            minHeight: 280,
            borderRadius: "8px",
          }}
        >
          <Outlet />
        </Content>
        <Footer style={{ textAlign: "center", color: "#666" }}>
          UniFi Network Insights Platform ©{new Date().getFullYear()} |
          Complement to UniFi App
        </Footer>
      </Layout>
    </Layout>
  );
};

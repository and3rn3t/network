/**
 * Main application layout with navigation - Material Design 3
 */

import { ThemeToggle } from "@/components/ThemeToggle";
import { useAuth } from "@/contexts/AuthContext";
import { useRealTimeAlerts } from "@/hooks/useRealTime";
import {
  BarChartOutlined,
  BellOutlined,
  DashboardOutlined,
  DotChartOutlined,
  ExportOutlined,
  LineChartOutlined,
  LogoutOutlined,
  SettingOutlined,
  SwapOutlined,
  UserOutlined,
} from "@ant-design/icons";
import type { MenuProps } from "antd";
import { Avatar, Badge, Button, Dropdown, Layout, Menu } from "antd";
import React from "react";
import { Link, Outlet, useLocation } from "react-router-dom";
import "./AppLayout.css";
import { ConnectionStatus } from "./ConnectionStatus";

const { Header, Sider, Content, Footer } = Layout;

export const AppLayout: React.FC = () => {
  const location = useLocation();
  const { user, logout } = useAuth();
  const { newAlertCount } = useRealTimeAlerts();

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
      key: "/comparison",
      icon: <SwapOutlined />,
      label: <Link to="/comparison">Device Comparison</Link>,
    },
    {
      key: "/correlation",
      icon: <DotChartOutlined />,
      label: <Link to="/correlation">Correlation Analysis</Link>,
    },
    {
      key: "/analytics",
      icon: <BarChartOutlined />,
      label: <Link to="/analytics">Analytics</Link>,
    },
    {
      key: "/alerts",
      icon: <BellOutlined />,
      label: (
        <Badge count={newAlertCount} offset={[10, 0]}>
          <Link to="/alerts">Alert Intelligence</Link>
        </Badge>
      ),
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

  const userMenuItems: MenuProps["items"] = [
    {
      key: "profile",
      icon: <UserOutlined />,
      label: "Profile",
      disabled: true,
    },
    {
      type: "divider",
    },
    {
      key: "logout",
      icon: <LogoutOutlined />,
      label: "Logout",
      onClick: () => {
        void logout();
      },
      danger: true,
    },
  ];

  return (
    <Layout className="app-layout">
      <Sider className="app-sider" theme="dark" width={280}>
        <div className="app-logo">
          <div className="app-logo-icon">📊</div>
          <div className="app-logo-text">
            <div className="app-logo-title">UniFi Insights</div>
            <div className="app-logo-subtitle">Network Analytics</div>
          </div>
        </div>
        <Menu
          className="app-menu"
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
        />
      </Sider>
      <Layout>
        <Header className="app-header">
          <div className="app-header-title">
            <h1 className="app-header-text">Historical Analysis & Insights</h1>
            <p className="app-header-subtitle">
              Deep network analytics and trend analysis
            </p>
          </div>
          <div className="app-header-actions">
            <ConnectionStatus />
            <ThemeToggle variant="button" />
            <Button type="text" icon={<BellOutlined />} size="large">
              <Badge count={newAlertCount} offset={[0, 0]} />
            </Button>
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <Button
                type="text"
                size="large"
                className="app-header-user-button"
              >
                <Avatar
                  icon={<UserOutlined />}
                  style={{
                    backgroundColor: "var(--md-sys-color-primary)",
                  }}
                />
                <span className="app-header-username">{user?.username}</span>
              </Button>
            </Dropdown>
          </div>
        </Header>
        <Content className="app-content">
          <Outlet />
        </Content>
        <Footer className="app-footer">
          <div className="app-footer-content">
            <span className="app-footer-text">
              UniFi Network Insights Platform ©{new Date().getFullYear()}
            </span>
            <span className="app-footer-divider">•</span>
            <span className="app-footer-tagline">Complement to UniFi App</span>
          </div>
        </Footer>
      </Layout>
    </Layout>
  );
};

/**
 * Main application layout with navigation - Material Design 3
 */

import { GlobalFilterBar } from "@/components/filters/GlobalFilterBar";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useAuth } from "@/contexts/AuthContext";
import { usePageMetadata } from "@/contexts/PageMetadataContext";
import { useRealTimeAlerts } from "@/hooks/useRealTime";
import {
  BarChartOutlined,
  BellOutlined,
  DashboardOutlined,
  DotChartOutlined,
  ExportOutlined,
  HddOutlined,
  LineChartOutlined,
  LogoutOutlined,
  NotificationOutlined,
  SettingOutlined,
  SwapOutlined,
  TeamOutlined,
  ThunderboltOutlined,
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
  const { metadata } = usePageMetadata();

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
          Alert System
        </Badge>
      ),
      children: [
        {
          key: "/alerts",
          icon: <BellOutlined />,
          label: <Link to="/alerts">Active Alerts</Link>,
        },
        {
          key: "/rules",
          icon: <ThunderboltOutlined />,
          label: <Link to="/rules">Alert Rules</Link>,
        },
        {
          key: "/channels",
          icon: <NotificationOutlined />,
          label: <Link to="/channels">Notification Channels</Link>,
        },
      ],
    },
    {
      key: "/devices",
      icon: <HddOutlined />,
      label: <Link to="/devices">Device Management</Link>,
    },
    {
      key: "/clients",
      icon: <TeamOutlined />,
      label: <Link to="/clients">Client Management</Link>,
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
          <div className="app-header-info">
            {metadata.breadcrumbs && metadata.breadcrumbs.length > 0 && (
              <div className="app-header-breadcrumbs">
                {metadata.breadcrumbs.map((crumb, index) => (
                  <span key={crumb.path ?? crumb.label}>
                    {crumb.path ? <Link to={crumb.path}>{crumb.label}</Link> : crumb.label}
                    {index < metadata.breadcrumbs!.length - 1 && (
                      <span className="app-header-breadcrumb-separator">/</span>
                    )}
                  </span>
                ))}
              </div>
            )}
            <div className="app-header-title">
              {metadata.icon && (
                <span className="app-header-icon" aria-hidden>
                  {metadata.icon}
                </span>
              )}
              <div>
                <h1 className="app-header-text">{metadata.title}</h1>
                {metadata.description && (
                  <p className="app-header-subtitle">{metadata.description}</p>
                )}
              </div>
            </div>
          </div>
          <div className="app-header-actions">
            {metadata.actions && (
              <div className="app-header-custom-actions">{metadata.actions}</div>
            )}
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
          {metadata.showFilters && (
            <GlobalFilterBar config={metadata.filtersConfig} />
          )}
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

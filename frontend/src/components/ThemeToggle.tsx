/**
 * Theme Toggle Component
 * Allows users to switch between light, dark, and system theme
 */

import { useTheme } from "@/contexts/ThemeContext";
import { BulbOutlined, MoonOutlined, SunOutlined } from "@ant-design/icons";
import { Segmented, Tooltip } from "antd";
import React from "react";
import "./ThemeToggle.css";

interface ThemeToggleProps {
  variant?: "button" | "segmented";
  size?: "small" | "middle" | "large";
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({
  variant = "segmented",
  size = "middle",
}) => {
  const { theme, effectiveTheme, setTheme } = useTheme();

  if (variant === "button") {
    // Simple toggle button (cycles through themes)
    const getNextTheme = () => {
      if (theme === "light") {
        return "dark";
      }
      if (theme === "dark") {
        return "system";
      }
      return "light";
    };

    const getIcon = () => {
      if (effectiveTheme === "dark") {
        return <MoonOutlined />;
      }
      return <SunOutlined />;
    };

    const getTooltip = () => {
      if (theme === "system") {
        return `System (${effectiveTheme})`;
      }
      return theme === "dark" ? "Dark Mode" : "Light Mode";
    };

    return (
      <Tooltip title={getTooltip()}>
        <button
          type="button"
          className="theme-toggle-button"
          onClick={() => {
            setTheme(getNextTheme());
          }}
          aria-label="Toggle theme"
        >
          {getIcon()}
        </button>
      </Tooltip>
    );
  }

  // Segmented control with all three options
  return (
    <Segmented
      size={size}
      value={theme}
      onChange={(value) => {
        setTheme(value as "light" | "dark" | "system");
      }}
      options={[
        {
          label: (
            <Tooltip title="Light Mode">
              <span className="theme-toggle-option">
                <SunOutlined />
                <span className="theme-toggle-label">Light</span>
              </span>
            </Tooltip>
          ),
          value: "light",
        },
        {
          label: (
            <Tooltip title="Dark Mode">
              <span className="theme-toggle-option">
                <MoonOutlined />
                <span className="theme-toggle-label">Dark</span>
              </span>
            </Tooltip>
          ),
          value: "dark",
        },
        {
          label: (
            <Tooltip title="Follow System">
              <span className="theme-toggle-option">
                <BulbOutlined />
                <span className="theme-toggle-label">System</span>
              </span>
            </Tooltip>
          ),
          value: "system",
        },
      ]}
      className="theme-toggle-segmented"
    />
  );
};

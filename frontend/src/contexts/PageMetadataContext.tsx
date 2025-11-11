import {
  AlertOutlined,
  ApiOutlined,
  BarChartOutlined,
  BellOutlined,
  BranchesOutlined,
  BuildOutlined,
  CloudDownloadOutlined,
  DashboardOutlined,
  DotChartOutlined,
  LineChartOutlined,
  SettingOutlined,
  SwapOutlined,
  TeamOutlined,
} from "@ant-design/icons";
import type { ReactNode } from "react";
import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useLocation } from "react-router-dom";

export interface BreadcrumbItem {
  label: string;
  path?: string;
}

export interface GlobalFilterConfig {
  showSitePicker?: boolean;
  siteOptions?: Array<{ value: string; label: string }>;
  sitePlaceholder?: string;
}

export interface PageMetadata {
  title: string;
  description?: string;
  icon?: ReactNode;
  breadcrumbs?: BreadcrumbItem[];
  actions?: ReactNode;
  showFilters?: boolean;
  filtersConfig?: GlobalFilterConfig;
}

interface PageMetadataContextValue {
  metadata: PageMetadata;
  setMetadata: (updates: Partial<PageMetadata>) => void;
  resetMetadata: () => void;
}

const DEFAULT_METADATA: PageMetadata = {
  title: "UniFi Insights",
  description: "Network analytics platform",
  icon: <DashboardOutlined />,
  showFilters: false,
};

const normalizePath = (path: string): string => {
  if (path.length > 1 && path.endsWith("/")) {
    return path.slice(0, -1);
  }
  return path;
};

const ROUTE_DEFAULTS: Record<string, PageMetadata> = {
  "/": {
    title: "Network Health Overview",
    description: "Live operational snapshot with real-time telemetry",
    icon: <DashboardOutlined />,
    showFilters: false,
  },
  "/historical": {
    title: "Client Performance History",
    description:
      "Analyze long-term client trends to spot recurring WiFi issues",
    icon: <LineChartOutlined />,
    showFilters: true,
    filtersConfig: {
      showSitePicker: false,
    },
  },
  "/comparison": {
    title: "Client Performance Comparison",
    description: "Compare key metrics across multiple clients over time",
    icon: <SwapOutlined />,
    showFilters: true,
    filtersConfig: {
      showSitePicker: false,
    },
  },
  "/correlation": {
    title: "Correlation Analysis",
    description:
      "Reveal relationships between network metrics and device behavior",
    icon: <DotChartOutlined />,
    showFilters: true,
    filtersConfig: {
      showSitePicker: false,
    },
  },
  "/analytics": {
    title: "Advanced Analytics",
    description: "Run statistical analysis, anomaly detection, and forecasting",
    icon: <BarChartOutlined />,
    showFilters: true,
    filtersConfig: {
      showSitePicker: false,
    },
  },
  "/alerts": {
    title: "Active Alerts",
    description: "Monitor and triage current alert activity across the network",
    icon: <BellOutlined />,
    showFilters: false,
  },
  "/rules": {
    title: "Alert Rules",
    description: "Manage alert thresholds, cooldowns, and notification routing",
    icon: <AlertOutlined />,
    showFilters: false,
  },
  "/channels": {
    title: "Notification Channels",
    description: "Configure how notifications reach your team",
    icon: <BranchesOutlined />,
    showFilters: false,
  },
  "/reports": {
    title: "Reports & Exports",
    description: "Build exports and scheduled summaries for stakeholders",
    icon: <CloudDownloadOutlined />,
    showFilters: true,
    filtersConfig: {
      showSitePicker: false,
    },
  },
  "/devices": {
    title: "Device Management",
    description: "Perform management operations on UniFi devices",
    icon: <BuildOutlined />,
    showFilters: false,
  },
  "/clients": {
    title: "Client Management",
    description: "Manage client connectivity, bandwidth, and policies",
    icon: <TeamOutlined />,
    showFilters: false,
  },
  "/settings": {
    title: "Settings",
    description: "Customize application preferences and integrations",
    icon: <SettingOutlined />,
    showFilters: false,
  },
  "/analytics/predictive": {
    title: "Predictive Insights",
    description: "Forecast capacity needs and detect early warning signals",
    icon: <ApiOutlined />,
    showFilters: true,
    filtersConfig: {
      showSitePicker: false,
    },
  },
};

const PageMetadataContext = createContext<PageMetadataContextValue | undefined>(
  undefined
);

const getDefaultMetadataForPath = (path: string): PageMetadata => {
  const normalized = normalizePath(path);
  return ROUTE_DEFAULTS[normalized] ?? DEFAULT_METADATA;
};

export const PageMetadataProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const location = useLocation();
  const [metadata, setMetadataState] = useState<PageMetadata>(() =>
    getDefaultMetadataForPath(location.pathname)
  );

  useEffect(() => {
    setMetadataState(getDefaultMetadataForPath(location.pathname));
  }, [location.pathname]);

  const setMetadata = useCallback((updates: Partial<PageMetadata>) => {
    setMetadataState((current) => ({
      ...current,
      ...updates,
    }));
  }, []);

  const resetMetadata = useCallback(() => {
    setMetadataState(getDefaultMetadataForPath(location.pathname));
  }, [location.pathname]);

  const contextValue = useMemo<PageMetadataContextValue>(
    () => ({
      metadata,
      setMetadata,
      resetMetadata,
    }),
    [metadata, resetMetadata, setMetadata]
  );

  return (
    <PageMetadataContext.Provider value={contextValue}>
      {children}
    </PageMetadataContext.Provider>
  );
};

export const usePageMetadata = (): PageMetadataContextValue => {
  const context = useContext(PageMetadataContext);

  if (!context) {
    throw new Error(
      "usePageMetadata must be used within a PageMetadataProvider"
    );
  }

  return context;
};

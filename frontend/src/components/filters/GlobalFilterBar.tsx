import { MaterialCard } from "@/components/MaterialCard";
import { TimeRangeSelector } from "@/components/TimeRangeSelector";
import { useGlobalFilters } from "@/contexts/GlobalFilterContext";
import type { GlobalFilterConfig } from "@/contexts/PageMetadataContext";
import {
  ClockCircleOutlined,
  EnvironmentOutlined,
  FilterOutlined,
} from "@ant-design/icons";
import { Select, Space, Tag, Typography } from "antd";
import React, { useMemo } from "react";

interface GlobalFilterBarProps {
  config?: GlobalFilterConfig;
}

export const GlobalFilterBar: React.FC<GlobalFilterBarProps> = ({ config }) => {
  const { timeRange, setTimeRange, siteId, setSiteId } = useGlobalFilters();
  const { showSitePicker, siteOptions, sitePlaceholder } = config ?? {};

  const normalizedSiteOptions = useMemo(
    () => siteOptions?.filter((option) => option.value && option.label) ?? [],
    [siteOptions]
  );

  const hasSiteOptions = showSitePicker && normalizedSiteOptions.length > 0;
  const siteValue = siteId ?? "all";

  return (
    <MaterialCard elevation={1} className="global-filter-bar">
      <Space direction="vertical" size="large" className="global-filter-stack">
        <div className="global-filter-heading">
          <FilterOutlined className="global-filter-icon" />
          <div>
            <Typography.Title level={5} className="global-filter-title">
              Global Filters
            </Typography.Title>
            <Typography.Text
              type="secondary"
              className="global-filter-subtitle"
            >
              Applies to analytics views across the dashboard
            </Typography.Text>
          </div>
        </div>

        <Space size="large" wrap className="global-filter-row">
          <div className="global-filter-section">
            <Typography.Text strong>Time Range</Typography.Text>
            <Tag
              icon={<ClockCircleOutlined />}
              className="global-filter-tag"
              color="var(--md-sys-color-primary-container)"
            >
              {timeRange.label}
            </Tag>
            <TimeRangeSelector
              onChange={setTimeRange}
              defaultHours={timeRange.hours ?? 24}
              showQuickOptions
              size="middle"
            />
          </div>

          {showSitePicker && (
            <div className="global-filter-section">
              <Typography.Text strong>Site</Typography.Text>
              <Select
                className="global-filter-select"
                value={siteValue}
                size="large"
                onChange={(value) => {
                  if (value === "all") {
                    setSiteId(null);
                  } else {
                    setSiteId(value);
                  }
                }}
                options={
                  hasSiteOptions
                    ? normalizedSiteOptions
                    : [{ value: "all", label: "All Sites" }]
                }
                suffixIcon={<EnvironmentOutlined />}
                placeholder={sitePlaceholder ?? "Select site"}
                disabled={!hasSiteOptions}
                allowClear={false}
              />
              {!hasSiteOptions && (
                <Typography.Text
                  type="secondary"
                  className="global-filter-hint"
                >
                  Add site metadata to enable site filtering
                </Typography.Text>
              )}
            </div>
          )}
        </Space>
      </Space>
    </MaterialCard>
  );
};

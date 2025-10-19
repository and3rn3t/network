/**
 * Time Range Selector component
 * Provides preset and custom time range selection with enhanced options
 */

import { CalendarOutlined, ClockCircleOutlined } from "@ant-design/icons";
import type { RadioChangeEvent } from "antd";
import { DatePicker, Radio, Space, Tooltip, Typography } from "antd";
import dayjs, { Dayjs } from "dayjs";
import { useState } from "react";

const { RangePicker } = DatePicker;
const { Text } = Typography;

export interface TimeRange {
  hours: number;
  label: string;
  start?: Dayjs;
  end?: Dayjs;
}

interface TimeRangeSelectorProps {
  onChange?: (range: TimeRange) => void;
  defaultHours?: number;
  showQuickOptions?: boolean;
  size?: "small" | "middle" | "large";
}

const PRESET_RANGES = [
  { hours: 1, label: "Last Hour", shortLabel: "1h" },
  { hours: 6, label: "Last 6 Hours", shortLabel: "6h" },
  { hours: 24, label: "Last 24 Hours", shortLabel: "24h" },
  { hours: 24 * 7, label: "Last 7 Days", shortLabel: "7d" },
  { hours: 24 * 30, label: "Last 30 Days", shortLabel: "30d" },
];

const QUICK_RANGES = {
  Today: [dayjs().startOf("day"), dayjs()],
  Yesterday: [
    dayjs().subtract(1, "day").startOf("day"),
    dayjs().subtract(1, "day").endOf("day"),
  ],
  "This Week": [dayjs().startOf("week"), dayjs()],
  "Last Week": [
    dayjs().subtract(1, "week").startOf("week"),
    dayjs().subtract(1, "week").endOf("week"),
  ],
  "This Month": [dayjs().startOf("month"), dayjs()],
  "Last Month": [
    dayjs().subtract(1, "month").startOf("month"),
    dayjs().subtract(1, "month").endOf("month"),
  ],
};

export const TimeRangeSelector: React.FC<TimeRangeSelectorProps> = ({
  onChange,
  defaultHours = 24,
  showQuickOptions = false,
  size = "large",
}) => {
  const [selectedPreset, setSelectedPreset] = useState<number>(defaultHours);
  const [customRange, setCustomRange] = useState<[Dayjs, Dayjs] | null>(null);
  const [isCustom, setIsCustom] = useState(false);

  const handlePresetChange = (e: RadioChangeEvent) => {
    const hours = e.target.value;
    setSelectedPreset(hours);
    setIsCustom(false);
    setCustomRange(null);

    const preset = PRESET_RANGES.find((r) => r.hours === hours);
    if (preset && onChange) {
      onChange({
        hours: preset.hours,
        label: preset.label,
      });
    }
  };

  const handleCustomRangeChange = (
    dates: [Dayjs | null, Dayjs | null] | null
  ) => {
    if (dates && dates[0] && dates[1]) {
      const validRange: [Dayjs, Dayjs] = [dates[0], dates[1]];
      setCustomRange(validRange);
      const [start, end] = validRange;
      const hours = end.diff(start, "hour");

      if (onChange) {
        onChange({
          hours,
          label: `${start.format("MMM D, YYYY HH:mm")} - ${end.format(
            "MMM D, YYYY HH:mm"
          )}`,
          start,
          end,
        });
      }
    } else {
      setCustomRange(null);
    }
  };

  const handleCustomToggle = () => {
    setIsCustom(true);
    setSelectedPreset(-1);
  };

  return (
    <Space direction="vertical" style={{ width: "100%" }} size="middle">
      {/* Preset time ranges */}
      <div>
        <Text
          type="secondary"
          style={{ fontSize: "12px", marginBottom: "8px", display: "block" }}
        >
          <ClockCircleOutlined /> Quick Select
        </Text>
        <Radio.Group
          value={isCustom ? -1 : selectedPreset}
          onChange={handlePresetChange}
          buttonStyle="solid"
          size={size}
        >
          {PRESET_RANGES.map((range) => (
            <Tooltip key={range.hours} title={range.label}>
              <Radio.Button value={range.hours}>
                {range.shortLabel}
              </Radio.Button>
            </Tooltip>
          ))}
          <Radio.Button value={-1} onClick={handleCustomToggle}>
            <CalendarOutlined /> Custom
          </Radio.Button>
        </Radio.Group>
      </div>

      {/* Custom date range picker */}
      {isCustom && (
        <div>
          <Text
            type="secondary"
            style={{ fontSize: "12px", marginBottom: "8px", display: "block" }}
          >
            Select Date Range
          </Text>
          <RangePicker
            value={customRange}
            onChange={handleCustomRangeChange}
            showTime={{ format: "HH:mm" }}
            format="YYYY-MM-DD HH:mm"
            style={{ width: "100%" }}
            size={size}
            disabledDate={(current) => {
              // Disable future dates
              return current && current > dayjs().endOf("day");
            }}
            presets={
              showQuickOptions
                ? Object.entries(QUICK_RANGES).map(([label, range]) => ({
                    label,
                    value: range as [Dayjs, Dayjs],
                  }))
                : undefined
            }
            allowClear
          />
        </div>
      )}
    </Space>
  );
};

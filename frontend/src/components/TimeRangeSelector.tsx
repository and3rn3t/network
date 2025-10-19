/**
 * Time Range Selector component
 * Provides preset and custom time range selection
 */

import type { RadioChangeEvent } from "antd";
import { DatePicker, Radio, Space } from "antd";
import dayjs, { Dayjs } from "dayjs";
import { useState } from "react";

const { RangePicker } = DatePicker;

export interface TimeRange {
  hours: number;
  label: string;
  start?: Dayjs;
  end?: Dayjs;
}

interface TimeRangeSelectorProps {
  onChange?: (range: TimeRange) => void;
}

const PRESET_RANGES = [
  { hours: 24, label: "Last 24 Hours" },
  { hours: 24 * 7, label: "Last 7 Days" },
  { hours: 24 * 30, label: "Last 30 Days" },
  { hours: 24 * 90, label: "Last 90 Days" },
];

export const TimeRangeSelector: React.FC<TimeRangeSelectorProps> = ({
  onChange,
}) => {
  const [selectedPreset, setSelectedPreset] = useState<number>(24);
  const [customRange, setCustomRange] = useState<[Dayjs, Dayjs] | null>(null);
  const [isCustom, setIsCustom] = useState(false);

  const handlePresetChange = (e: RadioChangeEvent) => {
    const hours = e.target.value;
    setSelectedPreset(hours);
    setIsCustom(false);
    setCustomRange(null);

    const preset = PRESET_RANGES.find((r) => r.hours === hours);
    if (preset && onChange) {
      onChange(preset);
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
          label: "Custom Range",
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
    <Space direction="vertical" style={{ width: "100%" }}>
      <Radio.Group
        value={isCustom ? -1 : selectedPreset}
        onChange={handlePresetChange}
        buttonStyle="solid"
      >
        {PRESET_RANGES.map((range) => (
          <Radio.Button key={range.hours} value={range.hours}>
            {range.label}
          </Radio.Button>
        ))}
        <Radio.Button value={-1} onClick={handleCustomToggle}>
          Custom Range
        </Radio.Button>
      </Radio.Group>

      {isCustom && (
        <RangePicker
          value={customRange}
          onChange={handleCustomRangeChange}
          showTime
          format="YYYY-MM-DD HH:mm"
          style={{ width: "100%" }}
          disabledDate={(current) => {
            // Disable future dates
            return current && current > dayjs().endOf("day");
          }}
        />
      )}
    </Space>
  );
};

/**
 * Enhanced Time Range Selector with Comparison Mode
 * Allows selecting two time ranges for before/after analysis
 */

import {
  CalendarOutlined,
  ClockCircleOutlined,
  InfoCircleOutlined,
  SwapOutlined,
} from "@ant-design/icons";
import {
  Card,
  Col,
  DatePicker,
  Radio,
  Row,
  Space,
  Switch,
  Tag,
  Tooltip,
  Typography,
} from "antd";
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

export interface ComparisonTimeRanges {
  primary: TimeRange;
  comparison?: TimeRange;
}

interface EnhancedTimeRangeSelectorProps {
  onChange?: (ranges: ComparisonTimeRanges) => void;
  defaultHours?: number;
  allowComparison?: boolean;
  size?: "small" | "middle" | "large";
}

const PRESET_RANGES = [
  { hours: 1, label: "Last Hour", shortLabel: "1h" },
  { hours: 6, label: "Last 6 Hours", shortLabel: "6h" },
  { hours: 24, label: "Last 24 Hours", shortLabel: "24h" },
  { hours: 24 * 7, label: "Last 7 Days", shortLabel: "7d" },
  { hours: 24 * 30, label: "Last 30 Days", shortLabel: "30d" },
];

export const EnhancedTimeRangeSelector: React.FC<
  EnhancedTimeRangeSelectorProps
> = ({
  onChange,
  defaultHours = 24,
  allowComparison = false,
  size = "large",
}) => {
  const [primaryPreset, setPrimaryPreset] = useState<number>(defaultHours);
  const [primaryCustom, setPrimaryCustom] = useState<[Dayjs, Dayjs] | null>(
    null
  );
  const [isPrimaryCustom, setIsPrimaryCustom] = useState(false);

  const [comparisonEnabled, setComparisonEnabled] = useState(false);
  const [comparisonPreset, setComparisonPreset] =
    useState<number>(defaultHours);
  const [comparisonCustom, setComparisonCustom] = useState<
    [Dayjs, Dayjs] | null
  >(null);
  const [isComparisonCustom, setIsComparisonCustom] = useState(false);

  const getPrimaryRange = (): TimeRange => {
    if (isPrimaryCustom && primaryCustom) {
      const [start, end] = primaryCustom;
      return {
        hours: end.diff(start, "hour"),
        label: `${start.format("MMM D")} - ${end.format("MMM D")}`,
        start,
        end,
      };
    }
    const preset = PRESET_RANGES.find((r) => r.hours === primaryPreset);
    return preset || PRESET_RANGES[2];
  };

  const getComparisonRange = (): TimeRange | undefined => {
    if (!comparisonEnabled) return undefined;

    if (isComparisonCustom && comparisonCustom) {
      const [start, end] = comparisonCustom;
      return {
        hours: end.diff(start, "hour"),
        label: `${start.format("MMM D")} - ${end.format("MMM D")}`,
        start,
        end,
      };
    }
    const preset = PRESET_RANGES.find((r) => r.hours === comparisonPreset);
    return preset;
  };

  const notifyChange = () => {
    if (onChange) {
      onChange({
        primary: getPrimaryRange(),
        comparison: getComparisonRange(),
      });
    }
  };

  const handlePrimaryPresetChange = (hours: number) => {
    setPrimaryPreset(hours);
    setIsPrimaryCustom(false);
    setPrimaryCustom(null);
    setTimeout(notifyChange, 0);
  };

  const handlePrimaryCustomChange = (
    dates: [Dayjs | null, Dayjs | null] | null
  ) => {
    if (dates && dates[0] && dates[1]) {
      setPrimaryCustom([dates[0], dates[1]]);
      setTimeout(notifyChange, 0);
    }
  };

  const handleComparisonToggle = (checked: boolean) => {
    setComparisonEnabled(checked);
    setTimeout(notifyChange, 0);
  };

  const handleComparisonPresetChange = (hours: number) => {
    setComparisonPreset(hours);
    setIsComparisonCustom(false);
    setComparisonCustom(null);
    setTimeout(notifyChange, 0);
  };

  const handleComparisonCustomChange = (
    dates: [Dayjs | null, Dayjs | null] | null
  ) => {
    if (dates && dates[0] && dates[1]) {
      setComparisonCustom([dates[0], dates[1]]);
      setTimeout(notifyChange, 0);
    }
  };

  return (
    <Space direction="vertical" style={{ width: "100%" }} size="large">
      {/* Primary Time Range */}
      <Card
        size="small"
        title={
          <Space>
            <ClockCircleOutlined />
            <Text strong>Primary Time Range</Text>
          </Space>
        }
      >
        <Space direction="vertical" style={{ width: "100%" }} size="middle">
          <Radio.Group
            value={isPrimaryCustom ? -1 : primaryPreset}
            onChange={(e) => handlePrimaryPresetChange(e.target.value)}
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
            <Radio.Button value={-1} onClick={() => setIsPrimaryCustom(true)}>
              <CalendarOutlined /> Custom
            </Radio.Button>
          </Radio.Group>

          {isPrimaryCustom && (
            <RangePicker
              value={primaryCustom}
              onChange={handlePrimaryCustomChange}
              showTime={{ format: "HH:mm" }}
              format="YYYY-MM-DD HH:mm"
              style={{ width: "100%" }}
              size={size}
              disabledDate={(current) =>
                current && current > dayjs().endOf("day")
              }
            />
          )}
        </Space>
      </Card>

      {/* Comparison Mode */}
      {allowComparison && (
        <Card
          size="small"
          title={
            <Row justify="space-between" align="middle">
              <Col>
                <Space>
                  <SwapOutlined />
                  <Text strong>Comparison Mode</Text>
                  <Tooltip title="Compare two different time periods">
                    <InfoCircleOutlined
                      style={{ color: "rgba(0, 0, 0, 0.45)" }}
                    />
                  </Tooltip>
                </Space>
              </Col>
              <Col>
                <Switch
                  checked={comparisonEnabled}
                  onChange={handleComparisonToggle}
                  checkedChildren="ON"
                  unCheckedChildren="OFF"
                />
              </Col>
            </Row>
          }
        >
          {comparisonEnabled ? (
            <Space direction="vertical" style={{ width: "100%" }} size="middle">
              <div>
                <Text type="secondary" style={{ fontSize: "12px" }}>
                  Select a second time range to compare against the primary
                  range
                </Text>
              </div>

              <Radio.Group
                value={isComparisonCustom ? -1 : comparisonPreset}
                onChange={(e) => handleComparisonPresetChange(e.target.value)}
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
                <Radio.Button
                  value={-1}
                  onClick={() => setIsComparisonCustom(true)}
                >
                  <CalendarOutlined /> Custom
                </Radio.Button>
              </Radio.Group>

              {isComparisonCustom && (
                <RangePicker
                  value={comparisonCustom}
                  onChange={handleComparisonCustomChange}
                  showTime={{ format: "HH:mm" }}
                  format="YYYY-MM-DD HH:mm"
                  style={{ width: "100%" }}
                  size={size}
                  disabledDate={(current) =>
                    current && current > dayjs().endOf("day")
                  }
                />
              )}

              {comparisonEnabled && (
                <div>
                  <Tag color="blue">Primary: {getPrimaryRange().label}</Tag>
                  {getComparisonRange() && (
                    <Tag color="green">
                      Comparison: {getComparisonRange()?.label}
                    </Tag>
                  )}
                </div>
              )}
            </Space>
          ) : (
            <Text type="secondary">
              Enable comparison mode to analyze two time periods side by side
            </Text>
          )}
        </Card>
      )}
    </Space>
  );
};

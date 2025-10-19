/**
 * Correlation Scatter Plot Component
 * Shows relationship between two metrics with correlation coefficient
 */

import { Alert, Card, Col, Row, Spin, Statistic, Typography } from "antd";
import { useMemo } from "react";
import {
  CartesianGrid,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const { Text } = Typography;

interface MetricPoint {
  timestamp: string;
  value: number;
}

interface CorrelationScatterPlotProps {
  xAxisData: MetricPoint[];
  yAxisData: MetricPoint[];
  xAxisLabel: string;
  yAxisLabel: string;
  xAxisUnit?: string;
  yAxisUnit?: string;
  deviceName?: string;
  loading?: boolean;
  error?: any;
}

interface ScatterDataPoint {
  x: number;
  y: number;
  timestamp: string;
}

interface CorrelationStats {
  coefficient: number;
  strength: string;
  direction: string;
  rSquared: number;
  slope: number;
  intercept: number;
}

// Calculate Pearson correlation coefficient
const calculateCorrelation = (data: ScatterDataPoint[]): CorrelationStats => {
  const n = data.length;
  if (n < 2) {
    return {
      coefficient: 0,
      strength: "Insufficient Data",
      direction: "None",
      rSquared: 0,
      slope: 0,
      intercept: 0,
    };
  }

  const sumX = data.reduce((sum, point) => sum + point.x, 0);
  const sumY = data.reduce((sum, point) => sum + point.y, 0);
  const sumXY = data.reduce((sum, point) => sum + point.x * point.y, 0);
  const sumX2 = data.reduce((sum, point) => sum + point.x * point.x, 0);
  const sumY2 = data.reduce((sum, point) => sum + point.y * point.y, 0);

  const numerator = n * sumXY - sumX * sumY;
  const denominator = Math.sqrt(
    (n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY)
  );

  const coefficient = denominator === 0 ? 0 : numerator / denominator;

  // Calculate linear regression for trend line
  const meanX = sumX / n;
  const meanY = sumY / n;
  const slope =
    denominator === 0
      ? 0
      : (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
  const intercept = meanY - slope * meanX;

  // Determine correlation strength
  const absCorr = Math.abs(coefficient);
  let strength = "";
  if (absCorr >= 0.9) strength = "Very Strong";
  else if (absCorr >= 0.7) strength = "Strong";
  else if (absCorr >= 0.5) strength = "Moderate";
  else if (absCorr >= 0.3) strength = "Weak";
  else strength = "Very Weak";

  const direction =
    coefficient > 0 ? "Positive" : coefficient < 0 ? "Negative" : "None";

  return {
    coefficient,
    strength,
    direction,
    rSquared: coefficient * coefficient,
    slope,
    intercept,
  };
};

export const CorrelationScatterPlot: React.FC<CorrelationScatterPlotProps> = ({
  xAxisData,
  yAxisData,
  xAxisLabel,
  yAxisLabel,
  xAxisUnit = "",
  yAxisUnit = "",
  deviceName = "Device",
  loading = false,
  error = null,
}) => {
  // Merge data by timestamp
  const scatterData = useMemo(() => {
    const dataMap = new Map<string, { x?: number; y?: number }>();

    xAxisData.forEach((point) => {
      dataMap.set(point.timestamp, { x: point.value });
    });

    yAxisData.forEach((point) => {
      const existing = dataMap.get(point.timestamp);
      if (existing) {
        existing.y = point.value;
      } else {
        dataMap.set(point.timestamp, { y: point.value });
      }
    });

    // Filter to only points with both x and y values
    const result: ScatterDataPoint[] = [];
    dataMap.forEach((value, timestamp) => {
      if (value.x !== undefined && value.y !== undefined) {
        result.push({ x: value.x, y: value.y, timestamp });
      }
    });

    return result;
  }, [xAxisData, yAxisData]);

  const stats = useMemo(() => calculateCorrelation(scatterData), [scatterData]);

  // Calculate trend line points
  const trendLineData = useMemo(() => {
    if (scatterData.length < 2) return [];

    const xValues = scatterData.map((d) => d.x);
    const minX = Math.min(...xValues);
    const maxX = Math.max(...xValues);

    return [
      { x: minX, y: stats.slope * minX + stats.intercept },
      { x: maxX, y: stats.slope * maxX + stats.intercept },
    ];
  }, [scatterData, stats]);

  if (loading) {
    return (
      <Card
        title={`${xAxisLabel} vs ${yAxisLabel} - ${deviceName}`}
        style={{ marginBottom: "24px" }}
      >
        <div style={{ textAlign: "center", padding: "50px" }}>
          <Spin size="large" tip="Loading correlation data..." />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card
        title={`${xAxisLabel} vs ${yAxisLabel} - ${deviceName}`}
        style={{ marginBottom: "24px" }}
      >
        <Alert
          message="Error Loading Data"
          description="Failed to load correlation data. Please try again."
          type="error"
          showIcon
        />
      </Card>
    );
  }

  if (scatterData.length === 0) {
    return (
      <Card
        title={`${xAxisLabel} vs ${yAxisLabel} - ${deviceName}`}
        style={{ marginBottom: "24px" }}
      >
        <Alert
          message="No Data Available"
          description="No matching data points found for correlation analysis."
          type="info"
          showIcon
        />
      </Card>
    );
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;
    return (
      <div
        style={{
          backgroundColor: "white",
          border: "1px solid #ccc",
          padding: "10px",
          borderRadius: "4px",
        }}
      >
        <p style={{ margin: 0, fontWeight: "bold", marginBottom: "5px" }}>
          Data Point
        </p>
        <p style={{ margin: 0 }}>
          {xAxisLabel}: {data.x.toFixed(2)} {xAxisUnit}
        </p>
        <p style={{ margin: 0 }}>
          {yAxisLabel}: {data.y.toFixed(2)} {yAxisUnit}
        </p>
      </div>
    );
  };

  // Determine correlation color
  const getCorrelationColor = () => {
    const absCorr = Math.abs(stats.coefficient);
    if (absCorr >= 0.7) return "#52c41a"; // Green for strong
    if (absCorr >= 0.5) return "#1890ff"; // Blue for moderate
    if (absCorr >= 0.3) return "#faad14"; // Orange for weak
    return "#ff4d4f"; // Red for very weak
  };

  return (
    <Card
      title={`${xAxisLabel} vs ${yAxisLabel} - ${deviceName}`}
      style={{ marginBottom: "24px" }}
    >
      {/* Statistics */}
      <Row gutter={16} style={{ marginBottom: "24px" }}>
        <Col span={6}>
          <Statistic
            title="Correlation"
            value={stats.coefficient.toFixed(3)}
            valueStyle={{ color: getCorrelationColor() }}
            prefix={
              stats.direction === "Positive"
                ? "+"
                : stats.direction === "Negative"
                ? "-"
                : ""
            }
          />
          <Text type="secondary" style={{ fontSize: "12px" }}>
            {stats.strength} {stats.direction}
          </Text>
        </Col>
        <Col span={6}>
          <Statistic
            title="R² Value"
            value={(stats.rSquared * 100).toFixed(1)}
            suffix="%"
            valueStyle={{ color: "#1890ff" }}
          />
          <Text type="secondary" style={{ fontSize: "12px" }}>
            Variance Explained
          </Text>
        </Col>
        <Col span={6}>
          <Statistic
            title="Data Points"
            value={scatterData.length}
            valueStyle={{ color: "#722ed1" }}
          />
          <Text type="secondary" style={{ fontSize: "12px" }}>
            Matching Timestamps
          </Text>
        </Col>
        <Col span={6}>
          <Statistic
            title="Trend Slope"
            value={stats.slope.toFixed(3)}
            valueStyle={{ color: "#13c2c2" }}
          />
          <Text type="secondary" style={{ fontSize: "12px" }}>
            Rate of Change
          </Text>
        </Col>
      </Row>

      {/* Scatter Plot */}
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            type="number"
            dataKey="x"
            name={xAxisLabel}
            label={{
              value: `${xAxisLabel} (${xAxisUnit})`,
              position: "bottom",
            }}
            domain={["auto", "auto"]}
          />
          <YAxis
            type="number"
            dataKey="y"
            name={yAxisLabel}
            label={{
              value: `${yAxisLabel} (${yAxisUnit})`,
              angle: -90,
              position: "insideLeft",
            }}
            domain={["auto", "auto"]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />

          {/* Trend line */}
          {trendLineData.length === 2 && (
            <ReferenceLine
              segment={trendLineData}
              stroke="#ff7875"
              strokeWidth={2}
              strokeDasharray="5 5"
              label="Trend"
            />
          )}

          {/* Data points */}
          <Scatter
            name={`${xAxisLabel} vs ${yAxisLabel}`}
            data={scatterData}
            fill={getCorrelationColor()}
            fillOpacity={0.6}
          />
        </ScatterChart>
      </ResponsiveContainer>

      {/* Interpretation */}
      <Alert
        message="Correlation Interpretation"
        description={
          <div>
            <p style={{ margin: "8px 0" }}>
              <strong>Correlation:</strong>{" "}
              {Math.abs(stats.coefficient).toFixed(3)} ({stats.strength}{" "}
              {stats.direction})
            </p>
            <p style={{ margin: "8px 0" }}>
              <strong>Meaning:</strong>{" "}
              {stats.direction === "Positive" &&
                `As ${xAxisLabel} increases, ${yAxisLabel} tends to increase.`}
              {stats.direction === "Negative" &&
                `As ${xAxisLabel} increases, ${yAxisLabel} tends to decrease.`}
              {stats.direction === "None" &&
                `No linear relationship detected between ${xAxisLabel} and ${yAxisLabel}.`}
            </p>
            <p style={{ margin: "8px 0" }}>
              <strong>R² Value:</strong> {(stats.rSquared * 100).toFixed(1)}% of
              the variance in {yAxisLabel} can be explained by {xAxisLabel}.
            </p>
          </div>
        }
        type="info"
        showIcon
        style={{ marginTop: "16px" }}
      />
    </Card>
  );
};

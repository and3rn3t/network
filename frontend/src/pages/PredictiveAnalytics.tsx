/**
 * Predictive Analytics Page
 * 
 * Displays forecasting, capacity planning, anomaly detection, and failure predictions.
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Select,
  DatePicker,
  Typography,
  Alert,
  Spin,
  Progress,
  Tag,
  Table,
  Space,
  Statistic,
  Divider,
} from 'antd';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  WarningOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ThunderboltOutlined,
  TrendingUp,
  TrendingDown,
  Assessment,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { MaterialCard } from '@/components/MaterialCard';
import { useDevices } from '@/hooks/useDevices';
import {
  getForecast,
  getCapacityForecast,
  detectAnomalies,
  predictFailure,
  getNetworkInsights,
} from '@/api/analytics';
import './PredictiveAnalytics.css';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

const PredictiveAnalytics: React.FC = () => {
  const { data: devicesData, isLoading: devicesLoading } = useDevices();
  const [selectedDevice, setSelectedDevice] = useState<number | null>(null);
  const [selectedMetric, setSelectedMetric] = useState<string>('bandwidth');
  const [forecastDays, setForecastDays] = useState<number>(30);
  
  // Data states
  const [forecast, setForecast] = useState<any>(null);
  const [capacityForecast, setCapacityForecast] = useState<any>(null);
  const [anomalies, setAnomalies] = useState<any>(null);
  const [failurePrediction, setFailurePrediction] = useState<any>(null);
  const [networkInsights, setNetworkInsights] = useState<any>(null);
  
  // Loading states
  const [loadingForecast, setLoadingForecast] = useState(false);
  const [loadingCapacity, setLoadingCapacity] = useState(false);
  const [loadingAnomalies, setLoadingAnomalies] = useState(false);
  const [loadingFailure, setLoadingFailure] = useState(false);
  const [loadingInsights, setLoadingInsights] = useState(false);

  // Load network insights on mount
  useEffect(() => {
    loadNetworkInsights();
  }, []);

  // Load device-specific analytics when device or metric changes
  useEffect(() => {
    if (selectedDevice) {
      loadDeviceAnalytics();
    }
  }, [selectedDevice, selectedMetric, forecastDays]);

  const loadNetworkInsights = async () => {
    setLoadingInsights(true);
    try {
      const data = await getNetworkInsights();
      setNetworkInsights(data);
    } catch (error) {
      console.error('Failed to load network insights:', error);
    } finally {
      setLoadingInsights(false);
    }
  };

  const loadDeviceAnalytics = async () => {
    if (!selectedDevice) return;

    // Load forecast
    setLoadingForecast(true);
    try {
      const forecastData = await getForecast(selectedDevice, selectedMetric, forecastDays);
      setForecast(forecastData);
    } catch (error) {
      console.error('Failed to load forecast:', error);
      setForecast(null);
    } finally {
      setLoadingForecast(false);
    }

    // Load capacity forecast
    setLoadingCapacity(true);
    try {
      const capacity = selectedMetric === 'bandwidth' ? 1000 : 100; // Mock capacity
      const capacityData = await getCapacityForecast(
        selectedDevice,
        selectedMetric,
        capacity,
        80
      );
      setCapacityForecast(capacityData);
    } catch (error) {
      console.error('Failed to load capacity forecast:', error);
      setCapacityForecast(null);
    } finally {
      setLoadingCapacity(false);
    }

    // Load anomalies
    setLoadingAnomalies(true);
    try {
      const anomalyData = await detectAnomalies(selectedDevice, selectedMetric, 7);
      setAnomalies(anomalyData);
    } catch (error) {
      console.error('Failed to load anomalies:', error);
      setAnomalies(null);
    } finally {
      setLoadingAnomalies(false);
    }

    // Load failure prediction
    setLoadingFailure(true);
    try {
      const failureData = await predictFailure(selectedDevice);
      setFailurePrediction(failureData);
    } catch (error) {
      console.error('Failed to load failure prediction:', error);
      setFailurePrediction(null);
    } finally {
      setLoadingFailure(false);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'critical':
        return '#d32f2f';
      case 'high':
        return '#f57c00';
      case 'medium':
        return '#ffa726';
      case 'low':
        return '#388e3c';
      default:
        return '#757575';
    }
  };

  const getRiskIcon = (risk: string) => {
    switch (risk) {
      case 'critical':
      case 'high':
        return <ErrorIcon style={{ color: getRiskColor(risk) }} />;
      case 'medium':
        return <WarningOutlined style={{ color: getRiskColor(risk) }} />;
      case 'low':
        return <CheckCircleOutlined style={{ color: getRiskColor(risk) }} />;
      default:
        return null;
    }
  };

  // Format forecast data for chart
  const formatForecastData = () => {
    if (!forecast?.forecast) return [];
    return forecast.forecast.map((point: any) => ({
      time: new Date(point.timestamp).toLocaleDateString(),
      predicted: point.predicted_value,
      lower: point.confidence_lower,
      upper: point.confidence_upper,
    }));
  };

  return (
    <div className="predictive-analytics-container">
      {/* Header */}
      <div className="page-header">
        <Title level={2}>
          <Assessment style={{ marginRight: 8, verticalAlign: 'middle' }} />
          Predictive Analytics
        </Title>
        <Paragraph type="secondary">
          Machine learning-powered forecasting, anomaly detection, and capacity planning
        </Paragraph>
      </div>

      {/* Device & Metric Selection */}
      <MaterialCard elevation={2} style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <Text strong>Select Device</Text>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              placeholder="Choose a device"
              value={selectedDevice}
              onChange={setSelectedDevice}
              loading={devicesLoading}
            >
              {devicesData?.devices?.map((device: any) => (
                <Option key={device.id} value={device.id}>
                  {device.name} ({device.type})
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} md={8}>
            <Text strong>Select Metric</Text>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              value={selectedMetric}
              onChange={setSelectedMetric}
            >
              <Option value="bandwidth">Bandwidth</Option>
              <Option value="cpu">CPU Usage</Option>
              <Option value="memory">Memory Usage</Option>
              <Option value="temperature">Temperature</Option>
            </Select>
          </Col>
          <Col xs={24} md={8}>
            <Text strong>Forecast Period</Text>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              value={forecastDays}
              onChange={setForecastDays}
            >
              <Option value={7}>7 Days</Option>
              <Option value={30}>30 Days</Option>
              <Option value={60}>60 Days</Option>
              <Option value={90}>90 Days</Option>
            </Select>
          </Col>
        </Row>
      </MaterialCard>

      {/* Network-Wide Insights */}
      <MaterialCard
        elevation={2}
        title="🌐 Network-Wide Insights"
        style={{ marginBottom: 24 }}
      >
        {loadingInsights ? (
          <div className="loading-center">
            <Spin size="large" tip="Analyzing network..." />
          </div>
        ) : networkInsights ? (
          <>
            <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
              <Col xs={24} sm={12} md={6}>
                <Statistic
                  title="Total Devices"
                  value={networkInsights.network_summary.total_devices}
                  prefix={<ThunderboltOutlined />}
                />
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Statistic
                  title="Online"
                  value={networkInsights.network_summary.online_devices}
                  valueStyle={{ color: '#388e3c' }}
                  prefix={<CheckCircleOutlined />}
                />
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Statistic
                  title="Offline"
                  value={networkInsights.network_summary.offline_devices}
                  valueStyle={{ color: '#d32f2f' }}
                  prefix={<CloseCircleOutlined />}
                />
              </Col>
              <Col xs={24} sm={12} md={6}>
                <Statistic
                  title="Active Alerts"
                  value={networkInsights.network_summary.active_alerts}
                  valueStyle={{ color: '#f57c00' }}
                  prefix={<WarningOutlined />}
                />
              </Col>
            </Row>

            <Divider />

            <Row gutter={[16, 16]}>
              <Col xs={24} md={12}>
                <Text strong>💡 Key Insights</Text>
                <ul className="insights-list">
                  {networkInsights.insights.map((insight: string, index: number) => (
                    <li key={index}>{insight}</li>
                  ))}
                </ul>
              </Col>
              <Col xs={24} md={12}>
                <Text strong>📋 Recommendations</Text>
                <ul className="insights-list">
                  {networkInsights.recommendations.map((rec: string, index: number) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </Col>
            </Row>
          </>
        ) : (
          <Alert
            message="No insights available"
            description="Network insights will appear here once data collection begins."
            type="info"
          />
        )}
      </MaterialCard>

      {selectedDevice ? (
        <>
          {/* Time-Series Forecast */}
          <MaterialCard
            elevation={2}
            title="📈 Time-Series Forecast"
            style={{ marginBottom: 24 }}
          >
            {loadingForecast ? (
              <div className="loading-center">
                <Spin size="large" tip="Generating forecast..." />
              </div>
            ) : forecast ? (
              <>
                <Alert
                  message="Forecast Generated"
                  description={`${forecast.forecast.length} data points predicted for the next ${forecastDays} days using exponential smoothing.`}
                  type="success"
                  style={{ marginBottom: 16 }}
                />
                <ResponsiveContainer width="100%" height={350}>
                  <AreaChart data={formatForecastData()}>
                    <defs>
                      <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#1976d2" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#1976d2" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="upper"
                      stackId="1"
                      stroke="#90caf9"
                      fill="#90caf9"
                      fillOpacity={0.3}
                      name="Upper Bound"
                    />
                    <Area
                      type="monotone"
                      dataKey="predicted"
                      stackId="2"
                      stroke="#1976d2"
                      fill="url(#colorPredicted)"
                      name="Predicted"
                    />
                    <Area
                      type="monotone"
                      dataKey="lower"
                      stackId="1"
                      stroke="#90caf9"
                      fill="#90caf9"
                      fillOpacity={0.3}
                      name="Lower Bound"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </>
            ) : (
              <Alert
                message="Insufficient Data"
                description="Not enough historical data available for forecasting. Need at least 10 data points."
                type="warning"
              />
            )}
          </MaterialCard>

          {/* Capacity Planning */}
          <MaterialCard
            elevation={2}
            title="⚡ Capacity Planning"
            style={{ marginBottom: 24 }}
          >
            {loadingCapacity ? (
              <div className="loading-center">
                <Spin size="large" tip="Analyzing capacity..." />
              </div>
            ) : capacityForecast ? (
              <Row gutter={[16, 16]}>
                <Col xs={24} md={12}>
                  <Card>
                    <Statistic
                      title="Current Utilization"
                      value={capacityForecast.current_utilization}
                      suffix="%"
                      precision={1}
                    />
                    <Progress
                      percent={capacityForecast.current_utilization}
                      status={
                        capacityForecast.current_utilization > 80
                          ? 'exception'
                          : capacityForecast.current_utilization > 60
                          ? 'normal'
                          : 'success'
                      }
                    />
                  </Card>
                </Col>
                <Col xs={24} md={12}>
                  <Card>
                    <Statistic
                      title="Days Until Threshold"
                      value={capacityForecast.days_until_threshold || 'N/A'}
                      suffix={capacityForecast.days_until_threshold ? 'days' : ''}
                    />
                    {capacityForecast.days_until_threshold && (
                      <Tag
                        color={
                          capacityForecast.days_until_threshold < 30
                            ? 'red'
                            : capacityForecast.days_until_threshold < 60
                            ? 'orange'
                            : 'green'
                        }
                        style={{ marginTop: 8 }}
                      >
                        {capacityForecast.days_until_threshold < 30
                          ? 'Action Required'
                          : capacityForecast.days_until_threshold < 60
                          ? 'Plan Ahead'
                          : 'Healthy'}
                      </Tag>
                    )}
                  </Card>
                </Col>
                <Col xs={24}>
                  <Alert
                    message="Recommendation"
                    description={capacityForecast.recommendation}
                    type={
                      capacityForecast.recommendation.includes('CRITICAL')
                        ? 'error'
                        : capacityForecast.recommendation.includes('WARNING')
                        ? 'warning'
                        : 'info'
                    }
                    showIcon
                  />
                </Col>
              </Row>
            ) : (
              <Alert
                message="No capacity data"
                description="Capacity forecast will appear once enough data is collected."
                type="info"
              />
            )}
          </MaterialCard>

          {/* Anomaly Detection */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} lg={12}>
              <MaterialCard elevation={2} title="🔍 Anomaly Detection">
                {loadingAnomalies ? (
                  <div className="loading-center">
                    <Spin tip="Detecting anomalies..." />
                  </div>
                ) : anomalies && anomalies.anomalies_detected > 0 ? (
                  <>
                    <Alert
                      message={`${anomalies.anomalies_detected} Anomalies Detected`}
                      description={`Found in ${anomalies.total_data_points} data points over ${anomalies.days_analyzed} days`}
                      type="warning"
                      style={{ marginBottom: 16 }}
                    />
                    <Table
                      dataSource={anomalies.anomalies}
                      columns={[
                        {
                          title: 'Time',
                          dataIndex: 'timestamp',
                          key: 'timestamp',
                          render: (ts: string) => new Date(ts).toLocaleString(),
                        },
                        {
                          title: 'Value',
                          dataIndex: 'value',
                          key: 'value',
                          render: (val: number) => val.toFixed(2),
                        },
                        {
                          title: 'Severity',
                          dataIndex: 'severity',
                          key: 'severity',
                          render: (severity: string) => (
                            <Tag color={getRiskColor(severity)}>{severity.toUpperCase()}</Tag>
                          ),
                        },
                      ]}
                      pagination={{ pageSize: 5 }}
                      size="small"
                    />
                  </>
                ) : (
                  <Alert
                    message="No Anomalies Detected"
                    description="All metrics are within expected ranges."
                    type="success"
                    showIcon
                  />
                )}
              </MaterialCard>
            </Col>

            {/* Failure Prediction */}
            <Col xs={24} lg={12}>
              <MaterialCard elevation={2} title="⚠️ Device Health Prediction">
                {loadingFailure ? (
                  <div className="loading-center">
                    <Spin tip="Analyzing device health..." />
                  </div>
                ) : failurePrediction ? (
                  <>
                    <Space direction="vertical" size="large" style={{ width: '100%' }}>
                      <div>
                        <Text strong>Failure Probability</Text>
                        <div className="margin-top-8">
                          <Progress
                            type="circle"
                            percent={Math.round(failurePrediction.failure_probability * 100)}
                            format={(percent) => `${percent}%`}
                            status={
                              failurePrediction.failure_probability > 0.7
                                ? 'exception'
                                : failurePrediction.failure_probability > 0.5
                                ? 'normal'
                                : 'success'
                            }
                          />
                        </div>
                      </div>

                      <div>
                        <Space>
                          <Text strong>Risk Level:</Text>
                          {getRiskIcon(failurePrediction.risk_level)}
                          <Tag color={getRiskColor(failurePrediction.risk_level)}>
                            {failurePrediction.risk_level.toUpperCase()}
                          </Tag>
                        </Space>
                      </div>

                      {failurePrediction.time_to_failure_days && (
                        <Alert
                          message={`Potential failure in ${failurePrediction.time_to_failure_days} days`}
                          type="error"
                          showIcon
                        />
                      )}

                      <div>
                        <Text strong>Contributing Factors:</Text>
                        <ul className="insights-list">
                          {failurePrediction.contributing_factors.map(
                            (factor: string, index: number) => (
                              <li key={index}>{factor}</li>
                            )
                          )}
                        </ul>
                      </div>

                      <Alert
                        message="Recommendation"
                        description={failurePrediction.recommendation}
                        type={
                          failurePrediction.risk_level === 'critical' ||
                          failurePrediction.risk_level === 'high'
                            ? 'error'
                            : 'info'
                        }
                        showIcon
                      />
                    </Space>
                  </>
                ) : (
                  <Alert
                    message="No prediction available"
                    description="Device health prediction requires historical data."
                    type="info"
                  />
                )}
              </MaterialCard>
            </Col>
          </Row>
        </>
      ) : (
        <MaterialCard elevation={2}>
          <Alert
            message="Select a Device"
            description="Choose a device from the dropdown above to view predictive analytics and forecasts."
            type="info"
            showIcon
          />
        </MaterialCard>
      )}
    </div>
  );
};

export default PredictiveAnalytics;

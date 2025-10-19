/**
 * Login page component
 */

import { MaterialCard } from "@/components/MaterialCard";
import { useAuth } from "@/contexts/AuthContext";
import { LockOutlined, UserOutlined } from "@ant-design/icons";
import { Button, Form, Input, message, Typography } from "antd";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const { Text } = Typography;

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      await login(values.username, values.password);
      message.success("Login successful!");
      navigate("/");
    } catch (error) {
      message.error("Login failed. Please check your credentials.");
      console.error("Login error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        background:
          "linear-gradient(135deg, var(--md-sys-color-primary) 0%, var(--md-sys-color-secondary) 100%)",
      }}
    >
      <MaterialCard
        elevation={3}
        style={{ width: 450 }}
      >
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <h1 className="md-headline-large" style={{ marginBottom: 8, background: "linear-gradient(135deg, var(--md-sys-color-primary), var(--md-sys-color-secondary))", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", backgroundClip: "text" }}>
            📊 UniFi Insights
          </h1>
          <p className="md-body-large" style={{ color: "var(--md-sys-color-on-surface-variant)" }}>
            Historical Analysis & Intelligence Platform
          </p>
        </div>

        <Form onFinish={onFinish} layout="vertical" size="large">
          <Form.Item
            name="username"
            rules={[{ required: true, message: "Please enter your username" }]}
          >
            <Input prefix={<UserOutlined />} placeholder="Username" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: "Please enter your password" }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Password" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              Log in
            </Button>
          </Form.Item>
        </Form>

        <div
          style={{
            textAlign: "center",
            marginTop: 24,
            padding: 16,
            background: "var(--md-sys-color-surface-variant)",
            borderRadius: 8,
          }}
        >
          <Text type="secondary" style={{ fontSize: 12 }}>
            <strong>Default credentials:</strong> admin / admin123!
          </Text>
        </div>
      </MaterialCard>
    </div>
  );
};

export default Login;

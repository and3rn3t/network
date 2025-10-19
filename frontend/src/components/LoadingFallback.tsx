/**
 * Material Design 3 Loading Component
 */

import { Spin } from "antd";
import React from "react";
import "./LoadingFallback.css";

export const LoadingFallback: React.FC = () => (
  <div className="loading-fallback">
    <Spin size="large" tip="Loading..." />
  </div>
);

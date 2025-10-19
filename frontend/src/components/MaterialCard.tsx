/**
 * Material Design 3 Card Component
 */

import type { CardProps as AntCardProps } from "antd";
import { Card as AntCard } from "antd";
import React from "react";
import "./MaterialCard.css";

export interface MaterialCardProps extends Omit<AntCardProps, "variant"> {
  elevation?: 0 | 1 | 2 | 3 | 4 | 5;
  variant?: "elevated" | "filled" | "outlined";
}

export const MaterialCard: React.FC<MaterialCardProps> = ({
  elevation = 1,
  variant = "elevated",
  className = "",
  ...props
}) => {
  const cardClassName = `material-card material-card-${variant} material-card-elevation-${elevation} ${className}`;

  return <AntCard className={cardClassName} {...props} />;
};

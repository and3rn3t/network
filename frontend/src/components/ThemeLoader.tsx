/**
 * Theme Loader Component
 * Shows a minimal loading indicator while the theme system initializes
 * Prevents flash of unstyled content (FOUC)
 */

import React, { useEffect, useState } from "react";
import "./ThemeLoader.css";

interface ThemeLoaderProps {
  delay?: number; // Delay in ms before showing loader (prevents flash for fast loads)
}

export const ThemeLoader: React.FC<ThemeLoaderProps> = ({ delay = 100 }) => {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShow(true);
    }, delay);

    return () => clearTimeout(timer);
  }, [delay]);

  if (!show) {
    return null;
  }

  return (
    <div className="theme-loader">
      <div className="theme-loader-spinner">
        <div className="theme-loader-circle"></div>
      </div>
    </div>
  );
};

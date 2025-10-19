/**
 * Material Design 3 (Material You) Theme Configuration
 *
 * Following Material Design 3 guidelines:
 * - Dynamic color system
 * - Elevation and surfaces
 * - Typography scale
 * - Motion and interaction
 */

import type { ThemeConfig } from "antd";

// Material Design 3 Color Tokens
export const materialColors = {
  // Primary palette (Blue - for data/analytics feel)
  primary: {
    main: "#1E88E5", // Primary-40
    light: "#42A5F5", // Primary-80
    dark: "#1565C0", // Primary-20
    container: "#E3F2FD", // Primary-90
    onContainer: "#0D47A1", // Primary-10
  },

  // Secondary palette (Teal - for accents)
  secondary: {
    main: "#00897B",
    light: "#4DB6AC",
    dark: "#00695C",
    container: "#E0F2F1",
    onContainer: "#004D40",
  },

  // Tertiary palette (Deep Orange - for alerts/warnings)
  tertiary: {
    main: "#F4511E",
    light: "#FF7043",
    dark: "#D84315",
    container: "#FBE9E7",
    onContainer: "#BF360C",
  },

  // Error palette
  error: {
    main: "#D32F2F",
    light: "#EF5350",
    dark: "#C62828",
    container: "#FFEBEE",
    onContainer: "#B71C1C",
  },

  // Success palette
  success: {
    main: "#388E3C",
    light: "#66BB6A",
    dark: "#2E7D32",
    container: "#E8F5E9",
    onContainer: "#1B5E20",
  },

  // Warning palette
  warning: {
    main: "#F57C00",
    light: "#FFB74D",
    dark: "#E65100",
    container: "#FFF3E0",
    onContainer: "#E65100",
  },

  // Neutral palette
  neutral: {
    0: "#FFFFFF",
    10: "#FAFAFA",
    20: "#F5F5F5",
    30: "#EEEEEE",
    40: "#E0E0E0",
    50: "#BDBDBD",
    60: "#9E9E9E",
    70: "#757575",
    80: "#616161",
    90: "#424242",
    100: "#212121",
  },

  // Surface colors
  surface: {
    default: "#FFFFFF",
    variant: "#F5F5F5",
    dim: "#FAFAFA",
    bright: "#FFFFFF",
    container: "#F5F5F5",
    containerLow: "#FAFAFA",
    containerHigh: "#EEEEEE",
    containerHighest: "#E0E0E0",
  },

  // Outline colors
  outline: {
    default: "#E0E0E0",
    variant: "#EEEEEE",
  },
};

// Material Design 3 Typography Scale
export const materialTypography = {
  // Display styles (large, expressive)
  displayLarge: {
    fontSize: "57px",
    lineHeight: "64px",
    fontWeight: 400,
    letterSpacing: "-0.25px",
  },
  displayMedium: {
    fontSize: "45px",
    lineHeight: "52px",
    fontWeight: 400,
    letterSpacing: 0,
  },
  displaySmall: {
    fontSize: "36px",
    lineHeight: "44px",
    fontWeight: 400,
    letterSpacing: 0,
  },

  // Headline styles (medium emphasis)
  headlineLarge: {
    fontSize: "32px",
    lineHeight: "40px",
    fontWeight: 500,
    letterSpacing: 0,
  },
  headlineMedium: {
    fontSize: "28px",
    lineHeight: "36px",
    fontWeight: 500,
    letterSpacing: 0,
  },
  headlineSmall: {
    fontSize: "24px",
    lineHeight: "32px",
    fontWeight: 500,
    letterSpacing: 0,
  },

  // Title styles
  titleLarge: {
    fontSize: "22px",
    lineHeight: "28px",
    fontWeight: 600,
    letterSpacing: 0,
  },
  titleMedium: {
    fontSize: "16px",
    lineHeight: "24px",
    fontWeight: 600,
    letterSpacing: "0.15px",
  },
  titleSmall: {
    fontSize: "14px",
    lineHeight: "20px",
    fontWeight: 600,
    letterSpacing: "0.1px",
  },

  // Body styles
  bodyLarge: {
    fontSize: "16px",
    lineHeight: "24px",
    fontWeight: 400,
    letterSpacing: "0.5px",
  },
  bodyMedium: {
    fontSize: "14px",
    lineHeight: "20px",
    fontWeight: 400,
    letterSpacing: "0.25px",
  },
  bodySmall: {
    fontSize: "12px",
    lineHeight: "16px",
    fontWeight: 400,
    letterSpacing: "0.4px",
  },

  // Label styles
  labelLarge: {
    fontSize: "14px",
    lineHeight: "20px",
    fontWeight: 500,
    letterSpacing: "0.1px",
  },
  labelMedium: {
    fontSize: "12px",
    lineHeight: "16px",
    fontWeight: 500,
    letterSpacing: "0.5px",
  },
  labelSmall: {
    fontSize: "11px",
    lineHeight: "16px",
    fontWeight: 500,
    letterSpacing: "0.5px",
  },
};

// Material Design 3 Elevation (shadows)
export const materialElevation = {
  level0: "none",
  level1: "0px 1px 2px rgba(0, 0, 0, 0.3), 0px 1px 3px 1px rgba(0, 0, 0, 0.15)",
  level2: "0px 1px 2px rgba(0, 0, 0, 0.3), 0px 2px 6px 2px rgba(0, 0, 0, 0.15)",
  level3: "0px 4px 8px 3px rgba(0, 0, 0, 0.15), 0px 1px 3px rgba(0, 0, 0, 0.3)",
  level4:
    "0px 6px 10px 4px rgba(0, 0, 0, 0.15), 0px 2px 3px rgba(0, 0, 0, 0.3)",
  level5:
    "0px 8px 12px 6px rgba(0, 0, 0, 0.15), 0px 4px 4px rgba(0, 0, 0, 0.3)",
};

// Material Design 3 Spacing (8px grid system)
export const materialSpacing = {
  xs: "4px", // 0.5 unit
  sm: "8px", // 1 unit
  md: "16px", // 2 units
  lg: "24px", // 3 units
  xl: "32px", // 4 units
  xxl: "48px", // 6 units
  xxxl: "64px", // 8 units
};

// Material Design 3 Border Radius
export const materialBorderRadius = {
  none: "0px",
  xs: "4px",
  sm: "8px",
  md: "12px",
  lg: "16px",
  xl: "28px",
  full: "9999px",
};

// Ant Design Theme Configuration with Material Design 3
export const materialTheme: ThemeConfig = {
  token: {
    // Color tokens
    colorPrimary: materialColors.primary.main,
    colorSuccess: materialColors.success.main,
    colorWarning: materialColors.warning.main,
    colorError: materialColors.error.main,
    colorInfo: materialColors.secondary.main,

    // Background tokens
    colorBgBase: materialColors.surface.default,
    colorBgContainer: materialColors.surface.default,
    colorBgElevated: materialColors.surface.default,
    colorBgLayout: materialColors.surface.variant,
    colorBgSpotlight: materialColors.surface.containerHigh,

    // Border tokens
    colorBorder: materialColors.outline.default,
    colorBorderSecondary: materialColors.outline.variant,

    // Text tokens
    colorText: materialColors.neutral[100],
    colorTextSecondary: materialColors.neutral[70],
    colorTextTertiary: materialColors.neutral[60],
    colorTextQuaternary: materialColors.neutral[50],

    // Typography
    fontFamily:
      '"Inter", "Roboto", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    fontSize: 14,
    fontSizeHeading1: 32,
    fontSizeHeading2: 28,
    fontSizeHeading3: 24,
    fontSizeHeading4: 20,
    fontSizeHeading5: 16,
    lineHeight: 1.5715,
    lineHeightHeading1: 1.25,
    lineHeightHeading2: 1.2857,
    lineHeightHeading3: 1.3333,
    lineHeightHeading4: 1.4,
    lineHeightHeading5: 1.5,

    // Spacing
    padding: 16,
    paddingXS: 8,
    paddingSM: 12,
    paddingLG: 24,
    paddingXL: 32,
    margin: 16,
    marginXS: 8,
    marginSM: 12,
    marginLG: 24,
    marginXL: 32,

    // Border radius
    borderRadius: 12,
    borderRadiusLG: 16,
    borderRadiusSM: 8,
    borderRadiusXS: 4,

    // Shadows (elevation)
    boxShadow: materialElevation.level1,
    boxShadowSecondary: materialElevation.level2,
    boxShadowTertiary: materialElevation.level3,

    // Motion
    motionUnit: 0.1,
    motionBase: 0,
    motionEaseInOut: "cubic-bezier(0.4, 0, 0.2, 1)",
    motionEaseOut: "cubic-bezier(0.0, 0, 0.2, 1)",

    // Control height
    controlHeight: 40,
    controlHeightLG: 48,
    controlHeightSM: 32,

    // Z-index
    zIndexBase: 0,
    zIndexPopupBase: 1000,
  },

  components: {
    Layout: {
      headerBg: materialColors.surface.default,
      headerHeight: 64,
      headerPadding: "0 24px",
      siderBg: materialColors.neutral[100],
      bodyBg: materialColors.surface.variant,
      footerBg: materialColors.surface.default,
      footerPadding: "24px 50px",
    },

    Menu: {
      itemBg: "transparent",
      itemSelectedBg: materialColors.primary.container,
      itemSelectedColor: materialColors.primary.onContainer,
      itemHoverBg: "rgba(30, 136, 229, 0.08)",
      itemHoverColor: materialColors.primary.main,
      itemActiveBg: materialColors.primary.container,
      itemColor: "rgba(255, 255, 255, 0.87)",
      iconSize: 20,
      itemBorderRadius: 12,
      itemMarginInline: 8,
      itemPaddingInline: 16,
    },

    Card: {
      boxShadow: materialElevation.level1,
      borderRadiusLG: 16,
      paddingLG: 24,
      headerFontSize: 20,
      headerFontSizeSM: 16,
      headerHeight: 64,
      headerHeightSM: 48,
    },

    Button: {
      borderRadius: 20,
      controlHeight: 40,
      controlHeightLG: 48,
      controlHeightSM: 32,
      fontSizeLG: 15,
      paddingContentHorizontal: 24,
      primaryShadow: materialElevation.level0,
      defaultShadow: materialElevation.level0,
    },

    Input: {
      borderRadius: 12,
      controlHeight: 48,
      paddingBlock: 12,
      paddingInline: 16,
    },

    Select: {
      borderRadius: 12,
      controlHeight: 48,
    },

    Table: {
      borderRadiusLG: 16,
      headerBg: materialColors.surface.containerHigh,
      headerColor: materialColors.neutral[100],
      rowHoverBg: materialColors.surface.containerLow,
      cellPaddingBlock: 16,
      cellPaddingInline: 16,
    },

    Statistic: {
      titleFontSize: 14,
      contentFontSize: 28,
    },

    Alert: {
      borderRadiusLG: 12,
      paddingContentVertical: 12,
      paddingContentHorizontal: 16,
    },

    Modal: {
      borderRadiusLG: 24,
      headerBg: materialColors.surface.default,
      contentBg: materialColors.surface.default,
    },

    Drawer: {
      borderRadiusLG: 16,
    },

    Tag: {
      borderRadiusSM: 16,
      defaultBg: materialColors.surface.containerHigh,
      defaultColor: materialColors.neutral[100],
    },

    Tabs: {
      itemActiveColor: materialColors.primary.main,
      itemHoverColor: materialColors.primary.main,
      itemSelectedColor: materialColors.primary.main,
      inkBarColor: materialColors.primary.main,
      titleFontSize: 15,
      cardBg: materialColors.surface.default,
    },
  },
};

// Dark theme variant
export const materialDarkTheme: ThemeConfig = {
  ...materialTheme,
  token: {
    ...materialTheme.token,
    colorBgBase: "#1C1B1F",
    colorBgContainer: "#1C1B1F",
    colorBgElevated: "#2B2930",
    colorBgLayout: "#141218",
    colorBgSpotlight: "#2B2930",
    colorText: "#E6E1E5",
    colorTextSecondary: "#CAC4D0",
    colorTextTertiary: "#938F99",
  },
};

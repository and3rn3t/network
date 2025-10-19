# Material Design 3 Implementation Guide

## Overview

The UniFi Network Insights frontend has been fully redesigned following **Material Design 3 (Material You)** guidelines to provide a modern, cohesive, and accessible user experience.

## Key Features

### 🎨 Color System

- **Primary**: Blue (#1E88E5) - Main brand color for primary actions
- **Secondary**: Teal (#00897B) - Accent color for secondary elements
- **Tertiary**: Deep Orange (#F4511E) - For alerts and warnings
- **Surface**: White (#FFFFFF) - Background surfaces
- **Error/Success/Warning**: Semantic colors following Material Design 3

### 📐 Typography Scale

Using **Inter** font family with Material Design 3 type scale:

- **Display**: Large, expressive text (57px, 45px, 36px)
- **Headline**: Medium emphasis headers (32px, 28px, 24px)
- **Title**: Card titles and section headers (22px, 16px, 14px)
- **Body**: Main content text (16px, 14px, 12px)
- **Label**: UI labels and captions (14px, 12px, 11px)

### 🔲 Spacing System

8px grid system with consistent spacing tokens:

- **xs**: 4px (0.5 unit)
- **sm**: 8px (1 unit)
- **md**: 16px (2 units)
- **lg**: 24px (3 units)
- **xl**: 32px (4 units)
- **xxl**: 48px (6 units)
- **xxxl**: 64px (8 units)

### 🌟 Elevation (Shadows)

Five levels of elevation for layering:

- **Level 0**: No shadow
- **Level 1**: Subtle elevation for cards
- **Level 2**: Medium elevation for hover states
- **Level 3**: High elevation for modals
- **Level 4-5**: Reserved for special emphasis

### 🔄 Motion

- **Easing**: `cubic-bezier(0.4, 0, 0.2, 1)` - Standard easing
- **Duration**: 200ms (short), 300ms (medium), 400ms (long)
- Smooth transitions for all interactive elements

### 🎯 Border Radius

Rounded corners following Material Design 3:

- **xs**: 4px - Small elements
- **sm**: 8px - Buttons, tags
- **md**: 12px - Cards, inputs
- **lg**: 16px - Large cards
- **xl**: 28px - Modals
- **full**: 9999px - Circular elements

## Component Library

### MaterialCard

Custom card component with Material Design 3 styling:

```tsx
import { MaterialCard } from "@/components/MaterialCard";

<MaterialCard elevation={2} variant="elevated" title="Card Title">
  Card content
</MaterialCard>;
```

**Props:**

- `elevation`: 0-5 (default: 1)
- `variant`: "elevated" | "filled" | "outlined" (default: "elevated")

### LoadingFallback

Styled loading component:

```tsx
import { LoadingFallback } from "@/components/LoadingFallback";

<LoadingFallback />;
```

### AppLayout

Main application layout with:

- Material Design 3 sidebar with gradient logo
- Elevated header with user menu
- Responsive content area
- Styled footer

## Theme Configuration

The theme is configured in `src/theme/material-theme.ts` and includes:

- **Color tokens** from Material Design 3
- **Typography** settings
- **Spacing** values
- **Component overrides** for Ant Design

Import and use:

```tsx
import { materialTheme } from "@/theme/material-theme";

<ConfigProvider theme={materialTheme}>{/* Your app */}</ConfigProvider>;
```

## CSS Custom Properties

Global CSS variables are defined in `src/index.css`:

```css
var(--md-sys-color-primary)
var(--md-sys-color-surface)
var(--md-sys-spacing-md)
var(--md-sys-elevation-2)
var(--md-sys-shape-corner-lg)
var(--md-sys-motion-duration-medium)
```

## Utility Classes

Use Material Design utility classes:

```tsx
<div className="md-surface p-lg mb-md">
  <h3 className="md-headline-small">Headline</h3>
  <p className="md-body-medium">Body text</p>
</div>
```

**Spacing utilities:**

- `mt-xs`, `mt-sm`, `mt-md`, `mt-lg`, `mt-xl` (margin-top)
- `mb-xs`, `mb-sm`, `mb-md`, `mb-lg`, `mb-xl` (margin-bottom)
- `p-xs`, `p-sm`, `p-md`, `p-lg`, `p-xl` (padding)

**Typography utilities:**

- `md-display-large`, `md-headline-medium`, `md-title-small`
- `md-body-large`, `md-label-medium`

**Surface utilities:**

- `md-surface` - Basic surface
- `md-surface-variant` - Variant surface
- `md-surface-elevated` - With elevation

## Ant Design Enhancements

All Ant Design components are styled to match Material Design 3:

- **Buttons**: Rounded with proper elevation
- **Cards**: Material Design shadows and radius
- **Tables**: Clean headers with hover states
- **Forms**: Material Design inputs
- **Modals**: Large radius with elevation
- **Alerts**: Container colors with proper contrast

## Accessibility

- Focus-visible outlines on all interactive elements
- Proper contrast ratios (WCAG AA compliant)
- Screen reader support with `.sr-only` class
- Keyboard navigation support

## Responsive Design

Breakpoints:

- **Desktop**: > 1024px
- **Tablet**: 768px - 1024px
- **Mobile**: < 768px

The layout automatically adjusts spacing, font sizes, and component sizes.

## Best Practices

1. **Always use theme tokens** instead of hardcoded colors
2. **Follow 8px spacing grid** for consistency
3. **Use appropriate elevation** for visual hierarchy
4. **Apply proper typography scale** for content
5. **Ensure accessibility** with focus states and ARIA labels
6. **Test responsive behavior** across devices

## Examples

### Page Header

```tsx
<div className="page-header">
  <h1 className="page-header-title">Dashboard</h1>
  <p className="page-header-description">Overview of your network performance</p>
</div>
```

### Card Grid

```tsx
<div className="material-card-grid">
  <MaterialCard title="CPU Usage" elevation={1}>
    Content
  </MaterialCard>
  <MaterialCard title="Memory" elevation={1}>
    Content
  </MaterialCard>
</div>
```

### Styled Button

```tsx
<Button type="primary" size="large" icon={<PlusOutlined />}>
  Add Device
</Button>
```

## Resources

- [Material Design 3 Guidelines](https://m3.material.io/)
- [Material You Design Kit](https://www.figma.com/community/file/1035203688168086460)
- [Ant Design Documentation](https://ant.design/)
- [Inter Font Family](https://fonts.google.com/specimen/Inter)

## Next Steps

1. Update individual page components to use MaterialCard
2. Implement dark mode variant
3. Add animation transitions between routes
4. Create additional custom Material Design components (chips, FAB, etc.)
5. Optimize performance with code splitting

---

**Note**: This is a living document. Update as new components and patterns are added.

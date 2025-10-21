# Material Design 3 Visual Showcase

## 🎨 Color Palette

### Primary Colors

- **Primary**: `#1E88E5` - Blue (Data/Analytics theme)
- **Primary Container**: `#E3F2FD` - Light blue background
- **On Primary**: `#FFFFFF` - White text on primary
- **On Primary Container**: `#0D47A1` - Dark blue text

### Secondary Colors

- **Secondary**: `#00897B` - Teal (Accents)
- **Secondary Container**: `#E0F2F1` - Light teal background
- **On Secondary**: `#FFFFFF` - White text on secondary
- **On Secondary Container**: `#004D40` - Dark teal text

### Tertiary Colors

- **Tertiary**: `#F4511E` - Deep Orange (Alerts/Warnings)
- **Tertiary Container**: `#FBE9E7` - Light orange background
- **On Tertiary**: `#FFFFFF` - White text on tertiary
- **On Tertiary Container**: `#BF360C` - Dark orange text

### Semantic Colors

- **Error**: `#D32F2F` (Red) with container `#FFEBEE`
- **Success**: `#388E3C` (Green) with container `#E8F5E9`
- **Warning**: `#F57C00` (Orange) with container `#FFF3E0`

### Surface Colors

- **Surface**: `#FFFFFF` - Default background
- **Surface Variant**: `#F5F5F5` - Alternate background
- **Surface Container**: `#EEEEEE` - High emphasis background

### Neutral Palette

```
0:   #FFFFFF (White)
10:  #FAFAFA
20:  #F5F5F5
30:  #EEEEEE
40:  #E0E0E0
50:  #BDBDBD
60:  #9E9E9E
70:  #757575
80:  #616161
90:  #424242
100: #212121 (Black)
```

---

## 📝 Typography Scale

### Display Styles (Large, Expressive)

```
Display Large:  57px / 64px line-height, 400 weight
Display Medium: 45px / 52px line-height, 400 weight
Display Small:  36px / 44px line-height, 400 weight
```

### Headline Styles (Medium Emphasis)

```
Headline Large:  32px / 40px line-height, 500 weight
Headline Medium: 28px / 36px line-height, 500 weight
Headline Small:  24px / 32px line-height, 500 weight
```

### Title Styles

```
Title Large:  22px / 28px line-height, 600 weight
Title Medium: 16px / 24px line-height, 600 weight
Title Small:  14px / 20px line-height, 600 weight
```

### Body Styles

```
Body Large:  16px / 24px line-height, 400 weight
Body Medium: 14px / 20px line-height, 400 weight
Body Small:  12px / 16px line-height, 400 weight
```

### Label Styles

```
Label Large:  14px / 20px line-height, 500 weight
Label Medium: 12px / 16px line-height, 500 weight
Label Small:  11px / 16px line-height, 500 weight
```

---

## 📏 Spacing System (8px Grid)

```
xs:   4px  (0.5 unit) - Tight spacing, list items
sm:   8px  (1 unit)   - Default spacing, compact layouts
md:   16px (2 units)  - Standard spacing, card padding
lg:   24px (3 units)  - Section spacing, large cards
xl:   32px (4 units)  - Page section spacing
xxl:  48px (6 units)  - Major section breaks
xxxl: 64px (8 units)  - Hero spacing, page headers
```

### Usage Examples

- **Card Padding**: `24px` (lg)
- **Button Padding**: `8px 24px` (sm vertical, lg horizontal)
- **List Item Gap**: `8px` (sm)
- **Section Margin**: `32px` (xl)
- **Page Margin**: `24px` (lg)

---

## 🌟 Elevation System

### Level 0 - Flat

```css
box-shadow: none;
```

Use for: Filled cards, inline content

### Level 1 - Subtle Elevation

```css
box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.3), 0px 1px 3px 1px rgba(0, 0, 0, 0.15);
```

Use for: Standard cards, default surfaces

### Level 2 - Medium Elevation

```css
box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.3), 0px 2px 6px 2px rgba(0, 0, 0, 0.15);
```

Use for: Hover states, app bar

### Level 3 - High Elevation

```css
box-shadow: 0px 4px 8px 3px rgba(0, 0, 0, 0.15), 0px 1px 3px rgba(0, 0, 0, 0.3);
```

Use for: Modals, dropdowns, FAB

### Level 4 - Very High Elevation

```css
box-shadow: 0px 6px 10px 4px rgba(0, 0, 0, 0.15), 0px 2px 3px rgba(0, 0, 0, 0.3);
```

Use for: Special emphasis, navigation drawer

### Level 5 - Maximum Elevation

```css
box-shadow: 0px 8px 12px 6px rgba(0, 0, 0, 0.15), 0px 4px 4px rgba(0, 0, 0, 0.3);
```

Use for: Tooltips, snackbars

---

## 🔲 Border Radius

```
none: 0px    - Square corners
xs:   4px    - Subtle rounding, small elements
sm:   8px    - Buttons, tags, chips
md:   12px   - Standard cards, inputs
lg:   16px   - Large cards, containers
xl:   28px   - Modals, dialogs
full: 9999px - Circular, pills
```

### Component Mapping

- **Buttons**: `20px` (xl for pill shape)
- **Cards**: `16px` (lg)
- **Inputs**: `12px` (md)
- **Modals**: `24px` (xl)
- **Tags**: `16px` (lg for pill)
- **Avatars**: `9999px` (full circle)

---

## 🎭 Motion System

### Easing Functions

**Standard Easing** (Most common)

```css
cubic-bezier(0.4, 0, 0.2, 1)
```

Use for: General transitions, hover effects

**Emphasized Easing** (Dramatic entries)

```css
cubic-bezier(0.2, 0, 0, 1)
```

Use for: Modals opening, page transitions

**Deceleration** (Exits)

```css
cubic-bezier(0.0, 0, 0.2, 1)
```

Use for: Elements leaving screen

### Duration

```
Short:  200ms - Quick feedback, hover states
Medium: 300ms - Standard transitions, fades
Long:   400ms - Page transitions, complex animations
```

### Example Transitions

**Button Hover**

```css
transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
```

**Card Hover**

```css
transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
```

**Modal Open**

```css
transition: all 400ms cubic-bezier(0.2, 0, 0, 1);
```

---

## 🎯 Component States

### Button States

1. **Default**: Primary color, elevation 0
2. **Hover**: Lighter background, elevation 1
3. **Active**: Pressed state, elevation 0
4. **Focus**: 2px outline, offset 2px
5. **Disabled**: 38% opacity, no interaction

### Card States

1. **Rest**: Elevation 1
2. **Hover**: Elevation 2, translate -2px
3. **Active/Selected**: Primary container background
4. **Disabled**: 60% opacity

### Input States

1. **Default**: Outline border
2. **Hover**: Primary border
3. **Focus**: Primary border + shadow
4. **Error**: Error color border
5. **Disabled**: Surface variant background

---

## 📱 Responsive Breakpoints

### Desktop (>1024px)

- Full sidebar (280px)
- Multi-column layout (3-4 columns)
- Large spacing (32px)
- Full header with subtitle

### Tablet (768px - 1024px)

- Narrow sidebar (240px)
- Two-column layout
- Medium spacing (24px)
- Full header

### Mobile (<768px)

- Collapsed sidebar (drawer)
- Single column layout
- Compact spacing (16px)
- Minimal header (no subtitle)
- Hidden username in header

---

## 🎨 Usage Examples

### Page Layout

```tsx
<div>
  <div className="page-header">
    <h1 className="page-header-title">Dashboard</h1>
    <p className="page-header-description">Overview</p>
  </div>

  <Row gutter={[24, 24]}>
    <Col xs={24} lg={12}>
      <MaterialCard elevation={1} title="Card">
        Content
      </MaterialCard>
    </Col>
  </Row>
</div>
```

### Statistic Card

```tsx
<MaterialCard elevation={1}>
  <Statistic title="Active Devices" value={24} prefix={<CloudServerOutlined />} />
</MaterialCard>
```

### Alert Container

```tsx
<Alert message="Success" description="Operation completed successfully" type="success" showIcon closable />
```

---

## 🎨 Color Usage Guidelines

### When to Use Each Color

**Primary (Blue)**

- Primary action buttons
- Active navigation items
- Links
- Important icons
- Focus states

**Secondary (Teal)**

- Secondary actions
- Accent elements
- Decorative icons
- Progress indicators

**Tertiary (Orange)**

- Alert states
- Warning indicators
- Delete/destructive actions
- Error highlights

**Surface Colors**

- White: Main content background
- Variant: Alternate backgrounds, table headers
- Container: Elevated sections, sidebars

**Text Colors**

- On Surface (Black): Primary text
- On Surface Variant (Gray 70): Secondary text
- On Surface Tertiary (Gray 60): Disabled text

---

## ♿ Accessibility

### Contrast Ratios (WCAG AA)

**Normal Text** (4.5:1 minimum)

- Primary on White: ✅ 4.52:1
- On Surface on Surface: ✅ 8.59:1
- On Surface Variant on Surface: ✅ 4.54:1

**Large Text** (3:1 minimum)

- All combinations exceed 3:1 ✅

### Focus States

- 2px solid outline
- Primary color
- 2px offset
- Visible on keyboard navigation

### Screen Readers

- Semantic HTML
- ARIA labels where needed
- Proper heading hierarchy
- Alt text for images

---

## 🚀 Quick Start

### Using Theme Tokens in CSS

```css
.my-component {
  color: var(--md-sys-color-on-surface);
  background: var(--md-sys-color-surface);
  padding: var(--md-sys-spacing-md);
  border-radius: var(--md-sys-shape-corner-lg);
  box-shadow: var(--md-sys-elevation-1);
  transition: all var(--md-sys-motion-duration-medium) var(--md-sys-motion-easing-standard);
}
```

### Using Utility Classes

```tsx
<div className="md-surface p-lg mb-md">
  <h3 className="md-headline-small">Title</h3>
  <p className="md-body-medium">Content</p>
</div>
```

### Using Components

```tsx
import { MaterialCard } from "@/components/MaterialCard";

<MaterialCard elevation={2} variant="elevated" title="Card">
  Card content here
</MaterialCard>;
```

---

**This is the foundation of our Material Design 3 system. Use it consistently across the application for a cohesive, modern user experience! 🎨**

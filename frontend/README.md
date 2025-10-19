# UniFi Network Insights - Frontend

A modern, Material Design 3 web application for historical network analysis and insights.

## 🎨 Design System

This frontend is built following **Material Design 3 (Material You)** guidelines, featuring:

- **Modern Typography** - Inter font with Material Design type scale
- **Rich Color System** - Primary (Blue), Secondary (Teal), Tertiary (Orange)
- **Consistent Spacing** - 8px grid system
- **Elevation System** - 5 levels of shadows for depth
- **Smooth Animations** - Standard Material Design motion
- **Accessibility** - WCAG AA compliant with focus states

📚 **Full Design Guide**: See [MATERIAL_DESIGN_GUIDE.md](../docs/MATERIAL_DESIGN_GUIDE.md)

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend server running on `http://localhost:8000`

### Installation

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```powershell
npm run build
```

Output will be in the `dist/` directory.

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/              # API client and services
│   ├── components/       # Reusable components
│   │   ├── layout/       # Layout components (AppLayout, etc.)
│   │   ├── charts/       # Chart components
│   │   ├── MaterialCard.tsx      # Material Design 3 card
│   │   └── LoadingFallback.tsx   # Loading component
│   ├── contexts/         # React contexts (Auth, etc.)
│   ├── hooks/            # Custom React hooks
│   ├── pages/            # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Historical.tsx
│   │   ├── Comparison.tsx
│   │   ├── Correlation.tsx
│   │   ├── Analytics.tsx
│   │   ├── Alerts.tsx
│   │   ├── Reports.tsx
│   │   └── Settings.tsx
│   ├── theme/            # Material Design 3 theme
│   │   └── material-theme.ts
│   ├── types/            # TypeScript types
│   ├── App.tsx           # Main app component
│   ├── App.css           # Global app styles
│   ├── index.css         # Material Design 3 global styles
│   └── main.tsx          # App entry point
├── public/               # Static assets
├── index.html            # HTML template
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
└── vite.config.ts        # Vite config
```

## 🎯 Key Features

### Pages

1. **Dashboard** - Real-time network overview
2. **Historical Analysis** - Long-term trends and patterns
3. **Device Comparison** - Side-by-side device metrics
4. **Correlation Analysis** - Relationship between metrics
5. **Analytics** - Statistical analysis and forecasting
6. **Alert Intelligence** - Alert management and insights
7. **Reports & Export** - Generate reports and export data
8. **Settings** - Application configuration

### Components

#### MaterialCard

Material Design 3 card component:

```tsx
import { MaterialCard } from "@/components/MaterialCard";

<MaterialCard elevation={2} variant="elevated" title="Card Title">
  Card content
</MaterialCard>;
```

**Props:**

- `elevation`: 0-5 (default: 1)
- `variant`: "elevated" | "filled" | "outlined"

#### LoadingFallback

Styled loading spinner:

```tsx
import { LoadingFallback } from "@/components/LoadingFallback";

<LoadingFallback />;
```

### Theme System

Material Design 3 theme configured in `src/theme/material-theme.ts`:

```tsx
import { materialTheme } from "@/theme/material-theme";

<ConfigProvider theme={materialTheme}>{/* Your app */}</ConfigProvider>;
```

### CSS Custom Properties

Use Material Design tokens:

```css
var(--md-sys-color-primary)       /* Primary color */
var(--md-sys-color-surface)        /* Surface background */
var(--md-sys-spacing-md)           /* 16px spacing */
var(--md-sys-elevation-2)          /* Level 2 shadow */
var(--md-sys-shape-corner-lg)      /* 16px border radius */
var(--md-sys-motion-duration-medium) /* 300ms */
```

### Utility Classes

Quick styling with Material Design utilities:

```tsx
<div className="md-surface p-lg mb-md">
  <h3 className="md-headline-small">Headline</h3>
  <p className="md-body-medium">Body text</p>
</div>
```

**Available classes:**

- Typography: `md-display-large`, `md-headline-medium`, `md-body-small`, etc.
- Spacing: `mt-xs`, `mb-lg`, `p-md`, etc.
- Surfaces: `md-surface`, `md-surface-variant`, `md-surface-elevated`

## 🛠️ Technology Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Ant Design 5** - UI component library
- **React Query** - Data fetching and caching
- **React Router 7** - Routing
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **Day.js** - Date manipulation

## 🎨 Styling

- **Material Design 3** - Design system
- **CSS Custom Properties** - Theme tokens
- **CSS Modules** - Component styles
- **Inter Font** - Typography

## 📱 Responsive Design

Breakpoints:

- **Desktop**: > 1024px - Full layout
- **Tablet**: 768px - 1024px - Adjusted spacing
- **Mobile**: < 768px - Compact layout

## ♿ Accessibility

- WCAG AA compliant contrast ratios
- Focus-visible outlines on interactive elements
- Keyboard navigation support
- Screen reader friendly
- Semantic HTML

## 🔧 Development

### Available Scripts

```powershell
npm run dev      # Start dev server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

### Code Style

- Use TypeScript for all components
- Follow Material Design 3 guidelines
- Use utility classes for spacing
- Keep components small and focused
- Write meaningful prop types

### Adding New Components

1. Create component in `src/components/`
2. Use Material Design 3 tokens
3. Export from component file
4. Add to component documentation

### Adding New Pages

1. Create page in `src/pages/`
2. Add route in `App.tsx`
3. Add menu item in `AppLayout.tsx`
4. Follow page structure pattern

## 🐛 Troubleshooting

### Port Already in Use

```powershell
# Change port in vite.config.ts or:
npm run dev -- --port 3000
```

### Build Errors

```powershell
# Clear cache and rebuild
rm -rf node_modules dist
npm install
npm run build
```

### Type Errors

```powershell
# Check TypeScript
npx tsc --noEmit
```

## 📚 Documentation

- [Material Design Guide](../docs/MATERIAL_DESIGN_GUIDE.md) - Complete design system guide
- [Material Design Complete](../docs/MATERIAL_DESIGN_COMPLETE.md) - Implementation summary
- [Frontend Strategy](../docs/FRONTEND_STRATEGY.md) - Strategic vision
- [API Reference](../docs/BACKEND_API_REFERENCE.md) - Backend API docs

## 🤝 Contributing

1. Follow Material Design 3 guidelines
2. Use existing components when possible
3. Write TypeScript types
4. Test responsive behavior
5. Ensure accessibility

## 📄 License

Part of the UniFi Network Insights project.

---

**Built with ❤️ using Material Design 3**

# CodeGate UI Design System

This document outlines the visual language and design principles for the CodeGate Local PR Quality Platform.

## 1. Principles
CodeGate is designed to look like a professional, polished local software product. It avoids flashy or generic marketing templates and instead focuses on clean hierarchy, data legibility, and technical confidence.

## 2. Layout & App Shell
- **Sidebar**: Fixed on desktop, 280px wide. Background color is deep navy (`#0b1220`).
- **Main Content**: Fluid width, light neutral background (`#f4f7fb`).
- **Responsive**: 
  - Mobile (390px): Sidebar becomes a collapsible hamburger menu. Main content stacks vertically.
  - Tables use horizontal scrolling on mobile only when necessary; secondary columns are hidden first.

## 3. Typography
- **Font Stack**: System sans-serif (`system-ui, 'Segoe UI', Roboto, sans-serif`).
- **Sizes**:
  - Page Title: 28-32px, font-weight: 800
  - Section Title: 16-18px, font-weight: 700
  - Card Metric: 28-34px, font-weight: 900
  - Body Text: 14px, font-weight: 400
  - Meta/Small: 12-13px, font-weight: 500

## 4. Color Palette
The app is explicitly forced into **light mode** (via `color-scheme: light`) to prevent unexpected OS dark mode overrides, maintaining intentional contrast.

- **Brand Primary**: Indigo/Blue-Violet (`#4f46e5`, `#7c3aed`)
- **Backgrounds**: Base `#f4f7fb`, Surface `#ffffff`, Soft Surface `#f8fafc`
- **Borders**: `#e2e8f0`, soft borders `rgba(148, 163, 184, 0.24)`
- **Text**: Primary `#0f172a`, Secondary `#334155`, Muted `#64748b`

### Semantic Colors
Only use semantic colors to convey meaning:
- **Success/Pass**: Green (`#16a34a`)
- **Info/Notice**: Blue (`#2563eb`)
- **Warning**: Amber (`#d97706`)
- **Danger/Block**: Red (`#dc2626`)

*(Never use color as the *only* indicator of status. Always pair with text/icons.)*

## 5. Components

### Cards & Panels
- **Border Radius**: 14px to 22px (e.g., `22px` for large dashboard panels).
- **Shadows**: Subtle, clean drop shadows (`0 14px 34px rgba(15, 23, 42, 0.06)`). No heavy neumorphism.
- **Backgrounds**: Crisp white (`#ffffff` or `rgba(255, 255, 255, 0.92)`).

### Buttons
- **Primary**: Indigo gradient, white text, subtle hover lift.
- **Secondary**: White background, light gray border, secondary text color.
- **Danger**: Red border/background used only for destructive actions (Delete, Remove, Revoke).

### Badges
- **Shape**: Pill-shaped, `border-radius: 999px`.
- **Style**: Soft background tint with a bold foreground text color (e.g., `#effdf5` background, `#166534` text for Pass).
- **Variants**: Quality Grade (A-F), Risk (Low-Critical), Policy (Pass/Warning/Block), Analysis (Queued, Running, Succeeded, Failed).

### Tables
- **Header**: Soft background (`#f8fafc`), uppercase or bold headers.
- **Rows**: Subtle hover state (`background: var(--cg-surface-soft)`), distinct dividing lines.
- **Cells**: Use `cell-primary` for the main entity name (e.g., Repository name).

## 6. States
- **Loading**: Use skeletal loaders (`<Skeleton />`) to prevent layout jumping instead of standard spinners where possible.
- **Empty**: Friendly empty state components (`<EmptyState />`) featuring a muted icon, a short description, and a Call-To-Action (if applicable).
- **Error**: Safe error panels (`<ErrorState />`) with clear retry mechanisms. No raw JSON or Axios tracebacks exposed to the UI.

## 7. Accessibility
- Provide visually distinct focus rings (`outline`).
- Ensure adequate text contrast across all badges and muted text.
- Use semantic HTML and `aria-labels` for icon-only buttons.

# Android Material Design 3 (Material You)

## 1. Core Philosophy (Material 3)

- **Material as Metaphor**: Surfaces in 3D space, light and shadow define hierarchy.
- **Dynamic Color**: UI adapts to the user's wallpaper (Android 12+).
- **Personalized**: Focus on "Material You" — design that feels specific to the individual.

---

## 2. Android Typography (Roboto & sp)

### Scalable Pixels (sp)
Mandatory: Use `sp` units for text to support accessibility font scaling.

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| **Display Large** | 57sp | Regular | 64sp |
| **Title Large** | 22sp | Regular | 28sp |
| **Body Large** | 16sp | Regular | 24sp |
| **Label Large** | 14sp | Medium | 20sp |

---

## 3. Material Color System

### Semantic Roles
Use semantic color roles instead of hardcoded hex values.
- **Surface**: The main background.
- **Primary**: Key actions and the Floating Action Button (FAB).
- **Secondary/Tertiary**: Supporting content and emphasis.
- **Error**: Red roles for destructive or failed state (#B3261E light / #F2B8B5 dark).

### Dark Theme Principles
- **Elevation Overlay**: In dark mode, higher elevation = lighter surface color.
- **Contrast**: Maintain readable contrast even with dynamic color overlays.

---

## 4. Layout & Accessibility

- **Baseline Grid**: 8dp grid for all layout spacing.
- **Touch Targets**: Minimum **48dp x 48dp** (even if visual is smaller).
- **Ripple Effect**: **MANDATORY** feedback for all touchable elements.
- **Font Scaling**: UI must remain usable at 200% font scale.

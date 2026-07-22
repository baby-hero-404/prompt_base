# Android Patterns, Gestures & Components

## 1. Navigation Patterns

| Component | Position | Constraint |
|-----------|----------|------------|
| **Bottom Navigation** | Bottom | 3-5 destinations. Active icons have a pill indicator. |
| **Navigation Rail** | Side (Left) | For Foldables/Tablets. |
| **Navigation Drawer** | Side (Hide) | For large lists of destinations (>5). |
| **Top App Bar** | Top | Small, Medium, Large variants. |

---

## 2. Platform Gestures & Navigation

- **System Back**: Respect the system back button or edge swipe gesture.
- **Predictive Back**: Support the back preview animation (Android 14+).
- **Pull-to-Refresh**: Circular progress indicator that pulls down with content.
- **Swipe-to-Dismiss**: Standard for notifications and Snackbars.

---

## 3. Core Components (Material 3)

### Floating Action Button (FAB)
- Primary entry point for the screen's main action.
- Positioned usually at the bottom right.

### Buttons
- **Filled**: High emphasis (Primary).
- **Tonal**: Medium emphasis.
- **Outlined**: Low emphasis.

### Selection & Feedback
- **Chips**: For filters, choices (Assist, Filter, Input, Suggestion).
- **Snackbars**: Brief messages at the bottom with one optional text action (e.g., "UNDO").
- **Cards**: 12dp corner radius by default. ElevatedButton for resting states.

---

## 4. States & Feedback
- **Interactive**: Hover, pressed (ripple), focused, and dragged states must be visually distinct.
- **Empty States**: Use illustrations or clear text to explain missing content.

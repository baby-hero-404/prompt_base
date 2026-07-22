# iOS Design System (HIG Foundation)

## 1. Core Philosophy (Apple Design Values)

- **Clarity**: High legibility, precise icons, lucid content.
- **Deference**: UI never competes with content; use translucency to hint at more.
- **Depth**: Visual layers convey hierarchy; transitions provide spatial sense.

---

## 2. iOS Typography (SF Pro)

### Proportional Scale (Dynamic Type)
Mandatory: Use semantic styles to support user-defined font sizes.

| Style | Default Size | Weight |
|-------|--------------|--------|
| **Large Title** | 34pt | Bold |
| **Title 1-3** | 28pt → 20pt | Bold / Semibold |
| **Body** | 17pt | Regular |
| **Footnote/Caption** | 13pt → 11pt | Regular |

**Rule**: Never hardcode font sizes (e.g., `fontSize: 17`). Use platform-specific dynamic type tokens.

---

## 3. iOS Color System

### Semantic Colors
Use semantic tokens for automatic light/dark mode adaptation.
- **Label**: Primary text.
- **SystemBackground**: Primary surface.
- **SystemAccent**: Default blue tint (#007AFF light / #0A84FF dark).

### Dark Mode Principles
- **Not just inverted**: iOS dark mode uses desaturated colors.
- **True Black**: background (#000000) for OLED battery efficiency.

---

## 4. Accessibility & Human Factors

- **Touch Targets**: Minimum **44pt x 44pt**.
- **Safe Areas**: Respect the Notch and Home Indicator. Never place interactive items in safe area insets.
- **Dynamic Type**: Test UI at maximum accessibility font scales.
- **VoiceOver**: Labels, hints, and roles for every interactive element.

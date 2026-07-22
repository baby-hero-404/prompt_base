# iOS Patterns, Gestures & Components

## 1. Navigation Patterns

| Pattern | UI Component | Constraint |
|---------|--------------|------------|
| **Tab Bar** | Bottom Tab Bar (49pt) | 3-5 items max. Active icons are filled. |
| **Drill-down** | Navigation Stack | Back button top-left + Edge swipe gesture. |
| **Focus Task** | Modal Sheet / Full-screen | Slide up from bottom. |
| **Sidebar** | iPad-only navigation | Left drawer. |

---

## 2. Interactive Gestures (MANDATORY)

- **Back Gesture**: Edge swipe from the left edge is the primary back navigation.
- **Context Menus**: Long press triggers a preview card + menu.
- **Pull-to-Refresh**: **MANDATORY** native implementation (UIRefreshControl).
- **Sheet Dismissal**: Swipe down on modal sheets.

---

## 3. Core Components (HIG Compliance)

### Buttons
- **Primary**: Filled/Tinted (High hierarchy).
- **Secondary**: Bordered/Outline.
- **Tertiary**: Plain text.
- **Rule**: Actions like "Delete" must be red (`.systemRed`).

### Lists (UITableView / List)
- **Plain**: Flat list.
- **Inset Grouped**: Rounded cards for categorized data (Default for modern iOS).
- **Disclosure Indicator**: Use `>` for navigating to details.

### Selection & Feedbacks
- **Segmented Control**: 2-5 related options.
- **Haptic Feedback**: Subtle feedback for successful actions or errors.
- **Picker**: Use the native scroll wheel for dates/selections.

# Stitch Prompt Generator — Phase Templates

### Phase 1 — Requirement & Context Preamble

**Purpose:** Set the baseline context. Stitch remembers this across subsequent prompts.

**Prompt Template:**

```
I'm designing a {platform} app called {app_name}.

About the app:
- Description: {description}
- Target users: {target_users}
- Key goals:
{for each goal}
  * {goal}
{end}

Core Features:
{for each feature}
- {feature}
{end}

Platform: {platform}
Industry: {industry}

Keep this context in mind for all subsequent requests. I'll start with the user flow next.
```

---

### Phase 2 — Information Architecture & User Flow

**Purpose:** Define the screen hierarchy and navigation structure.

**Prompt Template:**

```
Create the user flow and screen structure for {app_name}.

The main flow should be:
{primary_flow}

Screen hierarchy:
{screen_tree}

Also include:
- Settings
- Empty states for each main screen
- Error states for data-dependent screens
- Loading states

Output the complete screen map with navigation relationships.
Do NOT design any UI yet — only the structure.
```

---

### Phase 3 — Design System

**Purpose:** Lock in visual consistency before generating any screen.

**Prompt Template:**

```
Create a design system for {app_name}.

Style Direction:
- Industry: {industry}
- Vibe: {design_vibe_1}, {design_vibe_2}, {design_vibe_3}
{if reference_apps}- Reference apps: {reference_apps}{end}

Colors:
{if brand_colors}
- Primary: {primary_color}
- Accent: {accent_color}
- Define Background, Surface, Text, Success, Warning, Error colors that complement the brand
{else}
- Choose a color palette that fits a {industry} app with a {design_vibe} feel
- Define: Primary, Accent, Background, Surface, Text (primary + secondary), Success, Warning, Error
{end}

Typography:
{if font_preference}
- Use {font_preference}
{else}
- Choose a modern sans-serif font appropriate for {industry}
{end}
- Define heading hierarchy (H1-H4), body, caption, button text sizes
- Specify font weights for each level

Components (design all of these):
- Buttons (primary, secondary, ghost, disabled states)
- Cards (content card, feature card)
- Bottom navigation / Tab bar
- Input fields (default, focused, error, disabled)
- Empty state template
- Error state template
- Loading skeleton

Spacing:
- Define a consistent spacing scale (4px base)
- Border radius system (small, medium, large)

Keep this design system consistent across ALL screens that follow.
```

---

### Phase 4 — Screen Generation (Batched)

**Prompt Template:**

```
Using the design system created above, generate these screens for {app_name}:

Batch {N} — {batch_label}:
{for each screen in batch}
{i}. {screen_name}
   - Purpose: {what this screen does}
   - Key elements: {list main UI elements}
   - Data shown: {what data appears}
{end}

Rules:
- Use ONLY the design system defined earlier (colors, typography, components, spacing)
- Maintain visual consistency with previously generated screens
- Design for {platform}
- Show the populated/normal state
```

---

### Phase 5 — Interactive Prototype

**Prompt Template:**

```
Connect the screens of {app_name} into an interactive prototype.

Interactions:
{for each flow_connection}
{source_screen} → {action/trigger} → {destination_screen}
{end}

Bottom navigation should switch between:
{tab_1}, {tab_2}, {tab_3}, {tab_4}

Back navigation:
- All detail screens should have a back button returning to parent
- Quiz flow should NOT allow back (forward-only)

Do not change any screen designs. Only add navigation and interactions.
```

---

### Phase 6 — State Coverage

**Prompt Template:**

```
Create the following states for {app_name} screens.
Use the existing design system. Do not change the normal/populated designs.

{for each screen_with_states}
{screen_name}:
{for each state}
- {state_name}: {description of when this state appears}
{end}
{end}
```

---

### Phase 7 — Iteration & Refinement

**Prompt Template:**

```
Improve the {screen_name} screen of {app_name}.

Current issue:
{describe what feels wrong}

Requested changes:
{for each change}
- {specific improvement}
{end}

Constraints:
- Keep the existing design system (colors, typography, spacing, components)
- Keep all existing functionality
- Do not change other screens
```

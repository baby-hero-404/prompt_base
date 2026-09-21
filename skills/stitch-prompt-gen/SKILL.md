---
name: stitch-prompt-gen
description: "Use when generating structured, copy-ready prompts for Stitch (UI design tool). Collects app requirements interactively, then outputs 7 sequential prompts following the Requirement → Flow → Design System → Screens → Interaction → States → Iteration workflow. Triggers on stitch, stitch prompt, ui prompt, design prompt, generate stitch."
allowed-tools: Read, Write
priority: MEDIUM
---

# Stitch Prompt Generator

> Generate production-grade, copy-ready prompts for Stitch following a battle-tested 7-phase workflow. Turns vague "build me an app" requests into structured, phase-separated prompts that keep Stitch consistent and design-drift-free.

## Core Principle

**Never mix Structure, Design, Interaction, and Refinement in a single prompt.** Each phase prompt serves exactly one purpose:

| Prompt Type | Purpose |
|---|---|
| **Structure** | What screens the app has |
| **Design** | What the UI looks like |
| **Interaction** | How screens connect to each other |
| **Refinement** | Improve a specific part |

---

## 1. Input Collection (Interactive)

Before generating any prompt, collect the following from the user. Ask questions **one at a time** using the `ask_question` tool.

### Input Flexibility Rules

- **If the user provides multiple inputs at once**, extract them — don't re-ask what's already answered.
- **If the user says "use defaults"** or similar, infer reasonable values based on the app description and proceed.
- **Minimum viable input** = App Name + One-line Description + Core Screens. Everything else can be inferred.
- **If you can confidently infer** an input from context (e.g., industry from "finance education app"), do NOT ask — just state your inference and move on.

### Required Inputs

| Input | Example | Notes |
|---|---|---|
| **App Name** | FinNest | Short, memorable |
| **One-line Description** | Personal finance education app for Vietnamese users | What the app does in ≤15 words |
| **Target Users** | Young adults 18–35, beginners in personal finance | Who + their context |
| **Main Goals** (2-4) | Learn financial concepts, Take quizzes, Track progress | What users accomplish |
| **Core Features/Screens** (5-10) | Home, Lessons, Quiz, Quiz Result, Profile | The screens that exist |
| **Industry** | Fintech / Education / E-commerce / Health / Social / Productivity / Travel / Other | Drives design vocabulary |
| **Platform** | Flutter / React Native / SwiftUI / Web (React) / Web (Next.js) / Other | Drives code structure hint |
| **Design Vibe** (pick 2-3) | Modern, Minimal, Friendly, Premium, Playful, Serious, Dark, Editorial, Glassmorphism, Brutalist | Visual direction |

### Optional Inputs (ask only if user seems engaged)

| Input | Example |
|---|---|
| **Brand Colors** | Primary: #1E3A5F, Accent: #4CAF50 |
| **Reference Apps** | Duolingo, Robinhood, Notion |
| **Font Preference** | Inter, SF Pro, custom serif |

---

## 2. The 7-Phase Prompt Pipeline

> **Template Notation:**
> - `{variable}` = replace with user's input
> - `{for each X}...{end}` = repeat the block for each item the user provided
> - `{if condition}...{else}...{end}` = include conditionally based on whether the user provided that input
>
> These are **instructions to you (the AI)**, NOT literal output. The final prompt must contain only plain text with the user's actual data filled in.

After collecting inputs, generate prompts **one phase at a time**. Output each prompt as a markdown artifact with:
1. A brief explanation of the phase's purpose (2-3 sentences)
2. A copy-ready prompt inside a fenced code block
3. A "✅ What to check" section listing what to verify in Stitch before proceeding

**Do NOT generate the next phase until the user confirms the current one is done or requests it.**

---

### Phase 1 — Requirement Definition (Context Preamble)

**Purpose:** Establish the product context so Stitch understands what it's building before any visual work. This is a **context-setting prompt** — paste it into Stitch first, then immediately follow with Phase 2 in the same session.

> **Why not ask Stitch to "confirm understanding"?** Stitch is a design tool, not a chat assistant. Asking it to just acknowledge scope wastes a turn. Instead, this prompt sets context that Phase 2 will immediately build upon.

**Prompt Template:**

```
I'm building an app called {app_name} — {one_line_description}.

Here's the product context for everything that follows:

Target Users:
{for each target_user}
- {target_user}
{end}

Main Goals:
{for each goal}
- {goal}
{end}

Core Features:
{for each feature}
- {feature}
{end}

Platform: {platform}
Industry: {industry}

Keep this context in mind for all subsequent requests. I'll start with the user flow next.
```

**✅ What to check:** Paste this, then immediately follow with Phase 2. Do NOT wait for a response — this is a context anchor, not a question.

---

### Phase 2 — Information Architecture & User Flow

**Purpose:** Define the screen hierarchy and navigation structure. If the flow is wrong, beautiful UI is worthless.

**Prompt Template:**

```
Create the user flow and screen structure for {app_name}.

The main flow should be:
{primary_flow — e.g.: Onboarding → Home → Lesson → Quiz → Quiz Result → Progress}

Screen hierarchy:

{screen_tree — e.g.:
Home
 ├── Lessons
 │    └── Lesson Detail
 │          └── Quiz
 │                └── Result
 ├── Progress
 └── Profile
}

Also include:
- Settings
- Empty states for each main screen
- Error states for data-dependent screens
- Loading states

Output the complete screen map with navigation relationships.
Do NOT design any UI yet — only the structure.
```

**✅ What to check:**
- Every core feature maps to at least one screen
- Navigation paths are logical (no dead ends)
- Edge screens (empty, error, loading) are accounted for

---

### Phase 3 — Design System

**Purpose:** Lock in visual consistency before generating any screen. This is the single source of truth for colors, typography, spacing, and components.

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
- {industry_specific_components — e.g. Quiz option buttons, Progress bars for education}
- Empty state template
- Error state template
- Loading skeleton

Spacing:
- Define a consistent spacing scale (4px base)
- Border radius system (small, medium, large)

Keep this design system consistent across ALL screens that follow.
```

**Industry-Specific Component Map:**

| Industry | Additional Components |
|---|---|
| Fintech | Transaction cards, Balance display, Chart containers, KPI tiles |
| Education | Quiz options, Progress bars, Achievement badges, Lesson cards |
| E-commerce | Product cards, Cart summary, Price tags, Rating stars |
| Health | Metric cards, Appointment slots, Vital signs display |
| Social | Post cards, Story bubbles, Comment threads, Reaction bar |
| Productivity | Task items, Kanban columns, Calendar cells, Timer display |

**✅ What to check:**
- Color palette has sufficient contrast (especially text on backgrounds)
- Typography hierarchy is clear and consistent
- All listed components are designed, not just mentioned
- The system feels cohesive — would you recognize any screen as part of this app?

---

### Phase 4 — Screen Generation (Batched)

**Purpose:** Generate screens in small batches (3-5 per prompt) to prevent design drift. Always reference the design system.

**Prompt Template (repeat per batch):**

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
- Show the populated/normal state (other states come later)
```

**Recommended Batching:**

| Batch | Screens | Label |
|---|---|---|
| 1 | Onboarding, Home, primary listing | Core |
| 2 | Detail views, interaction screens | Interaction |
| 3 | Profile, Settings, secondary screens | Account |

**✅ What to check per batch:**
- Design system colors/fonts/spacing match Phase 3
- Components look identical across screens (buttons, cards, nav)
- No "design drift" — later screens should feel like the same app as earlier ones
- Layout is appropriate for {platform}

---

### Phase 5 — Interactive Prototype

**Purpose:** Wire screens together into a clickable flow so the product feels real, not just a collection of screenshots.

**Prompt Template:**

```
Connect the screens of {app_name} into an interactive prototype.

Interactions:

{for each flow_connection}
{source_screen}
→ {action/trigger} → {destination_screen}
{end}

Example flow to test:
{primary_user_journey — e.g.:
1. Onboarding → Tap "Get Started" → Home
2. Home → Tap lesson card → Lesson Detail
3. Lesson Detail → Tap "Start Quiz" → Quiz
4. Quiz → Submit answers → Quiz Result
5. Quiz Result → Tap "Continue" → Home
}

Bottom navigation should switch between:
{tab_1}, {tab_2}, {tab_3}, {tab_4}

Back navigation:
- All detail screens should have a back button returning to parent
- Quiz flow should NOT allow back (forward-only)

Do not change any screen designs. Only add navigation and interactions.
```

**✅ What to check:**
- Every screen is reachable (no orphan screens)
- Primary flow works end-to-end
- Tab navigation works
- Back buttons work correctly
- No visual changes were introduced (only interactions added)

---

### Phase 6 — State Coverage

**Purpose:** Design the non-happy-path states. This is what separates a prototype from an actual product spec. Most AI design tools skip this — don't.

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

Example:
Home:
- Loading: Skeleton placeholders while data loads
- Empty: New user, no progress yet — show welcome message + CTA to start first lesson
- Error: Network/server error — show retry button
- Normal: (already designed)

{generate states based on industry and screens}

Each state must:
- Use the existing design system (colors, fonts, components)
- Feel intentional, not like an afterthought
- Have a clear user action to escape the state (CTA for empty, retry for error)
```

**State Generation Rules by Screen Type:**

| Screen Type | Required States |
|---|---|
| List/Feed screens | Loading, Empty, Error, Populated, End-of-list |
| Detail screens | Loading, Error, Populated |
| Form/Input screens | Default, Validation error, Submitting, Success, Server error |
| Quiz/Interactive | Not started, In progress, Answer selected, Correct, Wrong, Completed |
| Profile/Settings | Loading, Populated, Editing |
| Dashboard/Stats | Loading, Empty (no data), Populated, Error |

**✅ What to check:**
- Every data-dependent screen has Loading + Error + Empty states
- Empty states have actionable CTAs (not just "No data")
- Error states have plain-language messages + recovery action
- States use the same design system (no rogue colors or fonts)

---

### Phase 7 — Iteration & Refinement

**Purpose:** Polish specific screens without breaking the whole. This is where Stitch shines — targeted improvements with guardrails.

**Prompt Template (use as needed):**

```
Improve the {screen_name} screen of {app_name}.

Current issue:
{describe what feels wrong — e.g. "too dense", "not engaging enough", "hierarchy unclear"}

Requested changes:
{for each change}
- {specific improvement}
{end}

Constraints:
- Keep the existing design system (colors, typography, spacing, components)
- Keep all existing functionality
- Do not change other screens
- {any additional constraints}
```

**Common Refinement Patterns:**

| Issue | Prompt Direction |
|---|---|
| Too dense | "More spacious, easier to scan, reduce visual clutter" |
| Not engaging | "Improve visual hierarchy, add micro-interactions, make CTAs more prominent" |
| Inconsistent | "Align with the design system — check colors, fonts, spacing, border radius" |
| Poor hierarchy | "Restructure information priority, make primary action obvious" |
| Accessibility | "Increase contrast, enlarge touch targets, add labels" |

**✅ What to check:**
- Only the targeted screen changed
- Design system integrity maintained
- The change actually addresses the stated issue
- No new inconsistencies introduced

---

## 3. Context Anchoring

Stitch (and most AI design tools) can lose design context between sessions or after many turns. Use these rules to prevent drift:

### For Phase 4+ prompts, always prepend a context anchor:

```
Continue working on {app_name}.
Use the design system established earlier:
- Colors: {primary}, {accent}, {background}
- Font: {font_name}
- Style: {design_vibe}
Do not deviate from this system.
```

### When to re-paste the full design system:

- Stitch starts using colors/fonts not in the design system
- You start a new Stitch session
- More than ~10 prompts have passed since Phase 3
- Stitch generates a screen that looks visually different from previous ones

When this happens, re-paste the Phase 3 design system prompt before continuing with screen generation.

---

## 4. Output Format

Each phase prompt is delivered as a **markdown artifact** with this structure:

```markdown
# 🎯 Phase {N}: {Phase Name}

> **Purpose:** {2-3 sentence explanation of why this phase exists and what it accomplishes}

## Prompt (copy to Stitch ↓)

\```
{the actual prompt — ready to copy-paste}
\```

## ✅ Checklist — verify in Stitch before Phase {N+1}

- [ ] {check item 1}
- [ ] {check item 2}
- [ ] {check item 3}
```

---

## 5. Anti-Patterns (Things to NEVER Do)

| ❌ Don't | ✅ Do Instead |
|---|---|
| Generate all 7 phases in one dump | Generate one phase, wait for confirmation, then next |
| Mix structure + design in same prompt | Separate: flow first, then visual |
| Say "Generate 15 screens" | Batch: 3-5 screens per prompt |
| Skip empty/error/loading states | Phase 6 exists for exactly this |
| Change design system mid-project | Lock it in Phase 3, reference it in every subsequent phase |
| Use vague refinement ("make it better") | Specify: what's wrong, what to change, what to keep |

---

## 6. Handoff to Development

After all 7 phases are complete, generate a **handoff summary** artifact:

```markdown
# 📦 {app_name} — Stitch Design Handoff

## Screen Inventory
| Screen | States Designed | Notes |
|---|---|---|
| {screen} | Normal, Loading, Empty, Error | {notes} |

## Design System Summary
- Colors: {palette}
- Font: {font}
- Key components: {list}

## Suggested Code Structure ({platform})
{platform-specific directory structure — e.g. Flutter:
lib/
├── core/
├── features/
│   ├── home/
│   ├── lesson/
│   ├── quiz/
│   └── profile/
├── shared/
└── main.dart
}

## Implementation Notes
- Components that need custom implementation: {list}
- Components available from libraries: {list}
- Screens that need special animation/interaction work: {list}
```

> **Important:** Stitch output is a UI specification + prototype + starting point. Developers should refactor generated code to match the project's architecture, not copy-paste blindly.

---

## 7. Quick Reference — Full Pipeline

```
Phase 1: Requirement     → "Here's what the app does" (context preamble)
Phase 2: Flow            → "Here's the screen hierarchy"
Phase 3: Design System   → "Here's the visual language"
Phase 4: Screens         → "Generate these screens in batches"
Phase 5: Interaction     → "Wire them together"
Phase 6: States          → "Design the non-happy paths"
Phase 7: Iteration       → "Polish specific parts"
        Handoff          → "Summary for developers"
```

Each phase builds on the previous. Never skip. Never combine.

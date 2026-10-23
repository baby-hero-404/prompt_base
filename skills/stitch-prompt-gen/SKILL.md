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
- **Phase 1: Structure** — What screens the app has (Context Preamble).
- **Phase 2: Flow** — Information Architecture & User Flow.
- **Phase 3: Design System** — Visual foundation (Colors, Typography, Components).
- **Phase 4: Screen Generation** — Batched screens (3-5 per prompt) referencing Design System.
- **Phase 5: Interaction** — Wire screens into a clickable prototype.
- **Phase 6: State Coverage** — Non-happy paths (Loading, Empty, Error).
- **Phase 7: Iteration** — Targeted refinements with guardrails.

Templates for all phases live in `references/phase-templates.md`.

---

## 1. Input Collection (Interactive)

Before generating any prompt, collect the following from the user. Ask questions **one at a time** using the `ask_question` tool.

### Minimum Viable Inputs
- **App Name**: Short and memorable.
- **One-line Description**: What the app does in $\le 15$ words.
- **Core Screens** (5-10): The screens that exist.
- **Industry & Platform**: E.g., Fintech, Education, Health on Flutter / React / Next.js.
- **Design Vibe**: Pick 2-3 (Modern, Minimal, Friendly, Premium, Dark, etc.).

If the user provides multiple inputs or says "use defaults", infer reasonable values and proceed.

---

## 2. Execution Pipeline

1. **Phase 1: Requirement Preamble** — Establish product baseline context.
2. **Phase 2: IA & User Flow** — Output complete screen map without UI.
3. **Phase 3: Design System** — Lock in palette, typography scale, component library, and spacing tokens.
4. **Phase 4: Batched Screens** — 3-5 screens per batch to prevent design drift.
5. **Phase 5: Interactive Prototype** — Connect navigation, tabs, and back paths without modifying UI.
6. **Phase 6: States** — Loading skeleton, Empty with CTA, Error with retry.
7. **Phase 7: Refinement** — Isolate screen, specify issue, keep constraints intact.

For exact prompt templates and copy-ready markdown formatting, consult `references/phase-templates.md`.

---

## 3. Output Format

Deliver each phase prompt as a markdown artifact:
- **Purpose**: 2-3 sentence explanation of the phase's goal.
- **Prompt**: Copy-ready inside a fenced code block with user data pre-filled.
- **Checklist**: 3-4 concrete verification checks in Stitch before continuing to the next phase.

---

## 4. Anti-Patterns

| ❌ Don't | ✅ Do Instead |
|---|---|
| Generate all 7 phases in one dump | Generate one phase, wait for confirmation, then next |
| Mix structure + design in same prompt | Separate: flow first, then visual |
| Say "Generate 15 screens" | Batch: 3-5 screens per prompt |
| Skip empty/error/loading states | Phase 6 covers non-happy paths |
| Change design system mid-project | Lock in Phase 3, reference in every subsequent phase |

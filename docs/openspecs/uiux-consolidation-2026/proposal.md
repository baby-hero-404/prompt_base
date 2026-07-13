# Proposal: UI/UX Skill Consolidation

## Why
`frontend-design` and `ux-ui-pro-max` both cover frontend design (typography, layout, color), but they are not pure duplicates — they serve different jobs:
- `frontend-design`: design *philosophy* — 60-30-10 rule, 8-point grid, psychology laws, and an explicit "Forbidden AI Defaults" list banning generic AI-generated design clichés (bento grids, mesh gradients, glassmorphism, "fintech blue").
- `ux-ui-pro-max`: a searchable style/palette *lookup tool* — a Python CLI database of 50+ styles, 97 palettes, and 57 font pairings across many stacks (React, Next.js, SwiftUI, Flutter, Jetpack Compose, etc.), plus accessibility/touch/performance checklists.

Having both compete for the same trigger keywords is real ambiguity. But a straight "deprecate `frontend-design`, migrate unique assets" risks quietly losing the judgment-based content (the psychology rationale and, especially, the "Forbidden AI Defaults" anti-pattern list) inside a skill that's structured as a lookup tool, not a principles document.

## What Changes
- Deprecate `frontend-design` as a standalone skill.
- Migrate its unique content — psychology laws, 60-30-10/8-point-grid rules, and the "Forbidden AI Defaults" anti-pattern list — into `ux-ui-pro-max` as an explicit "Design Principles" section or reference file, not folded loosely into the existing style-lookup material.

## Capabilities

### Modified Capabilities
- `ux-ui-pro-max` gains a design-principles/anti-patterns section distinct from its existing style-lookup capability.

### Removed Capabilities
- Standalone access to `frontend-design`.

## Impact

| Area | Files Affected |
|------|----------------|
| Skill (updated) | `antigravity/skills/tech/ux-ui-pro-max/SKILL.md` (+ possible new reference file for principles/anti-patterns) |
| Skill (removed) | `antigravity/skills/process/frontend-design/` |
| Agent frontmatter | `antigravity/agents/frontend-specialist.md` (`skills:` list references `frontend-design`) |
| Registry | `registry.min.json` (regenerated) |

Note: `antigravity/global_workflows/ux-ui-pro.md` was checked and only references `ux-ui-pro-max` already — no update needed there.

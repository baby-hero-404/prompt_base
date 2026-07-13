# Tasks: UI/UX Skill Consolidation

## P0 — Critical

### Task 1.1: Migrate content into `ux-ui-pro-max`
> Links to: REQ-M01

**Acceptance Criteria:**
- [x] 60-30-10 rule, 8-point grid, and psychology-laws content present in `ux-ui-pro-max` (inline or as a reference file), as a distinct "Design Principles" section
- [x] "Forbidden AI Defaults" anti-pattern list present verbatim (or equivalently complete), confirmed via diff against the source file before deletion
- [x] `frontend-design/` directory deleted

### Task 1.2: Update agent frontmatter
> Links to: REQ-M01

**Acceptance Criteria:**
- [x] `antigravity/agents/frontend-specialist.md`'s `skills:` list has `frontend-design` replaced with `ux-ui-pro-max` (dedupe if already present)
- [x] `grep -rln "frontend-design" antigravity/` returns no results

## P0 — Gating (do last)

### Task 2.1: Regenerate registry & redeploy
> Links to: REQ-M01

**Acceptance Criteria:**
- [x] `make registry` run successfully
- [x] `registry.min.json` confirmed to no longer list `frontend-design`, and `ux-ui-pro-max`'s description covers the migrated principles/anti-pattern trigger keywords
- [x] `make install-claude` / `make install-gemini` run to deploy

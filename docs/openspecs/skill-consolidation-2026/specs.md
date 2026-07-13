# Specs: Skill Consolidation 2026

## Added Requirements

### REQ-001: Create `red-team-operations`
> ❌ Status: Not Started

**Scenario:**
- WHEN a user requests offensive security testing, penetration testing, or red teaming
- THEN the system should trigger a single, unified `red-team-operations` skill
- AND the skill should contain both methodology (PTES) and tactical implementation (MITRE)

## Modified Requirements

### REQ-M01: Unify Code Verification
> ❌ Status: Not Started

**Scenario:**
- WHEN the user finishes a task or asks to run pre-commit checks
- THEN the system should route exclusively to `verification-before-completion`
- AND the unified skill must include the checklists previously found in the deprecated skills

### REQ-M02: Consolidate UI/UX Design
> ❌ Status: Not Started

**Scenario:**
- WHEN the user asks for frontend layout, color palette, or typography design
- THEN the system should route exclusively to `ux-ui-pro-max`

### REQ-M03: Streamline Testing Routing
> ❌ Status: Not Started

**Scenario:**
- WHEN a user asks to write tests for a feature
- THEN the system should route to `tdd-workflow`
- AND `tdd-workflow` should selectively load `testing-patterns` internally as a reference file without competing at the top-level registry.

## Removed Requirements

- REQ-R01: Remove `code-review-checklist`
- REQ-R02: Remove `review-pre-commit-git`
- REQ-R03: Remove `frontend-design`
- REQ-R04: Remove `red-team-tactics`
- REQ-R05: Remove `red-teaming`

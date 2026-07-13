# Proposal: Skill Consolidation 2026

## Why
Analysis of the current `registry.min.json` revealed significant overlaps and redundancies among several skills. This redundancy causes the AI orchestrator to waste tokens loading duplicate contexts, or to fail to load the correct skill when intent triggers are ambiguous. 

Specifically:
- **Verification/Review**: 3 distinct skills trigger at the end of a task or before a commit (`code-review-checklist`, `review-pre-commit-git`, `verification-before-completion`).
- **Frontend Design**: `frontend-design` and `ux-ui-pro-max` cover the exact same domain (typography, layouts, color).
- **Security**: `red-team-tactics` (tactics) and `red-teaming` (methodology) share an indistinguishable boundary for LLM routing.
- **Testing**: `testing-patterns` and `tdd-workflow` often conflict when a user asks to "write tests".

## What Changes

### Issue 1: Code Verification Redundancy
- Consolidate `code-review-checklist`, `review-pre-commit-git`, and `verification-before-completion` into a single, unified `verification-before-completion` skill.

### Issue 2: Frontend Design Overlap
- Deprecate `frontend-design` and migrate any unique assets into `ux-ui-pro-max`.

### Issue 3: Red Team Operations Fragmentation
- Merge `red-team-tactics` and `red-teaming` into a single unified skill `red-team-operations`.

### Issue 4: Testing Conflicts
- Keep `tdd-workflow` as the primary operational skill, but have it dynamically reference `testing-patterns` rather than having both compete for top-level triggers.

## Capabilities

### Modified Capabilities
- LLM Router precision will increase significantly due to removed ambiguities.
- Token overhead will decrease by removing redundant skill loads.

### Removed Capabilities
- Standalone access to deprecated skills (`code-review-checklist`, `review-pre-commit-git`, `frontend-design`, `red-teaming`, `red-team-tactics`).

## Impact

| Area | Files Affected |
|------|----------------|
| Skills (Verification) | `verification-before-completion/SKILL.md` (Updated) |
| Skills (Verification) | `code-review-checklist/` (Removed) |
| Skills (Verification) | `review-pre-commit-git/` (Removed) |
| Skills (UI/UX) | `ux-ui-pro-max/SKILL.md` (Updated) |
| Skills (UI/UX) | `frontend-design/` (Removed) |
| Skills (Security) | `red-team-operations/SKILL.md` (Created) |
| Skills (Security) | `red-team-tactics/` (Removed) |
| Skills (Security) | `red-teaming/` (Removed) |
| Skills (Testing) | `tdd-workflow/SKILL.md` (Updated) |
| Registry | `registry.min.json` (Regenerated) |

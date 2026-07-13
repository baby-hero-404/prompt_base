# Tasks: Skill Consolidation 2026

## P0 — Critical

### Task 1.1: Consolidate Verification Skills
> Links to: REQ-M01, REQ-R01, REQ-R02

**Acceptance Criteria:**
- [ ] Content from `code-review-checklist` and `review-pre-commit-git` is merged into `verification-before-completion` (or its reference files).
- [ ] `code-review-checklist` directory is deleted.
- [ ] `review-pre-commit-git` directory is deleted.
- [ ] Any references in global workflows (e.g. `/review`) pointing to deprecated skills are updated.

### Task 1.2: Consolidate UI/UX Skills
> Links to: REQ-M02, REQ-R03

**Acceptance Criteria:**
- [ ] Unique content from `frontend-design` (if any) is merged into `ux-ui-pro-max`.
- [ ] `frontend-design` directory is deleted.

### Task 1.3: Unify Red Team Operations
> Links to: REQ-001, REQ-R04, REQ-R05

**Acceptance Criteria:**
- [ ] A new directory `red-team-operations` is created with a new `SKILL.md`.
- [ ] Content from `red-team-tactics` and `red-teaming` is merged into the new skill logically.
- [ ] `red-team-tactics` directory is deleted.
- [ ] `red-teaming` directory is deleted.

## P1 — High

### Task 2.1: Update Testing Flow
> Links to: REQ-M03

**Acceptance Criteria:**
- [ ] `tdd-workflow` is updated to mention and rely on `testing-patterns` for specific structural implementations.
- [ ] `testing-patterns` YAML description is updated to clarify it is a reference pattern library, not the primary workflow trigger.

## P0 — Gating (do last)

### Task 3.1: Regenerate Registry & Redeploy
> Links to: all REQs above

**Acceptance Criteria:**
- [ ] `make registry` is run successfully.
- [ ] Check `registry.min.json` to confirm deleted skills are gone and the new `red-team-operations` is present.
- [ ] `make install-claude` and `make install-gemini` are run to deploy changes to local environments.

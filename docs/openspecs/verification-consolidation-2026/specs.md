# Specs: Verification Skill Consolidation

## Modified Requirements

### REQ-M01: Unify code verification into `verification-before-completion`
> ❌ Status: Not Started

**Scenario:**
- WHEN `verification-before-completion`'s `SKILL.md` (or its reference files) is read after this change
- THEN it must contain the two-stage spec-compliance/code-quality review process and dispatch instructions previously in `code-review-checklist`
- AND it must contain the pre-commit OK/Not-OK output template previously in `review-pre-commit-git`
- AND `code-review-checklist/` and `review-pre-commit-git/` must no longer exist as directories

### REQ-M02: `subagent-driven-development` references the consolidated skill
> ❌ Status: Not Started

**Scenario:**
- WHEN `subagent-driven-development`'s two-stage review step is read
- THEN it must reference `verification-before-completion` for the review mechanics rather than independently re-describing "spec review then quality review"
- AND its own workflow-specific detail (fresh-subagent dispatch, task-loop structure) is preserved unchanged — this skill is not being deleted or merged, only cross-referenced

## Removed Requirements
- REQ-R01: Remove `code-review-checklist`
- REQ-R02: Remove `review-pre-commit-git`

## Note on Verifiability
Requirements below are phrased in terms of file content and existence (checkable by reading/grepping the repo), not runtime "routing behavior" — skill auto-trigger is influenced by YAML `description` matching, not a deterministic router, so "the system routes exclusively to X" cannot be verified as a repo-side acceptance criterion. Where trigger precision matters, the checkable proxy is: the deleted skills' descriptions no longer exist to compete, and `verification-before-completion`'s own description accurately reflects its widened scope.

# Proposal: Verification Skill Consolidation

## Why
Three skills all trigger around "is this done / is this correct" moments, causing redundant context loads and ambiguous routing:
- `code-review-checklist`: two-stage review (spec compliance → code quality) with dispatch instructions and anti-pattern examples.
- `review-pre-commit-git`: a thin protocol pointing to a template for pre-commit OK/Not-OK output.
- `verification-before-completion`: an "Iron Law" discipline against claiming completion without fresh, executed verification evidence.

A fourth skill was found during review that overlaps in spirit but is **not** being merged: `subagent-driven-development` independently defines its own "two-stage review after each task: spec compliance review first, then code quality review" (its own `SKILL.md`, lines 9-13) — nearly the same structure `code-review-checklist` provides standalone. It stays separate because it's an execution-workflow skill (dispatching fresh subagents), not a review-output skill, but its review step should point at the consolidated skill rather than silently re-describing the same process. See REQ-M02.

## What Changes
- Consolidate `code-review-checklist` and `review-pre-commit-git` into `verification-before-completion`, which becomes the single skill for "is this task actually done and correct."
- Update `subagent-driven-development` to reference the consolidated skill for its own two-stage review step instead of re-describing it inline.

## Capabilities

### Modified Capabilities
- `verification-before-completion` gains: the two-stage spec/quality review process and dispatch instructions from `code-review-checklist`, and the pre-commit OK/Not-OK output template from `review-pre-commit-git`.
- `subagent-driven-development` references the consolidated skill for its review step.

### Removed Capabilities
- Standalone access to `code-review-checklist` and `review-pre-commit-git`.

## Impact

| Area | Files Affected |
|------|----------------|
| Skill (updated) | `antigravity/skills/process/verification-before-completion/SKILL.md` |
| Skill (removed) | `antigravity/skills/process/code-review-checklist/` |
| Skill (removed) | `antigravity/skills/process/review-pre-commit-git/` |
| Skill (cross-ref only, not deleted) | `antigravity/skills/process/subagent-driven-development/SKILL.md` |
| Agent frontmatter | `antigravity/agents/test-engineer.md` (`skills:` list references `code-review-checklist`) |
| Workflow | `antigravity/global_workflows/review.md` (invokes `tool="review-pre-commit-git"` by string, plus 2 prose mentions) |
| Registry | `registry.min.json` (regenerated) |

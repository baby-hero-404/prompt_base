# Tasks: Testing Skill Routing Clarification
**Status**: Investigated, no action needed

## P1 — High

### Task 1.1: Investigate actual overlap
> Links to: REQ-001

**Acceptance Criteria:**
- [x] `tdd-workflow` and `testing-patterns` YAML `description` fields compared and overlapping keywords (if any) listed (No significant keyword overlap: tdd focuses on 'implementing feature/bugfix', patterns focuses on 'structuring unit/integration tests').
- [x] At least a search of `antigravity/agents/*.md` and `antigravity/global_workflows/*.md` done for evidence of actual ambiguous routing (e.g. both invoked for the same trigger with conflicting guidance), not just theoretical co-matching
- [x] Finding documented in this task's notes: no real conflict found. Both are loaded concurrently by `test-engineer` and provide complementary advice (process vs structure).

## P2 — Medium (conditional — only if Task 1.1 confirms conflict)

### Task 2.1: Narrow `testing-patterns` description
> Links to: REQ-M01

**Acceptance Criteria:**
- [ ] `testing-patterns`'s YAML `description` updated to disambiguate it as a pattern/reference library
- [ ] No body content or file structure changes
- [ ] `make registry` run and `registry.min.json` reflects the updated description

## Note
If Task 1.1 finds no real conflict, stop here — do not execute Task 2.1. Update this file's status and close the proposal as "investigated, no action needed" rather than proceeding on the original bundle's unverified assumption.

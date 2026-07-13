# Tasks: Verification Skill Consolidation

## P0 — Critical

### Task 1.1: Merge content into `verification-before-completion`
> Links to: REQ-M01

**Acceptance Criteria:**
- [x] Two-stage review process + dispatch instructions from `code-review-checklist` present in `verification-before-completion` (inline or as a reference file)
- [x] Pre-commit OK/Not-OK template from `review-pre-commit-git` present in `verification-before-completion` (inline or as a reference file), output format unchanged
- [x] `code-review-checklist/` directory deleted
- [x] `review-pre-commit-git/` directory deleted

### Task 1.2: Update `review.md` workflow
> Links to: REQ-M01

**Acceptance Criteria:**
- [x] `antigravity/global_workflows/review.md` line 2 (`description`), line 28 (`Activate Skill`), and line 53 (`tool="review-pre-commit-git"`) all updated to reference `verification-before-completion`
- [x] `grep -rn "review-pre-commit-git" antigravity/` returns no results

### Task 1.3: Update agent frontmatter
> Links to: REQ-M01

**Acceptance Criteria:**
- [x] `antigravity/agents/test-engineer.md`'s `skills:` list has `code-review-checklist` replaced with `verification-before-completion` (dedupe if already present)
- [x] `grep -rln "code-review-checklist" antigravity/` returns no results

### Task 1.4: Cross-reference from `subagent-driven-development`
> Links to: REQ-M02

**Acceptance Criteria:**
- [x] The "two-stage review" description in `subagent-driven-development/SKILL.md` (lines ~9-13, ~33-36) is rewritten to reference `verification-before-completion` rather than independently describing the same two stages
- [x] The rest of the skill (fresh-subagent dispatch workflow) is unchanged

## P0 — Gating (do last)

### Task 2.1: Regenerate registry & redeploy
> Links to: all REQs above

**Acceptance Criteria:**
- [x] `make registry` run successfully
- [x] `registry.min.json` confirmed to no longer list `code-review-checklist` or `review-pre-commit-git`, and `verification-before-completion`'s description reflects its widened scope
- [x] `make install-claude` / `make install-gemini` run to deploy

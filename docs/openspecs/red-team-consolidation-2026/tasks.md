# Tasks: Red Team Skill Consolidation

## P0 — Critical

### Task 1.1: Create `red-team-operations`
> Links to: REQ-001

**Acceptance Criteria:**
- [x] New directory `antigravity/skills/process/red-team-operations/` with a new `SKILL.md`
- [x] Contains all of `red-teaming`'s content (PTES phases, OWASP-2025-dated attack surface, ethical boundaries checklist)
- [x] Contains all of `red-team-tactics`'s content, including the "Web, Cloud & AI Attacks (2026 Landscape)" section — re-read the current file before merging, don't work from a stale copy
- [x] `grep -n "^## " ` on the new file shows strictly increasing section numbers with no duplicates
- [x] `red-team-tactics/` directory deleted
- [x] `red-teaming/` directory deleted

### Task 1.2: Update agent frontmatter
> Links to: REQ-001

**Acceptance Criteria:**
- [x] `antigravity/agents/security-auditor.md`'s `skills:` list has `red-team-tactics, red-teaming` replaced with `red-team-operations`
- [x] `grep -rln -E "red-team-tactics|red-teaming\b"  antigravity/` returns no results outside `docs/`

## P0 — Gating (do last)

### Task 2.1: Regenerate registry & redeploy
> Links to: REQ-001

**Acceptance Criteria:**
- [x] `make registry` run successfully
- [x] `registry.min.json` confirmed to list `red-team-operations` and no longer list `red-team-tactics` or `red-teaming`
- [x] `make install-claude` / `make install-gemini` run to deploy

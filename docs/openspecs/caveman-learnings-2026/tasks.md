# Tasks: Caveman Learnings — Prompt & Delivery Refactor

## P0 — Critical

### Task 1.1: Fix installer breakage (manifest + excludes)
> Links to: REQ-004

**Acceptance Criteria:**
- [x] `install.manifest.json` created with targets, include and exclude globs (excludes: `caveman/`, `.git*`, `docs/`, `scripts/`, `__pycache__/`, `Makefile`, `README.md`, `*.pyc`)
- [x] `scripts/install_manifest.py` performs the filtered copy, overwriting read-only destinations safely
- [x] `Makefile` `install-claude` / `install-gemini` call the script instead of `cp -r ./*`
- [x] Post-install assertion fails the build if `registry.min.json`, `core/`, or `antigravity/skills/` is missing from a target

### Task 1.2: Repair existing global state
> Links to: REQ-005

**Acceptance Criteria:**
- [x] `caveman/` removed from `~/.claude` and `~/.gemini`
- [x] `make install` run twice consecutively; both runs exit 0

## P1 — High

### Task 2.1: Add Token-Efficient Output rules to TIER 0
> Links to: REQ-001

**Acceptance Criteria:**
- [x] `core/rules.md` gains a "Token-Efficient Output" subsection (ban invented abbreviations and arrow chains; compress filler, not words; never compress language)
- [x] `antigravity/skills/core/context-management/SKILL.md` mirrors the rule with the BPE-tokenizer rationale
- [x] `make registry && make install` re-run if any skill frontmatter `description` changed

### Task 2.2: Add Auto-Clarity Override
> Links to: REQ-002

**Acceptance Criteria:**
- [x] `core/system_prompt.md` gains the Auto-Clarity Override with an explicit trigger list (security warnings, destructive/irreversible actions, ambiguous multi-step sequences)
- [x] `antigravity/skills/core/behavioral-modes/SKILL.md` states the override applies to every mode/persona

## P2 — Medium

### Task 3.1: Section-level skill loading protocol (JIT v2)
> Links to: REQ-003

**Acceptance Criteria:**
- [x] `antigravity/skills/core/skill-loading/SKILL.md` documents the heading-match protocol and the always-load floor (frontmatter + Core Principles)
- [x] Escalation rule to full-file read documented
- [x] Spot-check: activating one section of a large skill (e.g., `testing-patterns`) demonstrably loads fewer lines than the full file

### Task 3.2: Reduce cleanup.sh to pycache pruning
> Links to: REQ-M01

**Acceptance Criteria:**
- [x] `scripts/cleanup.sh` no longer deletes `docs/`, `scripts/`, `Makefile`, `README.md` in targets (excludes make it unnecessary)
- [x] `__pycache__` pruning retained

## P3 — Low

### Task 4.1: Documentation sync
> Links to: REQ-004

**Acceptance Criteria:**
- [x] `ARCHITECTURE.md` installer section updated to describe the manifest flow
- [x] Status icons in `specs.md` updated as tasks complete
